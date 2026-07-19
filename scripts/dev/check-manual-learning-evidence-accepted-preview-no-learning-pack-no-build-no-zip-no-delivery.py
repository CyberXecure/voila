from pathlib import Path
import json
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-learning-evidence-accepted-preview-no-learning-pack-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V085_WEB_APP_MISSING"),
    (doc, "FAILED_V085_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_5_MANUAL_LEARNING_EVIDENCE_ACCEPTED_PREVIEW_START",
    "VOILA_V0_8_5_MANUAL_LEARNING_EVIDENCE_ACCEPTED_PREVIEW_CSS_START",
    "_voila_v085_manual_learning_evidence_accepted_preview_html",
    "accepted_preview_html = _voila_v085_manual_learning_evidence_accepted_preview_html(items)",
    'data-testid="manual-evidence-accepted-preview"',
    'data-testid="manual-evidence-accepted-card"',
    "Accepted evidence preview",
    "Would be eligible for future Learning Pack",
    "v0.8.5 does not generate or modify Learning Pack artifacts",
    "accepted preview read-only",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V085_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "read-only accepted evidence preview",
    "status=accepted_owner_verified",
    "owner_verified=true",
    "verified_text",
    "explanation_ro",
    "eligible for a future Learning Pack",
    "Adds no new write endpoint.",
    "Does not generate or modify Learning Pack artifacts.",
    "No new write endpoint.",
    "No crop file write.",
    "No Learning Pack integration or generation.",
    "No build.",
    "No ZIP.",
    "No share.",
    "No delivery.",
    "No distribution.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit(f"FAILED_V085_DOC_TERM_MISSING={term}")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/save-draft"') != 1:
    raise SystemExit("FAILED_V085_SAVE_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/verify-draft"') != 1:
    raise SystemExit("FAILED_V085_VERIFY_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/reject-draft"') != 1:
    raise SystemExit("FAILED_V085_REJECT_ENDPOINT_COUNT")

for forbidden in [
    '@app.post("/owner/manual-learning-evidence/{course_id}/accepted-preview"',
    '@app.post("/owner/manual-learning-evidence/{course_id}/learning-pack"',
    "learning_pack_changed = True",
    '"learning_pack_changed": True',
]:
    if forbidden in web_text:
        raise SystemExit(f"FAILED_V085_FORBIDDEN_TERM_FOUND={forbidden}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-learning-evidence-accepted-preview-no-learning-pack-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-learning-evidence-accepted-preview-no-learning-pack-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-learning-evidence-accepted-preview-no-learning-pack-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V085_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

course_id = "03-pag-30-34-vectori-trigonometrie"
manual_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}?page=1"
save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"
verify_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/verify-draft"
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
        raise SystemExit(f"FAILED_V085_POST={url}; STATUS={exc.code}; BODY={error_body}")

accepted_id = "v085-check-accepted-preview"
rejected_id = "v085-check-rejected-hidden-from-preview"

for draft_id, title in [
    (accepted_id, "v0.8.5 accepted preview item"),
    (rejected_id, "v0.8.5 rejected non-preview item"),
]:
    status, body = post_form(
        save_url,
        {
            "draft_id": draft_id,
            "page": "1",
            "bbox": "[62, 84, 300, 230]",
            "kind": "formula",
            "title": title,
            "verified_text": "Accepted preview verified text",
            "explanation_ro": "Explicație verificată pentru preview accepted.",
            "source_status": "verified",
            "source_note": "Created by v0.8.5 accepted preview check.",
        },
    )
    if status != 200:
        raise SystemExit(f"FAILED_V085_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body = post_form(verify_url, {"draft_id": accepted_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V085_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

reject_status, reject_body = post_form(
    reject_url,
    {
        "draft_id": rejected_id,
        "rejection_reason": "owner_rejected_noise",
    },
)
if reject_status != 200:
    raise SystemExit(f"FAILED_V085_REJECT_FIXTURE_STATUS={reject_status}; BODY={reject_body}")

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
    raise SystemExit(f"FAILED_V085_MANUAL_ROUTE_STATUS={manual_status}; ERROR={last_error}")

runtime_terms = [
    "Manual Learning Evidence · skeleton",
    "Accepted evidence preview",
    "manual-evidence-accepted-preview",
    "manual-evidence-accepted-card",
    "accepted_owner_verified",
    "Would be eligible for future Learning Pack",
    "v0.8.5 does not generate or modify Learning Pack artifacts",
    "v085-check-accepted-preview",
    "v0.8.5 accepted preview item",
    "Accepted preview verified text",
    "Explicație verificată pentru preview accepted.",
]

for term in runtime_terms:
    if term not in manual_body:
        raise SystemExit(f"FAILED_V085_RUNTIME_TERM_MISSING={term}")

evidence_json = root / "data" / "output" / course_id / "manual_learning_evidence.json"
if not evidence_json.exists():
    raise SystemExit("FAILED_V085_MANUAL_EVIDENCE_JSON_MISSING")

data = json.loads(evidence_json.read_text(encoding="utf-8", errors="replace"))
items = data.get("items") if isinstance(data, dict) else None
if not isinstance(items, list):
    raise SystemExit("FAILED_V085_ITEMS_INVALID")

status_by_id = {
    item.get("id"): item.get("status")
    for item in items
    if isinstance(item, dict)
}

if status_by_id.get(accepted_id) != "accepted_owner_verified":
    raise SystemExit(f"FAILED_V085_ACCEPTED_STATUS={status_by_id.get(accepted_id)!r}")

if status_by_id.get(rejected_id) != "rejected_noise":
    raise SystemExit(f"FAILED_V085_REJECTED_STATUS={status_by_id.get(rejected_id)!r}")

preview_start = manual_body.find('data-testid="manual-evidence-accepted-preview"')
draft_list_start = manual_body.find('data-testid="manual-evidence-draft-list"')
if preview_start < 0 or draft_list_start < 0 or draft_list_start <= preview_start:
    raise SystemExit("FAILED_V085_PREVIEW_SECTION_ORDER")

accepted_preview_section = manual_body[preview_start:draft_list_start]
if accepted_id not in accepted_preview_section:
    raise SystemExit("FAILED_V085_ACCEPTED_ID_NOT_IN_ACCEPTED_PREVIEW")

if rejected_id in accepted_preview_section:
    raise SystemExit("FAILED_V085_REJECTED_ID_LEAKED_IN_ACCEPTED_PREVIEW")

summary = {
    "VOILA_V0_8_5_MANUAL_LEARNING_EVIDENCE_ACCEPTED_PREVIEW_CHECK": "PASS",
    "depends_on_v080_save_draft_json": True,
    "depends_on_v081_list_drafts": True,
    "depends_on_v082_verify_draft": True,
    "depends_on_v083_reject_draft": True,
    "depends_on_v084_review_summary": True,
    "manual_learning_evidence_route": "/owner/manual-learning-evidence/{course_id}?page=1",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "manual_route_status": manual_status,
    "accepted_preview_added": True,
    "accepted_preview_filters_only_owner_verified": True,
    "accepted_preview_runtime_rendered": True,
    "rejected_item_excluded_from_accepted_preview": True,
    "new_write_endpoint_added": False,
    "manual_learning_evidence_json_read": True,
    "manual_learning_evidence_json_written_by_existing_endpoints_for_fixture": True,
    "learning_pack_generated": False,
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
    "TESTER_READINESS": "BLOCKED_ACCEPTED_PREVIEW_ONLY_NO_LEARNING_PACK",
    "POLICY": "manual_learning_evidence_accepted_preview_no_learning_pack_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v085-manual-learning-evidence-accepted-preview")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.8.5-MANUAL-LEARNING-EVIDENCE-ACCEPTED-PREVIEW-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
