from pathlib import Path
import json
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-learning-evidence-learning-pack-export-draft-json-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V088_WEB_APP_MISSING"),
    (doc, "FAILED_V088_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_8_MANUAL_LEARNING_PACK_EXPORT_DRAFT_START",
    "VOILA_V0_8_8_MANUAL_LEARNING_PACK_EXPORT_DRAFT_CSS_START",
    "VOILA_V0_8_8_MANUAL_LEARNING_PACK_EXPORT_DRAFT_ENDPOINT_START",
    "_voila_v088_manual_learning_pack_eligible_items",
    "_voila_v088_manual_learning_pack_payload",
    "_voila_v088_manual_learning_pack_export_form_html",
    'data-testid="manual-learning-pack-export-draft"',
    'data-testid="manual-learning-pack-export-draft-button"',
    "/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft",
    "manual_learning_pack.preview.json",
    "learning pack draft export",
    "voila.manual_learning_pack.preview.v1",
    "v0.8.8_manual_learning_evidence_export_draft_json",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V088_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "controlled owner-local export",
    "`manual_learning_pack.preview.json`",
    "status=accepted_owner_verified",
    "owner_verified=true",
    "all quality gate required fields present",
    "`title`",
    "`kind`",
    "`verified_text`",
    "`explanation_ro`",
    "`page`",
    "`bbox`",
    "Adds an export button",
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
        raise SystemExit(f"FAILED_V088_DOC_TERM_MISSING={term}")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/save-draft"') != 1:
    raise SystemExit("FAILED_V088_SAVE_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/verify-draft"') != 1:
    raise SystemExit("FAILED_V088_VERIFY_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/reject-draft"') != 1:
    raise SystemExit("FAILED_V088_REJECT_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"') != 1:
    raise SystemExit("FAILED_V088_EXPORT_ENDPOINT_COUNT")

for forbidden in [
    '@app.post("/owner/manual-learning-evidence/{course_id}/learning-pack"',
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
        raise SystemExit(f"FAILED_V088_FORBIDDEN_TERM_FOUND={forbidden}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-learning-evidence-learning-pack-export-draft-json-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-learning-evidence-learning-pack-export-draft-json-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-learning-evidence-learning-pack-export-draft-json-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V088_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

course_id = "03-pag-30-34-vectori-trigonometrie"
output_dir = root / "data" / "output" / course_id
preview_json = output_dir / "manual_learning_pack.preview.json"

before_preview = preview_json.read_text(encoding="utf-8", errors="replace") if preview_json.exists() else None

manual_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}?page=1"
save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"
verify_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/verify-draft"
reject_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/reject-draft"
export_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"

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
        raise SystemExit(f"FAILED_V088_POST={url}; STATUS={exc.code}; BODY={error_body}")

eligible_id = "v088-check-learning-pack-export-eligible"
incomplete_id = "v088-check-learning-pack-export-incomplete"
rejected_id = "v088-check-learning-pack-export-rejected"

fixtures = [
    (
        eligible_id,
        {
            "draft_id": eligible_id,
            "page": "1",
            "bbox": "[92, 114, 360, 290]",
            "kind": "formula",
            "title": "v0.8.8 export eligible",
            "verified_text": "Export draft verified text",
            "explanation_ro": "Explicație completă pentru export draft.",
            "source_status": "verified",
            "source_note": "Created by v0.8.8 export check.",
        },
        "verify",
    ),
    (
        incomplete_id,
        {
            "draft_id": incomplete_id,
            "page": "1",
            "bbox": "[94, 116, 362, 292]",
            "kind": "formula",
            "title": "v0.8.8 export incomplete",
            "verified_text": "Export incomplete text",
            "explanation_ro": "",
            "source_status": "verified",
            "source_note": "Created by v0.8.8 export check.",
        },
        "verify",
    ),
    (
        rejected_id,
        {
            "draft_id": rejected_id,
            "page": "1",
            "bbox": "[96, 118, 364, 294]",
            "kind": "formula",
            "title": "v0.8.8 export rejected",
            "verified_text": "Export rejected text",
            "explanation_ro": "Nu trebuie să intre în export.",
            "source_status": "verified",
            "source_note": "Created by v0.8.8 export check.",
        },
        "reject",
    ),
]

for draft_id, payload, action in fixtures:
    status, body, _ = post_form(save_url, payload)
    if status != 200:
        raise SystemExit(f"FAILED_V088_SAVE_FIXTURE_STATUS={status}; BODY={body}")

    if action == "verify":
        action_status, action_body, _ = post_form(verify_url, {"draft_id": draft_id})
        if action_status != 200:
            raise SystemExit(f"FAILED_V088_VERIFY_FIXTURE_STATUS={action_status}; BODY={action_body}")
    elif action == "reject":
        action_status, action_body, _ = post_form(
            reject_url,
            {
                "draft_id": draft_id,
                "rejection_reason": "owner_rejected_noise",
            },
        )
        if action_status != 200:
            raise SystemExit(f"FAILED_V088_REJECT_FIXTURE_STATUS={action_status}; BODY={action_body}")

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
    raise SystemExit(f"FAILED_V088_MANUAL_ROUTE_STATUS={manual_status}; ERROR={last_error}")

runtime_terms = [
    "Learning Pack dry-run preview",
    "manual-learning-pack-export-draft",
    "manual-learning-pack-export-draft-button",
    "manual_learning_pack.preview.json",
    "Exportă draft Learning Pack JSON",
    "v088-check-learning-pack-export-eligible",
    "v0.8.8 export eligible",
]

for term in runtime_terms:
    if term not in manual_body:
        raise SystemExit(f"FAILED_V088_RUNTIME_TERM_MISSING={term}")

export_status, export_body, final_url = post_form(export_url, {})
if export_status != 200:
    raise SystemExit(f"FAILED_V088_EXPORT_STATUS={export_status}; BODY={export_body}")

if "learning_pack_preview_exported=1" not in final_url:
    raise SystemExit(f"FAILED_V088_EXPORT_REDIRECT_URL={final_url}")

if not preview_json.exists():
    raise SystemExit("FAILED_V088_PREVIEW_JSON_MISSING")

after_preview = preview_json.read_text(encoding="utf-8", errors="replace")
if before_preview == after_preview:
    raise SystemExit("FAILED_V088_PREVIEW_JSON_NOT_UPDATED")

pack = json.loads(after_preview)

if pack.get("schema") != "voila.manual_learning_pack.preview.v1":
    raise SystemExit(f"FAILED_V088_SCHEMA={pack.get('schema')!r}")

if pack.get("course_id") != course_id:
    raise SystemExit(f"FAILED_V088_COURSE_ID={pack.get('course_id')!r}")

if pack.get("artifact") != "manual_learning_pack.preview.json":
    raise SystemExit(f"FAILED_V088_ARTIFACT={pack.get('artifact')!r}")

items = pack.get("items")
if not isinstance(items, list):
    raise SystemExit("FAILED_V088_ITEMS_INVALID")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}

if eligible_id not in ids:
    raise SystemExit("FAILED_V088_ELIGIBLE_ID_NOT_EXPORTED")

if incomplete_id in ids:
    raise SystemExit("FAILED_V088_INCOMPLETE_ID_EXPORTED")

if rejected_id in ids:
    raise SystemExit("FAILED_V088_REJECTED_ID_EXPORTED")

policy = pack.get("policy")
if not isinstance(policy, dict):
    raise SystemExit("FAILED_V088_POLICY_INVALID")

for key in [
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
]:
    if policy.get(key) is not False:
        raise SystemExit(f"FAILED_V088_POLICY_FLAG={key}:{policy.get(key)!r}")

summary = {
    "VOILA_V0_8_8_MANUAL_LEARNING_PACK_EXPORT_DRAFT_JSON_CHECK": "PASS",
    "depends_on_v080_save_draft_json": True,
    "depends_on_v081_list_drafts": True,
    "depends_on_v082_verify_draft": True,
    "depends_on_v083_reject_draft": True,
    "depends_on_v084_review_summary": True,
    "depends_on_v085_accepted_preview": True,
    "depends_on_v086_quality_gate": True,
    "depends_on_v087_dry_run_preview": True,
    "manual_learning_evidence_route": "/owner/manual-learning-evidence/{course_id}?page=1",
    "export_endpoint": "/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "manual_route_status": manual_status,
    "export_status": export_status,
    "export_button_added": True,
    "manual_learning_pack_preview_json_written": True,
    "preview_json_path": str(preview_json),
    "preview_schema_valid": True,
    "export_uses_only_quality_gate_eligible_accepted_items": True,
    "incomplete_item_excluded_from_export": True,
    "rejected_item_excluded_from_export": True,
    "manual_learning_evidence_json_read": True,
    "manual_learning_evidence_json_written_by_existing_endpoints_for_fixture": True,
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
    "TESTER_READINESS": "BLOCKED_PREVIEW_JSON_ONLY_NO_STUDY_COURSE_INTEGRATION",
    "POLICY": "manual_learning_pack_preview_json_export_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v088-manual-learning-pack-export-draft-json")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.8.8-MANUAL-LEARNING-PACK-EXPORT-DRAFT-JSON-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
