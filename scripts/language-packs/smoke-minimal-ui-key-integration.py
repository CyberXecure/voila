from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_APP = ROOT / "services" / "api" / "web_app.py"

text = WEB_APP.read_text(encoding="utf-8")

required_snippets = [
    '_ut("ui.upload_pdf", "Upload PDF")',
    '_ut("ui.generate_course", "Generate course")',
    '_ut("ui.open_course", _ut("open_course", "Open course"))',
]

for snippet in required_snippets:
    if snippet not in text:
        raise SystemExit(f"Missing minimal UI key integration snippet: {snippet}")

for forbidden in [
    "<h2>Upload PDF</h2>",
    '<button class="primary" type="submit">Upload PDF</button>',
    '<button class="primary" type="submit">Generate course</button>',
]:
    if forbidden in text:
        raise SystemExit(f"Hardcoded label still present: {forbidden}")

print("Minimal UI key integration smoke test passed.")
