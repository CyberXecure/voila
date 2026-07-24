from __future__ import annotations

import json
import subprocess
from pathlib import Path

repo = Path(".").resolve()

doc = repo / "docs" / "dev" / "review-document-visual-validation-ui-plan-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"

required_existing_files = [
    repo / "docs" / "dev" / "bbox-visual-item-contract-no-share-no-delivery.md",
    repo / "docs" / "dev" / "real-crop-artifact-from-bbox-no-share-no-delivery.md",
    repo / "docs" / "dev" / "ocrmath-on-crop-candidate-no-share-no-delivery.md",
    repo / "docs" / "dev" / "manual-visual-validation-gate-no-share-no-delivery.md",
    repo / "docs" / "dev" / "clean-study-visual-item-ingestion-no-share-no-delivery.md",
    repo / "scripts" / "dev" / "validate-bbox-visual-items.py",
    repo / "scripts" / "dev" / "build-bbox-visual-crops.py",
    repo / "scripts" / "dev" / "run-ocrmath-on-bbox-crops.py",
    repo / "scripts" / "dev" / "apply-bbox-visual-validation-decisions.py",
    repo / "scripts" / "dev" / "build-clean-study-visual-items-from-bbox.py",
]

def fail(message: str) -> None:
    raise SystemExit(message)

if not doc.exists():
    fail("FAILED_V0873_DOC_MISSING=" + str(doc))

if not web_app.exists():
    fail("FAILED_V0873_WEB_APP_MISSING=" + str(web_app))

for path in required_existing_files:
    if not path.exists():
        fail("FAILED_V0873_REQUIRED_PREVIOUS_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_terms = [
    "v0.8.73 Review Document visual validation UI plan",
    "This is a planning-only milestone.",
    "It does not implement the UI.",
    "It does not modify `services/api/web_app.py`.",
    "It does not add a POST endpoint.",
    "It does not change `/study`.",
    "`v0.8.67` defines the bbox visual item contract.",
    "`v0.8.68` validates bbox visual items.",
    "`v0.8.69` creates real crop PNG artifacts from bbox coordinates.",
    "`v0.8.70` runs OCR Math candidate extraction on crop PNG artifacts.",
    "`v0.8.71` applies explicit manual validation decisions.",
    "`v0.8.72` ingests only validated `accept/edit` items into Clean Study preview.",
    "Formule și imagini de verificat",
    "Imagine extrasă din document",
    "Text detectat",
    "Corectare",
    "Explicație pe înțeles",
    "Acceptă",
    "Salvează corectarea",
    "Ignoră",
    "Gata pentru lecție",
    "Nu intră încă în lecție",
    "Diagnostic tehnic",
    "bbox coordinates",
    "raw artifact file names",
    "absolute local paths",
    "JSON schema internals",
    "formula_visual_evidence/visual_items.bbox.with-ocrmath-candidates.json",
    "formula_visual_evidence/visual_items.bbox.validated.json",
    "formula_visual_evidence/visual_items.clean-study.preview.json",
    "scripts/dev/apply-bbox-visual-validation-decisions.py",
    "The future UI implementation should not allow implicit approval.",
    "`Acceptă` should require:",
    "`Editează` should require:",
    "`Ignoră` should require:",
    "Undecided items remain pending.",
    "Clean Study may include only:",
    "`ready_for_study=true`",
    "`user_decision=accept` or `user_decision=edit`",
    "Clean Study must exclude:",
    "`user_decision=ignore`",
    "`user_decision=pending`",
    "The visual validation UI should feel like document review, not developer tooling.",
    "Add read-only visual validation UI section in `Revizuire document`.",
    "Show crop image and candidate text from existing artifacts.",
    "Add owner-local save action for Accept/Edit/Ignore decisions.",
    "This milestone does not implement visual validation UI.",
    "It does not start the server.",
    "It does not call any route.",
    "It does not upload a PDF.",
    "It does not run `/generate`.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "It does not run OCR Math.",
    "It does not generate crops.",
    "It does not write manual decisions.",
    "It does not write Clean Study.",
    "It does not write Progress.",
    "It does not build.",
    "It does not create a ZIP.",
    "It does not create OneDrive staging.",
    "It does not create a share link.",
    "It does not deliver to testers.",
    "It does not distribute anything.",
    "It does not create a public release.",
]

for term in required_terms:
    if term not in doc_text:
        fail("FAILED_V0873_DOC_TERM_MISSING=" + term)

web_diff = subprocess.check_output(
    ["git", "diff", "--name-only", "--", "services/api/web_app.py"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).strip()

if web_diff:
    fail("FAILED_V0873_WEB_APP_HAS_WORKTREE_DIFF=" + web_diff)

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/review-document-visual-validation-ui-plan-no-share-no-delivery.md",
    "scripts/dev/check-review-document-visual-validation-ui-plan-no-share-no-delivery.py",
    "scripts/dev/check-review-document-visual-validation-ui-plan-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0873_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary = {
    "VOILA_V0_8_73_REVIEW_DOCUMENT_VISUAL_VALIDATION_UI_PLAN_CHECK": "PASS",
    "planning_only": True,
    "ui_implementation_performed": False,
    "web_route_change_performed": False,
    "web_app_changed": False,
    "post_endpoint_added": False,
    "study_route_changed": False,
    "server_started": False,
    "route_called": False,
    "upload_performed": False,
    "generate_performed": False,
    "ocr_run": False,
    "languagetool_run": False,
    "ocr_math_run": False,
    "crop_generation_performed": False,
    "manual_decision_write": False,
    "clean_study_write": False,
    "progress_write": False,
    "build_performed": False,
    "zip_created": False,
    "onedrive_staging_created": False,
    "share_link_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "recommended_next": "v0.8.74-owner-local-review-document-visual-validation-readonly-ui-no-share-no-delivery",
}

evidence_dir = Path(r"D:\dev\tester-runs\v0873-review-document-visual-validation-ui-plan-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

out_json = evidence_dir / "V0.8.73-REVIEW-DOCUMENT-VISUAL-VALIDATION-UI-PLAN-CHECK.json"
out_md = evidence_dir / "V0.8.73-REVIEW-DOCUMENT-VISUAL-VALIDATION-UI-PLAN-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.73 Review Document visual validation UI plan\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
