$ErrorActionPreference = "Stop"

Write-Output "v0.8.66 hide deprecated visual/OCR Math user links check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-hide-deprecated-visual-ocrmath-user-links-no-share-no-delivery.py

python scripts/dev/check-hide-deprecated-visual-ocrmath-user-links-no-share-no-delivery.py
