$ErrorActionPreference = "Stop"

Write-Output "v0.8.88 Real-course Review-to-Clean-Study visual flow manual smoke check: start"

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

& $Python -m py_compile scripts/dev/check-real-course-review-to-clean-study-visual-flow-manual-smoke-no-share-no-delivery.py
& $Python scripts/dev/check-real-course-review-to-clean-study-visual-flow-manual-smoke-no-share-no-delivery.py
