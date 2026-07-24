$ErrorActionPreference = "Stop"

Write-Output "v0.8.75 Review Document visual validation read-only browser smoke: start"

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

& $Python -m py_compile scripts/dev/check-review-document-visual-validation-readonly-browser-smoke-no-share-no-delivery.py
& $Python scripts/dev/check-review-document-visual-validation-readonly-browser-smoke-no-share-no-delivery.py
