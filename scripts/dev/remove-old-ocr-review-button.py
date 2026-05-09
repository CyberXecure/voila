from pathlib import Path
import re
import time

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

backup = path.with_name("web_app.py.before_remove_old_ocr_button_" + time.strftime("%Y%m%d_%H%M%S"))
backup.write_text(text, encoding="utf-8")

patterns = [
    # Anchor/button containing old OCR label.
    r'\s*<a\b[^>]*>\s*(?:Old OCR Review|OCR Review vechi|Editor OCR vechi)\s*</a>',
    r'\s*<button\b[^>]*>\s*(?:Old OCR Review|OCR Review vechi|Editor OCR vechi)\s*</button>',

    # Anchor pointing to old route, regardless of label.
    r'\s*<a\b[^>]*href=["\'][^"\']*review-ocr-text[^"\']*["\'][^>]*>.*?</a>',
]

changed = 0

for pattern in patterns:
    text, count = re.subn(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)
    changed += count

path.write_text(text, encoding="utf-8")

print("OK: removed old OCR Review button/link from UI.")
print("Removed:", changed)
print("Backup:", backup)
