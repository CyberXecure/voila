$ErrorActionPreference = "Stop"

Write-Output "v0.8.70 OCR Math on crop candidate check: start"

python -m py_compile scripts/dev/run-ocrmath-on-bbox-crops.py
python -m py_compile scripts/dev/check-ocrmath-on-crop-candidate-no-share-no-delivery.py

python scripts/dev/check-ocrmath-on-crop-candidate-no-share-no-delivery.py
