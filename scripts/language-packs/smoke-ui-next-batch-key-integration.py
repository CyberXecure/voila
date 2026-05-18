from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_APP = ROOT / "services" / "api" / "web_app.py"

text = WEB_APP.read_text(encoding="utf-8")

required_snippets = [
    '_ut("ui.edit_crops", "Edit crops")',
    '_ut("ui.review_weak", "Review weak")',
    '_ut("ui.generated", "Generated")',
    '_ut("ui.source_mode", "Source Mode")',
    '_ut("ui.progress", _ut("progress", "Progress"))',
]

for snippet in required_snippets:
    if snippet not in text:
        raise SystemExit(f"Missing UI next batch key integration snippet: {snippet}")

for forbidden in [
    'f\'<a class="btn" href="/edit-crops?pdf={quote(pdf.name)}">Edit crops</a>\'',
    'f\'<a class="btn" href="/review?pdf={quote(pdf.name)}">Review weak</a>\'',
    'f\'<a class="btn" href="/progress?pdf={quote(pdf.name)}">Progress</a>\'',
    '("Edit crops", f"/edit-crops?pdf={q}", "crops"),',
    'card("Edit crops", "Manually edit figure crops.", f"/edit-crops?pdf={q}", checks["figures"]),',
    '<span class="status">Course generated</span>',
    'Generated: <strong>{html.escape(generated)}</strong>',
    'Source Mode: no translation, local processing, original PDF text preserved.',
]:
    if forbidden in text:
        raise SystemExit(f"Hardcoded UI next batch label still present: {forbidden}")

print("UI next batch key integration smoke test passed.")
