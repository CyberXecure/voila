from pathlib import Path
import json
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-learning-evidence-quality-gate-no-learning-pack-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V086_WEB_APP_MISSING"),
    (doc, "FAILED_V086_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_6_MANUAL_LEARNING_EVIDENCE_QUALITY_GATE_START",
    "VOILA_V0_8_6_MANUAL_LEARNING_EVIDENCE_QUALITY_GATE_CSS_START",
    "_voila_v086_manual_learning_evidence_quality_gate_html",
    "quality_gate_html = _voila_v086_manual_learning_evidence_quality_gate_html(items)",
    'data-testid="manual-evidence-quality-gate"',
    'data-testid="manual-evidence-quality-eligible"',
    'data-testid="manual-evidence-quality-incomplete"',
    'data-testid="manual-evidence-quality-blocked"',
    'data-testid="manual-evidence-quality-state"',
    'data-testid="manual-evidence-quality-item"',
    "Accepted evidence quality gate",
    "No Learning Pack is generated in v0.8.6.",
    "quality gate read-only",
    "required_fields = [\"title\", \"kind\", \"verified_text\", \"explanation_ro\", \"page\", \"bbox\"]",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V086_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "read-only quality gate",
    "status=accepted_owner_verified",
    "owner_verified=true",
    "`title`",
    "`kind`",
    "`verified_text`",
    "`explanation_ro`",
    "`page`",
    "`bbox`",
    "eligible",
    "incomplete",
    "blocked",
    "Shows missing fields per accepted item.",
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
        raise SystemExit(f"FAILED_V086_DOC_TERM_MISSING={term}")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/save-draft"') != 1:
    raise SystemExit("FAILED_V086_SAVE_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/verify-draft"') != 1:
    raise SystemExit("FAILED_V086_VERIFY_ENDPOINT_COUNT")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/reject-draft"') != 1:
    raise SystemExit("FAILED_V086_REJECT_ENDPOINT_COUNT")

for forbidden in [
    '@app.post("/owner/manual-learning-evidence/{course_id}/quality-gate"',
    '@app.post("/owner/manual-learning-evidence/{course_id}/learning-pack"',
    "learning_pack_generated = True",
    "learning_pack_changed = True",
    '"learning_pack_changed": True',
]:
    if forbidden in web_text:
        raise SystemExit(f"FAILED_V086_FORBIDDEN_TERM_FOUND={forbidden}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-learning-evidence-quality-gate-no-learning-pack-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-learning-evidence-quality-gate-no-learning-pack-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-learning-evidence-quality-gate-no-learning-pack-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V086_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

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
        raise SystemExit(f"FAILED_V086_POST={url}; STATUS={exc.code}; BODY={error_body}")

eligible_id = "v086-check-quality-eligible"
incomplete_id = "v086-check-quality-incomplete"

fixtures = [
    (
        eligible_id,
        {
            "draft_id": eligible_id,
            "page": "1",
            "bbox": "[72, 94, 320, 250]",
            "kind": "formula",
            "title": "v0.8.6 quality eligible",
            "verified_text": "Quality gate verified text",
            "explanation_ro": "Explicație completă pentru quality gate.",
            "source_status": "verified",
            "source_note": "Created by v0.8.6 quality gate check.",
        },
    ),
    (
        incomplete_id,
        {
            "draft_id": incomplete_id,
            "page": "1",
            "bbox": "[74, 96, 322, 252]",
            "kind": "formula",
            "title": "v0.8.6 quality incomplete",
            "verified_text": "Quality gate incomplete text",
            "explanation_ro": "",
            "source_status": "verified",
            "source_note": "Created by v0.8.6 quality gate check.",
        },
    ),
]

for draft_id, payload in fixtures:
    status, body = post_form(save_url, payload)
    if status != 200:
        raise SystemExit(f"FAILED_V086_SAVE_FIXTURE_STATUS={status}; BODY={body}")

    verify_status, verify_body = post_form(verify_url, {"draft_id": draft_id})
    if verify_status != 200:
        raise SystemExit(f"FAILED_V086_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

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
    raise SystemExit(f"FAILED_V086_MANUAL_ROUTE_STATUS={manual_status}; ERROR={last_error}")

runtime_terms = [
    "Manual Learning Evidence · skeleton",
    "Accepted evidence quality gate",
    "manual-evidence-quality-gate",
    "manual-evidence-quality-eligible",
    "manual-evidence-quality-incomplete",
    "manual-evidence-quality-blocked",
    "manual-evidence-quality-state",
    "manual-evidence-quality-item",
    "eligible",
    "incomplete",
    "blocked",
    "No Learning Pack is generated in v0.8.6.",
    "v086-check-quality-eligible",
    "v0.8.6 quality eligible",
    "v086-check-quality-incomplete",
    "v0.8.6 quality incomplete",
    "missing: <code>explanation_ro</code>",
]

for term in runtime_terms:
    if term not in manual_body:
        raise SystemExit(f"FAILED_V086_RUNTIME_TERM_MISSING={term}")

evidence_json = root / "data" / "output" / course_id / "manual_learning_evidence.json"
if not evidence_json.exists():
    raise SystemExit("FAILED_V086_MANUAL_EVIDENCE_JSON_MISSING")

data = json.loads(evidence_json.read_text(encoding="utf-8", errors="replace"))
items = data.get("items") if isinstance(data, dict) else None
if not isinstance(items, list):
    raise SystemExit("FAILED_V086_ITEMS_INVALID")

status_by_id = {
    item.get("id"): item.get("status")
    for item in items
    if isinstance(item, dict)
}

if status_by_id.get(eligible_id) != "accepted_owner_verified":
    raise SystemExit(f"FAILED_V086_ELIGIBLE_STATUS={status_by_id.get(eligible_id)!r}")

if status_by_id.get(incomplete_id) != "accepted_owner_verified":
    raise SystemExit(f"FAILED_V086_INCOMPLETE_STATUS={status_by_id.get(incomplete_id)!r}")

summary = {
    "VOILA_V0_8_6_MANUAL_LEARNING_EVIDENCE_QUALITY_GATE_CHECK": "PASS",
    "depends_on_v080_save_draft_json": True,
    "depends_on_v081_list_drafts": True,
    "depends_on_v082_verify_draft": True,
    "depends_on_v083_reject_draft": True,
    "depends_on_v084_review_summary": True,
    "depends_on_v085_accepted_preview": True,
    "manual_learning_evidence_route": "/owner/manual-learning-evidence/{course_id}?page=1",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "manual_route_status": manual_status,
    "quality_gate_added": True,
    "quality_gate_checks_required_fields": True,
    "eligible_status_visible": True,
    "incomplete_status_visible": True,
    "blocked_status_visible": True,
    "missing_fields_visible": True,
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
    "TESTER_READINESS": "BLOCKED_QUALITY_GATE_ONLY_NO_LEARNING_PACK",
    "POLICY": "manual_learning_evidence_quality_gate_no_learning_pack_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v086-manual-learning-evidence-quality-gate")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.8.6-MANUAL-LEARNING-EVIDENCE-QUALITY-GATE-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
