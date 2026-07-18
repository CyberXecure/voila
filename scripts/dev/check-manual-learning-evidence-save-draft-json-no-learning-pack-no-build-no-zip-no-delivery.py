from pathlib import Path
import json
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-learning-evidence-save-draft-json-no-learning-pack-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V080_WEB_APP_MISSING"),
    (doc, "FAILED_V080_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_0_MANUAL_LEARNING_EVIDENCE_SAVE_DRAFT_JSON_START",
    "VOILA_V0_8_0_MANUAL_LEARNING_EVIDENCE_SAVE_DRAFT_ENDPOINT_START",
    '@app.post("/owner/manual-learning-evidence/{course_id}/save-draft"',
    "owner_manual_learning_evidence_save_draft",
    "Save draft evidence",
    "v080SaveDraftButton",
    "v080SaveDraftBbox",
    'manual_learning_evidence.json',
    '"status": "pending_owner_review"',
    '"owner_verified": False',
    '"save_state": "draft"',
    '"crop_file_written": False',
    '"learning_pack_changed": False',
    "target.write_text(",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V080_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "first controlled write",
    "Save draft evidence",
    "manual_learning_evidence.json",
    "status=pending_owner_review",
    "owner_verified=false",
    "save_state=draft",
    "crop_file_written=false",
    "learning_pack_changed=false",
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
        raise SystemExit(f"FAILED_V080_DOC_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-learning-evidence-save-draft-json-no-learning-pack-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-learning-evidence-save-draft-json-no-learning-pack-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-learning-evidence-save-draft-json-no-learning-pack-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V080_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

course_id = "03-pag-30-34-vectori-trigonometrie"
manual_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}?page=1"
save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"

def fetch_get(url):
    last_error = ""
    for _ in range(10):
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                return response.status, response.read().decode("utf-8", errors="replace")
        except Exception as exc:
            last_error = str(exc)
            time.sleep(2)
    raise SystemExit(f"FAILED_V080_GET={url}; ERROR={last_error}")

manual_status, manual_body = fetch_get(manual_url)
if manual_status != 200:
    raise SystemExit(f"FAILED_V080_MANUAL_ROUTE_STATUS={manual_status}")

runtime_terms = [
    "Manual Learning Evidence · skeleton",
    "Save draft evidence",
    "v080SaveDraftButton",
    "v080SaveDraftBbox",
    "/owner/manual-learning-evidence/03-pag-30-34-vectori-trigonometrie/save-draft",
    "Writes only",
    "manual_learning_evidence.json",
    "No crop file",
    "No Learning Pack",
]

for term in runtime_terms:
    if term not in manual_body:
        raise SystemExit(f"FAILED_V080_RUNTIME_TERM_MISSING={term}")

payload = {
    "draft_id": "v080-check-draft",
    "page": "1",
    "bbox": "[12, 34, 180, 140]",
    "kind": "formula",
    "title": "v0.8.0 check draft",
    "verified_text": "AB = vector verificat local",
    "explanation_ro": "Draft local pentru verificarea scrierii controlate.",
    "source_status": "uncertain",
    "source_note": "Created by v0.8.0 owner-local check.",
}

encoded = urllib.parse.urlencode(payload).encode("utf-8")
request = urllib.request.Request(
    save_url,
    data=encoded,
    method="POST",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)

try:
    with urllib.request.urlopen(request, timeout=15) as response:
        post_status = response.status
        post_body = response.read().decode("utf-8", errors="replace")
except urllib.error.HTTPError as exc:
    error_body = exc.read().decode("utf-8", errors="replace")
    raise SystemExit(f"FAILED_V080_POST_STATUS={exc.code}; BODY={error_body}")

if post_status != 200:
    raise SystemExit(f"FAILED_V080_POST_STATUS={post_status}; BODY={post_body}")

try:
    post_data = json.loads(post_body)
except Exception as exc:
    raise SystemExit(f"FAILED_V080_POST_JSON_PARSE={exc}; BODY={post_body}")

if post_data.get("ok") is not True:
    raise SystemExit("FAILED_V080_POST_OK_FALSE=" + post_body)

if post_data.get("manual_learning_evidence_written") is not True:
    raise SystemExit("FAILED_V080_POST_DID_NOT_WRITE_JSON")

if post_data.get("crop_file_written") is not False:
    raise SystemExit("FAILED_V080_POST_CROP_FILE_WRITTEN")

if post_data.get("learning_pack_changed") is not False:
    raise SystemExit("FAILED_V080_POST_LEARNING_PACK_CHANGED")

evidence_json = root / "data" / "output" / course_id / "manual_learning_evidence.json"
if not evidence_json.exists():
    raise SystemExit("FAILED_V080_MANUAL_LEARNING_EVIDENCE_JSON_MISSING")

data = json.loads(evidence_json.read_text(encoding="utf-8", errors="replace"))
items = data.get("items") if isinstance(data, dict) else None
if not isinstance(items, list):
    raise SystemExit("FAILED_V080_MANUAL_LEARNING_EVIDENCE_ITEMS_INVALID")

matching = [item for item in items if isinstance(item, dict) and item.get("id") == "v080-check-draft"]
if len(matching) != 1:
    raise SystemExit(f"FAILED_V080_CHECK_DRAFT_COUNT={len(matching)}")

item = matching[0]
expected_item = {
    "status": "pending_owner_review",
    "owner_verified": False,
    "save_state": "draft",
    "bbox": [12, 34, 180, 140],
    "crop_file_written": False,
    "learning_pack_changed": False,
    "course_generation_changed": False,
    "study_changed": False,
    "progress_changed": False,
}

for key, expected in expected_item.items():
    if item.get(key) != expected:
        raise SystemExit(f"FAILED_V080_ITEM_{key.upper()}={item.get(key)!r}")

summary = {
    "VOILA_V0_8_0_MANUAL_LEARNING_EVIDENCE_SAVE_DRAFT_JSON_CHECK": "PASS",
    "depends_on_v0794_direction_charter": True,
    "depends_on_v0795_ui_design": True,
    "depends_on_v0796_ui_skeleton": True,
    "depends_on_v0797_visual_polish_course_tools_link": True,
    "depends_on_v0798_crop_selection_preview": True,
    "depends_on_v0799_metadata_preview_binding": True,
    "manual_learning_evidence_route": "/owner/manual-learning-evidence/{course_id}?page=1",
    "save_endpoint": "/owner/manual-learning-evidence/{course_id}/save-draft",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "manual_route_status": manual_status,
    "save_post_status": post_status,
    "save_draft_button_added": True,
    "manual_learning_evidence_json_written": True,
    "manual_learning_evidence_json_path": str(evidence_json),
    "saved_draft_id": "v080-check-draft",
    "saved_status": "pending_owner_review",
    "owner_verified": False,
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
    "TESTER_READINESS": "BLOCKED_DRAFT_JSON_ONLY_NO_LEARNING_PACK",
    "POLICY": "manual_learning_evidence_save_draft_json_no_learning_pack_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v080-manual-learning-evidence-save-draft-json")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.8.0-MANUAL-LEARNING-EVIDENCE-SAVE-DRAFT-JSON-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
