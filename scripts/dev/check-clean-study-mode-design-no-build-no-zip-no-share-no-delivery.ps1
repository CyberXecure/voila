$ErrorActionPreference = "Stop"

Write-Output "v0.8.48 Clean Study mode design check: start"

python -m py_compile scripts/dev/check-clean-study-mode-design-no-build-no-zip-no-share-no-delivery.py

python scripts/dev/check-clean-study-mode-design-no-build-no-zip-no-share-no-delivery.py
