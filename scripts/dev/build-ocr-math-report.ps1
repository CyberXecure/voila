param(
  [string]$Pdf = "Pages from Matematica-M1-material-didactic-si-testare.pdf",
  [string]$Evidence = "D:\dev\release-assets\voila\v0.7.0-owner-local-testability-and-ui-polish-no-build-no-distribution\ocr-math-diagnostic-report-check"
)

$ErrorActionPreference = "Stop"

$Project = "D:\dev\projects\voila"
Set-Location $Project

New-Item -ItemType Directory -Force $Evidence | Out-Null

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = "$Project\services\api"

Write-Host "`n=== Build Voila OCR math diagnostic report ===" -ForegroundColor Cyan

python -m compileall .\services\api | Tee-Object "$Evidence\python-compile.txt"

$Stem = [System.IO.Path]::GetFileNameWithoutExtension($Pdf)
$OutDir = Join-Path $Project "data\output\$Stem"

if (-not (Test-Path $OutDir)) {
  throw "Output folder not found: $OutDir"
}

python -m ocr_math_report `
  --output-folder "$OutDir" `
  --pdf-name "$Pdf" 2>&1 |
  Tee-Object "$Evidence\ocr-math-report-output.json"

$ReportJson = Join-Path $OutDir "ocr_math_report.json"
$ReportMd = Join-Path $OutDir "ocr_math_report.md"

if (-not (Test-Path $ReportJson)) {
  throw "Missing report JSON: $ReportJson"
}

if (-not (Test-Path $ReportMd)) {
  throw "Missing report Markdown: $ReportMd"
}

Copy-Item -Force $ReportJson "$Evidence\ocr_math_report.json"
Copy-Item -Force $ReportMd "$Evidence\ocr_math_report.md"

@"
OCR_MATH_DIAGNOSTIC_REPORT_CHECK=PASS
PDF=$Pdf
OutputFolder=$OutDir
ReportJson=$ReportJson
ReportMarkdown=$ReportMd
Evidence=$Evidence
"@ | Tee-Object "$Evidence\summary.txt"

Write-Host "`nDONE: OCR math diagnostic report check passed." -ForegroundColor Green
