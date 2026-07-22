$ErrorActionPreference = "Stop"

Write-Output "v0.8.60 Package rebuild preflight check: start"

python -m py_compile scripts/dev/check-package-rebuild-preflight-after-owner-approval-no-build-no-zip-no-share-no-delivery.py

.\scripts\dev\stop-voila.ps1
.\scripts\dev\start-voila.ps1 -Silent

python scripts/dev/check-package-rebuild-preflight-after-owner-approval-no-build-no-zip-no-share-no-delivery.py
