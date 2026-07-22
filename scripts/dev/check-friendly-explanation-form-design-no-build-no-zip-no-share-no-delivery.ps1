$ErrorActionPreference = "Stop"

Write-Output "v0.8.47 Friendly explanation form design check: start"

python -m py_compile scripts/dev/check-friendly-explanation-form-design-no-build-no-zip-no-share-no-delivery.py

python scripts/dev/check-friendly-explanation-form-design-no-build-no-zip-no-share-no-delivery.py
