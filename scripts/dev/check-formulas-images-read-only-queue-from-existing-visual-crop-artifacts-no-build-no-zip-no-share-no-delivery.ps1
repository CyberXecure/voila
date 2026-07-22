$ErrorActionPreference = "Stop"

Write-Output "v0.8.54 Formule și imagini read-only queue check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-formulas-images-read-only-queue-from-existing-visual-crop-artifacts-no-build-no-zip-no-share-no-delivery.py

python scripts/dev/check-formulas-images-read-only-queue-from-existing-visual-crop-artifacts-no-build-no-zip-no-share-no-delivery.py
