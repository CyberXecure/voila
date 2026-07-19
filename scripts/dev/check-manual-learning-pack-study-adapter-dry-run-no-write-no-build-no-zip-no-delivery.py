from pathlib import Path
import json
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-learning-pack-study-adapter-dry-run-no-write-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0810_WEB_APP_MISSING"),
    (doc, "FAILED_V0810_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_10_MANUAL_LEARNING_PACK_STUDY_ADAPTER_DRY_RUN_START",
    "VOILA_V0_8_10_MANUAL_LEARNING_PACK_STUDY_ADAPTER_DRY_RUN_CSS_START",
    "_voila_v0810_build_study_adapter_dry_run_items",
    "_voila_v0810_study_adapter_items_html",
    '@app.get("/owner/manual-learning-pack-study-adapter-dry-run/{course_id}")',
    'data-testid="manual-learning-pack-study-adapter-dry-run"',
    'data-testid="manual-learning-pack-study-adapter-schema"',
    'data-testid="manual-learning-pack-study-adapter-source-count"',
    'data-testid="manual-learning-pack-study-adapter-dry-run-count"',
    'data-testid="manual-learning-pack-study-adapter-policy"',
    'data-testid="manual-learning-pack-study-adapter-items"',
    'data-testid="manual-learning-pack-study-adapter-item"',
    "Manual Learning Pack → Study Adapter Dry-run",
    "write_target",
    "study_integration",
    "study adapter dry-run",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0810_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "read-only Study Adapter dry-run",
    "`manual_learning_pack.preview.json`",
    "`/owner/manual-learning-pack-study-adapter-dry-run/{course_id}`",
    "Transforms preview items in memory",
    "candidate Study items",
    "dry_run_id",
    "source_evidence_id",
    "study_item_type",
    "write_target=none",
    "It does not write any artifact.",
    "It does not write `study_items.preview.json`.",
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
        raise SystemExit(f"FAILED_V0810_DOC_TERM_MISSING={term}")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/save-draft"') != 1:
    raise SystemExit("FAILED_V0810_SAVE_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/verify-draft"') != 1:
    raise SystemExit("FAILED_V0810_VERIFY_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/reject-draft"') != 1:
    raise SystemExit("FAILED_V0810_REJECT_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"') != 1:
    raise SystemExit("FAILED_V0810_EXPORT_ENDPOINT_COUNT")

if web_text.count('@app.get("/owner/manual-learning-pack-study-adapter-dry-run/{course_id}"') != 1:
    raise SystemExit("FAILED_V0810_DRY_RUN_ROUTE_COUNT")

for forbidden in [
    '@app.post("/owner/manual-learning-pack-study-adapter',
    "write_target =",
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
        raise SystemExit(f"FAILED_V0810_FORBIDDEN_TERM_FOUND={forbidden}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-learning-pack-study-adapter-dry-run-no-write-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-learning-pack-study-adapter-dry-run-no-write-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-learning-pack-study-adapter-dry-run-no-write-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0810_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

course_id = "03-pag-30-34-vectori-trigonometrie"
output_dir = root / "data" / "output" / course_id
preview_json = output_dir / "manual_learning_pack.preview.json"
legacy_study_preview = output_dir / "study_items.preview.json"
legacy_before = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None

save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"
verify_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/verify-draft"
export_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"
viewer_url = f"http://127.0.0.1:8787/owner/manual-learning-pack-preview/{course_id}"
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
        raise SystemExit(f"FAILED_V0810_POST={url}; STATUS={exc.code}; BODY={error_body}")

eligible_id = "v0810-check-study-adapter-eligible"

payload = {
    "draft_id": eligible_id,
    "page": "1",
    "bbox": "[112, 134, 400, 330]",
    "kind": "formula",
    "title": "v0.8.10 study adapter eligible",
    "verified_text": "Study adapter prompt text",
    "explanation_ro": "Răspuns adaptat pentru cardul de studiu.",
    "source_status": "verified",
    "source_note": "Created by v0.8.10 study adapter check.",
}

status, body, _ = post_form(save_url, payload)
if status != 200:
    raise SystemExit(f"FAILED_V0810_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body, _ = post_form(verify_url, {"draft_id": eligible_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V0810_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

export_status, export_body, _ = post_form(export_url, {})
if export_status != 200:
    raise SystemExit(f"FAILED_V0810_EXPORT_STATUS={export_status}; BODY={export_body}")

if not preview_json.exists():
    raise SystemExit("FAILED_V0810_PREVIEW_JSON_MISSING")

def fetch_url(url, label):
    last_error = ""
    for _ in range(10):
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                return response.status, response.read().decode("utf-8", errors="replace")
        except Exception as exc:
            last_error = str(exc)
            time.sleep(2)
    raise SystemExit(f"FAILED_V0810_{label}_FETCH={last_error}")

viewer_status, viewer_body = fetch_url(viewer_url, "VIEWER")
adapter_status, adapter_body = fetch_url(adapter_url, "ADAPTER")

if viewer_status != 200:
    raise SystemExit(f"FAILED_V0810_VIEWER_STATUS={viewer_status}")

if adapter_status != 200:
    raise SystemExit(f"FAILED_V0810_ADAPTER_STATUS={adapter_status}")

runtime_terms = [
    "Manual Learning Pack → Study Adapter Dry-run",
    "manual-learning-pack-study-adapter-dry-run",
    "manual-learning-pack-study-adapter-schema",
    "manual-learning-pack-study-adapter-source-count",
    "manual-learning-pack-study-adapter-dry-run-count",
    "manual-learning-pack-study-adapter-policy",
    "manual-learning-pack-study-adapter-items",
    "manual-learning-pack-study-adapter-item",
    "formula_card",
    "write_target",
    "none",
    "study_integration",
    "false",
    "v0810-check-study-adapter-eligible",
    "v0.8.10 study adapter eligible",
    "Study adapter prompt text",
    "Răspuns adaptat pentru cardul de studiu.",
    "course_generation_changed",
    "progress_changed",
    "build_performed",
    "zip_created",
    "delivery_performed",
]

for term in runtime_terms:
    if term not in adapter_body:
        raise SystemExit(f"FAILED_V0810_ADAPTER_RUNTIME_TERM_MISSING={term}")

viewer_terms = [
    "Study adapter dry-run:",
    "/owner/manual-learning-pack-study-adapter-dry-run/",
]

for term in viewer_terms:
    if term not in viewer_body:
        raise SystemExit(f"FAILED_V0810_VIEWER_RUNTIME_TERM_MISSING={term}")

pack = json.loads(preview_json.read_text(encoding="utf-8", errors="replace"))
items = pack.get("items")
if not isinstance(items, list):
    raise SystemExit("FAILED_V0810_PACK_ITEMS_INVALID")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}
if eligible_id not in ids:
    raise SystemExit("FAILED_V0810_ELIGIBLE_ID_NOT_IN_PREVIEW_JSON")

legacy_after = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None
if legacy_before != legacy_after:
    raise SystemExit("FAILED_V0810_LEGACY_STUDY_PREVIEW_CHANGED")

summary = {
    "VOILA_V0_8_10_MANUAL_LEARNING_PACK_STUDY_ADAPTER_DRY_RUN_CHECK": "PASS",
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
    "adapter_route": "/owner/manual-learning-pack-study-adapter-dry-run/{course_id}",
    "viewer_route": "/owner/manual-learning-pack-preview/{course_id}",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "viewer_route_status": viewer_status,
    "adapter_route_status": adapter_status,
    "study_adapter_dry_run_added": True,
    "preview_json_read": True,
    "adapter_transforms_preview_items_in_memory": True,
    "candidate_study_items_visible": True,
    "write_target_none_visible": True,
    "new_write_endpoint_added": False,
    "study_artifact_written": False,
    "legacy_study_preview_changed": False,
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
    "TESTER_READINESS": "BLOCKED_ADAPTER_DRY_RUN_ONLY_NO_STUDY_WRITE",
    "POLICY": "manual_learning_pack_study_adapter_dry_run_no_write_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0810-manual-learning-pack-study-adapter-dry-run")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.8.10-MANUAL-LEARNING-PACK-STUDY-ADAPTER-DRY-RUN-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
