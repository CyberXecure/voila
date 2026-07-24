$ErrorActionPreference = "Stop"

Write-Output "v0.8.71 manual visual validation gate check: start"

python -m py_compile scripts/dev/apply-bbox-visual-validation-decisions.py
python -m py_compile scripts/dev/check-manual-visual-validation-gate-no-share-no-delivery.py

python scripts/dev/check-manual-visual-validation-gate-no-share-no-delivery.py
