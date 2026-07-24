from __future__ import annotations

from pathlib import Path

repo = Path(".").resolve()
web_app = repo / "services" / "api" / "web_app.py"

text = web_app.read_text(encoding="utf-8", errors="replace")

old = '''    candidate_paths = [
        visual_dir / "visual_items.bbox.with-ocrmath-candidates.json",
        visual_dir / "visual_items.bbox.validated.json",
    ]
'''

new = '''    # VOILA_V0_8_79_POST_SAVE_READBACK_PREFERS_VALIDATED_ARTIFACT
    candidate_paths = [
        visual_dir / "visual_items.bbox.validated.json",
        visual_dir / "visual_items.bbox.with-ocrmath-candidates.json",
    ]
'''

if new in text:
    print("V0.8.79 readback priority patch already applied")
    raise SystemExit(0)

if old not in text:
    raise SystemExit("FAILED_V0879_READBACK_PATCH_TARGET_NOT_FOUND")

web_app.write_text(text.replace(old, new, 1).rstrip() + "\n", encoding="utf-8")
print("V0.8.79 readback priority patch applied")
