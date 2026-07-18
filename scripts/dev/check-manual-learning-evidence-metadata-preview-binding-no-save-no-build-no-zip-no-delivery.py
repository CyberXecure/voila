from pathlib import Path
import json
import subprocess
import time
import urllib.request

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-learning-evidence-metadata-preview-binding-no-save-no-build-no-zip-no-delivery.md"
v0798_check = root / "scripts" / "dev" / "check-manual-learning-evidence-crop-selection-preview-no-save-no-build-no-zip-no-delivery.py"

for path, marker in [
    (web, "FAILED_V0799_WEB_APP_MISSING"),
    (doc, "FAILED_V0799_DOC_MISSING"),
    (v0798_check, "FAILED_V0799_V0798_CHECK_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_7_99_MANUAL_LEARNING_EVIDENCE_METADATA_PREVIEW_BINDING_START",
    "VOILA_V0_7_99_MANUAL_LEARNING_EVIDENCE_METADATA_PREVIEW_BINDING_JS_START",
    "VOILA_V0_7_99_MANUAL_LEARNING_EVIDENCE_PENDING_PREVIEW_START",
    "v0799BoundBboxPreview",
    "v0799PendingEvidencePreview",
    "v0799TitlePreview",
    "v0799KindPreview",
    "v0799VerifiedTextPreview",
    "v0799ExplanationPreview",
    "v0799SourceStatusPreview",
    "v0799SourceNotePreview",
    "v0799StatusPreview",
    "Pending evidence preview",
    "manual_learning_evidence.preview",
    "updatePendingEvidencePreview(bbox, cropW, cropH);",
    "save_enabled: false",
    "manual_learning_evidence_written: false",
    "crop_file_written: false",
    "learning_pack_changed: false",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0799_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "metadata preview binding",
    "Selected bbox updates",
    "pending evidence preview",
    "save_enabled=false",
    "manual_learning_evidence_written=false",
    "crop_file_written=false",
    "learning_pack_changed=false",
    "POST endpoint",
    "save endpoint",
    "manual_learning_evidence.json write",
    "crop file write",
    "Learning Pack integration",
    "No build.",
    "No ZIP.",
    "No share.",
    "No delivery.",
    "No distribution.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit(f"FAILED_V0799_DOC_TERM_MISSING={term}")

if '@app.post("/owner/manual-learning-evidence' in web_text:
    raise SystemExit("FAILED_V0799_SAVE_POST_ENDPOINT_FOUND")

route_block = web_text[
    web_text.find("VOILA_V0_7_96_MANUAL_LEARNING_EVIDENCE_UI_SKELETON_START"):
    web_text.find("VOILA_V0_7_96_MANUAL_LEARNING_EVIDENCE_UI_SKELETON_END")
]
if ".write_text(" in route_block or "open(" in route_block:
    raise SystemExit("FAILED_V0799_ROUTE_HAS_FILE_WRITE_OR_OPEN")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-learning-evidence-metadata-preview-binding-no-save-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-learning-evidence-metadata-preview-binding-no-save-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-learning-evidence-metadata-preview-binding-no-save-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0799_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

course_id = "03-pag-30-34-vectori-trigonometrie"
manual_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}?page=1"

last_error = ""
manual_status = None
manual_body = ""
for _ in range(10):
    try:
        with urllib.request.urlopen(manual_url, timeout=15) as response:
            manual_status = response.status
            manual_body = response.read().decode("utf-8", errors="replace")
            break
    except Exception as exc:
        last_error = str(exc)
        time.sleep(2)

if manual_status != 200:
    raise SystemExit(f"FAILED_V0799_MANUAL_ROUTE_STATUS={manual_status}; ERROR={last_error}")

runtime_terms = [
    "Manual Learning Evidence · skeleton",
    "Pending evidence preview",
    "v0799BoundBboxPreview",
    "v0799PendingEvidencePreview",
    "manual_learning_evidence.preview",
    "save_enabled",
    "manual_learning_evidence_written",
    "crop_file_written",
    "learning_pack_changed",
    "bbox_px=[]",
]

for term in runtime_terms:
    if term not in manual_body:
        raise SystemExit(f"FAILED_V0799_RUNTIME_TERM_MISSING={term}")

summary = {
    "VOILA_V0_7_99_MANUAL_LEARNING_EVIDENCE_METADATA_PREVIEW_BINDING_CHECK": "PASS",
    "depends_on_v0794_direction_charter": True,
    "depends_on_v0795_ui_design": True,
    "depends_on_v0796_ui_skeleton": True,
    "depends_on_v0797_visual_polish_course_tools_link": True,
    "depends_on_v0798_crop_selection_preview": True,
    "manual_learning_evidence_route": "/owner/manual-learning-evidence/{course_id}?page=1",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "manual_route_status": manual_status,
    "bbox_bound_to_metadata_preview": True,
    "pending_evidence_preview_added": True,
    "preview_artifact_name": "manual_learning_evidence.preview",
    "save_endpoint_implemented": False,
    "manual_learning_evidence_written": False,
    "crop_file_written": False,
    "learning_pack_changed": False,
    "course_generation_changed": False,
    "study_changed": False,
    "progress_changed": False,
    "ocr_rewrite_performed": False,
    "formula_ocr_performed": False,
    "build_performed": False,
    "zip_created": False,
    "share_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "TESTER_READINESS": "BLOCKED_METADATA_PREVIEW_ONLY_NO_SAVE",
    "POLICY": "manual_learning_evidence_metadata_preview_binding_no_save_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0799-manual-learning-evidence-metadata-preview-binding")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.7.99-MANUAL-LEARNING-EVIDENCE-METADATA-PREVIEW-BINDING-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
