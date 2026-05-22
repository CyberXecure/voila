import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PLANNED_KEYS = [
    "ui.link.previous",
    "ui.link.prev",
    "ui.link.next",
    "ui.link.back_to_ocr_review",

    "ui.message.local_pdf_learning_studio",
    "ui.message.generate_study_quiz_first",
    "ui.message.crop_editor_port_not_responding",
    "ui.message.no_study_questions_found",
    "ui.message.concept_title_cannot_be_empty",
    "ui.message.correction_not_saved_exception",
    "ui.message.ocr_corrections_applied",
    "ui.message.no_pdfs_found",

    "ui.title.correct_ocr",
]


def load_messages(lang: str) -> dict:
    path = ROOT / "language-packs" / "core" / f"{lang}.language-pack.json"
    return json.loads(path.read_text(encoding="utf-8"))["messages"]


for lang in ["ro", "en"]:
    messages = load_messages(lang)

    missing = [key for key in PLANNED_KEYS if key not in messages]
    if missing:
        raise SystemExit(f"{lang} missing next-batch full UI localization core keys: {missing}")

    empty = [key for key in PLANNED_KEYS if not str(messages[key]).strip()]
    if empty:
        raise SystemExit(f"{lang} has empty next-batch full UI localization core keys: {empty}")

ro = load_messages("ro")
en = load_messages("en")

if en["ui.link.next"] != "Next":
    raise SystemExit("Unexpected English ui.link.next value")

if ro["ui.link.next"] != "Următor":
    raise SystemExit("Unexpected Romanian ui.link.next value")

if en["ui.message.no_pdfs_found"] != "No PDFs found.":
    raise SystemExit("Unexpected English ui.message.no_pdfs_found value")

if ro["ui.message.no_pdfs_found"] != "Nu au fost găsite PDF-uri.":
    raise SystemExit("Unexpected Romanian ui.message.no_pdfs_found value")

print("UI full localization next-batch core key smoke test passed.")