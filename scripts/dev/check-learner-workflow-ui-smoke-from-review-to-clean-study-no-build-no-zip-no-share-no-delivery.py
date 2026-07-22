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

doc_path = root / "docs" / "dev" / "learner-workflow-ui-smoke-from-review-to-clean-study-no-build-no-zip-no-share-no-delivery.md"
web_path = root / "services" / "api" / "web_app.py"

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

for path in [doc_path, web_path]:
    if not path.exists():
        fail("FAILED_V0858_REQUIRED_FILE_MISSING=" + str(path))

doc = doc_path.read_text(encoding="utf-8", errors="replace")
web = web_path.read_text(encoding="utf-8", errors="replace")

for term in [
    "v0.8.58 Learner workflow UI smoke",
    "Course Tools opens.",
    "Revizuire document",
    "Text detectat",
    "Corecturi sugerate",
    "Formule și imagini",
    "Explicație prietenoasă",
    "Draft explicație",
    "Study curat — previzualizare",
    "This smoke does not submit the draft form.",
    "It does not call POST endpoints.",
    "It does not create a new explanation draft.",
    "It does not write manual evidence.",
    "It does not create Study cards.",
    "It does not write Progress.",
    "No build.",
    "No ZIP.",
    "No share.",
    "No delivery.",
]:
    if term not in doc:
        fail("FAILED_V0858_DOC_TERM_MISSING=" + term)

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
        fail("FAILED_V0858_REQUIRED_CHAIN_MARKER_MISSING=" + marker)

changed = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/learner-workflow-ui-smoke-from-review-to-clean-study-no-build-no-zip-no-share-no-delivery.md",
    "scripts/dev/check-learner-workflow-ui-smoke-from-review-to-clean-study-no-build-no-zip-no-share-no-delivery.py",
    "scripts/dev/check-learner-workflow-ui-smoke-from-review-to-clean-study-no-build-no-zip-no-share-no-delivery.ps1",
}

for line in changed:
    if not line.strip():
        continue
    path = line[3:].replace("\\", "/")
    if path not in allowed:
        fail("FAILED_V0858_UNEXPECTED_GIT_STATUS_PATH=" + line)

before = {str(path): sha_or_missing(path) for path in watch_paths}

health_status, health_html = fetch("http://127.0.0.1:8787/health")
if health_status != 200:
    fail("FAILED_V0858_HEALTH_STATUS=" + str(health_status))

course_tools_url = "http://127.0.0.1:8787/course-tools?pdf=" + urllib.parse.quote(pdf_name)
review_url = "http://127.0.0.1:8787/review-document?pdf=" + urllib.parse.quote(pdf_name)
draft_form_url = review_url + "&draft=1"
clean_preview_url = "http://127.0.0.1:8787/study-clean-preview?pdf=" + urllib.parse.quote(pdf_name)
clean_preview_alias_url = "http://127.0.0.1:8787/study-clean-preview/" + urllib.parse.quote(course_id)

course_tools_status, course_tools_html = fetch(course_tools_url)
if course_tools_status != 200:
    fail("FAILED_V0858_COURSE_TOOLS_STATUS=" + str(course_tools_status))

for term in [
    "course-tools-review-document-entry",
    "Deschide Revizuire document",
    "/review-document?pdf=03-pag-30-34-vectori-trigonometrie.pdf",
]:
    if term not in course_tools_html:
        fail("FAILED_V0858_COURSE_TOOLS_TERM_MISSING=" + term)

review_status, review_html = fetch(review_url)
if review_status != 200:
    fail("FAILED_V0858_REVIEW_STATUS=" + str(review_status))

for term in [
    "review-document-shell-read-only",
    "review-document-text-detected-queue",
    "review-document-corrections-suggested-queue",
    "review-document-formulas-images-queue",
    "review-document-friendly-explanation-shell",
    "friendly-explanation-save-entry",
    "friendly-explanation-open-draft-form",
    "clean-study-preview-entry",
    "clean-study-preview-link",
    "Deschide previzualizare Study curat",
]:
    if term not in review_html:
        fail("FAILED_V0858_REVIEW_TERM_MISSING=" + term)

draft_form_status, draft_form_html = fetch(draft_form_url)
if draft_form_status != 200:
    fail("FAILED_V0858_DRAFT_FORM_STATUS=" + str(draft_form_status))

for term in [
    "friendly-explanation-save-form-shell",
    "friendly-explanation-save-form",
    'method="post"',
    'action="/review-drafts/save-explanation-draft"',
    "Salvează draft local",
]:
    if term not in draft_form_html:
        fail("FAILED_V0858_DRAFT_FORM_TERM_MISSING=" + term)

clean_status, clean_html = fetch(clean_preview_url)
if clean_status != 200:
    fail("FAILED_V0858_CLEAN_PREVIEW_STATUS=" + str(clean_status))

alias_status, alias_html = fetch(clean_preview_alias_url)
if alias_status != 200:
    fail("FAILED_V0858_CLEAN_PREVIEW_ALIAS_STATUS=" + str(alias_status))

for term in [
    "study-clean-preview-route",
    "study-clean-preview-read-only-status",
    "Read-only",
    "nu creează carduri reale",
    "nu scrie Progress",
    "study-clean-preview-cards",
    "study-clean-preview-diagnostic",
]:
    if term not in clean_html:
        fail("FAILED_V0858_CLEAN_PREVIEW_TERM_MISSING=" + term)

if not ("Study curat" in clean_html and "previzualizare" in clean_html):
    fail("FAILED_V0858_CLEAN_PREVIEW_TITLE_MISSING=Study curat + previzualizare")

card_visible = "study-clean-preview-card" in clean_html
empty_visible = "study-clean-preview-empty-state" in clean_html
if not (card_visible or empty_visible):
    fail("FAILED_V0858_CLEAN_PREVIEW_NO_CARD_OR_EMPTY_STATE")

if "<form" in clean_html.lower():
    fail("FAILED_V0858_CLEAN_PREVIEW_FORM_PRESENT")

if "friendly-explanation-draft-save-result" in clean_html:
    fail("FAILED_V0858_POST_RESULT_APPEARED_WITHOUT_POST")

for term in [
    "study-clean-preview-route",
]:
    if term not in alias_html:
        fail("FAILED_V0858_ALIAS_TERM_MISSING=" + term)

if not ("Study curat" in alias_html and "previzualizare" in alias_html):
    fail("FAILED_V0858_ALIAS_TITLE_MISSING=Study curat + previzualizare")

after = {str(path): sha_or_missing(path) for path in watch_paths}

changed_artifacts = [
    path for path in watch_paths
    if after[str(path)] != before[str(path)]
]
if changed_artifacts:
    fail("FAILED_V0858_READ_ONLY_SMOKE_CHANGED_ARTIFACTS=" + ",".join(str(path) for path in changed_artifacts))

evidence_dir = Path(r"D:\dev\tester-runs\v0858-learner-workflow-ui-smoke-from-review-to-clean-study-no-build-no-zip-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_58_LEARNER_WORKFLOW_UI_SMOKE_CHECK": "PASS",
    "implementation_performed": False,
    "workflow_smoke_performed": True,
    "course_tools_status": course_tools_status,
    "review_document_status": review_status,
    "draft_form_get_status": draft_form_status,
    "clean_preview_status": clean_status,
    "clean_preview_alias_status": alias_status,
    "course_tools_to_review_link_visible": True,
    "text_detected_queue_visible": True,
    "corrections_suggested_queue_visible": True,
    "formulas_images_queue_visible": True,
    "friendly_explanation_shell_visible": True,
    "draft_entry_visible": True,
    "draft_form_get_visible": True,
    "clean_study_preview_link_visible": True,
    "clean_study_preview_visible": True,
    "clean_study_card_or_empty_state_visible": True,
    "clean_study_draft_cards_visible": card_visible,
    "clean_study_empty_state_visible": empty_visible,
    "no_post_called": True,
    "no_post_result_rendered": True,
    "read_only_smoke": True,
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
    "answer_marking_added": False,
    "manual_evidence_written": False,
    "ocr_started": False,
    "languagetool_started": False,
    "formula_ocr_performed": False,
    "crop_extraction_performed": False,
    "build_performed": False,
    "package_rebuild_performed": False,
    "new_zip_created": False,
    "share_created": False,
    "delivery_performed": False,
    "public_release_created": False,
    "LEARNER_WORKFLOW_UI_SMOKE": "PASS_OWNER_LOCAL_READ_ONLY_SMOKE_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_UI_IMPLEMENTATION_AND_RETEST",
    "POLICY": "learner_workflow_ui_smoke_from_review_to_clean_study_no_build_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.59-owner-local-ui-polish-readability-pass-or-separate-package-rebuild-preflight-after-owner-approval",
}

out_json = evidence_dir / "V0.8.58-LEARNER-WORKFLOW-UI-SMOKE-CHECK.json"
out_md = evidence_dir / "V0.8.58-LEARNER-WORKFLOW-UI-SMOKE-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.58 Learner workflow UI smoke\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
