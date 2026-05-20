from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_APP = ROOT / "services" / "api" / "web_app.py"

text = WEB_APP.read_text(encoding="utf-8")

required_snippets = [
    '_ut("message.open_course_description", "Read the generated course with navigation.")',
    '_ut("message.lessons_description", "Choose a lesson, read it, then study only that lesson.")',
    '_ut("message.study_mode_description", "Practice questions generated from the course.")',
    '_ut("message.review_ocr_text_description", "Correct OCR text page by page.")',
    '_ut("message.review_concepts_description", "Correct lesson and concept titles.")',
    '_ut("message.figures_description", "View extracted figures.")',
    '_ut("message.edit_crops_description", "Manually edit figure crops.")',
    '_ut("message.progress_description", "View study progress.")',
    '_ut("message.return_to_library_description", "Return to the main course library.")',
    '_ut("message.source_mode_description", "No translation, local processing, original PDF text preserved.")',
    '_ut("status.uploaded", "Uploaded")',
    '_ut("status.not_generated_yet", "Not generated yet")',
    '_ut("status.no_suspicious_pages_detected", "No suspicious pages detected.")',
    '_ut("status.focused_concept", "Focused concept")',
    '_ut("status.attempts", "Attempts")',
    '_ut("status.status", "Status")',
    '_ut("status.study_coverage", _ut("study_coverage", "Study coverage"))',
    '_ut("status.overall_mastery", _ut("overall_mastery", "Overall mastery"))',
    '_ut("status.concept_status", "Concept status")',
]

for snippet in required_snippets:
    if snippet not in text:
        raise SystemExit(f"Missing status/message integration snippet: {snippet}")

for forbidden in [
    'card("Open course", "Read the generated course with navigation.", f"/view-course?pdf={q}", checks["course"]),',
    'card("Lessons", "Choose a lesson, read it, then study only that lesson.", f"/lessons?pdf={q}", checks["study"]),',
    'card(_ut("ui.study_mode", "Study mode"), "Practice questions generated from the course.", f"/study?pdf={q}", checks["study"]),',
    'card(_ut("ui.review_ocr_text", "Review OCR Text"), "Correct OCR text page by page.", f"/review-ocr-corrected?pdf={q}&page=1", checks["ocr"]),',
    'card(_ut("ui.review_study_concepts", "Review Study Concepts"), "Correct lesson and concept titles.", f"/review-concepts?pdf={q}", checks["concepts"]),',
    'card(_ut("ui.figures", "Figures"), "View extracted figures.", f"/view-figures?pdf={q}", checks["figures"]),',
    'card(_ut("ui.edit_crops", "Edit crops"), "Manually edit figure crops.", f"/edit-crops?pdf={q}", checks["figures"]),',
    'card(_ut("ui.progress", _ut("progress", "Progress")), "View study progress.", f"/progress?pdf={q}", checks["study"]),',
    'card(_ut("ui.library", _ut("library", "Library")), "Return to the main course library.", "/", True),',
    'Uploaded: <strong>{html.escape(uploaded)}</strong>',
    '<span class="status missing">Not generated yet</span>',
    '<p class="meta">No suspicious pages detected.</p>',
    '<div class="meta">Focused concept: <strong>{concept_id}</strong></div>',
    '<div class="meta">Attempts: {attempts}</div>',
    '<h2>Study coverage</h2>',
    '<h2>Overall mastery</h2>',
    '<h2>Concept status</h2>',
]:
    if forbidden in text:
        raise SystemExit(f"Hardcoded status/message text still present: {forbidden}")

# Intentionally deferred error/status route output must remain unchanged in this batch.
for deferred in [
    'Save OCR text failed',
    'logs = []',
]:
    if deferred not in text:
        raise SystemExit(f"Deferred text was unexpectedly changed: {deferred}")

print("UI status/message integration smoke test passed.")
