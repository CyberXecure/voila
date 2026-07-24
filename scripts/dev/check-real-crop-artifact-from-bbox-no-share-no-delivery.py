from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import subprocess
import sys

repo = Path(".").resolve()

doc = repo / "docs" / "dev" / "real-crop-artifact-from-bbox-no-share-no-delivery.md"
builder = repo / "scripts" / "dev" / "build-bbox-visual-crops.py"
validator = repo / "scripts" / "dev" / "validate-bbox-visual-items.py"
contract_doc = repo / "docs" / "dev" / "bbox-visual-item-contract-no-share-no-delivery.md"
example_doc = repo / "docs" / "dev" / "bbox-visual-item-example-and-validator-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"

def fail(message: str) -> None:
    raise SystemExit(message)

for path in [doc, builder, validator, contract_doc, example_doc, web_app]:
    if not path.exists():
        fail("FAILED_V0869_REQUIRED_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
contract_text = contract_doc.read_text(encoding="utf-8", errors="replace")
example_text = example_doc.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.69 Real crop artifact from bbox",
    "controlled local builder",
    "create real PNG crop artifacts",
    "scripts/dev/build-bbox-visual-crops.py",
    "page image PNG files under `formula_visual_evidence/pages/`",
    "crop PNG files under `formula_visual_evidence/crops/`",
    "visual_items.bbox.with-crops.json",
    "visual_items.bbox.crop-summary.json",
    "This milestone does not connect the builder to the web UI.",
    "It does not modify `services/api/web_app.py`.",
    "It does not run `/generate`.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "It does not run OCR Math.",
    "It does not ingest the crop into Study.",
    "Controlled local crop artifact generation only.",
    "No web route change.",
    "No server required.",
    "No POST.",
    "No upload.",
    "No generate.",
    "No OCR run.",
    "No LanguageTool run.",
    "No OCR Math run.",
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
        fail("FAILED_V0869_DOC_TERM_MISSING=" + term)

for term in [
    "formula_visual_evidence/visual_items.bbox.json",
    "crop_path",
    "crop_exists",
    "OCR Math may run only after a bbox/crop exists.",
]:
    if term not in contract_text:
        fail("FAILED_V0869_CONTRACT_TERM_MISSING=" + term)

for term in [
    "validate-bbox-visual-items.py",
    "Study gate rules enforced",
]:
    if term not in example_text:
        fail("FAILED_V0869_EXAMPLE_VALIDATOR_TERM_MISSING=" + term)

web_before = web_app.read_text(encoding="utf-8", errors="replace")

subprocess.check_call([sys.executable, "-m", "py_compile", str(builder)], cwd=str(repo))
subprocess.check_call([sys.executable, "-m", "py_compile", str(validator)], cwd=str(repo))

evidence_dir = Path(r"D:\dev\tester-runs\v0869-real-crop-artifact-from-bbox-no-share-no-delivery")
work_dir = evidence_dir / "work"
output_root = work_dir / "output"
work_dir.mkdir(parents=True, exist_ok=True)
output_root.mkdir(parents=True, exist_ok=True)

pdf_path = work_dir / "synthetic-bbox-crop-source.pdf"
visual_items_path = work_dir / "visual_items.bbox.json"

try:
    import fitz
except Exception as exc:
    fail("FAILED_V0869_IMPORT_PYMUPDF=" + str(exc))

doc_pdf = fitz.open()
page = doc_pdf.new_page(width=800, height=1000)
page.draw_rect(fitz.Rect(100, 120, 700, 300), color=(0, 0, 0), width=2)
page.insert_text((130, 190), "sin x / cos x", fontsize=32)
page.draw_rect(fitz.Rect(100, 500, 700, 760), color=(0, 0, 0), width=2)
page.insert_text((130, 610), "Diagram ABC", fontsize=32)
doc_pdf.save(str(pdf_path))
doc_pdf.close()

payload = {
    "schema_version": "v0.8.67",
    "course_id": "synthetic-bbox-crop-source",
    "source_pdf": "synthetic-bbox-crop-source.pdf",
    "items": [
        {
            "item_id": "bbox-item-0001",
            "kind": "formula",
            "page": 1,
            "bbox": [100, 120, 700, 300],
            "bbox_units": "pdf_points",
            "page_image_path": "formula_visual_evidence/pages/page-001.png",
            "crop_path": "formula_visual_evidence/crops/page-001-item-0001.png",
            "crop_exists": False,
            "ocr_math_candidate_text": "sin x / cos x",
            "ocr_math_status": "pending_user_validation",
            "user_decision": "accept",
            "user_corrected_text": "",
            "user_explanation": "Synthetic accepted formula crop.",
            "ready_for_study": True,
            "created_by": "v0.8.69-check",
            "review_notes": "Synthetic local check only."
        },
        {
            "item_id": "bbox-item-0002",
            "kind": "diagram",
            "page": 1,
            "bbox": [100, 500, 700, 760],
            "bbox_units": "pdf_points",
            "page_image_path": "formula_visual_evidence/pages/page-001.png",
            "crop_path": "formula_visual_evidence/crops/page-001-item-0002.png",
            "crop_exists": False,
            "ocr_math_candidate_text": "Diagram ABC",
            "ocr_math_status": "not_applicable",
            "user_decision": "accept",
            "user_corrected_text": "",
            "user_explanation": "Synthetic accepted diagram crop.",
            "ready_for_study": True,
            "created_by": "v0.8.69-check",
            "review_notes": "Synthetic local check only."
        }
    ]
}
visual_items_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

subprocess.check_call(
    [
        sys.executable,
        str(builder),
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

page_png = output_root / "formula_visual_evidence" / "pages" / "page-001.png"
crop_1 = output_root / "formula_visual_evidence" / "crops" / "page-001-item-0001.png"
crop_2 = output_root / "formula_visual_evidence" / "crops" / "page-001-item-0002.png"
updated_path = output_root / "formula_visual_evidence" / "visual_items.bbox.with-crops.json"
summary_path = output_root / "formula_visual_evidence" / "visual_items.bbox.crop-summary.json"

for path in [page_png, crop_1, crop_2, updated_path, summary_path]:
    if not path.exists():
        fail("FAILED_V0869_EXPECTED_ARTIFACT_MISSING=" + str(path))
    if path.suffix.lower() == ".png" and path.stat().st_size <= 0:
        fail("FAILED_V0869_PNG_EMPTY=" + str(path))

updated = json.loads(updated_path.read_text(encoding="utf-8"))
items = updated.get("items", [])
if len(items) != 2:
    fail("FAILED_V0869_UPDATED_ITEM_COUNT_UNEXPECTED")
if not all(item.get("crop_exists") is True for item in items):
    fail("FAILED_V0869_UPDATED_CROP_EXISTS_NOT_TRUE")

summary_data = json.loads(summary_path.read_text(encoding="utf-8"))
if summary_data.get("generated_crop_count") != 2:
    fail("FAILED_V0869_SUMMARY_GENERATED_CROP_COUNT_UNEXPECTED")

spec = importlib.util.spec_from_file_location("validate_bbox_visual_items", validator)
if spec is None or spec.loader is None:
    fail("FAILED_V0869_VALIDATOR_IMPORT_SPEC")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ok, errors, validator_summary = module.validate_file(updated_path)
if not ok:
    fail("FAILED_V0869_UPDATED_ARTIFACT_VALIDATOR_ERRORS=" + json.dumps(errors, ensure_ascii=False))

web_after = web_app.read_text(encoding="utf-8", errors="replace")
if web_before != web_after:
    fail("FAILED_V0869_WEB_APP_CHANGED_DURING_CHECK")

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/real-crop-artifact-from-bbox-no-share-no-delivery.md",
    "scripts/dev/build-bbox-visual-crops.py",
    "scripts/dev/check-real-crop-artifact-from-bbox-no-share-no-delivery.py",
    "scripts/dev/check-real-crop-artifact-from-bbox-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0869_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary_out = {
    "VOILA_V0_8_69_REAL_CROP_ARTIFACT_FROM_BBOX_CHECK": "PASS",
    "real_crop_artifact_builder_added": True,
    "implementation_performed": True,
    "controlled_local_crop_generation_performed": True,
    "synthetic_pdf_used": True,
    "generated_page_png_exists": page_png.exists(),
    "generated_crop_png_count": 2,
    "generated_crop_pngs_non_empty": crop_1.stat().st_size > 0 and crop_2.stat().st_size > 0,
    "updated_visual_items_with_crops_exists": updated_path.exists(),
    "crop_summary_exists": summary_path.exists(),
    "updated_items_crop_exists_true": True,
    "updated_artifact_validator_pass": True,
    "web_route_change_performed": False,
    "web_app_changed": False,
    "server_started": False,
    "post_called": False,
    "upload_performed": False,
    "generate_performed": False,
    "ocr_run": False,
    "languagetool_run": False,
    "ocr_math_run": False,
    "study_write": False,
    "progress_write": False,
    "build_performed": False,
    "zip_created": False,
    "onedrive_staging_created": False,
    "share_link_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "recommended_next": "v0.8.70-owner-local-ocrmath-on-crop-candidate-no-share-no-delivery",
    "evidence_output_root": str(output_root),
}

evidence_dir.mkdir(parents=True, exist_ok=True)
out_json = evidence_dir / "V0.8.69-REAL-CROP-ARTIFACT-FROM-BBOX-CHECK.json"
out_md = evidence_dir / "V0.8.69-REAL-CROP-ARTIFACT-FROM-BBOX-CHECK.md"

out_json.write_text(json.dumps(summary_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.69 Real crop artifact from bbox\n\n"
    + "\n".join(f"- {k}: {v}" for k, v in summary_out.items())
    + "\n",
    encoding="utf-8",
)

for k, v in summary_out.items():
    print(f"{k}={v}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))

