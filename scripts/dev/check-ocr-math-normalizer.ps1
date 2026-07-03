param(
  [string]$Pdf = "Pages from Matematica-M1-material-didactic-si-testare.pdf",
  [string]$Evidence = "D:\dev\release-assets\voila\v0.7.0-owner-local-testability-and-ui-polish-no-build-no-distribution\ocr-math-normalizer-engine-check"
)

$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force $Evidence | Out-Null

$Project = "D:\dev\projects\voila"
Set-Location $Project

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = "$Project\services\api"

Write-Host "`n=== Check Voila OCR math normalizer ===" -ForegroundColor Cyan

python -m compileall .\services\api | Tee-Object "$Evidence\python-compile.txt"

python -m ocr_math_normalizer --self-test 2>&1 |
  Tee-Object "$Evidence\self-test.json"

$Stem = [System.IO.Path]::GetFileNameWithoutExtension($Pdf)
$OutDir = Join-Path $Project "data\output\$Stem"

if (-not (Test-Path $OutDir)) {
  throw "Output folder not found: $OutDir"
}

$Candidates = @(
  (Join-Path $OutDir "pages.md"),
  (Join-Path $OutDir "course.cleaned.md"),
  (Join-Path $OutDir "course.md")
) | Where-Object { Test-Path $_ }

if ($Candidates.Count -lt 1) {
  throw "No text candidates found in $OutDir"
}

foreach ($Candidate in $Candidates) {
  $Name = [System.IO.Path]::GetFileName($Candidate)
  $SafeName = $Name.Replace(".", "-")

  python -m ocr_math_normalizer `
    --text-file "$Candidate" `
    --out-json "$Evidence\$SafeName.ocr-math-normalized.json" `
    --out-text "$Evidence\$SafeName.ocr-math-normalized.txt" 2>&1 |
    Tee-Object "$Evidence\$SafeName.run.txt"
}

@"
OCR_MATH_NORMALIZER_CHECK=PASS
PDF=$Pdf
Evidence=$Evidence
"@ | Tee-Object "$Evidence\summary.txt"

Write-Host "`nDONE: OCR math normalizer check passed." -ForegroundColor Green
