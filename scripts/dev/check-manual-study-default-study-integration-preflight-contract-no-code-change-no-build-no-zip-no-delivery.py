from pathlib import Path
import hashlib
import json
import re
import subprocess
import time
import urllib.request
import urllib.error

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-study-default-study-integration-preflight-contract-no-code-change-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0826_WEB_APP_MISSING"),
    (doc, "FAILED_V0826_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

expected_v0821_study_route_hash = "ad12be8afe880715e47cfcb9ef7aeb3dd364aeb0d98ee4a97ce2de338c3566ad"

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
        raise SystemExit(f"FAILED_V0826_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "Manual Study default `/study` integration preflight contract",
    "Manual Study is available only through the explicit owner-local shadow route:",
    "`/study?manual_study_shadow=1&course_id={course_id}`",
    "Course Tools links to that explicit shadow route.",
    "The existing `/study` route remains unchanged and is not replaced.",
    "Manual Study is not the default `/study`.",
    "Future default `/study` contract",
    "If `manual_study_items.preview.json` exists for that course and is readable:",
    "render Manual Study read-only cards;",
    "keep answers inside `<details>`;",
    "keep source metadata visible;",
    "do not write Progress;",
    "do not mark answers;",
    "do not write or modify `study_items.preview.json`.",
    "If `manual_study_items.preview.json` does not exist, is invalid, or is empty:",
    "fall back to the existing legacy `/study` behavior.",
    "Safety gates for the future implementation",
    "default `/study` works with Manual Study only when `manual_study_items.preview.json` is present;",
    "fallback legacy `/study` remains available when Manual Study preview is missing or invalid;",
    "no POST endpoint is added;",
    "no Progress write is added;",
    "no answer marking is added;",
    "no `study_items.preview.json` overwrite happens;",
    "no Course generation behavior changes;",
    "no OCR rewrite happens;",
    "no Formula OCR happens;",
    "source metadata remains visible;",
    "answers remain read-only;",
    "Rollback contract",
    "do not merge;",
    "do not package;",
    "do not deliver;",
    "revert the implementation patch;",
    "preserve the v0.8.22 shadow route and v0.8.24 Course Tools shadow link as the safe owner-local access path.",
    "This milestone is preflight/docs/check only.",
    "It does not modify `services/api/web_app.py`.",
    "It does not add a route.",
    "It does not add a POST endpoint.",
    "It does not make Manual Study the default `/study`.",
    "It does not replace or modify the existing `/study` route.",
    "It does not write progress.",
    "It does not mark answers.",
    "It does not overwrite or modify the legacy `study_items.preview.json`.",
    "Tester readiness remains blocked.",
    "A separate explicit implementation milestone is required before any default `/study` change.",
    "A separate explicit packaging milestone is required before any tester package.",
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
        raise SystemExit(f"FAILED_V0826_DOC_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/manual-study-default-study-integration-preflight-contract-no-code-change-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-study-default-study-integration-preflight-contract-no-code-change-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-study-default-study-integration-preflight-contract-no-code-change-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0826_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0826_STUDY_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/study"') != 0:
    raise SystemExit("FAILED_V0826_STUDY_POST_ADDED")

if web_text.count("VOILA_V0_8_22_MANUAL_STUDY_REAL_STUDY_READ_ONLY_SHADOW_TOGGLE_START") != 1:
    raise SystemExit("FAILED_V0826_SHADOW_TOGGLE_COUNT_CHANGED")

if web_text.count("VOILA_V0_8_24_MANUAL_STUDY_SHADOW_COURSE_TOOLS_LINK_START") != 1:
    raise SystemExit("FAILED_V0826_COURSE_TOOLS_SHADOW_LINK_COUNT_CHANGED")

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
        raise SystemExit(f"FAILED_V0826_FORBIDDEN_WEB_TERM_FOUND={forbidden}")

study_route_match = re.search(
    r'@app\.get\("/study"[\s\S]*?(?=\n@app\.(?:get|post|put|delete|patch)\(|\Z)',
    web_text,
)
if not study_route_match:
    raise SystemExit("FAILED_V0826_STUDY_ROUTE_STATIC_BLOCK_NOT_FOUND")

study_route_block = study_route_match.group(0)
study_route_hash = hashlib.sha256(study_route_block.encode("utf-8", errors="replace")).hexdigest()

if study_route_hash != expected_v0821_study_route_hash:
    raise SystemExit(
        "FAILED_V0826_STUDY_ROUTE_HASH_CHANGED="
        + study_route_hash
        + ";EXPECTED="
        + expected_v0821_study_route_hash
    )

course_id = "03-pag-30-34-vectori-trigonometrie"
shadow_url = f"http://127.0.0.1:8787/study?manual_study_shadow=1&course_id={course_id}"
home_url = "http://127.0.0.1:8787/"
course_tools_url = "http://127.0.0.1:8787/course-tools"
# VOILA_V0_8_26_COURSE_TOOLS_DISCOVERY_FIX
fallback_url = "http://127.0.0.1:8787/study"

def fetch_url_allow_http_error(url, label):
    last_error = ""
    for _ in range(10):
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                return response.status, response.read().decode("utf-8", errors="replace"), response.geturl()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8", errors="replace"), url
        except Exception as exc:
            last_error = str(exc)
            time.sleep(2)
    raise SystemExit(f"FAILED_V0826_{label}_FETCH={last_error}")


def absolutize(local_or_absolute_href):
    href = local_or_absolute_href.replace("&amp;", "&")
    if href.startswith("/"):
        return "http://127.0.0.1:8787" + href
    if href.startswith("http://") or href.startswith("https://"):
        return href
    return "http://127.0.0.1:8787/" + href.lstrip("./")


home_status, home_body, _ = fetch_url_allow_http_error(home_url, "HOME")
if home_status != 200:
    raise SystemExit(f"FAILED_V0826_HOME_STATUS={home_status}; BODY={home_body[:800]}")

course_tools_match = re.search(r'href="([^"]*/course-tools[^"]*)"', home_body)
if course_tools_match:
    course_tools_url = absolutize(course_tools_match.group(1))

course_tools_status, course_tools_body, _ = fetch_url_allow_http_error(course_tools_url, "COURSE_TOOLS")
shadow_status, shadow_body, _ = fetch_url_allow_http_error(shadow_url, "SHADOW")
fallback_status, fallback_body, _ = fetch_url_allow_http_error(fallback_url, "FALLBACK")

if course_tools_status != 200:
    raise SystemExit(f"FAILED_V0826_COURSE_TOOLS_STATUS={course_tools_status}; BODY={course_tools_body[:800]}")

if shadow_status != 200:
    raise SystemExit(f"FAILED_V0826_SHADOW_STATUS={shadow_status}; BODY={shadow_body[:800]}")

if fallback_status == 200 and "manual-study-shadow-route" in fallback_body:
    raise SystemExit("FAILED_V0826_FALLBACK_RENDERED_SHADOW_WITHOUT_TOGGLE")

course_tools_terms = [
    "manual-study-shadow-course-tools-link",
    "/study?manual_study_shadow=1&amp;course_id=03-pag-30-34-vectori-trigonometrie",
    "manual_study_default_enabled",
    "false",
    "shadow_only_explicit_link",
    "progress_write",
    "answer_marking",
    "writes_legacy_study_items_preview",
]

for term in course_tools_terms:
    if term not in course_tools_body:
        raise SystemExit(f"FAILED_V0826_COURSE_TOOLS_TERM_MISSING={term}")

shadow_terms = [
    "manual-study-shadow-route",
    "manual-study-shadow-source",
    "manual-study-shadow-policy",
    "manual-study-shadow-cards",
    "manual_study_items.preview.json",
    "read_only_shadow_toggle",
]

for term in shadow_terms:
    if term not in shadow_body:
        raise SystemExit(f"FAILED_V0826_SHADOW_TERM_MISSING={term}")

summary = {
    "VOILA_V0_8_26_MANUAL_STUDY_DEFAULT_STUDY_INTEGRATION_PREFLIGHT_CONTRACT_CHECK": "PASS",
    "depends_on_v0822_shadow_toggle": True,
    "depends_on_v0824_course_tools_shadow_link": True,
    "depends_on_v0825_course_tools_shadow_browser_audit": True,
    "preflight_contract_doc_added": True,
    "future_default_study_contract_defined": True,
    "future_default_rule_manual_study_preview_exists_then_manual_study": True,
    "future_fallback_rule_missing_invalid_empty_preview_then_legacy_study": True,
    "future_safety_gates_defined": True,
    "rollback_contract_defined": True,
    "course_tools_shadow_link_still_visible": True,
    "shadow_route_still_reachable": True,
    "fallback_without_toggle_does_not_render_shadow": True,
    "study_route_hash_matches_v0821_preflight": True,
    "study_route_block_sha256": study_route_hash,
    "web_app_changed": False,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "manual_study_default_enabled": False,
    "manual_study_connected_to_real_study": "not_default_preflight_only",
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
    "TESTER_READINESS": "BLOCKED_PREFLIGHT_ONLY_NO_DEFAULT_STUDY_NO_PACKAGE",
    "POLICY": "manual_study_default_study_integration_preflight_contract_no_code_change_no_build_no_zip_no_share_no_delivery_no_distribution",
    "RECOMMENDED_NEXT": "v0.8.27-owner-local-manual-study-default-study-read-only-fallback-no-progress-no-build-no-zip-no-delivery",
}

evidence = Path(r"D:\dev\tester-runs\v0826-manual-study-default-study-integration-preflight-contract")
evidence.mkdir(parents=True, exist_ok=True)

out_json = evidence / "V0.8.26-MANUAL-STUDY-DEFAULT-STUDY-INTEGRATION-PREFLIGHT-CONTRACT-CHECK.json"
out_md = evidence / "V0.8.26-MANUAL-STUDY-DEFAULT-STUDY-INTEGRATION-PREFLIGHT-CONTRACT-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.26 Manual Study default `/study` integration preflight contract",
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
