from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_APP = ROOT / "services" / "api" / "web_app.py"

text = WEB_APP.read_text(encoding="utf-8")

required_snippets = [
    '_ut("ui.figures", "Figures")',
    '_ut("ui.study", _ut("study", "Study"))',
    '_ut("ui.progress", _ut("progress", "Progress"))',
    '_ut("ui.delete_from_library", "Delete from library")',
]

for snippet in required_snippets:
    if snippet not in text:
        raise SystemExit(f"Missing UI expansion key integration snippet: {snippet}")

for forbidden in [
    'button.textContent = "Delete from library";',
    'f\'<a class="btn" href="/study?pdf={quote(pdf.name)}">Study</a>\'',
    '("Study", f"/study?pdf={q}", "study"),',
    '("Figures", f"/view-figures?pdf={q}", "figures"),',
    '("Progress", f"/progress?pdf={q}", "progress"),',
    'card("Figures", "View extracted figures.", f"/view-figures?pdf={q}", checks["figures"]),',
    'card("Progress", "View study progress.", f"/progress?pdf={q}", checks["study"]),',
]:
    if forbidden in text:
        raise SystemExit(f"Hardcoded UI expansion label still present: {forbidden}")

print("UI expansion key integration smoke test passed.")
