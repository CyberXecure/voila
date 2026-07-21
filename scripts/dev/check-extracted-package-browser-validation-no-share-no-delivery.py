from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "extracted-package-browser-validation-no-share-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0835_WEB_APP_MISSING"),
    (doc, "FAILED_V0835_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "Extracted package browser validation BLOCKED",
    "Extracted-package browser validation is blocked.",
    ".venv\\Scripts\\python.exe",
    "Nu gasesc Python venv",
    "The v0.8.34 package rebuild copied tracked repository files and intentionally excluded `.venv`.",
    "the ZIP is not self-startable after extraction",
    "This milestone records blocker evidence only.",
    "It does not extract the package.",
    "It does not start the extracted package.",
    "It does not rebuild the ZIP.",
    "It does not create a new ZIP.",
    "It does not copy to OneDrive.",
    "It does not create a share.",
    "It does not deliver anything.",
    "It does not distribute anything.",
    "A separate package runtime fix/rebuild milestone is required before extracted-package browser validation can pass.",
    "No share.",
    "No OneDrive copy.",
    "No delivery.",
    "No distribution.",
    "No public release.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit(f"FAILED_V0835_DOC_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/extracted-package-browser-validation-no-share-no-delivery.md",
    "scripts/dev/check-extracted-package-browser-validation-no-share-no-delivery.py",
    "scripts/dev/check-extracted-package-browser-validation-no-share-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0835_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

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
        raise SystemExit(f"FAILED_V0835_REPO_WEB_TERM_MISSING={term}")

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0835_STUDY_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/study"') != 0:
    raise SystemExit("FAILED_V0835_STUDY_POST_ADDED")

release_dir = Path(r"D:\dev\release-assets\voila\v0.8.34-tester-package-rebuild-no-share-no-delivery")
candidate_dir_name = "voila-v0.8.34-controlled-tester-windows-package-candidate"

zip_path = release_dir / (candidate_dir_name + ".zip")
sha_path = release_dir / (candidate_dir_name + ".zip.sha256")
manifest_path = release_dir / "V0.8.34-TESTER-PACKAGE-REBUILD-MANIFEST.json"

for path, marker in [
    (zip_path, "FAILED_V0835_PACKAGE_ZIP_MISSING"),
    (sha_path, "FAILED_V0835_PACKAGE_SHA_FILE_MISSING"),
    (manifest_path, "FAILED_V0835_PACKAGE_MANIFEST_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker + "=" + str(path))

zip_resolved = str(zip_path.resolve()).lower()
root_resolved = str(root.resolve()).lower()

if zip_resolved.startswith(root_resolved):
    raise SystemExit("FAILED_V0835_PACKAGE_ZIP_INSIDE_REPO=" + str(zip_path))

if "onedrive" in zip_resolved:
    raise SystemExit("FAILED_V0835_PACKAGE_ZIP_IN_ONEDRIVE=" + str(zip_path))

actual_sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
sha_text = sha_path.read_text(encoding="utf-8", errors="replace").strip()
expected_sha = sha_text.split()[0] if sha_text else ""

if actual_sha.lower() != expected_sha.lower():
    raise SystemExit("FAILED_V0835_PACKAGE_SHA_MISMATCH=" + actual_sha + ";EXPECTED=" + expected_sha)

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
            raise SystemExit("FAILED_V0835_REQUIRED_ZIP_ENTRY_MISSING=" + entry)

    packaged_web = zf.read(f"{candidate_dir_name}/services/api/web_app.py").decode("utf-8", errors="replace")
    packaged_start = zf.read(f"{candidate_dir_name}/scripts/dev/start-voila.ps1").decode("utf-8", errors="replace")
    packaged_policy = zf.read(f"{candidate_dir_name}/NO-SHARE-NO-DELIVERY.txt").decode("utf-8", errors="replace")

for term in required_web_terms:
    if term not in packaged_web:
        raise SystemExit(f"FAILED_V0835_ZIP_WEB_TERM_MISSING={term}")

package_venv_python_present = f"{candidate_dir_name}/.venv/Scripts/python.exe" in names
package_has_any_venv = any("/.venv/" in name.lower() for name in names)

packaged_start_lower = packaged_start.lower()
start_script_requires_venv = ".venv" in packaged_start_lower and "python.exe" in packaged_start_lower
policy_notes_present = "NO SHARE" in packaged_policy and "NO DELIVERY" in packaged_policy

if not start_script_requires_venv:
    raise SystemExit("FAILED_V0835_START_SCRIPT_VENV_REQUIREMENT_NOT_CONFIRMED")

if package_venv_python_present or package_has_any_venv:
    raise SystemExit("FAILED_V0835_EXPECTED_MISSING_VENV_BUT_VENV_FOUND_IN_ZIP")

if not policy_notes_present:
    raise SystemExit("FAILED_V0835_POLICY_NOTES_NOT_CONFIRMED")

evidence_dir = Path(r"D:\dev\tester-runs\v0835-extracted-package-browser-validation-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_35_EXTRACTED_PACKAGE_BROWSER_VALIDATION_CHECK": "FAIL",
    "VOILA_V0_8_35_BLOCKER_EVIDENCE_RECORDED": "PASS",
    "depends_on_v0834b_package_rebuild_final_main": True,
    "blocker": "EXTRACTED_PACKAGE_MISSING_VENV_RUNTIME",
    "root_cause": "package_excludes_dot_venv_but_start_script_requires_dot_venv_scripts_python_exe",
    "package_zip_exists": True,
    "package_candidate_path": str(zip_path),
    "package_sha256": actual_sha,
    "package_sha256_matches_file": True,
    "package_manifest_path": str(manifest_path),
    "package_source_git_head": package_manifest.get("source_git_head"),
    "zip_contains_web_app": True,
    "zip_contains_start_stop_scripts": True,
    "zip_contains_manual_study_markers": True,
    "zip_contains_policy_notes": True,
    "zip_entry_count": len(names),
    "start_script_requires_venv": True,
    "required_venv_python": ".venv\\Scripts\\python.exe",
    "package_venv_python_present": False,
    "package_has_any_venv": False,
    "extracted_package_validation_completed": False,
    "extracted_voila_started": False,
    "browser_validation_completed": False,
    "normal_study_link_renders_manual_default": False,
    "requires_separate_package_runtime_fix_or_rebuild": True,
    "requires_separate_extracted_package_validation_retry": True,
    "requires_final_no_delivery_review": True,
    "requires_explicit_owner_approval_before_share_or_delivery": True,
    "web_app_changed": False,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "progress_write_added": False,
    "answer_marking_added": False,
    "package_rebuild_performed": False,
    "new_zip_created": False,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "EXTRACTED_PACKAGE_BROWSER_VALIDATION": "BLOCKED_MISSING_VENV_RUNTIME_NO_BROWSER_VALIDATION",
    "PACKAGE_READINESS": "BLOCKED_MISSING_RUNTIME_VENV_NO_EXTRACTED_BROWSER_VALIDATION",
    "POLICY": "record_extracted_package_validation_blocker_no_rebuild_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.36-owner-local-package-runtime-fix-or-rebuild-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.35-EXTRACTED-PACKAGE-BROWSER-VALIDATION-BLOCKED.json"
out_md = evidence_dir / "V0.8.35-EXTRACTED-PACKAGE-BROWSER-VALIDATION-BLOCKED.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.35 Extracted package browser validation BLOCKED",
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
