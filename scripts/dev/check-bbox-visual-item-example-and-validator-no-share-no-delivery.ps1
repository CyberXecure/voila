$ErrorActionPreference = "Stop"

Write-Output "v0.8.68 bbox visual item example and validator check: start"

python -m py_compile scripts/dev/validate-bbox-visual-items.py
python -m py_compile scripts/dev/check-bbox-visual-item-example-and-validator-no-share-no-delivery.py

python scripts/dev/check-bbox-visual-item-example-and-validator-no-share-no-delivery.py
