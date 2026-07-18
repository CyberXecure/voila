from pathlib import Path
import json
import subprocess
import time
import urllib.request

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-learning-evidence-ui-skeleton-no-build-no-zip-no-delivery.md"
design = root / "docs" / "dev" / "manual-learning-evidence-ui-design-no-build-no-zip-no-delivery.md"
charter = root / "docs" / "dev" / "voila-direction-charter-and-guard-no-build-no-zip-no-delivery.md"

for path, marker in [
    (charter, "FAILED_V0796_DIRECTION_CHARTER_MISSING"),
    (design, "FAILED_V0796_DESIGN_DOC_MISSING"),
    (doc, "FAILED_V0796_SKELETON_DOC_MISSING"),
    (web, "FAILED_V0796_WEB_APP_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_7_96_MANUAL_LEARNING_EVIDENCE_UI_SKELETON_START",
    '@app.get("/owner/manual-learning-evidence/{course_id}"',
    'alias="page"',
    "Manual Learning Evidence · skeleton",
    "manual_learning_evidence.json",
    "formula_visual_evidence",
    "title",
    "kind",
    "verified_text",
    "explanation_ro",
    "source_status",
    "source_note",
    "possible_source_error",
    "accepted_owner_verified",
    "rejected_noise",
    "Save disabled",
    "Manual crop disabled",
    "Learning Pack integration disabled",
    "cleaned = \"\".join",
    "quote(safe_course_id, safe=\"\")",
    "html.escape(f\"/course-tools?pdf={pdf_name_url}\"",
    "html.escape(f\"/owner/formula-visual-evidence/{safe_course_id_url}/view\"",
    "page_image_src = html.escape(",
    "safe_course_id_html = html.escape(",
    "output_dir_html = html.escape(",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0796_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "read-only skeleton route",
    "/owner/manual-learning-evidence/{course_id}",
    "port `8787`",
    "does not use the old external Crop Editor on port `8790`",
    "disabled metadata form",
    "title",
    "kind",
    "verified_text",
    "explanation_ro",
    "source_status",
    "source_note",
    "possible_source_error",
    "manual_learning_evidence.json",
    "manual_learning_evidence/crops/",
    "No mouse crop selection.",
    "No save endpoint.",
    "No Learning Pack integration.",
    "No build.",
    "No ZIP.",
    "No share.",
    "No delivery.",
    "No distribution.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit(f"FAILED_V0796_DOC_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-learning-evidence-ui-skeleton-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-learning-evidence-ui-skeleton-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-learning-evidence-ui-skeleton-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0796_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

course_id = "03-pag-30-34-vectori-trigonometrie"
page_image = root / "data" / "output" / course_id / "formula_visual_evidence" / "pages" / "page-001.png"
url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}?page=1"

route_status = None
route_has_terms = False
last_error = ""

for _ in range(10):
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            body = response.read().decode("utf-8", errors="replace")
            route_status = response.status
            route_has_terms = all(
                term in body
                for term in [
                    "Manual Learning Evidence · skeleton",
                    "manual_learning_evidence.json",
                    "title",
                    "verified_text",
                    "possible_source_error",
                    "Save disabled",
                ]
            )
            break
    except Exception as exc:
        last_error = str(exc)
        time.sleep(2)

if route_status != 200:
    raise SystemExit(f"FAILED_V0796_RUNTIME_ROUTE_STATUS={route_status}; ERROR={last_error}")

if not route_has_terms:
    raise SystemExit("FAILED_V0796_RUNTIME_ROUTE_REQUIRED_TERMS_MISSING")

summary = {
    "VOILA_V0_7_96_MANUAL_LEARNING_EVIDENCE_UI_SKELETON_CHECK": "PASS",
    "depends_on_v0794_direction_charter": True,
    "depends_on_v0795_ui_design": True,
    "future_route": "/owner/manual-learning-evidence/{course_id}",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "read_only_skeleton_implemented": True,
    "source_page_image_expected": str(page_image),
    "source_page_image_exists": page_image.exists(),
    "runtime_route_status": route_status,
    "runtime_route_has_required_terms": route_has_terms,
    "metadata_form_disabled": True,
    "manual_learning_evidence_artifact": "manual_learning_evidence.json",
    "manual_learning_evidence_crops_dir": "manual_learning_evidence/crops/",
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
    "TESTER_READINESS": "BLOCKED_SKELETON_ONLY_NO_SAVE_NO_CROP",
    "POLICY": "manual_learning_evidence_ui_skeleton_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0796-manual-learning-evidence-ui-skeleton")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.7.96-MANUAL-LEARNING-EVIDENCE-UI-SKELETON-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
