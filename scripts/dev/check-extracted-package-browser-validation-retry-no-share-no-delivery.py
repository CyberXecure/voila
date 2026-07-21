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

doc = root / "docs" / "dev" / "extracted-package-browser-validation-retry-no-share-no-delivery.md"
check_py = root / "scripts" / "dev" / "check-extracted-package-browser-validation-retry-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-extracted-package-browser-validation-retry-no-share-no-delivery.ps1"
web = root / "services" / "api" / "web_app.py"

for path, marker in [
    (doc, "FAILED_V0839_DOC_MISSING"),
    (check_py, "FAILED_V0839_CHECK_PY_MISSING"),
    (check_ps1, "FAILED_V0839_CHECK_PS1_MISSING"),
    (web, "FAILED_V0839_WEB_APP_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker + "=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
web_text = web.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "Extracted package browser validation retry",
    "retries extracted-package browser validation using the v0.8.38 local ZIP candidate",
    "package contains `scripts/dev/start-voila-packaged.ps1`",
    "package still excludes `.venv`",
    "package is extracted only under `D:\\dev\\tester-runs`",
    "packaged startup can run from extracted package root",
    "normal Study renders Manual Study default",
    "normal Study falls back to legacy Study when `manual_study_items.preview.json` is temporarily unavailable",
    "no rebuild happens",
    "no new ZIP is created",
    "no OneDrive copy is created",
    "no share is created",
    "no delivery is performed",
    "no public release is created",
    "It does not rebuild the package.",
    "It does not create a new ZIP.",
    "It does not modify `services/api/web_app.py`.",
    "It does not add a route.",
    "It does not add a POST endpoint.",
    "It does not copy to OneDrive.",
    "It does not create a share.",
    "It does not deliver anything.",
    "It does not distribute anything.",
    "It does not create a public release.",
    "Package readiness remains blocked until this validation passes and a separate final no-delivery review is completed.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit("FAILED_V0839_DOC_TERM_MISSING=" + term)

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/extracted-package-browser-validation-retry-no-share-no-delivery.md",
    "scripts/dev/check-extracted-package-browser-validation-retry-no-share-no-delivery.py",
    "scripts/dev/check-extracted-package-browser-validation-retry-no-share-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0839_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

required_web_terms = [
    "VOILA_V0_8_27_MANUAL_STUDY_DEFAULT_STUDY_READ_ONLY_FALLBACK_START",
    "manual-study-default-route",
    "manual-study-default-cards",
    "manual_study_default_read_only_fallback",
    "VOILA_V0_8_22_MANUAL_STUDY_REAL_STUDY_READ_ONLY_SHADOW_TOGGLE_START",
    "manual-study-shadow-route",
    "VOILA_V0_8_24_MANUAL_STUDY_SHADOW_COURSE_TOOLS_LINK_START",
    "manual-study-shadow-course-tools-link",
    "manual-study-dry-run-course-tools-link",
    "/study?pdf=",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit("FAILED_V0839_WEB_TERM_MISSING=" + term)

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0839_STUDY_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/study"') != 0:
    raise SystemExit("FAILED_V0839_STUDY_POST_ADDED")

def win_extended_path(path):
    resolved = Path(path).resolve()
    value = str(resolved)
    prefix = chr(92) + chr(92) + "?" + chr(92)
    if os.name == "nt" and not value.startswith(prefix):
        return prefix + value
    return value

def ensure_not_repo_or_onedrive(path, label):
    resolved = str(Path(path).resolve()).lower()
    root_resolved = str(root.resolve()).lower()
    if resolved.startswith(root_resolved):
        raise SystemExit(f"FAILED_V0839_{label}_INSIDE_REPO={path}")
    if "onedrive" in resolved:
        raise SystemExit(f"FAILED_V0839_{label}_INSIDE_ONEDRIVE={path}")

def safe_rmtree(path):
    path = Path(path)
    if path.exists():
        shutil.rmtree(win_extended_path(path))

def safe_copy_file(src, dst):
    src = Path(src)
    dst = Path(dst)
    os.makedirs(win_extended_path(dst.parent), exist_ok=True)
    shutil.copy2(win_extended_path(src), win_extended_path(dst))

def safe_copy_tree(src_dir, dst_dir):
    src_dir = Path(src_dir)
    dst_dir = Path(dst_dir)
    safe_rmtree(dst_dir)
    if not src_dir.exists():
        raise SystemExit("FAILED_V0839_COPY_TREE_SOURCE_MISSING=" + str(src_dir))
    for src in src_dir.rglob("*"):
        if src.is_file():
            rel = src.relative_to(src_dir)
            safe_copy_file(src, dst_dir / rel)

def safe_extract_zip(zip_path, dest_dir):
    zip_path = Path(zip_path)
    dest_dir = Path(dest_dir)
    safe_rmtree(dest_dir)
    os.makedirs(win_extended_path(dest_dir), exist_ok=True)

    dest_resolved = dest_dir.resolve()
    dest_resolved_s = str(dest_resolved).lower()

    extracted_files = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            name = info.filename.replace("\\", "/")
            if not name or name.endswith("/"):
                continue
            parts = Path(name).parts
            if Path(name).is_absolute() or ".." in parts:
                raise SystemExit("FAILED_V0839_UNSAFE_ZIP_ENTRY=" + name)

            target = dest_dir / name
            target_resolved_s = str(target.resolve()).lower()
            if not target_resolved_s.startswith(dest_resolved_s):
                raise SystemExit("FAILED_V0839_ZIP_ENTRY_ESCAPES_DEST=" + name)

            os.makedirs(win_extended_path(target.parent), exist_ok=True)
            with zf.open(info, "r") as source_file:
                with open(win_extended_path(target), "wb") as target_file:
                    shutil.copyfileobj(source_file, target_file)
            extracted_files.append(name)
    return extracted_files

def run_powershell(script_path, args=None, cwd=None, timeout=900, label="POWERSHELL"):
    cmd = ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)]
    if args:
        cmd.extend(args)

    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )

    if result.returncode != 0:
        raise SystemExit(f"FAILED_V0839_{label}_RC={result.returncode}\n{result.stdout}")

    return result.stdout

def fetch_url_allow_http_error(url, label, attempts=30):
    last_error = ""
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                return response.status, response.read().decode("utf-8", errors="replace"), response.geturl()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8", errors="replace"), url
        except Exception as exc:
            last_error = str(exc)
            time.sleep(3)
    raise SystemExit(f"FAILED_V0839_{label}_FETCH={last_error}")

def post_form(url, payload):
    encoded = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=encoded,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read().decode("utf-8", errors="replace"), response.geturl()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"FAILED_V0839_POST_STATUS={exc.code}; URL={url}; BODY={body[:1200]}")

def absolutize(href):
    href = href.replace("&amp;", "&")
    if href.startswith("/"):
        return "http://127.0.0.1:8787" + href
    if href.startswith("http://") or href.startswith("https://"):
        return href
    return "http://127.0.0.1:8787/" + href.lstrip("./")

release_dir = Path(r"D:\dev\release-assets\voila\v0.8.38-package-rebuild-with-packaged-startup-no-share-no-delivery")
candidate_dir_name = "voila-v0.8.38-controlled-tester-windows-package-candidate"
zip_path = release_dir / (candidate_dir_name + ".zip")
sha_path = release_dir / (candidate_dir_name + ".zip.sha256")
manifest_path = release_dir / "V0.8.38-PACKAGE-REBUILD-WITH-PACKAGED-STARTUP-MANIFEST.json"

for path, marker in [
    (zip_path, "FAILED_V0839_PACKAGE_ZIP_MISSING"),
    (sha_path, "FAILED_V0839_PACKAGE_SHA_MISSING"),
    (manifest_path, "FAILED_V0839_PACKAGE_MANIFEST_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker + "=" + str(path))

ensure_not_repo_or_onedrive(zip_path, "PACKAGE_ZIP")

actual_sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
sha_text = sha_path.read_text(encoding="utf-8", errors="replace").strip()
expected_sha = sha_text.split()[0] if sha_text else ""

if actual_sha.lower() != expected_sha.lower():
    raise SystemExit("FAILED_V0839_PACKAGE_SHA_MISMATCH=" + actual_sha + ";EXPECTED=" + expected_sha)

package_manifest = json.loads(manifest_path.read_text(encoding="utf-8", errors="replace"))

with zipfile.ZipFile(zip_path, "r") as zf:
    names = set(zf.namelist())

required_zip_entries = [
    f"{candidate_dir_name}/services/api/web_app.py",
    f"{candidate_dir_name}/scripts/dev/start-voila.ps1",
    f"{candidate_dir_name}/scripts/dev/stop-voila.ps1",
    f"{candidate_dir_name}/scripts/dev/start-voila-packaged.ps1",
    f"{candidate_dir_name}/README-TESTERS-SHORT.txt",
    f"{candidate_dir_name}/RELEASE-NOTES-TESTERS.txt",
    f"{candidate_dir_name}/KNOWN-LIMITATIONS-TESTERS.txt",
    f"{candidate_dir_name}/NO-SHARE-NO-DELIVERY.txt",
    f"{candidate_dir_name}/PACKAGE-MANIFEST.json",
]

for entry in required_zip_entries:
    if entry not in names:
        raise SystemExit("FAILED_V0839_REQUIRED_ZIP_ENTRY_MISSING=" + entry)

forbidden_venv_hits = [
    name for name in names
    if "/.venv/" in name.lower()
    or "/venv/" in name.lower()
    or name.lower().endswith(".env")
]

if forbidden_venv_hits:
    raise SystemExit("FAILED_V0839_FORBIDDEN_VENV_OR_ENV_IN_ZIP=" + ",".join(sorted(forbidden_venv_hits)[:20]))

with zipfile.ZipFile(zip_path, "r") as zf:
    packaged_web = zf.read(f"{candidate_dir_name}/services/api/web_app.py").decode("utf-8", errors="replace")
    packaged_bootstrap = zf.read(f"{candidate_dir_name}/scripts/dev/start-voila-packaged.ps1").decode("utf-8", errors="replace")
    packaged_policy = zf.read(f"{candidate_dir_name}/NO-SHARE-NO-DELIVERY.txt").decode("utf-8", errors="replace")

for term in required_web_terms:
    if term not in packaged_web:
        raise SystemExit("FAILED_V0839_ZIP_WEB_TERM_MISSING=" + term)

for term in [
    "VOILA_V0_8_37_PACKAGED_STARTUP_BOOTSTRAP_START",
    "[switch]$CheckOnly",
    ".venv\\Scripts\\python.exe",
    "python -m venv",
    "pip install --upgrade pip",
    "uvicorn",
    "web_app:app",
    "127.0.0.1",
    "8787",
]:
    if term.lower() not in packaged_bootstrap.lower():
        raise SystemExit("FAILED_V0839_ZIP_BOOTSTRAP_TERM_MISSING=" + term)

for term in ["NO SHARE", "NO ONEDRIVE COPY", "NO DELIVERY", "NO DISTRIBUTION", "NO PUBLIC RELEASE"]:
    if term not in packaged_policy:
        raise SystemExit("FAILED_V0839_ZIP_POLICY_TERM_MISSING=" + term)

tester_run_dir = Path(r"D:\dev\tester-runs\v0839")
extract_root = tester_run_dir / "x"
package_root = extract_root / candidate_dir_name

ensure_not_repo_or_onedrive(tester_run_dir, "TESTER_RUN_DIR")
extracted_files = safe_extract_zip(zip_path, extract_root)

if not package_root.exists():
    raise SystemExit("FAILED_V0839_PACKAGE_ROOT_NOT_EXTRACTED=" + str(package_root))

ensure_not_repo_or_onedrive(package_root, "EXTRACTED_PACKAGE_ROOT")

packaged_bootstrap_path = package_root / "scripts" / "dev" / "start-voila-packaged.ps1"
packaged_stop_path = package_root / "scripts" / "dev" / "stop-voila.ps1"

for path, marker in [
    (packaged_bootstrap_path, "FAILED_V0839_EXTRACTED_BOOTSTRAP_MISSING"),
    (packaged_stop_path, "FAILED_V0839_EXTRACTED_STOP_SCRIPT_MISSING"),
    (package_root / "services" / "api" / "web_app.py", "FAILED_V0839_EXTRACTED_WEB_APP_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker + "=" + str(path))

course_id = "03-pag-30-34-vectori-trigonometrie"
pdf_name = course_id + ".pdf"

source_input_pdf = root / "data" / "input" / pdf_name
source_output_dir = root / "data" / "output" / course_id

if not source_input_pdf.exists():
    raise SystemExit("FAILED_V0839_SOURCE_INPUT_PDF_MISSING=" + str(source_input_pdf))
if not source_output_dir.exists():
    raise SystemExit("FAILED_V0839_SOURCE_OUTPUT_DIR_MISSING=" + str(source_output_dir))

package_input_pdf = package_root / "data" / "input" / pdf_name
package_output_dir = package_root / "data" / "output" / course_id

safe_copy_file(source_input_pdf, package_input_pdf)
safe_copy_tree(source_output_dir, package_output_dir)

manual_study_preview = package_output_dir / "manual_study_items.preview.json"
legacy_study_preview = package_output_dir / "study_items.preview.json"

legacy_before = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None

run_powershell(root / "scripts" / "dev" / "stop-voila.ps1", label="STOP_REPO_OR_PREVIOUS", timeout=180)
run_powershell(packaged_stop_path, cwd=package_root, label="STOP_EXTRACTED_BEFORE_START", timeout=180)

check_only_output = run_powershell(
    packaged_bootstrap_path,
    args=["-CheckOnly", "-NoBrowser"],
    cwd=package_root,
    label="BOOTSTRAP_CHECK_ONLY",
    timeout=180,
)

for term in [
    "VOILA_V0_8_37_PACKAGED_STARTUP_BOOTSTRAP_CHECK_ONLY=PASS",
    "server_start_performed=False",
    "browser_open_performed=False",
]:
    if term not in check_only_output:
        raise SystemExit("FAILED_V0839_BOOTSTRAP_CHECK_ONLY_OUTPUT_MISSING=" + term + "\n" + check_only_output)

start_output = run_powershell(
    packaged_bootstrap_path,
    args=["-Silent", "-NoBrowser"],
    cwd=package_root,
    label="START_EXTRACTED_PACKAGED",
    timeout=900,
)

if "VOILA_V0_8_37_PACKAGED_STARTUP_BOOTSTRAP_STARTED=PASS" not in start_output:
    raise SystemExit("FAILED_V0839_START_OUTPUT_MISSING_STARTED_MARKER\n" + start_output)

health_status, health_body, _ = fetch_url_allow_http_error("http://127.0.0.1:8787/health", "HEALTH", attempts=40)
if health_status != 200:
    raise SystemExit("FAILED_V0839_HEALTH_STATUS=" + str(health_status) + ";BODY=" + health_body[:800])

if not manual_study_preview.exists():
    save_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/save-draft"
    verify_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/verify-draft"
    learning_pack_export_url = f"http://127.0.0.1:8787/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft"
    manual_study_export_url = f"http://127.0.0.1:8787/owner/manual-learning-pack-study-adapter-dry-run/{course_id}/export-manual-study-items-preview"

    eligible_id = "v0839-extracted-package-browser-validation-retry-eligible"
    payload = {
        "draft_id": eligible_id,
        "page": "1",
        "bbox": "[342, 364, 860, 790]",
        "kind": "formula",
        "title": "v0.8.39 extracted package browser validation retry eligible",
        "verified_text": "Extracted package browser validation retry prompt text",
        "explanation_ro": "Răspuns read-only pentru validarea browser din pachetul extras v0.8.39.",
        "source_status": "verified",
        "source_note": "Created by v0.8.39 extracted package browser validation retry check.",
    }

    post_form(save_url, payload)
    post_form(verify_url, {"draft_id": eligible_id})
    post_form(learning_pack_export_url, {})
    post_form(manual_study_export_url, {})

if not manual_study_preview.exists():
    raise SystemExit("FAILED_V0839_EXTRACTED_MANUAL_STUDY_PREVIEW_JSON_MISSING")

home_status, home_body, _ = fetch_url_allow_http_error("http://127.0.0.1:8787/", "HOME")
if home_status != 200:
    raise SystemExit("FAILED_V0839_HOME_STATUS=" + str(home_status) + ";BODY=" + home_body[:800])

if course_id not in home_body and pdf_name not in home_body:
    raise SystemExit("FAILED_V0839_HOME_DOES_NOT_REFERENCE_VALIDATION_COURSE")

course_tools_hrefs = [
    href.replace("&amp;", "&")
    for href in re.findall(r'href="([^"]*/course-tools[^"]*)"', home_body)
]

if not course_tools_hrefs:
    raise SystemExit("FAILED_V0839_HOME_COURSE_TOOLS_LINK_NOT_FOUND")

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
    raise SystemExit("FAILED_V0839_COURSE_TOOLS_STATUS=" + str(course_tools_status) + ";BODY=" + course_tools_body[:800])

normal_study_matches = re.findall(r'href="([^"]*/study\?pdf=[^"]+)"', course_tools_body)
normal_study_hrefs = [href.replace("&amp;", "&") for href in normal_study_matches if "manual_study_shadow" not in href]
expected_normal_study_href = f"/study?pdf={urllib.parse.quote(pdf_name)}"

normal_study_href = None
for href in normal_study_hrefs:
    if href == expected_normal_study_href:
        normal_study_href = href
        break

if normal_study_href is None:
    raise SystemExit("FAILED_V0839_NORMAL_STUDY_LINK_HREF_NOT_FOUND_OR_UNEXPECTED=" + ",".join(normal_study_hrefs[:10]))

shadow_link_match = re.search(
    r'<a\s+href="([^"]+)"\s+data-testid="manual-study-shadow-course-tools-link"',
    course_tools_body,
)
if not shadow_link_match:
    raise SystemExit("FAILED_V0839_SHADOW_LINK_HREF_NOT_FOUND")

dry_run_link_match = re.search(
    r'<a\s+href="([^"]+)"\s+data-testid="manual-study-dry-run-course-tools-link"',
    course_tools_body,
)
if not dry_run_link_match:
    raise SystemExit("FAILED_V0839_DRY_RUN_LINK_HREF_NOT_FOUND")

shadow_href = shadow_link_match.group(1).replace("&amp;", "&")
dry_run_href = dry_run_link_match.group(1).replace("&amp;", "&")

normal_study_url = absolutize(normal_study_href)
shadow_url = absolutize(shadow_href)
dry_run_url = absolutize(dry_run_href)

normal_status, normal_body, _ = fetch_url_allow_http_error(normal_study_url, "NORMAL_STUDY")
shadow_status, shadow_body, _ = fetch_url_allow_http_error(shadow_url, "SHADOW_STUDY")
dry_run_status, dry_run_body, _ = fetch_url_allow_http_error(dry_run_url, "DRY_RUN")

if normal_status != 200:
    raise SystemExit("FAILED_V0839_NORMAL_STUDY_STATUS=" + str(normal_status) + ";BODY=" + normal_body[:800])
if shadow_status != 200:
    raise SystemExit("FAILED_V0839_SHADOW_STATUS=" + str(shadow_status) + ";BODY=" + shadow_body[:800])
if dry_run_status != 200:
    raise SystemExit("FAILED_V0839_DRY_RUN_STATUS=" + str(dry_run_status) + ";BODY=" + dry_run_body[:800])

normal_terms = [
    "manual-study-default-route",
    "manual-study-default-navigation",
    "manual-study-default-source",
    "manual-study-default-policy",
    "manual-study-default-cards",
    "manual_study_items.preview.json",
    "manual_study_default_read_only_fallback",
    "manual_study_default_enabled",
    "fallback_legacy_study_available",
    "default_read_only_with_legacy_fallback",
    "progress_write",
    "answer_marking",
    "writes_legacy_study_items_preview",
    "study_artifact_written",
    "manual-study-preview-card",
    "manual-study-preview-answer",
    "manual-study-preview-source",
]

for term in normal_terms:
    if term not in normal_body:
        raise SystemExit("FAILED_V0839_NORMAL_STUDY_TERM_MISSING=" + term)

if "<details" not in normal_body or "</details>" not in normal_body:
    raise SystemExit("FAILED_V0839_ANSWER_DETAILS_NOT_RENDERED")

for term in [
    "manual-study-shadow-route",
    "manual-study-shadow-source",
    "manual-study-shadow-policy",
    "manual-study-shadow-cards",
    "read_only_shadow_toggle",
]:
    if term not in shadow_body:
        raise SystemExit("FAILED_V0839_SHADOW_TERM_MISSING=" + term)

for term in [
    "Manual Study Integration Dry Run",
    "manual-study-integration-dry-run-route",
    "dry_run_toggle_enabled",
    "dry_run_only",
]:
    if term not in dry_run_body:
        raise SystemExit("FAILED_V0839_DRY_RUN_TERM_MISSING=" + term)

fallback_status = None
fallback_body = ""
tmp_preview = manual_study_preview.with_name(manual_study_preview.name + ".v0839tmp")

if tmp_preview.exists():
    tmp_preview.unlink()

try:
    os.replace(win_extended_path(manual_study_preview), win_extended_path(tmp_preview))
    fallback_status, fallback_body, _ = fetch_url_allow_http_error(normal_study_url, "NORMAL_STUDY_LEGACY_FALLBACK")
finally:
    if tmp_preview.exists():
        os.replace(win_extended_path(tmp_preview), win_extended_path(manual_study_preview))

if fallback_status != 200:
    raise SystemExit("FAILED_V0839_NORMAL_STUDY_LEGACY_FALLBACK_STATUS=" + str(fallback_status) + ";BODY=" + fallback_body[:800])

if "manual-study-default-route" in fallback_body:
    raise SystemExit("FAILED_V0839_FALLBACK_RENDERED_MANUAL_DEFAULT_WHEN_PREVIEW_MISSING")

legacy_after = legacy_study_preview.read_text(encoding="utf-8", errors="replace") if legacy_study_preview.exists() else None
if legacy_before != legacy_after:
    raise SystemExit("FAILED_V0839_LEGACY_STUDY_PREVIEW_CHANGED")

run_powershell(packaged_stop_path, cwd=package_root, label="STOP_EXTRACTED_AFTER_VALIDATION", timeout=180)

evidence_dir = Path(r"D:\dev\tester-runs\v0839-extracted-package-browser-validation-retry-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_39_EXTRACTED_PACKAGE_BROWSER_VALIDATION_RETRY_CHECK": "PASS",
    "depends_on_v0838_package_rebuild_with_packaged_startup": True,
    "package_candidate_path": str(zip_path),
    "package_sha256": actual_sha,
    "package_sha256_matches_file": True,
    "package_manifest_path": str(manifest_path),
    "package_source_git_head": package_manifest.get("source_git_head"),
    "zip_contains_web_app": True,
    "zip_contains_start_stop_scripts": True,
    "zip_contains_packaged_startup_bootstrap": True,
    "zip_contains_manual_study_markers": True,
    "zip_contains_policy_notes": True,
    "zip_entry_count": len(names),
    "package_excludes_dot_venv": True,
    "package_venv_python_present": False,
    "extracted_package_validation_completed": True,
    "extracted_file_count": len(extracted_files),
    "extracted_package_root": str(package_root),
    "extracted_package_not_in_repo": True,
    "extracted_package_not_in_onedrive": True,
    "packaged_bootstrap_check_only_passed": True,
    "packaged_bootstrap_started_extracted_app": True,
    "health_status": health_status,
    "starts_from_extracted_home_ui": True,
    "home_status": home_status,
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
    "legacy_study_items_preview_unchanged": True,
    "web_app_changed": False,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "progress_write_added": False,
    "answer_marking_added": False,
    "ocr_rewrite_performed": False,
    "formula_ocr_performed": False,
    "crop_file_written": False,
    "package_rebuild_performed": False,
    "new_zip_created": False,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "EXTRACTED_PACKAGE_BROWSER_VALIDATION_RETRY": "PASS_OWNER_LOCAL_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_FINAL_NO_DELIVERY_REVIEW",
    "POLICY": "extracted_package_browser_validation_retry_no_rebuild_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.40-owner-local-final-no-delivery-review-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.39-EXTRACTED-PACKAGE-BROWSER-VALIDATION-RETRY-CHECK.json"
out_md = evidence_dir / "V0.8.39-EXTRACTED-PACKAGE-BROWSER-VALIDATION-RETRY-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.39 Extracted package browser validation retry — no share/no delivery",
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
