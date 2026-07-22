from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import shutil
import subprocess
import zipfile

root = Path(".").resolve()
version = "v0.8.61"
release_dir = Path(r"D:\dev\release-assets\voila\v0.8.61-package-rebuild-with-review-document-clean-study-flow-no-share-no-delivery")
zip_name = "voila-v0.8.61-controlled-tester-windows-package-candidate.zip"
zip_path = release_dir / zip_name

doc_path = root / "docs" / "dev" / "package-rebuild-with-review-document-clean-study-flow-no-share-no-delivery.md"
web_path = root / "services" / "api" / "web_app.py"

required_scripts = [
    root / "scripts" / "dev" / "check-learner-workflow-ui-smoke-from-review-to-clean-study-no-build-no-zip-no-share-no-delivery.py",
    root / "scripts" / "dev" / "check-ui-polish-readability-pass-no-build-no-zip-no-share-no-delivery.py",
    root / "scripts" / "dev" / "check-package-rebuild-preflight-after-owner-approval-no-build-no-zip-no-share-no-delivery.py",
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

for path in [doc_path, web_path] + required_scripts:
    if not path.exists():
        fail("FAILED_V0861_REQUIRED_FILE_MISSING=" + str(path))

doc = doc_path.read_text(encoding="utf-8", errors="replace")
web = web_path.read_text(encoding="utf-8", errors="replace")

for term in [
    "v0.8.61 Package rebuild",
    "explicitly approved for local package rebuild and ZIP creation only",
    "No OneDrive copy.",
    "No share.",
    "No delivery.",
    "No distribution.",
    "No public release.",
    "voila-v0.8.61-controlled-tester-windows-package-candidate.zip",
]:
    if term not in doc:
        fail("FAILED_V0861_DOC_TERM_MISSING=" + term)

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
        fail("FAILED_V0861_CHAIN_MARKER_MISSING=" + marker)

changed = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/package-rebuild-with-review-document-clean-study-flow-no-share-no-delivery.md",
    "scripts/dev/check-package-rebuild-with-review-document-clean-study-flow-no-share-no-delivery.py",
    "scripts/dev/check-package-rebuild-with-review-document-clean-study-flow-no-share-no-delivery.ps1",
}

for line in changed:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        fail("FAILED_V0861_UNEXPECTED_GIT_STATUS_PATH=" + line)

if is_inside(zip_path, root):
    fail("FAILED_V0861_ZIP_INSIDE_REPO=" + str(zip_path))

onedrive_root = Path(os.environ.get("USERPROFILE", r"C:\Users\liian")) / "OneDrive"
if is_inside(zip_path, onedrive_root):
    fail("FAILED_V0861_ZIP_INSIDE_ONEDRIVE=" + str(zip_path))

release_dir.mkdir(parents=True, exist_ok=True)
if zip_path.exists():
    zip_path.unlink()

tracked_raw = subprocess.check_output(["git", "ls-files", "-z"])
tracked = [item for item in tracked_raw.decode("utf-8", errors="replace").split("\0") if item]

def safe_zip_name(rel: str) -> str:
    normalized = rel.replace("\\", "/").strip("/")
    pure = PurePosixPath(normalized)
    if not normalized or normalized.startswith("/") or ".." in pure.parts:
        fail("FAILED_V0861_UNSAFE_TRACKED_PATH=" + rel)
    return normalized

def should_skip(rel: str) -> bool:
    lowered = rel.replace("\\", "/").lower()
    parts = lowered.split("/")
    if ".git" in parts:
        return True
    if ".venv" in parts or "venv" in parts:
        return True
    if "__pycache__" in parts:
        return True
    if ".pytest_cache" in parts or ".mypy_cache" in parts:
        return True
    if "node_modules" in parts:
        return True
    if lowered.endswith(".pyc") or lowered.endswith(".pyo"):
        return True
    return False

included = []
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for rel in tracked:
        rel_zip = safe_zip_name(rel)
        if should_skip(rel_zip):
            continue
        source = root / rel_zip
        if not source.exists() or not source.is_file():
            continue
        zf.write(source, rel_zip)
        included.append(rel_zip)

if not zip_path.exists():
    fail("FAILED_V0861_ZIP_NOT_CREATED=" + str(zip_path))

zip_size = zip_path.stat().st_size
zip_sha = sha256_file(zip_path)

with zipfile.ZipFile(zip_path, "r") as zf:
    names = zf.namelist()
    names_set = set(names)

    for required in [
        "scripts/dev/start-voila-packaged.ps1",
        "services/api/web_app.py",
        "scripts/dev/check-learner-workflow-ui-smoke-from-review-to-clean-study-no-build-no-zip-no-share-no-delivery.py",
        "scripts/dev/check-ui-polish-readability-pass-no-build-no-zip-no-share-no-delivery.py",
        "scripts/dev/check-package-rebuild-preflight-after-owner-approval-no-build-no-zip-no-share-no-delivery.py",
    ]:
        if required not in names_set:
            fail("FAILED_V0861_REQUIRED_ZIP_ENTRY_MISSING=" + required)

    for forbidden in [
        ".git/",
        ".venv/",
        "__pycache__/",
        ".pytest_cache/",
        ".mypy_cache/",
        "node_modules/",
    ]:
        if any(forbidden in name for name in names):
            fail("FAILED_V0861_FORBIDDEN_ZIP_ENTRY_PRESENT=" + forbidden)

    if any(name.lower().endswith(".pyc") for name in names):
        fail("FAILED_V0861_PYC_ENTRY_PRESENT")

    web_text = zf.read("services/api/web_app.py").decode("utf-8", errors="replace")
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
        if marker not in web_text:
            fail("FAILED_V0861_ZIPPED_WEB_MARKER_MISSING=" + marker)

entry_count = len(included)
if entry_count < 100:
    fail("FAILED_V0861_ZIP_ENTRY_COUNT_TOO_LOW=" + str(entry_count))

source_head = subprocess.check_output(
    ["git", "rev-parse", "--short", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).strip()

evidence_dir = Path(r"D:\dev\tester-runs\v0861-package-rebuild-with-review-document-clean-study-flow-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_61_PACKAGE_REBUILD_CHECK": "PASS",
    "implementation_performed": False,
    "owner_explicitly_approved_build_zip": True,
    "package_rebuild_performed": True,
    "new_zip_created": True,
    "build_performed": False,
    "zip_path": str(zip_path),
    "zip_name": zip_name,
    "zip_sha256": zip_sha,
    "zip_size_bytes": zip_size,
    "zip_entry_count": entry_count,
    "zip_created_outside_repo": True,
    "zip_created_outside_onedrive": True,
    "zip_source": "git_tracked_files_only",
    "packaged_startup_bootstrap_present": True,
    "web_app_packaged": True,
    "review_document_clean_study_markers_packaged": True,
    "v0858_smoke_script_packaged": True,
    "v0859_readability_script_packaged": True,
    "v0860_preflight_script_packaged": True,
    "dot_git_excluded": True,
    "dot_venv_excluded": True,
    "pycache_excluded": True,
    "node_modules_excluded": True,
    "pyc_excluded": True,
    "source_head": source_head,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "PACKAGE_REBUILD": "PASS_OWNER_LOCAL_ZIP_CREATED_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "OWNER_LOCAL_PACKAGE_REBUILT_PENDING_EXTRACTED_PACKAGE_VALIDATION",
    "SHARE_OR_DELIVERY_APPROVED": False,
    "POLICY": "package_rebuild_with_review_document_clean_study_flow_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.62-owner-local-extracted-package-validation-review-document-clean-study-flow-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.61-PACKAGE-REBUILD-CHECK.json"
out_md = evidence_dir / "V0.8.61-PACKAGE-REBUILD-CHECK.md"
sha_file = release_dir / (zip_name + ".sha256")

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.61 Package rebuild\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)
sha_file.write_text(zip_sha + "  " + zip_name + "\n", encoding="utf-8")

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
print("SHA256_FILE=" + str(sha_file))

