$ErrorActionPreference = "Stop"

Write-Output "v0.7.94 direction charter check: start"

python -m py_compile scripts/dev/check-voila-direction-charter-no-build-no-zip-no-delivery.py
python scripts/dev/check-voila-direction-charter-no-build-no-zip-no-delivery.py
