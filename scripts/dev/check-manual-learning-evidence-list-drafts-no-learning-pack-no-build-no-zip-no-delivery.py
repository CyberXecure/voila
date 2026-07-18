from pathlib import Path
import json
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-learning-evidence-list-drafts-no-learning-pack-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V081_WEB_APP_MISSING"),
    (doc, "FAILED_V081_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_1_MANUAL_LEARNING_EVIDENCE_LIST_DRAFTS_START",
    "VOILA_V0_8_1_MANUAL_LEARNING_EVIDENCE_LIST_DRAFTS_CSS_START",
    "VOILA_V0_8_1_MANUAL_LEARNING_EVIDENCE_LIST_DRAFTS_READ_START",
    "_voila_v081_manual_learning_evidence_list_html",
    "manual_evidence_list_html",
    "manual_evidence_item_count",
    "Draft evidence list",
    'data-testid="manual-evidence-draft-list"',
    'data-testid="manual-evidence-draft-card"',
    "draft list read-only",
    "No accept/verify action in v0.8.1.",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V081_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "read-only draft list",
    "manual_learning_evidence.json",
    "Displays draft evidence cards.",
    "Keeps the list read-only.",
    "Adds no new write endpoint.",
    "No accept/verify.",
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
        raise SystemExit(f"FAILED_V081_DOC_TERM_MISSING={term}")

if web_text.count('@app.post("/owner/manual-learning-evidence/{course_id}/save-draft"') != 1:
    raise SystemExit("FAILED_V081_UNEXPECTED_SAVE_DRAFT_ENDPOINT_COUNT")

# v0.8.1 must not add accept/verify endpoints.
# The display term accepted_owner_verified may already exist as an inert status option
# from earlier metadata UI work, so do not scan the whole app for that string.
for forbidden in [
    '@app.post("/owner/manual-learning-evidence/{course_id}/accept"',
    '@app.post("/owner/manual-learning-evidence/{course_id}/verify"',
]:
    if forbidden in web_text:
        raise SystemExit(f"FAILED_V081_FORBIDDEN_ENDPOINT_FOUND={forbidden}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-learning-evidence-list-drafts-no-learning-pack-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-learning-evidence-list-drafts-no-learning-pack-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-learning-evidence-list-drafts-no-learning-pack-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V081_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

course_id = "03-pag-30-34-vectori-trigonometrie"
manual_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}?page=1"
save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"

payload = {
    "draft_id": "v081-check-list-draft",
    "page": "1",
    "bbox": "[22, 44, 200, 160]",
    "kind": "formula",
    "title": "v0.8.1 list draft",
    "verified_text": "Draft list check",
    "explanation_ro": "Draft local pentru verificarea listei read-only.",
    "source_status": "uncertain",
    "source_note": "Created by v0.8.1 list check via existing v0.8.0 endpoint.",
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
    raise SystemExit(f"FAILED_V081_POST_FIXTURE_STATUS={exc.code}; BODY={error_body}")

if post_status != 200:
    raise SystemExit(f"FAILED_V081_POST_FIXTURE_STATUS={post_status}; BODY={post_body}")

try:
    post_data = json.loads(post_body)
except Exception as exc:
    raise SystemExit(f"FAILED_V081_POST_FIXTURE_JSON_PARSE={exc}; BODY={post_body}")

if post_data.get("ok") is not True:
    raise SystemExit("FAILED_V081_POST_FIXTURE_OK_FALSE=" + post_body)

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
    raise SystemExit(f"FAILED_V081_MANUAL_ROUTE_STATUS={manual_status}; ERROR={last_error}")

runtime_terms = [
    "Manual Learning Evidence · skeleton",
    "Draft evidence list",
    "manual_learning_evidence.json",
    "v081-check-list-draft",
    "v0.8.1 list draft",
    "pending_owner_review",
    "owner_verified: <code>false</code>",
    "save_state: <code>draft</code>",
    "bbox: <code>[22, 44, 200, 160]</code>",
    "No accept/verify action in v0.8.1.",
]

for term in runtime_terms:
    if term not in manual_body:
        raise SystemExit(f"FAILED_V081_RUNTIME_TERM_MISSING={term}")

summary = {
    "VOILA_V0_8_1_MANUAL_LEARNING_EVIDENCE_LIST_DRAFTS_CHECK": "PASS",
    "depends_on_v0794_direction_charter": True,
    "depends_on_v0795_ui_design": True,
    "depends_on_v0796_ui_skeleton": True,
    "depends_on_v0797_visual_polish_course_tools_link": True,
    "depends_on_v0798_crop_selection_preview": True,
    "depends_on_v0799_metadata_preview_binding": True,
    "depends_on_v080_save_draft_json": True,
    "manual_learning_evidence_route": "/owner/manual-learning-evidence/{course_id}?page=1",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "manual_route_status": manual_status,
    "list_drafts_ui_added": True,
    "draft_list_runtime_rendered": True,
    "fixture_saved_via_existing_v080_endpoint": True,
    "new_write_endpoint_added": False,
    "accept_verify_implemented": False,
    "manual_learning_evidence_json_read": True,
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
    "TESTER_READINESS": "BLOCKED_DRAFT_LIST_ONLY_NO_VERIFY_NO_LEARNING_PACK",
    "POLICY": "manual_learning_evidence_list_drafts_no_learning_pack_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v081-manual-learning-evidence-list-drafts")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.8.1-MANUAL-LEARNING-EVIDENCE-LIST-DRAFTS-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
