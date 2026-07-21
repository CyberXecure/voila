from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

root = Path(".").resolve()

doc = root / "docs" / "dev" / "package-runtime-fix-or-rebuild-preflight-no-share-no-delivery.md"
check_py = root / "scripts" / "dev" / "check-package-runtime-fix-or-rebuild-preflight-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-package-runtime-fix-or-rebuild-preflight-no-share-no-delivery.ps1"
web = root / "services" / "api" / "web_app.py"
start_script = root / "scripts" / "dev" / "start-voila.ps1"

for path, marker in [
    (doc, "FAILED_V0836_DOC_MISSING"),
    (check_py, "FAILED_V0836_CHECK_PY_MISSING"),
    (check_ps1, "FAILED_V0836_CHECK_PS1_MISSING"),
    (web, "FAILED_V0836_WEB_APP_MISSING"),
    (start_script, "FAILED_V0836_START_SCRIPT_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker + "=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
web_text = web.read_text(encoding="utf-8", errors="replace")
start_text = start_script.read_text(encoding="utf-8", errors="replace")
start_lower = start_text.lower()

required_doc_terms = [
    "Package runtime fix/rebuild preflight",
    "v0.8.35 confirmed that the v0.8.34 tester ZIP is not self-startable after extraction",
    "the ZIP excludes `.venv`",
    "`scripts/dev/start-voila.ps1` requires `.venv\\Scripts\\python.exe`",
    "This milestone is a preflight/decision milestone only.",
    "It does not rebuild the package.",
    "It does not create a new ZIP.",
    "It does not extract the package.",
    "It does not start the extracted package.",
    "It does not modify `services/api/web_app.py`.",
    "Option A — include `.venv` in the tester ZIP",
    "Option B — add a packaged bootstrap/start script",
    "Use Option B first.",
    "`scripts/dev/start-voila-packaged.ps1`",
    "v0.8.37 — packaged startup bootstrap implementation, no ZIP",
    "v0.8.38 — package rebuild with packaged startup, no share/no delivery",
    "v0.8.39 — extracted-package browser validation retry, no share/no delivery",
    "No package rebuild.",
    "No new ZIP.",
    "No extraction.",
    "No app behavior change.",
    "No `services/api/web_app.py` change.",
    "No route change.",
    "No Progress write.",
    "No answer marking.",
    "No OneDrive copy.",
    "No share.",
    "No delivery.",
    "No distribution.",
    "No public release.",
    "Package readiness remains blocked.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit("FAILED_V0836_DOC_TERM_MISSING=" + term)

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/package-runtime-fix-or-rebuild-preflight-no-share-no-delivery.md",
    "scripts/dev/check-package-runtime-fix-or-rebuild-preflight-no-share-no-delivery.py",
    "scripts/dev/check-package-runtime-fix-or-rebuild-preflight-no-share-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0836_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

if ".venv" not in start_lower or "python.exe" not in start_lower:
    raise SystemExit("FAILED_V0836_CURRENT_START_SCRIPT_VENV_REQUIREMENT_NOT_CONFIRMED")

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
        raise SystemExit("FAILED_V0836_WEB_TERM_MISSING=" + term)

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0836_STUDY_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/study"') != 0:
    raise SystemExit("FAILED_V0836_STUDY_POST_ADDED")

release_dir = Path(r"D:\dev\release-assets\voila\v0.8.34-tester-package-rebuild-no-share-no-delivery")
candidate_dir_name = "voila-v0.8.34-controlled-tester-windows-package-candidate"

zip_path = release_dir / (candidate_dir_name + ".zip")
sha_path = release_dir / (candidate_dir_name + ".zip.sha256")
manifest_path = release_dir / "V0.8.34-TESTER-PACKAGE-REBUILD-MANIFEST.json"

for path, marker in [
    (zip_path, "FAILED_V0836_PACKAGE_ZIP_MISSING"),
    (sha_path, "FAILED_V0836_PACKAGE_SHA_MISSING"),
    (manifest_path, "FAILED_V0836_PACKAGE_MANIFEST_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker + "=" + str(path))

zip_resolved = str(zip_path.resolve()).lower()
root_resolved = str(root.resolve()).lower()

if zip_resolved.startswith(root_resolved):
    raise SystemExit("FAILED_V0836_PACKAGE_ZIP_INSIDE_REPO=" + str(zip_path))

if "onedrive" in zip_resolved:
    raise SystemExit("FAILED_V0836_PACKAGE_ZIP_IN_ONEDRIVE=" + str(zip_path))

actual_sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
sha_text = sha_path.read_text(encoding="utf-8", errors="replace").strip()
expected_sha = sha_text.split()[0] if sha_text else ""

if actual_sha.lower() != expected_sha.lower():
    raise SystemExit("FAILED_V0836_PACKAGE_SHA_MISMATCH=" + actual_sha + ";EXPECTED=" + expected_sha)

package_manifest = json.loads(manifest_path.read_text(encoding="utf-8", errors="replace"))

with zipfile.ZipFile(zip_path, "r") as zf:
    names = set(zf.namelist())

    required_entries = [
        f"{candidate_dir_name}/services/api/web_app.py",
        f"{candidate_dir_name}/scripts/dev/start-voila.ps1",
        f"{candidate_dir_name}/scripts/dev/stop-voila.ps1",
        f"{candidate_dir_name}/README-TESTERS-SHORT.txt",
        f"{candidate_dir_name}/RELEASE-NOTES-TESTERS.txt",
        f"{candidate_dir_name}/KNOWN-LIMITATIONS-TESTERS.txt",
        f"{candidate_dir_name}/NO-SHARE-NO-DELIVERY.txt",
        f"{candidate_dir_name}/PACKAGE-MANIFEST.json",
    ]

    for entry in required_entries:
        if entry not in names:
            raise SystemExit("FAILED_V0836_REQUIRED_ZIP_ENTRY_MISSING=" + entry)

    packaged_start = zf.read(f"{candidate_dir_name}/scripts/dev/start-voila.ps1").decode("utf-8", errors="replace")
    packaged_web = zf.read(f"{candidate_dir_name}/services/api/web_app.py").decode("utf-8", errors="replace")

packaged_start_lower = packaged_start.lower()
packaged_start_requires_venv = ".venv" in packaged_start_lower and "python.exe" in packaged_start_lower
package_venv_python_present = f"{candidate_dir_name}/.venv/Scripts/python.exe" in names
package_has_any_venv = any("/.venv/" in name.lower() for name in names)
packaged_bootstrap_present = f"{candidate_dir_name}/scripts/dev/start-voila-packaged.ps1" in names

if not packaged_start_requires_venv:
    raise SystemExit("FAILED_V0836_PACKAGED_START_VENV_REQUIREMENT_NOT_CONFIRMED")

if package_venv_python_present or package_has_any_venv:
    raise SystemExit("FAILED_V0836_EXPECTED_NO_VENV_IN_CURRENT_PACKAGE_BUT_FOUND")

if packaged_bootstrap_present:
    raise SystemExit("FAILED_V0836_UNEXPECTED_PACKAGED_BOOTSTRAP_ALREADY_IN_CURRENT_PACKAGE")

for term in required_web_terms:
    if term not in packaged_web:
        raise SystemExit("FAILED_V0836_PACKAGED_WEB_TERM_MISSING=" + term)

evidence_dir = Path(r"D:\dev\tester-runs\v0836-package-runtime-fix-or-rebuild-preflight-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_36_PACKAGE_RUNTIME_FIX_OR_REBUILD_PREFLIGHT_CHECK": "PASS",
    "depends_on_v0835_blocker_evidence": True,
    "current_package_not_self_startable": True,
    "blocker_confirmed": "EXTRACTED_PACKAGE_MISSING_VENV_RUNTIME",
    "root_cause_confirmed": "package_excludes_dot_venv_but_start_script_requires_dot_venv_scripts_python_exe",
    "package_candidate_path": str(zip_path),
    "package_sha256": actual_sha,
    "package_sha256_matches_file": True,
    "package_manifest_path": str(manifest_path),
    "package_source_git_head": package_manifest.get("source_git_head"),
    "zip_contains_web_app": True,
    "zip_contains_start_stop_scripts": True,
    "zip_contains_policy_notes": True,
    "zip_contains_manual_study_markers": True,
    "zip_entry_count": len(names),
    "current_owner_start_script_requires_venv": True,
    "packaged_start_script_requires_venv": True,
    "package_venv_python_present": False,
    "package_has_any_venv": False,
    "packaged_bootstrap_present": False,
    "option_a_include_venv_considered": True,
    "option_b_packaged_bootstrap_considered": True,
    "recommended_runtime_strategy": "OPTION_B_PACKAGED_BOOTSTRAP_START_SCRIPT_FIRST",
    "recommended_next_implementation": "add_scripts_dev_start_voila_packaged_ps1_without_rebuild",
    "recommended_next_rebuild_after_bootstrap": "separate_owner_local_package_rebuild_no_share_no_delivery",
    "recommended_next_validation_after_rebuild": "separate_extracted_package_browser_validation_retry_no_share_no_delivery",
    "web_app_changed": False,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "study_changed": False,
    "progress_write_added": False,
    "answer_marking_added": False,
    "ocr_rewrite_performed": False,
    "formula_ocr_performed": False,
    "crop_file_written": False,
    "package_rebuild_performed": False,
    "new_zip_created": False,
    "package_extracted": False,
    "extracted_package_started": False,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "PACKAGE_RUNTIME_PREFLIGHT": "PASS_RUNTIME_STRATEGY_SELECTED_NO_REBUILD_NO_ZIP",
    "PACKAGE_READINESS": "BLOCKED_PENDING_PACKAGED_BOOTSTRAP_REBUILD_AND_EXTRACTED_VALIDATION",
    "POLICY": "package_runtime_preflight_no_rebuild_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.37-owner-local-packaged-startup-bootstrap-no-build-no-zip-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.36-PACKAGE-RUNTIME-FIX-OR-REBUILD-PREFLIGHT-CHECK.json"
out_md = evidence_dir / "V0.8.36-PACKAGE-RUNTIME-FIX-OR-REBUILD-PREFLIGHT-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.36 Package runtime fix/rebuild preflight — no share/no delivery",
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
