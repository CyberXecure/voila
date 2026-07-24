$ErrorActionPreference = "Stop"

Write-Output "v0.8.84 Clean Study preview visual items read-only UI plan check: start"

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

& $Python -m py_compile scripts/dev/check-clean-study-preview-visual-items-readonly-ui-plan-no-share-no-delivery.py
& $Python scripts/dev/check-clean-study-preview-visual-items-readonly-ui-plan-no-share-no-delivery.py
