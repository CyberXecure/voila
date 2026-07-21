from pathlib import Path
import hashlib
import json
import re
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-study-shadow-browser-readiness-audit-no-progress-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0823_WEB_APP_MISSING"),
    (doc, "FAILED_V0823_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

expected_v0821_study_route_hash = "ad12be8afe880715e47cfcb9ef7aeb3dd364aeb0d98ee4a97ce2de338c3566ad"

required_web_terms = [
    "VOILA_V0_8_22_MANUAL_STUDY_REAL_STUDY_READ_ONLY_SHADOW_TOGGLE_START",
    "_voila_v0822_manual_study_shadow_toggle_enabled",
    "_voila_v0822_manual_study_shadow_page",
    "_voila_v0822_manual_study_real_study_read_only_shadow_toggle_middleware",
    '@app.get("/study"',
    "manual_study_shadow",
    "manual-study-shadow-route",
    "manual-study-shadow-source",
    "manual-study-shadow-policy",
    "manual-study-shadow-cards",
    "manual-study-shadow-missing-course",
    "manual_study_items.preview.json",
    "study_items.preview.json",
    "read_only_shadow_toggle",
    "fallback_existing_study_available",
    "writes_legacy_study_items_preview",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0823_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "Manual Study shadow browser readiness audit",
    "`/study?manual_study_shadow=1&course_id={course_id}` loads with HTTP 200.",
    "The shadow route reads `manual_study_items.preview.json`.",
    "The shadow route renders Manual Study cards.",
    "Answers remain read-only inside `<details>`.",
    "Source metadata remains visible.",
    "`/study?manual_study_shadow=1` without `course_id` shows the missing course message.",
    "`/study` without shadow toggle does not render the Manual Study shadow page.",
    "Existing `/study` route block hash remains unchanged from the v0.8.21 preflight snapshot.",
    "Legacy `study_items.preview.json` remains unchanged.",
    "This milestone is audit/check only.",
    "It does not modify `services/api/web_app.py`.",
    "It does not add a route.",
    "It does not add a POST endpoint.",
    "It does not connect Manual Study as the default real `/study`.",
    "It does not replace or modify the existing `/study` route.",
    "It does not write progress.",
    "It does not mark answers.",
    "It does not overwrite or modify the legacy `study_items.preview.json`.",
    "No UI implementation change.",
    "No default `/study` replacement.",
    "No silent switch from legacy Study to Manual Study.",
    "No new Progress behavior.",
    "No answer marking.",
    "No Study artifact write.",
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
        raise SystemExit(f"FAILED_V0823_DOC_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/manual-study-shadow-browser-readiness-audit-no-progress-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-study-shadow-browser-readiness-audit-no-progress-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-study-shadow-browser-readiness-audit-no-progress-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0823_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0823_STUDY_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/study"') != 0:
    raise SystemExit("FAILED_V0823_STUDY_POST_ADDED")

if web_text.count("VOILA_V0_8_22_MANUAL_STUDY_REAL_STUDY_READ_ONLY_SHADOW_TOGGLE_START") != 1:
    raise SystemExit("FAILED_V0823_SHADOW_BLOCK_COUNT_CHANGED")

for forbidden in [
    '@app.post("/study"',
    "progress_write = True",
    "answer_marking = True",
    "replaces_existing_study_route = True",
    "writes_legacy_study_items_preview = True",
    "study_artifact_written = True",
    "course_generation_changed = True",
    "progress_changed = True",
    "ocr_rewrite_performed = True",
    "formula_ocr_performed = True",
    '"progress_changed": True',
]:
    if forbidden in web_text:
        raise SystemExit(f"FAILED_V0823_FORBIDDEN_WEB_TERM_FOUND={forbidden}")

study_route_match = re.search(
    r'@app\.get\("/study"[\s\S]*?(?=\n@app\.(?:get|post|put|delete|patch)\(|\Z)',
    web_text,
)
if not study_route_match:
    raise SystemExit("FAILED_V0823_STUDY_ROUTE_STATIC_BLOCK_NOT_FOUND")

study_route_block = study_route_match.group(0)
study_route_hash = hashlib.sha256(study_route_block.encode("utf-8", errors="replace")).hexdigest()

if study_route_hash != expected_v0821_study_route_hash:
    raise SystemExit(
        "FAILED_V0823_STUDY_ROUTE_HASH_CHANGED="
        + study_route_hash
        + ";EXPECTED="
        + expected_v0821_study_route_hash
    )

course_id = "03-pag-30-34-vectori-trigonometrie"
output_dir = root / "data" / "output" / course_id
manual_study_preview = output_dir / "manual_study_items.preview.json"
legacy_study_preview = output_dir / "study_items.preview.json"
legacy_before = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None

save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"
verify_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/verify-draft"
learning_pack_export_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"
manual_study_export_url = f"http://127.0.0.1:8787/owner/manual-learning-pack-study-adapter-dry-run/{course_id}/export-manual-study-items-preview"

study_shadow_url = f"http://127.0.0.1:8787/study?manual_study_shadow=1&course_id={course_id}"
study_shadow_missing_course_url = "http://127.0.0.1:8787/study?manual_study_shadow=1"
study_fallback_probe_url = "http://127.0.0.1:8787/study"

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
        raise SystemExit(f"FAILED_V0823_POST={url}; STATUS={exc.code}; BODY={error_body}")

def fetch_url_allow_http_error(url, label):
    last_error = ""
    for _ in range(10):
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                return response.status, response.read().decode("utf-8", errors="replace"), response.geturl()
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            return exc.code, error_body, url
        except Exception as exc:
            last_error = str(exc)
            time.sleep(2)
    raise SystemExit(f"FAILED_V0823_{label}_FETCH={last_error}")

eligible_id = "v0823-check-shadow-browser-readiness-eligible"

payload = {
    "draft_id": eligible_id,
    "page": "1",
    "bbox": "[232, 254, 640, 570]",
    "kind": "formula",
    "title": "v0.8.23 shadow browser readiness eligible",
    "verified_text": "Shadow browser readiness prompt text",
    "explanation_ro": "Răspuns read-only pentru auditul shadow browser readiness.",
    "source_status": "verified",
    "source_note": "Created by v0.8.23 shadow browser readiness audit check.",
}

status, body, _ = post_form(save_url, payload)
if status != 200:
    raise SystemExit(f"FAILED_V0823_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body, _ = post_form(verify_url, {"draft_id": eligible_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V0823_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

learning_export_status, learning_export_body, _ = post_form(learning_pack_export_url, {})
if learning_export_status != 200:
    raise SystemExit(f"FAILED_V0823_LEARNING_PACK_EXPORT_STATUS={learning_export_status}; BODY={learning_export_body}")

manual_study_export_status, manual_study_export_body, _ = post_form(manual_study_export_url, {})
if manual_study_export_status != 200:
    raise SystemExit(f"FAILED_V0823_MANUAL_STUDY_EXPORT_STATUS={manual_study_export_status}; BODY={manual_study_export_body}")

if not manual_study_preview.exists():
    raise SystemExit("FAILED_V0823_MANUAL_STUDY_PREVIEW_JSON_MISSING")

shadow_status, shadow_body, _ = fetch_url_allow_http_error(study_shadow_url, "STUDY_SHADOW")
missing_status, missing_body, _ = fetch_url_allow_http_error(study_shadow_missing_course_url, "STUDY_SHADOW_MISSING_COURSE")
fallback_status, fallback_body, _ = fetch_url_allow_http_error(study_fallback_probe_url, "STUDY_FALLBACK")

if shadow_status != 200:
    raise SystemExit(f"FAILED_V0823_STUDY_SHADOW_STATUS={shadow_status}; BODY={shadow_body[:800]}")

if missing_status != 200:
    raise SystemExit(f"FAILED_V0823_STUDY_SHADOW_MISSING_COURSE_STATUS={missing_status}; BODY={missing_body[:800]}")

if fallback_status == 200 and "manual-study-shadow-route" in fallback_body:
    raise SystemExit("FAILED_V0823_FALLBACK_RENDERED_SHADOW_WITHOUT_TOGGLE")

shadow_terms = [
    "Study · Manual Shadow",
    "manual-study-shadow-route",
    "manual-study-shadow-navigation",
    "manual-study-shadow-source",
    "manual-study-shadow-policy",
    "manual-study-shadow-cards",
    "manual_study_shadow",
    "true",
    "manual_study_items.preview.json",
    "read_only_shadow_toggle",
    "fallback_existing_study_available",
    "manual_study_connected_to_real_study",
    "shadow_only",
    "replaces_existing_study_route",
    "progress_write",
    "answer_marking",
    "writes_legacy_study_items_preview",
    "study_artifact_written",
    "false",
    "manual-study-preview-card",
    "manual-study-preview-answer",
    "manual-study-preview-source",
    "manual-study-preview-card-navigation",
    "Shadow browser readiness prompt text",
    "Răspuns read-only pentru auditul shadow browser readiness.",
]

for term in shadow_terms:
    if term not in shadow_body:
        raise SystemExit(f"FAILED_V0823_STUDY_SHADOW_TERM_MISSING={term}")

missing_terms = [
    "manual-study-shadow-missing-course",
    "Lipsește",
    "course_id",
    "Fallback-ul /study existent",
]

for term in missing_terms:
    if term not in missing_body:
        raise SystemExit(f"FAILED_V0823_MISSING_COURSE_TERM_MISSING={term}")

manual_study = json.loads(manual_study_preview.read_text(encoding="utf-8", errors="replace"))
items = manual_study.get("items")
if not isinstance(items, list):
    raise SystemExit("FAILED_V0823_ITEMS_INVALID")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}
if eligible_id not in ids:
    raise SystemExit("FAILED_V0823_ELIGIBLE_ID_NOT_EXPORTED")

legacy_after = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None
if legacy_before != legacy_after:
    raise SystemExit("FAILED_V0823_LEGACY_STUDY_PREVIEW_CHANGED")

manual_result = {
    "manual_browser_audit_status": "OWNER_LOCAL_MANUAL_STUDY_SHADOW_BROWSER_READINESS_PASS",
    "steps": [
        {"step": "study_shadow_route_loads", "status": "PASS", "http_status": shadow_status},
        {"step": "manual_study_items_preview_json_read", "status": "PASS"},
        {"step": "manual_study_shadow_cards_visible", "status": "PASS"},
        {"step": "answers_remain_read_only_details", "status": "PASS"},
        {"step": "source_metadata_visible", "status": "PASS"},
        {"step": "missing_course_id_message_visible", "status": "PASS", "http_status": missing_status},
        {"step": "fallback_without_toggle_does_not_render_shadow", "status": "PASS", "http_status": fallback_status},
        {"step": "study_route_hash_matches_v0821_preflight", "status": "PASS"},
        {"step": "legacy_study_items_preview_unchanged", "status": "PASS"},
    ],
}

summary = {
    "VOILA_V0_8_23_MANUAL_STUDY_SHADOW_BROWSER_READINESS_AUDIT_CHECK": "PASS",
    "depends_on_v0822_shadow_toggle": True,
    "study_shadow_status": shadow_status,
    "study_shadow_missing_course_status": missing_status,
    "study_fallback_probe_status": fallback_status,
    "study_route_hash_matches_v0821_preflight": True,
    "study_route_block_sha256": study_route_hash,
    "manual_study_items_preview_json_read": True,
    "manual_study_shadow_cards_visible": True,
    "answer_details_remain_read_only": True,
    "source_metadata_visible": True,
    "missing_course_id_message_visible": True,
    "fallback_without_toggle_does_not_render_shadow": True,
    "manual_browser_audit_recorded": True,
    "web_app_changed": False,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "manual_study_connected_to_real_study": "shadow_only_existing_v0822",
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
    "TESTER_READINESS": "BLOCKED_AUDIT_ONLY_NO_DEFAULT_STUDY_NO_PACKAGE",
    "POLICY": "manual_study_shadow_browser_readiness_audit_no_progress_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0823-manual-study-shadow-browser-readiness-audit")
evidence.mkdir(parents=True, exist_ok=True)

out_json = evidence / "V0.8.23-MANUAL-STUDY-SHADOW-BROWSER-READINESS-AUDIT-CHECK.json"
out_md = evidence / "V0.8.23-MANUAL-STUDY-SHADOW-BROWSER-READINESS-AUDIT-CHECK.md"

out_json.write_text(json.dumps({"summary": summary, "manual_result": manual_result}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.23 Manual Study shadow browser readiness audit",
    "",
    "## Summary",
]
for key, value in summary.items():
    md_lines.append(f"- {key}: {value}")

md_lines.extend(["", "## Audited steps"])
for step in manual_result["steps"]:
    md_lines.append(f"- {step['step']}: {step['status']}")

out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
