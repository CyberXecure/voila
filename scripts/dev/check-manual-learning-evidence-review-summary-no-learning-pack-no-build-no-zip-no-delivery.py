from pathlib import Path
import json
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-learning-evidence-review-summary-no-learning-pack-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V084_WEB_APP_MISSING"),
    (doc, "FAILED_V084_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_4_MANUAL_LEARNING_EVIDENCE_REVIEW_SUMMARY_START",
    "VOILA_V0_8_4_MANUAL_LEARNING_EVIDENCE_REVIEW_SUMMARY_CSS_START",
    "VOILA_V0_8_4_MANUAL_LEARNING_EVIDENCE_REVIEW_SUMMARY_COUNTS_START",
    "_voila_v084_manual_learning_evidence_review_summary_html",
    'data-testid="manual-evidence-review-summary"',
    'data-testid="manual-evidence-count-pending"',
    'data-testid="manual-evidence-count-accepted"',
    'data-testid="manual-evidence-count-rejected"',
    'data-testid="manual-evidence-status-filters"',
    "manual-evidence-status-pending_owner_review",
    "manual-evidence-status-accepted_owner_verified",
    "manual-evidence-status-rejected_noise",
    'data-status="{status_anchor}"',
    "review summary read-only",
    "No new write endpoint in v0.8.4. No Learning Pack.",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V084_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "read-only review summary",
    "pending_owner_review",
    "accepted_owner_verified",
    "rejected_noise",
    "simple status filter links",
    "status anchors/sections",
    "Adds no new write endpoint.",
    "No new write endpoint.",
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
        raise SystemExit(f"FAILED_V084_DOC_TERM_MISSING={term}")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/save-draft"') != 1:
    raise SystemExit("FAILED_V084_SAVE_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/verify-draft"') != 1:
    raise SystemExit("FAILED_V084_VERIFY_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/reject-draft"') != 1:
    raise SystemExit("FAILED_V084_REJECT_ENDPOINT_COUNT")

for forbidden in [
    '@app.post("/owner/manual-learning-evidence/{course_id}/summary"',
    '@app.post("/owner/manual-learning-evidence/{course_id}/review-summary"',
    "learning_pack_changed = True",
    '"learning_pack_changed": True',
]:
    if forbidden in web_text:
        raise SystemExit(f"FAILED_V084_FORBIDDEN_TERM_FOUND={forbidden}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-learning-evidence-review-summary-no-learning-pack-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-learning-evidence-review-summary-no-learning-pack-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-learning-evidence-review-summary-no-learning-pack-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V084_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

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
        raise SystemExit(f"FAILED_V084_POST={url}; STATUS={exc.code}; BODY={error_body}")

pending_id = "v084-check-pending-draft"
accepted_id = "v084-check-accepted-draft"
rejected_id = "v084-check-rejected-draft"

for draft_id, title in [
    (pending_id, "v0.8.4 pending summary draft"),
    (accepted_id, "v0.8.4 accepted summary draft"),
    (rejected_id, "v0.8.4 rejected summary draft"),
]:
    status, body = post_form(
        save_url,
        {
            "draft_id": draft_id,
            "page": "1",
            "bbox": "[52, 74, 280, 210]",
            "kind": "formula",
            "title": title,
            "verified_text": "Review summary check",
            "explanation_ro": "Draft local pentru sumar review.",
            "source_status": "uncertain",
            "source_note": "Created by v0.8.4 review summary check.",
        },
    )
    if status != 200:
        raise SystemExit(f"FAILED_V084_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body = post_form(verify_url, {"draft_id": accepted_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V084_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

reject_status, reject_body = post_form(
    reject_url,
    {
        "draft_id": rejected_id,
        "rejection_reason": "owner_rejected_noise",
    },
)
if reject_status != 200:
    raise SystemExit(f"FAILED_V084_REJECT_FIXTURE_STATUS={reject_status}; BODY={reject_body}")

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
    raise SystemExit(f"FAILED_V084_MANUAL_ROUTE_STATUS={manual_status}; ERROR={last_error}")

runtime_terms = [
    "Manual Learning Evidence · skeleton",
    "Review summary",
    "manual-evidence-review-summary",
    "manual-evidence-count-pending",
    "manual-evidence-count-accepted",
    "manual-evidence-count-rejected",
    "manual-evidence-status-filters",
    "manual-evidence-status-pending_owner_review",
    "manual-evidence-status-accepted_owner_verified",
    "manual-evidence-status-rejected_noise",
    "pending_owner_review",
    "accepted_owner_verified",
    "rejected_noise",
    "No new write endpoint in v0.8.4. No Learning Pack.",
    "v084-check-pending-draft",
    "v084-check-accepted-draft",
    "v084-check-rejected-draft",
]

for term in runtime_terms:
    if term not in manual_body:
        raise SystemExit(f"FAILED_V084_RUNTIME_TERM_MISSING={term}")

evidence_json = root / "data" / "output" / course_id / "manual_learning_evidence.json"
if not evidence_json.exists():
    raise SystemExit("FAILED_V084_MANUAL_EVIDENCE_JSON_MISSING")

data = json.loads(evidence_json.read_text(encoding="utf-8", errors="replace"))
items = data.get("items") if isinstance(data, dict) else None
if not isinstance(items, list):
    raise SystemExit("FAILED_V084_ITEMS_INVALID")

status_by_id = {
    item.get("id"): item.get("status")
    for item in items
    if isinstance(item, dict)
}

if status_by_id.get(pending_id) != "pending_owner_review":
    raise SystemExit(f"FAILED_V084_PENDING_STATUS={status_by_id.get(pending_id)!r}")

if status_by_id.get(accepted_id) != "accepted_owner_verified":
    raise SystemExit(f"FAILED_V084_ACCEPTED_STATUS={status_by_id.get(accepted_id)!r}")

if status_by_id.get(rejected_id) != "rejected_noise":
    raise SystemExit(f"FAILED_V084_REJECTED_STATUS={status_by_id.get(rejected_id)!r}")

summary = {
    "VOILA_V0_8_4_MANUAL_LEARNING_EVIDENCE_REVIEW_SUMMARY_CHECK": "PASS",
    "depends_on_v080_save_draft_json": True,
    "depends_on_v081_list_drafts": True,
    "depends_on_v082_verify_draft": True,
    "depends_on_v083_reject_draft": True,
    "manual_learning_evidence_route": "/owner/manual-learning-evidence/{course_id}?page=1",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "manual_route_status": manual_status,
    "review_summary_added": True,
    "status_counts_visible": True,
    "status_filter_links_added": True,
    "status_sections_added": True,
    "new_write_endpoint_added": False,
    "manual_learning_evidence_json_read": True,
    "manual_learning_evidence_json_written_by_existing_endpoints_for_fixture": True,
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
    "TESTER_READINESS": "BLOCKED_REVIEW_SUMMARY_ONLY_NO_LEARNING_PACK",
    "POLICY": "manual_learning_evidence_review_summary_no_learning_pack_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v084-manual-learning-evidence-review-summary")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.8.4-MANUAL-LEARNING-EVIDENCE-REVIEW-SUMMARY-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
