$ErrorActionPreference = "Stop"

Write-Output "v0.8.89 Real-course Review-to-Clean-Study visual flow final readiness audit check: start"

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

& $Python -m py_compile scripts/dev/check-real-course-review-to-clean-study-visual-flow-final-readiness-audit-no-share-no-delivery.py
& $Python scripts/dev/check-real-course-review-to-clean-study-visual-flow-final-readiness-audit-no-share-no-delivery.py
