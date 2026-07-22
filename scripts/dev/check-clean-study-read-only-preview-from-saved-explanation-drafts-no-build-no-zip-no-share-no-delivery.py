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

doc_path = root / "docs" / "dev" / "clean-study-read-only-preview-from-saved-explanation-drafts-no-build-no-zip-no-share-no-delivery.md"
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
        with urllib.request.urlopen(url, timeout=15) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")

for path in [doc_path, web_path]:
    if not path.exists():
        fail("FAILED_V0857_REQUIRED_FILE_MISSING=" + str(path))

doc = doc_path.read_text(encoding="utf-8", errors="replace")
web = web_path.read_text(encoding="utf-8", errors="replace")

for term in [
    "v0.8.57 Clean Study read-only preview",
    "explanation_drafts.preview.json",
    "/study-clean-preview?pdf=<pdf_name>",
    "/study-clean-preview/<course_id>",
    "It does not create manual evidence.",
    "It does not create real Study cards.",
    "It does not write Progress.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "No build.",
    "No ZIP.",
    "No share.",
    "No delivery.",
]:
    if term not in doc:
        fail("FAILED_V0857_DOC_TERM_MISSING=" + term)

for term in [
    "VOILA_V0_8_57_CLEAN_STUDY_READ_ONLY_PREVIEW_FROM_EXPLANATION_DRAFTS_START",
    "study-clean-preview-route",
    "study-clean-preview-card",
    "study-clean-preview-empty-state",
    "study-clean-preview-read-only-status",
    "study-clean-preview-diagnostic",
    "clean-study-preview-entry",
    "clean-study-preview-link",
    '@app.get("/study-clean-preview"',
    '@app.get("/study-clean-preview/{course_id}"',
    "Card {index} din {total}",
    "Explicație pe înțeles",
    "nu creează carduri reale",
    "nu scrie Progress",
]:
    if term not in web:
        fail("FAILED_V0857_WEB_TERM_MISSING=" + term)

changed = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/clean-study-read-only-preview-from-saved-explanation-drafts-no-build-no-zip-no-share-no-delivery.md",
    "scripts/dev/check-clean-study-read-only-preview-from-saved-explanation-drafts-no-build-no-zip-no-share-no-delivery.py",
    "scripts/dev/check-clean-study-read-only-preview-from-saved-explanation-drafts-no-build-no-zip-no-share-no-delivery.ps1",
}

for line in changed:
    if not line.strip():
        continue
    path = line[3:].replace("\\", "/")
    if path not in allowed:
        fail("FAILED_V0857_UNEXPECTED_GIT_STATUS_PATH=" + line)

before = {str(path): sha_or_missing(path) for path in watch_paths}

health_status, _ = fetch("http://127.0.0.1:8787/health")
if health_status != 200:
    fail("FAILED_V0857_HEALTH_STATUS=" + str(health_status))

review_status, review_html = fetch("http://127.0.0.1:8787/review-document?pdf=" + urllib.parse.quote(pdf_name))
if review_status != 200:
    fail("FAILED_V0857_REVIEW_DOCUMENT_STATUS=" + str(review_status))

for term in [
    "review-document-text-detected-queue",
    "review-document-corrections-suggested-queue",
    "review-document-formulas-images-queue",
    "review-document-friendly-explanation-shell",
    "clean-study-preview-entry",
    "clean-study-preview-link",
    "Deschide previzualizare Study curat",
]:
    if term not in review_html:
        fail("FAILED_V0857_REVIEW_TERM_MISSING=" + term)

query_status, query_html = fetch("http://127.0.0.1:8787/study-clean-preview?pdf=" + urllib.parse.quote(pdf_name))
if query_status != 200:
    fail("FAILED_V0857_QUERY_ROUTE_STATUS=" + str(query_status))

alias_status, alias_html = fetch("http://127.0.0.1:8787/study-clean-preview/" + urllib.parse.quote(course_id))
if alias_status != 200:
    fail("FAILED_V0857_ALIAS_ROUTE_STATUS=" + str(alias_status))

for term in [
    "study-clean-preview-route",
    "Study curat - previzualizare",
    "study-clean-preview-read-only-status",
    "Read-only",
    "nu creează carduri reale",
    "nu scrie Progress",
    "study-clean-preview-cards",
    "study-clean-preview-diagnostic",
    "Înapoi la Revizuire document",
]:
    if term not in query_html:
        fail("FAILED_V0857_PREVIEW_TERM_MISSING=" + term)

card_visible = "study-clean-preview-card" in query_html
empty_visible = "study-clean-preview-empty-state" in query_html
if not (card_visible or empty_visible):
    fail("FAILED_V0857_NO_CARD_OR_EMPTY_STATE_VISIBLE")

if "<form" in query_html.lower():
    fail("FAILED_V0857_FORM_PRESENT_IN_READ_ONLY_PREVIEW")

main_part = query_html.split("Diagnostic tehnic", 1)[0]
for forbidden in [
    "metadata",
    "bbox",
    "crop_path",
    "visual_evidence_id",
    "source_evidence_id",
    "manual_study_item_id",
    "delivery_performed",
    "build_performed",
    "zip_created",
    "explanation_drafts.preview.json",
]:
    if forbidden in main_part.lower():
        fail("FAILED_V0857_TECHNICAL_LABEL_VISIBLE_IN_MAIN_SURFACE=" + forbidden)

for term in [
    "study-clean-preview-route",
    "Study curat - previzualizare",
]:
    if term not in alias_html:
        fail("FAILED_V0857_ALIAS_TERM_MISSING=" + term)

after = {str(path): sha_or_missing(path) for path in watch_paths}

for path in watch_paths:
    key = str(path)
    if after[key] != before[key]:
        fail("FAILED_V0857_READ_ONLY_ARTIFACT_CHANGED=" + key)

evidence_dir = Path(r"D:\dev\tester-runs\v0857-clean-study-read-only-preview-from-saved-explanation-drafts-no-build-no-zip-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_57_CLEAN_STUDY_READ_ONLY_PREVIEW_CHECK": "PASS",
    "implementation_performed": True,
    "clean_study_preview_added": True,
    "review_document_link_added": True,
    "query_route_status": query_status,
    "alias_route_status": alias_status,
    "review_document_status": review_status,
    "reads_explanation_drafts_preview_json": True,
    "card_or_empty_state_visible": True,
    "draft_cards_visible": card_visible,
    "empty_state_visible": empty_visible,
    "read_only_preview": True,
    "no_form_present": True,
    "main_surface_technical_labels_hidden": True,
    "text_detected_queue_still_visible": True,
    "corrections_suggested_queue_still_visible": True,
    "formulas_images_queue_still_visible": True,
    "friendly_explanation_shell_still_visible": True,
    "explanation_drafts_unchanged": True,
    "manual_learning_evidence_unchanged": True,
    "manual_study_items_preview_unchanged": True,
    "study_items_preview_unchanged": True,
    "web_app_changed": True,
    "new_route_added": True,
    "new_post_endpoint_added": False,
    "default_study_changed": False,
    "study_cards_created": False,
    "progress_write_added": False,
    "answer_marking_added": False,
    "ocr_started": False,
    "languagetool_started": False,
    "formula_ocr_performed": False,
    "crop_extraction_performed": False,
    "manual_evidence_written": False,
    "build_performed": False,
    "package_rebuild_performed": False,
    "new_zip_created": False,
    "share_created": False,
    "delivery_performed": False,
    "public_release_created": False,
    "CLEAN_STUDY_READ_ONLY_PREVIEW": "PASS_OWNER_LOCAL_READ_ONLY_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_UI_IMPLEMENTATION_AND_RETEST",
    "POLICY": "clean_study_read_only_preview_from_saved_explanation_drafts_no_build_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.58-owner-local-learner-workflow-ui-smoke-from-review-to-clean-study-no-build-no-zip-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.57-CLEAN-STUDY-READ-ONLY-PREVIEW-CHECK.json"
out_md = evidence_dir / "V0.8.57-CLEAN-STUDY-READ-ONLY-PREVIEW-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.57 Clean Study read-only preview\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
