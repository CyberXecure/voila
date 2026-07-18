$ErrorActionPreference = "Stop"

Write-Output "v0.7.95 Manual Learning Evidence UI design check: start"

python -m py_compile scripts/dev/check-manual-learning-evidence-ui-design-no-build-no-zip-no-delivery.py
python scripts/dev/check-manual-learning-evidence-ui-design-no-build-no-zip-no-delivery.py
