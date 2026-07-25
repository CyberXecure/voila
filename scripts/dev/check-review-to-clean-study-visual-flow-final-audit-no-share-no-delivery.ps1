$ErrorActionPreference = "Stop"

Write-Output "v0.8.87 Review-to-Clean-Study visual flow final audit check: start"

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

& $Python -m py_compile scripts/dev/check-review-to-clean-study-visual-flow-final-audit-no-share-no-delivery.py
& $Python scripts/dev/check-review-to-clean-study-visual-flow-final-audit-no-share-no-delivery.py
