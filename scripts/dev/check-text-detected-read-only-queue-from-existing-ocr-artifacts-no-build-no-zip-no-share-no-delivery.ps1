$ErrorActionPreference = "Stop"

Write-Output "v0.8.52 Text detectat read-only queue check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-text-detected-read-only-queue-from-existing-ocr-artifacts-no-build-no-zip-no-share-no-delivery.py

python scripts/dev/check-text-detected-read-only-queue-from-existing-ocr-artifacts-no-build-no-zip-no-share-no-delivery.py
