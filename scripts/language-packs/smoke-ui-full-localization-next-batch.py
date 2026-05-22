from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_APP = ROOT / "services" / "api" / "web_app.py"

text = WEB_APP.read_text(encoding="utf-8")

required_snippets = [
    '_ut("ui.link.previous", "Previous")',
    '_ut("ui.link.prev", "Prev")',
    '_ut("ui.link.next", "Next")',
    '_ut("ui.link.back_to_ocr_review", "Back to OCR Review")',
    '_ut("ui.message.local_pdf_learning_studio", "Your local PDF learning studio")',
    '_ut("ui.message.generate_study_quiz_first", "Generate a study quiz first.")',
    '_ut("ui.message.crop_editor_port_not_responding", "Port 8790 is not responding. Start it manually:")',
    '_ut("ui.message.no_study_questions_found", "No study questions found. Generate Study first.")',
    '_ut("ui.message.concept_title_cannot_be_empty", "Concept title cannot be empty.")',
    '_ut("ui.message.correction_not_saved_exception", "The correction was not saved because the server raised an exception.")',
    '_ut("ui.message.ocr_corrections_applied", "OCR text corrections were applied to course and study.")',
    '_ut("ui.message.no_pdfs_found", "No PDFs found.")',
    '_ut("ui.title.correct_ocr", "Correct OCR · Voila!")',
]

for snippet in required_snippets:
    if snippet not in text:
        raise SystemExit(f"Missing full UI next-batch integration snippet: {snippet}")

for forbidden in [
    "<p>Your local PDF learning studio</p>",
    "<p>Generate a study quiz first.</p>",
    "<p>Port 8790 is not responding. Start it manually:</p>",
    "<p>The correction was not saved because the server raised an exception.</p>",
    "<p>OCR text corrections were applied to course and study.</p>",
    "<title>Correct OCR · Voila!</title>",
    ">← Previous</a>",
    ">← Prev</a>",
    ">Next →</a>",
    ">Back to OCR Review</a>",
]:
    if forbidden in text:
        raise SystemExit(f"Hardcoded full UI next-batch literal still present: {forbidden}")

if "_html_escape(str(page))" not in text:
    raise SystemExit("Expected v0.2.81 page-not-found HTML escaping to remain present")

if "_ut(\"ui.heading.empty_title\"" in text:
    raise SystemExit("Unexpected non-planned ui.heading.empty_title key introduced")

print("UI full localization next batch smoke test passed.")