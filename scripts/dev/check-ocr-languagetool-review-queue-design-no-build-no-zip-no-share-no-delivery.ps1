$ErrorActionPreference = "Stop"

Write-Output "v0.8.45 OCR + LanguageTool review queue design check: start"

python -m py_compile scripts/dev/check-ocr-languagetool-review-queue-design-no-build-no-zip-no-share-no-delivery.py

python scripts/dev/check-ocr-languagetool-review-queue-design-no-build-no-zip-no-share-no-delivery.py
