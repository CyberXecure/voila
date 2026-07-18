from pathlib import Path
import json
import subprocess
import time
import urllib.request

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-learning-evidence-visual-polish-and-course-tools-link-no-save-no-build-no-delivery.md"
v0796_check = root / "scripts" / "dev" / "check-manual-learning-evidence-ui-skeleton-no-build-no-zip-no-delivery.py"

for path, marker in [
    (web, "FAILED_V0797_WEB_APP_MISSING"),
    (doc, "FAILED_V0797_DOC_MISSING"),
    (v0796_check, "FAILED_V0797_V0796_CHECK_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_7_96_MANUAL_LEARNING_EVIDENCE_UI_SKELETON_START",
    "VOILA_V0_7_97_MANUAL_LEARNING_EVIDENCE_COURSE_TOOLS_LINK_START",
    "VOILA_V0_7_97_MANUAL_LEARNING_EVIDENCE_VISUAL_POLISH_START",
    "manual_learning_evidence_href = html.escape(",
    '"/owner/manual-learning-evidence/" + quote(pdf_path.stem, safe="") + "?page=1"',
    'href="{manual_learning_evidence_href}">Manual evidence</a>',
    "v0797-readonly-banner",
    "v0797-status-row",
    "v0797-chip",
    "Skeleton only · read-only.",
    "crop disabled",
    "save disabled",
    "Learning Pack disabled",
    "owner-local only",
    "manual_learning_evidence.json",
    "Save disabled. Manual crop disabled. Learning Pack integration disabled.",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0797_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "Manual Learning Evidence visual polish",
    "Manual evidence",
    "Course Tools top navigation",
    "port `8787`",
    "port `8790` unused",
    "quote(pdf_path.stem, safe=\"\")",
    "html.escape(..., quote=True)",
    "No mouse crop selection.",
    "No save endpoint.",
    "No manual_learning_evidence.json write.",
    "No Learning Pack integration.",
    "No build.",
    "No ZIP.",
    "No share.",
    "No delivery.",
    "No distribution.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit(f"FAILED_V0797_DOC_TERM_MISSING={term}")

if '@app.post("/owner/manual-learning-evidence' in web_text:
    raise SystemExit("FAILED_V0797_SAVE_ENDPOINT_FOUND")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-learning-evidence-visual-polish-and-course-tools-link-no-save-no-build-no-delivery.md",
    "scripts/dev/check-manual-learning-evidence-visual-polish-and-course-tools-link-no-save-no-build-no-delivery.py",
    "scripts/dev/check-manual-learning-evidence-visual-polish-and-course-tools-link-no-save-no-build-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0797_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

course_id = "03-pag-30-34-vectori-trigonometrie"
pdf_name = course_id + ".pdf"
manual_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}?page=1"
tools_url = f"http://127.0.0.1:8787/course-tools?pdf={pdf_name}"

def fetch(url):
    last_error = ""
    for _ in range(10):
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                return response.status, response.read().decode("utf-8", errors="replace")
        except Exception as exc:
            last_error = str(exc)
            time.sleep(2)
    raise SystemExit(f"FAILED_V0797_RUNTIME_FETCH={url}; ERROR={last_error}")

manual_status, manual_body = fetch(manual_url)
tools_status, tools_body = fetch(tools_url)

if manual_status != 200:
    raise SystemExit(f"FAILED_V0797_MANUAL_ROUTE_STATUS={manual_status}")

if tools_status != 200:
    raise SystemExit(f"FAILED_V0797_COURSE_TOOLS_STATUS={tools_status}")

manual_required = [
    "Manual Learning Evidence · skeleton",
    "Skeleton only · read-only.",
    "crop disabled",
    "save disabled",
    "Learning Pack disabled",
    "manual_learning_evidence.json",
    "Save disabled",
]

for term in manual_required:
    if term not in manual_body:
        raise SystemExit(f"FAILED_V0797_MANUAL_ROUTE_TERM_MISSING={term}")

tools_required = [
    "Manual evidence",
    f"/owner/manual-learning-evidence/{course_id}?page=1",
]

for term in tools_required:
    if term not in tools_body:
        raise SystemExit(f"FAILED_V0797_COURSE_TOOLS_TERM_MISSING={term}")

summary = {
    "VOILA_V0_7_97_MANUAL_LEARNING_EVIDENCE_VISUAL_POLISH_AND_COURSE_TOOLS_LINK_CHECK": "PASS",
    "depends_on_v0794_direction_charter": True,
    "depends_on_v0795_ui_design": True,
    "depends_on_v0796_ui_skeleton": True,
    "course_tools_link_added": True,
    "manual_learning_evidence_route": "/owner/manual-learning-evidence/{course_id}?page=1",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "manual_route_status": manual_status,
    "course_tools_status": tools_status,
    "manual_route_has_visual_polish": True,
    "course_tools_has_manual_evidence_link": True,
    "manual_crop_implemented": False,
    "save_endpoint_implemented": False,
    "manual_learning_evidence_written": False,
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
    "TESTER_READINESS": "BLOCKED_VISUAL_POLISH_ONLY_NO_SAVE_NO_CROP",
    "POLICY": "manual_learning_evidence_visual_polish_course_tools_link_no_save_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0797-manual-learning-evidence-visual-polish-course-tools-link")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.7.97-MANUAL-LEARNING-EVIDENCE-VISUAL-POLISH-COURSE-TOOLS-LINK-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
