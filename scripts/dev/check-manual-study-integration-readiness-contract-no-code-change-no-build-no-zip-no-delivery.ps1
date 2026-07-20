$ErrorActionPreference = "Stop"

Write-Output "v0.8.17 Manual Study integration readiness contract check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-manual-study-integration-readiness-contract-no-code-change-no-build-no-zip-no-delivery.py

python scripts/dev/check-manual-study-integration-readiness-contract-no-code-change-no-build-no-zip-no-delivery.py
