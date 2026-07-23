from pathlib import Path
import json
import subprocess
import sys

repo = Path(".").resolve()
doc = repo / "docs" / "dev" / "real-upload-to-review-pipeline-audit-no-share-no-delivery.md"
evidence_dir = Path(r"D:\dev\tester-runs\v0864-real-upload-to-review-pipeline-audit-no-share-no-delivery")
step6b = evidence_dir / "STEP6B-bbox-ocrmath-architecture-summary.txt"

required_doc_terms = [
    "V0.8.64_AUDIT_VERDICT=BLOCKED_FOR_TESTER_SHARE",
    "PDF page image -> bbox -> crop -> OCR Math on crop -> manual validation -> clean Study",
    "Global OCR Math before bbox/crop is deprecated",
    "Old shrink/preview/hybrid figure/crop UI must be removed",
    "No build.",
    "No ZIP.",
    "No OneDrive staging.",
    "No share link.",
    "No tester delivery.",
    "No distribution.",
    "No public release.",
]

required_step6b_terms = [
    "GLOBAL_OCR_MATH_BEFORE_BBOX=DEPRECATED_FOR_USER_FLOW",
    "BBOX_CROP_OCR_MATH_AFTER_SELECTION=CANONICAL_USER_FLOW",
    "OLD_SHRINK_PREVIEW_HYBRID_CROP=TO_BE_REMOVED_FROM_USER_FACING_FLOW",
    "V0.8.64_AUDIT_VERDICT=BLOCKED_FOR_TESTER_SHARE",
    "REASON_1=/generate currently runs global OCR Math before bbox/crop.",
    "REASON_2=LanguageTool artifacts are not proven as automatic pipeline output.",
    "REASON_3=Old visual/crop/shrink/hybrid flows may still be exposed or present.",
    "REASON_4=Canonical user-facing flow must be bbox/crop-first, then OCR Math per crop, then manual validation.",
    "NEXT=v0.8.65-owner-local-bbox-crop-ocrmath-pipeline-plan-no-share-no-delivery",
]

def fail(message: str) -> None:
    raise SystemExit(message)

if not doc.exists():
    fail("FAILED_V0864_DOC_MISSING=" + str(doc))

if not step6b.exists():
    fail("FAILED_V0864_STEP6B_EVIDENCE_MISSING=" + str(step6b))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_V0864_DOC_TERM_MISSING=" + term)

step6b_text = step6b.read_text(encoding="utf-8", errors="replace")
for term in required_step6b_terms:
    if term not in step6b_text:
        fail("FAILED_V0864_STEP6B_TERM_MISSING=" + term)

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/real-upload-to-review-pipeline-audit-no-share-no-delivery.md",
    "scripts/dev/check-real-upload-to-review-pipeline-audit-no-share-no-delivery.py",
    "scripts/dev/check-real-upload-to-review-pipeline-audit-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0864_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary = {
    "VOILA_V0_8_64_REAL_UPLOAD_TO_REVIEW_PIPELINE_AUDIT_CHECK": "PASS",
    "audit_verdict": "BLOCKED_FOR_TESTER_SHARE",
    "global_ocr_math_before_bbox": "DEPRECATED_FOR_USER_FLOW",
    "bbox_crop_ocr_math_after_selection": "CANONICAL_USER_FLOW",
    "old_shrink_preview_hybrid_crop": "TO_BE_REMOVED_FROM_USER_FACING_FLOW",
    "language_tool_artifacts_proven_automatic_pipeline_output": False,
    "build_performed": False,
    "zip_created": False,
    "onedrive_staging_created": False,
    "share_link_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "recommended_next": "v0.8.65-owner-local-bbox-crop-ocrmath-pipeline-plan-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.64-REAL-UPLOAD-TO-REVIEW-PIPELINE-AUDIT-CHECK.json"
out_md = evidence_dir / "V0.8.64-REAL-UPLOAD-TO-REVIEW-PIPELINE-AUDIT-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.64 Real upload-to-review pipeline audit\n\n"
    + "\n".join(f"- {k}: {v}" for k, v in summary.items())
    + "\n",
    encoding="utf-8",
)

for k, v in summary.items():
    print(f"{k}={v}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
