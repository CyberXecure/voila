from __future__ import annotations

import json
import subprocess
from pathlib import Path

repo = Path(".").resolve()

doc = repo / "docs" / "dev" / "real-course-review-to-clean-study-visual-flow-final-readiness-audit-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"

required_existing_files = [
    repo / "docs" / "dev" / "review-to-clean-study-visual-flow-final-audit-no-share-no-delivery.md",
    repo / "scripts" / "dev" / "check-review-to-clean-study-visual-flow-final-audit-no-share-no-delivery.py",
    repo / "docs" / "dev" / "real-course-review-to-clean-study-visual-flow-manual-smoke-no-share-no-delivery.md",
    repo / "scripts" / "dev" / "check-real-course-review-to-clean-study-visual-flow-manual-smoke-no-share-no-delivery.py",
    repo / "docs" / "dev" / "clean-study-preview-visual-items-readonly-ui-implementation-no-share-no-delivery.md",
    repo / "docs" / "dev" / "clean-study-preview-visual-items-readonly-ui-smoke-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-clean-study-refresh-rendered-form-post-smoke-no-share-no-delivery.md",
    repo / "docs" / "dev" / "review-document-visual-validation-form-controls-post-smoke-no-share-no-delivery.md",
]


def fail(message: str) -> None:
    raise SystemExit(message)


if not doc.exists():
    fail("FAILED_V0889_DOC_MISSING=" + str(doc))

if not web_app.exists():
    fail("FAILED_V0889_WEB_APP_MISSING=" + str(web_app))

for path in required_existing_files:
    if not path.exists():
        fail("FAILED_V0889_REQUIRED_PREVIOUS_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
web_text = web_app.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.89 Real-course Review-to-Clean-Study visual flow final readiness audit",
    "This is an audit-only milestone.",
    "It does not implement new behavior.",
    "It does not modify `services/api/web_app.py`.",
    "It does not add a route.",
    "It does not add a POST endpoint.",
    "It does not change `/study`.",
    "It does not write Clean Study.",
    "It does not write Progress.",
    "v0.8.88-owner-local-real-course-review-to-clean-study-visual-flow-manual-smoke-no-share-no-delivery",
    "`03-pag-30-34-vectori-trigonometrie`",
    "Review Document GET works",
    "rendered visual validation forms are found",
    "accept POST works",
    "edit POST works",
    "ignore POST works",
    "temporary validated visual artifact is created",
    "refresh form submits only `course_id`",
    "explicit refresh POST works",
    "temporary Clean Study preview artifact is created",
    "Clean Study preview GET works",
    "accepted item is visible",
    "edited item is visible with corrected text",
    "ignored item is excluded",
    "safe image data URI is rendered",
    "missing crop degrades gracefully",
    "technical metadata is hidden",
    "raw JSON is hidden",
    "absolute paths are hidden",
    "real course visual artifacts are restored after the check",
    "no persistent smoke artifacts are left in the real course",
    "Progress is not modified",
    "`/study` is not changed",
    "This audit confirms the owner-local visual review-to-clean-study flow is ready as a local feature path.",
    "This audit does not claim full tester readiness.",
    "This audit does not authorize a tester package.",
    "This audit does not authorize a ZIP rebuild.",
    "This audit does not authorize OneDrive staging.",
    "This audit does not authorize a share link.",
    "This audit does not authorize delivery.",
    "This audit does not authorize distribution.",
    "This audit does not authorize a public release.",
    "`visual_items.bbox.validated.json`",
    "`Actualizează lecția curată`",
    "`visual_items.clean-study.preview.json`",
    "Clean Study preview read-only learner UI",
    "Before any new tester package or share decision, a separate package-readiness chain is required.",
    "package rebuild preflight",
    "extracted-package validation",
    "real browser smoke from extracted package",
    "explicit owner approval before any share or delivery",
    "It does not submit a form.",
    "It does not call a route.",
    "It does not use TestClient.",
    "It does not start uvicorn.",
    "It does not start LanguageTool.",
    "It does not upload a PDF.",
    "It does not run `/generate`.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "It does not run OCR Math.",
    "It does not generate crops.",
    "It does not write manual decisions.",
    "It does not refresh Clean Study.",
    "It does not build.",
    "It does not create a ZIP.",
    "It does not create OneDrive staging.",
    "It does not create a share link.",
    "It does not deliver to testers.",
    "It does not distribute anything.",
    "It does not create a public release.",
    "v0.8.90-owner-local-package-rebuild-preflight-after-visual-flow-no-share-no-delivery",
]

for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_V0889_DOC_TERM_MISSING=" + term)

required_web_terms = [
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
        fail("FAILED_V0889_WEB_TERM_MISSING=" + term)

web_diff = subprocess.check_output(
    ["git", "diff", "--name-only", "--", "services/api/web_app.py"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).strip()

if web_diff:
    fail("FAILED_V0889_WEB_APP_HAS_WORKTREE_DIFF=" + web_diff)

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/real-course-review-to-clean-study-visual-flow-final-readiness-audit-no-share-no-delivery.md",
    "scripts/dev/check-real-course-review-to-clean-study-visual-flow-final-readiness-audit-no-share-no-delivery.py",
    "scripts/dev/check-real-course-review-to-clean-study-visual-flow-final-readiness-audit-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0889_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary = {
    "VOILA_V0_8_89_REAL_COURSE_REVIEW_TO_CLEAN_STUDY_VISUAL_FLOW_FINAL_READINESS_AUDIT_CHECK": "PASS",
    "audit_only": True,
    "implementation_performed": False,
    "web_app_changed": False,
    "route_added": False,
    "post_endpoint_added": False,
    "form_submitted": False,
    "route_called": False,
    "testclient_used": False,
    "real_course_smoke_baseline": "v0.8.88",
    "real_course_id": "03-pag-30-34-vectori-trigonometrie",
    "review_to_clean_study_visual_flow_ready_as_owner_local_feature_path": True,
    "full_tester_readiness_claimed": False,
    "tester_package_authorized": False,
    "zip_rebuild_authorized": False,
    "onedrive_staging_authorized": False,
    "share_link_authorized": False,
    "delivery_authorized": False,
    "distribution_authorized": False,
    "public_release_authorized": False,
    "separate_package_readiness_chain_required": True,
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
    "recommended_next": "v0.8.90-owner-local-package-rebuild-preflight-after-visual-flow-no-share-no-delivery",
}

evidence_dir = Path(r"D:\dev\tester-runs\v0889-real-course-review-to-clean-study-visual-flow-final-readiness-audit-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

out_json = evidence_dir / "V0.8.89-REAL-COURSE-REVIEW-TO-CLEAN-STUDY-VISUAL-FLOW-FINAL-READINESS-AUDIT-CHECK.json"
out_md = evidence_dir / "V0.8.89-REAL-COURSE-REVIEW-TO-CLEAN-STUDY-VISUAL-FLOW-FINAL-READINESS-AUDIT-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.89 Real-course Review-to-Clean-Study visual flow final readiness audit\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
