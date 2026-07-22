$ErrorActionPreference = "Stop"

Write-Output "v0.8.59 UI polish/readability pass check: start"

python -m py_compile scripts/dev/check-ui-polish-readability-pass-no-build-no-zip-no-share-no-delivery.py

.\scripts\dev\stop-voila.ps1
.\scripts\dev\start-voila.ps1 -Silent

python scripts/dev/check-ui-polish-readability-pass-no-build-no-zip-no-share-no-delivery.py
