$ErrorActionPreference = "Stop"

Write-Output "v0.8.50 Review Document shell read-only first slice check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-review-document-shell-read-only-first-slice-no-build-no-zip-no-share-no-delivery.py

python scripts/dev/check-review-document-shell-read-only-first-slice-no-build-no-zip-no-share-no-delivery.py
