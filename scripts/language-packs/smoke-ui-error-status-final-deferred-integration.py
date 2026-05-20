from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_APP = ROOT / "services" / "api" / "web_app.py"

text = WEB_APP.read_text(encoding="utf-8")

required_snippets = [
    '_ut("error.only_pdf_files_supported", "Only PDF files are supported.")',
    "_ut('error.page_not_found', 'Page not found')",
    '_ut("message.no_log_file_found_yet", "No log file found yet.")',
]

for snippet in required_snippets:
    if snippet not in text:
        raise SystemExit(f"Missing final deferred error/status integration snippet: {snippet}")

for forbidden in [
    'raise HTTPException(status_code=400, detail="Only PDF files are supported.")',
    'return HTMLResponse(f"<h1>Page not found: {page}</h1>", status_code=404)',
    'return PlainTextResponse("No log file found yet.", status_code=404)',
]:
    if forbidden in text:
        raise SystemExit(f"Hardcoded final deferred error/status output still present: {forbidden}")

if ": {page}</h1>" not in text:
    raise SystemExit("Expected dynamic page value to remain present in page-not-found output")

if "HTTPException(status_code=400" not in text:
    raise SystemExit("Expected HTTPException status_code=400 to remain present")

if "status_code=404" not in text:
    raise SystemExit("Expected status_code=404 to remain present")

print("UI error/status final deferred integration smoke test passed.")