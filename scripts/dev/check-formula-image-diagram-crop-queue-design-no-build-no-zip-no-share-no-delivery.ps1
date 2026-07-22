$ErrorActionPreference = "Stop"

Write-Output "v0.8.46 Formula/image/diagram/crop queue design check: start"

python -m py_compile scripts/dev/check-formula-image-diagram-crop-queue-design-no-build-no-zip-no-share-no-delivery.py

python scripts/dev/check-formula-image-diagram-crop-queue-design-no-build-no-zip-no-share-no-delivery.py
