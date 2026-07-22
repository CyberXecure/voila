$ErrorActionPreference = "Stop"

Write-Output "v0.8.61 Package rebuild check: start"

python -m py_compile scripts/dev/check-package-rebuild-with-review-document-clean-study-flow-no-share-no-delivery.py

python scripts/dev/check-package-rebuild-with-review-document-clean-study-flow-no-share-no-delivery.py
