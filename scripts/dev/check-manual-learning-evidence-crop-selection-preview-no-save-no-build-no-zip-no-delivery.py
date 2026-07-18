from pathlib import Path
import json
import subprocess
import time
import urllib.request

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-learning-evidence-crop-selection-preview-no-save-no-build-no-zip-no-delivery.md"
v0797_check = root / "scripts" / "dev" / "check-manual-learning-evidence-visual-polish-and-course-tools-link-no-save-no-build-no-delivery.py"

for path, marker in [
    (web, "FAILED_V0798_WEB_APP_MISSING"),
    (doc, "FAILED_V0798_DOC_MISSING"),
    (v0797_check, "FAILED_V0798_V0797_CHECK_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_7_98_MANUAL_LEARNING_EVIDENCE_CROP_SELECTION_PREVIEW_START",
    "VOILA_V0_7_98_MANUAL_LEARNING_EVIDENCE_CROP_SELECTION_PREVIEW_JS_START",
    "v0798-crop-shell",
    "v0798-selection-box",
    "v0798-preview-panel",
    "v0798PreviewCanvas",
    "v0798BboxText",
    "bbox_px=[]",
    "bbox_px=[",
    "shell.addEventListener(\"pointerdown\"",
    "shell.addEventListener(\"pointermove\"",
    "shell.addEventListener(\"pointerup\"",
    "ctx.drawImage(image",
    "Crop preview ready. Save is disabled in v0.7.98.",
    "Preview only. Save disabled. No manual_learning_evidence.json write.",
    "Save disabled. Manual crop disabled. Learning Pack integration disabled.",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0798_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "browser-only crop selection preview",
    "Pointer drag selection",
    "Visible selection rectangle",
    "bbox_px=[x1, y1, x2, y2]",
    "Browser-only crop preview",
    "does not add:",
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
        raise SystemExit(f"FAILED_V0798_DOC_TERM_MISSING={term}")

if '@app.post("/owner/manual-learning-evidence' in web_text:
    raise SystemExit("FAILED_V0798_SAVE_POST_ENDPOINT_FOUND")

if "manual_learning_evidence.json" in web_text and ".write_text(" in web_text[web_text.find("VOILA_V0_7_96_MANUAL_LEARNING_EVIDENCE_UI_SKELETON_START"):web_text.find("VOILA_V0_7_96_MANUAL_LEARNING_EVIDENCE_UI_SKELETON_END")]:
    raise SystemExit("FAILED_V0798_ROUTE_WRITES_MANUAL_EVIDENCE_JSON")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-learning-evidence-crop-selection-preview-no-save-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-learning-evidence-crop-selection-preview-no-save-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-learning-evidence-crop-selection-preview-no-save-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0798_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

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
    raise SystemExit(f"FAILED_V0798_MANUAL_ROUTE_STATUS={manual_status}; ERROR={last_error}")

runtime_terms = [
    "Manual Learning Evidence · skeleton",
    "Crop selection preview",
    "v0798CropShell",
    "v0798SelectionBox",
    "v0798PreviewCanvas",
    "bbox_px=[]",
    "pointerdown",
    "pointermove",
    "pointerup",
    "Crop preview ready. Save is disabled in v0.7.98.",
    "No manual_learning_evidence.json write.",
]

for term in runtime_terms:
    if term not in manual_body:
        raise SystemExit(f"FAILED_V0798_RUNTIME_TERM_MISSING={term}")

summary = {
    "VOILA_V0_7_98_MANUAL_LEARNING_EVIDENCE_CROP_SELECTION_PREVIEW_CHECK": "PASS",
    "depends_on_v0794_direction_charter": True,
    "depends_on_v0795_ui_design": True,
    "depends_on_v0796_ui_skeleton": True,
    "depends_on_v0797_visual_polish_course_tools_link": True,
    "manual_learning_evidence_route": "/owner/manual-learning-evidence/{course_id}?page=1",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "manual_route_status": manual_status,
    "browser_pointer_crop_selection_added": True,
    "bbox_preview_added": True,
    "canvas_crop_preview_added": True,
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
    "TESTER_READINESS": "BLOCKED_CROP_PREVIEW_ONLY_NO_SAVE",
    "POLICY": "manual_learning_evidence_crop_selection_preview_no_save_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0798-manual-learning-evidence-crop-selection-preview")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.7.98-MANUAL-LEARNING-EVIDENCE-CROP-SELECTION-PREVIEW-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
