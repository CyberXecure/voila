from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import subprocess
import sys

repo = Path(".").resolve()

doc = repo / "docs" / "dev" / "ocrmath-on-crop-candidate-no-share-no-delivery.md"
runner = repo / "scripts" / "dev" / "run-ocrmath-on-bbox-crops.py"
crop_builder = repo / "scripts" / "dev" / "build-bbox-visual-crops.py"
validator = repo / "scripts" / "dev" / "validate-bbox-visual-items.py"
v0869_doc = repo / "docs" / "dev" / "real-crop-artifact-from-bbox-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"

def fail(message: str) -> None:
    raise SystemExit(message)

for path in [doc, runner, crop_builder, validator, v0869_doc, web_app]:
    if not path.exists():
        fail("FAILED_V0870_REQUIRED_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
v0869_text = v0869_doc.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.70 OCR Math on crop candidate",
    "controlled local runner",
    "existing bbox crop PNG artifacts",
    "scripts/dev/run-ocrmath-on-bbox-crops.py",
    "visual_items.bbox.with-crops.json",
    "visual_items.bbox.with-ocrmath-candidates.json",
    "visual_items.bbox.ocrmath-candidates-summary.json",
    "OCR Math on crop produces only a candidate.",
    "It must not mark the item as ready for Study.",
    "`ocr_math_status` becomes `pending_user_validation`",
    "`user_decision` remains `pending`",
    "`ready_for_study` remains `false`",
    "This milestone does not connect the runner to the web UI.",
    "It does not modify `services/api/web_app.py`.",
    "It does not run `/generate`.",
    "It does not run global OCR Math.",
    "It does not run LanguageTool.",
    "It does not ingest candidates into Study.",
    "Controlled local OCR Math candidate extraction from crop PNG only.",
    "No web route change.",
    "No server required.",
    "No POST.",
    "No upload.",
    "No generate.",
    "No global OCR Math run.",
    "No LanguageTool run.",
    "No Study write.",
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
        fail("FAILED_V0870_DOC_TERM_MISSING=" + term)

for term in [
    "scripts/dev/build-bbox-visual-crops.py",
    "visual_items.bbox.with-crops.json",
    "crop PNG files under `formula_visual_evidence/crops/`",
]:
    if term not in v0869_text:
        fail("FAILED_V0870_V0869_TERM_MISSING=" + term)

web_before = web_app.read_text(encoding="utf-8", errors="replace")

subprocess.check_call([sys.executable, "-m", "py_compile", str(runner)], cwd=str(repo))
subprocess.check_call([sys.executable, "-m", "py_compile", str(crop_builder)], cwd=str(repo))
subprocess.check_call([sys.executable, "-m", "py_compile", str(validator)], cwd=str(repo))

evidence_dir = Path(r"D:\dev\tester-runs\v0870-ocrmath-on-crop-candidate-no-share-no-delivery")
work_dir = evidence_dir / "work"
output_root = work_dir / "output"
work_dir.mkdir(parents=True, exist_ok=True)
output_root.mkdir(parents=True, exist_ok=True)

try:
    import fitz
except Exception as exc:
    fail("FAILED_V0870_IMPORT_PYMUPDF=" + str(exc))

pdf_path = work_dir / "synthetic-ocrmath-crop-source.pdf"
visual_items_path = work_dir / "visual_items.bbox.json"

doc_pdf = fitz.open()
page = doc_pdf.new_page(width=900, height=500)
page.draw_rect(fitz.Rect(80, 100, 780, 260), color=(0, 0, 0), width=2)
page.insert_text((130, 185), "sin x / cos x", fontsize=42)
doc_pdf.save(str(pdf_path))
doc_pdf.close()

payload = {
    "schema_version": "v0.8.67",
    "course_id": "synthetic-ocrmath-crop-source",
    "source_pdf": "synthetic-ocrmath-crop-source.pdf",
    "items": [
        {
            "item_id": "bbox-item-0001",
            "kind": "formula",
            "page": 1,
            "bbox": [80, 100, 780, 260],
            "bbox_units": "pdf_points",
            "page_image_path": "formula_visual_evidence/pages/page-001.png",
            "crop_path": "formula_visual_evidence/crops/page-001-item-0001.png",
            "crop_exists": False,
            "ocr_math_candidate_text": "",
            "ocr_math_status": "not_run",
            "user_decision": "pending",
            "user_corrected_text": "",
            "user_explanation": "",
            "ready_for_study": False,
            "created_by": "v0.8.70-check",
            "review_notes": "Synthetic local check only."
        }
    ]
}
visual_items_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

subprocess.check_call(
    [
        sys.executable,
        str(crop_builder),
        "--pdf",
        str(pdf_path),
        "--visual-items",
        str(visual_items_path),
        "--output-root",
        str(output_root),
        "--zoom",
        "2.0",
    ],
    cwd=str(repo),
)

with_crops = output_root / "formula_visual_evidence" / "visual_items.bbox.with-crops.json"
crop_png = output_root / "formula_visual_evidence" / "crops" / "page-001-item-0001.png"

if not with_crops.exists():
    fail("FAILED_V0870_WITH_CROPS_ARTIFACT_MISSING")
if not crop_png.exists() or crop_png.stat().st_size <= 0:
    fail("FAILED_V0870_CROP_PNG_MISSING_OR_EMPTY")

subprocess.check_call(
    [
        sys.executable,
        str(runner),
        "--visual-items",
        str(with_crops),
        "--output-root",
        str(output_root),
        "--lang",
        "eng",
        "--psm",
        "6",
    ],
    cwd=str(repo),
)

with_candidates = output_root / "formula_visual_evidence" / "visual_items.bbox.with-ocrmath-candidates.json"
candidate_summary = output_root / "formula_visual_evidence" / "visual_items.bbox.ocrmath-candidates-summary.json"

for path in [with_candidates, candidate_summary]:
    if not path.exists():
        fail("FAILED_V0870_EXPECTED_OCRMATH_ARTIFACT_MISSING=" + str(path))

candidate_payload = json.loads(with_candidates.read_text(encoding="utf-8"))
items = candidate_payload.get("items", [])
if len(items) != 1:
    fail("FAILED_V0870_CANDIDATE_ITEM_COUNT_UNEXPECTED")

item = items[0]
candidate_text = str(item.get("ocr_math_candidate_text") or "").strip()
if not candidate_text:
    fail("FAILED_V0870_CANDIDATE_TEXT_EMPTY")

if item.get("ocr_math_status") != "pending_user_validation":
    fail("FAILED_V0870_OCRMATH_STATUS_NOT_PENDING_USER_VALIDATION")

if item.get("user_decision") != "pending":
    fail("FAILED_V0870_USER_DECISION_NOT_PENDING")

if item.get("ready_for_study") is not False:
    fail("FAILED_V0870_READY_FOR_STUDY_NOT_FALSE")

summary_data = json.loads(candidate_summary.read_text(encoding="utf-8"))
if summary_data.get("processed_count") != 1:
    fail("FAILED_V0870_SUMMARY_PROCESSED_COUNT_UNEXPECTED")
if summary_data.get("candidate_generated_count") != 1:
    fail("FAILED_V0870_SUMMARY_CANDIDATE_COUNT_UNEXPECTED")
if summary_data.get("ready_for_study_count") != 0:
    fail("FAILED_V0870_SUMMARY_READY_COUNT_UNEXPECTED")

spec = importlib.util.spec_from_file_location("validate_bbox_visual_items", validator)
if spec is None or spec.loader is None:
    fail("FAILED_V0870_VALIDATOR_IMPORT_SPEC")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ok, errors, validator_summary = module.validate_file(with_candidates)
if not ok:
    fail("FAILED_V0870_CANDIDATE_ARTIFACT_VALIDATOR_ERRORS=" + json.dumps(errors, ensure_ascii=False))

web_after = web_app.read_text(encoding="utf-8", errors="replace")
if web_before != web_after:
    fail("FAILED_V0870_WEB_APP_CHANGED_DURING_CHECK")

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/ocrmath-on-crop-candidate-no-share-no-delivery.md",
    "scripts/dev/run-ocrmath-on-bbox-crops.py",
    "scripts/dev/check-ocrmath-on-crop-candidate-no-share-no-delivery.py",
    "scripts/dev/check-ocrmath-on-crop-candidate-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0870_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary_out = {
    "VOILA_V0_8_70_OCRMATH_ON_CROP_CANDIDATE_CHECK": "PASS",
    "ocrmath_on_crop_candidate_runner_added": True,
    "implementation_performed": True,
    "controlled_local_ocrmath_on_crop_performed": True,
    "synthetic_pdf_used": True,
    "crop_builder_used": True,
    "crop_png_exists_before_ocrmath": True,
    "candidate_artifact_exists": True,
    "candidate_summary_exists": True,
    "candidate_generated_count": 1,
    "ocr_math_status_pending_user_validation": True,
    "user_decision_remains_pending": True,
    "ready_for_study_remains_false": True,
    "updated_artifact_validator_pass": True,
    "global_ocr_math_run": False,
    "web_route_change_performed": False,
    "web_app_changed": False,
    "server_started": False,
    "post_called": False,
    "upload_performed": False,
    "generate_performed": False,
    "languagetool_run": False,
    "study_write": False,
    "progress_write": False,
    "build_performed": False,
    "zip_created": False,
    "onedrive_staging_created": False,
    "share_link_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "recommended_next": "v0.8.71-owner-local-manual-visual-validation-gate-no-share-no-delivery",
    "candidate_text_observed": candidate_text,
    "evidence_output_root": str(output_root),
}

evidence_dir.mkdir(parents=True, exist_ok=True)
out_json = evidence_dir / "V0.8.70-OCRMATH-ON-CROP-CANDIDATE-CHECK.json"
out_md = evidence_dir / "V0.8.70-OCRMATH-ON-CROP-CANDIDATE-CHECK.md"

out_json.write_text(json.dumps(summary_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.70 OCR Math on crop candidate\n\n"
    + "\n".join(f"- {k}: {v}" for k, v in summary_out.items())
    + "\n",
    encoding="utf-8",
)

for k, v in summary_out.items():
    print(f"{k}={v}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
