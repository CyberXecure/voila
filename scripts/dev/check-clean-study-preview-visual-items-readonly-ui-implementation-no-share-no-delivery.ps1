$ErrorActionPreference = "Stop"

Write-Output "v0.8.85 Clean Study preview visual items read-only UI implementation check: start"

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

& $Python -m py_compile services/api/web_app.py
& $Python -m py_compile scripts/dev/apply-clean-study-preview-visual-items-readonly-ui-v0885.py
& $Python -m py_compile scripts/dev/check-clean-study-preview-visual-items-readonly-ui-implementation-no-share-no-delivery.py
& $Python scripts/dev/check-clean-study-preview-visual-items-readonly-ui-implementation-no-share-no-delivery.py
