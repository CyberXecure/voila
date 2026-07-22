$ErrorActionPreference = "Stop"

Write-Output "v0.8.42 Exam document workflow UX polish check: start"

python -m py_compile services/api/web_app.py
python -m py_compile scripts/dev/check-exam-document-workflow-ux-polish-no-share-no-delivery.py

python scripts/dev/check-exam-document-workflow-ux-polish-no-share-no-delivery.py
