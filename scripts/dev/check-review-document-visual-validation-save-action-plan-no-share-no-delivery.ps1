$ErrorActionPreference = "Stop"

Write-Output "v0.8.76 Review Document visual validation save-action plan check: start"

python -m py_compile scripts/dev/check-review-document-visual-validation-save-action-plan-no-share-no-delivery.py

python scripts/dev/check-review-document-visual-validation-save-action-plan-no-share-no-delivery.py
