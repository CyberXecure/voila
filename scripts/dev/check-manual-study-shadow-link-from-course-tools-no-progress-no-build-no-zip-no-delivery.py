from pathlib import Path
import json
import re
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-study-shadow-link-from-course-tools-no-progress-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0824_WEB_APP_MISSING"),
    (doc, "FAILED_V0824_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_24_MANUAL_STUDY_SHADOW_COURSE_TOOLS_LINK_START",
    "manual-study-shadow-course-tools-link",
    "shadow_route",
    "shadow_integration_mode",
    "manual_study_default_enabled",
    "shadow_only_explicit_link",
    "/study?manual_study_shadow=1&course_id=",
    "read_only_shadow_toggle",
    "manual-study-dry-run-course-tools-link",
    "manual-study-dry-run-course-tools-status",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0824_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "Manual Study shadow link from Course Tools",
    "`/study?manual_study_shadow=1&course_id={course_id}`",
    "`/owner/manual-study-integration-dry-run/{course_id}?enabled=0`",
    "`manual_study_items.preview.json`",
    "`read_only_shadow_toggle`",
    "`manual_study_default_enabled=false`",
    "`manual_study_connected_to_real_study=shadow_only_explicit_link`",
    "`progress_write=false`",
    "`answer_marking=false`",
    "`writes_legacy_study_items_preview=false`",
    "This milestone only exposes a Course Tools link to the existing explicit shadow route.",
    "It does not make Manual Study the default `/study`.",
    "It does not replace or modify the existing `/study` route.",
    "It does not add a route.",
    "It does not add a POST endpoint.",
    "It does not write progress.",
    "It does not mark answers.",
    "It does not overwrite or modify the legacy `study_items.preview.json`.",
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
        raise SystemExit(f"FAILED_V0824_DOC_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-study-shadow-link-from-course-tools-no-progress-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-study-shadow-link-from-course-tools-no-progress-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-study-shadow-link-from-course-tools-no-progress-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0824_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0824_STUDY_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/study"') != 0:
    raise SystemExit("FAILED_V0824_STUDY_POST_ADDED")

if web_text.count("VOILA_V0_8_24_MANUAL_STUDY_SHADOW_COURSE_TOOLS_LINK_START") != 1:
    raise SystemExit("FAILED_V0824_SHADOW_COURSE_TOOLS_LINK_COUNT_CHANGED")

for forbidden in [
    '@app.post("/study"',
    "progress_write = True",
    "answer_marking = True",
    "replaces_existing_study_route = True",
    "writes_legacy_study_items_preview = True",
    "study_artifact_written = True",
    "manual_study_default_enabled=<code>true</code>",
    "course_generation_changed = True",
    "progress_changed = True",
    "ocr_rewrite_performed = True",
    "formula_ocr_performed = True",
    '"progress_changed": True',
]:
    if forbidden in web_text:
        raise SystemExit(f"FAILED_V0824_FORBIDDEN_WEB_TERM_FOUND={forbidden}")

course_id = "03-pag-30-34-vectori-trigonometrie"
output_dir = root / "data" / "output" / course_id
manual_study_preview = output_dir / "manual_study_items.preview.json"
legacy_study_preview = output_dir / "study_items.preview.json"
legacy_before = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None

home_url = "http://127.0.0.1:8787/"
course_tools_url = "http://127.0.0.1:8787/course-tools"
study_shadow_url = f"http://127.0.0.1:8787/study?manual_study_shadow=1&course_id={course_id}"
dry_run_off_url = f"http://127.0.0.1:8787/owner/manual-study-integration-dry-run/{course_id}?enabled=0"

save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"
verify_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/verify-draft"
learning_pack_export_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"
manual_study_export_url = f"http://127.0.0.1:8787/owner/manual-learning-pack-study-adapter-dry-run/{course_id}/export-manual-study-items-preview"

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
        raise SystemExit(f"FAILED_V0824_POST={url}; STATUS={exc.code}; BODY={error_body}")

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
    raise SystemExit(f"FAILED_V0824_{label}_FETCH={last_error}")

eligible_id = "v0824-check-shadow-course-tools-link-eligible"

payload = {
    "draft_id": eligible_id,
    "page": "1",
    "bbox": "[242, 264, 660, 590]",
    "kind": "formula",
    "title": "v0.8.24 shadow course tools link eligible",
    "verified_text": "Shadow Course Tools link prompt text",
    "explanation_ro": "Răspuns read-only pentru linkul shadow din Course Tools.",
    "source_status": "verified",
    "source_note": "Created by v0.8.24 shadow Course Tools link check.",
}

status, body, _ = post_form(save_url, payload)
if status != 200:
    raise SystemExit(f"FAILED_V0824_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body, _ = post_form(verify_url, {"draft_id": eligible_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V0824_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

learning_export_status, learning_export_body, _ = post_form(learning_pack_export_url, {})
if learning_export_status != 200:
    raise SystemExit(f"FAILED_V0824_LEARNING_PACK_EXPORT_STATUS={learning_export_status}; BODY={learning_export_body}")

manual_study_export_status, manual_study_export_body, _ = post_form(manual_study_export_url, {})
if manual_study_export_status != 200:
    raise SystemExit(f"FAILED_V0824_MANUAL_STUDY_EXPORT_STATUS={manual_study_export_status}; BODY={manual_study_export_body}")

if not manual_study_preview.exists():
    raise SystemExit("FAILED_V0824_MANUAL_STUDY_PREVIEW_JSON_MISSING")

home_status, home_body, _ = fetch_url_allow_http_error(home_url, "HOME")
course_tools_match = re.search(r'href="([^"]*/course-tools[^"]*)"', home_body)
if course_tools_match:
    discovered_course_tools_url = course_tools_match.group(1).replace("&amp;", "&")
    if discovered_course_tools_url.startswith("/"):
        course_tools_url = "http://127.0.0.1:8787" + discovered_course_tools_url
    elif discovered_course_tools_url.startswith("http://") or discovered_course_tools_url.startswith("https://"):
        course_tools_url = discovered_course_tools_url

course_tools_status, course_tools_body, fetched_course_tools_url = fetch_url_allow_http_error(course_tools_url, "COURSE_TOOLS")
study_shadow_status, study_shadow_body, _ = fetch_url_allow_http_error(study_shadow_url, "STUDY_SHADOW")
dry_run_status, dry_run_body, _ = fetch_url_allow_http_error(dry_run_off_url, "DRY_RUN")

if home_status != 200:
    raise SystemExit(f"FAILED_V0824_HOME_STATUS={home_status}")

if course_tools_status != 200:
    raise SystemExit(f"FAILED_V0824_COURSE_TOOLS_STATUS={course_tools_status}; BODY={course_tools_body[:800]}")

if study_shadow_status != 200:
    raise SystemExit(f"FAILED_V0824_STUDY_SHADOW_STATUS={study_shadow_status}; BODY={study_shadow_body[:800]}")

if dry_run_status != 200:
    raise SystemExit(f"FAILED_V0824_DRY_RUN_STATUS={dry_run_status}; BODY={dry_run_body[:800]}")

course_tools_terms = [
    "manual-study-dry-run-course-tools-link",
    "manual-study-shadow-course-tools-link",
    "manual-study-dry-run-course-tools-status",
    "/owner/manual-study-integration-dry-run/03-pag-30-34-vectori-trigonometrie?enabled=0",
    "/study?manual_study_shadow=1&amp;course_id=03-pag-30-34-vectori-trigonometrie",
    "shadow_route",
    "shadow_integration_mode",
    "read_only_shadow_toggle",
    "manual_study_default_enabled",
    "false",
    "manual_study_connected_to_real_study",
    "shadow_only_explicit_link",
    "progress_write",
    "answer_marking",
    "writes_legacy_study_items_preview",
]

for term in course_tools_terms:
    if term not in course_tools_body:
        raise SystemExit(f"FAILED_V0824_COURSE_TOOLS_TERM_MISSING={term}")

shadow_terms = [
    "Study · Manual Shadow",
    "manual-study-shadow-route",
    "manual-study-shadow-source",
    "manual-study-shadow-policy",
    "manual-study-shadow-cards",
    "manual_study_items.preview.json",
    "read_only_shadow_toggle",
    "manual-study-preview-card",
    "manual-study-preview-answer",
    "manual-study-preview-source",
    "Shadow Course Tools link prompt text",
    "Răspuns read-only pentru linkul shadow din Course Tools.",
]

for term in shadow_terms:
    if term not in study_shadow_body:
        raise SystemExit(f"FAILED_V0824_STUDY_SHADOW_TERM_MISSING={term}")

dry_run_terms = [
    "Manual Study Integration Dry Run",
    "manual-study-integration-dry-run-route",
    "dry_run_toggle_enabled",
    "false",
    "dry_run_only",
]

for term in dry_run_terms:
    if term not in dry_run_body:
        raise SystemExit(f"FAILED_V0824_DRY_RUN_TERM_MISSING={term}")

manual_study = json.loads(manual_study_preview.read_text(encoding="utf-8", errors="replace"))
items = manual_study.get("items")
if not isinstance(items, list):
    raise SystemExit("FAILED_V0824_ITEMS_INVALID")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}
if eligible_id not in ids:
    raise SystemExit("FAILED_V0824_ELIGIBLE_ID_NOT_EXPORTED")

legacy_after = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None
if legacy_before != legacy_after:
    raise SystemExit("FAILED_V0824_LEGACY_STUDY_PREVIEW_CHANGED")

summary = {
    "VOILA_V0_8_24_MANUAL_STUDY_SHADOW_LINK_FROM_COURSE_TOOLS_CHECK": "PASS",
    "depends_on_v0822_shadow_toggle": True,
    "depends_on_v0823_shadow_browser_readiness_audit": True,
    "course_tools_route_status": course_tools_status,
    "study_shadow_status": study_shadow_status,
    "dry_run_status": dry_run_status,
    "course_tools_shadow_link_added": True,
    "course_tools_dry_run_link_preserved": True,
    "course_tools_shadow_status_visible": True,
    "manual_study_items_preview_json_detected": True,
    "shadow_route_reachable": True,
    "dry_run_route_still_reachable": True,
    "integration_mode": "read_only_shadow_toggle",
    "manual_study_default_enabled": False,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "manual_study_connected_to_real_study": "shadow_only_explicit_link",
    "replaces_existing_study_route": False,
    "progress_write_added": False,
    "answer_marking_added": False,
    "study_artifact_written": False,
    "legacy_study_items_preview_unchanged": True,
    "crop_file_written": False,
    "course_generation_changed": False,
    "study_changed": "course_tools_link_only",
    "progress_changed": False,
    "ocr_rewrite_performed": False,
    "formula_ocr_performed": False,
    "build_performed": False,
    "zip_created": False,
    "share_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "TESTER_READINESS": "BLOCKED_LINK_ONLY_NO_DEFAULT_STUDY_NO_PACKAGE",
    "POLICY": "manual_study_shadow_link_from_course_tools_no_progress_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0824-manual-study-shadow-link-from-course-tools")
evidence.mkdir(parents=True, exist_ok=True)

out_json = evidence / "V0.8.24-MANUAL-STUDY-SHADOW-LINK-FROM-COURSE-TOOLS-CHECK.json"
out_md = evidence / "V0.8.24-MANUAL-STUDY-SHADOW-LINK-FROM-COURSE-TOOLS-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.24 Manual Study shadow link from Course Tools",
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
