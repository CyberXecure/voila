$ErrorActionPreference = "Stop"

Write-Output "v0.8.55 Friendly explanation form read-only static draft shell check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-friendly-explanation-form-read-only-static-draft-shell-no-build-no-zip-no-share-no-delivery.py

python scripts/dev/check-friendly-explanation-form-read-only-static-draft-shell-no-build-no-zip-no-share-no-delivery.py
