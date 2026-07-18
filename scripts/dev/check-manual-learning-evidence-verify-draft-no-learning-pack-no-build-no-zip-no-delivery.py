from pathlib import Path
import json
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-learning-evidence-verify-draft-no-learning-pack-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V082_WEB_APP_MISSING"),
    (doc, "FAILED_V082_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_2_MANUAL_LEARNING_EVIDENCE_VERIFY_DRAFT_ENDPOINT_START",
    "VOILA_V0_8_2_MANUAL_LEARNING_EVIDENCE_VERIFY_DRAFT_CARD_START",
    "VOILA_V0_8_2_MANUAL_LEARNING_EVIDENCE_VERIFY_DRAFT_CSS_START",
    '@app.post("/owner/manual-learning-evidence/{course_id}/verify-draft"',
    "owner_manual_learning_evidence_verify_draft",
    "Verify / Accept draft",
    "verify draft enabled",
    '"status": "accepted_owner_verified"',
    '"owner_verified": True',
    'target_item["save_state"] = "verified"',
    'target_item["verified_by"] = "owner"',
    '"crop_file_written": False',
    '"learning_pack_changed": False',
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V082_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "verify draft",
    "Verify / Accept draft",
    "accepted_owner_verified",
    "owner_verified=true",
    "save_state=verified",
    "verified_by=owner",
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
        raise SystemExit(f"FAILED_V082_DOC_TERM_MISSING={term}")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/save-draft"') != 1:
    raise SystemExit("FAILED_V082_SAVE_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/verify-draft"') != 1:
    raise SystemExit("FAILED_V082_VERIFY_ENDPOINT_COUNT")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-learning-evidence-verify-draft-no-learning-pack-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-learning-evidence-verify-draft-no-learning-pack-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-learning-evidence-verify-draft-no-learning-pack-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V082_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

course_id = "03-pag-30-34-vectori-trigonometrie"
manual_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}?page=1"
save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"
verify_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/verify-draft"

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
        raise SystemExit(f"FAILED_V082_POST={url}; STATUS={exc.code}; BODY={error_body}")

draft_id = "v082-check-verify-draft"

save_payload = {
    "draft_id": draft_id,
    "page": "1",
    "bbox": "[32, 54, 240, 180]",
    "kind": "formula",
    "title": "v0.8.2 verify draft",
    "verified_text": "Verify draft check",
    "explanation_ro": "Draft local pentru verificare owner.",
    "source_status": "uncertain",
    "source_note": "Created by v0.8.2 verify check via v0.8.0 endpoint.",
}

save_status, save_body = post_form(save_url, save_payload)
if save_status != 200:
    raise SystemExit(f"FAILED_V082_SAVE_FIXTURE_STATUS={save_status}; BODY={save_body}")

verify_status, verify_body = post_form(verify_url, {"draft_id": draft_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V082_VERIFY_STATUS={verify_status}; BODY={verify_body}")

try:
    verify_data = json.loads(verify_body)
except Exception as exc:
    raise SystemExit(f"FAILED_V082_VERIFY_JSON_PARSE={exc}; BODY={verify_body}")

if verify_data.get("ok") is not True:
    raise SystemExit("FAILED_V082_VERIFY_OK_FALSE=" + verify_body)

for key, expected in {
    "status": "accepted_owner_verified",
    "owner_verified": True,
    "manual_learning_evidence_written": True,
    "crop_file_written": False,
    "learning_pack_changed": False,
    "course_generation_changed": False,
    "study_changed": False,
    "progress_changed": False,
}.items():
    if verify_data.get(key) != expected:
        raise SystemExit(f"FAILED_V082_VERIFY_RESPONSE_{key.upper()}={verify_data.get(key)!r}")

evidence_json = root / "data" / "output" / course_id / "manual_learning_evidence.json"
if not evidence_json.exists():
    raise SystemExit("FAILED_V082_MANUAL_EVIDENCE_JSON_MISSING")

data = json.loads(evidence_json.read_text(encoding="utf-8", errors="replace"))
items = data.get("items") if isinstance(data, dict) else None
if not isinstance(items, list):
    raise SystemExit("FAILED_V082_ITEMS_INVALID")

matching = [item for item in items if isinstance(item, dict) and item.get("id") == draft_id]
if len(matching) != 1:
    raise SystemExit(f"FAILED_V082_CHECK_DRAFT_COUNT={len(matching)}")

item = matching[0]
for key, expected in {
    "status": "accepted_owner_verified",
    "owner_verified": True,
    "save_state": "verified",
    "verified_by": "owner",
    "crop_file_written": False,
    "learning_pack_changed": False,
    "course_generation_changed": False,
    "study_changed": False,
    "progress_changed": False,
}.items():
    if item.get(key) != expected:
        raise SystemExit(f"FAILED_V082_ITEM_{key.upper()}={item.get(key)!r}")

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
    raise SystemExit(f"FAILED_V082_MANUAL_ROUTE_STATUS={manual_status}; ERROR={last_error}")

runtime_terms = [
    "Manual Learning Evidence · skeleton",
    "Draft evidence list",
    "v082-check-verify-draft",
    "v0.8.2 verify draft",
    "accepted_owner_verified",
    "owner_verified: <code>true</code>",
    "save_state: <code>verified</code>",
]

for term in runtime_terms:
    if term not in manual_body:
        raise SystemExit(f"FAILED_V082_RUNTIME_TERM_MISSING={term}")

summary = {
    "VOILA_V0_8_2_MANUAL_LEARNING_EVIDENCE_VERIFY_DRAFT_CHECK": "PASS",
    "depends_on_v080_save_draft_json": True,
    "depends_on_v081_list_drafts": True,
    "manual_learning_evidence_route": "/owner/manual-learning-evidence/{course_id}?page=1",
    "verify_endpoint": "/owner/manual-learning-evidence/{course_id}/verify-draft",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "manual_route_status": manual_status,
    "save_fixture_status": save_status,
    "verify_post_status": verify_status,
    "verify_button_added": True,
    "draft_status_updated_to_accepted_owner_verified": True,
    "owner_verified_set_true": True,
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
    "TESTER_READINESS": "BLOCKED_VERIFIED_JSON_ONLY_NO_LEARNING_PACK",
    "POLICY": "manual_learning_evidence_verify_draft_no_learning_pack_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v082-manual-learning-evidence-verify-draft")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.8.2-MANUAL-LEARNING-EVIDENCE-VERIFY-DRAFT-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
