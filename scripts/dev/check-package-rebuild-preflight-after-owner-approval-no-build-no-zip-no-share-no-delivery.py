from pathlib import Path
import hashlib
import json
import subprocess
import urllib.parse
import urllib.request
import urllib.error

root = Path(".").resolve()
course_id = "03-pag-30-34-vectori-trigonometrie"
pdf_name = course_id + ".pdf"
out_dir = root / "data" / "output" / course_id

doc_path = root / "docs" / "dev" / "package-rebuild-preflight-after-owner-approval-no-build-no-zip-no-share-no-delivery.md"
web_path = root / "services" / "api" / "web_app.py"

smoke58 = root / "scripts" / "dev" / "check-learner-workflow-ui-smoke-from-review-to-clean-study-no-build-no-zip-no-share-no-delivery.py"
readability59 = root / "scripts" / "dev" / "check-ui-polish-readability-pass-no-build-no-zip-no-share-no-delivery.py"

watch_paths = [
    out_dir / "explanation_drafts.preview.json",
    out_dir / "manual_learning_evidence.json",
    out_dir / "manual_study_items.preview.json",
    out_dir / "study_items.preview.json",
]

def fail(message: str):
    raise SystemExit(message)

def sha_or_missing(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fetch(url: str):
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")

for path in [doc_path, web_path, smoke58, readability59]:
    if not path.exists():
        fail("FAILED_V0860_REQUIRED_FILE_MISSING=" + str(path))

doc = doc_path.read_text(encoding="utf-8", errors="replace")
web = web_path.read_text(encoding="utf-8", errors="replace")

for term in [
    "v0.8.60 Package rebuild preflight",
    "It does not perform the package rebuild.",
    "It does not create a ZIP.",
    "It does not copy anything to OneDrive.",
    "It does not share anything.",
    "It does not deliver anything.",
    "v0.8.50",
    "v0.8.51",
    "v0.8.52",
    "v0.8.53",
    "v0.8.54",
    "v0.8.55",
    "v0.8.56",
    "v0.8.57",
    "v0.8.58",
    "v0.8.59",
    "no POST is called",
    "no draft is created",
    "no Study cards are created",
    "no Progress is written",
    "No build.",
    "No ZIP.",
    "No package rebuild.",
    "No OneDrive copy.",
    "No share.",
    "No delivery.",
]:
    if term not in doc:
        fail("FAILED_V0860_DOC_TERM_MISSING=" + term)

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
        fail("FAILED_V0860_CHAIN_MARKER_MISSING=" + marker)

changed = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/package-rebuild-preflight-after-owner-approval-no-build-no-zip-no-share-no-delivery.md",
    "scripts/dev/check-package-rebuild-preflight-after-owner-approval-no-build-no-zip-no-share-no-delivery.py",
    "scripts/dev/check-package-rebuild-preflight-after-owner-approval-no-build-no-zip-no-share-no-delivery.ps1",
}

for line in changed:
    if not line.strip():
        continue
    path = line[3:].replace("\\", "/")
    if path not in allowed:
        fail("FAILED_V0860_UNEXPECTED_GIT_STATUS_PATH=" + line)

before = {str(path): sha_or_missing(path) for path in watch_paths}

health_status, _ = fetch("http://127.0.0.1:8787/health")
if health_status != 200:
    fail("FAILED_V0860_HEALTH_STATUS=" + str(health_status))

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
        fail("FAILED_V0860_" + label + "_STATUS=" + str(status))

for term in [
    "course-tools-review-document-entry",
    "Deschide Revizuire document",
]:
    if term not in course_html:
        fail("FAILED_V0860_COURSE_TOOLS_TERM_MISSING=" + term)

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
        fail("FAILED_V0860_REVIEW_TERM_MISSING=" + term)

for term in [
    "friendly-explanation-save-form-shell",
    "friendly-explanation-save-form",
    'method="post"',
    'action="/review-drafts/save-explanation-draft"',
    "Salvează draft local",
]:
    if term not in draft_html:
        fail("FAILED_V0860_DRAFT_FORM_TERM_MISSING=" + term)

for term in [
    "study-clean-preview-route",
    "study-clean-preview-read-only-status",
    "Read-only",
    "nu creează carduri reale",
    "nu scrie Progress",
    "study-clean-preview-cards",
]:
    if term not in clean_html:
        fail("FAILED_V0860_CLEAN_PREVIEW_TERM_MISSING=" + term)

if not ("Study curat" in clean_html and "previzualizare" in clean_html):
    fail("FAILED_V0860_CLEAN_PREVIEW_TITLE_MISSING")

if not ("study-clean-preview-card" in clean_html or "study-clean-preview-empty-state" in clean_html):
    fail("FAILED_V0860_CLEAN_PREVIEW_CARD_OR_EMPTY_STATE_MISSING")

if "friendly-explanation-draft-save-result" in review_html or "friendly-explanation-draft-save-result" in draft_html or "friendly-explanation-draft-save-result" in clean_html:
    fail("FAILED_V0860_POST_RESULT_RENDERED_WITHOUT_POST")

after = {str(path): sha_or_missing(path) for path in watch_paths}

changed_artifacts = [
    path for path in watch_paths
    if after[str(path)] != before[str(path)]
]
if changed_artifacts:
    fail("FAILED_V0860_PREFLIGHT_CHANGED_ARTIFACTS=" + ",".join(str(path) for path in changed_artifacts))

if "voila-v0.8.60" in "\n".join(subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()).lower():
    fail("FAILED_V0860_PACKAGE_ARTIFACT_APPEARS_IN_GIT_STATUS")

evidence_dir = Path(r"D:\dev\tester-runs\v0860-package-rebuild-preflight-after-owner-approval-no-build-no-zip-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_60_PACKAGE_REBUILD_PREFLIGHT_CHECK": "PASS",
    "implementation_performed": False,
    "package_rebuild_preflight_performed": True,
    "chain_v0850_to_v0857_markers_present": True,
    "v0858_smoke_script_present": True,
    "v0859_readability_script_present": True,
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
    "read_only_preflight": True,
    "explanation_drafts_unchanged": True,
    "manual_learning_evidence_unchanged": True,
    "manual_study_items_preview_unchanged": True,
    "study_items_preview_unchanged": True,
    "web_app_changed": False,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "default_study_changed": False,
    "study_cards_created": False,
    "progress_write_added": False,
    "manual_evidence_written": False,
    "ocr_started": False,
    "languagetool_started": False,
    "formula_ocr_performed": False,
    "crop_extraction_performed": False,
    "build_performed": False,
    "package_rebuild_performed": False,
    "new_zip_created": False,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "public_release_created": False,
    "PACKAGE_REBUILD_PREFLIGHT": "PASS_OWNER_LOCAL_PREFLIGHT_ONLY_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "READY_FOR_SEPARATE_OWNER_APPROVED_REBUILD_MILESTONE_ONLY",
    "REBUILD_APPROVED_IN_THIS_MILESTONE": False,
    "SHARE_OR_DELIVERY_APPROVED": False,
    "POLICY": "package_rebuild_preflight_after_owner_approval_no_build_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.61-owner-local-package-rebuild-with-review-document-clean-study-flow-no-share-no-delivery-only-if-owner-explicitly-approves-build_zip",
}

out_json = evidence_dir / "V0.8.60-PACKAGE-REBUILD-PREFLIGHT-CHECK.json"
out_md = evidence_dir / "V0.8.60-PACKAGE-REBUILD-PREFLIGHT-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.60 Package rebuild preflight\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
