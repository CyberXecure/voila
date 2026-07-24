$ErrorActionPreference = "Stop"

Write-Output "v0.8.82 Review Document Clean Study refresh UI control check: start"

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

& $Python -m py_compile services/api/web_app.py
& $Python -m py_compile scripts/dev/apply-review-document-clean-study-refresh-ui-control-v0882.py
& $Python -m py_compile scripts/dev/check-review-document-clean-study-refresh-ui-control-no-share-no-delivery.py
& $Python scripts/dev/check-review-document-clean-study-refresh-ui-control-no-share-no-delivery.py
