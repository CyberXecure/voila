from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile

root = Path(".").resolve()

doc = root / "docs" / "dev" / "package-rebuild-with-packaged-startup-no-share-no-delivery.md"
check_py = root / "scripts" / "dev" / "check-package-rebuild-with-packaged-startup-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-package-rebuild-with-packaged-startup-no-share-no-delivery.ps1"
web = root / "services" / "api" / "web_app.py"
bootstrap = root / "scripts" / "dev" / "start-voila-packaged.ps1"

for path, marker in [
    (doc, "FAILED_V0838_DOC_MISSING"),
    (check_py, "FAILED_V0838_CHECK_PY_MISSING"),
    (check_ps1, "FAILED_V0838_CHECK_PS1_MISSING"),
    (web, "FAILED_V0838_WEB_APP_MISSING"),
    (bootstrap, "FAILED_V0838_BOOTSTRAP_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker + "=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
web_text = web.read_text(encoding="utf-8", errors="replace")
bootstrap_text = bootstrap.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "Package rebuild with packaged startup",
    "rebuilds the local tester ZIP candidate with the packaged startup bootstrap added in v0.8.37",
    "`scripts/dev/start-voila-packaged.ps1`",
    "The package must still exclude `.venv`.",
    "This milestone creates a local ZIP candidate only under `D:\\dev\\release-assets`.",
    "This milestone does not copy to OneDrive.",
    "This milestone does not create a share.",
    "This milestone does not deliver anything.",
    "This milestone does not distribute anything.",
    "This milestone does not create a public release.",
    "This milestone does not modify `services/api/web_app.py`.",
    "This milestone does not add a route.",
    "This milestone does not add a POST endpoint.",
    "This milestone does not change Study behavior.",
    "This milestone does not write Progress.",
    "This milestone does not mark answers.",
    "This milestone does not perform extracted-package browser validation.",
    "v0.8.39 must retry extracted-package browser validation using this rebuilt package.",
    "Package readiness remains blocked until extracted-package validation passes.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit("FAILED_V0838_DOC_TERM_MISSING=" + term)

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/package-rebuild-with-packaged-startup-no-share-no-delivery.md",
    "scripts/dev/check-package-rebuild-with-packaged-startup-no-share-no-delivery.py",
    "scripts/dev/check-package-rebuild-with-packaged-startup-no-share-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0838_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

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
        raise SystemExit("FAILED_V0838_WEB_TERM_MISSING=" + term)

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0838_STUDY_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/study"') != 0:
    raise SystemExit("FAILED_V0838_STUDY_POST_ADDED")

required_bootstrap_terms = [
    "VOILA_V0_8_37_PACKAGED_STARTUP_BOOTSTRAP_START",
    "[switch]$CheckOnly",
    ".venv\\Scripts\\python.exe",
    "python -m venv",
    "pip install --upgrade pip",
    "pip install -r",
    "uvicorn",
    "web_app:app",
    "127.0.0.1",
    "8787",
    "VOILA_V0_8_37_PACKAGED_STARTUP_BOOTSTRAP_CHECK_ONLY=PASS",
]

bootstrap_lower = bootstrap_text.lower()
for term in required_bootstrap_terms:
    if term.lower() not in bootstrap_lower:
        raise SystemExit("FAILED_V0838_BOOTSTRAP_TERM_MISSING=" + term)

def win_extended_path(path):
    resolved = Path(path).resolve()
    value = str(resolved)
    prefix = chr(92) + chr(92) + "?" + chr(92)
    if os.name == "nt" and not value.startswith(prefix):
        return prefix + value
    return value

def safe_rmtree(path):
    path = Path(path)
    if path.exists():
        shutil.rmtree(win_extended_path(path))

def safe_copy_file(src, dst):
    src = Path(src)
    dst = Path(dst)
    os.makedirs(win_extended_path(dst.parent), exist_ok=True)
    shutil.copy2(win_extended_path(src), win_extended_path(dst))

def safe_write_text(path, text):
    path = Path(path)
    os.makedirs(win_extended_path(path.parent), exist_ok=True)
    path.write_text(text, encoding="utf-8")

def ensure_not_repo_or_onedrive(path, label):
    resolved = str(Path(path).resolve()).lower()
    root_resolved = str(root.resolve()).lower()
    if resolved.startswith(root_resolved):
        raise SystemExit(f"FAILED_V0838_{label}_INSIDE_REPO={path}")
    if "onedrive" in resolved:
        raise SystemExit(f"FAILED_V0838_{label}_INSIDE_ONEDRIVE={path}")

def should_exclude(rel):
    rel_posix = rel.replace("\\", "/")
    rel_lower = rel_posix.lower()

    excluded_prefixes = [
        ".git/",
        ".venv/",
        "venv/",
        "node_modules/",
        "__pycache__/",
        ".pytest_cache/",
        ".mypy_cache/",
        ".ruff_cache/",
        "dist/",
        "build/",
        "release-assets/",
        "tester-runs/",
    ]

    excluded_parts = [
        "/__pycache__/",
        "/.pytest_cache/",
        "/.mypy_cache/",
        "/.ruff_cache/",
        "/node_modules/",
        "/.venv/",
        "/venv/",
    ]

    excluded_suffixes = [
        ".pyc",
        ".pyo",
        ".pyd",
        ".sqlite",
        ".sqlite3",
        ".db",
        ".log",
        ".tmp",
        ".bak",
        ".key",
        ".pem",
        ".pfx",
        ".env",
    ]

    secret_terms = [
        "secret",
        "token",
        "apikey",
        "api_key",
        "password",
        "credential",
        "credentials",
    ]

    if any(rel_lower.startswith(prefix) for prefix in excluded_prefixes):
        return True
    if any(part in rel_lower for part in excluded_parts):
        return True
    if any(rel_lower.endswith(suffix) for suffix in excluded_suffixes):
        return True
    if any(term in rel_lower for term in secret_terms):
        return True
    return False

release_dir = Path(r"D:\dev\release-assets\voila\v0.8.38-package-rebuild-with-packaged-startup-no-share-no-delivery")
candidate_dir_name = "voila-v0.8.38-controlled-tester-windows-package-candidate"
staging_dir = release_dir / "_s"
package_root = staging_dir / candidate_dir_name
zip_path = release_dir / (candidate_dir_name + ".zip")
sha_path = release_dir / (candidate_dir_name + ".zip.sha256")
manifest_path = release_dir / "V0.8.38-PACKAGE-REBUILD-WITH-PACKAGED-STARTUP-MANIFEST.json"

ensure_not_repo_or_onedrive(release_dir, "RELEASE_DIR")
ensure_not_repo_or_onedrive(zip_path, "PACKAGE_ZIP")

release_dir.mkdir(parents=True, exist_ok=True)
safe_rmtree(staging_dir)

tracked = subprocess.check_output(
    ["git", "ls-files"],
    cwd=str(root),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

files_to_package = []
for rel in tracked:
    rel = rel.strip()
    if not rel:
        continue
    rel_norm = rel.replace("\\", "/")
    if should_exclude(rel_norm):
        continue
    src = root / rel_norm
    if src.is_file():
        files_to_package.append(rel_norm)

required_repo_entries = [
    "services/api/web_app.py",
    "scripts/dev/start-voila.ps1",
    "scripts/dev/stop-voila.ps1",
    "scripts/dev/start-voila-packaged.ps1",
]

for entry in required_repo_entries:
    if entry not in files_to_package:
        raise SystemExit("FAILED_V0838_REQUIRED_REPO_ENTRY_NOT_PACKAGED=" + entry)

for rel in files_to_package:
    safe_copy_file(root / rel, package_root / rel)

policy_text = """VOILA v0.8.38 controlled tester package candidate

NO SHARE.
NO ONEDRIVE COPY.
NO DELIVERY.
NO DISTRIBUTION.
NO PUBLIC RELEASE.

This package is owner-local only until extracted-package browser validation and final no-delivery review pass.

Use scripts/dev/start-voila-packaged.ps1 for future extracted-package startup validation.
"""

readme_text = """Voila controlled tester package candidate v0.8.38

This local candidate includes packaged startup bootstrap support.

Do not share.
Do not copy to OneDrive.
Do not deliver.
Do not distribute.
Do not create a public release.
"""

release_notes_text = """v0.8.38

- Rebuilt local package candidate with scripts/dev/start-voila-packaged.ps1.
- Keeps package owner-local.
- Keeps readiness blocked pending extracted-package browser validation.
"""

known_limitations_text = """Known limitations

- Package has not yet passed extracted-package browser validation.
- Package readiness remains blocked.
- Sharing and delivery remain blocked.
"""

safe_write_text(package_root / "NO-SHARE-NO-DELIVERY.txt", policy_text)
safe_write_text(package_root / "README-TESTERS-SHORT.txt", readme_text)
safe_write_text(package_root / "RELEASE-NOTES-TESTERS.txt", release_notes_text)
safe_write_text(package_root / "KNOWN-LIMITATIONS-TESTERS.txt", known_limitations_text)

source_git_head = subprocess.check_output(
    ["git", "rev-parse", "HEAD"],
    cwd=str(root),
    text=True,
    encoding="utf-8",
    errors="replace",
).strip()

package_manifest = {
    "package": candidate_dir_name,
    "milestone": "v0.8.38-owner-local-package-rebuild-with-packaged-startup-no-share-no-delivery",
    "source_git_head": source_git_head,
    "packaged_startup_bootstrap_included": True,
    "package_excludes_dot_venv": True,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
}

safe_write_text(package_root / "PACKAGE-MANIFEST.json", json.dumps(package_manifest, ensure_ascii=False, indent=2) + "\n")

check_only = subprocess.run(
    [
        "pwsh",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(package_root / "scripts" / "dev" / "start-voila-packaged.ps1"),
        "-CheckOnly",
        "-NoBrowser",
    ],
    cwd=str(package_root),
    text=True,
    encoding="utf-8",
    errors="replace",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    timeout=90,
)

if check_only.returncode != 0:
    raise SystemExit("FAILED_V0838_PACKAGED_BOOTSTRAP_CHECK_ONLY_RC=" + str(check_only.returncode) + "\n" + check_only.stdout)

for term in [
    "VOILA_V0_8_37_PACKAGED_STARTUP_BOOTSTRAP_START",
    "VOILA_V0_8_37_PACKAGED_STARTUP_BOOTSTRAP_CHECK_ONLY=PASS",
    "venv_create_performed=False",
    "dependency_install_performed=False",
    "server_start_performed=False",
    "browser_open_performed=False",
]:
    if term not in check_only.stdout:
        raise SystemExit("FAILED_V0838_PACKAGED_BOOTSTRAP_CHECK_ONLY_OUTPUT_MISSING=" + term + "\n" + check_only.stdout)

if zip_path.exists():
    zip_path.unlink()
if sha_path.exists():
    sha_path.unlink()

zip_entries = []
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for file_path in package_root.rglob("*"):
        if not file_path.is_file():
            continue
        rel_zip = str(file_path.relative_to(staging_dir)).replace("\\", "/")
        if "/.venv/" in rel_zip.lower() or rel_zip.lower().endswith(".env"):
            raise SystemExit("FAILED_V0838_FORBIDDEN_FILE_IN_STAGING=" + rel_zip)
        with open(win_extended_path(file_path), "rb") as source_file:
            zf.writestr(rel_zip, source_file.read())
        zip_entries.append(rel_zip)

actual_sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
sha_path.write_text(actual_sha + "  " + zip_path.name + "\n", encoding="utf-8")

package_size = zip_path.stat().st_size

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
        raise SystemExit("FAILED_V0838_REQUIRED_ZIP_ENTRY_MISSING=" + entry)

forbidden_zip_hits = [
    name for name in names
    if "/.venv/" in name.lower()
    or "/venv/" in name.lower()
    or name.lower().endswith(".env")
]

if forbidden_zip_hits:
    raise SystemExit("FAILED_V0838_FORBIDDEN_ZIP_HITS=" + ",".join(sorted(forbidden_zip_hits)[:20]))

with zipfile.ZipFile(zip_path, "r") as zf:
    packaged_web = zf.read(f"{candidate_dir_name}/services/api/web_app.py").decode("utf-8", errors="replace")
    packaged_bootstrap = zf.read(f"{candidate_dir_name}/scripts/dev/start-voila-packaged.ps1").decode("utf-8", errors="replace")
    packaged_policy = zf.read(f"{candidate_dir_name}/NO-SHARE-NO-DELIVERY.txt").decode("utf-8", errors="replace")

for term in required_web_terms:
    if term not in packaged_web:
        raise SystemExit("FAILED_V0838_ZIP_WEB_TERM_MISSING=" + term)

for term in required_bootstrap_terms:
    if term.lower() not in packaged_bootstrap.lower():
        raise SystemExit("FAILED_V0838_ZIP_BOOTSTRAP_TERM_MISSING=" + term)

for term in ["NO SHARE", "NO ONEDRIVE COPY", "NO DELIVERY", "NO DISTRIBUTION", "NO PUBLIC RELEASE"]:
    if term not in packaged_policy:
        raise SystemExit("FAILED_V0838_ZIP_POLICY_TERM_MISSING=" + term)

manifest_summary = {
    **package_manifest,
    "package_candidate_path": str(zip_path),
    "package_sha256": actual_sha,
    "package_size_bytes": package_size,
    "package_zip_entry_count": len(names),
}
manifest_path.write_text(json.dumps(manifest_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

evidence_dir = Path(r"D:\dev\tester-runs\v0838-package-rebuild-with-packaged-startup-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_38_PACKAGE_REBUILD_WITH_PACKAGED_STARTUP_CHECK": "PASS",
    "depends_on_v0837_packaged_startup_bootstrap": True,
    "package_rebuild_performed": True,
    "new_zip_created": True,
    "package_candidate_path": str(zip_path),
    "package_sha256": actual_sha,
    "package_sha256_file": str(sha_path),
    "package_manifest_path": str(manifest_path),
    "source_git_head": source_git_head,
    "package_size_bytes": package_size,
    "package_zip_entry_count": len(names),
    "package_contains_web_app": True,
    "package_contains_start_stop_scripts": True,
    "package_contains_packaged_startup_bootstrap": True,
    "package_contains_manual_study_markers": True,
    "package_contains_policy_notes": True,
    "packaged_bootstrap_check_only_passed_in_staging": True,
    "packaged_bootstrap_check_only_created_venv": False,
    "packaged_bootstrap_check_only_installed_dependencies": False,
    "packaged_bootstrap_check_only_started_server": False,
    "packaged_bootstrap_check_only_opened_browser": False,
    "package_excludes_dot_venv": True,
    "package_venv_python_present": False,
    "package_has_any_venv": False,
    "package_not_in_repo": True,
    "package_not_in_onedrive": True,
    "extracted_package_validation_completed": False,
    "requires_separate_extracted_package_validation_retry": True,
    "requires_final_no_delivery_review": True,
    "requires_explicit_owner_approval_before_share_or_delivery": True,
    "web_app_changed": False,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "study_changed": False,
    "progress_write_added": False,
    "answer_marking_added": False,
    "ocr_rewrite_performed": False,
    "formula_ocr_performed": False,
    "crop_file_written": False,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "PACKAGE_REBUILD": "PASS_LOCAL_ZIP_CREATED_WITH_PACKAGED_STARTUP_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_EXTRACTED_PACKAGE_VALIDATION_RETRY_AND_FINAL_NO_DELIVERY_REVIEW",
    "POLICY": "package_rebuild_with_packaged_startup_no_share_no_onedrive_no_delivery_no_distribution",
    "RECOMMENDED_NEXT": "v0.8.39-owner-local-extracted-package-browser-validation-retry-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.38-PACKAGE-REBUILD-WITH-PACKAGED-STARTUP-CHECK.json"
out_md = evidence_dir / "V0.8.38-PACKAGE-REBUILD-WITH-PACKAGED-STARTUP-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.38 Package rebuild with packaged startup — no share/no delivery",
    "",
    "## Summary",
]
for key, value in summary.items():
    md_lines.append(f"- {key}: {value}")

out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

safe_rmtree(staging_dir)

for k, v in summary.items():
    print(f"{k}={v}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
