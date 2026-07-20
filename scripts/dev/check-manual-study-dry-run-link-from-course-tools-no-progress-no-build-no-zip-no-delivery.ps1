$ErrorActionPreference = "Stop"

Write-Output "v0.8.19 Manual Study dry-run link from Course Tools check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-manual-study-dry-run-link-from-course-tools-no-progress-no-build-no-zip-no-delivery.py

.\scripts\dev\stop-voila.ps1
.\scripts\dev\start-voila.ps1 -Silent
Start-Sleep -Seconds 3

python scripts/dev/check-manual-study-dry-run-link-from-course-tools-no-progress-no-build-no-zip-no-delivery.py
