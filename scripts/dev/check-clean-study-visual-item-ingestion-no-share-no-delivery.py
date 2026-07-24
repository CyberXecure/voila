from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys

repo = Path(".").resolve()

doc = repo / "docs" / "dev" / "clean-study-visual-item-ingestion-no-share-no-delivery.md"
ingest = repo / "scripts" / "dev" / "build-clean-study-visual-items-from-bbox.py"
v0871_doc = repo / "docs" / "dev" / "manual-visual-validation-gate-no-share-no-delivery.md"
validator = repo / "scripts" / "dev" / "validate-bbox-visual-items.py"
web_app = repo / "services" / "api" / "web_app.py"

def fail(message: str) -> None:
    raise SystemExit(message)

for path in [doc, ingest, v0871_doc, validator, web_app]:
    if not path.exists():
        fail("FAILED_V0872_REQUIRED_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
v0871_text = v0871_doc.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.72 Clean Study visual item ingestion",
    "controlled local ingestion step",
    "It is not a default Study integration.",
    "It does not modify the learner Study route.",
    "scripts/dev/build-clean-study-visual-items-from-bbox.py",
    "visual_items.bbox.validated.json",
    "visual_items.clean-study.preview.json",
    "visual_items.clean-study.preview-summary.json",
    "Only validated visual items may enter the Clean Study preview artifact.",
    "`ready_for_study=true`",
    "`user_decision=accept` or `user_decision=edit`",
    "Ignored items are excluded.",
    "Pending items are excluded.",
    "It does not include bbox coordinates.",
    "This milestone does not connect ingestion to the web UI.",
    "It does not modify `services/api/web_app.py`.",
    "It does not modify `/study`.",
    "It does not write Progress.",
    "It does not run `/generate`.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "It does not run OCR Math.",
    "It does not create new crops.",
    "Controlled local Clean Study visual preview artifact only.",
    "No web route change.",
    "No server required.",
    "No POST.",
    "No upload.",
    "No generate.",
    "No OCR run.",
    "No LanguageTool run.",
    "No OCR Math run.",
    "No crop generation.",
    "No default Study route change.",
    "No Progress write.",
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
        fail("FAILED_V0872_DOC_TERM_MISSING=" + term)

for term in [
    "visual_items.bbox.validated.json",
    "Pending and ignored items must not feed Study.",
    "`ready_for_study` becomes `true`",
    "It does not ingest validated items into Study.",
]:
    if term not in v0871_text:
        fail("FAILED_V0872_V0871_TERM_MISSING=" + term)

web_before = web_app.read_text(encoding="utf-8", errors="replace")

subprocess.check_call([sys.executable, "-m", "py_compile", str(ingest)], cwd=str(repo))
subprocess.check_call([sys.executable, "-m", "py_compile", str(validator)], cwd=str(repo))

evidence_dir = Path(r"D:\dev\tester-runs\v0872-clean-study-visual-item-ingestion-no-share-no-delivery")
work_dir = evidence_dir / "work"
output_root = work_dir / "output"
work_dir.mkdir(parents=True, exist_ok=True)
output_root.mkdir(parents=True, exist_ok=True)

validated_path = work_dir / "visual_items.bbox.validated.json"

validated_payload = {
    "schema_version": "v0.8.67",
    "course_id": "synthetic-clean-study-visual-ingestion",
    "source_pdf": "synthetic-clean-study-visual-ingestion.pdf",
    "items": [
        {
            "item_id": "bbox-item-accept",
            "kind": "formula",
            "page": 1,
            "bbox": [80, 100, 780, 260],
            "bbox_units": "pdf_points",
            "page_image_path": "formula_visual_evidence/pages/page-001.png",
            "crop_path": "formula_visual_evidence/crops/page-001-item-accept.png",
            "crop_exists": True,
            "ocr_math_candidate_text": "sin x / cos x",
            "ocr_math_status": "validated_by_user",
            "user_decision": "accept",
            "user_corrected_text": "",
            "user_explanation": "Acceptăm candidatul pentru studiu.",
            "ready_for_study": True,
            "created_by": "v0.8.72-check",
            "review_notes": "Synthetic accepted visual item."
        },
        {
            "item_id": "bbox-item-edit",
            "kind": "formula",
            "page": 2,
            "bbox": [90, 300, 790, 420],
            "bbox_units": "pdf_points",
            "page_image_path": "formula_visual_evidence/pages/page-002.png",
            "crop_path": "formula_visual_evidence/crops/page-002-item-edit.png",
            "crop_exists": True,
            "ocr_math_candidate_text": "tan x = sin x / cos x",
            "ocr_math_status": "validated_by_user",
            "user_decision": "edit",
            "user_corrected_text": "\\tan x = \\frac{\\sin x}{\\cos x}",
            "user_explanation": "Formula corectată intră în studiu.",
            "ready_for_study": True,
            "created_by": "v0.8.72-check",
            "review_notes": "Synthetic edited visual item."
        },
        {
            "item_id": "bbox-item-ignore",
            "kind": "unknown",
            "page": 3,
            "bbox": [100, 500, 300, 580],
            "bbox_units": "pdf_points",
            "page_image_path": "formula_visual_evidence/pages/page-003.png",
            "crop_path": "formula_visual_evidence/crops/page-003-item-ignore.png",
            "crop_exists": True,
            "ocr_math_candidate_text": "",
            "ocr_math_status": "not_applicable",
            "user_decision": "ignore",
            "user_corrected_text": "",
            "user_explanation": "",
            "ready_for_study": False,
            "created_by": "v0.8.72-check",
            "review_notes": "Synthetic ignored visual item."
        },
        {
            "item_id": "bbox-item-pending",
            "kind": "diagram",
            "page": 4,
            "bbox": [400, 500, 700, 760],
            "bbox_units": "pdf_points",
            "page_image_path": "formula_visual_evidence/pages/page-004.png",
            "crop_path": "formula_visual_evidence/crops/page-004-item-pending.png",
            "crop_exists": True,
            "ocr_math_candidate_text": "Diagram ABC",
            "ocr_math_status": "pending_user_validation",
            "user_decision": "pending",
            "user_corrected_text": "",
            "user_explanation": "",
            "ready_for_study": False,
            "created_by": "v0.8.72-check",
            "review_notes": "Synthetic pending visual item."
        }
    ]
}

validated_path.write_text(json.dumps(validated_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

subprocess.check_call([sys.executable, str(validator), str(validated_path)], cwd=str(repo))

subprocess.check_call(
    [
        sys.executable,
        str(ingest),
        "--visual-items",
        str(validated_path),
        "--output-root",
        str(output_root),
    ],
    cwd=str(repo),
)

preview_path = output_root / "formula_visual_evidence" / "visual_items.clean-study.preview.json"
summary_path = output_root / "formula_visual_evidence" / "visual_items.clean-study.preview-summary.json"

for path in [preview_path, summary_path]:
    if not path.exists():
        fail("FAILED_V0872_EXPECTED_ARTIFACT_MISSING=" + str(path))

preview = json.loads(preview_path.read_text(encoding="utf-8"))
summary = json.loads(summary_path.read_text(encoding="utf-8"))

items = preview.get("items")
if not isinstance(items, list):
    fail("FAILED_V0872_PREVIEW_ITEMS_NOT_LIST")

if len(items) != 2:
    fail("FAILED_V0872_PREVIEW_ITEM_COUNT_UNEXPECTED")

ids = {item.get("source_visual_item_id") for item in items if isinstance(item, dict)}
if ids != {"bbox-item-accept", "bbox-item-edit"}:
    fail("FAILED_V0872_PREVIEW_INCLUDED_IDS_UNEXPECTED=" + json.dumps(sorted(ids), ensure_ascii=False))

accept_item = next(item for item in items if item.get("source_visual_item_id") == "bbox-item-accept")
edit_item = next(item for item in items if item.get("source_visual_item_id") == "bbox-item-edit")

if accept_item.get("answer") != "sin x / cos x":
    fail("FAILED_V0872_ACCEPT_ANSWER_UNEXPECTED")

if edit_item.get("answer") != "\\tan x = \\frac{\\sin x}{\\cos x}":
    fail("FAILED_V0872_EDIT_ANSWER_NOT_CORRECTED_TEXT")

if any("bbox" in item for item in items if isinstance(item, dict)):
    fail("FAILED_V0872_LEARNER_ITEM_CONTAINS_BBOX_FIELD")

if not all(item.get("ready_for_clean_study") is True for item in items if isinstance(item, dict)):
    fail("FAILED_V0872_READY_FOR_CLEAN_STUDY_NOT_TRUE")

excluded = preview.get("excluded_items")
if not isinstance(excluded, list) or len(excluded) != 2:
    fail("FAILED_V0872_EXCLUDED_ITEM_COUNT_UNEXPECTED")

excluded_ids = {item.get("source_visual_item_id") for item in excluded if isinstance(item, dict)}
if excluded_ids != {"bbox-item-ignore", "bbox-item-pending"}:
    fail("FAILED_V0872_EXCLUDED_IDS_UNEXPECTED=" + json.dumps(sorted(excluded_ids), ensure_ascii=False))

if summary.get("clean_study_item_count") != 2:
    fail("FAILED_V0872_SUMMARY_CLEAN_STUDY_ITEM_COUNT_UNEXPECTED")
if summary.get("excluded_item_count") != 2:
    fail("FAILED_V0872_SUMMARY_EXCLUDED_ITEM_COUNT_UNEXPECTED")
if summary.get("accepted_count") != 1:
    fail("FAILED_V0872_SUMMARY_ACCEPTED_COUNT_UNEXPECTED")
if summary.get("edited_count") != 1:
    fail("FAILED_V0872_SUMMARY_EDITED_COUNT_UNEXPECTED")

web_after = web_app.read_text(encoding="utf-8", errors="replace")
if web_before != web_after:
    fail("FAILED_V0872_WEB_APP_CHANGED_DURING_CHECK")

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/clean-study-visual-item-ingestion-no-share-no-delivery.md",
    "scripts/dev/build-clean-study-visual-items-from-bbox.py",
    "scripts/dev/check-clean-study-visual-item-ingestion-no-share-no-delivery.py",
    "scripts/dev/check-clean-study-visual-item-ingestion-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0872_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary_out = {
    "VOILA_V0_8_72_CLEAN_STUDY_VISUAL_ITEM_INGESTION_CHECK": "PASS",
    "clean_study_visual_ingestion_added": True,
    "implementation_performed": True,
    "controlled_local_ingestion_performed": True,
    "accepted_item_included": True,
    "edited_item_included_with_corrected_text": True,
    "ignored_item_excluded": True,
    "pending_item_excluded": True,
    "clean_study_preview_artifact_exists": True,
    "clean_study_preview_summary_exists": True,
    "clean_study_item_count": 2,
    "excluded_item_count": 2,
    "learner_items_hide_bbox_field": True,
    "web_route_change_performed": False,
    "web_app_changed": False,
    "study_route_changed": False,
    "server_started": False,
    "post_called": False,
    "upload_performed": False,
    "generate_performed": False,
    "ocr_run": False,
    "languagetool_run": False,
    "ocr_math_run": False,
    "crop_generation_performed": False,
    "default_study_write": False,
    "progress_write": False,
    "build_performed": False,
    "zip_created": False,
    "onedrive_staging_created": False,
    "share_link_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "recommended_next": "v0.8.73-owner-local-review-document-visual-validation-ui-plan-no-share-no-delivery",
    "evidence_output_root": str(output_root),
}

evidence_dir.mkdir(parents=True, exist_ok=True)
out_json = evidence_dir / "V0.8.72-CLEAN-STUDY-VISUAL-ITEM-INGESTION-CHECK.json"
out_md = evidence_dir / "V0.8.72-CLEAN-STUDY-VISUAL-ITEM-INGESTION-CHECK.md"

out_json.write_text(json.dumps(summary_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.72 Clean Study visual item ingestion\n\n"
    + "\n".join(f"- {k}: {v}" for k, v in summary_out.items())
    + "\n",
    encoding="utf-8",
)

for k, v in summary_out.items():
    print(f"{k}={v}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
