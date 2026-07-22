$ErrorActionPreference = "Stop"

Write-Output "v0.8.43 Student workflow UX reset charter check: start"

python -m py_compile scripts/dev/check-student-workflow-ux-reset-charter-no-build-no-zip-no-share-no-delivery.py

python scripts/dev/check-student-workflow-ux-reset-charter-no-build-no-zip-no-share-no-delivery.py
