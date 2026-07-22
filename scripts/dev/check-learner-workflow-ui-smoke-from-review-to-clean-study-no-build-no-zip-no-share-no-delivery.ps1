$ErrorActionPreference = "Stop"

Write-Output "v0.8.58 Learner workflow UI smoke check: start"

python -m py_compile scripts/dev/check-learner-workflow-ui-smoke-from-review-to-clean-study-no-build-no-zip-no-share-no-delivery.py

.\scripts\dev\stop-voila.ps1
.\scripts\dev\start-voila.ps1 -Silent

python scripts/dev/check-learner-workflow-ui-smoke-from-review-to-clean-study-no-build-no-zip-no-share-no-delivery.py
