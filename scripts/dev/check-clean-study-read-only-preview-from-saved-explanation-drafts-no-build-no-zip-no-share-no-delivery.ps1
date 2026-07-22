$ErrorActionPreference = "Stop"

Write-Output "v0.8.57 Clean Study read-only preview check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-clean-study-read-only-preview-from-saved-explanation-drafts-no-build-no-zip-no-share-no-delivery.py

.\scripts\dev\stop-voila.ps1
.\scripts\dev\start-voila.ps1 -Silent

python scripts/dev/check-clean-study-read-only-preview-from-saved-explanation-drafts-no-build-no-zip-no-share-no-delivery.py
