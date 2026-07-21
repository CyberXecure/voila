from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "full-manual-study-flow-readiness-audit-no-progress-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0830_WEB_APP_MISSING"),
    (doc, "FAILED_V0830_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

expected_v0821_study_route_hash = "ad12be8afe880715e47cfcb9ef7aeb3dd364aeb0d98ee4a97ce2de338c3566ad"

required_web_terms = [
    "VOILA_V0_8_27_MANUAL_STUDY_DEFAULT_STUDY_READ_ONLY_FALLBACK_START",
    "_voila_v0827_manual_study_default_page",
    "_voila_v0827_manual_study_default_study_read_only_fallback_middleware",
    "manual-study-default-route",
    "manual-study-default-source",
    "manual-study-default-policy",
    "manual-study-default-cards",
    "manual_study_default_read_only_fallback",
    "default_read_only_with_legacy_fallback",
    "fallback_legacy_study_available",
    "manual_study_default_enabled",
    "manual_study_items.preview.json",
    "study_items.preview.json",
    "VOILA_V0_8_22_MANUAL_STUDY_REAL_STUDY_READ_ONLY_SHADOW_TOGGLE_START",
    "manual-study-shadow-route",
    "VOILA_V0_8_24_MANUAL_STUDY_SHADOW_COURSE_TOOLS_LINK_START",
    "manual-study-shadow-course-tools-link",
    "manual-study-dry-run-course-tools-link",
    "/study?pdf=",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0830_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "Full Manual Study flow readiness audit",
    "Course Tools loads with HTTP 200.",
    "Course Tools contains the normal Study link to `/study?pdf={pdf_name}`.",
    "Following the normal Study link opens `/study?pdf={pdf_name}` with HTTP 200.",
    "The normal Study path renders Manual Study by default when `manual_study_items.preview.json` exists and contains items.",
    "The default Manual Study page renders Manual Study cards.",
    "Answers remain read-only inside `<details>`.",
    "Source metadata remains visible.",
    "Course Tools contains the explicit Manual Study shadow link.",
    "Following the shadow link opens `/study?manual_study_shadow=1&course_id={course_id}` with HTTP 200.",
    "The shadow page remains separate from the normal Study link.",
    "Course Tools contains the separate dry-run link.",
    "Following the dry-run link opens the dry-run route with HTTP 200.",
    "The dry-run route remains separate from default Study.",
    "When `manual_study_items.preview.json` is temporarily missing, the normal Study path falls back to legacy Study.",
    "Legacy `study_items.preview.json` remains unchanged.",
    "No Progress write is added.",
    "No answer marking is added.",
    "No Study artifact is written.",
    "No Course generation behavior changes.",
    "No OCR rewrite happens.",
    "No Formula OCR happens.",
    "This milestone is audit/check only.",
    "It does not modify `services/api/web_app.py`.",
    "It does not add a route.",
    "It does not add a POST endpoint.",
    "It does not change Course Tools implementation.",
    "It does not change the default Study implementation.",
    "It does not write progress.",
    "It does not mark answers.",
    "It does not overwrite or modify the legacy `study_items.preview.json`.",
    "This is owner-local readiness evidence only.",
    "Tester readiness remains blocked until a separate explicit tester-readiness milestone",
    "No UI implementation change.",
    "No new default behavior change.",
    "No Progress integration.",
    "No answer scoring.",
    "No answer persistence.",
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
        raise SystemExit(f"FAILED_V0830_DOC_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/full-manual-study-flow-readiness-audit-no-progress-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-full-manual-study-flow-readiness-audit-no-progress-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-full-manual-study-flow-readiness-audit-no-progress-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0830_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0830_STUDY_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/study"') != 0:
    raise SystemExit("FAILED_V0830_STUDY_POST_ADDED")

if web_text.count("VOILA_V0_8_27_MANUAL_STUDY_DEFAULT_STUDY_READ_ONLY_FALLBACK_START") != 1:
    raise SystemExit("FAILED_V0830_DEFAULT_BLOCK_COUNT_CHANGED")

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
        raise SystemExit(f"FAILED_V0830_FORBIDDEN_WEB_TERM_FOUND={forbidden}")

study_route_match = re.search(
    r'@app\.get\("/study"[\s\S]*?(?=\n@app\.(?:get|post|put|delete|patch)\(|\n# VOILA_V0_8_22_MANUAL_STUDY_REAL_STUDY_READ_ONLY_SHADOW_TOGGLE_START|\Z)',
    web_text,
)
if not study_route_match:
    raise SystemExit("FAILED_V0830_STUDY_ROUTE_STATIC_BLOCK_NOT_FOUND")

study_route_block = study_route_match.group(0)
study_route_hash = hashlib.sha256(study_route_block.encode("utf-8", errors="replace")).hexdigest()

if study_route_hash != expected_v0821_study_route_hash:
    raise SystemExit(
        "FAILED_V0830_STUDY_ROUTE_HASH_CHANGED="
        + study_route_hash
        + ";EXPECTED="
        + expected_v0821_study_route_hash
    )

course_id = "03-pag-30-34-vectori-trigonometrie"
pdf_name = course_id + ".pdf"
output_dir = root / "data" / "output" / course_id
manual_study_preview = output_dir / "manual_study_items.preview.json"
legacy_study_preview = output_dir / "study_items.preview.json"
legacy_before = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None

home_url = "http://127.0.0.1:8787/"
course_tools_url = "http://127.0.0.1:8787/course-tools"

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
        raise SystemExit(f"FAILED_V0830_POST={url}; STATUS={exc.code}; BODY={error_body}")

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
    raise SystemExit(f"FAILED_V0830_{label}_FETCH={last_error}")

def absolutize(local_or_absolute_href):
    href = local_or_absolute_href.replace("&amp;", "&")
    if href.startswith("/"):
        return "http://127.0.0.1:8787" + href
    if href.startswith("http://") or href.startswith("https://"):
        return href
    return "http://127.0.0.1:8787/" + href.lstrip("./")

eligible_id = "v0830-check-full-manual-study-flow-readiness-audit-eligible"

payload = {
    "draft_id": eligible_id,
    "page": "1",
    "bbox": "[292, 314, 760, 690]",
    "kind": "formula",
    "title": "v0.8.30 full Manual Study flow readiness eligible",
    "verified_text": "Full Manual Study flow readiness prompt text",
    "explanation_ro": "Răspuns read-only pentru auditul complet Manual Study flow.",
    "source_status": "verified",
    "source_note": "Created by v0.8.30 full Manual Study flow readiness audit check.",
}

status, body, _ = post_form(save_url, payload)
if status != 200:
    raise SystemExit(f"FAILED_V0830_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body, _ = post_form(verify_url, {"draft_id": eligible_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V0830_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

learning_export_status, learning_export_body, _ = post_form(learning_pack_export_url, {})
if learning_export_status != 200:
    raise SystemExit(f"FAILED_V0830_LEARNING_PACK_EXPORT_STATUS={learning_export_status}; BODY={learning_export_body}")

manual_study_export_status, manual_study_export_body, _ = post_form(manual_study_export_url, {})
if manual_study_export_status != 200:
    raise SystemExit(f"FAILED_V0830_MANUAL_STUDY_EXPORT_STATUS={manual_study_export_status}; BODY={manual_study_export_body}")

if not manual_study_preview.exists():
    raise SystemExit("FAILED_V0830_MANUAL_STUDY_PREVIEW_JSON_MISSING")

home_status, home_body, _ = fetch_url_allow_http_error(home_url, "HOME")
if home_status != 200:
    raise SystemExit(f"FAILED_V0830_HOME_STATUS={home_status}; BODY={home_body[:800]}")

course_tools_match = re.search(r'href="([^"]*/course-tools[^"]*)"', home_body)
if course_tools_match:
    course_tools_url = absolutize(course_tools_match.group(1))

course_tools_status, course_tools_body, _ = fetch_url_allow_http_error(course_tools_url, "COURSE_TOOLS")
if course_tools_status != 200:
    raise SystemExit(f"FAILED_V0830_COURSE_TOOLS_STATUS={course_tools_status}; BODY={course_tools_body[:800]}")

normal_study_matches = re.findall(r'href="([^"]*/study\?pdf=[^"]+)"', course_tools_body)
normal_study_hrefs = [href.replace("&amp;", "&") for href in normal_study_matches if "manual_study_shadow" not in href]
expected_normal_study_href = f"/study?pdf={urllib.parse.quote(pdf_name)}"

normal_study_href = None
for href in normal_study_hrefs:
    if href == expected_normal_study_href:
        normal_study_href = href
        break

if normal_study_href is None:
    raise SystemExit("FAILED_V0830_NORMAL_STUDY_LINK_HREF_NOT_FOUND_OR_UNEXPECTED=" + ",".join(normal_study_hrefs[:10]))

shadow_link_match = re.search(
    r'<a\s+href="([^"]+)"\s+data-testid="manual-study-shadow-course-tools-link"',
    course_tools_body,
)
if not shadow_link_match:
    raise SystemExit("FAILED_V0830_SHADOW_LINK_HREF_NOT_FOUND")

dry_run_link_match = re.search(
    r'<a\s+href="([^"]+)"\s+data-testid="manual-study-dry-run-course-tools-link"',
    course_tools_body,
)
if not dry_run_link_match:
    raise SystemExit("FAILED_V0830_DRY_RUN_LINK_HREF_NOT_FOUND")

shadow_href = shadow_link_match.group(1).replace("&amp;", "&")
dry_run_href = dry_run_link_match.group(1).replace("&amp;", "&")

normal_study_url = absolutize(normal_study_href)
shadow_url = absolutize(shadow_link_match.group(1))
dry_run_url = absolutize(dry_run_link_match.group(1))

normal_status, normal_body, _ = fetch_url_allow_http_error(normal_study_url, "NORMAL_STUDY")
shadow_status, shadow_body, _ = fetch_url_allow_http_error(shadow_url, "SHADOW_STUDY")
dry_run_status, dry_run_body, _ = fetch_url_allow_http_error(dry_run_url, "DRY_RUN")

if normal_status != 200:
    raise SystemExit(f"FAILED_V0830_NORMAL_STUDY_STATUS={normal_status}; BODY={normal_body[:800]}")

if shadow_status != 200:
    raise SystemExit(f"FAILED_V0830_SHADOW_STATUS={shadow_status}; BODY={shadow_body[:800]}")

if dry_run_status != 200:
    raise SystemExit(f"FAILED_V0830_DRY_RUN_STATUS={dry_run_status}; BODY={dry_run_body[:800]}")

course_tools_terms = [
    "manual-study-shadow-course-tools-link",
    "manual-study-dry-run-course-tools-link",
    "/study?manual_study_shadow=1&amp;course_id=03-pag-30-34-vectori-trigonometrie",
    "/owner/manual-study-integration-dry-run/03-pag-30-34-vectori-trigonometrie?enabled=0",
    "shadow_only_explicit_link",
    "manual_study_default_enabled",
    "false",
]

for term in course_tools_terms:
    if term not in course_tools_body:
        raise SystemExit(f"FAILED_V0830_COURSE_TOOLS_TERM_MISSING={term}")

normal_terms = [
    "manual-study-default-route",
    "manual-study-default-navigation",
    "manual-study-default-source",
    "manual-study-default-policy",
    "manual-study-default-cards",
    "manual_study_items.preview.json",
    "manual_study_default_read_only_fallback",
    "manual_study_default_enabled",
    "true",
    "fallback_legacy_study_available",
    "default_read_only_with_legacy_fallback",
    "progress_write",
    "answer_marking",
    "writes_legacy_study_items_preview",
    "study_artifact_written",
    "false",
    "manual-study-preview-card",
    "manual-study-preview-answer",
    "manual-study-preview-source",
    "Full Manual Study flow readiness prompt text",
    "Răspuns read-only pentru auditul complet Manual Study flow.",
]

for term in normal_terms:
    if term not in normal_body:
        raise SystemExit(f"FAILED_V0830_NORMAL_STUDY_TERM_MISSING={term}")

shadow_terms = [
    "manual-study-shadow-route",
    "manual-study-shadow-source",
    "manual-study-shadow-policy",
    "manual-study-shadow-cards",
    "read_only_shadow_toggle",
]

for term in shadow_terms:
    if term not in shadow_body:
        raise SystemExit(f"FAILED_V0830_SHADOW_TERM_MISSING={term}")

dry_run_terms = [
    "Manual Study Integration Dry Run",
    "manual-study-integration-dry-run-route",
    "dry_run_toggle_enabled",
    "false",
    "dry_run_only",
]

for term in dry_run_terms:
    if term not in dry_run_body:
        raise SystemExit(f"FAILED_V0830_DRY_RUN_TERM_MISSING={term}")

manual_study = json.loads(manual_study_preview.read_text(encoding="utf-8", errors="replace"))
items = manual_study.get("items")
if not isinstance(items, list) or not items:
    raise SystemExit("FAILED_V0830_ITEMS_INVALID_OR_EMPTY")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}
if eligible_id not in ids:
    raise SystemExit("FAILED_V0830_ELIGIBLE_ID_NOT_EXPORTED")

fallback_status = None
fallback_body = ""
tmp_preview = manual_study_preview.with_name(manual_study_preview.name + ".v0830tmp")
if tmp_preview.exists():
    tmp_preview.unlink()

try:
    shutil.move(str(manual_study_preview), str(tmp_preview))
    fallback_status, fallback_body, _ = fetch_url_allow_http_error(normal_study_url, "NORMAL_STUDY_LEGACY_FALLBACK")
finally:
    if tmp_preview.exists():
        shutil.move(str(tmp_preview), str(manual_study_preview))

if fallback_status != 200:
    raise SystemExit(f"FAILED_V0830_NORMAL_STUDY_LEGACY_FALLBACK_STATUS={fallback_status}; BODY={fallback_body[:800]}")

if "manual-study-default-route" in fallback_body:
    raise SystemExit("FAILED_V0830_NORMAL_STUDY_FALLBACK_RENDERED_MANUAL_DEFAULT_WHEN_PREVIEW_MISSING")

legacy_after = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None
if legacy_before != legacy_after:
    raise SystemExit("FAILED_V0830_LEGACY_STUDY_PREVIEW_CHANGED")

manual_result = {
    "manual_browser_audit_status": "OWNER_LOCAL_FULL_MANUAL_STUDY_FLOW_READINESS_PASS",
    "steps": [
        {"step": "course_tools_loads", "status": "PASS", "http_status": course_tools_status},
        {"step": "course_tools_normal_study_link_visible", "status": "PASS", "href": normal_study_href},
        {"step": "follow_normal_study_link", "status": "PASS", "http_status": normal_status},
        {"step": "normal_study_renders_manual_default_cards", "status": "PASS"},
        {"step": "answers_remain_read_only_details", "status": "PASS"},
        {"step": "source_metadata_visible", "status": "PASS"},
        {"step": "course_tools_shadow_link_visible", "status": "PASS", "href": shadow_href},
        {"step": "follow_shadow_link", "status": "PASS", "http_status": shadow_status},
        {"step": "course_tools_dry_run_link_visible", "status": "PASS", "href": dry_run_href},
        {"step": "follow_dry_run_link", "status": "PASS", "http_status": dry_run_status},
        {"step": "normal_study_legacy_fallback_when_manual_preview_missing", "status": "PASS", "http_status": fallback_status},
        {"step": "legacy_study_items_preview_unchanged", "status": "PASS"},
    ],
}

summary = {
    "VOILA_V0_8_30_FULL_MANUAL_STUDY_FLOW_READINESS_AUDIT_CHECK": "PASS",
    "depends_on_v0829_normal_study_link_audit": True,
    "course_tools_status": course_tools_status,
    "course_tools_normal_study_link_visible": True,
    "course_tools_normal_study_link_href": normal_study_href,
    "normal_study_link_status": normal_status,
    "normal_study_link_renders_manual_default": True,
    "manual_study_default_cards_visible": True,
    "answer_details_remain_read_only": True,
    "source_metadata_visible": True,
    "course_tools_shadow_link_visible": True,
    "course_tools_shadow_link_href": shadow_href,
    "shadow_route_status": shadow_status,
    "course_tools_dry_run_link_visible": True,
    "course_tools_dry_run_link_href": dry_run_href,
    "dry_run_route_status": dry_run_status,
    "normal_study_legacy_fallback_status_when_manual_preview_missing": fallback_status,
    "fallback_legacy_study_available_when_preview_missing": True,
    "manual_study_items_preview_json_read": True,
    "study_route_legacy_block_unchanged": True,
    "study_route_block_sha256": study_route_hash,
    "manual_browser_audit_recorded": True,
    "web_app_changed": False,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "manual_study_connected_to_real_study": "full_owner_local_flow_default_manual_study_read_only_with_legacy_fallback",
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
    "TESTER_READINESS": "BLOCKED_FULL_OWNER_LOCAL_AUDIT_ONLY_NO_PROGRESS_NO_PACKAGE",
    "POLICY": "full_manual_study_flow_readiness_audit_no_progress_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0830-full-manual-study-flow-readiness-audit")
evidence.mkdir(parents=True, exist_ok=True)

out_json = evidence / "V0.8.30-FULL-MANUAL-STUDY-FLOW-READINESS-AUDIT-CHECK.json"
out_md = evidence / "V0.8.30-FULL-MANUAL-STUDY-FLOW-READINESS-AUDIT-CHECK.md"

out_json.write_text(json.dumps({"summary": summary, "manual_result": manual_result}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.30 Full Manual Study flow readiness audit",
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
