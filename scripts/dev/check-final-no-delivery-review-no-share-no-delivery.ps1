$ErrorActionPreference = "Stop"

Write-Output "v0.8.40 Final no-delivery review check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-final-no-delivery-review-no-share-no-delivery.py

.\scripts\dev\stop-voila.ps1

python scripts/dev/check-final-no-delivery-review-no-share-no-delivery.py
