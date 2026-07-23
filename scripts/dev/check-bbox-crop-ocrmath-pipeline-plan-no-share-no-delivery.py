from pathlib import Path
import json
import subprocess

repo = Path(".").resolve()

doc = repo / "docs" / "dev" / "bbox-crop-ocrmath-pipeline-plan-no-share-no-delivery.md"
v0864_doc = repo / "docs" / "dev" / "real-upload-to-review-pipeline-audit-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"

def fail(message: str) -> None:
    raise SystemExit(message)

if not doc.exists():
    fail("FAILED_V0865_DOC_MISSING=" + str(doc))

if not v0864_doc.exists():
    fail("FAILED_V0865_V0864_DOC_MISSING=" + str(v0864_doc))

if not web_app.exists():
    fail("FAILED_V0865_WEB_APP_MISSING=" + str(web_app))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
v0864_text = v0864_doc.read_text(encoding="utf-8", errors="replace")
web_text = web_app.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.65 BBox/Crop/OCR Math pipeline plan",
    "No implementation is performed in this milestone.",
    "PDF -> OCR text -> LanguageTool suggestions -> page image -> bbox -> real crop -> OCR Math on crop -> manual validation -> clean Study",
    "Global OCR Math before bbox/crop is deprecated for the user-facing flow.",
    "OCR Math should run only after a bbox/crop exists.",
    "The crop must be a real local artifact, not only a preview.",
    '"ocr_math_status": "not_run_or_pending_user_validation"',
    "LanguageTool suggestions must also be candidates, not automatic truth.",
    "Course Tools should not expose duplicate old crop/figure flows as primary actions.",
    "Technical diagnostics may remain collapsed under `Diagnostic tehnic`.",
    "figures_hybrid",
    "figures.html",
    "old `edit-crops` shrink controls",
    "v0.8.66-owner-local-hide-deprecated-visual-ocrmath-user-links-no-share-no-delivery",
    "No server required.",
    "No POST.",
    "No upload.",
    "No generate.",
    "No OCR run.",
    "No LanguageTool run.",
    "No crop generation.",
    "No build.",
    "No ZIP.",
    "No OneDrive staging.",
    "No share link.",
    "No tester delivery.",
    "No distribution.",
    "No public release.",
]

for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_V0865_DOC_TERM_MISSING=" + term)

required_v0864_terms = [
    "V0.8.64_AUDIT_VERDICT=BLOCKED_FOR_TESTER_SHARE",
    "PDF page image -> bbox -> crop -> OCR Math on crop -> manual validation -> clean Study",
    "Global OCR Math before bbox/crop is deprecated",
    "Old shrink/preview/hybrid figure/crop UI must be removed",
]

for term in required_v0864_terms:
    if term not in v0864_text:
        fail("FAILED_V0865_V0864_DOC_TERM_MISSING=" + term)

extract_idx = web_text.find('"extract pages"')
ocr_math_idx = web_text.find('"build OCR Math report if enabled"')
outline_idx = web_text.find('"build outline"')

if not (extract_idx != -1 and ocr_math_idx != -1 and outline_idx != -1):
    fail("FAILED_V0865_CURRENT_GENERATE_SEQUENCE_MARKERS_MISSING")

if not (extract_idx < ocr_math_idx < outline_idx):
    fail("FAILED_V0865_CURRENT_GENERATE_SEQUENCE_UNEXPECTED")

current_markers = {
    "current_generate_runs_global_ocr_math_before_outline": True,
    "check_ocr_languagetool_endpoint_present": "/check-ocr-languagetool" in web_text,
    "old_figures_hybrid_marker_present": "figures_hybrid" in web_text,
    "old_edit_crops_marker_present": "edit-crops" in web_text,
    "bbox_marker_present": "bbox" in web_text,
    "formula_visual_evidence_marker_present": "formula_visual_evidence" in web_text,
}

for key, value in current_markers.items():
    if value is not True:
        fail("FAILED_V0865_CURRENT_MARKER_FALSE=" + key)

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/bbox-crop-ocrmath-pipeline-plan-no-share-no-delivery.md",
    "scripts/dev/check-bbox-crop-ocrmath-pipeline-plan-no-share-no-delivery.py",
    "scripts/dev/check-bbox-crop-ocrmath-pipeline-plan-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0865_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary = {
    "VOILA_V0_8_65_BBOX_CROP_OCRMATH_PIPELINE_PLAN_CHECK": "PASS",
    "implementation_performed": False,
    "planning_only": True,
    "v0864_blocked_verdict_confirmed": True,
    "canonical_flow": "PDF -> OCR text -> LanguageTool suggestions -> page image -> bbox -> real crop -> OCR Math on crop -> manual validation -> clean Study",
    "global_ocr_math_before_bbox": "DEPRECATED_FOR_USER_FLOW",
    "bbox_crop_ocr_math_after_selection": "CANONICAL_USER_FLOW",
    "old_shrink_preview_hybrid_crop": "TO_BE_REMOVED_FROM_USER_FACING_FLOW",
    "language_tool_suggestions_are_candidates": True,
    "manual_validation_required_before_study": True,
    "current_generate_runs_global_ocr_math_before_outline": True,
    "check_ocr_languagetool_endpoint_present": True,
    "old_figures_hybrid_marker_present": True,
    "old_edit_crops_marker_present": True,
    "bbox_marker_present": True,
    "formula_visual_evidence_marker_present": True,
    "server_started": False,
    "post_called": False,
    "upload_performed": False,
    "generate_performed": False,
    "ocr_run": False,
    "languagetool_run": False,
    "crop_generation_performed": False,
    "build_performed": False,
    "zip_created": False,
    "onedrive_staging_created": False,
    "share_link_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "recommended_next": "v0.8.66-owner-local-hide-deprecated-visual-ocrmath-user-links-no-share-no-delivery",
}

evidence_dir = Path(r"D:\dev\tester-runs\v0865-bbox-crop-ocrmath-pipeline-plan-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

out_json = evidence_dir / "V0.8.65-BBOX-CROP-OCRMATH-PIPELINE-PLAN-CHECK.json"
out_md = evidence_dir / "V0.8.65-BBOX-CROP-OCRMATH-PIPELINE-PLAN-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.65 BBox/Crop/OCR Math pipeline plan\n\n"
    + "\n".join(f"- {k}: {v}" for k, v in summary.items())
    + "\n",
    encoding="utf-8",
)

for k, v in summary.items():
    print(f"{k}={v}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
