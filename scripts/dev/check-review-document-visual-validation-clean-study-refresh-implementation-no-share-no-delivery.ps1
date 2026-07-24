$ErrorActionPreference = "Stop"

Write-Output "v0.8.81 Review Document visual validation Clean Study refresh implementation check: start"

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

& $Python -m py_compile services/api/web_app.py
& $Python -m py_compile scripts/dev/apply-review-document-clean-study-refresh-action-v0881.py
& $Python -m py_compile scripts/dev/check-review-document-visual-validation-clean-study-refresh-implementation-no-share-no-delivery.py
& $Python scripts/dev/check-review-document-visual-validation-clean-study-refresh-implementation-no-share-no-delivery.py
