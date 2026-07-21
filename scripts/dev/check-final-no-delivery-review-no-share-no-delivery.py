from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

root = Path(".").resolve()

doc = root / "docs" / "dev" / "final-no-delivery-review-no-share-no-delivery.md"
check_py = root / "scripts" / "dev" / "check-final-no-delivery-review-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-final-no-delivery-review-no-share-no-delivery.ps1"
web = root / "services" / "api" / "web_app.py"

for path, marker in [
    (doc, "FAILED_V0840_DOC_MISSING"),
    (check_py, "FAILED_V0840_CHECK_PY_MISSING"),
    (check_ps1, "FAILED_V0840_CHECK_PS1_MISSING"),
    (web, "FAILED_V0840_WEB_APP_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker + "=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
web_text = web.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "Final no-delivery review",
    "v0.8.39 extracted-package browser validation retry PASS",
    "The local package candidate is owner-local validated.",
    "The package has not been copied to OneDrive.",
    "No share link has been created.",
    "No delivery has been performed.",
    "No distribution has been performed.",
    "No public release has been created.",
    "The package may only move forward after a separate explicit owner approval milestone.",
    "local ZIP candidate created",
    "packaged startup bootstrap included",
    "package extracted under `D:\\dev\\tester-runs`",
    "packaged startup started the extracted app",
    "`/health` returned 200",
    "normal Study rendered Manual Study default",
    "legacy fallback worked when `manual_study_items.preview.json` was temporarily unavailable",
    "This milestone is review/evidence only.",
    "It does not rebuild the package.",
    "It does not create a new ZIP.",
    "It does not extract the package.",
    "It does not start the extracted package.",
    "It does not modify `services/api/web_app.py`.",
    "It does not add a route.",
    "It does not add a POST endpoint.",
    "It does not change Study behavior.",
    "It does not write Progress.",
    "It does not mark answers.",
    "It does not copy to OneDrive.",
    "It does not create a share.",
    "It does not deliver anything.",
    "It does not distribute anything.",
    "It does not create a public release.",
    "The package is ready for a separate owner decision.",
    "The package is not delivered.",
    "The package is not shared.",
    "The package is not distributed.",
    "requires a separate explicit owner-approved milestone",
    "No OneDrive copy.",
    "No share.",
    "No delivery.",
    "No distribution.",
    "No public release.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit("FAILED_V0840_DOC_TERM_MISSING=" + term)

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/final-no-delivery-review-no-share-no-delivery.md",
    "scripts/dev/check-final-no-delivery-review-no-share-no-delivery.py",
    "scripts/dev/check-final-no-delivery-review-no-share-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0840_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

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
        raise SystemExit("FAILED_V0840_WEB_TERM_MISSING=" + term)

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0840_STUDY_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/study"') != 0:
    raise SystemExit("FAILED_V0840_STUDY_POST_ADDED")

release_dir = Path(r"D:\dev\release-assets\voila\v0.8.38-package-rebuild-with-packaged-startup-no-share-no-delivery")
candidate_dir_name = "voila-v0.8.38-controlled-tester-windows-package-candidate"
zip_path = release_dir / (candidate_dir_name + ".zip")
sha_path = release_dir / (candidate_dir_name + ".zip.sha256")
manifest_path = release_dir / "V0.8.38-PACKAGE-REBUILD-WITH-PACKAGED-STARTUP-MANIFEST.json"

evidence_v0838_json = Path(r"D:\dev\tester-runs\v0838-package-rebuild-with-packaged-startup-no-share-no-delivery\V0.8.38-PACKAGE-REBUILD-WITH-PACKAGED-STARTUP-CHECK.json")
evidence_v0839_json = Path(r"D:\dev\tester-runs\v0839-extracted-package-browser-validation-retry-no-share-no-delivery\V0.8.39-EXTRACTED-PACKAGE-BROWSER-VALIDATION-RETRY-CHECK.json")

for path, marker in [
    (zip_path, "FAILED_V0840_PACKAGE_ZIP_MISSING"),
    (sha_path, "FAILED_V0840_PACKAGE_SHA_MISSING"),
    (manifest_path, "FAILED_V0840_PACKAGE_MANIFEST_MISSING"),
    (evidence_v0838_json, "FAILED_V0840_V0838_EVIDENCE_MISSING"),
    (evidence_v0839_json, "FAILED_V0840_V0839_EVIDENCE_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker + "=" + str(path))

zip_resolved = str(zip_path.resolve()).lower()
root_resolved = str(root.resolve()).lower()

if zip_resolved.startswith(root_resolved):
    raise SystemExit("FAILED_V0840_PACKAGE_ZIP_INSIDE_REPO=" + str(zip_path))

if "onedrive" in zip_resolved:
    raise SystemExit("FAILED_V0840_PACKAGE_ZIP_IN_ONEDRIVE=" + str(zip_path))

actual_sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
sha_text = sha_path.read_text(encoding="utf-8", errors="replace").strip()
expected_sha = sha_text.split()[0] if sha_text else ""

if actual_sha.lower() != expected_sha.lower():
    raise SystemExit("FAILED_V0840_PACKAGE_SHA_MISMATCH=" + actual_sha + ";EXPECTED=" + expected_sha)

manifest = json.loads(manifest_path.read_text(encoding="utf-8", errors="replace"))
v0838 = json.loads(evidence_v0838_json.read_text(encoding="utf-8", errors="replace"))
v0839 = json.loads(evidence_v0839_json.read_text(encoding="utf-8", errors="replace"))

expected_v0838 = {
    "VOILA_V0_8_38_PACKAGE_REBUILD_WITH_PACKAGED_STARTUP_CHECK": "PASS",
    "package_rebuild_performed": True,
    "new_zip_created": True,
    "package_contains_packaged_startup_bootstrap": True,
    "packaged_bootstrap_check_only_passed_in_staging": True,
    "package_excludes_dot_venv": True,
    "package_venv_python_present": False,
    "package_not_in_repo": True,
    "package_not_in_onedrive": True,
    "extracted_package_validation_completed": False,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "PACKAGE_REBUILD": "PASS_LOCAL_ZIP_CREATED_WITH_PACKAGED_STARTUP_NO_SHARE_NO_DELIVERY",
}

for key, expected in expected_v0838.items():
    if v0838.get(key) != expected:
        raise SystemExit(f"FAILED_V0840_V0838_EVIDENCE_VALUE={key}; ACTUAL={v0838.get(key)!r}; EXPECTED={expected!r}")

expected_v0839 = {
    "VOILA_V0_8_39_EXTRACTED_PACKAGE_BROWSER_VALIDATION_RETRY_CHECK": "PASS",
    "package_sha256_matches_file": True,
    "zip_contains_packaged_startup_bootstrap": True,
    "package_excludes_dot_venv": True,
    "package_venv_python_present": False,
    "extracted_package_validation_completed": True,
    "extracted_package_not_in_repo": True,
    "extracted_package_not_in_onedrive": True,
    "packaged_bootstrap_check_only_passed": True,
    "packaged_bootstrap_started_extracted_app": True,
    "health_status": 200,
    "starts_from_extracted_home_ui": True,
    "home_status": 200,
    "course_tools_from_home_status": 200,
    "normal_study_link_status": 200,
    "normal_study_link_renders_manual_default": True,
    "manual_study_default_cards_visible": True,
    "answer_details_remain_read_only": True,
    "source_metadata_visible": True,
    "shadow_route_status": 200,
    "dry_run_route_status": 200,
    "fallback_legacy_study_available_when_preview_missing": True,
    "legacy_fallback_status_when_manual_preview_missing": 200,
    "legacy_study_items_preview_unchanged": True,
    "package_rebuild_performed": False,
    "new_zip_created": False,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "EXTRACTED_PACKAGE_BROWSER_VALIDATION_RETRY": "PASS_OWNER_LOCAL_NO_SHARE_NO_DELIVERY",
}

for key, expected in expected_v0839.items():
    if v0839.get(key) != expected:
        raise SystemExit(f"FAILED_V0840_V0839_EVIDENCE_VALUE={key}; ACTUAL={v0839.get(key)!r}; EXPECTED={expected!r}")

if v0839.get("package_sha256") != actual_sha:
    raise SystemExit("FAILED_V0840_V0839_SHA_DOES_NOT_MATCH_CURRENT_ZIP")

if manifest.get("package_sha256") != actual_sha:
    raise SystemExit("FAILED_V0840_MANIFEST_SHA_DOES_NOT_MATCH_CURRENT_ZIP")

with zipfile.ZipFile(zip_path, "r") as zf:
    names = set(zf.namelist())
    required_entries = [
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

    for entry in required_entries:
        if entry not in names:
            raise SystemExit("FAILED_V0840_REQUIRED_ZIP_ENTRY_MISSING=" + entry)

    forbidden_hits = [
        name for name in names
        if "/.venv/" in name.lower()
        or "/venv/" in name.lower()
        or name.lower().endswith(".env")
    ]
    if forbidden_hits:
        raise SystemExit("FAILED_V0840_FORBIDDEN_RUNTIME_OR_ENV_IN_ZIP=" + ",".join(sorted(forbidden_hits)[:20]))

source_git_head = subprocess.check_output(
    ["git", "rev-parse", "HEAD"],
    cwd=str(root),
    text=True,
    encoding="utf-8",
    errors="replace",
).strip()

evidence_dir = Path(r"D:\dev\tester-runs\v0840-final-no-delivery-review-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_40_FINAL_NO_DELIVERY_REVIEW_CHECK": "PASS",
    "depends_on_v0838_package_rebuild_with_packaged_startup": True,
    "depends_on_v0839_extracted_package_browser_validation_retry": True,
    "source_git_head": source_git_head,
    "reviewed_package_candidate_path": str(zip_path),
    "reviewed_package_sha256": actual_sha,
    "reviewed_package_sha256_matches_file": True,
    "reviewed_package_manifest_path": str(manifest_path),
    "reviewed_package_zip_entry_count": len(names),
    "reviewed_package_contains_packaged_startup_bootstrap": True,
    "reviewed_package_excludes_dot_venv": True,
    "reviewed_package_not_in_repo": True,
    "reviewed_package_not_in_onedrive": True,
    "v0838_package_rebuild_evidence_pass": True,
    "v0839_extracted_package_browser_validation_evidence_pass": True,
    "extracted_package_validation_completed": True,
    "extracted_package_browser_flow_passed": True,
    "home_course_tools_study_flow_passed": True,
    "normal_study_renders_manual_default": True,
    "manual_study_cards_visible": True,
    "answer_details_remain_read_only": True,
    "source_metadata_visible": True,
    "shadow_route_separate": True,
    "dry_run_route_separate": True,
    "legacy_fallback_available": True,
    "legacy_study_items_preview_unchanged": True,
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
    "FINAL_NO_DELIVERY_REVIEW": "PASS_OWNER_LOCAL_VALIDATED_NO_SHARE_NO_DELIVERY",
    "PACKAGE_DECISION_STATE": "READY_FOR_SEPARATE_OWNER_APPROVAL_MILESTONE_ONLY",
    "PACKAGE_READINESS": "OWNER_LOCAL_VALIDATED_PENDING_EXPLICIT_OWNER_SHARE_OR_DELIVERY_APPROVAL",
    "POLICY": "final_no_delivery_review_no_rebuild_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "separate_explicit_owner_decision_required_before_any_onedrive_share_or_delivery",
}

out_json = evidence_dir / "V0.8.40-FINAL-NO-DELIVERY-REVIEW-CHECK.json"
out_md = evidence_dir / "V0.8.40-FINAL-NO-DELIVERY-REVIEW-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.40 Final no-delivery review — no share/no delivery",
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
