from pathlib import Path
import json
import subprocess

repo = Path(".").resolve()

doc = repo / "docs" / "dev" / "bbox-visual-item-contract-no-share-no-delivery.md"
v0865_doc = repo / "docs" / "dev" / "bbox-crop-ocrmath-pipeline-plan-no-share-no-delivery.md"
v0866_doc = repo / "docs" / "dev" / "hide-deprecated-visual-ocrmath-user-links-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"

def fail(message: str) -> None:
    raise SystemExit(message)

for path in [doc, v0865_doc, v0866_doc, web_app]:
    if not path.exists():
        fail("FAILED_V0867_REQUIRED_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
v0865_text = v0865_doc.read_text(encoding="utf-8", errors="replace")
v0866_text = v0866_doc.read_text(encoding="utf-8", errors="replace")
web_text = web_app.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.67 BBox visual item contract",
    "It is a contract milestone only.",
    "No crop generation is implemented.",
    "No OCR Math on crop is implemented.",
    "No Study integration is implemented.",
    "formula_visual_evidence/visual_items.bbox.json",
    "data/output/<course_id>/formula_visual_evidence/visual_items.bbox.json",
    '"schema_version": "v0.8.67"',
    '"item_id": "bbox-item-0001"',
    '"bbox_units": "page_pixels"',
    '"ocr_math_status": "not_run"',
    '"user_decision": "pending"',
    '"ready_for_study": false',
    "Allowed `kind` values",
    "Allowed `bbox_units` values",
    "Allowed `ocr_math_status` values",
    "Allowed `user_decision` values",
    "A visual item may enter clean Study only when:",
    "Items with `user_decision=ignore` must never feed Study.",
    "Items with `user_decision=pending` must never feed Study.",
    "OCR Math may run only after a bbox/crop exists.",
    "LanguageTool suggestions belong to OCR text review.",
    "The user should see one coherent Review Document workspace.",
    "Technical details may remain available under owner-local diagnostics.",
    "Contract only.",
    "No web route change.",
    "No server required.",
    "No POST.",
    "No upload.",
    "No generate.",
    "No OCR run.",
    "No LanguageTool run.",
    "No crop generation.",
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
        fail("FAILED_V0867_DOC_TERM_MISSING=" + term)

required_v0865_terms = [
    "PDF -> OCR text -> LanguageTool suggestions -> page image -> bbox -> real crop -> OCR Math on crop -> manual validation -> clean Study",
    "OCR Math should run only after a bbox/crop exists.",
    "The crop must be a real local artifact, not only a preview.",
]

for term in required_v0865_terms:
    if term not in v0865_text:
        fail("FAILED_V0867_V0865_TERM_MISSING=" + term)

required_v0866_terms = [
    "Display-only UI/navigation change.",
    "It does not delete routes.",
    "Still preserved as owner-local technical capability",
    "Course Tools card `OCR Math Diagnostic`",
    "Course Tools card `Figures`",
    "Course Tools card `Edit crops`",
]

for term in required_v0866_terms:
    if term not in v0866_text:
        fail("FAILED_V0867_V0866_TERM_MISSING=" + term)

required_web_markers = [
    "VOILA_V0_8_66_HIDE_DEPRECATED_HOME_VISUAL_LINKS_START",
    "VOILA_V0_8_66_HIDE_DEPRECATED_COURSE_TOOLS_OCRMATH_CARD_START",
    "VOILA_V0_8_66_HIDE_DEPRECATED_COURSE_TOOLS_FIGURES_CARD_START",
    "VOILA_V0_8_66_HIDE_DEPRECATED_COURSE_TOOLS_EDIT_CROPS_CARD_START",
    "VOILA_V0_8_66_HIDE_DEPRECATED_TOOLS_BAR_FIGURES_LINK",
    "VOILA_V0_8_66_HIDE_DEPRECATED_TOOLS_BAR_EDIT_CROPS_LINK",
    "VOILA_V0_8_66_HIDE_DEPRECATED_TOOLS_BAR_OCRMATH_LINK",
    "VOILA_V0_8_66_HIDE_DEPRECATED_COURSE_TOOLS_BOTTOM_OCRMATH_LINK",
]

for marker in required_web_markers:
    if marker not in web_text:
        fail("FAILED_V0867_V0866_WEB_MARKER_MISSING=" + marker)

start = doc_text.find("```json")
end = doc_text.find("```", start + len("```json"))
if start == -1 or end == -1:
    fail("FAILED_V0867_JSON_BLOCK_NOT_FOUND")

json_text = doc_text[start + len("```json"):end].strip()
try:
    sample = json.loads(json_text)
except Exception as exc:
    fail("FAILED_V0867_JSON_BLOCK_INVALID=" + str(exc))

required_top = ["schema_version", "course_id", "source_pdf", "items"]
for key in required_top:
    if key not in sample:
        fail("FAILED_V0867_SAMPLE_TOP_FIELD_MISSING=" + key)

if sample.get("schema_version") != "v0.8.67":
    fail("FAILED_V0867_SAMPLE_SCHEMA_VERSION_UNEXPECTED")

items = sample.get("items")
if not isinstance(items, list) or not items:
    fail("FAILED_V0867_SAMPLE_ITEMS_INVALID")

item = items[0]
required_item = [
    "item_id",
    "kind",
    "page",
    "bbox",
    "bbox_units",
    "page_image_path",
    "crop_path",
    "crop_exists",
    "ocr_math_candidate_text",
    "ocr_math_status",
    "user_decision",
    "user_corrected_text",
    "user_explanation",
    "ready_for_study",
    "created_by",
    "review_notes",
]
for key in required_item:
    if key not in item:
        fail("FAILED_V0867_SAMPLE_ITEM_FIELD_MISSING=" + key)

allowed_kind = {"formula", "figure", "diagram", "table", "symbol", "mixed", "unknown"}
allowed_bbox_units = {"page_pixels", "pdf_points"}
allowed_ocr_math_status = {
    "not_run",
    "candidate_generated",
    "failed",
    "not_applicable",
    "pending_user_validation",
    "validated_by_user",
}
allowed_user_decision = {"pending", "accept", "edit", "ignore"}

if item["kind"] not in allowed_kind:
    fail("FAILED_V0867_SAMPLE_KIND_UNEXPECTED")

if item["bbox_units"] not in allowed_bbox_units:
    fail("FAILED_V0867_SAMPLE_BBOX_UNITS_UNEXPECTED")

if item["ocr_math_status"] not in allowed_ocr_math_status:
    fail("FAILED_V0867_SAMPLE_OCRMATH_STATUS_UNEXPECTED")

if item["user_decision"] not in allowed_user_decision:
    fail("FAILED_V0867_SAMPLE_USER_DECISION_UNEXPECTED")

bbox = item["bbox"]
if not isinstance(bbox, list) or len(bbox) != 4 or not all(isinstance(x, int) for x in bbox):
    fail("FAILED_V0867_SAMPLE_BBOX_INVALID")

if item["ready_for_study"] is not False:
    fail("FAILED_V0867_SAMPLE_READY_FOR_STUDY_SHOULD_BE_FALSE")

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/bbox-visual-item-contract-no-share-no-delivery.md",
    "scripts/dev/check-bbox-visual-item-contract-no-share-no-delivery.py",
    "scripts/dev/check-bbox-visual-item-contract-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0867_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary = {
    "VOILA_V0_8_67_BBOX_VISUAL_ITEM_CONTRACT_CHECK": "PASS",
    "contract_only": True,
    "implementation_performed": False,
    "canonical_artifact": "formula_visual_evidence/visual_items.bbox.json",
    "schema_version": "v0.8.67",
    "required_top_fields_count": len(required_top),
    "required_item_fields_count": len(required_item),
    "allowed_kind_values_count": len(allowed_kind),
    "allowed_bbox_units_count": len(allowed_bbox_units),
    "allowed_ocr_math_status_values_count": len(allowed_ocr_math_status),
    "allowed_user_decision_values_count": len(allowed_user_decision),
    "study_gate_requires_manual_validation": True,
    "pending_items_blocked_from_study": True,
    "ignored_items_blocked_from_study": True,
    "ocr_math_on_crop_only_rule_documented": True,
    "languagetool_relationship_documented": True,
    "v0865_plan_confirmed": True,
    "v0866_hidden_links_state_confirmed": True,
    "web_route_change_performed": False,
    "server_started": False,
    "post_called": False,
    "upload_performed": False,
    "generate_performed": False,
    "ocr_run": False,
    "languagetool_run": False,
    "crop_generation_performed": False,
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
    "recommended_next": "v0.8.68-owner-local-bbox-visual-item-example-and-validator-no-share-no-delivery",
}

evidence_dir = Path(r"D:\dev\tester-runs\v0867-bbox-visual-item-contract-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

out_json = evidence_dir / "V0.8.67-BBOX-VISUAL-ITEM-CONTRACT-CHECK.json"
out_md = evidence_dir / "V0.8.67-BBOX-VISUAL-ITEM-CONTRACT-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.67 BBox visual item contract\n\n"
    + "\n".join(f"- {k}: {v}" for k, v in summary.items())
    + "\n",
    encoding="utf-8",
)

for k, v in summary.items():
    print(f"{k}={v}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))

