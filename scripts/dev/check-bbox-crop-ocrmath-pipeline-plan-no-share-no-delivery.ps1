$ErrorActionPreference = "Stop"

Write-Output "v0.8.65 bbox/crop/OCR Math pipeline plan check: start"

python -m py_compile scripts/dev/check-bbox-crop-ocrmath-pipeline-plan-no-share-no-delivery.py

python scripts/dev/check-bbox-crop-ocrmath-pipeline-plan-no-share-no-delivery.py
