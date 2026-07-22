$ErrorActionPreference = "Stop"

Write-Output "v0.8.49 Learner workflow implementation preflight check: start"

python -m py_compile scripts/dev/check-learner-workflow-implementation-preflight-no-build-no-zip-no-share-no-delivery.py

python scripts/dev/check-learner-workflow-implementation-preflight-no-build-no-zip-no-share-no-delivery.py
