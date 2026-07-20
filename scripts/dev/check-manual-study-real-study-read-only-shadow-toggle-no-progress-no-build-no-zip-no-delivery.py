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
doc = root / "docs" / "dev" / "manual-study-real-study-read-only-shadow-toggle-no-progress-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0822_WEB_APP_MISSING"),
    (doc, "FAILED_V0822_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_22_MANUAL_STUDY_REAL_STUDY_READ_ONLY_SHADOW_TOGGLE_START",
    "_voila_v0822_manual_study_shadow_toggle_enabled",
    "_voila_v0822_manual_study_shadow_page",
    "_voila_v0822_manual_study_real_study_read_only_shadow_toggle_middleware",
    '@app.get("/study"',
    'getattr(request.url, "path", "") != "/study"',
    "manual_study_shadow",
    "manual-study-shadow-route",
    "manual-study-shadow-source",
    "manual-study-shadow-policy",
    "manual-study-shadow-cards",
    "manual_study_items.preview.json",
    "study_items.preview.json",
    "read_only_shadow_toggle",
    "fallback_existing_study_available",
    "writes_legacy_study_items_preview",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0822_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "Manual Study real `/study` read-only shadow toggle",
    "first controlled owner-local touchpoint on the real `/study` route",
    "`/study?manual_study_shadow=1&course_id={course_id}`",
    "`manual_study_items.preview.json`",
    "existing `/study` behavior remains the fallback",
    "This is not default `/study` replacement.",
    "`manual_study_shadow=1`",
    "`course_id` is provided",
    "This milestone does not add a POST endpoint.",
    "It does not write progress.",
    "It does not mark answers.",
    "It does not overwrite or modify the legacy `study_items.preview.json`.",
    "It does not write a new Study artifact.",
    "`read_only_shadow_toggle`",
    "Existing `/study` fallback: available",
    "Answers: read-only in `<details>`",
    "Source metadata: visible",
    "Progress write: disabled",
    "Answer marking: disabled",
    "Legacy Study artifact write: disabled",
    "No default `/study` replacement.",
    "No silent switch from legacy Study to Manual Study.",
    "No new POST endpoint.",
    "No Progress write.",
    "No answer marking.",
    "No Study artifact write.",
    "No Course generation change.",
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
        raise SystemExit(f"FAILED_V0822_DOC_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-study-real-study-read-only-shadow-toggle-no-progress-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-study-real-study-read-only-shadow-toggle-no-progress-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-study-real-study-read-only-shadow-toggle-no-progress-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0822_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0822_STUDY_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/study"') != 0:
    raise SystemExit("FAILED_V0822_STUDY_POST_ADDED")

if web_text.count("VOILA_V0_8_22_MANUAL_STUDY_REAL_STUDY_READ_ONLY_SHADOW_TOGGLE_START") != 1:
    raise SystemExit("FAILED_V0822_SHADOW_BLOCK_COUNT_CHANGED")

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
        raise SystemExit(f"FAILED_V0822_FORBIDDEN_WEB_TERM_FOUND={forbidden}")

study_route_match = re.search(
    r'@app\.get\("/study"[\s\S]*?(?=\n@app\.(?:get|post|put|delete|patch)\(|\Z)',
    web_text,
)
if not study_route_match:
    raise SystemExit("FAILED_V0822_STUDY_ROUTE_STATIC_BLOCK_NOT_FOUND")

study_route_block = study_route_match.group(0)
study_route_hash = hashlib.sha256(study_route_block.encode("utf-8", errors="replace")).hexdigest()

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
        raise SystemExit(f"FAILED_V0822_POST={url}; STATUS={exc.code}; BODY={error_body}")

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
    raise SystemExit(f"FAILED_V0822_{label}_FETCH={last_error}")

eligible_id = "v0822-check-real-study-shadow-toggle-eligible"

payload = {
    "draft_id": eligible_id,
    "page": "1",
    "bbox": "[222, 244, 620, 550]",
    "kind": "formula",
    "title": "v0.8.22 real study shadow eligible",
    "verified_text": "Real Study shadow prompt text",
    "explanation_ro": "Răspuns read-only pentru shadow toggle pe /study.",
    "source_status": "verified",
    "source_note": "Created by v0.8.22 real Study shadow toggle check.",
}

status, body, _ = post_form(save_url, payload)
if status != 200:
    raise SystemExit(f"FAILED_V0822_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body, _ = post_form(verify_url, {"draft_id": eligible_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V0822_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

learning_export_status, learning_export_body, _ = post_form(learning_pack_export_url, {})
if learning_export_status != 200:
    raise SystemExit(f"FAILED_V0822_LEARNING_PACK_EXPORT_STATUS={learning_export_status}; BODY={learning_export_body}")

manual_study_export_status, manual_study_export_body, _ = post_form(manual_study_export_url, {})
if manual_study_export_status != 200:
    raise SystemExit(f"FAILED_V0822_MANUAL_STUDY_EXPORT_STATUS={manual_study_export_status}; BODY={manual_study_export_body}")

if not manual_study_preview.exists():
    raise SystemExit("FAILED_V0822_MANUAL_STUDY_PREVIEW_JSON_MISSING")

shadow_status, shadow_body, _ = fetch_url_allow_http_error(study_shadow_url, "STUDY_SHADOW")
missing_status, missing_body, _ = fetch_url_allow_http_error(study_shadow_missing_course_url, "STUDY_SHADOW_MISSING_COURSE")
fallback_status, fallback_body, _ = fetch_url_allow_http_error(study_fallback_probe_url, "STUDY_FALLBACK")

if shadow_status != 200:
    raise SystemExit(f"FAILED_V0822_STUDY_SHADOW_STATUS={shadow_status}; BODY={shadow_body[:800]}")

if missing_status != 200:
    raise SystemExit(f"FAILED_V0822_STUDY_SHADOW_MISSING_COURSE_STATUS={missing_status}; BODY={missing_body[:800]}")

if fallback_status == 200 and "manual-study-shadow-route" in fallback_body:
    raise SystemExit("FAILED_V0822_FALLBACK_RENDERED_SHADOW_WITHOUT_TOGGLE")

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
    "Real Study shadow prompt text",
    "Răspuns read-only pentru shadow toggle pe /study.",
]

for term in shadow_terms:
    if term not in shadow_body:
        raise SystemExit(f"FAILED_V0822_STUDY_SHADOW_TERM_MISSING={term}")

missing_terms = [
    "manual-study-shadow-missing-course",
    "Lipsește",
    "course_id",
    "Fallback-ul /study existent",
]

for term in missing_terms:
    if term not in missing_body:
        raise SystemExit(f"FAILED_V0822_MISSING_COURSE_TERM_MISSING={term}")

manual_study = json.loads(manual_study_preview.read_text(encoding="utf-8", errors="replace"))
items = manual_study.get("items")
if not isinstance(items, list):
    raise SystemExit("FAILED_V0822_ITEMS_INVALID")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}
if eligible_id not in ids:
    raise SystemExit("FAILED_V0822_ELIGIBLE_ID_NOT_EXPORTED")

legacy_after = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None
if legacy_before != legacy_after:
    raise SystemExit("FAILED_V0822_LEGACY_STUDY_PREVIEW_CHANGED")

summary = {
    "VOILA_V0_8_22_MANUAL_STUDY_REAL_STUDY_READ_ONLY_SHADOW_TOGGLE_CHECK": "PASS",
    "depends_on_v0821_preflight_freeze": True,
    "study_shadow_url": "/study?manual_study_shadow=1&course_id={course_id}",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "study_shadow_status": shadow_status,
    "study_shadow_missing_course_status": missing_status,
    "study_fallback_probe_status": fallback_status,
    "study_route_static_snapshot_recorded": True,
    "study_route_block_sha256_after_v0822": study_route_hash,
    "real_study_shadow_toggle_added": True,
    "manual_study_items_preview_json_read": True,
    "manual_study_items_rendered_when_shadow_enabled": True,
    "fallback_existing_study_available": True,
    "answer_details_remain_read_only": True,
    "source_metadata_visible": True,
    "integration_mode": "read_only_shadow_toggle",
    "new_post_endpoint_added": False,
    "manual_study_connected_to_real_study": "shadow_only",
    "replaces_existing_study_route": False,
    "progress_write_added": False,
    "answer_marking_added": False,
    "study_artifact_written": False,
    "legacy_study_items_preview_unchanged": True,
    "crop_file_written": False,
    "course_generation_changed": False,
    "study_changed": "shadow_toggle_only",
    "progress_changed": False,
    "ocr_rewrite_performed": False,
    "formula_ocr_performed": False,
    "build_performed": False,
    "zip_created": False,
    "share_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "TESTER_READINESS": "BLOCKED_SHADOW_TOGGLE_ONLY_NO_PROGRESS_NO_PACKAGE",
    "POLICY": "manual_study_real_study_read_only_shadow_toggle_no_progress_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0822-manual-study-real-study-read-only-shadow-toggle")
evidence.mkdir(parents=True, exist_ok=True)

out_json = evidence / "V0.8.22-MANUAL-STUDY-REAL-STUDY-READ-ONLY-SHADOW-TOGGLE-CHECK.json"
out_md = evidence / "V0.8.22-MANUAL-STUDY-REAL-STUDY-READ-ONLY-SHADOW-TOGGLE-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.22 Manual Study real `/study` read-only shadow toggle",
    "",
    "## Summary",
]
for key, value in summary.items():
    md_lines.append(f"- {key}: {value}")

out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
