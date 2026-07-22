$ErrorActionPreference = "Stop"

Write-Output "v0.8.56 Safe local save for explanation drafts check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-safe-local-save-for-explanation-drafts-no-build-no-zip-no-share-no-delivery.py

python scripts/dev/check-safe-local-save-for-explanation-drafts-no-build-no-zip-no-share-no-delivery.py
