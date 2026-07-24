$ErrorActionPreference = "Stop"

Write-Output "v0.8.80 Review Document visual validation Clean Study refresh plan check: start"

python -m py_compile scripts/dev/check-review-document-visual-validation-clean-study-refresh-plan-no-share-no-delivery.py

python scripts/dev/check-review-document-visual-validation-clean-study-refresh-plan-no-share-no-delivery.py
