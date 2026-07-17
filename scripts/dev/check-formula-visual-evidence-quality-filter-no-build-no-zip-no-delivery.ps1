$ErrorActionPreference = "Stop"

Write-Output "v0.7.92 check: start"

python -m py_compile scripts/dev/build-formula-visual-evidence-manifest.py
python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-formula-visual-evidence-quality-filter-no-build-no-zip-no-delivery.py

$env:PYTHONPATH = "D:\dev\projects\voila\services\api"
python scripts/dev/check-formula-visual-evidence-quality-filter-no-build-no-zip-no-delivery.py
