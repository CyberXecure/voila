from __future__ import annotations

import json
import subprocess
from pathlib import Path

repo = Path(".").resolve()

doc = repo / "docs" / "dev" / "review-document-visual-validation-save-action-plan-no-share-no-delivery.md"
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
    repo / "scripts" / "dev" / "validate-bbox-visual-items.py",
    repo / "scripts" / "dev" / "apply-bbox-visual-validation-decisions.py",
    repo / "scripts" / "dev" / "build-clean-study-visual-items-from-bbox.py",
    repo / "scripts" / "dev" / "check-review-document-visual-validation-readonly-browser-smoke-no-share-no-delivery.py",
]

def fail(message: str) -> None:
    raise SystemExit(message)

if not doc.exists():
    fail("FAILED_V0876_DOC_MISSING=" + str(doc))

if not web_app.exists():
    fail("FAILED_V0876_WEB_APP_MISSING=" + str(web_app))

for path in required_existing_files:
    if not path.exists():
        fail("FAILED_V0876_REQUIRED_PREVIOUS_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_terms = [
    "v0.8.76 Review Document visual validation save-action plan",
    "This is a planning-only milestone.",
    "It does not implement a POST endpoint.",
    "It does not modify `services/api/web_app.py`.",
    "It does not write manual decisions.",
    "It does not write Clean Study.",
    "It does not change `/study`.",
    "`v0.8.67` defines the bbox visual item contract.",
    "`v0.8.68` validates bbox visual item artifacts.",
    "`v0.8.69` creates real crop artifacts from bbox coordinates.",
    "`v0.8.70` creates OCR Math candidates from real crop PNG artifacts.",
    "`v0.8.71` defines and validates explicit manual decisions.",
    "`v0.8.72` ingests only validated accept/edit items into Clean Study preview.",
    "`v0.8.73` defines the visual validation UI plan.",
    "`v0.8.74` adds read-only UI in `Revizuire document`.",
    "`v0.8.75` smoke-tests the read-only UI through a GET-only TestClient check.",
    "POST /review-document/visual-validation/save",
    "owner-local only",
    "accept",
    "edit",
    "ignore",
    "No implicit approval is allowed.",
    "Pending items remain pending",
    "`course_id`",
    "`item_id`",
    "`decision`",
    "`user_corrected_text`",
    "`user_explanation`",
    "The form must not submit:",
    "bbox coordinates",
    "crop path",
    "page image path",
    "absolute local path",
    "ready flag",
    "Those values must be reloaded server-side from existing local artifacts.",
    "formula_visual_evidence/visual_items.bbox.with-ocrmath-candidates.json",
    "formula_visual_evidence/visual_items.bbox.validated.json",
    "The route must identify the item by `item_id`.",
    "The route must not trust client-submitted crop paths, bbox coordinates, page numbers, or ready flags.",
    "`accept` is valid only when:",
    "`crop_exists=true`",
    "`ocr_math_candidate_text` is non-empty",
    "`user_decision=accept`",
    "`ocr_math_status=validated_by_user`",
    "`ready_for_study=true`",
    "`edit` is valid only when:",
    "`user_corrected_text` is non-empty after trimming",
    "`user_decision=edit`",
    "`ignore` is valid only when:",
    "`user_decision=ignore`",
    "`ocr_math_status=not_applicable`",
    "`ready_for_study=false`",
    "Ignored items must not enter Clean Study.",
    "Items not included in the submitted decision remain pending.",
    "A GET request must not write anything.",
    "The future save action should write only:",
    "formula_visual_evidence/visual_items.bbox.validation-summary.json",
    "The write should be atomic or replace-safe.",
    "The write should preserve unrelated items.",
    "Saving decisions must not directly write Clean Study.",
    "Clean Study may include only:",
    "`user_decision=accept` or `user_decision=edit`",
    "Clean Study must exclude:",
    "`user_decision=ignore`",
    "`user_decision=pending`",
    "bounded validation",
    "`course_id` must use a safe ASCII allowlist.",
    "`item_id` must be treated as an identifier only, not as a path.",
    "The route must not join client-controlled paths.",
    "The route must not expose stack traces.",
    "The route must escape all reflected values in HTML.",
    "The route must redirect only to a safe local `Revizuire document` URL.",
    "`Acceptă`",
    "`Salvează corectarea`",
    "`Ignoră`",
    "This milestone does not implement the save action.",
    "It does not add a route.",
    "It does not add buttons.",
    "It does not submit a form.",
    "It does not call any route.",
    "It does not start the server.",
    "It does not upload a PDF.",
    "It does not run `/generate`.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "It does not run OCR Math.",
    "It does not generate crops.",
    "It does not write `visual_items.bbox.validated.json`.",
    "It does not write `visual_items.clean-study.preview.json`.",
    "It does not write Progress.",
    "It does not build.",
    "It does not create a ZIP.",
    "It does not create OneDrive staging.",
    "It does not create a share link.",
    "It does not deliver to testers.",
    "It does not distribute anything.",
    "It does not create a public release.",
    "v0.8.77-owner-local-review-document-visual-validation-save-action-implementation-no-share-no-delivery",
]

for term in required_terms:
    if term not in doc_text:
        fail("FAILED_V0876_DOC_TERM_MISSING=" + term)

web_diff = subprocess.check_output(
    ["git", "diff", "--name-only", "--", "services/api/web_app.py"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).strip()

if web_diff:
    fail("FAILED_V0876_WEB_APP_HAS_WORKTREE_DIFF=" + web_diff)

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/review-document-visual-validation-save-action-plan-no-share-no-delivery.md",
    "scripts/dev/check-review-document-visual-validation-save-action-plan-no-share-no-delivery.py",
    "scripts/dev/check-review-document-visual-validation-save-action-plan-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0876_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary = {
    "VOILA_V0_8_76_REVIEW_DOCUMENT_VISUAL_VALIDATION_SAVE_ACTION_PLAN_CHECK": "PASS",
    "planning_only": True,
    "save_action_implementation_performed": False,
    "web_app_changed": False,
    "route_added": False,
    "post_endpoint_added": False,
    "buttons_added": False,
    "form_submitted": False,
    "route_called": False,
    "server_started": False,
    "manual_decision_write": False,
    "clean_study_write": False,
    "study_route_changed": False,
    "upload_performed": False,
    "generate_performed": False,
    "ocr_run": False,
    "languagetool_run": False,
    "ocr_math_run": False,
    "crop_generation_performed": False,
    "progress_write": False,
    "build_performed": False,
    "zip_created": False,
    "onedrive_staging_created": False,
    "share_link_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "recommended_next": "v0.8.77-owner-local-review-document-visual-validation-save-action-implementation-no-share-no-delivery",
}

evidence_dir = Path(r"D:\dev\tester-runs\v0876-review-document-visual-validation-save-action-plan-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

out_json = evidence_dir / "V0.8.76-REVIEW-DOCUMENT-VISUAL-VALIDATION-SAVE-ACTION-PLAN-CHECK.json"
out_md = evidence_dir / "V0.8.76-REVIEW-DOCUMENT-VISUAL-VALIDATION-SAVE-ACTION-PLAN-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.76 Review Document visual validation save-action plan\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
