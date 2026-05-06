from pathlib import Path
import re

files = [
    Path("services/api/web_app.py"),
    Path("services/api/crop_editor_app.py"),
]

for path in files:
    if not path.exists():
        print(f"SKIP missing: {path}")
        continue

    text = path.read_text(encoding="utf-8")

    text = text.replace(' target="_blank"', "")
    text = text.replace(" target='_blank'", "")

    # Also catch target with spaces, if any.
    text = re.sub(r'\s+target\s*=\s*"_blank"', "", text)
    text = re.sub(r"\s+target\s*=\s*'_blank'", "", text)

    path.write_text(text, encoding="utf-8")
    print(f"OK: removed target=_blank from {path}")
