from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# Înlocuiește linkuri directe către 8790 cu ruta locală care pornește automat serverul.
text = re.sub(
    r'http://127\.0\.0\.1:8790/\?pdf=\{([^}]+)\}',
    r'/edit-crops?pdf={\1}',
    text,
)

text = text.replace(
    'http://127.0.0.1:8790/?pdf=',
    '/edit-crops?pdf=',
)

path.write_text(text, encoding="utf-8")
print("OK: Edit crops links redirected through /edit-crops")
