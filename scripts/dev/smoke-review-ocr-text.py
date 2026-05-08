import sys
from pathlib import Path

sys.path.insert(0, str(Path("services/api").resolve()))

import web_app

response = web_app.review_ocr_text(
    pdf="Manualul Instalatiilor Electrice.pdf",
    page=15,
)

body = response.body.decode("utf-8", errors="replace")

print("Status:", response.status_code)
print("HTML length:", len(body))
print("Has VS autocomplete:", "VS Code style OCR autocomplete" in body)
print("Has suggestions div:", 'id="ocrSuggestions"' in body)
print("OK")
