$ErrorActionPreference = "Stop"

Write-Output "v0.8.51 Course Tools link to Review Document shell check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-course-tools-link-to-review-document-shell-no-build-no-zip-no-share-no-delivery.py

python scripts/dev/check-course-tools-link-to-review-document-shell-no-build-no-zip-no-share-no-delivery.py
