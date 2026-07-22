$ErrorActionPreference = "Stop"

Write-Output "v0.8.44 Review Document shell design check: start"

python -m py_compile scripts/dev/check-review-document-shell-design-no-build-no-zip-no-share-no-delivery.py

python scripts/dev/check-review-document-shell-design-no-build-no-zip-no-share-no-delivery.py
