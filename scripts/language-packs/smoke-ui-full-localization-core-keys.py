import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PLANNED_KEYS = [
    "ui.heading.home",
    "ui.heading.review",
    "ui.heading.review_question",
    "ui.heading.no_review_questions",
    "ui.heading.review_weak_concepts",
    "ui.heading.progress",
    "ui.heading.progress_dashboard",
    "ui.heading.crop_editor_not_started",
    "ui.heading.source_page",
    "ui.heading.editable_ocr_text",
    "ui.heading.suspicious_pages",

    "ui.button.save_page_correction",
    "ui.button.save_reviewed_page",
    "ui.button.save_as_needs_review",
    "ui.button.apply_corrected_ocr",

    "ui.link.back",
    "ui.link.next_review",
    "ui.link.study",
    "ui.link.progress",
    "ui.link.continue_study",
    "ui.link.course_tools",
    "ui.link.top",
    "ui.link.bottom",
    "ui.link.back_to_voila",
    "ui.link.reload",
    "ui.link.concepts",
    "ui.link.course",
    "ui.link.review_ocr",

    "ui.label.correct_concept_title",
]


def load_messages(lang: str) -> dict:
    path = ROOT / "language-packs" / "core" / f"{lang}.language-pack.json"
    return json.loads(path.read_text(encoding="utf-8"))["messages"]


for lang in ["ro", "en"]:
    messages = load_messages(lang)
    missing = [key for key in PLANNED_KEYS if key not in messages]
    if missing:
        raise SystemExit(f"{lang} missing full UI localization core keys: {missing}")

    empty = [key for key in PLANNED_KEYS if not str(messages[key]).strip()]
    if empty:
        raise SystemExit(f"{lang} has empty full UI localization core keys: {empty}")

ro = load_messages("ro")
en = load_messages("en")

if en["ui.link.study"] != "Study":
    raise SystemExit("Unexpected English ui.link.study value")

if ro["ui.link.study"] != "Studiu":
    raise SystemExit("Unexpected Romanian ui.link.study value")

print("UI full localization core key smoke test passed.")