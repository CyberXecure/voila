from pathlib import Path
import hashlib
import json
import os
import subprocess

repo_root = Path(".").resolve()

zip_path = Path(r"D:\dev\release-assets\voila\v0.8.61-package-rebuild-with-review-document-clean-study-flow-no-share-no-delivery\voila-v0.8.61-controlled-tester-windows-package-candidate.zip")
sha_path = Path(str(zip_path) + ".sha256")
expected_sha = "1f46f26ca4e5cbc357450d568428d1a9c595a4356c2523c2eb67442774979ff7"

v0861_evidence = Path(r"D:\dev\tester-runs\v0861-package-rebuild-with-review-document-clean-study-flow-no-share-no-delivery\V0.8.61-PACKAGE-REBUILD-CHECK.json")
v0862_evidence = Path(r"D:\dev\tester-runs\v0862pkg\evidence\V0.8.62-EXTRACTED-PACKAGE-VALIDATION-CHECK.json")

doc_path = repo_root / "docs" / "dev" / "final-no-delivery-review-for-v0861-package-no-share-no-delivery.md"
web_path = repo_root / "services" / "api" / "web_app.py"

required_repo_files = [
    repo_root / "docs" / "dev" / "package-rebuild-preflight-after-owner-approval-no-build-no-zip-no-share-no-delivery.md",
    repo_root / "scripts" / "dev" / "check-package-rebuild-preflight-after-owner-approval-no-build-no-zip-no-share-no-delivery.py",
    repo_root / "docs" / "dev" / "package-rebuild-with-review-document-clean-study-flow-no-share-no-delivery.md",
    repo_root / "scripts" / "dev" / "check-package-rebuild-with-review-document-clean-study-flow-no-share-no-delivery.py",
    repo_root / "docs" / "dev" / "extracted-package-validation-review-document-clean-study-flow-no-share-no-delivery.md",
    repo_root / "scripts" / "dev" / "check-extracted-package-validation-review-document-clean-study-flow-no-share-no-delivery.py",
]

def fail(message: str):
    raise SystemExit(message)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def is_inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except Exception:
        return False

def read_json(path: Path):
    if not path.exists():
        fail("FAILED_V0863_EVIDENCE_MISSING=" + str(path))
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))

if not doc_path.exists():
    fail("FAILED_V0863_DOC_MISSING=" + str(doc_path))

for path in required_repo_files:
    if not path.exists():
        fail("FAILED_V0863_REQUIRED_REPO_FILE_MISSING=" + str(path))

doc = doc_path.read_text(encoding="utf-8", errors="replace")

for term in [
    "v0.8.63 Final no-delivery review",
    "It does not rebuild the package.",
    "It does not create a new ZIP.",
    "It does not extract a new package copy.",
    "It does not start a new browser validation run.",
    "It does not copy anything to OneDrive.",
    "It does not share anything.",
    "It does not deliver anything.",
    "1f46f26ca4e5cbc357450d568428d1a9c595a4356c2523c2eb67442774979ff7",
    "v0.8.60 confirmed rebuild preflight readiness only.",
    "v0.8.61 created the owner-local ZIP package.",
    "v0.8.62 validated the extracted package locally.",
    "v0.8.62a fixed Windows cleanup lock behavior",
    "Course Tools",
    "Revizuire document",
    "Draft explicație form via GET only",
    "Study curat",
    "no POST called",
    "no draft created",
    "no Study cards created",
    "no Progress write",
    "pending a separate explicit owner approval",
    "No rebuild.",
    "No new ZIP.",
    "No new extraction.",
    "No browser validation rerun.",
    "No OneDrive copy.",
    "No share.",
    "No delivery.",
    "No distribution.",
    "No public release.",
]:
    if term not in doc:
        fail("FAILED_V0863_DOC_TERM_MISSING=" + term)

changed = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo_root),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/final-no-delivery-review-for-v0861-package-no-share-no-delivery.md",
    "scripts/dev/check-final-no-delivery-review-for-v0861-package-no-share-no-delivery.py",
    "scripts/dev/check-final-no-delivery-review-for-v0861-package-no-share-no-delivery.ps1",
}

for line in changed:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        fail("FAILED_V0863_UNEXPECTED_GIT_STATUS_PATH=" + line)

if not zip_path.exists():
    fail("FAILED_V0863_SOURCE_ZIP_MISSING=" + str(zip_path))

if not sha_path.exists():
    fail("FAILED_V0863_SHA_FILE_MISSING=" + str(sha_path))

zip_sha_before = sha256_file(zip_path)
zip_size_before = zip_path.stat().st_size
zip_mtime_before = zip_path.stat().st_mtime

if zip_sha_before.lower() != expected_sha.lower():
    fail("FAILED_V0863_SOURCE_ZIP_SHA_MISMATCH=" + zip_sha_before)

sha_text = sha_path.read_text(encoding="utf-8", errors="replace")
if expected_sha not in sha_text:
    fail("FAILED_V0863_SHA_FILE_CONTENT_MISMATCH=" + str(sha_path))

if is_inside(zip_path, repo_root):
    fail("FAILED_V0863_ZIP_INSIDE_REPO=" + str(zip_path))

onedrive_root = Path(os.environ.get("USERPROFILE", r"C:\Users\liian")) / "OneDrive"
if is_inside(zip_path, onedrive_root):
    fail("FAILED_V0863_ZIP_INSIDE_ONEDRIVE=" + str(zip_path))

v0861 = read_json(v0861_evidence)
v0862 = read_json(v0862_evidence)

expected_v0861 = {
    "VOILA_V0_8_61_PACKAGE_REBUILD_CHECK": "PASS",
    "owner_explicitly_approved_build_zip": True,
    "package_rebuild_performed": True,
    "new_zip_created": True,
    "zip_created_outside_repo": True,
    "zip_created_outside_onedrive": True,
    "zip_source": "git_tracked_files_only",
    "packaged_startup_bootstrap_present": True,
    "web_app_packaged": True,
    "review_document_clean_study_markers_packaged": True,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "PACKAGE_REBUILD": "PASS_OWNER_LOCAL_ZIP_CREATED_NO_SHARE_NO_DELIVERY",
}

for key, expected in expected_v0861.items():
    if v0861.get(key) != expected:
        fail("FAILED_V0863_V0861_EVIDENCE_MISMATCH=" + key + "=" + repr(v0861.get(key)))

if str(v0861.get("zip_sha256", "")).lower() != expected_sha.lower():
    fail("FAILED_V0863_V0861_EVIDENCE_SHA_MISMATCH=" + str(v0861.get("zip_sha256")))

expected_v0862 = {
    "VOILA_V0_8_62_EXTRACTED_PACKAGE_VALIDATION_CHECK": "PASS",
    "extracted_package_validation_performed": True,
    "source_zip_sha256_matches_v0861_final": True,
    "package_extracted": True,
    "local_validation_fixture_seeded": True,
    "fixture_pdf_seeded": True,
    "fixture_output_seeded": True,
    "extracted_outside_repo": True,
    "extracted_outside_onedrive": True,
    "packaged_startup_bootstrap_present": True,
    "packaged_startup_invoked": True,
    "packaged_app_started": True,
    "health_status": 200,
    "course_tools_status": 200,
    "review_document_status": 200,
    "draft_form_get_status": 200,
    "clean_preview_status": 200,
    "default_study_status": 200,
    "no_post_called": True,
    "no_draft_created": True,
    "read_only_validation": True,
    "explanation_drafts_unchanged": True,
    "manual_learning_evidence_unchanged": True,
    "manual_study_items_preview_unchanged": True,
    "study_items_preview_unchanged": True,
    "web_app_changed": False,
    "new_zip_created": False,
    "package_rebuild_performed": False,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "EXTRACTED_PACKAGE_VALIDATION": "PASS_OWNER_LOCAL_EXTRACTED_PACKAGE_VALIDATED_NO_SHARE_NO_DELIVERY",
}

for key, expected in expected_v0862.items():
    if v0862.get(key) != expected:
        fail("FAILED_V0863_V0862_EVIDENCE_MISMATCH=" + key + "=" + repr(v0862.get(key)))

if str(v0862.get("source_zip_sha256", "")).lower() != expected_sha.lower():
    fail("FAILED_V0863_V0862_EVIDENCE_SHA_MISMATCH=" + str(v0862.get("source_zip_sha256")))

web = web_path.read_text(encoding="utf-8", errors="replace")
for marker in [
    "VOILA_V0_8_50_REVIEW_DOCUMENT_SHELL_READ_ONLY_FIRST_SLICE_START",
    "VOILA_V0_8_51_COURSE_TOOLS_LINK_TO_REVIEW_DOCUMENT_SHELL_START",
    "VOILA_V0_8_52_TEXT_DETECTED_READ_ONLY_QUEUE_START",
    "VOILA_V0_8_53_CORRECTIONS_SUGGESTED_READ_ONLY_QUEUE_START",
    "VOILA_V0_8_54_FORMULAS_IMAGES_READ_ONLY_QUEUE_START",
    "VOILA_V0_8_55_FRIENDLY_EXPLANATION_FORM_READ_ONLY_STATIC_DRAFT_SHELL_START",
    "VOILA_V0_8_56_SAFE_LOCAL_SAVE_FOR_EXPLANATION_DRAFTS_START",
    "VOILA_V0_8_57_CLEAN_STUDY_READ_ONLY_PREVIEW_FROM_EXPLANATION_DRAFTS_START",
]:
    if marker not in web:
        fail("FAILED_V0863_WEB_MARKER_MISSING=" + marker)

zip_sha_after = sha256_file(zip_path)
zip_size_after = zip_path.stat().st_size
zip_mtime_after = zip_path.stat().st_mtime

if zip_sha_after != zip_sha_before:
    fail("FAILED_V0863_ZIP_CHANGED_DURING_REVIEW_SHA")
if zip_size_after != zip_size_before:
    fail("FAILED_V0863_ZIP_CHANGED_DURING_REVIEW_SIZE")
if zip_mtime_after != zip_mtime_before:
    fail("FAILED_V0863_ZIP_CHANGED_DURING_REVIEW_MTIME")

source_head = subprocess.check_output(
    ["git", "rev-parse", "--short", "HEAD"],
    cwd=str(repo_root),
    text=True,
    encoding="utf-8",
    errors="replace",
).strip()

evidence_dir = Path(r"D:\dev\tester-runs\v0863-final-no-delivery-review-for-v0861-package-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_63_FINAL_NO_DELIVERY_REVIEW_CHECK": "PASS",
    "implementation_performed": False,
    "final_no_delivery_review_performed": True,
    "reviewed_source_zip_path": str(zip_path),
    "reviewed_source_zip_sha256": zip_sha_after,
    "reviewed_zip_size_bytes": zip_size_after,
    "reviewed_zip_unchanged_during_check": True,
    "reviewed_zip_outside_repo": True,
    "reviewed_zip_outside_onedrive": True,
    "v0860_preflight_reviewed": True,
    "v0861_package_rebuild_evidence_reviewed": True,
    "v0861_package_rebuild_pass": True,
    "v0862_extracted_validation_evidence_reviewed": True,
    "v0862_extracted_validation_pass": True,
    "v0862a_cleanup_lock_fix_reviewed": True,
    "review_document_clean_study_markers_present_on_main": True,
    "course_tools_validated_in_extracted_package": True,
    "review_document_validated_in_extracted_package": True,
    "draft_form_get_validated_in_extracted_package": True,
    "clean_study_preview_validated_in_extracted_package": True,
    "default_study_validated_in_extracted_package": True,
    "no_post_called": True,
    "no_draft_created": True,
    "no_study_cards_created": True,
    "no_progress_write": True,
    "new_extraction_performed": False,
    "browser_validation_rerun": False,
    "package_rebuild_performed": False,
    "new_zip_created": False,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "source_head": source_head,
    "FINAL_NO_DELIVERY_REVIEW": "PASS_OWNER_LOCAL_PACKAGE_REVIEWED_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "OWNER_LOCAL_PACKAGE_READY_FOR_SEPARATE_OWNER_APPROVED_SHARE_PREPARATION_ONLY",
    "SHARE_OR_DELIVERY_APPROVED": False,
    "POLICY": "final_no_delivery_review_for_v0861_package_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.64-owner-local-controlled-tester-share-preparation-no-public-release-no-delivery-only-if-owner-explicitly-approves",
}

out_json = evidence_dir / "V0.8.63-FINAL-NO-DELIVERY-REVIEW-CHECK.json"
out_md = evidence_dir / "V0.8.63-FINAL-NO-DELIVERY-REVIEW-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.63 Final no-delivery review\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
