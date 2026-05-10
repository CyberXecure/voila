$ErrorActionPreference = "Stop"

$ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$TessdataDir = Join-Path $ProjectRoot ".tessdata"

New-Item -ItemType Directory -Force -Path $TessdataDir | Out-Null

$BaseUrl = "https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main"

$Langs = @(
  "eng",
  "ron",
  "fra",
  "deu",
  "rus",
  "ita",
  "spa",
  "por"
)

foreach ($lang in $Langs) {
  $out = Join-Path $TessdataDir "$lang.traineddata"
  $url = "$BaseUrl/$lang.traineddata"

  if (Test-Path $out) {
    Write-Host "OK exists: $lang"
    continue
  }

  Write-Host "Downloading $lang..."
  Invoke-WebRequest $url -OutFile $out
}

Write-Host ""
Write-Host "Installed OCR languages:"
Get-ChildItem $TessdataDir -Filter "*.traineddata" |
  Select-Object Name,Length |
  Sort-Object Name
