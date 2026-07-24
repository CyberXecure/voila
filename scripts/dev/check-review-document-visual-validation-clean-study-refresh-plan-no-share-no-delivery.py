from __future__ import annotations

import json
import subprocess
from pathlib import Path

repo = Path(".").resolve()

doc = repo / "docs" / "dev" / "review-document-visual-validation-clean-study-refresh-plan-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"

required_existing_files = [
    repo / "docs" / "dev" / "bbox-visual-item-contract-no-share-no-delivery.md",
    repo / "docs" / "dev" / "real-crop-artifact-from-bbox-no-share-no-delivery.md",
    repo / "docs" / "dev" / "ocrmath-on-crop-candidate-no-share-no-delivery.md",
    repo / "docs" / "dev" / "manual-visual-validation-gate-no-share-no-delivery.md",
    repo / "docs" / "dev" / "clean-study-visual-item-ingestion-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-ui-plan-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-readonly-ui-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-readonly-browser-smoke-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-save-action-plan-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-save-action-implementation-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-form-controls-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-form-controls-post-smoke-no-share-no-delivery.md",
    repo / "scripts" / "dev" / "build-clean-study-visual-items-from-bbox.py",
    repo / "scripts" / "dev" / "check-review-document-visual-validation-form-controls-post-smoke-no-share-no-delivery.py",
]

def fail(message: str) -> None:
    raise SystemExit(message)

if not doc.exists():
    fail("FAILED_V0880_DOC_MISSING=" + str(doc))

if not web_app.exists():
    fail("FAILED_V0880_WEB_APP_MISSING=" + str(web_app))

for path in required_existing_files:
    if not path.exists():
        fail("FAILED_V0880_REQUIRED_PREVIOUS_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_terms = [
    "v0.8.80 Review Document visual validation Clean Study refresh plan",
    "This is a planning-only milestone.",
    "It does not implement a refresh route.",
    "It does not modify `services/api/web_app.py`.",
    "It does not write Clean Study.",
    "It does not change `/study`.",
    "`v0.8.67` defines the bbox visual item contract.",
    "`v0.8.68` validates bbox visual item artifacts.",
    "`v0.8.69` creates real crop artifacts from bbox coordinates.",
    "`v0.8.70` creates OCR Math candidates from real crop PNG artifacts.",
    "`v0.8.71` validates explicit manual decisions.",
    "`v0.8.72` builds Clean Study visual preview items from validated visual items.",
    "`v0.8.77` implements the save action.",
    "`v0.8.78` adds form controls.",
    "`v0.8.79` smoke-tests rendered form POST flow and fixes post-save readback priority.",
    "The save action must remain separate from Clean Study refresh.",
    "`POST /review-document/visual-validation/save` should save only visual validation decisions.",
    "It should not directly write Clean Study.",
    "Clean Study preview should be refreshed by a separate explicit owner-local action.",
    "POST /review-document/visual-validation/refresh-clean-study-preview",
    "The route should be owner-local only.",
    "A GET request must not refresh Clean Study.",
    "A page refresh must not refresh Clean Study.",
    "formula_visual_evidence/visual_items.bbox.validated.json",
    "It should not read the older candidate artifact when rebuilding Clean Study.",
    "It should not trust client-submitted item data.",
    "It should not trust client-submitted crop paths.",
    "It should not trust client-submitted ready flags.",
    "scripts/dev/build-clean-study-visual-items-from-bbox.py",
    "`ready_for_study=true`",
    "`user_decision=accept` or `user_decision=edit`",
    "`crop_exists=true`",
    "accepted items have non-empty `ocr_math_candidate_text`",
    "edited items have non-empty `user_corrected_text`",
    "Clean Study preview must exclude:",
    "`user_decision=ignore`",
    "`user_decision=pending`",
    "any item without crop",
    "formula_visual_evidence/visual_items.clean-study.preview.json",
    "formula_visual_evidence/visual_items.clean-study.preview-summary.json",
    "The write should be atomic or replace-safe.",
    "The write should not modify the validated visual decisions artifact.",
    "The write should not modify Progress.",
    "The write should not modify the default `/study` route.",
    "`Actualizează lecția curată`",
    "`Lecția curată nu este actualizată încă`",
    "`Lecția curată a fost actualizată`",
    "`Elemente adăugate în lecție`",
    "`Elemente rămase în afara lecției`",
    "`Deschide lecția curată`",
    "The future refresh route must use safe course ID validation.",
    "The route must not join client-controlled paths.",
    "The route must not expose stack traces.",
    "The route must escape reflected values.",
    "The route must not redirect to user-controlled URLs.",
    "The route must not accept client-submitted item payloads.",
    "FastAPI TestClient",
    "Clean Study preview artifact exists",
    "accepted item is included",
    "edited item is included with corrected text",
    "ignored item is excluded",
    "pending item is excluded",
    "validated visual decisions artifact remains preserved",
    "`/study` is unchanged",
    "This milestone does not implement the refresh action.",
    "It does not add a route.",
    "It does not add a POST endpoint.",
    "It does not add a button.",
    "It does not submit a form.",
    "It does not call any route.",
    "It does not start the server.",
    "It does not use TestClient.",
    "It does not upload a PDF.",
    "It does not run `/generate`.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "It does not run OCR Math.",
    "It does not generate crops.",
    "It does not write manual decisions.",
    "It does not write Clean Study.",
    "It does not write Progress.",
    "It does not change `/study`.",
    "It does not build.",
    "It does not create a ZIP.",
    "It does not create OneDrive staging.",
    "It does not create a share link.",
    "It does not deliver to testers.",
    "It does not distribute anything.",
    "It does not create a public release.",
    "v0.8.81-owner-local-review-document-visual-validation-clean-study-refresh-implementation-no-share-no-delivery",
]

for term in required_terms:
    if term not in doc_text:
        fail("FAILED_V0880_DOC_TERM_MISSING=" + term)

web_diff = subprocess.check_output(
    ["git", "diff", "--name-only", "--", "services/api/web_app.py"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).strip()

if web_diff:
    fail("FAILED_V0880_WEB_APP_HAS_WORKTREE_DIFF=" + web_diff)

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/review-document-visual-validation-clean-study-refresh-plan-no-share-no-delivery.md",
    "scripts/dev/check-review-document-visual-validation-clean-study-refresh-plan-no-share-no-delivery.py",
    "scripts/dev/check-review-document-visual-validation-clean-study-refresh-plan-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0880_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary = {
    "VOILA_V0_8_80_REVIEW_DOCUMENT_VISUAL_VALIDATION_CLEAN_STUDY_REFRESH_PLAN_CHECK": "PASS",
    "planning_only": True,
    "refresh_action_implementation_performed": False,
    "web_app_changed": False,
    "route_added": False,
    "post_endpoint_added": False,
    "button_added": False,
    "form_submitted": False,
    "route_called": False,
    "server_started": False,
    "testclient_used": False,
    "manual_decision_write": False,
    "clean_study_write": False,
    "progress_write": False,
    "study_route_changed": False,
    "upload_performed": False,
    "generate_performed": False,
    "ocr_run": False,
    "languagetool_run": False,
    "ocr_math_run": False,
    "crop_generation_performed": False,
    "build_performed": False,
    "zip_created": False,
    "onedrive_staging_created": False,
    "share_link_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "recommended_next": "v0.8.81-owner-local-review-document-visual-validation-clean-study-refresh-implementation-no-share-no-delivery",
}

evidence_dir = Path(r"D:\dev\tester-runs\v0880-review-document-visual-validation-clean-study-refresh-plan-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

out_json = evidence_dir / "V0.8.80-REVIEW-DOCUMENT-VISUAL-VALIDATION-CLEAN-STUDY-REFRESH-PLAN-CHECK.json"
out_md = evidence_dir / "V0.8.80-REVIEW-DOCUMENT-VISUAL-VALIDATION-CLEAN-STUDY-REFRESH-PLAN-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.80 Review Document visual validation Clean Study refresh plan\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
