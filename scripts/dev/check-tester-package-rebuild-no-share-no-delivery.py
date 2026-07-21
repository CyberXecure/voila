from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error
import zipfile

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "tester-package-rebuild-no-share-no-delivery.md"
check_py = root / "scripts" / "dev" / "check-tester-package-rebuild-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-tester-package-rebuild-no-share-no-delivery.ps1"

for path, marker in [
    (web, "FAILED_V0834_WEB_APP_MISSING"),
    (doc, "FAILED_V0834_DOC_MISSING"),
    (check_py, "FAILED_V0834_CHECK_PY_MISSING"),
    (check_ps1, "FAILED_V0834_CHECK_PS1_MISSING"),
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
        raise SystemExit(f"FAILED_V0834_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "Owner-local tester package rebuild",
    "This milestone may create a local package ZIP.",
    "This milestone may create a SHA256 checksum.",
    "This milestone must not create a share.",
    "This milestone must not copy anything to OneDrive.",
    "This milestone must not deliver anything.",
    "This milestone must not distribute anything.",
    "This milestone must not create a public release.",
    "Manual Study default on `/study?pdf={pdf_name}`.",
    "Course Tools normal Study link.",
    "Course Tools explicit Manual Study shadow link.",
    "Course Tools separate dry-run link.",
    "Legacy fallback when `manual_study_items.preview.json` is missing, invalid, or empty.",
    "Read-only answers in `<details>`.",
    "Source metadata display.",
    "No Progress write.",
    "No answer marking.",
    "No new Study POST endpoint.",
    "No Course generation behavior change.",
    "No OCR rewrite.",
    "No Formula OCR.",
    "No crop file write.",
    "package candidate path;",
    "package SHA256;",
    "source commit used;",
    "package file count;",
    "included Manual Study readiness markers;",
    "no public release;",
    "no share;",
    "no delivery;",
    "no distribution.",
    "This milestone may create local files only under `D:\\dev\\release-assets\\voila\\v0.8.34-tester-package-rebuild-no-share-no-delivery`.",
    "This milestone does not modify `services/api/web_app.py`.",
    "This milestone does not add a route.",
    "This milestone does not add a POST endpoint.",
    "This milestone does not create a share.",
    "This milestone does not copy to OneDrive.",
    "This milestone does not deliver anything.",
    "This milestone does not distribute anything.",
    "extracted-package browser validation milestone;",
    "final no-delivery review milestone;",
    "explicit owner approval before any share or delivery.",
    "A local ZIP candidate may exist after this milestone.",
    "That ZIP candidate is not delivered.",
    "That ZIP candidate is not shared.",
    "That ZIP candidate is not a public release.",
    "A separate extracted-package validation milestone is required next.",
    "A separate final no-delivery review milestone is required before any share.",
    "Explicit owner approval is required before any share or delivery.",
    "No share.",
    "No OneDrive copy.",
    "No delivery.",
    "No distribution.",
    "No public release.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit(f"FAILED_V0834_DOC_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/tester-package-rebuild-no-share-no-delivery.md",
    "scripts/dev/check-tester-package-rebuild-no-share-no-delivery.py",
    "scripts/dev/check-tester-package-rebuild-no-share-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0834_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0834_STUDY_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/study"') != 0:
    raise SystemExit("FAILED_V0834_STUDY_POST_ADDED")

if web_text.count("VOILA_V0_8_27_MANUAL_STUDY_DEFAULT_STUDY_READ_ONLY_FALLBACK_START") != 1:
    raise SystemExit("FAILED_V0834_DEFAULT_BLOCK_COUNT_CHANGED")

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
        raise SystemExit(f"FAILED_V0834_FORBIDDEN_WEB_TERM_FOUND={forbidden}")

study_route_match = re.search(
    r'@app\.get\("/study"[\s\S]*?(?=\n@app\.(?:get|post|put|delete|patch)\(|\n# VOILA_V0_8_22_MANUAL_STUDY_REAL_STUDY_READ_ONLY_SHADOW_TOGGLE_START|\Z)',
    web_text,
)
if not study_route_match:
    raise SystemExit("FAILED_V0834_STUDY_ROUTE_STATIC_BLOCK_NOT_FOUND")

study_route_block = study_route_match.group(0)
study_route_hash = hashlib.sha256(study_route_block.encode("utf-8", errors="replace")).hexdigest()

if study_route_hash != expected_v0821_study_route_hash:
    raise SystemExit(
        "FAILED_V0834_STUDY_ROUTE_HASH_CHANGED="
        + study_route_hash
        + ";EXPECTED="
        + expected_v0821_study_route_hash
    )

course_id = "03-pag-30-34-vectori-trigonometrie"
pdf_name = course_id + ".pdf"
input_pdf = root / "data" / "input" / pdf_name
output_dir = root / "data" / "output" / course_id
manual_study_preview = output_dir / "manual_study_items.preview.json"
legacy_study_preview = output_dir / "study_items.preview.json"

if not input_pdf.exists():
    raise SystemExit("FAILED_V0834_INPUT_PDF_MISSING=" + str(input_pdf))

if not output_dir.exists():
    raise SystemExit("FAILED_V0834_EXISTING_GENERATED_COURSE_OUTPUT_MISSING=" + str(output_dir))

legacy_before = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None

home_url = "http://127.0.0.1:8787/"

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
        raise SystemExit(f"FAILED_V0834_POST={url}; STATUS={exc.code}; BODY={error_body}")

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
    raise SystemExit(f"FAILED_V0834_{label}_FETCH={last_error}")

def absolutize(local_or_absolute_href):
    href = local_or_absolute_href.replace("&amp;", "&")
    if href.startswith("/"):
        return "http://127.0.0.1:8787" + href
    if href.startswith("http://") or href.startswith("https://"):
        return href
    return "http://127.0.0.1:8787/" + href.lstrip("./")

eligible_id = "v0834-check-package-rebuild-eligible"

payload = {
    "draft_id": eligible_id,
    "page": "1",
    "bbox": "[332, 354, 840, 770]",
    "kind": "formula",
    "title": "v0.8.34 package rebuild eligible",
    "verified_text": "Tester package rebuild prompt text",
    "explanation_ro": "Răspuns read-only pentru rebuild-ul local de tester package.",
    "source_status": "verified",
    "source_note": "Created by v0.8.34 package rebuild check.",
}

status, body, _ = post_form(save_url, payload)
if status != 200:
    raise SystemExit(f"FAILED_V0834_SAVE_FIXTURE_STATUS={status}; BODY={body}")

verify_status, verify_body, _ = post_form(verify_url, {"draft_id": eligible_id})
if verify_status != 200:
    raise SystemExit(f"FAILED_V0834_VERIFY_FIXTURE_STATUS={verify_status}; BODY={verify_body}")

learning_export_status, learning_export_body, _ = post_form(learning_pack_export_url, {})
if learning_export_status != 200:
    raise SystemExit(f"FAILED_V0834_LEARNING_PACK_EXPORT_STATUS={learning_export_status}; BODY={learning_export_body}")

manual_study_export_status, manual_study_export_body, _ = post_form(manual_study_export_url, {})
if manual_study_export_status != 200:
    raise SystemExit(f"FAILED_V0834_MANUAL_STUDY_EXPORT_STATUS={manual_study_export_status}; BODY={manual_study_export_body}")

if not manual_study_preview.exists():
    raise SystemExit("FAILED_V0834_MANUAL_STUDY_PREVIEW_JSON_MISSING")

home_status, home_body, _ = fetch_url_allow_http_error(home_url, "HOME")
if home_status != 200:
    raise SystemExit(f"FAILED_V0834_HOME_STATUS={home_status}; BODY={home_body[:800]}")

if course_id not in home_body and pdf_name not in home_body:
    raise SystemExit("FAILED_V0834_HOME_DOES_NOT_REFERENCE_EXISTING_COURSE")

course_tools_hrefs = [
    href.replace("&amp;", "&")
    for href in re.findall(r'href="([^"]*/course-tools[^"]*)"', home_body)
]
if not course_tools_hrefs:
    raise SystemExit("FAILED_V0834_HOME_COURSE_TOOLS_LINK_NOT_FOUND")

preferred_course_tools_href = None
for href in course_tools_hrefs:
    if course_id in href or pdf_name in href:
        preferred_course_tools_href = href
        break

if preferred_course_tools_href is None:
    preferred_course_tools_href = course_tools_hrefs[0]

course_tools_url = absolutize(preferred_course_tools_href)

course_tools_status, course_tools_body, _ = fetch_url_allow_http_error(course_tools_url, "COURSE_TOOLS_FROM_HOME")
if course_tools_status != 200:
    raise SystemExit(f"FAILED_V0834_COURSE_TOOLS_FROM_HOME_STATUS={course_tools_status}; BODY={course_tools_body[:800]}")

normal_study_matches = re.findall(r'href="([^"]*/study\?pdf=[^"]+)"', course_tools_body)
normal_study_hrefs = [href.replace("&amp;", "&") for href in normal_study_matches if "manual_study_shadow" not in href]
expected_normal_study_href = f"/study?pdf={urllib.parse.quote(pdf_name)}"

normal_study_href = None
for href in normal_study_hrefs:
    if href == expected_normal_study_href:
        normal_study_href = href
        break

if normal_study_href is None:
    raise SystemExit("FAILED_V0834_NORMAL_STUDY_LINK_HREF_NOT_FOUND_OR_UNEXPECTED=" + ",".join(normal_study_hrefs[:10]))

shadow_link_match = re.search(
    r'<a\s+href="([^"]+)"\s+data-testid="manual-study-shadow-course-tools-link"',
    course_tools_body,
)
if not shadow_link_match:
    raise SystemExit("FAILED_V0834_SHADOW_LINK_HREF_NOT_FOUND")

dry_run_link_match = re.search(
    r'<a\s+href="([^"]+)"\s+data-testid="manual-study-dry-run-course-tools-link"',
    course_tools_body,
)
if not dry_run_link_match:
    raise SystemExit("FAILED_V0834_DRY_RUN_LINK_HREF_NOT_FOUND")

shadow_href = shadow_link_match.group(1).replace("&amp;", "&")
dry_run_href = dry_run_link_match.group(1).replace("&amp;", "&")

normal_study_url = absolutize(normal_study_href)
shadow_url = absolutize(shadow_link_match.group(1))
dry_run_url = absolutize(dry_run_link_match.group(1))

normal_status, normal_body, _ = fetch_url_allow_http_error(normal_study_url, "NORMAL_STUDY")
shadow_status, shadow_body, _ = fetch_url_allow_http_error(shadow_url, "SHADOW_STUDY")
dry_run_status, dry_run_body, _ = fetch_url_allow_http_error(dry_run_url, "DRY_RUN")

if normal_status != 200:
    raise SystemExit(f"FAILED_V0834_NORMAL_STUDY_STATUS={normal_status}; BODY={normal_body[:800]}")

if shadow_status != 200:
    raise SystemExit(f"FAILED_V0834_SHADOW_STATUS={shadow_status}; BODY={shadow_body[:800]}")

if dry_run_status != 200:
    raise SystemExit(f"FAILED_V0834_DRY_RUN_STATUS={dry_run_status}; BODY={dry_run_body[:800]}")

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
    "Tester package rebuild prompt text",
    "Răspuns read-only pentru rebuild-ul local de tester package.",
]

for term in normal_terms:
    if term not in normal_body:
        raise SystemExit(f"FAILED_V0834_NORMAL_STUDY_TERM_MISSING={term}")

shadow_terms = [
    "manual-study-shadow-route",
    "manual-study-shadow-source",
    "manual-study-shadow-policy",
    "manual-study-shadow-cards",
    "read_only_shadow_toggle",
]

for term in shadow_terms:
    if term not in shadow_body:
        raise SystemExit(f"FAILED_V0834_SHADOW_TERM_MISSING={term}")

dry_run_terms = [
    "Manual Study Integration Dry Run",
    "manual-study-integration-dry-run-route",
    "dry_run_toggle_enabled",
    "false",
    "dry_run_only",
]

for term in dry_run_terms:
    if term not in dry_run_body:
        raise SystemExit(f"FAILED_V0834_DRY_RUN_TERM_MISSING={term}")

manual_study = json.loads(manual_study_preview.read_text(encoding="utf-8", errors="replace"))
items = manual_study.get("items")
if not isinstance(items, list) or not items:
    raise SystemExit("FAILED_V0834_ITEMS_INVALID_OR_EMPTY")

ids = {item.get("source_evidence_id") for item in items if isinstance(item, dict)}
if eligible_id not in ids:
    raise SystemExit("FAILED_V0834_ELIGIBLE_ID_NOT_EXPORTED")

fallback_status = None
fallback_body = ""
tmp_preview = manual_study_preview.with_name(manual_study_preview.name + ".v0834tmp")
if tmp_preview.exists():
    tmp_preview.unlink()

try:
    shutil.move(str(manual_study_preview), str(tmp_preview))
    fallback_status, fallback_body, _ = fetch_url_allow_http_error(normal_study_url, "NORMAL_STUDY_LEGACY_FALLBACK")
finally:
    if tmp_preview.exists():
        shutil.move(str(tmp_preview), str(manual_study_preview))

if fallback_status != 200:
    raise SystemExit(f"FAILED_V0834_NORMAL_STUDY_LEGACY_FALLBACK_STATUS={fallback_status}; BODY={fallback_body[:800]}")

if "manual-study-default-route" in fallback_body:
    raise SystemExit("FAILED_V0834_NORMAL_STUDY_FALLBACK_RENDERED_MANUAL_DEFAULT_WHEN_PREVIEW_MISSING")

legacy_after = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None
if legacy_before != legacy_after:
    raise SystemExit("FAILED_V0834_LEGACY_STUDY_PREVIEW_CHANGED")

release_dir = Path(r"D:\dev\release-assets\voila\v0.8.34-tester-package-rebuild-no-share-no-delivery")
candidate_dir_name = "voila-v0.8.34-controlled-tester-windows-package-candidate"
staging_dir = release_dir / "_s"
zip_path = release_dir / (candidate_dir_name + ".zip")
sha_path = release_dir / (candidate_dir_name + ".zip.sha256")
manifest_path = release_dir / "V0.8.34-TESTER-PACKAGE-REBUILD-MANIFEST.json"
evidence_dir = Path(r"D:\dev\tester-runs\v0834-tester-package-rebuild-no-share-no-delivery")

repo_resolved = root.resolve()
release_resolved = release_dir.resolve()
if str(release_resolved).lower().startswith(str(repo_resolved).lower()):
    raise SystemExit("FAILED_V0834_RELEASE_DIR_INSIDE_REPO")

if "onedrive" in str(release_resolved).lower():
    raise SystemExit("FAILED_V0834_RELEASE_DIR_IS_ONEDRIVE")

release_dir.mkdir(parents=True, exist_ok=True)
evidence_dir.mkdir(parents=True, exist_ok=True)

if staging_dir.exists():
    shutil.rmtree(win_extended_path(staging_dir))

if zip_path.exists():
    zip_path.unlink()

if sha_path.exists():
    sha_path.unlink()

staging_dir.mkdir(parents=True, exist_ok=True)

git_head = subprocess.check_output(
    ["git", "rev-parse", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).strip()

git_status = subprocess.check_output(
    ["git", "status", "--short", "--branch", "-uall"],
    text=True,
    encoding="utf-8",
    errors="replace",
)

git_files_raw = subprocess.check_output(["git", "ls-files", "-z"])
tracked_files = [
    entry.decode("utf-8", errors="replace")
    for entry in git_files_raw.split(b"\0")
    if entry
]

extra_files = [
    "docs/dev/tester-package-rebuild-no-share-no-delivery.md",
    "scripts/dev/check-tester-package-rebuild-no-share-no-delivery.py",
    "scripts/dev/check-tester-package-rebuild-no-share-no-delivery.ps1",
]

for extra in extra_files:
    if extra not in tracked_files and (root / extra).exists():
        tracked_files.append(extra)

excluded_prefixes = (
    ".git/",
    ".venv/",
    "venv/",
    "node_modules/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    "dist/",
    "build/",
    "release-assets/",
    "tester-runs/",
)

excluded_names = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
}

excluded_suffixes = (
    ".pem",
    ".key",
    ".pfx",
    ".p12",
    ".zip",
    ".7z",
    ".rar",
)

def win_extended_path(path):
    resolved = Path(path).resolve()
    value = str(resolved)
    prefix = chr(92) + chr(92) + "?" + chr(92)
    if os.name == "nt" and not value.startswith(prefix):
        return prefix + value
    return value


def is_safe_relative(rel_text):
    rel = Path(rel_text)
    if rel.is_absolute():
        return False
    if ".." in rel.parts:
        return False
    normalized = rel_text.replace("\\", "/")
    lowered = normalized.lower()
    if any(lowered.startswith(prefix) for prefix in excluded_prefixes):
        return False
    if Path(lowered).name in excluded_names:
        return False
    if any(lowered.endswith(suffix) for suffix in excluded_suffixes):
        return False
    return True

copied_files = []
skipped_files = []

for rel_text in sorted(set(tracked_files)):
    normalized = rel_text.replace("\\", "/")
    if not is_safe_relative(normalized):
        skipped_files.append(normalized)
        continue
    src = root / normalized
    if not src.exists() or not src.is_file():
        skipped_files.append(normalized)
        continue
    dst = staging_dir / normalized
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(win_extended_path(src), win_extended_path(dst))
        copied_files.append(normalized)
    except Exception as exc:
        raise SystemExit(
            "FAILED_V0834_COPY_FILE="
            + normalized
            + ";SRC="
            + str(src)
            + ";DST="
            + str(dst)
            + ";ERROR="
            + repr(exc)
        )

package_readme = staging_dir / "README-TESTERS-SHORT.txt"
package_notes = staging_dir / "RELEASE-NOTES-TESTERS.txt"
package_limits = staging_dir / "KNOWN-LIMITATIONS-TESTERS.txt"
package_policy = staging_dir / "NO-SHARE-NO-DELIVERY.txt"

package_readme.write_text(
    "Voila v0.8.34 controlled tester Windows package candidate\n"
    "\n"
    "This is an owner-local rebuilt package candidate.\n"
    "It is not delivered, not shared, and not a public release.\n"
    "\n"
    "Manual Study readiness included:\n"
    "- normal Study route can render Manual Study by default when manual_study_items.preview.json exists;\n"
    "- Course Tools keeps normal Study, shadow, and dry-run links separate;\n"
    "- answers remain read-only;\n"
    "- source metadata remains visible;\n"
    "- legacy fallback remains available.\n",
    encoding="utf-8",
)

package_notes.write_text(
    "Release notes for controlled tester package candidate v0.8.34\n"
    "\n"
    "- Rebuilt from owner-local readiness baseline after v0.8.32/v0.8.33.\n"
    "- Includes Manual Study default readiness code and checks.\n"
    "- No public release was created.\n"
    "- No share was created.\n"
    "- No delivery was performed.\n",
    encoding="utf-8",
)

package_limits.write_text(
    "Known limitations for v0.8.34 controlled tester package candidate\n"
    "\n"
    "- Package still requires extracted-package browser validation.\n"
    "- Package still requires final no-delivery review.\n"
    "- Package must not be shared until explicit owner approval.\n"
    "- No Progress write or answer marking is included for Manual Study.\n",
    encoding="utf-8",
)

package_policy.write_text(
    "POLICY: NO SHARE / NO DELIVERY / NO DISTRIBUTION / NO PUBLIC RELEASE\n"
    "\n"
    "This package candidate was created locally only under D:\\dev\\release-assets.\n"
    "Do not copy to OneDrive.\n"
    "Do not create a share link.\n"
    "Do not send to testers.\n",
    encoding="utf-8",
)

generated_package_files = [
    "README-TESTERS-SHORT.txt",
    "RELEASE-NOTES-TESTERS.txt",
    "KNOWN-LIMITATIONS-TESTERS.txt",
    "NO-SHARE-NO-DELIVERY.txt",
]

packaged_web = staging_dir / "services" / "api" / "web_app.py"
if not packaged_web.exists():
    raise SystemExit("FAILED_V0834_PACKAGED_WEB_APP_MISSING")

packaged_web_text = packaged_web.read_text(encoding="utf-8", errors="replace")
for term in required_web_terms:
    if term not in packaged_web_text:
        raise SystemExit(f"FAILED_V0834_PACKAGED_WEB_TERM_MISSING={term}")

for required_packaged in [
    "scripts/dev/start-voila.ps1",
    "scripts/dev/stop-voila.ps1",
    "docs/dev/tester-package-rebuild-no-share-no-delivery.md",
    "scripts/dev/check-tester-package-rebuild-no-share-no-delivery.py",
    "scripts/dev/check-tester-package-rebuild-no-share-no-delivery.ps1",
    "README-TESTERS-SHORT.txt",
    "RELEASE-NOTES-TESTERS.txt",
    "KNOWN-LIMITATIONS-TESTERS.txt",
    "NO-SHARE-NO-DELIVERY.txt",
]:
    if not (staging_dir / required_packaged).exists():
        raise SystemExit("FAILED_V0834_REQUIRED_PACKAGED_FILE_MISSING=" + required_packaged)

manifest = {
    "milestone": "v0.8.34-owner-local-tester-package-rebuild-no-share-no-delivery",
    "package_candidate": str(zip_path),
    "package_sha256_file": str(sha_path),
    "source_git_head": git_head,
    "git_status_at_rebuild": git_status,
    "candidate_dir_name": candidate_dir_name,
    "copied_tracked_file_count": len(copied_files),
    "generated_package_files": generated_package_files,
    "skipped_file_count": len(skipped_files),
    "manual_study_default_marker": "VOILA_V0_8_27_MANUAL_STUDY_DEFAULT_STUDY_READ_ONLY_FALLBACK_START",
    "manual_study_shadow_marker": "VOILA_V0_8_22_MANUAL_STUDY_REAL_STUDY_READ_ONLY_SHADOW_TOGGLE_START",
    "course_tools_shadow_link_marker": "VOILA_V0_8_24_MANUAL_STUDY_SHADOW_COURSE_TOOLS_LINK_START",
    "normal_study_link_href": normal_study_href,
    "shadow_link_href": shadow_href,
    "dry_run_link_href": dry_run_href,
    "manual_study_default_ready": True,
    "legacy_fallback_ready": True,
    "progress_write_added": False,
    "answer_marking_added": False,
    "new_study_post_endpoint_added": False,
    "share_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
}
manifest_in_staging = staging_dir / "PACKAGE-MANIFEST.json"
manifest_in_staging.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

zip_entries = []
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for file_path in sorted(staging_dir.rglob("*")):
        if not file_path.is_file():
            continue
        rel = file_path.relative_to(staging_dir)
        rel_zip = str(Path(candidate_dir_name) / rel).replace("\\", "/")
        lowered = rel_zip.lower()
        if "/.git/" in lowered or "/.venv/" in lowered or "/node_modules/" in lowered or lowered.endswith(".zip"):
            raise SystemExit("FAILED_V0834_FORBIDDEN_ENTRY_IN_PACKAGE=" + rel_zip)
        with open(win_extended_path(file_path), "rb") as source_file:
            zf.writestr(rel_zip, source_file.read())
        zip_entries.append(rel_zip)

if not zip_path.exists() or zip_path.stat().st_size <= 0:
    raise SystemExit("FAILED_V0834_ZIP_NOT_CREATED")

sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()
sha_path.write_text(f"{sha256}  {zip_path.name}\n", encoding="utf-8")

manifest["package_sha256"] = sha256
manifest["package_size_bytes"] = zip_path.stat().st_size
manifest["zip_entry_count"] = len(zip_entries)
manifest["manifest_path"] = str(manifest_path)
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if len(zip_entries) < 50:
    raise SystemExit("FAILED_V0834_PACKAGE_TOO_SMALL_ENTRY_COUNT=" + str(len(zip_entries)))

with zipfile.ZipFile(zip_path, "r") as zf:
    names = set(zf.namelist())
    required_zip_entries = [
        f"{candidate_dir_name}/services/api/web_app.py",
        f"{candidate_dir_name}/scripts/dev/start-voila.ps1",
        f"{candidate_dir_name}/scripts/dev/stop-voila.ps1",
        f"{candidate_dir_name}/docs/dev/tester-package-rebuild-no-share-no-delivery.md",
        f"{candidate_dir_name}/scripts/dev/check-tester-package-rebuild-no-share-no-delivery.py",
        f"{candidate_dir_name}/README-TESTERS-SHORT.txt",
        f"{candidate_dir_name}/RELEASE-NOTES-TESTERS.txt",
        f"{candidate_dir_name}/KNOWN-LIMITATIONS-TESTERS.txt",
        f"{candidate_dir_name}/NO-SHARE-NO-DELIVERY.txt",
        f"{candidate_dir_name}/PACKAGE-MANIFEST.json",
    ]
    for entry in required_zip_entries:
        if entry not in names:
            raise SystemExit("FAILED_V0834_REQUIRED_ZIP_ENTRY_MISSING=" + entry)
    packaged_web_from_zip = zf.read(f"{candidate_dir_name}/services/api/web_app.py").decode("utf-8", errors="replace")
    for term in required_web_terms:
        if term not in packaged_web_from_zip:
            raise SystemExit(f"FAILED_V0834_ZIP_WEB_TERM_MISSING={term}")

if "onedrive" in str(zip_path).lower():
    raise SystemExit("FAILED_V0834_ZIP_CREATED_IN_ONEDRIVE")

summary = {
    "VOILA_V0_8_34_TESTER_PACKAGE_REBUILD_CHECK": "PASS",
    "depends_on_v0833_package_rebuild_preflight": True,
    "source_git_head": git_head,
    "starts_from_normal_home_ui": True,
    "home_status": home_status,
    "existing_generated_course_present": True,
    "input_pdf_present": True,
    "home_course_tools_link_visible": True,
    "home_course_tools_link_href": preferred_course_tools_href,
    "course_tools_from_home_status": course_tools_status,
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
    "fallback_legacy_study_available_when_preview_missing": True,
    "legacy_fallback_status_when_manual_preview_missing": fallback_status,
    "manual_study_items_preview_json_read": True,
    "study_route_legacy_block_unchanged": True,
    "study_route_block_sha256": study_route_hash,
    "package_rebuild_performed": True,
    "package_candidate_path": str(zip_path),
    "package_sha256": sha256,
    "package_sha256_file": str(sha_path),
    "package_manifest_path": str(manifest_path),
    "package_size_bytes": zip_path.stat().st_size,
    "package_zip_entry_count": len(zip_entries),
    "package_contains_web_app": True,
    "package_contains_start_stop_scripts": True,
    "package_contains_manual_study_markers": True,
    "package_contains_policy_notes": True,
    "package_not_in_repo": True,
    "package_not_in_onedrive": True,
    "extracted_package_validation_completed": False,
    "requires_separate_extracted_package_validation": True,
    "requires_final_no_delivery_review": True,
    "requires_explicit_owner_approval_before_share_or_delivery": True,
    "web_app_changed": False,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "manual_study_connected_to_real_study": "packaged_default_manual_study_read_only_with_legacy_fallback",
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
    "build_performed": True,
    "zip_created": True,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "PACKAGE_REBUILD": "PASS_LOCAL_ZIP_CREATED_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_EXTRACTED_PACKAGE_VALIDATION_AND_FINAL_NO_DELIVERY_REVIEW",
    "POLICY": "tester_package_rebuild_local_zip_no_share_no_onedrive_no_delivery_no_distribution",
    "RECOMMENDED_NEXT": "v0.8.35-owner-local-extracted-package-browser-validation-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.34-TESTER-PACKAGE-REBUILD-CHECK.json"
out_md = evidence_dir / "V0.8.34-TESTER-PACKAGE-REBUILD-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.34 Tester package rebuild — no share/no delivery",
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
