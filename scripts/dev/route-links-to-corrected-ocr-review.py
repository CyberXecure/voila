from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

replacements = {
    "/review-ocr-text?": "/review-ocr-corrected?",
    "review-ocr-text?": "review-ocr-corrected?",
    "Old OCR Review": "OCR Review vechi",
}

changed = 0

for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new)
        changed += 1

path.write_text(text, encoding="utf-8")
print(f"OK: OCR Review links now point to corrected Monaco route. Replacement groups: {changed}")
