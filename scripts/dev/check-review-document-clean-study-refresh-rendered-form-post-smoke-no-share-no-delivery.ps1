$ErrorActionPreference = "Stop"

Write-Output "v0.8.83 Review Document Clean Study refresh rendered-form POST smoke check: start"

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

& $Python -m py_compile scripts/dev/check-review-document-clean-study-refresh-rendered-form-post-smoke-no-share-no-delivery.py
& $Python scripts/dev/check-review-document-clean-study-refresh-rendered-form-post-smoke-no-share-no-delivery.py
