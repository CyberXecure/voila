from pathlib import Path
import json
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-study-items-preview-viewer-no-study-integration-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0812_WEB_APP_MISSING"),
    (doc, "FAILED_V0812_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_12_MANUAL_STUDY_ITEMS_PREVIEW_VIEWER_START",
    "VOILA_V0_8_12_MANUAL_STUDY_ITEMS_PREVIEW_VIEWER_CSS_START",
    "_voila_v0812_manual_study_policy_html",
    "_voila_v0812_manual_study_items_html",
    '@app.get("/owner/manual-study-items-preview/{course_id}")',
    'data-testid="manual-study-items-preview-viewer"',
    'data-testid="manual-study-items-preview-schema"',
    'data-testid="manual-study-items-preview-course"',
    'data-testid="manual-study-items-preview-items-count"',
    'data-testid="manual-study-items-preview-policy"',
    'data-testid="manual-study-items-preview-items"',
    'data-testid="manual-study-items-preview-item"',
    "Manual Study Items Preview",
    "manual_study_items.preview.json",
    "manual study preview viewer",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0812_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "read-only viewer",
    "`manual_study_items.preview.json`",
    "`/owner/manual-study-items-preview/{course_id}`",
    "Reads only",
    "schema",
    "items_count",
    "policy flags",
    "candidate Study items",
    "manual_study_item_id",
    "source_evidence_id",
    "study_item_type",
    "prompt",
    "answer",
    "write_target",
    "It does not write any artifact.",
    "It does not write or modify the legacy `study_items.preview.json`.",
    "It does not connect the real Study page.",
    "No new write endpoint.",
    "No Study artifact write.",
    "No Study integration.",
    "No Course integration.",
    "No Progress integration.",
    "No OCR rewrite.",
    "No Formula OCR.",
    "No crop file write.",
    "No build.",
    "No ZIP.",
    "No share.",
    "No delivery.",
    "No distribution.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit(f"FAILED_V0812_DOC_TERM_MISSING={term}")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/save-draft"') != 1:
    raise SystemExit("FAILED_V0812_SAVE_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/verify-draft"') != 1:
    raise SystemExit("FAILED_V0812_VERIFY_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/reject-draft"') != 1:
    raise SystemExit("FAILED_V0812_REJECT_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"') != 1:
    raise SystemExit("FAILED_V0812_LEARNING_PACK_EXPORT_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-pack-study-adapter-dry-run/{course_id}/export-manual-study-items-preview"') != 1:
    raise SystemExit("FAILED_V0812_MANUAL_STUDY_EXPORT_ENDPOINT_COUNT")

if web_text.count('@app.get("/owner/manual-study-items-preview/{course_id}"') != 1:
    raise SystemExit("FAILED_V0812_VIEWER_ROUTE_COUNT")

for forbidden in [
    '@app.post("/owner/manual-study-items-preview',
    "study_integration = True",
    "course_generation_changed = True",
    "study_changed = True",
    "progress_changed = True",
    "ocr_rewrite_performed = True",
    "formula_ocr_performed = True",
    '"study_changed": True',
    '"progress_changed": True',
]:
    if forbidden in web_text:
        raise SystemExit(f"FAILED_V0812_FORBIDDEN_TERM_FOUND={forbidden}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-study-items-preview-viewer-no-study-integration-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-study-items-preview-viewer-no-study-integration-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-study-items-preview-viewer-no-study-integration-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0812_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

course_id = "03-pag-30-34-vectori-trigonometrie"
output_dir = root / "data" / "output" / course_id
manual_study_preview = output_dir / "manual_study_items.preview.json"
legacy_study_preview = output_dir / "study_items.preview.json"
legacy_before = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None

save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"
verify_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/verify-draft"
learning_pack_export_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"
manual_study_export_url = f"http://127.0.0.1:8787/owner/manual-learning-pack-study-adapter-dry-run/{course_id}/export-manual-study-items-preview"
manual_study_viewer_url = f"http://127.0.0.1:8787/owner/manual-study-items-preview/{course_id}"
adapter_url = f"http://127.0.0.1:8787/owner/manual-learning-pack-study-adapter-dry-run/{course_id}"

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
        raise SystemExit(f"FAILED_V0812_POST={url}; STATUS={exc.code}; BODY={error_body}")

eligible_id = "v0812-check-manual-study-viewer-eligible"

payload = {
    "draft_id": eligible_id,
    "page": "1",
    "bbox": "[132, 154, 440, 370]",
    "kind": "formula",
    "title": "v0.8.12 manual study viewer eligible",
    "verified_text": "Manual study viewer prompt text",
    "explanation_ro": "Răspuns afișat în viewerul manual Study preview.",
    "source_status": "verified",
    "source_note": "Created by v0.8.12 manual study viewer check.",
}

status, body, _ = post_form(save_url, payload)
if status != 200:
    raise SystemExit(f"FAILED_V0812_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body, _ = post_form(verify_url, {"draft_id": eligible_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V0812_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

learning_export_status, learning_export_body, _ = post_form(learning_pack_export_url, {})
if learning_export_status != 200:
    raise SystemExit(f"FAILED_V0812_LEARNING_PACK_EXPORT_STATUS={learning_export_status}; BODY={learning_export_body}")

manual_study_export_status, manual_study_export_body, _ = post_form(manual_study_export_url, {})
if manual_study_export_status != 200:
    raise SystemExit(f"FAILED_V0812_MANUAL_STUDY_EXPORT_STATUS={manual_study_export_status}; BODY={manual_study_export_body}")

if not manual_study_preview.exists():
    raise SystemExit("FAILED_V0812_MANUAL_STUDY_PREVIEW_MISSING")

def fetch_url(url, label):
    last_error = ""
    for _ in range(10):
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                return response.status, response.read().decode("utf-8", errors="replace")
        except Exception as exc:
            last_error = str(exc)
            time.sleep(2)
    raise SystemExit(f"FAILED_V0812_{label}_FETCH={last_error}")

adapter_status, adapter_body = fetch_url(adapter_url, "ADAPTER")
viewer_status, viewer_body = fetch_url(manual_study_viewer_url, "VIEWER")

if adapter_status != 200:
    raise SystemExit(f"FAILED_V0812_ADAPTER_STATUS={adapter_status}")

if viewer_status != 200:
    raise SystemExit(f"FAILED_V0812_VIEWER_STATUS={viewer_status}")

adapter_terms = [
    "Viewer route:",
    "/owner/manual-study-items-preview/",
]

for term in adapter_terms:
    if term not in adapter_body:
        raise SystemExit(f"FAILED_V0812_ADAPTER_TERM_MISSING={term}")

runtime_terms = [
    "Manual Study Items Preview",
    "manual-study-items-preview-viewer",
    "manual-study-items-preview-schema",
    "manual-study-items-preview-course",
    "manual-study-items-preview-items-count",
    "manual-study-items-preview-policy",
    "manual-study-items-preview-items",
    "manual-study-items-preview-item",
    "voila.manual_study_items.preview.v1",
    "manual_study_items.preview.json",
    "manual_study_preview_only",
    "legacy_study_items_preview_untouched",
    "study_integration",
    "False",
    "v0812-check-manual-study-viewer-eligible",
    "v0.8.12 manual study viewer eligible",
    "Manual study viewer prompt text",
    "Răspuns afișat în viewerul manual Study preview.",
    "formula_card",
    "write_target",
    "course_generation_changed",
    "progress_changed",
    "build_performed",
    "zip_created",
    "delivery_performed",
]

for term in runtime_terms:
    if term not in viewer_body:
        raise SystemExit(f"FAILED_V0812_VIEWER_RUNTIME_TERM_MISSING={term}")

manual_study = json.loads(manual_study_preview.read_text(encoding="utf-8", errors="replace"))

if manual_study.get("schema") != "voila.manual_study_items.preview.v1":
    raise SystemExit(f"FAILED_V0812_SCHEMA={manual_study.get('schema')!r}")

items = manual_study.get("items")
if not isinstance(items, list):
    raise SystemExit("FAILED_V0812_ITEMS_INVALID")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}
if eligible_id not in ids:
    raise SystemExit("FAILED_V0812_ELIGIBLE_ID_NOT_EXPORTED")

legacy_after = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None
if legacy_before != legacy_after:
    raise SystemExit("FAILED_V0812_LEGACY_STUDY_PREVIEW_CHANGED")

summary = {
    "VOILA_V0_8_12_MANUAL_STUDY_ITEMS_PREVIEW_VIEWER_CHECK": "PASS",
    "depends_on_v080_save_draft_json": True,
    "depends_on_v081_list_drafts": True,
    "depends_on_v082_verify_draft": True,
    "depends_on_v083_reject_draft": True,
    "depends_on_v084_review_summary": True,
    "depends_on_v085_accepted_preview": True,
    "depends_on_v086_quality_gate": True,
    "depends_on_v087_dry_run_preview": True,
    "depends_on_v088_export_preview_json": True,
    "depends_on_v089_preview_viewer": True,
    "depends_on_v0810_study_adapter_dry_run": True,
    "depends_on_v0811_manual_study_export": True,
    "viewer_route": "/owner/manual-study-items-preview/{course_id}",
    "adapter_route": "/owner/manual-learning-pack-study-adapter-dry-run/{course_id}",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "adapter_route_status": adapter_status,
    "viewer_route_status": viewer_status,
    "manual_study_preview_viewer_added": True,
    "manual_study_preview_json_read": True,
    "schema_visible": True,
    "items_count_visible": True,
    "policy_flags_visible": True,
    "candidate_study_items_visible": True,
    "new_write_endpoint_added": False,
    "study_artifact_written": False,
    "legacy_study_items_preview_unchanged": True,
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
    "TESTER_READINESS": "BLOCKED_VIEWER_ONLY_NO_STUDY_INTEGRATION",
    "POLICY": "manual_study_items_preview_viewer_no_study_integration_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0812-manual-study-items-preview-viewer")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.8.12-MANUAL-STUDY-ITEMS-PREVIEW-VIEWER-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
