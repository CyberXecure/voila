from pathlib import Path
import json

course_id = "03-pag-30-34-vectori-trigonometrie"
root = Path(".").resolve()
out_dir = root / "data" / "output" / course_id
web_app = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "crop-editor-formula-evidence-audit-no-build-no-zip-no-delivery.md"

formula_manifest = out_dir / "formula_visual_evidence.manifest.json"
formula_edits = out_dir / "formula_visual_evidence.edits.json"
figure_manifest = out_dir / "figures_hybrid" / "figures_manifest.hybrid.json"

web_text = web_app.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "@app.get(\"/edit-crops\")",
    "ensure_crop_editor_running",
    "crop_editor_app:app",
    "formula_visual_evidence.manifest.json",
    "owner_formula_visual_evidence_view",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0793_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "Formula Visual Evidence is technically functional but not sufficient for learning quality",
    "Do not create a separate Formula Crop Editor",
    "source=formula_visual_evidence",
    "formula_visual_evidence.edits.json",
    "edited_crops",
    "raw_manifest_modified",
    "No OCR rewrite",
    "No build",
    "No ZIP",
    "No delivery",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit(f"FAILED_V0793_DOC_TERM_MISSING={term}")

summary = {
    "VOILA_V0_7_93_CROP_EDITOR_FORMULA_EVIDENCE_AUDIT_CHECK": "PASS",
    "course_id": course_id,
    "formula_manifest_exists": formula_manifest.exists(),
    "formula_edits_exists": formula_edits.exists(),
    "existing_figure_manifest_exists": figure_manifest.exists(),
    "edit_crops_route_present": "@app.get(\"/edit-crops\")" in web_text,
    "crop_editor_external_app_present": "crop_editor_app:app" in web_text,
    "recommended_next_artifact": str(formula_edits),
    "recommended_next_step": "v0.7.94 integrate formula_visual_evidence source mode into existing Crop Editor",
    "CROP_EDITOR_BEHAVIOR_CHANGED": False,
    "OCR_REWRITE_PERFORMED": False,
    "FORMULA_OCR_PERFORMED": False,
    "BUILD_PERFORMED": False,
    "ZIP_CREATED": False,
    "SHARE_CREATED": False,
    "DELIVERY_PERFORMED": False,
    "TESTER_READINESS": "BLOCKED_PENDING_MANUAL_FORMULA_CROP_EDITOR_INTEGRATION",
    "POLICY": "crop_editor_formula_evidence_audit_no_build_no_zip_no_share_no_delivery_no_distribution",
}

if not summary["formula_manifest_exists"]:
    raise SystemExit("FAILED_V0793_FORMULA_MANIFEST_MISSING")

if summary["formula_edits_exists"]:
    raise SystemExit("FAILED_V0793_FORMULA_EDITS_SHOULD_NOT_EXIST_YET")

evidence = Path(r"D:\dev\tester-runs\v0793-crop-editor-formula-evidence-audit")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.7.93-CROP-EDITOR-FORMULA-EVIDENCE-AUDIT-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    if isinstance(v, (str, bool, int)) or v is None:
        print(f"{k}={v}")
print("EVIDENCE=" + str(out))
