from __future__ import annotations

import json
import subprocess
from pathlib import Path

repo = Path(".").resolve()

doc = repo / "docs" / "dev" / "review-to-clean-study-visual-flow-final-audit-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"

required_existing_files = [
    repo / "docs" / "dev" / "bbox-visual-item-contract-no-share-no-delivery.md",
    repo / "docs" / "dev" / "fixtures" / "bbox-visual-items" / "visual_items.bbox.example.json",
    repo / "scripts" / "dev" / "validate-bbox-visual-items.py",
    repo / "docs" / "dev" / "real-crop-artifact-from-bbox-no-share-no-delivery.md",
    repo / "scripts" / "dev" / "build-bbox-visual-crops.py",
    repo / "docs" / "dev" / "ocrmath-on-crop-candidate-no-share-no-delivery.md",
    repo / "scripts" / "dev" / "run-ocrmath-on-bbox-crops.py",
    repo / "docs" / "dev" / "manual-visual-validation-gate-no-share-no-delivery.md",
    repo / "scripts" / "dev" / "apply-bbox-visual-validation-decisions.py",
    repo / "docs" / "dev" / "clean-study-visual-item-ingestion-no-share-no-delivery.md",
    repo / "scripts" / "dev" / "build-clean-study-visual-items-from-bbox.py",
    repo / "docs" / "dev" / "review-document-visual-validation-ui-plan-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-readonly-ui-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-readonly-browser-smoke-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-save-action-plan-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-save-action-implementation-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-form-controls-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-form-controls-post-smoke-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-clean-study-refresh-plan-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-clean-study-refresh-implementation-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-clean-study-refresh-ui-control-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-clean-study-refresh-rendered-form-post-smoke-no-share-no-delivery.md",
    repo / "docs" / "dev" / "clean-study-preview-visual-items-readonly-ui-plan-no-share-no-delivery.md",
    repo / "docs" / "dev" / "clean-study-preview-visual-items-readonly-ui-implementation-no-share-no-delivery.md",
    repo / "docs" / "dev" / "clean-study-preview-visual-items-readonly-ui-smoke-no-share-no-delivery.md",
    repo / "scripts" / "dev" / "check-review-document-clean-study-refresh-rendered-form-post-smoke-no-share-no-delivery.py",
    repo / "scripts" / "dev" / "check-clean-study-preview-visual-items-readonly-ui-implementation-no-share-no-delivery.py",
    repo / "scripts" / "dev" / "check-clean-study-preview-visual-items-readonly-ui-smoke-no-share-no-delivery.py",
]


def fail(message: str) -> None:
    raise SystemExit(message)


if not doc.exists():
    fail("FAILED_V0887_DOC_MISSING=" + str(doc))

if not web_app.exists():
    fail("FAILED_V0887_WEB_APP_MISSING=" + str(web_app))

for path in required_existing_files:
    if not path.exists():
        fail("FAILED_V0887_REQUIRED_CHAIN_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
web_text = web_app.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.87 Review-to-Clean-Study visual flow final audit",
    "This is an audit-only milestone.",
    "It does not implement new behavior.",
    "It does not modify `services/api/web_app.py`.",
    "It does not add a route.",
    "It does not add a POST endpoint.",
    "It does not change `/study`.",
    "It does not write Clean Study.",
    "It does not write Progress.",
    "`v0.8.67` defines the bbox visual item contract.",
    "`v0.8.68` validates bbox visual item artifacts.",
    "`v0.8.69` creates real crop PNG artifacts from bbox.",
    "`v0.8.70` creates OCR Math candidates from crop PNG artifacts.",
    "`v0.8.71` applies manual accept/edit/ignore validation.",
    "`v0.8.72` builds learner-facing Clean Study visual preview items.",
    "`v0.8.73` plans Review Document visual validation UI.",
    "`v0.8.74` adds read-only visual validation UI in Revizuire document.",
    "`v0.8.75` smoke-tests the read-only UI.",
    "`v0.8.76` plans the visual validation save action.",
    "`v0.8.77` implements the save action.",
    "`v0.8.78` adds rendered form controls.",
    "`v0.8.79` smoke-tests rendered accept/edit/ignore form POST flow.",
    "`v0.8.80` plans Clean Study preview refresh.",
    "`v0.8.81` implements explicit Clean Study preview refresh.",
    "`v0.8.82` adds the `Actualizează lecția curată` UI control.",
    "`v0.8.83` smoke-tests the rendered refresh form POST flow.",
    "`v0.8.84` plans Clean Study preview visual item display.",
    "`v0.8.85` implements read-only Clean Study preview visual item display.",
    "`v0.8.86` smoke-tests the Clean Study preview visual item UI.",
    "`visual_items.bbox.validated.json`",
    "`visual_items.clean-study.preview.json`",
    "Clean Study preview read-only learner UI",
    "friendly Romanian labels",
    "hidden technical metadata",
    "safe image rendering",
    "missing-image fallback",
    "The audited learner-facing UI must not expose:",
    "bbox",
    "bbox_units",
    "raw crop paths",
    "page image paths",
    "source visual item IDs",
    "study item IDs",
    "schema versions",
    "artifact names",
    "absolute paths",
    "local filesystem roots",
    "ready flags",
    "user decision internals",
    "OCR Math status internals",
    "learning source internals",
    "raw JSON",
    "This milestone does not rebuild the app.",
    "It does not create a ZIP.",
    "It does not create OneDrive staging.",
    "It does not create a share link.",
    "It does not deliver to testers.",
    "It does not distribute anything.",
    "It does not create a public release.",
    "The flow remains owner-local.",
    "It does not claim full tester readiness.",
    "A separate real-course manual smoke milestone is still required",
    "v0.8.88-owner-local-real-course-review-to-clean-study-visual-flow-manual-smoke-no-share-no-delivery",
]

for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_V0887_DOC_TERM_MISSING=" + term)

required_web_terms = [
    "VOILA_V0_8_74_REVIEW_DOCUMENT_VISUAL_VALIDATION_READONLY_UI_START",
    "VOILA_V0_8_77_REVIEW_DOCUMENT_VISUAL_VALIDATION_SAVE_ACTION_START",
    "VOILA_V0_8_78_REVIEW_DOCUMENT_VISUAL_VALIDATION_FORM_CONTROLS",
    "VOILA_V0_8_81_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_ACTION_START",
    '@app.post("/review-document/visual-validation/refresh-clean-study-preview")',
    "VOILA_V0_8_82_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_UI_CONTROL_START",
    "Actualizează lecția curată",
    "VOILA_V0_8_85_CLEAN_STUDY_PREVIEW_VISUAL_ITEMS_READONLY_UI_START",
    "_voila_v0885_visual_items_section_html",
    "_voila_v0885_install_clean_study_preview_visual_items_route_wrapper",
    "_VOILA_V0_8_85_CLEAN_STUDY_PREVIEW_VISUAL_ITEMS_ROUTE_WRAPPED",
    "visual_items.clean-study.preview.json",
    "Elemente vizuale validate",
]

for term in required_web_terms:
    if term not in web_text:
        fail("FAILED_V0887_WEB_TERM_MISSING=" + term)

web_diff = subprocess.check_output(
    ["git", "diff", "--name-only", "--", "services/api/web_app.py"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).strip()

if web_diff:
    fail("FAILED_V0887_WEB_APP_HAS_WORKTREE_DIFF=" + web_diff)

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/review-to-clean-study-visual-flow-final-audit-no-share-no-delivery.md",
    "scripts/dev/check-review-to-clean-study-visual-flow-final-audit-no-share-no-delivery.py",
    "scripts/dev/check-review-to-clean-study-visual-flow-final-audit-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0887_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary = {
    "VOILA_V0_8_87_REVIEW_TO_CLEAN_STUDY_VISUAL_FLOW_FINAL_AUDIT_CHECK": "PASS",
    "audit_only": True,
    "implementation_performed": False,
    "web_app_changed": False,
    "route_added": False,
    "post_endpoint_added": False,
    "form_submitted": False,
    "route_called": False,
    "server_started": False,
    "testclient_used": False,
    "review_document_visual_ui_present": True,
    "visual_save_action_present": True,
    "visual_form_controls_present": True,
    "clean_study_refresh_action_present": True,
    "clean_study_refresh_ui_control_present": True,
    "clean_study_visual_items_ui_present": True,
    "visual_flow_docs_present": True,
    "visual_flow_checks_present": True,
    "technical_metadata_policy_audited": True,
    "owner_local_only": True,
    "full_tester_readiness_claimed": False,
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
    "recommended_next": "v0.8.88-owner-local-real-course-review-to-clean-study-visual-flow-manual-smoke-no-share-no-delivery",
}

evidence_dir = Path(r"D:\dev\tester-runs\v0887-review-to-clean-study-visual-flow-final-audit-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

out_json = evidence_dir / "V0.8.87-REVIEW-TO-CLEAN-STUDY-VISUAL-FLOW-FINAL-AUDIT-CHECK.json"
out_md = evidence_dir / "V0.8.87-REVIEW-TO-CLEAN-STUDY-VISUAL-FLOW-FINAL-AUDIT-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.87 Review-to-Clean-Study visual flow final audit\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
