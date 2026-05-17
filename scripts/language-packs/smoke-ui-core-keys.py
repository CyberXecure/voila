from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[2]
RO_PATH = ROOT / "language-packs" / "core" / "ro.language-pack.json"
EN_PATH = ROOT / "language-packs" / "core" / "en.language-pack.json"

checks = [
    (RO_PATH, "ui.upload_pdf", "Încarcă PDF"),
    (EN_PATH, "ui.upload_pdf", "Upload PDF"),
    (RO_PATH, "ui.delete_from_library", "Șterge din bibliotecă"),
    (EN_PATH, "ui.delete_from_library", "Delete from library"),
]

for path, key, expected in checks:
    data = json.loads(path.read_text(encoding="utf-8"))
    actual = data.get("messages", {}).get(key)
    if actual != expected:
        raise SystemExit(
            f"UI core key smoke failed for {path}: {key} expected {expected!r}, got {actual!r}"
        )

print("UI core key smoke test passed.")
