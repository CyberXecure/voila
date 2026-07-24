$ErrorActionPreference = "Stop"

Write-Output "v0.8.73 Review Document visual validation UI plan check: start"

python -m py_compile scripts/dev/check-review-document-visual-validation-ui-plan-no-share-no-delivery.py

python scripts/dev/check-review-document-visual-validation-ui-plan-no-share-no-delivery.py
