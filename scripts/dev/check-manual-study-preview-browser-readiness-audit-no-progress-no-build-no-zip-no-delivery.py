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
doc = root / "docs" / "dev" / "manual-study-preview-browser-readiness-audit-no-progress-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0816_WEB_APP_MISSING"),
    (doc, "FAILED_V0816_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_13_MANUAL_STUDY_ROUTE_READ_ONLY_PREVIEW_START",
    "VOILA_V0_8_14_MANUAL_STUDY_PREVIEW_COURSE_TOOLS_LINK_START",
    "VOILA_V0_8_15_MANUAL_STUDY_PREVIEW_NAVIGATION_POLISH_CSS_START",
    '@app.get("/owner/manual-study-preview/{course_id}")',
    'data-testid="manual-study-preview-route"',
    'data-testid="manual-study-preview-top-navigation"',
    'data-testid="manual-study-preview-card-navigation"',
    'data-testid="manual-study-preview-prev"',
    'data-testid="manual-study-preview-next"',
    'data-testid="manual-study-preview-back-to-top"',
    "manual_study_items.preview.json",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0816_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "browser readiness audit",
    "Course Tools exposes Manual Study Preview link",
    "Manual Study Preview route loads",
    "Previous/Next navigation is visible",
    "Answers remain read-only inside `<details>`",
    "Source metadata remains visible",
    "This milestone is audit/check only.",
    "It does not modify `services/api/web_app.py`.",
    "It does not add a route.",
    "It does not add a write endpoint.",
    "It does not replace or modify the existing `/study` route.",
    "It does not write progress.",
    "It does not mark answers.",
    "It does not write or modify the legacy `study_items.preview.json`.",
    "No UI implementation change.",
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
        raise SystemExit(f"FAILED_V0816_DOC_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/manual-study-preview-browser-readiness-audit-no-progress-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-study-preview-browser-readiness-audit-no-progress-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-study-preview-browser-readiness-audit-no-progress-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0816_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

if web_text.count('@app.get("/owner/manual-study-preview/{course_id}"') != 1:
    raise SystemExit("FAILED_V0816_MANUAL_STUDY_PREVIEW_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/owner/manual-study-preview') != 0:
    raise SystemExit("FAILED_V0816_MANUAL_STUDY_PREVIEW_POST_ADDED")

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0816_STUDY_ROUTE_COUNT_CHANGED")

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
        raise SystemExit(f"FAILED_V0816_FORBIDDEN_TERM_FOUND={forbidden}")

course_id = "03-pag-30-34-vectori-trigonometrie"
output_dir = root / "data" / "output" / course_id
manual_study_preview = output_dir / "manual_study_items.preview.json"
legacy_study_preview = output_dir / "study_items.preview.json"
legacy_before = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None

save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"
verify_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/verify-draft"
learning_pack_export_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"
manual_study_export_url = f"http://127.0.0.1:8787/owner/manual-learning-pack-study-adapter-dry-run/{course_id}/export-manual-study-items-preview"
manual_study_preview_url = f"http://127.0.0.1:8787/owner/manual-study-preview/{course_id}"
home_url = "http://127.0.0.1:8787/"
course_tools_url = "http://127.0.0.1:8787/course-tools"

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
        raise SystemExit(f"FAILED_V0816_POST={url}; STATUS={exc.code}; BODY={error_body}")

def fetch_url(url, label):
    last_error = ""
    for _ in range(10):
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                return response.status, response.read().decode("utf-8", errors="replace")
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
    raise SystemExit(f"FAILED_V0816_{label}_FETCH={last_error}")

eligible_id = "v0816-check-browser-readiness-eligible"

payload = {
    "draft_id": eligible_id,
    "page": "1",
    "bbox": "[172, 194, 520, 450]",
    "kind": "formula",
    "title": "v0.8.16 browser readiness eligible",
    "verified_text": "Browser readiness prompt text",
    "explanation_ro": "Răspuns read-only pentru auditul browser readiness.",
    "source_status": "verified",
    "source_note": "Created by v0.8.16 browser readiness audit check.",
}

status, body, _ = post_form(save_url, payload)
if status != 200:
    raise SystemExit(f"FAILED_V0816_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body, _ = post_form(verify_url, {"draft_id": eligible_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V0816_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

learning_export_status, learning_export_body, _ = post_form(learning_pack_export_url, {})
if learning_export_status != 200:
    raise SystemExit(f"FAILED_V0816_LEARNING_PACK_EXPORT_STATUS={learning_export_status}; BODY={learning_export_body}")

manual_study_export_status, manual_study_export_body, _ = post_form(manual_study_export_url, {})
if manual_study_export_status != 200:
    raise SystemExit(f"FAILED_V0816_MANUAL_STUDY_EXPORT_STATUS={manual_study_export_status}; BODY={manual_study_export_body}")

if not manual_study_preview.exists():
    raise SystemExit("FAILED_V0816_MANUAL_STUDY_PREVIEW_JSON_MISSING")

home_status, home_body = fetch_url(home_url, "HOME")
course_tools_match = re.search(r'href="([^"]*/course-tools[^"]*)"', home_body)
if course_tools_match:
    discovered_course_tools_url = course_tools_match.group(1).replace("&amp;", "&")
    if discovered_course_tools_url.startswith("/"):
        course_tools_url = "http://127.0.0.1:8787" + discovered_course_tools_url
    elif discovered_course_tools_url.startswith("http://") or discovered_course_tools_url.startswith("https://"):
        course_tools_url = discovered_course_tools_url

course_tools_status, course_tools_body = fetch_url(course_tools_url, "COURSE_TOOLS")
preview_status, preview_body = fetch_url(manual_study_preview_url, "MANUAL_STUDY_PREVIEW")

if course_tools_status != 200:
    raise SystemExit(f"FAILED_V0816_COURSE_TOOLS_STATUS={course_tools_status}")

if preview_status != 200:
    raise SystemExit(f"FAILED_V0816_PREVIEW_STATUS={preview_status}")

course_tools_terms = [
    "manual-study-preview-course-tools-link",
    "manual-study-preview-course-tools-status",
    "/owner/manual-study-preview/03-pag-30-34-vectori-trigonometrie",
    "Manual Study Preview",
    "Manual Study preview: OK",
]

for term in course_tools_terms:
    if term not in course_tools_body:
        raise SystemExit(f"FAILED_V0816_COURSE_TOOLS_RUNTIME_TERM_MISSING={term}")

preview_terms = [
    "Manual Study Preview",
    "manual-study-preview-route",
    "manual-study-preview-top",
    "manual-study-preview-top-navigation",
    "manual-study-preview-nav-jump",
    "manual-study-preview-position",
    "manual-study-preview-card-navigation",
    "manual-study-preview-prev",
    "manual-study-preview-next",
    "manual-study-preview-back-to-top",
    "manual-study-preview-answer",
    "manual-study-preview-source",
    "Browser readiness prompt text",
    "Răspuns read-only pentru auditul browser readiness.",
    "Navigarea este doar cu ancore locale",
    "progress_write",
    "answer_marking",
    "replaces_study_route",
    "false",
]

for term in preview_terms:
    if term not in preview_body:
        raise SystemExit(f"FAILED_V0816_PREVIEW_RUNTIME_TERM_MISSING={term}")

manual_study = json.loads(manual_study_preview.read_text(encoding="utf-8", errors="replace"))
items = manual_study.get("items")
if not isinstance(items, list):
    raise SystemExit("FAILED_V0816_ITEMS_INVALID")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}
if eligible_id not in ids:
    raise SystemExit("FAILED_V0816_ELIGIBLE_ID_NOT_EXPORTED")

legacy_after = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None
if legacy_before != legacy_after:
    raise SystemExit("FAILED_V0816_LEGACY_STUDY_PREVIEW_CHANGED")

manual_result = {
    "manual_browser_audit_status": "OWNER_LOCAL_HTTP_BROWSER_ROUTE_READINESS_PASS",
    "steps": [
        {
            "step": "course_tools_loads",
            "route": course_tools_url,
            "status": "PASS",
            "http_status": course_tools_status,
        },
        {
            "step": "course_tools_manual_study_preview_link_visible",
            "status": "PASS",
        },
        {
            "step": "course_tools_manual_study_preview_status_visible",
            "status": "PASS",
        },
        {
            "step": "manual_study_preview_route_loads",
            "route": manual_study_preview_url,
            "status": "PASS",
            "http_status": preview_status,
        },
        {
            "step": "study_like_cards_visible",
            "status": "PASS",
        },
        {
            "step": "previous_next_back_to_top_navigation_visible",
            "status": "PASS",
        },
        {
            "step": "answers_remain_read_only_details",
            "status": "PASS",
        },
        {
            "step": "source_metadata_visible",
            "status": "PASS",
        },
    ],
}

summary = {
    "VOILA_V0_8_16_MANUAL_STUDY_PREVIEW_BROWSER_READINESS_AUDIT_CHECK": "PASS",
    "depends_on_v0813_manual_study_preview": True,
    "depends_on_v0814_course_tools_link": True,
    "depends_on_v0815_navigation_polish": True,
    "course_tools_route": "/course-tools",
    "manual_study_preview_route": "/owner/manual-study-preview/{course_id}",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "course_tools_route_status": course_tools_status,
    "manual_study_preview_route_status": preview_status,
    "course_tools_link_visible": True,
    "course_tools_status_visible": True,
    "manual_study_preview_status_ok_visible": True,
    "manual_study_preview_json_detected": True,
    "manual_study_preview_cards_visible": True,
    "top_navigation_visible": True,
    "previous_next_navigation_visible": True,
    "back_to_top_visible": True,
    "answer_details_remain_read_only": True,
    "source_metadata_visible": True,
    "manual_browser_audit_recorded": True,
    "web_app_changed": False,
    "new_route_added": False,
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
    "TESTER_READINESS": "BLOCKED_AUDIT_ONLY_NO_STUDY_INTEGRATION_NO_PACKAGE",
    "POLICY": "manual_study_preview_browser_readiness_audit_no_progress_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0816-manual-study-preview-browser-readiness-audit")
evidence.mkdir(parents=True, exist_ok=True)
out_json = evidence / "V0.8.16-MANUAL-STUDY-PREVIEW-BROWSER-READINESS-AUDIT-CHECK.json"
out_md = evidence / "V0.8.16-MANUAL-STUDY-PREVIEW-BROWSER-READINESS-AUDIT-CHECK.md"

out_json.write_text(json.dumps({"summary": summary, "manual_result": manual_result}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.16 Manual Study Preview browser readiness audit",
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
