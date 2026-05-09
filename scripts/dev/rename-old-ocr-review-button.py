from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

text = text.replace("OCR Review vechi", "Editor OCR vechi")
text = text.replace("Old OCR Review", "Editor OCR vechi")

path.write_text(text, encoding="utf-8")
print("OK: old OCR review button renamed.")
