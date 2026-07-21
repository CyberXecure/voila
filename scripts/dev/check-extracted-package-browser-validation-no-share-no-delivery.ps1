$ErrorActionPreference = "Stop"

Write-Output "v0.8.35 Extracted package browser validation blocker check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-extracted-package-browser-validation-no-share-no-delivery.py

.\scripts\dev\stop-voila.ps1

python scripts/dev/check-extracted-package-browser-validation-no-share-no-delivery.py
