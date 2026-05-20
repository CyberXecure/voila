from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_APP = ROOT / "services" / "api" / "web_app.py"

text = WEB_APP.read_text(encoding="utf-8")

required_snippets = [
    '_ut("status.rebuild_complete", "Rebuild complete")',
    '_ut("status.rebuild_failed", "Rebuild failed")',
    '_ut("error.save_title_override_failed", "Save title override failed")',
    '_ut("error.save_ocr_text_failed", "Save OCR text failed")',
]

for snippet in required_snippets:
    if snippet not in text:
        raise SystemExit(f"Missing deferred error/status integration snippet: {snippet}")

for forbidden in [
    "<h1>Rebuild complete</h1>",
    "<h1>Rebuild failed</h1>",
    "<h1>Save title override failed</h1>",
    "<h1>Save OCR text failed</h1>",
]:
    if forbidden in text:
        raise SystemExit(f"Hardcoded deferred error/status output still present: {forbidden}")

# These remain intentionally deferred after v0.2.78.
for still_deferred_key in [
]:
    if f'_ut("{still_deferred_key}"' in text:
        raise SystemExit(f"Still-deferred key was integrated too early: {still_deferred_key}")

for still_expected_literal in [
]:
    if still_expected_literal not in text:
        raise SystemExit(f"Expected still-deferred literal missing: {still_expected_literal}")

if "status_code=500" not in text:
    raise SystemExit("Expected status_code=500 to remain present")

print("UI error/status deferred integration smoke test passed.")
