$ErrorActionPreference = "Stop"

Write-Output "v0.8.79 Review Document visual validation form controls POST smoke check: start"

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

& $Python -m py_compile scripts/dev/check-review-document-visual-validation-form-controls-post-smoke-no-share-no-delivery.py
& $Python scripts/dev/check-review-document-visual-validation-form-controls-post-smoke-no-share-no-delivery.py
