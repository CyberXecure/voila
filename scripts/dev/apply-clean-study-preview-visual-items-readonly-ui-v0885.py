from __future__ import annotations

from pathlib import Path

repo = Path(__file__).resolve().parents[2]
web_app = repo / "services" / "api" / "web_app.py"

text = web_app.read_text(encoding="utf-8", errors="replace")

required = [
    "VOILA_V0_8_85_CLEAN_STUDY_PREVIEW_VISUAL_ITEMS_READONLY_UI_START",
    "_voila_v0885_install_clean_study_preview_visual_items_route_wrapper",
    "_VOILA_V0_8_85_CLEAN_STUDY_PREVIEW_VISUAL_ITEMS_ROUTE_WRAPPED",
    "visual_items.clean-study.preview.json",
    "Elemente vizuale validate",
]

missing = [term for term in required if term not in text]
if missing:
    raise SystemExit("FAILED_V0885_PATCH_REQUIRED_TERM_MISSING=" + repr(missing))

print("V0.8.85 Clean Study preview visual items read-only UI patch is present")
