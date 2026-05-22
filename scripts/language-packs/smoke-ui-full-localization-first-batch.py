from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_APP = ROOT / "services" / "api" / "web_app.py"

text = WEB_APP.read_text(encoding="utf-8")

required_snippets = [
    '_ut("ui.heading.home", "Voila!")',
    '_ut("ui.heading.review", "Voila! Review")',
    '_ut("ui.heading.review_question", "Review question")',
    '_ut("ui.heading.no_review_questions", "No review questions available")',
    '_ut("ui.heading.review_weak_concepts", "Voila! Review weak concepts")',
    '_ut("ui.heading.progress", "Voila! Progress")',
    '_ut("ui.heading.progress_dashboard", "Voila! Progress Dashboard")',
    '_ut("ui.heading.crop_editor_not_started", "Crop Editor did not start")',
    '_ut("ui.heading.source_page", "Source page")',
    '_ut("ui.heading.editable_ocr_text", "Editable OCR text")',
    '_ut("ui.heading.suspicious_pages", "Suspicious pages")',

    '_ut("ui.button.save_page_correction", "Save page correction")',
    '_ut("ui.button.save_reviewed_page", "Save reviewed page")',
    '_ut("ui.button.save_as_needs_review", "Save as needs review")',
    '_ut("ui.button.apply_corrected_ocr", "Apply corrected OCR to pages.json")',

    '_ut("ui.link.back", "Back")',
    '_ut("ui.link.next_review", "Next review")',
    '_ut("ui.link.study", "Study")',
    '_ut("ui.link.progress", "Progress")',
    '_ut("ui.link.continue_study", "Continue Study")',
    '_ut("ui.link.course_tools", "Course tools")',
    '_ut("ui.link.top", "Top")',
    '_ut("ui.link.bottom", "Bottom")',
    '_ut("ui.link.back_to_voila", "Back to Voila")',
    '_ut("ui.link.reload", "Reload")',
    '_ut("ui.link.concepts", "Concepts")',
    '_ut("ui.link.course", "Course")',
    '_ut("ui.link.review_ocr", "Review OCR")',

    '_ut("ui.label.correct_concept_title", "Correct concept title")',
]

for snippet in required_snippets:
    if snippet not in text:
        raise SystemExit(f"Missing full UI first-batch integration snippet: {snippet}")

for forbidden in [
    "<h2>Review question</h2>",
    "<h2>No review questions available</h2>",
    "<h1>Voila! Review weak concepts</h1>",
    "<h1>Voila! Progress Dashboard</h1>",
    "<h1>Crop Editor did not start</h1>",
    "<h2>Source page</h2>",
    "<h2>Editable OCR text</h2>",
    "<h3>Suspicious pages</h3>",
    "<button type=\"submit\">Save page correction</button>",
    "<button class=\"primary\" type=\"submit\" name=\"status\" value=\"reviewed\">Save reviewed page</button>",
    "<button type=\"submit\" name=\"status\" value=\"needs_review\">Save as needs review</button>",
    "<button class=\"danger\" type=\"submit\">Apply corrected OCR to pages.json</button>",
    "<label>Correct concept title</label>",
]:
    if forbidden in text:
        raise SystemExit(f"Hardcoded full UI first-batch literal still present: {forbidden}")

if "_html_escape(str(page))" not in text:
    raise SystemExit("Expected v0.2.81 page-not-found HTML escaping to remain present")

print("UI full localization first batch smoke test passed.")