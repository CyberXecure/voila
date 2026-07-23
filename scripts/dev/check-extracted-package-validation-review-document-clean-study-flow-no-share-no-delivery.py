from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error
import zipfile

repo_root = Path(".").resolve()
zip_path = Path(r"D:\dev\release-assets\voila\v0.8.61-package-rebuild-with-review-document-clean-study-flow-no-share-no-delivery\voila-v0.8.61-controlled-tester-windows-package-candidate.zip")
expected_sha = "1f46f26ca4e5cbc357450d568428d1a9c595a4356c2523c2eb67442774979ff7"

run_root = Path(r"D:\dev\tester-runs\v0862pkg")
extract_root = run_root / "x"
package_root = extract_root / "pkg"

course_id = "03-pag-30-34-vectori-trigonometrie"
pdf_name = course_id + ".pdf"

doc_path = repo_root / "docs" / "dev" / "extracted-package-validation-review-document-clean-study-flow-no-share-no-delivery.md"

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

def sha_or_missing(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    return sha256_file(path)

def fetch(url: str, attempts: int = 30):
    last = ""
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                return response.status, response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8", errors="replace")
        except Exception as exc:
            last = str(exc)
            time.sleep(2)
    fail("FAILED_V0862_FETCH_TIMEOUT=" + url + " :: " + last)

if not doc_path.exists():
    fail("FAILED_V0862_DOC_MISSING=" + str(doc_path))

doc = doc_path.read_text(encoding="utf-8", errors="replace")
for term in [
    "v0.8.62 Extracted package validation",
    "It does not rebuild the package.",
    "It does not create a new ZIP.",
    "It does not copy anything to OneDrive.",
    "It does not share anything.",
    "It does not deliver anything.",
    expected_sha,
    "scripts/dev/start-voila-packaged.ps1",
    "Course Tools",
    "Revizuire document",
    "Study curat",
    "No rebuild.",
    "No new ZIP.",
    "No OneDrive copy.",
    "No share.",
    "No delivery.",
]:
    if term not in doc:
        fail("FAILED_V0862_DOC_TERM_MISSING=" + term)

changed = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo_root),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/extracted-package-validation-review-document-clean-study-flow-no-share-no-delivery.md",
    "scripts/dev/check-extracted-package-validation-review-document-clean-study-flow-no-share-no-delivery.py",
    "scripts/dev/check-extracted-package-validation-review-document-clean-study-flow-no-share-no-delivery.ps1",
}

for line in changed:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        fail("FAILED_V0862_UNEXPECTED_GIT_STATUS_PATH=" + line)

if not zip_path.exists():
    fail("FAILED_V0862_SOURCE_ZIP_MISSING=" + str(zip_path))

zip_sha = sha256_file(zip_path)
if zip_sha.lower() != expected_sha.lower():
    fail("FAILED_V0862_SOURCE_ZIP_SHA_MISMATCH=" + zip_sha)

if is_inside(zip_path, repo_root):
    fail("FAILED_V0862_SOURCE_ZIP_INSIDE_REPO=" + str(zip_path))

onedrive_root = Path(os.environ.get("USERPROFILE", r"C:\Users\liian")) / "OneDrive"
if is_inside(zip_path, onedrive_root):
    fail("FAILED_V0862_SOURCE_ZIP_INSIDE_ONEDRIVE=" + str(zip_path))

# stop any previous packaged/repo app before deleting extracted files,
# because Windows can keep .pyd files locked inside the packaged .venv.
subprocess.run(
    ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(repo_root / "scripts" / "dev" / "stop-voila.ps1")],
    cwd=str(repo_root),
    check=False,
)
time.sleep(3)

run_root.mkdir(parents=True, exist_ok=True)
if extract_root.exists():
    shutil.rmtree(extract_root)
extract_root.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(zip_path, "r") as zf:
    names = zf.namelist()
    if not names:
        fail("FAILED_V0862_ZIP_EMPTY")

    for forbidden in [
        ".git/",
        ".venv/",
        "__pycache__/",
        ".pytest_cache/",
        ".mypy_cache/",
        "node_modules/",
    ]:
        if any(forbidden in name for name in names):
            fail("FAILED_V0862_FORBIDDEN_ZIP_ENTRY_PRESENT=" + forbidden)

    if any(name.lower().endswith(".pyc") for name in names):
        fail("FAILED_V0862_PYC_ENTRY_PRESENT")

    zf.extractall(package_root)

if is_inside(package_root, repo_root):
    fail("FAILED_V0862_EXTRACTED_PACKAGE_INSIDE_REPO=" + str(package_root))

if is_inside(package_root, onedrive_root):
    fail("FAILED_V0862_EXTRACTED_PACKAGE_INSIDE_ONEDRIVE=" + str(package_root))

required_extracted = [
    package_root / "scripts" / "dev" / "start-voila-packaged.ps1",
    package_root / "services" / "api" / "web_app.py",
    package_root / "scripts" / "dev" / "check-learner-workflow-ui-smoke-from-review-to-clean-study-no-build-no-zip-no-share-no-delivery.py",
    package_root / "scripts" / "dev" / "check-ui-polish-readability-pass-no-build-no-zip-no-share-no-delivery.py",
    package_root / "scripts" / "dev" / "check-package-rebuild-preflight-after-owner-approval-no-build-no-zip-no-share-no-delivery.py",
]

for path in required_extracted:
    if not path.exists():
        fail("FAILED_V0862_REQUIRED_EXTRACTED_FILE_MISSING=" + str(path))

web = (package_root / "services" / "api" / "web_app.py").read_text(encoding="utf-8", errors="replace")
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
        fail("FAILED_V0862_EXTRACTED_WEB_MARKER_MISSING=" + marker)

for forbidden_dir in [
    package_root / ".git",
    package_root / ".venv",
    package_root / "node_modules",
]:
    if forbidden_dir.exists():
        fail("FAILED_V0862_FORBIDDEN_EXTRACTED_DIR_PRESENT=" + str(forbidden_dir))

if list(package_root.rglob("*.pyc")):
    fail("FAILED_V0862_EXTRACTED_PYC_PRESENT")

repo_input_pdf = repo_root / "data" / "input" / pdf_name
repo_output_dir = repo_root / "data" / "output" / course_id
package_input_dir = package_root / "data" / "input"
package_output_dir = package_root / "data" / "output" / course_id

if not repo_input_pdf.exists():
    fail("FAILED_V0862_REPO_FIXTURE_PDF_MISSING=" + str(repo_input_pdf))

if not repo_output_dir.exists():
    fail("FAILED_V0862_REPO_FIXTURE_OUTPUT_MISSING=" + str(repo_output_dir))

package_input_dir.mkdir(parents=True, exist_ok=True)
package_output_dir.parent.mkdir(parents=True, exist_ok=True)

shutil.copy2(repo_input_pdf, package_input_dir / pdf_name)

if package_output_dir.exists():
    shutil.rmtree(package_output_dir)
shutil.copytree(repo_output_dir, package_output_dir)

watch_paths = [
    package_root / "data" / "output" / course_id / "explanation_drafts.preview.json",
    package_root / "data" / "output" / course_id / "manual_learning_evidence.json",
    package_root / "data" / "output" / course_id / "manual_study_items.preview.json",
    package_root / "data" / "output" / course_id / "study_items.preview.json",
]
before = {str(path): sha_or_missing(path) for path in watch_paths}

# stop repo/local existing services first
subprocess.run(
    ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(repo_root / "scripts" / "dev" / "stop-voila.ps1")],
    cwd=str(repo_root),
    check=False,
)

startup = package_root / "scripts" / "dev" / "start-voila-packaged.ps1"
startup_text = startup.read_text(encoding="utf-8", errors="replace")

cmd = ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(startup)]
if "-Silent" in startup_text:
    cmd.append("-Silent")

start_result = subprocess.run(
    cmd,
    cwd=str(package_root),
    text=True,
    encoding="utf-8",
    errors="replace",
    capture_output=True,
    timeout=180,
)

if start_result.returncode != 0:
    fail("FAILED_V0862_PACKAGED_START_FAILED=" + start_result.stdout[-2000:] + start_result.stderr[-2000:])

health_status, health_html = fetch("http://127.0.0.1:8787/health")
if health_status != 200:
    fail("FAILED_V0862_HEALTH_STATUS=" + str(health_status))

course_tools_url = "http://127.0.0.1:8787/course-tools?pdf=" + urllib.parse.quote(pdf_name)
review_url = "http://127.0.0.1:8787/review-document?pdf=" + urllib.parse.quote(pdf_name)
draft_form_url = review_url + "&draft=1"
clean_preview_url = "http://127.0.0.1:8787/study-clean-preview?pdf=" + urllib.parse.quote(pdf_name)
default_study_url = "http://127.0.0.1:8787/study?pdf=" + urllib.parse.quote(pdf_name)

course_status, course_html = fetch(course_tools_url)
review_status, review_html = fetch(review_url)
draft_status, draft_html = fetch(draft_form_url)
clean_status, clean_html = fetch(clean_preview_url)
study_status, study_html = fetch(default_study_url)

for label, status in [
    ("COURSE_TOOLS", course_status),
    ("REVIEW_DOCUMENT", review_status),
    ("DRAFT_FORM_GET", draft_status),
    ("CLEAN_PREVIEW", clean_status),
    ("DEFAULT_STUDY", study_status),
]:
    if status != 200:
        fail("FAILED_V0862_" + label + "_STATUS=" + str(status))

for term in [
    "course-tools-review-document-entry",
    "Deschide Revizuire document",
]:
    if term not in course_html:
        fail("FAILED_V0862_COURSE_TOOLS_TERM_MISSING=" + term)

for term in [
    "review-document-shell-read-only",
    "review-document-text-detected-queue",
    "review-document-corrections-suggested-queue",
    "review-document-formulas-images-queue",
    "review-document-friendly-explanation-shell",
    "friendly-explanation-save-entry",
    "clean-study-preview-entry",
    "clean-study-preview-link",
]:
    if term not in review_html:
        fail("FAILED_V0862_REVIEW_TERM_MISSING=" + term)

for term in [
    "friendly-explanation-save-form-shell",
    "friendly-explanation-save-form",
    'method="post"',
    'action="/review-drafts/save-explanation-draft"',
    "Salvează draft local",
]:
    if term not in draft_html:
        fail("FAILED_V0862_DRAFT_FORM_TERM_MISSING=" + term)

for term in [
    "study-clean-preview-route",
    "study-clean-preview-read-only-status",
    "Read-only",
    "nu creează carduri reale",
    "nu scrie Progress",
    "study-clean-preview-cards",
]:
    if term not in clean_html:
        fail("FAILED_V0862_CLEAN_PREVIEW_TERM_MISSING=" + term)

if not ("Study curat" in clean_html and "previzualizare" in clean_html):
    fail("FAILED_V0862_CLEAN_PREVIEW_TITLE_MISSING")

if not ("study-clean-preview-card" in clean_html or "study-clean-preview-empty-state" in clean_html):
    fail("FAILED_V0862_CLEAN_PREVIEW_CARD_OR_EMPTY_STATE_MISSING")

if "friendly-explanation-draft-save-result" in review_html or "friendly-explanation-draft-save-result" in draft_html or "friendly-explanation-draft-save-result" in clean_html:
    fail("FAILED_V0862_POST_RESULT_RENDERED_WITHOUT_POST")

after = {str(path): sha_or_missing(path) for path in watch_paths}
changed_artifacts = [path for path in watch_paths if after[str(path)] != before[str(path)]]
if changed_artifacts:
    fail("FAILED_V0862_EXTRACTED_VALIDATION_CHANGED_ARTIFACTS=" + ",".join(str(path) for path in changed_artifacts))

evidence_dir = run_root / "evidence"
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_62_EXTRACTED_PACKAGE_VALIDATION_CHECK": "PASS",
    "implementation_performed": False,
    "extracted_package_validation_performed": True,
    "source_zip_path": str(zip_path),
    "source_zip_sha256": zip_sha,
    "source_zip_sha256_matches_v0861_final": True,
    "package_extracted": True,
    "local_validation_fixture_seeded": True,
    "fixture_pdf_seeded": True,
    "fixture_output_seeded": True,
    "extract_root": str(package_root),
    "extracted_outside_repo": True,
    "extracted_outside_onedrive": True,
    "packaged_startup_bootstrap_present": True,
    "packaged_startup_invoked": True,
    "packaged_app_started": True,
    "health_status": health_status,
    "course_tools_status": course_status,
    "review_document_status": review_status,
    "draft_form_get_status": draft_status,
    "clean_preview_status": clean_status,
    "default_study_status": study_status,
    "course_tools_to_review_link_visible": True,
    "review_document_flow_visible": True,
    "draft_form_get_visible": True,
    "clean_study_preview_visible": True,
    "clean_study_card_or_empty_state_visible": True,
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
    "PACKAGE_READINESS": "OWNER_LOCAL_EXTRACTED_PACKAGE_VALIDATED_PENDING_FINAL_NO_DELIVERY_REVIEW",
    "SHARE_OR_DELIVERY_APPROVED": False,
    "POLICY": "extracted_package_validation_review_document_clean_study_flow_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.63-owner-local-final-no-delivery-review-for-v0861-package-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.62-EXTRACTED-PACKAGE-VALIDATION-CHECK.json"
out_md = evidence_dir / "V0.8.62-EXTRACTED-PACKAGE-VALIDATION-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.62 Extracted package validation\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
