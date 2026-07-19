from pathlib import Path
import json
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-learning-evidence-reject-draft-no-learning-pack-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V083_WEB_APP_MISSING"),
    (doc, "FAILED_V083_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_3_MANUAL_LEARNING_EVIDENCE_REJECT_DRAFT_ENDPOINT_START",
    "VOILA_V0_8_3_MANUAL_LEARNING_EVIDENCE_REJECT_DRAFT_CARD_START",
    "VOILA_V0_8_3_MANUAL_LEARNING_EVIDENCE_REJECT_DRAFT_CSS_START",
    '@app.post("/owner/manual-learning-evidence/{course_id}/reject-draft"',
    "owner_manual_learning_evidence_reject_draft",
    "Reject / Noise draft",
    "reject draft enabled",
    "rejected_noise",
    'target_item["status"] = "rejected_noise"',
    'target_item["owner_verified"] = False',
    'target_item["save_state"] = "rejected"',
    'target_item["rejected_by"] = "owner"',
    'target_item["crop_file_written"] = False',
    'target_item["learning_pack_changed"] = False',
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V083_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "reject draft",
    "Reject / Noise draft",
    "status=rejected_noise",
    "owner_verified=false",
    "save_state=rejected",
    "rejected_by=owner",
    "Writes only `manual_learning_evidence.json`",
    "No crop file write.",
    "No Learning Pack integration.",
    "No build.",
    "No ZIP.",
    "No share.",
    "No delivery.",
    "No distribution.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit(f"FAILED_V083_DOC_TERM_MISSING={term}")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/save-draft"') != 1:
    raise SystemExit("FAILED_V083_SAVE_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/verify-draft"') != 1:
    raise SystemExit("FAILED_V083_VERIFY_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/reject-draft"') != 1:
    raise SystemExit("FAILED_V083_REJECT_ENDPOINT_COUNT")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-learning-evidence-reject-draft-no-learning-pack-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-learning-evidence-reject-draft-no-learning-pack-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-learning-evidence-reject-draft-no-learning-pack-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V083_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

course_id = "03-pag-30-34-vectori-trigonometrie"
manual_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}?page=1"
save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"
reject_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/reject-draft"

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
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"FAILED_V083_POST={url}; STATUS={exc.code}; BODY={error_body}")

draft_id = "v083-check-reject-draft"

save_payload = {
    "draft_id": draft_id,
    "page": "1",
    "bbox": "[42, 64, 260, 190]",
    "kind": "formula",
    "title": "v0.8.3 reject draft",
    "verified_text": "Reject draft check",
    "explanation_ro": "Draft local pentru verificare reject/noise.",
    "source_status": "uncertain",
    "source_note": "Created by v0.8.3 reject check via v0.8.0 endpoint.",
}

save_status, save_body = post_form(save_url, save_payload)
if save_status != 200:
    raise SystemExit(f"FAILED_V083_SAVE_FIXTURE_STATUS={save_status}; BODY={save_body}")

reject_status, reject_body = post_form(
    reject_url,
    {
        "draft_id": draft_id,
        "rejection_reason": "owner_rejected_noise",
    },
)

if reject_status != 200:
    raise SystemExit(f"FAILED_V083_REJECT_STATUS={reject_status}; BODY={reject_body}")

try:
    reject_data = json.loads(reject_body)
except Exception as exc:
    raise SystemExit(f"FAILED_V083_REJECT_JSON_PARSE={exc}; BODY={reject_body}")

if reject_data.get("ok") is not True:
    raise SystemExit("FAILED_V083_REJECT_OK_FALSE=" + reject_body)

for key, expected in {
    "status": "rejected_noise",
    "owner_verified": False,
    "save_state": "rejected",
    "manual_learning_evidence_written": True,
    "crop_file_written": False,
    "learning_pack_changed": False,
    "course_generation_changed": False,
    "study_changed": False,
    "progress_changed": False,
}.items():
    if reject_data.get(key) != expected:
        raise SystemExit(f"FAILED_V083_REJECT_RESPONSE_{key.upper()}={reject_data.get(key)!r}")

evidence_json = root / "data" / "output" / course_id / "manual_learning_evidence.json"
if not evidence_json.exists():
    raise SystemExit("FAILED_V083_MANUAL_EVIDENCE_JSON_MISSING")

data = json.loads(evidence_json.read_text(encoding="utf-8", errors="replace"))
items = data.get("items") if isinstance(data, dict) else None
if not isinstance(items, list):
    raise SystemExit("FAILED_V083_ITEMS_INVALID")

matching = [item for item in items if isinstance(item, dict) and item.get("id") == draft_id]
if len(matching) != 1:
    raise SystemExit(f"FAILED_V083_CHECK_DRAFT_COUNT={len(matching)}")

item = matching[0]
for key, expected in {
    "status": "rejected_noise",
    "owner_verified": False,
    "save_state": "rejected",
    "rejected_by": "owner",
    "rejection_reason": "owner_rejected_noise",
    "crop_file_written": False,
    "learning_pack_changed": False,
    "course_generation_changed": False,
    "study_changed": False,
    "progress_changed": False,
}.items():
    if item.get(key) != expected:
        raise SystemExit(f"FAILED_V083_ITEM_{key.upper()}={item.get(key)!r}")

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
    raise SystemExit(f"FAILED_V083_MANUAL_ROUTE_STATUS={manual_status}; ERROR={last_error}")

runtime_terms = [
    "Manual Learning Evidence · skeleton",
    "Draft evidence list",
    "v083-check-reject-draft",
    "v0.8.3 reject draft",
    "rejected_noise",
    "owner_verified: <code>false</code>",
    "save_state: <code>rejected</code>",
]

for term in runtime_terms:
    if term not in manual_body:
        raise SystemExit(f"FAILED_V083_RUNTIME_TERM_MISSING={term}")

summary = {
    "VOILA_V0_8_3_MANUAL_LEARNING_EVIDENCE_REJECT_DRAFT_CHECK": "PASS",
    "depends_on_v080_save_draft_json": True,
    "depends_on_v081_list_drafts": True,
    "depends_on_v082_verify_draft": True,
    "manual_learning_evidence_route": "/owner/manual-learning-evidence/{course_id}?page=1",
    "reject_endpoint": "/owner/manual-learning-evidence/{course_id}/reject-draft",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "manual_route_status": manual_status,
    "save_fixture_status": save_status,
    "reject_post_status": reject_status,
    "reject_button_added": True,
    "draft_status_updated_to_rejected_noise": True,
    "owner_verified_set_false": True,
    "manual_learning_evidence_json_written": True,
    "manual_learning_evidence_json_path": str(evidence_json),
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
    "TESTER_READINESS": "BLOCKED_REJECTED_JSON_ONLY_NO_LEARNING_PACK",
    "POLICY": "manual_learning_evidence_reject_draft_no_learning_pack_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v083-manual-learning-evidence-reject-draft")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.8.3-MANUAL-LEARNING-EVIDENCE-REJECT-DRAFT-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
