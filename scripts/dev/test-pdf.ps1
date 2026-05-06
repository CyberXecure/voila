$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $ScriptDir "..\.."))

Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "Virtual environment Python not found. Run: python -m venv .venv"
}

$RequiredScripts = @(
    ".\services\api\pdf_extract.py",
    ".\services\api\ocr_report.py",
    ".\services\api\outline_builder.py",
    ".\services\api\normalize_outline.py",
    ".\services\api\course_generator.py",
    ".\services\api\course_polisher.py",
    ".\services\api\course_cleaned_finalizer.py",
    ".\services\api\study_quiz_builder.py",
    ".\services\api\figure_exporter_hybrid.py",
    ".\services\api\html_exporter.py"
)

foreach ($Script in $RequiredScripts) {
    if (-not (Test-Path $Script)) {
        throw "Missing required script: $Script"
    }
}

$CropConfig = ".\data\figure_crops.anchor.json"

if (-not (Test-Path $CropConfig)) {
    throw "Missing figure crop config: $CropConfig"
}

$pdf = Get-ChildItem -Path ".\data\input" -Filter "*.pdf" |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

if (-not $pdf) {
    Write-Host ""
    Write-Host "Nu am găsit niciun PDF în:"
    Write-Host "  $ProjectRoot\data\input"
    Write-Host ""
    Write-Host "Copiază un PDF acolo, apoi rulează:"
    Write-Host "  .\scripts\dev\test-pdf.ps1"
    exit 1
}

Write-Host ""
Write-Host "=== Voila! v0.1 input PDF ==="
Write-Host $pdf.FullName

Write-Host ""
Write-Host "=== 1. PDF extract ==="
& $Python .\services\api\pdf_extract.py $pdf.FullName --output-dir .\data\output

$outputDir = Join-Path ".\data\output" $pdf.BaseName
$pagesJson = Join-Path $outputDir "pages.json"

if (-not (Test-Path $pagesJson)) {
    throw "pages.json was not generated: $pagesJson"
}

Write-Host ""
Write-Host "=== 2. OCR report ==="
& $Python .\services\api\ocr_report.py $pagesJson

Write-Host ""
Write-Host "=== 3. Course outline ==="
& $Python .\services\api\outline_builder.py $pagesJson

$outlineJson = Join-Path $outputDir "course_outline.json"

if (-not (Test-Path $outlineJson)) {
    throw "course_outline.json was not generated: $outlineJson"
}

Write-Host ""
Write-Host "=== 4. Normalize outline ==="
& $Python .\services\api\normalize_outline.py $outlineJson

$normalizedJson = Join-Path $outputDir "course_outline.normalized.json"

if (-not (Test-Path $normalizedJson)) {
    throw "course_outline.normalized.json was not generated: $normalizedJson"
}

Write-Host ""
Write-Host "=== 5. Generate course files ==="
& $Python .\services\api\course_generator.py $normalizedJson

Write-Host ""
Write-Host "=== 6. Polish course ==="
& $Python .\services\api\course_polisher.py $normalizedJson

$courseCleaned = Join-Path $outputDir "course.cleaned.md"

if (-not (Test-Path $courseCleaned)) {
    throw "course.cleaned.md was not generated: $courseCleaned"
}

Write-Host ""
Write-Host "=== 7. Final cleanup ==="
& $Python .\services\api\course_cleaned_finalizer.py $courseCleaned

Write-Host ""
Write-Host "=== 8. Build study quiz ==="

$StudyConfigPath = ".\data\study_config.json"
$StudyMinPage = 1

if (Test-Path $StudyConfigPath) {
    $StudyConfig = Get-Content $StudyConfigPath -Raw | ConvertFrom-Json

    if ($StudyConfig.default_min_page) {
        $StudyMinPage = [int]$StudyConfig.default_min_page
    }

    if ($StudyConfig.per_pdf.$($pdf.BaseName).min_page) {
        $StudyMinPage = [int]$StudyConfig.per_pdf.$($pdf.BaseName).min_page
    }
}

& $Python .\services\api\study_quiz_builder.py $outputDir --min-page $StudyMinPage --max-per-lesson 4 --max-total 350

Write-Host ""
Write-Host "=== 9. Export figures ==="
& $Python .\services\api\figure_exporter_hybrid.py $pdf.FullName

Write-Host ""
Write-Host "=== 10. Export HTML course ==="
& $Python .\services\api\html_exporter.py $courseCleaned

$htmlCourse = Join-Path $outputDir "course.cleaned.html"
$figuresHtml = Join-Path $outputDir "figures\figures.html"

if (-not (Test-Path $htmlCourse)) {
    throw "course.cleaned.html was not generated: $htmlCourse"
}

Write-Host ""
Write-Host "=== Generated files ==="
Get-ChildItem $outputDir |
  Select-Object Name, Length, LastWriteTime |
  Format-Table -AutoSize

Write-Host ""
Write-Host "=== Main output files ==="
Write-Host "Course HTML:"
Write-Host "  $htmlCourse"
Write-Host "Clean Markdown:"
Write-Host "  $courseCleaned"
Write-Host "Figures gallery:"
Write-Host "  $figuresHtml"
Write-Host "Glossary:"
Write-Host "  $outputDir\glossary.json"
Write-Host "Quiz:"
Write-Host "  $outputDir\quiz.json"
Write-Host "Flashcards:"
Write-Host "  $outputDir\flashcards.json"
Write-Host "OCR corrections:"
Write-Host "  $outputDir\ocr_corrections.json"

Write-Host ""
Write-Host "Done."


