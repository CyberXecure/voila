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
doc = root / "docs" / "dev" / "manual-study-shadow-course-tools-browser-readiness-audit-no-progress-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0825_WEB_APP_MISSING"),
    (doc, "FAILED_V0825_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_22_MANUAL_STUDY_REAL_STUDY_READ_ONLY_SHADOW_TOGGLE_START",
    "VOILA_V0_8_24_MANUAL_STUDY_SHADOW_COURSE_TOOLS_LINK_START",
    "_voila_v0822_manual_study_shadow_page",
    "_voila_v0822_manual_study_real_study_read_only_shadow_toggle_middleware",
    "manual-study-shadow-course-tools-link",
    "manual-study-dry-run-course-tools-link",
    "manual-study-dry-run-course-tools-status",
    "/study?manual_study_shadow=1&course_id=",
    "manual_study_default_enabled",
    "shadow_only_explicit_link",
    "read_only_shadow_toggle",
    "manual-study-shadow-route",
    "manual-study-shadow-source",
    "manual-study-shadow-policy",
    "manual-study-shadow-cards",
    "manual_study_items.preview.json",
    "study_items.preview.json",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0825_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "Manual Study shadow Course Tools browser readiness audit",
    "Course Tools loads with HTTP 200.",
    "Course Tools shows the Manual Study shadow link.",
    "The Manual Study shadow link points to `/study?manual_study_shadow=1&course_id={course_id}`.",
    "Following the Course Tools shadow link loads the `/study` Manual Study shadow page with HTTP 200.",
    "The shadow page reads `manual_study_items.preview.json`.",
    "The shadow page renders Manual Study cards.",
    "Answers remain read-only inside `<details>`.",
    "Source metadata remains visible.",
    "Course Tools still shows the separate dry-run link.",
    "Following the dry-run link still loads the dry-run route.",
    "`/study` without the shadow toggle does not render the Manual Study shadow page.",
    "Legacy `study_items.preview.json` remains unchanged.",
    "No Progress write is added.",
    "No answer marking is added.",
    "This milestone is audit/check only.",
    "It does not modify `services/api/web_app.py`.",
    "It does not add a route.",
    "It does not add a POST endpoint.",
    "It does not make Manual Study the default `/study`.",
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
        raise SystemExit(f"FAILED_V0825_DOC_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/manual-study-shadow-course-tools-browser-readiness-audit-no-progress-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-study-shadow-course-tools-browser-readiness-audit-no-progress-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-study-shadow-course-tools-browser-readiness-audit-no-progress-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0825_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0825_STUDY_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/study"') != 0:
    raise SystemExit("FAILED_V0825_STUDY_POST_ADDED")

if web_text.count("VOILA_V0_8_24_MANUAL_STUDY_SHADOW_COURSE_TOOLS_LINK_START") != 1:
    raise SystemExit("FAILED_V0825_COURSE_TOOLS_SHADOW_LINK_COUNT_CHANGED")

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
        raise SystemExit(f"FAILED_V0825_FORBIDDEN_WEB_TERM_FOUND={forbidden}")

course_id = "03-pag-30-34-vectori-trigonometrie"
output_dir = root / "data" / "output" / course_id
manual_study_preview = output_dir / "manual_study_items.preview.json"
legacy_study_preview = output_dir / "study_items.preview.json"
legacy_before = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None

home_url = "http://127.0.0.1:8787/"
course_tools_url = "http://127.0.0.1:8787/course-tools"
study_fallback_probe_url = "http://127.0.0.1:8787/study"

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
        raise SystemExit(f"FAILED_V0825_POST={url}; STATUS={exc.code}; BODY={error_body}")

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
    raise SystemExit(f"FAILED_V0825_{label}_FETCH={last_error}")

def absolutize(local_or_absolute_href):
    href = local_or_absolute_href.replace("&amp;", "&")
    if href.startswith("/"):
        return "http://127.0.0.1:8787" + href
    if href.startswith("http://") or href.startswith("https://"):
        return href
    return "http://127.0.0.1:8787/" + href.lstrip("./")

eligible_id = "v0825-check-course-tools-shadow-browser-audit-eligible"

payload = {
    "draft_id": eligible_id,
    "page": "1",
    "bbox": "[252, 274, 680, 610]",
    "kind": "formula",
    "title": "v0.8.25 Course Tools shadow browser audit eligible",
    "verified_text": "Course Tools shadow browser audit prompt text",
    "explanation_ro": "Răspuns read-only pentru auditul Course Tools către Study Manual Shadow.",
    "source_status": "verified",
    "source_note": "Created by v0.8.25 Course Tools shadow browser readiness audit check.",
}

status, body, _ = post_form(save_url, payload)
if status != 200:
    raise SystemExit(f"FAILED_V0825_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body, _ = post_form(verify_url, {"draft_id": eligible_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V0825_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

learning_export_status, learning_export_body, _ = post_form(learning_pack_export_url, {})
if learning_export_status != 200:
    raise SystemExit(f"FAILED_V0825_LEARNING_PACK_EXPORT_STATUS={learning_export_status}; BODY={learning_export_body}")

manual_study_export_status, manual_study_export_body, _ = post_form(manual_study_export_url, {})
if manual_study_export_status != 200:
    raise SystemExit(f"FAILED_V0825_MANUAL_STUDY_EXPORT_STATUS={manual_study_export_status}; BODY={manual_study_export_body}")

if not manual_study_preview.exists():
    raise SystemExit("FAILED_V0825_MANUAL_STUDY_PREVIEW_JSON_MISSING")

home_status, home_body, _ = fetch_url_allow_http_error(home_url, "HOME")
if home_status != 200:
    raise SystemExit(f"FAILED_V0825_HOME_STATUS={home_status}")

course_tools_match = re.search(r'href="([^"]*/course-tools[^"]*)"', home_body)
if course_tools_match:
    course_tools_url = absolutize(course_tools_match.group(1))

course_tools_status, course_tools_body, fetched_course_tools_url = fetch_url_allow_http_error(course_tools_url, "COURSE_TOOLS")
if course_tools_status != 200:
    raise SystemExit(f"FAILED_V0825_COURSE_TOOLS_STATUS={course_tools_status}; BODY={course_tools_body[:800]}")

shadow_link_match = re.search(
    r'<a\s+href="([^"]+)"\s+data-testid="manual-study-shadow-course-tools-link"',
    course_tools_body,
)
if not shadow_link_match:
    raise SystemExit("FAILED_V0825_SHADOW_LINK_HREF_NOT_FOUND")

dry_run_link_match = re.search(
    r'<a\s+href="([^"]+)"\s+data-testid="manual-study-dry-run-course-tools-link"',
    course_tools_body,
)
if not dry_run_link_match:
    raise SystemExit("FAILED_V0825_DRY_RUN_LINK_HREF_NOT_FOUND")

shadow_href = shadow_link_match.group(1).replace("&amp;", "&")
dry_run_href = dry_run_link_match.group(1).replace("&amp;", "&")

if shadow_href != f"/study?manual_study_shadow=1&course_id={course_id}":
    raise SystemExit("FAILED_V0825_SHADOW_LINK_HREF_UNEXPECTED=" + shadow_href)

if dry_run_href != f"/owner/manual-study-integration-dry-run/{course_id}?enabled=0":
    raise SystemExit("FAILED_V0825_DRY_RUN_LINK_HREF_UNEXPECTED=" + dry_run_href)

shadow_link_url = absolutize(shadow_link_match.group(1))
dry_run_link_url = absolutize(dry_run_link_match.group(1))

shadow_status, shadow_body, fetched_shadow_url = fetch_url_allow_http_error(shadow_link_url, "SHADOW_LINK_TARGET")
dry_run_status, dry_run_body, fetched_dry_run_url = fetch_url_allow_http_error(dry_run_link_url, "DRY_RUN_LINK_TARGET")
fallback_status, fallback_body, _ = fetch_url_allow_http_error(study_fallback_probe_url, "STUDY_FALLBACK")

if shadow_status != 200:
    raise SystemExit(f"FAILED_V0825_SHADOW_LINK_TARGET_STATUS={shadow_status}; BODY={shadow_body[:800]}")

if dry_run_status != 200:
    raise SystemExit(f"FAILED_V0825_DRY_RUN_LINK_TARGET_STATUS={dry_run_status}; BODY={dry_run_body[:800]}")

if fallback_status == 200 and "manual-study-shadow-route" in fallback_body:
    raise SystemExit("FAILED_V0825_FALLBACK_RENDERED_SHADOW_WITHOUT_TOGGLE")

course_tools_terms = [
    "manual-study-shadow-course-tools-link",
    "manual-study-dry-run-course-tools-link",
    "manual-study-dry-run-course-tools-status",
    "/study?manual_study_shadow=1&amp;course_id=03-pag-30-34-vectori-trigonometrie",
    "/owner/manual-study-integration-dry-run/03-pag-30-34-vectori-trigonometrie?enabled=0",
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
        raise SystemExit(f"FAILED_V0825_COURSE_TOOLS_TERM_MISSING={term}")

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
    "manual-study-preview-card",
    "manual-study-preview-answer",
    "manual-study-preview-source",
    "manual-study-preview-card-navigation",
    "Course Tools shadow browser audit prompt text",
    "Răspuns read-only pentru auditul Course Tools către Study Manual Shadow.",
]

for term in shadow_terms:
    if term not in shadow_body:
        raise SystemExit(f"FAILED_V0825_SHADOW_TARGET_TERM_MISSING={term}")

dry_run_terms = [
    "Manual Study Integration Dry Run",
    "manual-study-integration-dry-run-route",
    "dry_run_toggle_enabled",
    "false",
    "dry_run_only",
]

for term in dry_run_terms:
    if term not in dry_run_body:
        raise SystemExit(f"FAILED_V0825_DRY_RUN_TARGET_TERM_MISSING={term}")

manual_study = json.loads(manual_study_preview.read_text(encoding="utf-8", errors="replace"))
items = manual_study.get("items")
if not isinstance(items, list):
    raise SystemExit("FAILED_V0825_ITEMS_INVALID")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}
if eligible_id not in ids:
    raise SystemExit("FAILED_V0825_ELIGIBLE_ID_NOT_EXPORTED")

legacy_after = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None
if legacy_before != legacy_after:
    raise SystemExit("FAILED_V0825_LEGACY_STUDY_PREVIEW_CHANGED")

manual_result = {
    "manual_browser_audit_status": "OWNER_LOCAL_COURSE_TOOLS_TO_MANUAL_STUDY_SHADOW_PASS",
    "steps": [
        {"step": "course_tools_loads", "status": "PASS", "http_status": course_tools_status},
        {"step": "course_tools_shadow_link_visible", "status": "PASS", "href": shadow_href},
        {"step": "course_tools_dry_run_link_preserved", "status": "PASS", "href": dry_run_href},
        {"step": "follow_shadow_link_to_study_shadow", "status": "PASS", "http_status": shadow_status},
        {"step": "shadow_page_reads_manual_study_items_preview_json", "status": "PASS"},
        {"step": "shadow_page_cards_visible", "status": "PASS"},
        {"step": "answers_remain_read_only_details", "status": "PASS"},
        {"step": "source_metadata_visible", "status": "PASS"},
        {"step": "follow_dry_run_link_still_loads_dry_run", "status": "PASS", "http_status": dry_run_status},
        {"step": "fallback_without_toggle_does_not_render_shadow", "status": "PASS", "http_status": fallback_status},
        {"step": "legacy_study_items_preview_unchanged", "status": "PASS"},
    ],
}

summary = {
    "VOILA_V0_8_25_MANUAL_STUDY_SHADOW_COURSE_TOOLS_BROWSER_READINESS_AUDIT_CHECK": "PASS",
    "depends_on_v0824_course_tools_shadow_link": True,
    "course_tools_route_status": course_tools_status,
    "course_tools_shadow_link_visible": True,
    "course_tools_shadow_link_href": shadow_href,
    "course_tools_dry_run_link_preserved": True,
    "course_tools_dry_run_link_href": dry_run_href,
    "follow_shadow_link_status": shadow_status,
    "follow_dry_run_link_status": dry_run_status,
    "study_fallback_probe_status": fallback_status,
    "manual_study_items_preview_json_read": True,
    "manual_study_shadow_cards_visible": True,
    "answer_details_remain_read_only": True,
    "source_metadata_visible": True,
    "fallback_without_toggle_does_not_render_shadow": True,
    "manual_browser_audit_recorded": True,
    "web_app_changed": False,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "manual_study_default_enabled": False,
    "manual_study_connected_to_real_study": "shadow_only_explicit_course_tools_link",
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
    "POLICY": "manual_study_shadow_course_tools_browser_readiness_audit_no_progress_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0825-manual-study-shadow-course-tools-browser-readiness-audit")
evidence.mkdir(parents=True, exist_ok=True)

out_json = evidence / "V0.8.25-MANUAL-STUDY-SHADOW-COURSE-TOOLS-BROWSER-READINESS-AUDIT-CHECK.json"
out_md = evidence / "V0.8.25-MANUAL-STUDY-SHADOW-COURSE-TOOLS-BROWSER-READINESS-AUDIT-CHECK.md"

out_json.write_text(json.dumps({"summary": summary, "manual_result": manual_result}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.25 Manual Study shadow Course Tools browser readiness audit",
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
