param(
  [string]$Pdf = "Pages from Matematica-M1-material-didactic-si-testare.pdf",
  [string]$Evidence = "D:\dev\release-assets\voila\v0.7.0-owner-local-testability-and-ui-polish-no-build-no-distribution\ocr-math-generate-guarded-hook-check"
)

$ErrorActionPreference = "Stop"

$Project = "D:\dev\projects\voila"
Set-Location $Project

New-Item -ItemType Directory -Force $Evidence | Out-Null

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = "$Project\services\api"

Write-Host "`n=== Check guarded OCR math Generate hook ===" -ForegroundColor Cyan

python -m compileall .\services\api | Tee-Object "$Evidence\python-compile.txt"

$MarkerFound = Select-String -Path ".\services\api\web_app.py" -SimpleMatch "VOILA_OCR_MATH_REPORT_HOOK_GENERATE_V1" -Quiet
if (-not $MarkerFound) {
  throw "Generate hook marker missing."
}

$HookImportFound = Select-String -Path ".\services\api\web_app.py" -SimpleMatch "from ocr_math_report_hook import build_ocr_math_report_if_enabled" -Quiet
if (-not $HookImportFound) {
  throw "Generate hook import missing."
}

$Stem = [System.IO.Path]::GetFileNameWithoutExtension($Pdf)
$OutDir = Join-Path $Project "data\output\$Stem"

if (-not (Test-Path $OutDir)) {
  throw "Output folder not found: $OutDir"
}

Write-Host "`n--- Disabled hook direct smoke ---" -ForegroundColor Yellow
$env:VOILA_ENABLE_OCR_MATH_REPORT_HOOK = ""
python -m ocr_math_report_hook `
  --output-folder "$OutDir" `
  --pdf-name "$Pdf" 2>&1 |
  Tee-Object "$Evidence\hook-disabled-output.json"

Write-Host "`n--- Enabled hook direct smoke ---" -ForegroundColor Yellow
$env:VOILA_ENABLE_OCR_MATH_REPORT_HOOK = "1"
python -m ocr_math_report_hook `
  --output-folder "$OutDir" `
  --pdf-name "$Pdf" `
  --enable `
  --reason "generate-hook-check" 2>&1 |
  Tee-Object "$Evidence\hook-enabled-output.json"

$ReportJson = Join-Path $OutDir "ocr_math_report.json"
$ReportMd = Join-Path $OutDir "ocr_math_report.md"

if (-not (Test-Path $ReportJson)) {
  throw "Missing report JSON after enabled smoke: $ReportJson"
}

if (-not (Test-Path $ReportMd)) {
  throw "Missing report Markdown after enabled smoke: $ReportMd"
}

Copy-Item -Force $ReportJson "$Evidence\ocr_math_report.json"
Copy-Item -Force $ReportMd "$Evidence\ocr_math_report.md"

@"
OCR_MATH_GENERATE_GUARDED_HOOK_CHECK=PASS
PDF=$Pdf
OutputFolder=$OutDir
ReportJson=$ReportJson
ReportMarkdown=$ReportMd
Policy=guarded owner-local diagnostic only; no OCR rewrite; no Study/Progress change; no build; no ZIP; no delivery; no distribution
"@ | Tee-Object "$Evidence\summary.txt"

Write-Host "`nDONE: guarded OCR math Generate hook check passed." -ForegroundColor Green
