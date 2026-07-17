$ErrorActionPreference = "Stop"

Write-Output "v0.7.93 check: start"

python -m py_compile scripts/dev/check-crop-editor-formula-evidence-audit-no-build-no-zip-no-delivery.py
python scripts/dev/check-crop-editor-formula-evidence-audit-no-build-no-zip-no-delivery.py
