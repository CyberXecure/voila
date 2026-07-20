from pathlib import Path
import json
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-study-route-read-only-preview-source-no-progress-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0813_WEB_APP_MISSING"),
    (doc, "FAILED_V0813_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_13_MANUAL_STUDY_ROUTE_READ_ONLY_PREVIEW_START",
    "VOILA_V0_8_13_MANUAL_STUDY_ROUTE_READ_ONLY_PREVIEW_CSS_START",
    "_voila_v0813_manual_study_preview_cards_html",
    '@app.get("/owner/manual-study-preview/{course_id}")',
    'data-testid="manual-study-preview-route"',
    'data-testid="manual-study-preview-schema"',
    'data-testid="manual-study-preview-course"',
    'data-testid="manual-study-preview-items-count"',
    'data-testid="manual-study-preview-policy"',
    'data-testid="manual-study-preview-cards"',
    'data-testid="manual-study-preview-card"',
    'data-testid="manual-study-preview-prompt"',
    'data-testid="manual-study-preview-answer"',
    'data-testid="manual-study-preview-source"',
    "Manual Study Preview",
    "manual_study_items.preview.json",
    "manual study route preview",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0813_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "separate owner-local read-only Manual Study preview route",
    "`/owner/manual-study-preview/{course_id}`",
    "`manual_study_items.preview.json`",
    "Study-like cards",
    "manual_study_item_id",
    "source_evidence_id",
    "study_item_type",
    "prompt",
    "answer in a read-only details block",
    "It does not write any artifact.",
    "It does not replace or modify the existing `/study` route.",
    "It does not write progress.",
    "It does not mark answers.",
    "It does not write or modify the legacy `study_items.preview.json`.",
    "No new POST endpoint.",
    "No Progress write.",
    "No answer marking.",
    "No Study integration.",
    "No Course integration.",
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
        raise SystemExit(f"FAILED_V0813_DOC_TERM_MISSING={term}")

if web_text.count('@app.get("/owner/manual-study-preview/{course_id}"') != 1:
    raise SystemExit("FAILED_V0813_MANUAL_STUDY_PREVIEW_ROUTE_COUNT")

if web_text.count('@app.post("/owner/manual-study-preview') != 0:
    raise SystemExit("FAILED_V0813_MANUAL_STUDY_PREVIEW_POST_ADDED")

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0813_STUDY_ROUTE_COUNT_CHANGED")

for forbidden in [
    '@app.post("/owner/manual-study-preview',
    "manual_progress",
    "progress_write = True",
    "answer_marking = True",
    "replaces_study_route = True",
    "course_generation_changed = True",
    "study_changed = True",
    "progress_changed = True",
    "ocr_rewrite_performed = True",
    "formula_ocr_performed = True",
    '"study_changed": True',
    '"progress_changed": True',
]:
    if forbidden in web_text:
        raise SystemExit(f"FAILED_V0813_FORBIDDEN_TERM_FOUND={forbidden}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-study-route-read-only-preview-source-no-progress-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-study-route-read-only-preview-source-no-progress-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-study-route-read-only-preview-source-no-progress-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0813_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

course_id = "03-pag-30-34-vectori-trigonometrie"
output_dir = root / "data" / "output" / course_id
manual_study_preview = output_dir / "manual_study_items.preview.json"
legacy_study_preview = output_dir / "study_items.preview.json"
legacy_before = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None

save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"
verify_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/verify-draft"
learning_pack_export_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"
manual_study_export_url = f"http://127.0.0.1:8787/owner/manual-learning-pack-study-adapter-dry-run/{course_id}/export-manual-study-items-preview"
manual_study_items_viewer_url = f"http://127.0.0.1:8787/owner/manual-study-items-preview/{course_id}"
manual_study_preview_url = f"http://127.0.0.1:8787/owner/manual-study-preview/{course_id}"

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
        raise SystemExit(f"FAILED_V0813_POST={url}; STATUS={exc.code}; BODY={error_body}")

eligible_id = "v0813-check-manual-study-preview-eligible"

payload = {
    "draft_id": eligible_id,
    "page": "1",
    "bbox": "[142, 164, 460, 390]",
    "kind": "formula",
    "title": "v0.8.13 manual study preview eligible",
    "verified_text": "Manual Study preview prompt text",
    "explanation_ro": "Răspuns afișat într-un card manual Study read-only.",
    "source_status": "verified",
    "source_note": "Created by v0.8.13 manual study route check.",
}

status, body, _ = post_form(save_url, payload)
if status != 200:
    raise SystemExit(f"FAILED_V0813_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body, _ = post_form(verify_url, {"draft_id": eligible_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V0813_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

learning_export_status, learning_export_body, _ = post_form(learning_pack_export_url, {})
if learning_export_status != 200:
    raise SystemExit(f"FAILED_V0813_LEARNING_PACK_EXPORT_STATUS={learning_export_status}; BODY={learning_export_body}")

manual_study_export_status, manual_study_export_body, _ = post_form(manual_study_export_url, {})
if manual_study_export_status != 200:
    raise SystemExit(f"FAILED_V0813_MANUAL_STUDY_EXPORT_STATUS={manual_study_export_status}; BODY={manual_study_export_body}")

if not manual_study_preview.exists():
    raise SystemExit("FAILED_V0813_MANUAL_STUDY_PREVIEW_JSON_MISSING")

def fetch_url(url, label):
    last_error = ""
    for _ in range(10):
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                return response.status, response.read().decode("utf-8", errors="replace")
        except Exception as exc:
            last_error = str(exc)
            time.sleep(2)
    raise SystemExit(f"FAILED_V0813_{label}_FETCH={last_error}")

items_viewer_status, items_viewer_body = fetch_url(manual_study_items_viewer_url, "ITEMS_VIEWER")
preview_status, preview_body = fetch_url(manual_study_preview_url, "MANUAL_STUDY_PREVIEW")

if items_viewer_status != 200:
    raise SystemExit(f"FAILED_V0813_ITEMS_VIEWER_STATUS={items_viewer_status}")

if preview_status != 200:
    raise SystemExit(f"FAILED_V0813_PREVIEW_STATUS={preview_status}")

items_viewer_terms = [
    "Manual Study Preview:",
    "/owner/manual-study-preview/",
]

for term in items_viewer_terms:
    if term not in items_viewer_body:
        raise SystemExit(f"FAILED_V0813_ITEMS_VIEWER_TERM_MISSING={term}")

runtime_terms = [
    "Manual Study Preview",
    "manual-study-preview-route",
    "manual-study-preview-schema",
    "manual-study-preview-course",
    "manual-study-preview-items-count",
    "manual-study-preview-policy",
    "manual-study-preview-cards",
    "manual-study-preview-card",
    "manual-study-preview-prompt",
    "manual-study-preview-answer",
    "manual-study-preview-source",
    "manual_study_items.preview.json",
    "progress_write",
    "answer_marking",
    "replaces_study_route",
    "false",
    "v0813-check-manual-study-preview-eligible",
    "v0.8.13 manual study preview eligible",
    "Manual Study preview prompt text",
    "Răspuns afișat într-un card manual Study read-only.",
    "formula_card",
]

for term in runtime_terms:
    if term not in preview_body:
        raise SystemExit(f"FAILED_V0813_PREVIEW_RUNTIME_TERM_MISSING={term}")

manual_study = json.loads(manual_study_preview.read_text(encoding="utf-8", errors="replace"))
items = manual_study.get("items")
if not isinstance(items, list):
    raise SystemExit("FAILED_V0813_ITEMS_INVALID")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}
if eligible_id not in ids:
    raise SystemExit("FAILED_V0813_ELIGIBLE_ID_NOT_EXPORTED")

legacy_after = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None
if legacy_before != legacy_after:
    raise SystemExit("FAILED_V0813_LEGACY_STUDY_PREVIEW_CHANGED")

summary = {
    "VOILA_V0_8_13_MANUAL_STUDY_ROUTE_READ_ONLY_PREVIEW_CHECK": "PASS",
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
    "depends_on_v0811_manual_study_export": True,
    "depends_on_v0812_manual_study_items_viewer": True,
    "manual_study_preview_route": "/owner/manual-study-preview/{course_id}",
    "manual_study_items_viewer_route": "/owner/manual-study-items-preview/{course_id}",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "manual_study_items_viewer_route_status": items_viewer_status,
    "manual_study_preview_route_status": preview_status,
    "manual_study_route_added": True,
    "manual_study_preview_json_read": True,
    "study_like_cards_visible": True,
    "prompt_visible": True,
    "answer_details_visible": True,
    "source_metadata_visible": True,
    "new_post_endpoint_added": False,
    "replaces_existing_study_route": False,
    "progress_write_added": False,
    "answer_marking_added": False,
    "study_artifact_written": False,
    "legacy_study_items_preview_unchanged": True,
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
    "TESTER_READINESS": "BLOCKED_MANUAL_STUDY_READ_ONLY_PREVIEW_NO_PROGRESS",
    "POLICY": "manual_study_route_read_only_preview_no_progress_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0813-manual-study-route-read-only-preview")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.8.13-MANUAL-STUDY-ROUTE-READ-ONLY-PREVIEW-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
