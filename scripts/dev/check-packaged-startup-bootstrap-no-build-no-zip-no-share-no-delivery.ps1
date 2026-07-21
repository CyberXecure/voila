$ErrorActionPreference = "Stop"

Write-Output "v0.8.37 Packaged startup bootstrap check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-packaged-startup-bootstrap-no-build-no-zip-no-share-no-delivery.py

.\scripts\dev\stop-voila.ps1

python scripts/dev/check-packaged-startup-bootstrap-no-build-no-zip-no-share-no-delivery.py
