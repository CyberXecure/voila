$ErrorActionPreference = "Stop"

Write-Output "v0.8.67 bbox visual item contract check: start"

python -m py_compile scripts/dev/check-bbox-visual-item-contract-no-share-no-delivery.py

python scripts/dev/check-bbox-visual-item-contract-no-share-no-delivery.py
