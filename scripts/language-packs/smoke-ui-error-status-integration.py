from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_APP = ROOT / "services" / "api" / "web_app.py"

text = WEB_APP.read_text(encoding="utf-8")

required_snippets = [
    '_ut("error.missing_pdf_name", "Missing PDF name")',
    '_ut("error.no_ocr_pages_found", "No OCR pages found")',
    '_ut("message.run_ocr_first", "Run OCR first")',
    '_ut("error.course_html_not_found", "Course HTML not found")',
    '_ut("error.figures_html_not_found", "Figures HTML not found")',
    '_ut("error.pdf_not_found", "PDF not found")',
    '_ut("error.not_found", "Not found")',
]

for snippet in required_snippets:
    if snippet not in text:
        raise SystemExit(f"Missing UI error/status integration snippet: {snippet}")

for forbidden in [
    'return HTMLResponse("<h1>Missing PDF name</h1>", status_code=400)',
    'return HTMLResponse("<h1>No OCR pages found</h1><p>Run OCR first.</p>", status_code=404)',
    'return HTMLResponse("<h1>No OCR pages found</h1>", status_code=404)',
    'return HTMLResponse("<h1>Course HTML not found</h1>", status_code=404)',
    'return HTMLResponse("<h1>Figures HTML not found</h1>", status_code=404)',
    'return _VoilaResponse("PDF not found", status_code=404)',
    'return Response("Not found", status_code=404)',
]:
    if forbidden in text:
        raise SystemExit(f"Hardcoded error/status route output still present: {forbidden}")

# These keys are intentionally deferred from the first integration batch.
for deferred_key in [
    "error.only_pdf_files_supported",
    "error.page_not_found",
    "message.no_log_file_found_yet",
]:
    if f'_ut("{deferred_key}"' in text:
        raise SystemExit(f"Deferred key was integrated too early: {deferred_key}")

if "status_code=400" not in text:
    raise SystemExit("Expected status_code=400 to remain present")

if "status_code=404" not in text:
    raise SystemExit("Expected status_code=404 to remain present")

print("UI error/status integration smoke test passed.")
