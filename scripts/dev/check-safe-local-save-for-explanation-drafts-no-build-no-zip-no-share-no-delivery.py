from pathlib import Path
import hashlib
import json
import subprocess
import urllib.error
import urllib.parse
import urllib.request

root = Path(".").resolve()
course_id = "03-pag-30-34-vectori-trigonometrie"
pdf_name = course_id + ".pdf"
out_dir = root / "data" / "output" / course_id
draft_path = out_dir / "explanation_drafts.preview.json"

doc_path = root / "docs" / "dev" / "safe-local-save-for-explanation-drafts-no-build-no-zip-no-share-no-delivery.md"
web_path = root / "services" / "api" / "web_app.py"

watch_paths = [
    draft_path,
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

def post_form(url: str, fields: dict):
    body = urllib.parse.urlencode(fields).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")

for path in [doc_path, web_path]:
    if not path.exists():
        fail("FAILED_V0856_REQUIRED_FILE_MISSING=" + str(path))

doc = doc_path.read_text(encoding="utf-8", errors="replace")
web = web_path.read_text(encoding="utf-8", errors="replace")

for term in [
    "v0.8.56 Safe local save for explanation drafts",
    "explanation_drafts.preview.json",
    "It is not manual evidence.",
    "It is not Study data.",
    "It is not Progress data.",
    "No build.",
    "No ZIP.",
    "No share.",
    "No delivery.",
]:
    if term not in doc:
        fail("FAILED_V0856_DOC_TERM_MISSING=" + term)

for term in [
    "VOILA_V0_8_56_SAFE_LOCAL_SAVE_FOR_EXPLANATION_DRAFTS_START",
    "friendly-explanation-save-entry",
    "friendly-explanation-save-form-shell",
    "friendly-explanation-save-form",
    "friendly-explanation-save-button",
    "friendly-explanation-draft-save-result",
    '@app.post("/review-drafts/save-explanation-draft"',
    "explanation_drafts.preview.json",
    "manual_evidence_written",
    "study_card_created",
    "progress_written",
]:
    if term not in web:
        fail("FAILED_V0856_WEB_TERM_MISSING=" + term)

changed = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed_suffixes = {
    "services/api/web_app.py",
    "docs/dev/safe-local-save-for-explanation-drafts-no-build-no-zip-no-share-no-delivery.md",
    "scripts/dev/check-safe-local-save-for-explanation-drafts-no-build-no-zip-no-share-no-delivery.py",
    "scripts/dev/check-safe-local-save-for-explanation-drafts-no-build-no-zip-no-share-no-delivery.ps1",
}

for line in changed:
    if not line.strip():
        continue
    path = line[3:].replace("\\", "/")
    if path not in allowed_suffixes:
        fail("FAILED_V0856_UNEXPECTED_GIT_STATUS_PATH=" + line)

health_status, _ = fetch("http://127.0.0.1:8787/health")
if health_status != 200:
    fail("FAILED_V0856_HEALTH_STATUS=" + str(health_status))

shell_status, shell = fetch("http://127.0.0.1:8787/review-document?pdf=" + urllib.parse.quote(pdf_name))
if shell_status != 200:
    fail("FAILED_V0856_SHELL_STATUS=" + str(shell_status))

form_status, form = fetch("http://127.0.0.1:8787/review-document?pdf=" + urllib.parse.quote(pdf_name) + "&draft=1")
if form_status != 200:
    fail("FAILED_V0856_FORM_STATUS=" + str(form_status))

for term in [
    "review-document-text-detected-queue",
    "review-document-corrections-suggested-queue",
    "review-document-formulas-images-queue",
    "review-document-friendly-explanation-shell",
    "friendly-explanation-save-entry",
]:
    if term not in shell:
        fail("FAILED_V0856_SHELL_TERM_MISSING=" + term)

for term in [
    "friendly-explanation-save-form-shell",
    "friendly-explanation-save-form",
    'method="post"',
    'action="/review-drafts/save-explanation-draft"',
    "Salvează draft local",
    "Titlu scurt",
    "Ce este asta?",
    "Text / zonă verificată",
    "Explicație pe înțeles",
    "De ce este important?",
    "Sursa: pagina X",
    "Limba lecției",
    "Gata pentru studiu",
]:
    if term not in form:
        fail("FAILED_V0856_FORM_TERM_MISSING=" + term)

before = {str(path): sha_or_missing(path) for path in watch_paths}

post_status, post_html = post_form(
    "http://127.0.0.1:8787/review-drafts/save-explanation-draft",
    {
        "pdf_name": pdf_name,
        "course_id": course_id,
        "title": "Vectori — draft local v0.8.56 check",
        "item_type": "Definiție",
        "verified_content": "Text verificat pentru draft local check.",
        "friendly_explanation": "Explicație pe înțeles pentru draftul local check.",
        "importance": "Important pentru Study curat și exerciții.",
        "source_page": "pagina 1",
        "lesson_language": "Română",
        "ready_for_study": "1",
    },
)

if post_status != 200:
    fail("FAILED_V0856_POST_STATUS=" + str(post_status))

for term in [
    "friendly-explanation-draft-save-result",
    "Salvat local",
    "Draftul local a fost salvat",
    "Local-only",
    "nu s-a creat Study card",
    "nu s-a scris Progress",
]:
    if term not in post_html:
        fail("FAILED_V0856_POST_RESULT_TERM_MISSING=" + term)

after = {str(path): sha_or_missing(path) for path in watch_paths}

if after[str(draft_path)] == before[str(draft_path)]:
    fail("FAILED_V0856_DRAFT_ARTIFACT_NOT_CHANGED")

for protected_path in watch_paths[1:]:
    key = str(protected_path)
    if after[key] != before[key]:
        fail("FAILED_V0856_PROTECTED_ARTIFACT_CHANGED=" + key)

if not draft_path.exists():
    fail("FAILED_V0856_DRAFT_ARTIFACT_MISSING=" + str(draft_path))

payload = json.loads(draft_path.read_text(encoding="utf-8", errors="replace"))
drafts = payload.get("drafts")
if not isinstance(drafts, list) or not drafts:
    fail("FAILED_V0856_DRAFT_LIST_EMPTY")

last = drafts[-1]
if last.get("draft_version") != "v0.8.56":
    fail("FAILED_V0856_LAST_DRAFT_VERSION_BAD")
if last.get("title") != "Vectori — draft local v0.8.56 check":
    fail("FAILED_V0856_LAST_DRAFT_TITLE_BAD")
if last.get("local_only") is not True:
    fail("FAILED_V0856_LAST_DRAFT_NOT_LOCAL_ONLY")
if last.get("manual_evidence_written") is not False:
    fail("FAILED_V0856_MANUAL_EVIDENCE_WRITTEN")
if last.get("study_card_created") is not False:
    fail("FAILED_V0856_STUDY_CARD_CREATED")
if last.get("progress_written") is not False:
    fail("FAILED_V0856_PROGRESS_WRITTEN")

evidence_dir = Path(r"D:\dev\tester-runs\v0856-safe-local-save-for-explanation-drafts-no-build-no-zip-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_56_SAFE_LOCAL_SAVE_FOR_EXPLANATION_DRAFTS_CHECK": "PASS",
    "implementation_performed": True,
    "controlled_local_write_introduced": True,
    "draft_entry_visible": True,
    "draft_form_visible": True,
    "post_endpoint_added": True,
    "post_endpoint": "/review-drafts/save-explanation-draft",
    "shell_status": shell_status,
    "form_status": form_status,
    "post_status": post_status,
    "draft_artifact_written": True,
    "draft_artifact_name": "explanation_drafts.preview.json",
    "only_allowed_draft_artifact_changed": True,
    "manual_learning_evidence_unchanged": True,
    "manual_study_items_preview_unchanged": True,
    "study_items_preview_unchanged": True,
    "draft_local_only": True,
    "manual_evidence_written": False,
    "study_cards_created": False,
    "progress_write_added": False,
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
    "SAFE_LOCAL_SAVE_FOR_EXPLANATION_DRAFTS": "PASS_OWNER_LOCAL_DRAFT_WRITE_ONLY_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_UI_IMPLEMENTATION_AND_RETEST",
    "POLICY": "safe_local_save_for_explanation_drafts_no_build_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.57-owner-local-clean-study-read-only-preview-from-saved-explanation-drafts-no-build-no-zip-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.56-SAFE-LOCAL-SAVE-FOR-EXPLANATION-DRAFTS-CHECK.json"
out_md = evidence_dir / "V0.8.56-SAFE-LOCAL-SAVE-FOR-EXPLANATION-DRAFTS-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.56 Safe local save for explanation drafts\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
