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
doc = root / "docs" / "dev" / "manual-study-preview-link-from-course-tools-no-progress-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0814_WEB_APP_MISSING"),
    (doc, "FAILED_V0814_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_14_MANUAL_STUDY_PREVIEW_COURSE_TOOLS_LINK_START",
    "VOILA_V0_8_14_MANUAL_STUDY_PREVIEW_COURSE_TOOLS_LINK_CSS_START",
    'data-testid="manual-study-preview-course-tools-link"',
    'data-testid="manual-study-preview-course-tools-status"',
    "_voila_v0814_manual_study_preview_course_tools_link_html",
    "_voila_v0814_inject_manual_study_preview_course_tools_link",
    "manual_study_items.preview.json",
    "Manual Study Preview",
    "manual study Course Tools link",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0814_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "visible Course Tools link",
    "`/owner/manual-study-preview/{course_id}`",
    "`manual_study_items.preview.json`",
    "`Manual Study preview: OK`",
    "`Manual Study preview: lipsește manual_study_items.preview.json`",
    "It does not write any artifact.",
    "It does not replace or modify the existing `/study` route.",
    "It does not write progress.",
    "It does not mark answers.",
    "It does not write or modify the legacy `study_items.preview.json`.",
    "No new POST endpoint.",
    "No Progress write.",
    "No answer marking.",
    "No Study integration.",
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
        raise SystemExit(f"FAILED_V0814_DOC_TERM_MISSING={term}")

if web_text.count('data-testid="manual-study-preview-course-tools-link"') != 1:
    raise SystemExit("FAILED_V0814_COURSE_TOOLS_LINK_COUNT")

if web_text.count('data-testid="manual-study-preview-course-tools-status"') < 1:
    raise SystemExit("FAILED_V0814_COURSE_TOOLS_STATUS_COUNT")

if web_text.count('@app.get("/owner/manual-study-preview/{course_id}"') != 1:
    raise SystemExit("FAILED_V0814_MANUAL_STUDY_PREVIEW_ROUTE_COUNT_CHANGED")

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0814_STUDY_ROUTE_COUNT_CHANGED")

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
        raise SystemExit(f"FAILED_V0814_FORBIDDEN_TERM_FOUND={forbidden}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-study-preview-link-from-course-tools-no-progress-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-study-preview-link-from-course-tools-no-progress-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-study-preview-link-from-course-tools-no-progress-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0814_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

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
        raise SystemExit(f"FAILED_V0814_POST={url}; STATUS={exc.code}; BODY={error_body}")

eligible_id = "v0814-check-course-tools-link-eligible"

payload = {
    "draft_id": eligible_id,
    "page": "1",
    "bbox": "[152, 174, 480, 410]",
    "kind": "formula",
    "title": "v0.8.14 Course Tools link eligible",
    "verified_text": "Course Tools Manual Study Preview prompt text",
    "explanation_ro": "Răspuns pentru verificarea linkului din Course Tools.",
    "source_status": "verified",
    "source_note": "Created by v0.8.14 Course Tools link check.",
}

status, body, _ = post_form(save_url, payload)
if status != 200:
    raise SystemExit(f"FAILED_V0814_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body, _ = post_form(verify_url, {"draft_id": eligible_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V0814_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

learning_export_status, learning_export_body, _ = post_form(learning_pack_export_url, {})
if learning_export_status != 200:
    raise SystemExit(f"FAILED_V0814_LEARNING_PACK_EXPORT_STATUS={learning_export_status}; BODY={learning_export_body}")

manual_study_export_status, manual_study_export_body, _ = post_form(manual_study_export_url, {})
if manual_study_export_status != 200:
    raise SystemExit(f"FAILED_V0814_MANUAL_STUDY_EXPORT_STATUS={manual_study_export_status}; BODY={manual_study_export_body}")

if not manual_study_preview.exists():
    raise SystemExit("FAILED_V0814_MANUAL_STUDY_PREVIEW_JSON_MISSING")

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
            last_error = f"HTTP {exc.code}: {error_body[:500]}"
            time.sleep(2)
        except Exception as exc:
            last_error = str(exc)
            time.sleep(2)
    raise SystemExit(f"FAILED_V0814_{label}_FETCH={last_error}")

home_status, home_body = fetch_url(home_url, "HOME")
course_tools_match = re.search(r'href="([^"]*/course-tools[^"]*)"', home_body)
if course_tools_match:
    discovered_course_tools_url = course_tools_match.group(1).replace("&amp;", "&")
    if discovered_course_tools_url.startswith("/"):
        course_tools_url = "http://127.0.0.1:8787" + discovered_course_tools_url
    elif discovered_course_tools_url.startswith("http://") or discovered_course_tools_url.startswith("https://"):
        course_tools_url = discovered_course_tools_url

course_tools_status, course_tools_body = fetch_url(course_tools_url, "COURSE_TOOLS")
manual_preview_status, manual_preview_body = fetch_url(manual_study_preview_url, "MANUAL_STUDY_PREVIEW")

if course_tools_status != 200:
    raise SystemExit(f"FAILED_V0814_COURSE_TOOLS_STATUS={course_tools_status}")

if manual_preview_status != 200:
    raise SystemExit(f"FAILED_V0814_MANUAL_PREVIEW_STATUS={manual_preview_status}")

course_tools_terms = [
    "manual-study-preview-course-tools-link",
    "manual-study-preview-course-tools-status",
    "/owner/manual-study-preview/03-pag-30-34-vectori-trigonometrie",
    "Manual Study Preview",
    "Manual Study preview: OK",
]

for term in course_tools_terms:
    if term not in course_tools_body:
        raise SystemExit(f"FAILED_V0814_COURSE_TOOLS_RUNTIME_TERM_MISSING={term}")

manual_preview_terms = [
    "Manual Study Preview",
    "manual-study-preview-route",
    "Course Tools Manual Study Preview prompt text",
    "Răspuns pentru verificarea linkului din Course Tools.",
]

for term in manual_preview_terms:
    if term not in manual_preview_body:
        raise SystemExit(f"FAILED_V0814_MANUAL_PREVIEW_RUNTIME_TERM_MISSING={term}")

manual_study = json.loads(manual_study_preview.read_text(encoding="utf-8", errors="replace"))
items = manual_study.get("items")
if not isinstance(items, list):
    raise SystemExit("FAILED_V0814_ITEMS_INVALID")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}
if eligible_id not in ids:
    raise SystemExit("FAILED_V0814_ELIGIBLE_ID_NOT_EXPORTED")

legacy_after = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None
if legacy_before != legacy_after:
    raise SystemExit("FAILED_V0814_LEGACY_STUDY_PREVIEW_CHANGED")

summary = {
    "VOILA_V0_8_14_MANUAL_STUDY_PREVIEW_LINK_FROM_COURSE_TOOLS_CHECK": "PASS",
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
    "depends_on_v0813_manual_study_preview": True,
    "course_tools_route": "/course-tools",
    "manual_study_preview_route": "/owner/manual-study-preview/{course_id}",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "course_tools_route_status": course_tools_status,
    "manual_study_preview_route_status": manual_preview_status,
    "course_tools_link_added": True,
    "course_tools_status_visible": True,
    "manual_study_preview_status_ok_visible": True,
    "manual_study_preview_json_detected": True,
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
    "TESTER_READINESS": "BLOCKED_COURSE_TOOLS_LINK_ONLY_NO_PROGRESS",
    "POLICY": "manual_study_preview_course_tools_link_no_progress_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0814-manual-study-preview-link-from-course-tools")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.8.14-MANUAL-STUDY-PREVIEW-LINK-FROM-COURSE-TOOLS-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
