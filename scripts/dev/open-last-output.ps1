$ErrorActionPreference = "Stop"

$ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
Set-Location $ProjectRoot

$pdf = Get-ChildItem .\data\input -Filter "*.pdf" |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

if (-not $pdf) {
    throw "No PDF found in data/input."
}

$OutDir = Join-Path ".\data\output" $pdf.BaseName
$CourseHtml = Join-Path $OutDir "course.cleaned.html"
$FiguresHtml = Join-Path $OutDir "figures\figures.html"

if (Test-Path $CourseHtml) {
    Start-Process $CourseHtml
}
else {
    Write-Host "Course HTML not found:"
    Write-Host $CourseHtml
}

if (Test-Path $FiguresHtml) {
    Start-Process $FiguresHtml
}
else {
    Write-Host "Figures HTML not found:"
    Write-Host $FiguresHtml
}
