$ErrorActionPreference = "Stop"

Write-Output "v0.8.64 real upload-to-review pipeline audit check: start"

python -m py_compile scripts/dev/check-real-upload-to-review-pipeline-audit-no-share-no-delivery.py

python scripts/dev/check-real-upload-to-review-pipeline-audit-no-share-no-delivery.py
