$ErrorActionPreference = "Stop"

Write-Output "v0.8.5 Manual Learning Evidence accepted preview check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-manual-learning-evidence-accepted-preview-no-learning-pack-no-build-no-zip-no-delivery.py

.\scripts\dev\stop-voila.ps1
.\scripts\dev\start-voila.ps1 -Silent
Start-Sleep -Seconds 3

python scripts/dev/check-manual-learning-evidence-accepted-preview-no-learning-pack-no-build-no-zip-no-delivery.py
