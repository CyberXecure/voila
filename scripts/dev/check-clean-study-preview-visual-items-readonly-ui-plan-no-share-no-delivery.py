from __future__ import annotations

import json
import subprocess
from pathlib import Path

repo = Path(".").resolve()

doc = repo / "docs" / "dev" / "clean-study-preview-visual-items-readonly-ui-plan-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"

required_existing_files = [
    repo / "docs" / "dev" / "clean-study-visual-item-ingestion-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-clean-study-refresh-plan-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-clean-study-refresh-implementation-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-clean-study-refresh-ui-control-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-clean-study-refresh-rendered-form-post-smoke-no-share-no-delivery.md",
    repo / "scripts" / "dev" / "build-clean-study-visual-items-from-bbox.py",
    repo / "scripts" / "dev" / "check-review-document-clean-study-refresh-rendered-form-post-smoke-no-share-no-delivery.py",
]


def fail(message: str) -> None:
    raise SystemExit(message)


if not doc.exists():
    fail("FAILED_V0884_DOC_MISSING=" + str(doc))

if not web_app.exists():
    fail("FAILED_V0884_WEB_APP_MISSING=" + str(web_app))

for path in required_existing_files:
    if not path.exists():
        fail("FAILED_V0884_REQUIRED_PREVIOUS_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
web_text = web_app.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.84 Clean Study preview visual items read-only UI plan",
    "This is a planning-only milestone.",
    "It does not implement the UI.",
    "It does not modify `services/api/web_app.py`.",
    "It does not change `/study`.",
    "It does not write Clean Study.",
    "It does not write Progress.",
    "`v0.8.67` defines bbox visual item artifacts.",
    "`v0.8.68` validates bbox visual item artifacts.",
    "`v0.8.69` creates real crop PNG artifacts.",
    "`v0.8.70` creates OCR Math candidates from crop PNG artifacts.",
    "`v0.8.71` applies manual accept/edit/ignore decisions.",
    "`v0.8.72` builds Clean Study visual preview items.",
    "`v0.8.81` implements explicit Clean Study preview refresh.",
    "`v0.8.82` adds the `Actualizează lecția curată` UI control.",
    "`v0.8.83` smoke-tests the rendered refresh form POST flow.",
    "formula_visual_evidence/visual_items.clean-study.preview.json",
    "It should not read:",
    "formula_visual_evidence/visual_items.bbox.validated.json",
    "formula_visual_evidence/visual_items.bbox.with-ocrmath-candidates.json",
    "Clean Study preview should consume the already refreshed learner-facing artifact",
    "`Elemente vizuale validate`",
    "`Formule și imagini validate`",
    "`Sursa: pagina`",
    "`Întrebare`",
    "`Răspuns validat`",
    "`Explicație`",
    "`Verificat în Revizuire document`",
    "The UI may use the crop path internally as an image source.",
    "The UI must not display the raw crop path as text.",
    "The UI must not display absolute paths.",
    "The UI must not expose local filesystem roots.",
    "The UI should include safe alt text.",
    "The UI should degrade gracefully if the crop file is missing.",
    "The future learner-facing UI must not display:",
    "`bbox`",
    "`bbox_units`",
    "`crop_path`",
    "`page_image_path`",
    "`source_visual_item_id`",
    "`study_item_id`",
    "`schema_version`",
    "`source_visual_items_path`",
    "artifact names",
    "absolute paths",
    "local filesystem paths",
    "`ready_for_study`",
    "`ready_for_clean_study`",
    "`user_decision`",
    "`ocr_math_status`",
    "`learning_source`",
    "raw JSON",
    "`Lecția curată nu a fost actualizată încă.`",
    "`Nu există încă elemente vizuale validate pentru lecție.`",
    "This plan does not change `/study`.",
    "Clean Study preview remains a separate preview surface.",
    "The future UI should not rebuild Clean Study automatically.",
    "A GET request to Clean Study preview must not write files.",
    "A page refresh must not write files.",
    "The future UI must escape learner-facing text.",
    "The future UI must not expose stack traces.",
    "The future UI must not trust client-submitted paths.",
    "The future UI should resolve image paths only under the course output directory.",
    "The future UI should reject or hide unsafe image paths.",
    "The future UI should not redirect to user-controlled URLs.",
    "FastAPI TestClient",
    "visual items section is visible",
    "accepted item is visible",
    "edited item is visible with corrected text",
    "explanation is visible",
    "page source is visible",
    "crop image reference is rendered safely when available",
    "missing crop image degrades gracefully",
    "empty state is friendly",
    "technical metadata is hidden",
    "raw JSON is hidden",
    "absolute paths are hidden",
    "GET does not write Clean Study",
    "GET does not write Progress",
    "`/study` remains unchanged",
    "This milestone does not implement the Clean Study visual item UI.",
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
    "It does not refresh Clean Study.",
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
    "v0.8.85-owner-local-clean-study-preview-visual-items-readonly-ui-implementation-no-share-no-delivery",
]

for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_V0884_DOC_TERM_MISSING=" + term)

required_web_terms = [
    "VOILA_V0_8_81_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_ACTION_START",
    "VOILA_V0_8_82_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_UI_CONTROL_START",
    '@app.post("/review-document/visual-validation/refresh-clean-study-preview")',
    "review-document-clean-study-refresh-control",
    "study-clean-preview",
]

for term in required_web_terms:
    if term not in web_text:
        fail("FAILED_V0884_WEB_TERM_MISSING=" + term)

web_diff = subprocess.check_output(
    ["git", "diff", "--name-only", "--", "services/api/web_app.py"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).strip()

if web_diff:
    fail("FAILED_V0884_WEB_APP_HAS_WORKTREE_DIFF=" + web_diff)

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/clean-study-preview-visual-items-readonly-ui-plan-no-share-no-delivery.md",
    "scripts/dev/check-clean-study-preview-visual-items-readonly-ui-plan-no-share-no-delivery.py",
    "scripts/dev/check-clean-study-preview-visual-items-readonly-ui-plan-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0884_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary = {
    "VOILA_V0_8_84_CLEAN_STUDY_PREVIEW_VISUAL_ITEMS_READONLY_UI_PLAN_CHECK": "PASS",
    "planning_only": True,
    "ui_implementation_performed": False,
    "web_app_changed": False,
    "route_added": False,
    "post_endpoint_added": False,
    "button_added": False,
    "form_submitted": False,
    "route_called": False,
    "server_started": False,
    "testclient_used": False,
    "manual_decision_write": False,
    "clean_study_refresh_performed": False,
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
    "input_artifact_planned": "formula_visual_evidence/visual_items.clean-study.preview.json",
    "technical_metadata_hidden_by_plan": True,
    "recommended_next": "v0.8.85-owner-local-clean-study-preview-visual-items-readonly-ui-implementation-no-share-no-delivery",
}

evidence_dir = Path(r"D:\dev\tester-runs\v0884-clean-study-preview-visual-items-readonly-ui-plan-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

out_json = evidence_dir / "V0.8.84-CLEAN-STUDY-PREVIEW-VISUAL-ITEMS-READONLY-UI-PLAN-CHECK.json"
out_md = evidence_dir / "V0.8.84-CLEAN-STUDY-PREVIEW-VISUAL-ITEMS-READONLY-UI-PLAN-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.84 Clean Study preview visual items read-only UI plan\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
