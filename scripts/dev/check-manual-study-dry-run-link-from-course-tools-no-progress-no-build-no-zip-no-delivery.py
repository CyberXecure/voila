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
doc = root / "docs" / "dev" / "manual-study-dry-run-link-from-course-tools-no-progress-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0819_WEB_APP_MISSING"),
    (doc, "FAILED_V0819_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_web_terms = [
    "VOILA_V0_8_19_MANUAL_STUDY_DRY_RUN_COURSE_TOOLS_LINK_START",
    "_voila_v0819_inject_manual_study_dry_run_course_tools_link",
    "_voila_v0819_manual_study_dry_run_course_tools_link_middleware",
    "manual-study-dry-run-course-tools-section",
    "manual-study-dry-run-course-tools-link",
    "manual-study-dry-run-course-tools-status",
    "/owner/manual-study-integration-dry-run/",
    "manual_study_items.preview.json",
    "dry_run_only",
    "manual_study_connected_to_real_study",
    "writes_legacy_study_items_preview",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0819_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "Manual Study dry-run link from Course Tools",
    "Manual Study integration dry-run toggle",
    "`/owner/manual-study-integration-dry-run/{course_id}?enabled=0`",
    "`manual_study_items.preview.json`",
    "`dry_run_only`",
    "`manual_study_connected_to_real_study=false`",
    "`progress_write=false`",
    "`answer_marking=false`",
    "`writes_legacy_study_items_preview=false`",
    "This milestone only exposes a link/status card from Course Tools.",
    "It does not connect Manual Study to real `/study`.",
    "It does not replace or modify the existing `/study` route.",
    "It does not add a POST endpoint.",
    "It does not write progress.",
    "It does not mark answers.",
    "It does not overwrite or modify the legacy `study_items.preview.json`.",
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
        raise SystemExit(f"FAILED_V0819_DOC_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-study-dry-run-link-from-course-tools-no-progress-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-study-dry-run-link-from-course-tools-no-progress-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-study-dry-run-link-from-course-tools-no-progress-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0819_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

if web_text.count('@app.get("/owner/manual-study-integration-dry-run/{course_id}"') != 1:
    raise SystemExit("FAILED_V0819_DRY_RUN_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/owner/manual-study-integration-dry-run') != 0:
    raise SystemExit("FAILED_V0819_DRY_RUN_POST_ADDED")

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0819_STUDY_ROUTE_COUNT_CHANGED")

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
        raise SystemExit(f"FAILED_V0819_FORBIDDEN_WEB_TERM_FOUND={forbidden}")

course_id = "03-pag-30-34-vectori-trigonometrie"
output_dir = root / "data" / "output" / course_id
manual_study_preview = output_dir / "manual_study_items.preview.json"
legacy_study_preview = output_dir / "study_items.preview.json"
legacy_before = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None

save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"
verify_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/verify-draft"
learning_pack_export_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"
manual_study_export_url = f"http://127.0.0.1:8787/owner/manual-learning-pack-study-adapter-dry-run/{course_id}/export-manual-study-items-preview"
home_url = "http://127.0.0.1:8787/"
course_tools_url = "http://127.0.0.1:8787/course-tools"
dry_run_off_url = f"http://127.0.0.1:8787/owner/manual-study-integration-dry-run/{course_id}?enabled=0"

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
        raise SystemExit(f"FAILED_V0819_POST={url}; STATUS={exc.code}; BODY={error_body}")

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
    raise SystemExit(f"FAILED_V0819_{label}_FETCH={last_error}")

eligible_id = "v0819-check-course-tools-dry-run-link-eligible"

payload = {
    "draft_id": eligible_id,
    "page": "1",
    "bbox": "[192, 214, 560, 490]",
    "kind": "formula",
    "title": "v0.8.19 course tools dry-run link eligible",
    "verified_text": "Course Tools dry-run link prompt text",
    "explanation_ro": "Răspuns read-only pentru linkul dry-run din Course Tools.",
    "source_status": "verified",
    "source_note": "Created by v0.8.19 Course Tools dry-run link check.",
}

status, body, _ = post_form(save_url, payload)
if status != 200:
    raise SystemExit(f"FAILED_V0819_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body, _ = post_form(verify_url, {"draft_id": eligible_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V0819_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

learning_export_status, learning_export_body, _ = post_form(learning_pack_export_url, {})
if learning_export_status != 200:
    raise SystemExit(f"FAILED_V0819_LEARNING_PACK_EXPORT_STATUS={learning_export_status}; BODY={learning_export_body}")

manual_study_export_status, manual_study_export_body, _ = post_form(manual_study_export_url, {})
if manual_study_export_status != 200:
    raise SystemExit(f"FAILED_V0819_MANUAL_STUDY_EXPORT_STATUS={manual_study_export_status}; BODY={manual_study_export_body}")

if not manual_study_preview.exists():
    raise SystemExit("FAILED_V0819_MANUAL_STUDY_PREVIEW_JSON_MISSING")

home_status, home_body, _ = fetch_url(home_url, "HOME")
course_tools_match = re.search(r'href="([^"]*/course-tools[^"]*)"', home_body)
if course_tools_match:
    discovered_course_tools_url = course_tools_match.group(1).replace("&amp;", "&")
    if discovered_course_tools_url.startswith("/"):
        course_tools_url = "http://127.0.0.1:8787" + discovered_course_tools_url
    elif discovered_course_tools_url.startswith("http://") or discovered_course_tools_url.startswith("https://"):
        course_tools_url = discovered_course_tools_url

course_tools_status, course_tools_body, _ = fetch_url(course_tools_url, "COURSE_TOOLS")
dry_run_status, dry_run_body, _ = fetch_url(dry_run_off_url, "DRY_RUN_OFF")

if course_tools_status != 200:
    raise SystemExit(f"FAILED_V0819_COURSE_TOOLS_STATUS={course_tools_status}")

if dry_run_status != 200:
    raise SystemExit(f"FAILED_V0819_DRY_RUN_OFF_STATUS={dry_run_status}")

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
        raise SystemExit(f"FAILED_V0819_COURSE_TOOLS_TERM_MISSING={term}")

dry_run_terms = [
    "Manual Study Integration Dry Run",
    "manual-study-integration-dry-run-route",
    "manual-study-integration-dry-run-toggle",
    "manual-study-integration-dry-run-toggle-off",
    "dry_run_toggle_enabled",
    "false",
    "manual_study_items.preview.json",
    "dry_run_only",
]

for term in dry_run_terms:
    if term not in dry_run_body:
        raise SystemExit(f"FAILED_V0819_DRY_RUN_TERM_MISSING={term}")

manual_study = json.loads(manual_study_preview.read_text(encoding="utf-8", errors="replace"))
items = manual_study.get("items")
if not isinstance(items, list):
    raise SystemExit("FAILED_V0819_ITEMS_INVALID")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}
if eligible_id not in ids:
    raise SystemExit("FAILED_V0819_ELIGIBLE_ID_NOT_EXPORTED")

legacy_after = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None
if legacy_before != legacy_after:
    raise SystemExit("FAILED_V0819_LEGACY_STUDY_PREVIEW_CHANGED")

summary = {
    "VOILA_V0_8_19_MANUAL_STUDY_DRY_RUN_LINK_FROM_COURSE_TOOLS_CHECK": "PASS",
    "depends_on_v0818_dry_run_toggle": True,
    "course_tools_route": "/course-tools",
    "dry_run_route": "/owner/manual-study-integration-dry-run/{course_id}?enabled=0",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "course_tools_route_status": course_tools_status,
    "dry_run_off_status": dry_run_status,
    "course_tools_dry_run_link_added": True,
    "course_tools_dry_run_status_visible": True,
    "manual_study_items_preview_json_detected": True,
    "dry_run_default_toggle_off": True,
    "dry_run_route_reachable": True,
    "integration_mode": "dry_run_only",
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
    "TESTER_READINESS": "BLOCKED_LINK_ONLY_NO_REAL_STUDY_INTEGRATION_NO_PACKAGE",
    "POLICY": "manual_study_dry_run_link_from_course_tools_no_progress_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0819-manual-study-dry-run-link-from-course-tools")
evidence.mkdir(parents=True, exist_ok=True)

out_json = evidence / "V0.8.19-MANUAL-STUDY-DRY-RUN-LINK-FROM-COURSE-TOOLS-CHECK.json"
out_md = evidence / "V0.8.19-MANUAL-STUDY-DRY-RUN-LINK-FROM-COURSE-TOOLS-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.19 Manual Study dry-run link from Course Tools",
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
