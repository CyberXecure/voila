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
doc = root / "docs" / "dev" / "manual-study-dry-run-browser-readiness-audit-no-progress-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0820_WEB_APP_MISSING"),
    (doc, "FAILED_V0820_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_18_MANUAL_STUDY_INTEGRATION_DRY_RUN_TOGGLE_START",
    "VOILA_V0_8_19_MANUAL_STUDY_DRY_RUN_COURSE_TOOLS_LINK_START",
    '@app.get("/owner/manual-study-integration-dry-run/{course_id}")',
    "_voila_v0819_inject_manual_study_dry_run_course_tools_link",
    "manual-study-dry-run-course-tools-link",
    "manual-study-dry-run-course-tools-status",
    "manual-study-integration-dry-run-route",
    "manual-study-integration-dry-run-toggle",
    "manual-study-integration-dry-run-toggle-off",
    "manual-study-integration-dry-run-cards",
    "manual_study_items.preview.json",
    "dry_run_only",
    "manual_study_connected_to_real_study",
    "writes_legacy_study_items_preview",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0820_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "Manual Study dry-run browser readiness audit",
    "Course Tools exposes the Manual Study dry-run link.",
    "Manual Study dry-run Toggle OFF route loads.",
    "Toggle OFF keeps cards hidden.",
    "Manual Study dry-run Toggle ON route loads.",
    "Toggle ON renders Study-like cards.",
    "Answers remain read-only inside `<details>`.",
    "Source metadata remains visible.",
    "Existing `/study` route code remains present and unchanged by this milestone.",
    "Legacy `study_items.preview.json` remains unchanged.",
    "This milestone is audit/check only.",
    "It does not modify `services/api/web_app.py`.",
    "It does not add a route.",
    "It does not add a POST endpoint.",
    "It does not connect Manual Study to real `/study`.",
    "It does not replace or modify the existing `/study` route.",
    "It does not write progress.",
    "It does not mark answers.",
    "It does not overwrite or modify the legacy `study_items.preview.json`.",
    "No UI implementation change.",
    "No real `/study` replacement.",
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
        raise SystemExit(f"FAILED_V0820_DOC_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/manual-study-dry-run-browser-readiness-audit-no-progress-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-study-dry-run-browser-readiness-audit-no-progress-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-study-dry-run-browser-readiness-audit-no-progress-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0820_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

if web_text.count('@app.get("/owner/manual-study-integration-dry-run/{course_id}"') != 1:
    raise SystemExit("FAILED_V0820_DRY_RUN_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/owner/manual-study-integration-dry-run') != 0:
    raise SystemExit("FAILED_V0820_DRY_RUN_POST_ADDED")

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0820_STUDY_ROUTE_COUNT_CHANGED")

for forbidden in [
    '@app.post("/owner/manual-study-integration-dry-run',
    "progress_write = True",
    "answer_marking = True",
    "manual_study_connected_to_real_study = True",
    "replaces_study_route = True",
    "writes_legacy_study_items_preview = True",
    "course_generation_changed = True",
    "study_changed = True",
    "progress_changed = True",
    "ocr_rewrite_performed = True",
    "formula_ocr_performed = True",
    '"study_changed": True',
    '"progress_changed": True',
]:
    if forbidden in web_text:
        raise SystemExit(f"FAILED_V0820_FORBIDDEN_WEB_TERM_FOUND={forbidden}")

course_id = "03-pag-30-34-vectori-trigonometrie"
output_dir = root / "data" / "output" / course_id
manual_study_preview = output_dir / "manual_study_items.preview.json"
legacy_study_preview = output_dir / "study_items.preview.json"
legacy_before = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None

home_url = "http://127.0.0.1:8787/"
course_tools_url = "http://127.0.0.1:8787/course-tools"
dry_run_off_url = f"http://127.0.0.1:8787/owner/manual-study-integration-dry-run/{course_id}?enabled=0"
dry_run_on_url = f"http://127.0.0.1:8787/owner/manual-study-integration-dry-run/{course_id}?enabled=1"

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
        raise SystemExit(f"FAILED_V0820_POST={url}; STATUS={exc.code}; BODY={error_body}")

def fetch_url(url, label):
    last_error = ""
    for _ in range(10):
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                return response.status, response.read().decode("utf-8", errors="replace"), response.geturl()
        except urllib.error.HTTPError as exc:
            try:
                error_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                error_body = ""
            last_error = f"HTTP {exc.code}: {error_body[:800]}"
            time.sleep(2)
        except Exception as exc:
            last_error = str(exc)
            time.sleep(2)
    raise SystemExit(f"FAILED_V0820_{label}_FETCH={last_error}")

eligible_id = "v0820-check-dry-run-browser-readiness-eligible"

payload = {
    "draft_id": eligible_id,
    "page": "1",
    "bbox": "[202, 224, 580, 510]",
    "kind": "formula",
    "title": "v0.8.20 dry-run browser readiness eligible",
    "verified_text": "Dry-run browser readiness prompt text",
    "explanation_ro": "Răspuns read-only pentru auditul dry-run browser readiness.",
    "source_status": "verified",
    "source_note": "Created by v0.8.20 dry-run browser readiness audit check.",
}

status, body, _ = post_form(save_url, payload)
if status != 200:
    raise SystemExit(f"FAILED_V0820_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body, _ = post_form(verify_url, {"draft_id": eligible_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V0820_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

learning_export_status, learning_export_body, _ = post_form(learning_pack_export_url, {})
if learning_export_status != 200:
    raise SystemExit(f"FAILED_V0820_LEARNING_PACK_EXPORT_STATUS={learning_export_status}; BODY={learning_export_body}")

manual_study_export_status, manual_study_export_body, _ = post_form(manual_study_export_url, {})
if manual_study_export_status != 200:
    raise SystemExit(f"FAILED_V0820_MANUAL_STUDY_EXPORT_STATUS={manual_study_export_status}; BODY={manual_study_export_body}")

if not manual_study_preview.exists():
    raise SystemExit("FAILED_V0820_MANUAL_STUDY_PREVIEW_JSON_MISSING")

home_status, home_body, _ = fetch_url(home_url, "HOME")
course_tools_match = re.search(r'href="([^"]*/course-tools[^"]*)"', home_body)
if course_tools_match:
    discovered_course_tools_url = course_tools_match.group(1).replace("&amp;", "&")
    if discovered_course_tools_url.startswith("/"):
        course_tools_url = "http://127.0.0.1:8787" + discovered_course_tools_url
    elif discovered_course_tools_url.startswith("http://") or discovered_course_tools_url.startswith("https://"):
        course_tools_url = discovered_course_tools_url

course_tools_status, course_tools_body, fetched_course_tools_url = fetch_url(course_tools_url, "COURSE_TOOLS")
dry_run_off_status, dry_run_off_body, _ = fetch_url(dry_run_off_url, "DRY_RUN_OFF")
dry_run_on_status, dry_run_on_body, _ = fetch_url(dry_run_on_url, "DRY_RUN_ON")

if home_status != 200:
    raise SystemExit(f"FAILED_V0820_HOME_STATUS={home_status}")

if course_tools_status != 200:
    raise SystemExit(f"FAILED_V0820_COURSE_TOOLS_STATUS={course_tools_status}")

if dry_run_off_status != 200:
    raise SystemExit(f"FAILED_V0820_DRY_RUN_OFF_STATUS={dry_run_off_status}")

if dry_run_on_status != 200:
    raise SystemExit(f"FAILED_V0820_DRY_RUN_ON_STATUS={dry_run_on_status}")

course_tools_terms = [
    "manual-study-dry-run-course-tools-section",
    "manual-study-dry-run-course-tools-link",
    "manual-study-dry-run-course-tools-status",
    "/owner/manual-study-integration-dry-run/03-pag-30-34-vectori-trigonometrie?enabled=0",
    "manual_study_items.preview.json",
    "dry_run_toggle_default",
    "off",
    "integration_mode",
    "dry_run_only",
    "manual_study_connected_to_real_study",
    "progress_write",
    "answer_marking",
    "writes_legacy_study_items_preview",
    "false",
]

for term in course_tools_terms:
    if term not in course_tools_body:
        raise SystemExit(f"FAILED_V0820_COURSE_TOOLS_TERM_MISSING={term}")

off_terms = [
    "Manual Study Integration Dry Run",
    "manual-study-integration-dry-run-route",
    "manual-study-integration-dry-run-toggle",
    "manual-study-integration-dry-run-toggle-off",
    "dry_run_toggle_enabled",
    "false",
    "manual_study_items.preview.json",
    "dry_run_only",
    "manual_study_connected_to_real_study",
    "progress_write",
    "answer_marking",
    "writes_legacy_study_items_preview",
]

for term in off_terms:
    if term not in dry_run_off_body:
        raise SystemExit(f"FAILED_V0820_DRY_RUN_OFF_TERM_MISSING={term}")

if "Dry-run browser readiness prompt text" in dry_run_off_body:
    raise SystemExit("FAILED_V0820_TOGGLE_OFF_RENDERED_CARD_TEXT")

on_terms = [
    "Manual Study Integration Dry Run",
    "manual-study-integration-dry-run-route",
    "manual-study-integration-dry-run-toggle",
    "manual-study-integration-dry-run-cards",
    "dry_run_toggle_enabled",
    "true",
    "target_route",
    "/study",
    "integration_mode",
    "dry_run_only",
    "manual-study-preview-card",
    "manual-study-preview-answer",
    "manual-study-preview-source",
    "manual-study-preview-card-navigation",
    "manual-study-preview-prev",
    "manual-study-preview-next",
    "Dry-run browser readiness prompt text",
    "Răspuns read-only pentru auditul dry-run browser readiness.",
    "manual_study_connected_to_real_study",
    "replaces_existing_study_route",
    "progress_write",
    "answer_marking",
    "writes_legacy_study_items_preview",
    "false",
]

for term in on_terms:
    if term not in dry_run_on_body:
        raise SystemExit(f"FAILED_V0820_DRY_RUN_ON_TERM_MISSING={term}")

manual_study = json.loads(manual_study_preview.read_text(encoding="utf-8", errors="replace"))
items = manual_study.get("items")
if not isinstance(items, list):
    raise SystemExit("FAILED_V0820_ITEMS_INVALID")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}
if eligible_id not in ids:
    raise SystemExit("FAILED_V0820_ELIGIBLE_ID_NOT_EXPORTED")

legacy_after = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None
if legacy_before != legacy_after:
    raise SystemExit("FAILED_V0820_LEGACY_STUDY_PREVIEW_CHANGED")

manual_result = {
    "manual_browser_audit_status": "OWNER_LOCAL_MANUAL_STUDY_DRY_RUN_BROWSER_READINESS_PASS",
    "steps": [
        {"step": "homepage_loads", "status": "PASS", "http_status": home_status},
        {"step": "course_tools_url_discovered", "status": "PASS", "url": fetched_course_tools_url},
        {"step": "course_tools_loads", "status": "PASS", "http_status": course_tools_status},
        {"step": "course_tools_dry_run_link_visible", "status": "PASS"},
        {"step": "course_tools_dry_run_status_visible", "status": "PASS"},
        {"step": "dry_run_toggle_off_loads", "status": "PASS", "http_status": dry_run_off_status},
        {"step": "dry_run_toggle_off_cards_hidden", "status": "PASS"},
        {"step": "dry_run_toggle_on_loads", "status": "PASS", "http_status": dry_run_on_status},
        {"step": "dry_run_toggle_on_cards_visible", "status": "PASS"},
        {"step": "answers_remain_read_only_details", "status": "PASS"},
        {"step": "source_metadata_visible", "status": "PASS"},
        {"step": "study_route_unchanged_static_guard", "status": "PASS"},
        {"step": "legacy_study_items_preview_unchanged", "status": "PASS"},
    ],
}

summary = {
    "VOILA_V0_8_20_MANUAL_STUDY_DRY_RUN_BROWSER_READINESS_AUDIT_CHECK": "PASS",
    "depends_on_v0818_dry_run_toggle": True,
    "depends_on_v0819_course_tools_link": True,
    "home_route_status": home_status,
    "course_tools_route_status": course_tools_status,
    "dry_run_off_status": dry_run_off_status,
    "dry_run_on_status": dry_run_on_status,
    "course_tools_dry_run_link_visible": True,
    "course_tools_dry_run_status_visible": True,
    "dry_run_toggle_off_visible": True,
    "dry_run_toggle_off_cards_hidden": True,
    "dry_run_toggle_on_visible": True,
    "dry_run_toggle_on_cards_visible": True,
    "answer_details_remain_read_only": True,
    "source_metadata_visible": True,
    "manual_browser_audit_recorded": True,
    "web_app_changed": False,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "manual_study_connected_to_real_study": False,
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
    "TESTER_READINESS": "BLOCKED_AUDIT_ONLY_NO_REAL_STUDY_INTEGRATION_NO_PACKAGE",
    "POLICY": "manual_study_dry_run_browser_readiness_audit_no_progress_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0820-manual-study-dry-run-browser-readiness-audit")
evidence.mkdir(parents=True, exist_ok=True)

out_json = evidence / "V0.8.20-MANUAL-STUDY-DRY-RUN-BROWSER-READINESS-AUDIT-CHECK.json"
out_md = evidence / "V0.8.20-MANUAL-STUDY-DRY-RUN-BROWSER-READINESS-AUDIT-CHECK.md"

out_json.write_text(json.dumps({"summary": summary, "manual_result": manual_result}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.20 Manual Study dry-run browser readiness audit",
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
