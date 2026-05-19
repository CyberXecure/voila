import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "language-packs" / "core"

REQUIRED_KEYS = {
    "error.missing_pdf_name",
    "error.no_ocr_pages_found",
    "error.course_html_not_found",
    "error.figures_html_not_found",
    "error.page_not_found",
    "error.pdf_not_found",
    "error.not_found",
    "error.only_pdf_files_supported",
    "error.save_title_override_failed",
    "error.save_ocr_text_failed",
    "status.rebuild_complete",
    "status.rebuild_failed",
    "message.run_ocr_first",
    "message.no_log_file_found_yet",
}

for lang in ("ro", "en"):
    path = CORE / f"{lang}.language-pack.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    messages = data.get("messages", {})

    missing = sorted(REQUIRED_KEYS - set(messages))
    if missing:
        raise SystemExit(f"{lang} core language pack missing error/status keys: {missing}")

    empty = sorted(key for key in REQUIRED_KEYS if not str(messages.get(key, "")).strip())
    if empty:
        raise SystemExit(f"{lang} core language pack has empty error/status values: {empty}")

print("UI error/status core key smoke test passed.")