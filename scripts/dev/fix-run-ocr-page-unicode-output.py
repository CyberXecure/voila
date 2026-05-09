from pathlib import Path

path = Path("scripts/dev/run-ocr-page.py")
text = path.read_text(encoding="utf-8")

# Ensure stdout/stderr can print Romanian/Russian/etc safely on Windows.
if "sys.stdout.reconfigure" not in text:
    text = text.replace(
'''import sys
import tempfile
''',
'''import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
'''
    )

# Replace final raw preview print with safe preview.
text = text.replace(
'''    print(text[:1200])
''',
'''    preview = text[:1200]
    try:
        print(preview)
    except UnicodeEncodeError:
        print(preview.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))
'''
)

path.write_text(text, encoding="utf-8")
print("OK: run-ocr-page.py now prints Unicode safely.")
