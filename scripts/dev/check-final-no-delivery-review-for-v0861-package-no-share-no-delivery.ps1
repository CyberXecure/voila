$ErrorActionPreference = "Stop"

Write-Output "v0.8.63 Final no-delivery review check: start"

python -m py_compile scripts/dev/check-final-no-delivery-review-for-v0861-package-no-share-no-delivery.py

python scripts/dev/check-final-no-delivery-review-for-v0861-package-no-share-no-delivery.py
