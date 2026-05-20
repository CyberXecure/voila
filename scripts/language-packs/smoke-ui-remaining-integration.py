from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_APP = ROOT / "services" / "api" / "web_app.py"

text = WEB_APP.read_text(encoding="utf-8")

required_snippets = [
    '_ut("ui.logs", "Logs")',
    '_ut("ui.course_tools", "Course Tools")',
    '_ut("ui.quick_tools", "Quick Tools")',
    '_ut("ui.review_ocr_text", "Review OCR Text")',
    '_ut("ui.review_concepts", "Review Concepts")',
    '_ut("ui.review_study_concepts", "Review Study Concepts")',
    '_ut("ui.correct_ocr_text", "Correct OCR Text")',
    '_ut("ui.study_mode", "Study Mode")',
    '_ut("ui.study_mode", "Study mode")',
    '_ut("ui.toggle_theme", "Toggle theme")',
    '_ut("ui.save_title_override", "Save title override")',
    '_ut("ui.fit_width", "Fit width")',
]

for snippet in required_snippets:
    if snippet not in text:
        raise SystemExit(f"Missing UI remaining integration snippet: {snippet}")

for forbidden in [
    'f\'<a class="btn" href="/log?pdf={quote(pdf.name)}">Logs</a>\'',
    '<button class="theme-toggle" id="themeToggle" type="button">Toggle theme</button>',
    '<button type="submit">Save title override</button>',
    '<button type="button" onclick="fitScanWidth()">Fit width</button>',
    '<h1>Study Mode</h1>',
    '<title>Review Study Concepts · Voila!</title>',
    '<h1>Review Study Concepts</h1>',
    '<title>Review OCR Text · Voila!</title>',
    '<h1>Review OCR Text</h1>',
    '("Review OCR Text", f"/review-ocr-corrected?pdf={q}&page=1", "ocr"),',
    '("Review Concepts", f"/review-concepts?pdf={q}", "concepts"),',
    'return f\'<a class="tool-link primary-tool" href="/course-tools?pdf={q}">Course Tools</a>\'',
    'card("Study mode", "Practice questions generated from the course.", f"/study?pdf={q}", checks["study"]),',
    'card("Review OCR Text", "Correct OCR text page by page.", f"/review-ocr-corrected?pdf={q}&page=1", checks["ocr"]),',
    'card("Review Study Concepts", "Correct lesson and concept titles.", f"/review-concepts?pdf={q}", checks["concepts"]),',
    '<title>Course Tools · Voila!</title>',
    '<h1>Course Tools</h1>',
    '<title>Quick Tools · Voila!</title>',
    '<h1>Quick Tools</h1>',
    '<h1>Correct OCR Text</h1>',
]:
    if forbidden in text:
        raise SystemExit(f"Hardcoded UI remaining integration label still present: {forbidden}")

# Ensure intentionally deferred text remains untouched in this batch.
for deferred in [
    'Generate course files first, then Study Mode will use quiz.json.',
    'logs = []',
]:
    if deferred not in text:
        raise SystemExit(f"Deferred/non-UI text was unexpectedly changed: {deferred}")

print("UI remaining integration smoke test passed.")
