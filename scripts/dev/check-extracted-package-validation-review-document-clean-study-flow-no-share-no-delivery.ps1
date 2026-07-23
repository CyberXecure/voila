$ErrorActionPreference = "Stop"

Write-Output "v0.8.62 Extracted package validation check: start"

python -m py_compile scripts/dev/check-extracted-package-validation-review-document-clean-study-flow-no-share-no-delivery.py

python scripts/dev/check-extracted-package-validation-review-document-clean-study-flow-no-share-no-delivery.py
