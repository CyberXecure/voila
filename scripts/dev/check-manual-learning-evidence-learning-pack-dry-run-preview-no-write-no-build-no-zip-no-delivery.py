from pathlib import Path
import json
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-learning-evidence-learning-pack-dry-run-preview-no-write-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V087_WEB_APP_MISSING"),
    (doc, "FAILED_V087_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_7_MANUAL_LEARNING_EVIDENCE_LEARNING_PACK_DRY_RUN_START",
    "VOILA_V0_8_7_MANUAL_LEARNING_EVIDENCE_LEARNING_PACK_DRY_RUN_CSS_START",
    "_voila_v087_manual_learning_evidence_learning_pack_dry_run_html",
    "learning_pack_dry_run_html = _voila_v087_manual_learning_evidence_learning_pack_dry_run_html(items)",
    'data-testid="manual-evidence-learning-pack-dry-run"',
    'data-testid="manual-evidence-learning-pack-dry-run-card"',
    "Learning Pack dry-run preview",
    "Would enter future Learning Pack",
    "Dry-run only · no Learning Pack artifact written",
    "v0.8.7 does not write or modify any Learning Pack artifact",
    "learning pack dry-run read-only",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V087_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "read-only Learning Pack dry-run preview",
    "status=accepted_owner_verified",
    "owner_verified=true",
    "all quality gate required fields present",
    "`title`",
    "`kind`",
    "`verified_text`",
    "`explanation_ro`",
    "`page`",
    "`bbox`",
    "Adds no new write endpoint.",
    "Does not generate or modify Learning Pack artifacts.",
    "No new write endpoint.",
    "No crop file write.",
    "No Learning Pack artifact write.",
    "No Learning Pack integration or generation.",
    "No build.",
    "No ZIP.",
    "No share.",
    "No delivery.",
    "No distribution.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit(f"FAILED_V087_DOC_TERM_MISSING={term}")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/save-draft"') != 1:
    raise SystemExit("FAILED_V087_SAVE_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/verify-draft"') != 1:
    raise SystemExit("FAILED_V087_VERIFY_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/reject-draft"') != 1:
    raise SystemExit("FAILED_V087_REJECT_ENDPOINT_COUNT")

for forbidden in [
    '@app.post("/owner/manual-learning-evidence/{course_id}/learning-pack"',
    '@app.post("/owner/manual-learning-evidence/{course_id}/learning-pack-dry-run"',
    "learning_pack_generated = True",
    "learning_pack_changed = True",
    '"learning_pack_changed": True',
    '"learning_pack_generated": True',
]:
    if forbidden in web_text:
        raise SystemExit(f"FAILED_V087_FORBIDDEN_TERM_FOUND={forbidden}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-learning-evidence-learning-pack-dry-run-preview-no-write-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-learning-evidence-learning-pack-dry-run-preview-no-write-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-learning-evidence-learning-pack-dry-run-preview-no-write-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V087_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

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
        raise SystemExit(f"FAILED_V087_POST={url}; STATUS={exc.code}; BODY={error_body}")

eligible_id = "v087-check-learning-pack-dry-run-eligible"
incomplete_id = "v087-check-learning-pack-dry-run-incomplete"
rejected_id = "v087-check-learning-pack-dry-run-rejected"

fixtures = [
    (
        eligible_id,
        {
            "draft_id": eligible_id,
            "page": "1",
            "bbox": "[82, 104, 340, 270]",
            "kind": "formula",
            "title": "v0.8.7 dry-run eligible",
            "verified_text": "Dry-run Learning Pack verified text",
            "explanation_ro": "Explicație completă pentru dry-run Learning Pack.",
            "source_status": "verified",
            "source_note": "Created by v0.8.7 dry-run check.",
        },
        "verify",
    ),
    (
        incomplete_id,
        {
            "draft_id": incomplete_id,
            "page": "1",
            "bbox": "[84, 106, 342, 272]",
            "kind": "formula",
            "title": "v0.8.7 dry-run incomplete",
            "verified_text": "Dry-run incomplete text",
            "explanation_ro": "",
            "source_status": "verified",
            "source_note": "Created by v0.8.7 dry-run check.",
        },
        "verify",
    ),
    (
        rejected_id,
        {
            "draft_id": rejected_id,
            "page": "1",
            "bbox": "[86, 108, 344, 274]",
            "kind": "formula",
            "title": "v0.8.7 dry-run rejected",
            "verified_text": "Dry-run rejected text",
            "explanation_ro": "Nu trebuie să intre în preview.",
            "source_status": "verified",
            "source_note": "Created by v0.8.7 dry-run check.",
        },
        "reject",
    ),
]

for draft_id, payload, action in fixtures:
    status, body = post_form(save_url, payload)
    if status != 200:
        raise SystemExit(f"FAILED_V087_SAVE_FIXTURE_STATUS={status}; BODY={body}")

    if action == "verify":
        action_status, action_body = post_form(verify_url, {"draft_id": draft_id})
        if action_status != 200:
            raise SystemExit(f"FAILED_V087_VERIFY_FIXTURE_STATUS={action_status}; BODY={action_body}")
    elif action == "reject":
        action_status, action_body = post_form(
            reject_url,
            {
                "draft_id": draft_id,
                "rejection_reason": "owner_rejected_noise",
            },
        )
        if action_status != 200:
            raise SystemExit(f"FAILED_V087_REJECT_FIXTURE_STATUS={action_status}; BODY={action_body}")

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
    raise SystemExit(f"FAILED_V087_MANUAL_ROUTE_STATUS={manual_status}; ERROR={last_error}")

runtime_terms = [
    "Manual Learning Evidence · skeleton",
    "Learning Pack dry-run preview",
    "manual-evidence-learning-pack-dry-run",
    "manual-evidence-learning-pack-dry-run-card",
    "accepted_owner_verified",
    "Would enter future Learning Pack",
    "v0.8.7 does not write or modify any Learning Pack artifact",
    "v087-check-learning-pack-dry-run-eligible",
    "v0.8.7 dry-run eligible",
    "Dry-run Learning Pack verified text",
    "Explicație completă pentru dry-run Learning Pack.",
]

for term in runtime_terms:
    if term not in manual_body:
        raise SystemExit(f"FAILED_V087_RUNTIME_TERM_MISSING={term}")

evidence_json = root / "data" / "output" / course_id / "manual_learning_evidence.json"
if not evidence_json.exists():
    raise SystemExit("FAILED_V087_MANUAL_EVIDENCE_JSON_MISSING")

data = json.loads(evidence_json.read_text(encoding="utf-8", errors="replace"))
items = data.get("items") if isinstance(data, dict) else None
if not isinstance(items, list):
    raise SystemExit("FAILED_V087_ITEMS_INVALID")

status_by_id = {
    item.get("id"): item.get("status")
    for item in items
    if isinstance(item, dict)
}

if status_by_id.get(eligible_id) != "accepted_owner_verified":
    raise SystemExit(f"FAILED_V087_ELIGIBLE_STATUS={status_by_id.get(eligible_id)!r}")

if status_by_id.get(incomplete_id) != "accepted_owner_verified":
    raise SystemExit(f"FAILED_V087_INCOMPLETE_STATUS={status_by_id.get(incomplete_id)!r}")

if status_by_id.get(rejected_id) != "rejected_noise":
    raise SystemExit(f"FAILED_V087_REJECTED_STATUS={status_by_id.get(rejected_id)!r}")

dry_run_start = manual_body.find('data-testid="manual-evidence-learning-pack-dry-run"')
draft_list_start = manual_body.find('data-testid="manual-evidence-draft-list"')
if dry_run_start < 0 or draft_list_start < 0 or draft_list_start <= dry_run_start:
    raise SystemExit("FAILED_V087_DRY_RUN_SECTION_ORDER")

dry_run_section = manual_body[dry_run_start:draft_list_start]
if eligible_id not in dry_run_section:
    raise SystemExit("FAILED_V087_ELIGIBLE_ID_NOT_IN_DRY_RUN")

if incomplete_id in dry_run_section:
    raise SystemExit("FAILED_V087_INCOMPLETE_ID_LEAKED_IN_DRY_RUN")

if rejected_id in dry_run_section:
    raise SystemExit("FAILED_V087_REJECTED_ID_LEAKED_IN_DRY_RUN")

summary = {
    "VOILA_V0_8_7_MANUAL_LEARNING_EVIDENCE_LEARNING_PACK_DRY_RUN_PREVIEW_CHECK": "PASS",
    "depends_on_v080_save_draft_json": True,
    "depends_on_v081_list_drafts": True,
    "depends_on_v082_verify_draft": True,
    "depends_on_v083_reject_draft": True,
    "depends_on_v084_review_summary": True,
    "depends_on_v085_accepted_preview": True,
    "depends_on_v086_quality_gate": True,
    "manual_learning_evidence_route": "/owner/manual-learning-evidence/{course_id}?page=1",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "manual_route_status": manual_status,
    "learning_pack_dry_run_preview_added": True,
    "dry_run_uses_only_quality_gate_eligible_accepted_items": True,
    "incomplete_item_excluded_from_dry_run": True,
    "rejected_item_excluded_from_dry_run": True,
    "new_write_endpoint_added": False,
    "manual_learning_evidence_json_read": True,
    "manual_learning_evidence_json_written_by_existing_endpoints_for_fixture": True,
    "learning_pack_generated": False,
    "learning_pack_artifact_written": False,
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
    "TESTER_READINESS": "BLOCKED_DRY_RUN_PREVIEW_ONLY_NO_LEARNING_PACK_WRITE",
    "POLICY": "manual_learning_evidence_learning_pack_dry_run_preview_no_write_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v087-manual-learning-evidence-learning-pack-dry-run-preview")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.8.7-MANUAL-LEARNING-EVIDENCE-LEARNING-PACK-DRY-RUN-PREVIEW-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
