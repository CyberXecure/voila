$ErrorActionPreference = "Stop"

Write-Output "v0.8.53 Corecturi sugerate read-only queue check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-corrections-suggested-read-only-queue-from-existing-languagetool-artifacts-no-build-no-zip-no-share-no-delivery.py

python scripts/dev/check-corrections-suggested-read-only-queue-from-existing-languagetool-artifacts-no-build-no-zip-no-share-no-delivery.py
