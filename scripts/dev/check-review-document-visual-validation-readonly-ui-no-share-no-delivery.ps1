$ErrorActionPreference = "Stop"

Write-Output "v0.8.74 Review Document visual validation read-only UI check: start"

python -m py_compile scripts/dev/apply-review-document-visual-validation-readonly-ui-v0874.py
python -m py_compile scripts/dev/check-review-document-visual-validation-readonly-ui-no-share-no-delivery.py

python scripts/dev/check-review-document-visual-validation-readonly-ui-no-share-no-delivery.py
