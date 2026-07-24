$ErrorActionPreference = "Stop"

Write-Output "v0.8.78 Review Document visual validation form controls check: start"

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

& $Python -m py_compile services/api/web_app.py
& $Python -m py_compile scripts/dev/apply-review-document-visual-validation-form-controls-v0878.py
& $Python -m py_compile scripts/dev/check-review-document-visual-validation-form-controls-no-share-no-delivery.py
& $Python scripts/dev/check-review-document-visual-validation-form-controls-no-share-no-delivery.py
