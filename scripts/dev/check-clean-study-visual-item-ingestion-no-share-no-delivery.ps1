$ErrorActionPreference = "Stop"

Write-Output "v0.8.72 clean Study visual item ingestion check: start"

python -m py_compile scripts/dev/build-clean-study-visual-items-from-bbox.py
python -m py_compile scripts/dev/check-clean-study-visual-item-ingestion-no-share-no-delivery.py

python scripts/dev/check-clean-study-visual-item-ingestion-no-share-no-delivery.py
