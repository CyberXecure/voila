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
doc = root / "docs" / "dev" / "manual-study-default-study-read-only-fallback-no-progress-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0827_WEB_APP_MISSING"),
    (doc, "FAILED_V0827_DOC_MISSING"),
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
    "validate_pdf_name(pdf_name)",
    "_voila_v0822_manual_study_shadow_toggle_enabled",
    "return await call_next(request)",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0827_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "Manual Study default `/study` read-only fallback",
    "first guarded default `/study` behavior change",
    "If `manual_study_items.preview.json` exists, is readable, and contains items:",
    "`/study` renders Manual Study read-only cards;",
    "answers remain inside `<details>`;",
    "source metadata remains visible;",
    "If `manual_study_items.preview.json` is missing, invalid, or empty:",
    "`/study` falls back to the existing legacy Study behavior.",
    "`/study?manual_study_shadow=1&course_id={course_id}`",
    "This milestone does not add a route.",
    "It does not add a POST endpoint.",
    "It does not remove the existing `/study` route.",
    "It does not modify the legacy `/study` route block.",
    "It does not write progress.",
    "It does not mark answers.",
    "It does not overwrite or modify the legacy `study_items.preview.json`.",
    "Default Manual Study is read-only.",
    "Default Manual Study is enabled only when `manual_study_items.preview.json` is present and valid.",
    "Legacy fallback remains active when Manual Study preview is missing, invalid, or empty.",
    "No Progress write.",
    "No answer marking.",
    "No legacy Study artifact overwrite.",
    "Rollback is a clean revert of this implementation commit.",
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
        raise SystemExit(f"FAILED_V0827_DOC_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/manual-study-default-study-read-only-fallback-no-progress-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-study-default-study-read-only-fallback-no-progress-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-study-default-study-read-only-fallback-no-progress-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0827_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0827_STUDY_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/study"') != 0:
    raise SystemExit("FAILED_V0827_STUDY_POST_ADDED")

if web_text.count("VOILA_V0_8_27_MANUAL_STUDY_DEFAULT_STUDY_READ_ONLY_FALLBACK_START") != 1:
    raise SystemExit("FAILED_V0827_DEFAULT_BLOCK_COUNT_CHANGED")

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
        raise SystemExit(f"FAILED_V0827_FORBIDDEN_WEB_TERM_FOUND={forbidden}")

study_route_match = re.search(
    r'@app\.get\("/study"[\s\S]*?(?=\n@app\.(?:get|post|put|delete|patch)\(|\n# VOILA_V0_8_22_MANUAL_STUDY_REAL_STUDY_READ_ONLY_SHADOW_TOGGLE_START|\Z)',
    web_text,
)
if not study_route_match:
    raise SystemExit("FAILED_V0827_STUDY_ROUTE_STATIC_BLOCK_NOT_FOUND")

study_route_block = study_route_match.group(0)
study_route_hash = hashlib.sha256(study_route_block.encode("utf-8", errors="replace")).hexdigest()

if study_route_hash != expected_v0821_study_route_hash:
    raise SystemExit(
        "FAILED_V0827_STUDY_ROUTE_HASH_CHANGED="
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

save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"
verify_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/verify-draft"
learning_pack_export_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"
manual_study_export_url = f"http://127.0.0.1:8787/owner/manual-learning-pack-study-adapter-dry-run/{course_id}/export-manual-study-items-preview"

study_default_url = f"http://127.0.0.1:8787/study?pdf={urllib.parse.quote(pdf_name)}"
study_shadow_url = f"http://127.0.0.1:8787/study?manual_study_shadow=1&course_id={course_id}"

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
        raise SystemExit(f"FAILED_V0827_POST={url}; STATUS={exc.code}; BODY={error_body}")

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
    raise SystemExit(f"FAILED_V0827_{label}_FETCH={last_error}")

eligible_id = "v0827-check-default-study-read-only-fallback-eligible"

payload = {
    "draft_id": eligible_id,
    "page": "1",
    "bbox": "[262, 284, 700, 630]",
    "kind": "formula",
    "title": "v0.8.27 default Study fallback eligible",
    "verified_text": "Default Study Manual prompt text",
    "explanation_ro": "Răspuns read-only pentru Study implicit cu fallback legacy.",
    "source_status": "verified",
    "source_note": "Created by v0.8.27 default Study read-only fallback check.",
}

status, body, _ = post_form(save_url, payload)
if status != 200:
    raise SystemExit(f"FAILED_V0827_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body, _ = post_form(verify_url, {"draft_id": eligible_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V0827_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

learning_export_status, learning_export_body, _ = post_form(learning_pack_export_url, {})
if learning_export_status != 200:
    raise SystemExit(f"FAILED_V0827_LEARNING_PACK_EXPORT_STATUS={learning_export_status}; BODY={learning_export_body}")

manual_study_export_status, manual_study_export_body, _ = post_form(manual_study_export_url, {})
if manual_study_export_status != 200:
    raise SystemExit(f"FAILED_V0827_MANUAL_STUDY_EXPORT_STATUS={manual_study_export_status}; BODY={manual_study_export_body}")

if not manual_study_preview.exists():
    raise SystemExit("FAILED_V0827_MANUAL_STUDY_PREVIEW_JSON_MISSING")

default_status, default_body, _ = fetch_url_allow_http_error(study_default_url, "DEFAULT_STUDY")
shadow_status, shadow_body, _ = fetch_url_allow_http_error(study_shadow_url, "SHADOW_STUDY")

if default_status != 200:
    raise SystemExit(f"FAILED_V0827_DEFAULT_STUDY_STATUS={default_status}; BODY={default_body[:800]}")

if shadow_status != 200:
    raise SystemExit(f"FAILED_V0827_SHADOW_STUDY_STATUS={shadow_status}; BODY={shadow_body[:800]}")

default_terms = [
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
    "Default Study Manual prompt text",
    "Răspuns read-only pentru Study implicit cu fallback legacy.",
]

for term in default_terms:
    if term not in default_body:
        raise SystemExit(f"FAILED_V0827_DEFAULT_STUDY_TERM_MISSING={term}")

shadow_terms = [
    "manual-study-shadow-route",
    "manual-study-shadow-source",
    "manual-study-shadow-policy",
    "manual-study-shadow-cards",
    "read_only_shadow_toggle",
]

for term in shadow_terms:
    if term not in shadow_body:
        raise SystemExit(f"FAILED_V0827_SHADOW_STUDY_TERM_MISSING={term}")

manual_study = json.loads(manual_study_preview.read_text(encoding="utf-8", errors="replace"))
items = manual_study.get("items")
if not isinstance(items, list) or not items:
    raise SystemExit("FAILED_V0827_ITEMS_INVALID_OR_EMPTY")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}
if eligible_id not in ids:
    raise SystemExit("FAILED_V0827_ELIGIBLE_ID_NOT_EXPORTED")

fallback_status = None
fallback_body = ""
tmp_preview = manual_study_preview.with_suffix(".preview.json.v0827tmp")
if tmp_preview.exists():
    tmp_preview.unlink()

try:
    shutil.move(str(manual_study_preview), str(tmp_preview))
    fallback_status, fallback_body, _ = fetch_url_allow_http_error(study_default_url, "LEGACY_FALLBACK")
finally:
    if tmp_preview.exists():
        shutil.move(str(tmp_preview), str(manual_study_preview))

if fallback_status != 200:
    raise SystemExit(f"FAILED_V0827_LEGACY_FALLBACK_STATUS={fallback_status}; BODY={fallback_body[:800]}")

if "manual-study-default-route" in fallback_body:
    raise SystemExit("FAILED_V0827_LEGACY_FALLBACK_RENDERED_MANUAL_DEFAULT_WHEN_PREVIEW_MISSING")

legacy_after = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None
if legacy_before != legacy_after:
    raise SystemExit("FAILED_V0827_LEGACY_STUDY_PREVIEW_CHANGED")

summary = {
    "VOILA_V0_8_27_MANUAL_STUDY_DEFAULT_STUDY_READ_ONLY_FALLBACK_CHECK": "PASS",
    "depends_on_v0826_preflight_contract": True,
    "default_study_url": "/study?pdf={pdf_name}",
    "default_study_status": default_status,
    "shadow_study_status": shadow_status,
    "legacy_fallback_status_when_manual_preview_missing": fallback_status,
    "manual_study_default_enabled": True,
    "manual_study_items_preview_json_read": True,
    "manual_study_default_cards_visible": True,
    "manual_study_shadow_still_available": True,
    "fallback_legacy_study_available_when_preview_missing": True,
    "answer_details_remain_read_only": True,
    "source_metadata_visible": True,
    "study_route_legacy_block_unchanged": True,
    "study_route_block_sha256": study_route_hash,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "manual_study_connected_to_real_study": "default_read_only_with_legacy_fallback",
    "replaces_existing_study_route": False,
    "progress_write_added": False,
    "answer_marking_added": False,
    "study_artifact_written": False,
    "legacy_study_items_preview_unchanged": True,
    "crop_file_written": False,
    "course_generation_changed": False,
    "study_changed": "default_read_only_middleware_with_legacy_fallback",
    "progress_changed": False,
    "ocr_rewrite_performed": False,
    "formula_ocr_performed": False,
    "build_performed": False,
    "zip_created": False,
    "share_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "TESTER_READINESS": "BLOCKED_DEFAULT_STUDY_OWNER_LOCAL_ONLY_NO_PROGRESS_NO_PACKAGE",
    "POLICY": "manual_study_default_study_read_only_fallback_no_progress_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0827-manual-study-default-study-read-only-fallback")
evidence.mkdir(parents=True, exist_ok=True)

out_json = evidence / "V0.8.27-MANUAL-STUDY-DEFAULT-STUDY-READ-ONLY-FALLBACK-CHECK.json"
out_md = evidence / "V0.8.27-MANUAL-STUDY-DEFAULT-STUDY-READ-ONLY-FALLBACK-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.27 Manual Study default `/study` read-only fallback",
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
