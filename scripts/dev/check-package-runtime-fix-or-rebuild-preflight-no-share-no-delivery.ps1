$ErrorActionPreference = "Stop"

Write-Output "v0.8.36 Package runtime fix/rebuild preflight check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-package-runtime-fix-or-rebuild-preflight-no-share-no-delivery.py

.\scripts\dev\stop-voila.ps1

python scripts/dev/check-package-runtime-fix-or-rebuild-preflight-no-share-no-delivery.py
