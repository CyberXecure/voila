$ErrorActionPreference = "Stop"

Write-Output "v0.8.86 Clean Study preview visual items read-only UI smoke check: start"

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

& $Python -m py_compile scripts/dev/check-clean-study-preview-visual-items-readonly-ui-smoke-no-share-no-delivery.py
& $Python scripts/dev/check-clean-study-preview-visual-items-readonly-ui-smoke-no-share-no-delivery.py
