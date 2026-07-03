param(
  [string]$Pdf = "Pages from Matematica-M1-material-didactic-si-testare.pdf",
  [string]$Evidence = "D:\dev\release-assets\voila\v0.7.0-owner-local-testability-and-ui-polish-no-build-no-distribution\final-status-check"
)

$ErrorActionPreference = "Stop"

$Project = "D:\dev\projects\voila"
Set-Location $Project

New-Item -ItemType Directory -Force $Evidence | Out-Null

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = "$Project\services\api"

Write-Host "`n=== Check v0.7.0 owner-local OCR math final status ===" -ForegroundColor Cyan

python -m compileall .\services\api | Tee-Object "$Evidence\python-compile.txt"

$RequiredFiles = @(
  "services/api/ocr_math_normalizer.py",
  "services/api/ocr_math_report.py",
  "services/api/ocr_math_report_hook.py",
  "scripts/dev/check-ocr-math-normalizer.ps1",
  "scripts/dev/build-ocr-math-report.ps1",
  "scripts/dev/check-ocr-math-report-hook.ps1",
  "scripts/dev/check-ocr-math-generate-hook.ps1",
  "docs/dev/v0.7.0-ocr-math-normalizer-engine.md",
  "docs/dev/v0.7.0-ocr-math-diagnostic-report.md",
  "docs/dev/v0.7.0-ocr-math-report-hook.md",
  "docs/dev/v0.7.0-ocr-math-generate-guarded-hook.md",
  "docs/dev/v0.7.0-owner-local-ocr-math-final-status-no-build-no-distribution.md"
)

foreach ($File in $RequiredFiles) {
  if (-not (Test-Path $File)) {
    throw "Missing required file: $File"
  }
  "OK: $File" | Tee-Object "$Evidence\required-files.txt" -Append
}

$Markers = [ordered]@{
  web_has_generate_hook = (Select-String -Path ".\services\api\web_app.py" -SimpleMatch "VOILA_OCR_MATH_REPORT_HOOK_GENERATE_V1" -Quiet)
  web_imports_hook = (Select-String -Path ".\services\api\web_app.py" -SimpleMatch "build_ocr_math_report_if_enabled" -Quiet)
  hook_has_env_flag = (Select-String -Path ".\services\api\ocr_math_report_hook.py" -SimpleMatch "VOILA_ENABLE_OCR_MATH_REPORT_HOOK" -Quiet)
  report_has_json_output = (Select-String -Path ".\services\api\ocr_math_report.py" -SimpleMatch "ocr_math_report.json" -Quiet)
  report_has_md_output = (Select-String -Path ".\services\api\ocr_math_report.py" -SimpleMatch "ocr_math_report.md" -Quiet)
  normalizer_has_x0 = (Select-String -Path ".\services\api\ocr_math_normalizer.py" -SimpleMatch "x₀" -Quiet)
  normalizer_has_subset_real = (Select-String -Path ".\services\api\ocr_math_normalizer.py" -SimpleMatch "⊂ ℝ" -Quiet)
  normalizer_has_element_real = (Select-String -Path ".\services\api\ocr_math_normalizer.py" -SimpleMatch "∈ ℝ" -Quiet)
}

$Markers.GetEnumerator() |
  ForEach-Object { "$($_.Key)=$($_.Value)" } |
  Tee-Object "$Evidence\marker-checks.txt"

foreach ($Marker in $Markers.GetEnumerator()) {
  if (-not $Marker.Value) {
    throw "Marker validation failed: $($Marker.Key)"
  }
}

Write-Host "`n--- Normalizer self-test ---" -ForegroundColor Yellow
python -m ocr_math_normalizer --self-test 2>&1 |
  Tee-Object "$Evidence\normalizer-self-test.json"

Write-Host "`n--- Hook disabled/enabled smoke ---" -ForegroundColor Yellow
$Stem = [System.IO.Path]::GetFileNameWithoutExtension($Pdf)
$OutDir = Join-Path $Project "data\output\$Stem"

if (-not (Test-Path $OutDir)) {
  throw "Output folder not found: $OutDir"
}

$env:VOILA_ENABLE_OCR_MATH_REPORT_HOOK = ""
python -m ocr_math_report_hook `
  --output-folder "$OutDir" `
  --pdf-name "$Pdf" 2>&1 |
  Tee-Object "$Evidence\hook-disabled-output.json"

$env:VOILA_ENABLE_OCR_MATH_REPORT_HOOK = "1"
python -m ocr_math_report_hook `
  --output-folder "$OutDir" `
  --pdf-name "$Pdf" `
  --enable `
  --reason "final-status-check" 2>&1 |
  Tee-Object "$Evidence\hook-enabled-output.json"

$ReportJson = Join-Path $OutDir "ocr_math_report.json"
$ReportMd = Join-Path $OutDir "ocr_math_report.md"

if (-not (Test-Path $ReportJson)) {
  throw "Missing OCR math report JSON: $ReportJson"
}

if (-not (Test-Path $ReportMd)) {
  throw "Missing OCR math report Markdown: $ReportMd"
}

$Report = Get-Content $ReportJson -Raw -Encoding UTF8 | ConvertFrom-Json

if ([int]$Report.total_suggestions -lt 1) {
  throw "OCR math report has no suggestions."
}

Copy-Item -Force $ReportJson "$Evidence\ocr_math_report.json"
Copy-Item -Force $ReportMd "$Evidence\ocr_math_report.md"

@"
VOILA_V0_7_0_OCR_MATH_FINAL_STATUS_CHECK=PASS
PDF=$Pdf
OutputFolder=$OutDir
total_suggestions=$($Report.total_suggestions)
changed_line_count=$($Report.changed_line_count)
Policy=owner-local diagnostic only; no OCR rewrite; no Study/Progress change; no build; no ZIP; no delivery; no distribution
"@ | Tee-Object "$Evidence\summary.txt"

Write-Host "`nDONE: v0.7.0 OCR math final status check passed." -ForegroundColor Green
# Validation marker: No build, no ZIP, no delivery, no distribution.
