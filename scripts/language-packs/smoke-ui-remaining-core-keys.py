import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "language-packs" / "core"

REQUIRED_KEYS = {
    "ui.back",
    "ui.tools",
    "ui.course",
    "ui.lessons",
    "ui.library",
    "ui.logs",
    "ui.course_tools",
    "ui.quick_tools",
    "ui.study_mode",
    "ui.review_ocr_text",
    "ui.review_concepts",
    "ui.review_study_concepts",
    "ui.correct_ocr_text",
    "ui.continue_study",
    "ui.toggle_theme",
    "ui.save_title_override",
    "ui.save_page_correction",
    "ui.save_reviewed_page",
    "ui.save_as_needs_review",
    "ui.apply_corrected_ocr",
    "ui.fit_width",
    "message.choose_pdf_helper",
    "message.no_pdf_files_found",
    "message.open_course_description",
    "message.lessons_description",
    "message.study_mode_description",
    "message.review_ocr_text_description",
    "message.review_concepts_description",
    "message.edit_crops_description",
    "message.figures_description",
    "message.progress_description",
    "message.return_to_library_description",
    "message.source_mode_description",
    "message.apply_corrected_ocr_warning",
    "status.uploaded",
    "status.not_generated_yet",
    "status.no_suspicious_pages_detected",
    "status.focused_concept",
    "status.attempts",
    "status.status",
    "status.study_coverage",
    "status.overall_mastery",
    "status.concept_status",
    "status.missing_pdf_name",
    "status.no_ocr_pages_found",
    "status.rebuild_complete",
    "status.rebuild_failed",
    "status.save_title_override_failed",
    "status.save_ocr_text_failed",
}

for lang in ("ro", "en"):
    path = CORE / f"{lang}.language-pack.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    messages = data.get("messages", {})

    missing = sorted(REQUIRED_KEYS - set(messages))
    if missing:
        raise SystemExit(f"{lang} core language pack missing keys: {missing}")

    empty = sorted(key for key in REQUIRED_KEYS if not str(messages.get(key, "")).strip())
    if empty:
        raise SystemExit(f"{lang} core language pack has empty values: {empty}")

print("UI remaining core key smoke test passed.")
