from pathlib import Path
import json
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-study-items-preview-export-json-no-study-integration-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0811_WEB_APP_MISSING"),
    (doc, "FAILED_V0811_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_11_MANUAL_STUDY_ITEMS_PREVIEW_EXPORT_START",
    "VOILA_V0_8_11_MANUAL_STUDY_ITEMS_PREVIEW_EXPORT_CSS_START",
    "VOILA_V0_8_11_MANUAL_STUDY_ITEMS_PREVIEW_EXPORT_ENDPOINT_START",
    "_voila_v0811_manual_study_items_preview_payload",
    "_voila_v0811_manual_study_items_export_form_html",
    '@app.post("/owner/manual-learning-pack-study-adapter-dry-run/{course_id}/export-manual-study-items-preview")',
    'data-testid="manual-study-items-preview-export"',
    'data-testid="manual-study-items-preview-export-button"',
    "manual_study_items.preview.json",
    "voila.manual_study_items.preview.v1",
    "manual study preview export",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0811_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "controlled owner-local export",
    "`manual_study_items.preview.json`",
    "`manual_learning_pack.preview.json`",
    "Study Adapter dry-run transformation",
    "source_evidence_id",
    "manual_study_item_id",
    "study_item_type",
    "write_target",
    "It does not write or modify the legacy `study_items.preview.json`.",
    "It does not connect the real Study page.",
    "No legacy Study artifact write.",
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
        raise SystemExit(f"FAILED_V0811_DOC_TERM_MISSING={term}")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/save-draft"') != 1:
    raise SystemExit("FAILED_V0811_SAVE_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/verify-draft"') != 1:
    raise SystemExit("FAILED_V0811_VERIFY_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/reject-draft"') != 1:
    raise SystemExit("FAILED_V0811_REJECT_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"') != 1:
    raise SystemExit("FAILED_V0811_LEARNING_PACK_EXPORT_ENDPOINT_COUNT")

if web_text.count('@app.get("/owner/manual-learning-pack-study-adapter-dry-run/{course_id}"') != 1:
    raise SystemExit("FAILED_V0811_ADAPTER_ROUTE_COUNT")

if web_text.count('@app.post("/owner/manual-learning-pack-study-adapter-dry-run/{course_id}/export-manual-study-items-preview"') != 1:
    raise SystemExit("FAILED_V0811_MANUAL_STUDY_EXPORT_ENDPOINT_COUNT")

for forbidden in [
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
        raise SystemExit(f"FAILED_V0811_FORBIDDEN_TERM_FOUND={forbidden}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-study-items-preview-export-json-no-study-integration-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-study-items-preview-export-json-no-study-integration-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-study-items-preview-export-json-no-study-integration-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0811_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

course_id = "03-pag-30-34-vectori-trigonometrie"
output_dir = root / "data" / "output" / course_id
manual_study_preview = output_dir / "manual_study_items.preview.json"
legacy_study_preview = output_dir / "study_items.preview.json"
legacy_before = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None

save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"
verify_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/verify-draft"
learning_pack_export_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"
adapter_url = f"http://127.0.0.1:8787/owner/manual-learning-pack-study-adapter-dry-run/{course_id}"
manual_study_export_url = f"http://127.0.0.1:8787/owner/manual-learning-pack-study-adapter-dry-run/{course_id}/export-manual-study-items-preview"

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
        raise SystemExit(f"FAILED_V0811_POST={url}; STATUS={exc.code}; BODY={error_body}")

eligible_id = "v0811-check-manual-study-export-eligible"

payload = {
    "draft_id": eligible_id,
    "page": "1",
    "bbox": "[122, 144, 420, 350]",
    "kind": "formula",
    "title": "v0.8.11 manual study export eligible",
    "verified_text": "Manual study export prompt text",
    "explanation_ro": "Răspuns exportat pentru manual Study preview.",
    "source_status": "verified",
    "source_note": "Created by v0.8.11 manual study export check.",
}

status, body, _ = post_form(save_url, payload)
if status != 200:
    raise SystemExit(f"FAILED_V0811_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body, _ = post_form(verify_url, {"draft_id": eligible_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V0811_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

learning_export_status, learning_export_body, _ = post_form(learning_pack_export_url, {})
if learning_export_status != 200:
    raise SystemExit(f"FAILED_V0811_LEARNING_PACK_EXPORT_STATUS={learning_export_status}; BODY={learning_export_body}")

def fetch_url(url, label):
    last_error = ""
    for _ in range(10):
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                return response.status, response.read().decode("utf-8", errors="replace")
        except Exception as exc:
            last_error = str(exc)
            time.sleep(2)
    raise SystemExit(f"FAILED_V0811_{label}_FETCH={last_error}")

adapter_status, adapter_body = fetch_url(adapter_url, "ADAPTER")
if adapter_status != 200:
    raise SystemExit(f"FAILED_V0811_ADAPTER_STATUS={adapter_status}")

adapter_terms = [
    "Manual Learning Pack → Study Adapter Dry-run",
    "manual-study-items-preview-export",
    "manual-study-items-preview-export-button",
    "manual_study_items.preview.json",
    "v0811-check-manual-study-export-eligible",
    "Manual study export prompt text",
]

for term in adapter_terms:
    if term not in adapter_body:
        raise SystemExit(f"FAILED_V0811_ADAPTER_TERM_MISSING={term}")

export_status, export_body, final_url = post_form(manual_study_export_url, {})
if export_status != 200:
    raise SystemExit(f"FAILED_V0811_EXPORT_STATUS={export_status}; BODY={export_body}")

if "manual_study_items_preview_exported=1" not in final_url:
    raise SystemExit(f"FAILED_V0811_EXPORT_REDIRECT={final_url}")

if not manual_study_preview.exists():
    raise SystemExit("FAILED_V0811_MANUAL_STUDY_PREVIEW_MISSING")

manual_study = json.loads(manual_study_preview.read_text(encoding="utf-8", errors="replace"))

if manual_study.get("schema") != "voila.manual_study_items.preview.v1":
    raise SystemExit(f"FAILED_V0811_SCHEMA={manual_study.get('schema')!r}")

if manual_study.get("artifact") != "manual_study_items.preview.json":
    raise SystemExit(f"FAILED_V0811_ARTIFACT={manual_study.get('artifact')!r}")

items = manual_study.get("items")
if not isinstance(items, list):
    raise SystemExit("FAILED_V0811_ITEMS_INVALID")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}
if eligible_id not in ids:
    raise SystemExit("FAILED_V0811_ELIGIBLE_ID_NOT_EXPORTED")

sample = None
for item in items:
    if isinstance(item, dict) and item.get("source_evidence_id") == eligible_id:
        sample = item
        break

if not isinstance(sample, dict):
    raise SystemExit("FAILED_V0811_SAMPLE_MISSING")

for key in ["manual_study_item_id", "study_item_type", "title", "prompt", "answer", "source_page", "source_bbox", "source_kind", "source_status", "write_target"]:
    if key not in sample:
        raise SystemExit(f"FAILED_V0811_SAMPLE_KEY_MISSING={key}")

if sample.get("write_target") != "manual_study_items.preview.json":
    raise SystemExit(f"FAILED_V0811_WRITE_TARGET={sample.get('write_target')!r}")

policy = manual_study.get("policy")
if not isinstance(policy, dict):
    raise SystemExit("FAILED_V0811_POLICY_INVALID")

for key, expected in [
    ("manual_study_preview_only", True),
    ("legacy_study_items_preview_untouched", True),
    ("study_integration", False),
    ("course_generation_changed", False),
    ("study_changed", False),
    ("progress_changed", False),
    ("ocr_rewrite_performed", False),
    ("formula_ocr_performed", False),
    ("build_performed", False),
    ("zip_created", False),
    ("share_created", False),
    ("delivery_performed", False),
    ("distribution_performed", False),
]:
    if policy.get(key) is not expected:
        raise SystemExit(f"FAILED_V0811_POLICY_FLAG={key}:{policy.get(key)!r}")

legacy_after = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None
if legacy_before != legacy_after:
    raise SystemExit("FAILED_V0811_LEGACY_STUDY_PREVIEW_CHANGED")

summary = {
    "VOILA_V0_8_11_MANUAL_STUDY_ITEMS_PREVIEW_EXPORT_JSON_CHECK": "PASS",
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
    "adapter_route": "/owner/manual-learning-pack-study-adapter-dry-run/{course_id}",
    "export_endpoint": "/owner/manual-learning-pack-study-adapter-dry-run/{course_id}/export-manual-study-items-preview",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "adapter_route_status": adapter_status,
    "export_status": export_status,
    "manual_study_export_button_added": True,
    "manual_study_items_preview_json_written": True,
    "manual_study_preview_schema_valid": True,
    "manual_study_preview_uses_adapter_dry_run": True,
    "manual_study_preview_path": str(manual_study_preview),
    "legacy_study_items_preview_unchanged": True,
    "new_study_integration_added": False,
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
    "TESTER_READINESS": "BLOCKED_MANUAL_STUDY_PREVIEW_JSON_ONLY_NO_STUDY_INTEGRATION",
    "POLICY": "manual_study_items_preview_json_export_no_study_integration_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0811-manual-study-items-preview-export-json")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.8.11-MANUAL-STUDY-ITEMS-PREVIEW-EXPORT-JSON-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
