$ErrorActionPreference = "Stop"

Write-Output "v0.8.69 real crop artifact from bbox check: start"

python -m py_compile scripts/dev/build-bbox-visual-crops.py
python -m py_compile scripts/dev/check-real-crop-artifact-from-bbox-no-share-no-delivery.py

python scripts/dev/check-real-crop-artifact-from-bbox-no-share-no-delivery.py
