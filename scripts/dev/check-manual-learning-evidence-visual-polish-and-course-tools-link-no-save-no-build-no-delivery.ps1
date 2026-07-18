$ErrorActionPreference = "Stop"

Write-Output "v0.7.97 Manual Learning Evidence visual polish + Course Tools link check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-manual-learning-evidence-ui-skeleton-no-build-no-zip-no-delivery.py
python -m py_compile scripts/dev/check-manual-learning-evidence-visual-polish-and-course-tools-link-no-save-no-build-no-delivery.py

.\scripts\dev\stop-voila.ps1
.\scripts\dev\start-voila.ps1 -Silent
Start-Sleep -Seconds 3

python scripts/dev/check-manual-learning-evidence-ui-skeleton-no-build-no-zip-no-delivery.py
python scripts/dev/check-manual-learning-evidence-visual-polish-and-course-tools-link-no-save-no-build-no-delivery.py
