$ErrorActionPreference = "Stop"

Write-Output "v0.8.41 Owner personal Manual Study workflow smoke check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-owner-personal-manual-study-workflow-smoke-no-share-no-delivery.py

python scripts/dev/check-owner-personal-manual-study-workflow-smoke-no-share-no-delivery.py
