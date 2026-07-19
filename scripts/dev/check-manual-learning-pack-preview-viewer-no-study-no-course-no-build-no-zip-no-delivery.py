from pathlib import Path
import json
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-learning-pack-preview-viewer-no-study-no-course-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V089_WEB_APP_MISSING"),
    (doc, "FAILED_V089_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_9_MANUAL_LEARNING_PACK_PREVIEW_VIEWER_START",
    "VOILA_V0_8_9_MANUAL_LEARNING_PACK_PREVIEW_VIEWER_CSS_START",
    "_voila_v089_find_existing_course_output_dir",
    "_voila_v089_pack_preview_policy_html",
    "_voila_v089_pack_preview_items_html",
    '@app.get("/owner/manual-learning-pack-preview/{course_id}")',
    'data-testid="manual-learning-pack-preview-viewer"',
    'data-testid="manual-learning-pack-preview-schema"',
    'data-testid="manual-learning-pack-preview-course"',
    'data-testid="manual-learning-pack-preview-items-count"',
    'data-testid="manual-learning-pack-preview-policy"',
    'data-testid="manual-learning-pack-preview-items"',
    'data-testid="manual-learning-pack-preview-item"',
    "Manual Learning Pack Preview",
    "manual_learning_pack.preview.json",
    "learning pack preview viewer",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V089_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "read-only viewer",
    "`manual_learning_pack.preview.json`",
    "`/owner/manual-learning-pack-preview/{course_id}`",
    "Reads only",
    "schema",
    "items_count",
    "policy flags",
    "source_evidence_id",
    "verified_text",
    "explanation_ro",
    "No new write endpoint.",
    "No Course integration.",
    "No Study integration.",
    "No Progress integration.",
    "No OCR rewrite.",
    "No Formula OCR.",
    "No crop file write.",
    "No final Learning Pack delivery artifact.",
    "No build.",
    "No ZIP.",
    "No share.",
    "No delivery.",
    "No distribution.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit(f"FAILED_V089_DOC_TERM_MISSING={term}")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/save-draft"') != 1:
    raise SystemExit("FAILED_V089_SAVE_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/verify-draft"') != 1:
    raise SystemExit("FAILED_V089_VERIFY_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/reject-draft"') != 1:
    raise SystemExit("FAILED_V089_REJECT_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"') != 1:
    raise SystemExit("FAILED_V089_EXPORT_ENDPOINT_COUNT")

if web_text.count('@app.get("/owner/manual-learning-pack-preview/{course_id}"') != 1:
    raise SystemExit("FAILED_V089_VIEWER_ROUTE_COUNT")

for forbidden in [
    '@app.post("/owner/manual-learning-pack-preview',
    "course_generation_changed = True",
    "study_changed = True",
    "progress_changed = True",
    "ocr_rewrite_performed = True",
    "formula_ocr_performed = True",
    '"course_generation_changed": True',
    '"study_changed": True',
    '"progress_changed": True',
]:
    if forbidden in web_text:
        raise SystemExit(f"FAILED_V089_FORBIDDEN_TERM_FOUND={forbidden}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-learning-pack-preview-viewer-no-study-no-course-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-learning-pack-preview-viewer-no-study-no-course-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-learning-pack-preview-viewer-no-study-no-course-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V089_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

course_id = "03-pag-30-34-vectori-trigonometrie"
output_dir = root / "data" / "output" / course_id
preview_json = output_dir / "manual_learning_pack.preview.json"

manual_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}?page=1"
save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"
verify_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/verify-draft"
export_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"
viewer_url = f"http://127.0.0.1:8787/owner/manual-learning-pack-preview/{course_id}"

def post_form(url, payload):
    encoded = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=encoded,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status, response.read().decode("utf-8", errors="replace"), response.geturl()
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"FAILED_V089_POST={url}; STATUS={exc.code}; BODY={error_body}")

eligible_id = "v089-check-pack-viewer-eligible"

payload = {
    "draft_id": eligible_id,
    "page": "1",
    "bbox": "[102, 124, 380, 310]",
    "kind": "formula",
    "title": "v0.8.9 viewer eligible",
    "verified_text": "Viewer preview verified text",
    "explanation_ro": "Explicație completă pentru viewer preview.",
    "source_status": "verified",
    "source_note": "Created by v0.8.9 viewer check.",
}

status, body, _ = post_form(save_url, payload)
if status != 200:
    raise SystemExit(f"FAILED_V089_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body, _ = post_form(verify_url, {"draft_id": eligible_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V089_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

export_status, export_body, _ = post_form(export_url, {})
if export_status != 200:
    raise SystemExit(f"FAILED_V089_EXPORT_STATUS={export_status}; BODY={export_body}")

if not preview_json.exists():
    raise SystemExit("FAILED_V089_PREVIEW_JSON_MISSING")

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
    raise SystemExit(f"FAILED_V089_MANUAL_ROUTE_STATUS={manual_status}; ERROR={last_error}")

viewer_status = None
viewer_body = ""
last_viewer_error = ""
for _ in range(10):
    try:
        with urllib.request.urlopen(viewer_url, timeout=15) as response:
            viewer_status = response.status
            viewer_body = response.read().decode("utf-8", errors="replace")
            break
    except Exception as exc:
        last_viewer_error = str(exc)
        time.sleep(2)

if viewer_status != 200:
    raise SystemExit(f"FAILED_V089_VIEWER_ROUTE_STATUS={viewer_status}; ERROR={last_viewer_error}")

runtime_terms = [
    "Manual Learning Pack Preview",
    "manual-learning-pack-preview-viewer",
    "manual-learning-pack-preview-schema",
    "manual-learning-pack-preview-course",
    "manual-learning-pack-preview-items-count",
    "manual-learning-pack-preview-policy",
    "manual-learning-pack-preview-items",
    "manual-learning-pack-preview-item",
    "voila.manual_learning_pack.preview.v1",
    "manual_learning_pack.preview.json",
    "v089-check-pack-viewer-eligible",
    "v0.8.9 viewer eligible",
    "Viewer preview verified text",
    "Explicație completă pentru viewer preview.",
    "course_generation_changed",
    "study_changed",
    "progress_changed",
    "ocr_rewrite_performed",
    "formula_ocr_performed",
    "build_performed",
    "zip_created",
    "share_created",
    "delivery_performed",
    "distribution_performed",
]

for term in runtime_terms:
    if term not in viewer_body:
        raise SystemExit(f"FAILED_V089_VIEWER_RUNTIME_TERM_MISSING={term}")

manual_terms = [
    "learning pack preview viewer",
    "/owner/manual-learning-pack-preview/",
]

for term in manual_terms:
    if term not in manual_body:
        raise SystemExit(f"FAILED_V089_MANUAL_RUNTIME_TERM_MISSING={term}")

pack = json.loads(preview_json.read_text(encoding="utf-8", errors="replace"))
if pack.get("schema") != "voila.manual_learning_pack.preview.v1":
    raise SystemExit(f"FAILED_V089_SCHEMA={pack.get('schema')!r}")

items = pack.get("items")
if not isinstance(items, list):
    raise SystemExit("FAILED_V089_ITEMS_INVALID")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}
if eligible_id not in ids:
    raise SystemExit("FAILED_V089_ELIGIBLE_ID_NOT_IN_PREVIEW_JSON")

summary = {
    "VOILA_V0_8_9_MANUAL_LEARNING_PACK_PREVIEW_VIEWER_CHECK": "PASS",
    "depends_on_v080_save_draft_json": True,
    "depends_on_v081_list_drafts": True,
    "depends_on_v082_verify_draft": True,
    "depends_on_v083_reject_draft": True,
    "depends_on_v084_review_summary": True,
    "depends_on_v085_accepted_preview": True,
    "depends_on_v086_quality_gate": True,
    "depends_on_v087_dry_run_preview": True,
    "depends_on_v088_export_preview_json": True,
    "viewer_route": "/owner/manual-learning-pack-preview/{course_id}",
    "manual_learning_evidence_route": "/owner/manual-learning-evidence/{course_id}?page=1",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "manual_route_status": manual_status,
    "viewer_route_status": viewer_status,
    "preview_viewer_added": True,
    "preview_json_read": True,
    "schema_visible": True,
    "items_count_visible": True,
    "policy_flags_visible": True,
    "preview_items_visible": True,
    "new_write_endpoint_added": False,
    "manual_learning_pack_preview_json_written_by_existing_v088_endpoint_for_fixture": True,
    "crop_file_written": False,
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
    "TESTER_READINESS": "BLOCKED_VIEWER_ONLY_NO_STUDY_COURSE_INTEGRATION",
    "POLICY": "manual_learning_pack_preview_viewer_no_study_no_course_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v089-manual-learning-pack-preview-viewer")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.8.9-MANUAL-LEARNING-PACK-PREVIEW-VIEWER-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
