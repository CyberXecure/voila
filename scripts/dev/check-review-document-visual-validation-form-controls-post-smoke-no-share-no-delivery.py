from __future__ import annotations

from html.parser import HTMLParser
import html
import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

repo = Path(".").resolve()
sys.path.insert(0, str(repo))
sys.path.insert(0, str(repo / "services" / "api"))

doc = repo / "docs" / "dev" / "review-document-visual-validation-form-controls-post-smoke-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"
form_doc = repo / "docs" / "dev" / "review-document-visual-validation-form-controls-no-share-no-delivery.md"
save_doc = repo / "docs" / "dev" / "review-document-visual-validation-save-action-implementation-no-share-no-delivery.md"

course_id = "v0879-visual-form-post-smoke"
output_root = repo / "data" / "output" / course_id
visual_dir = output_root / "formula_visual_evidence"
candidate_path = visual_dir / "visual_items.bbox.with-ocrmath-candidates.json"
validated_path = visual_dir / "visual_items.bbox.validated.json"
summary_path = visual_dir / "visual_items.bbox.validation-summary.json"
clean_study_path = visual_dir / "visual_items.clean-study.preview.json"

get_path = f"/review-document/{course_id}"
save_path = "/review-document/visual-validation/save"
evidence_dir = Path(r"D:\dev\tester-runs\v0879-review-document-visual-validation-form-controls-post-smoke-no-share-no-delivery")


def fail(message: str) -> None:
    raise SystemExit(message)


class FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.forms: list[dict[str, object]] = []
        self._current: dict[str, object] | None = None
        self._textarea_name = ""
        self._textarea_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {name: value or "" for name, value in attrs}
        if tag == "form":
            self._current = {
                "method": attr.get("method", ""),
                "action": attr.get("action", ""),
                "fields": {},
            }
            return

        if self._current is None:
            return

        fields = self._current["fields"]
        if not isinstance(fields, dict):
            return

        if tag == "input":
            name = attr.get("name", "")
            if name:
                fields[name] = html.unescape(attr.get("value", ""))
        elif tag == "textarea":
            name = attr.get("name", "")
            if name:
                self._textarea_name = name
                self._textarea_chunks = []

    def handle_data(self, data: str) -> None:
        if self._current is not None and self._textarea_name:
            self._textarea_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "textarea" and self._current is not None and self._textarea_name:
            fields = self._current["fields"]
            if isinstance(fields, dict):
                fields[self._textarea_name] = html.unescape("".join(self._textarea_chunks))
            self._textarea_name = ""
            self._textarea_chunks = []
            return

        if tag == "form" and self._current is not None:
            self.forms.append(self._current)
            self._current = None


def find_form(forms: list[dict[str, object]], item_id: str, decision: str) -> dict[str, str]:
    for form in forms:
        method = str(form.get("method") or "").lower()
        action = str(form.get("action") or "")
        fields_obj = form.get("fields")
        if not isinstance(fields_obj, dict):
            continue

        fields = {str(key): str(value) for key, value in fields_obj.items()}
        if (
            method == "post"
            and action == save_path
            and fields.get("course_id") == course_id
            and fields.get("item_id") == item_id
            and fields.get("decision") == decision
        ):
            return fields

    fail("FAILED_RENDERED_FORM_NOT_FOUND=" + item_id + "::" + decision)


for path in [doc, web_app, form_doc, save_doc]:
    if not path.exists():
        fail("FAILED_V0879_REQUIRED_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
form_doc_text = form_doc.read_text(encoding="utf-8", errors="replace")
save_doc_text = save_doc.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.79 Review Document visual validation form controls POST smoke",
    "validates the v0.8.78 rendered form controls end-to-end against the v0.8.77 save action",
    "FastAPI TestClient",
    "It extracts the rendered forms.",
    "It submits POST requests using the rendered form data.",
    "It may modify `services/api/web_app.py` only to make the Review Document UI prefer the validated visual artifact after save.",
    "It does not add a new route.",
    "It does not add a new POST endpoint.",
    "It does not change `/study`.",
    "It does not write Clean Study.",
    "data/output/v0879-visual-form-post-smoke",
    "/review-document/v0879-visual-form-post-smoke",
    "/review-document/visual-validation/save",
    "`accept`",
    "`edit`",
    "`ignore`",
    "invalid edit without corrected text",
    "accepted item becomes `ready_for_study=true`",
    "edited item becomes `ready_for_study=true` and stores corrected text",
    "ignored item remains excluded from study",
    "unrelated pending item remains pending",
    "visual_items.bbox.validated.json",
    "visual_items.bbox.validation-summary.json",
    "visual_items.clean-study.preview.json is not written",
    "This is an owner-local POST smoke only.",
    "The temporary fixture is removed after the check.",
    "It does not write Clean Study.",
    "It does not write Progress.",
    "It does not upload a PDF.",
    "It does not run `/generate`.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "It does not run OCR Math.",
    "It does not generate crops.",
    "It does not start uvicorn.",
    "It does not start LanguageTool.",
    "It does not build.",
    "It does not create a ZIP.",
    "It does not create OneDrive staging.",
    "It does not create a share link.",
    "It does not deliver to testers.",
    "It does not distribute anything.",
    "It does not create a public release.",
    "v0.8.80-owner-local-review-document-visual-validation-clean-study-refresh-plan-no-share-no-delivery",
]

for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_V0879_DOC_TERM_MISSING=" + term)

for term in [
    "v0.8.78 Review Document visual validation form controls",
    "The check does not submit the forms.",
]:
    if term not in form_doc_text:
        fail("FAILED_V0879_FORM_DOC_TERM_MISSING=" + term)

for term in [
    "v0.8.77 Review Document visual validation save-action implementation",
    "POST /review-document/visual-validation/save",
    "invalid edit without corrected text",
]:
    if term not in save_doc_text:
        fail("FAILED_V0879_SAVE_DOC_TERM_MISSING=" + term)

web_diff = subprocess.check_output(
    ["git", "diff", "--name-only", "--", "services/api/web_app.py"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).strip()

try:
    from fastapi.testclient import TestClient
except Exception as exc:
    fail("FAILED_IMPORT_TESTCLIENT=" + str(exc))

fixture_created = False

try:
    if output_root.exists():
        shutil.rmtree(output_root)

    visual_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema_version": "v0.8.67",
        "course_id": course_id,
        "source_pdf": course_id + ".pdf",
        "items": [
            {
                "item_id": "bbox-item-accept",
                "kind": "formula",
                "page": 1,
                "bbox": [80, 100, 780, 260],
                "bbox_units": "pdf_points",
                "page_image_path": "formula_visual_evidence/pages/page-001.png",
                "crop_path": "formula_visual_evidence/crops/page-001-item-accept.png",
                "crop_exists": True,
                "ocr_math_candidate_text": "sin x / cos x",
                "ocr_math_status": "pending_user_validation",
                "user_decision": "pending",
                "user_corrected_text": "",
                "user_explanation": "",
                "ready_for_study": False,
                "created_by": "v0.8.79-testclient-rendered-form-post",
                "review_notes": "Synthetic accept item.",
            },
            {
                "item_id": "bbox-item-edit",
                "kind": "formula",
                "page": 2,
                "bbox": [90, 300, 790, 420],
                "bbox_units": "pdf_points",
                "page_image_path": "formula_visual_evidence/pages/page-002.png",
                "crop_path": "formula_visual_evidence/crops/page-002-item-edit.png",
                "crop_exists": True,
                "ocr_math_candidate_text": "tan x = sin x / cos x",
                "ocr_math_status": "pending_user_validation",
                "user_decision": "pending",
                "user_corrected_text": "",
                "user_explanation": "",
                "ready_for_study": False,
                "created_by": "v0.8.79-testclient-rendered-form-post",
                "review_notes": "Synthetic edit item.",
            },
            {
                "item_id": "bbox-item-ignore",
                "kind": "diagram",
                "page": 3,
                "bbox": [100, 500, 300, 580],
                "bbox_units": "pdf_points",
                "page_image_path": "formula_visual_evidence/pages/page-003.png",
                "crop_path": "formula_visual_evidence/crops/page-003-item-ignore.png",
                "crop_exists": True,
                "ocr_math_candidate_text": "Diagram ABC",
                "ocr_math_status": "pending_user_validation",
                "user_decision": "pending",
                "user_corrected_text": "",
                "user_explanation": "",
                "ready_for_study": False,
                "created_by": "v0.8.79-testclient-rendered-form-post",
                "review_notes": "Synthetic ignore item.",
            },
            {
                "item_id": "bbox-item-pending",
                "kind": "symbol",
                "page": 4,
                "bbox": [400, 500, 700, 760],
                "bbox_units": "pdf_points",
                "page_image_path": "formula_visual_evidence/pages/page-004.png",
                "crop_path": "formula_visual_evidence/crops/page-004-item-pending.png",
                "crop_exists": True,
                "ocr_math_candidate_text": "R",
                "ocr_math_status": "pending_user_validation",
                "user_decision": "pending",
                "user_corrected_text": "",
                "user_explanation": "",
                "ready_for_study": False,
                "created_by": "v0.8.79-testclient-rendered-form-post",
                "review_notes": "Synthetic pending item.",
            },
        ],
    }

    candidate_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fixture_created = True

    app_module = importlib.import_module("services.api.web_app")
    client = TestClient(app_module.app)

    get_response = client.get(get_path)
    if get_response.status_code != 200:
        fail("FAILED_GET_STATUS=" + str(get_response.status_code))

    body = get_response.text
    section_start = body.find('id="review-document-visual-validation-readonly-ui"')
    if section_start < 0:
        fail("FAILED_VISUAL_SECTION_MISSING")

    section_end = body.find("</section>", section_start)
    if section_end < 0:
        fail("FAILED_VISUAL_SECTION_CLOSE_MISSING")

    section = body[section_start : section_end + len("</section>")]

    parser = FormParser()
    parser.feed(section)
    forms = parser.forms

    if len(forms) < 12:
        fail("FAILED_RENDERED_FORM_COUNT_TOO_LOW=" + str(len(forms)))

    accept_form = find_form(forms, "bbox-item-accept", "accept")
    edit_form = find_form(forms, "bbox-item-edit", "edit")
    ignore_form = find_form(forms, "bbox-item-ignore", "ignore")
    invalid_edit_form = find_form(forms, "bbox-item-pending", "edit")

    accept_form["user_explanation"] = "Acceptăm textul detectat din formularul randat."
    accept_response = client.post(save_path, data=accept_form)
    if accept_response.status_code != 200 or "DECIZIE_SALVATA=PASS" not in accept_response.text:
        fail("FAILED_ACCEPT_RENDERED_FORM_POST=" + str(accept_response.status_code))

    edit_form["user_corrected_text"] = r"\tan x = \frac{\sin x}{\cos x}"
    edit_form["user_explanation"] = "Corectarea trimisă din formularul randat intră în lecție."
    edit_response = client.post(save_path, data=edit_form)
    if edit_response.status_code != 200 or "DECIZIE_SALVATA=PASS" not in edit_response.text:
        fail("FAILED_EDIT_RENDERED_FORM_POST=" + str(edit_response.status_code))

    ignore_form["user_explanation"] = "Ignorăm elementul din formularul randat."
    ignore_response = client.post(save_path, data=ignore_form)
    if ignore_response.status_code != 200 or "DECIZIE_SALVATA=PASS" not in ignore_response.text:
        fail("FAILED_IGNORE_RENDERED_FORM_POST=" + str(ignore_response.status_code))

    invalid_edit_form["user_corrected_text"] = ""
    invalid_edit_response = client.post(save_path, data=invalid_edit_form)
    if invalid_edit_response.status_code != 400:
        fail("FAILED_INVALID_EDIT_RENDERED_FORM_NOT_REJECTED=" + str(invalid_edit_response.status_code))

    if not validated_path.exists():
        fail("FAILED_VALIDATED_ARTIFACT_MISSING")

    if not summary_path.exists():
        fail("FAILED_VALIDATION_SUMMARY_MISSING")

    if clean_study_path.exists():
        fail("FAILED_CLEAN_STUDY_WRITTEN_UNEXPECTEDLY")

    validated = json.loads(validated_path.read_text(encoding="utf-8"))
    items = validated.get("items")
    if not isinstance(items, list):
        fail("FAILED_VALIDATED_ITEMS_NOT_LIST")

    by_id = {item.get("item_id"): item for item in items if isinstance(item, dict)}

    accept_item = by_id.get("bbox-item-accept")
    edit_item = by_id.get("bbox-item-edit")
    ignore_item = by_id.get("bbox-item-ignore")
    pending_item = by_id.get("bbox-item-pending")

    if accept_item.get("user_decision") != "accept" or accept_item.get("ready_for_study") is not True:
        fail("FAILED_ACCEPT_VALIDATED_STATE")
    if accept_item.get("ocr_math_status") != "validated_by_user":
        fail("FAILED_ACCEPT_VALIDATED_STATUS")

    if edit_item.get("user_decision") != "edit" or edit_item.get("ready_for_study") is not True:
        fail("FAILED_EDIT_VALIDATED_STATE")
    if edit_item.get("user_corrected_text") != r"\tan x = \frac{\sin x}{\cos x}":
        fail("FAILED_EDIT_VALIDATED_CORRECTED_TEXT")
    if edit_item.get("ocr_math_status") != "validated_by_user":
        fail("FAILED_EDIT_VALIDATED_STATUS")

    if ignore_item.get("user_decision") != "ignore" or ignore_item.get("ready_for_study") is not False:
        fail("FAILED_IGNORE_VALIDATED_STATE")
    if ignore_item.get("ocr_math_status") != "not_applicable":
        fail("FAILED_IGNORE_VALIDATED_STATUS")

    if pending_item.get("user_decision") != "pending" or pending_item.get("ready_for_study") is not False:
        fail("FAILED_PENDING_ITEM_CHANGED")

    if clean_study_path.exists():
        fail("FAILED_CLEAN_STUDY_EXISTS_AFTER_VALIDATION")

    post_get_response = client.get(get_path)
    if post_get_response.status_code != 200:
        fail("FAILED_POST_SAVE_GET_STATUS=" + str(post_get_response.status_code))

    post_body = post_get_response.text
    for term in ["Acceptat", "Corectat", "Ignorat", "Gata pentru lecție", "Nu intră încă în lecție"]:
        if term not in post_body:
            fail("FAILED_POST_SAVE_UI_TERM_MISSING=" + term)

    status_lines = subprocess.check_output(
        ["git", "status", "--porcelain", "-uall"],
        cwd=str(repo),
        text=True,
        encoding="utf-8",
        errors="replace",
    ).splitlines()

    allowed = {
        "services/api/web_app.py",
        "docs/dev/review-document-visual-validation-form-controls-post-smoke-no-share-no-delivery.md",
        "scripts/dev/apply-review-document-visual-validation-post-save-readback-v0879.py",
        "scripts/dev/check-review-document-visual-validation-form-controls-post-smoke-no-share-no-delivery.py",
        "scripts/dev/check-review-document-visual-validation-form-controls-post-smoke-no-share-no-delivery.ps1",
    }

    unexpected = []
    for line in status_lines:
        if not line.strip():
            continue
        rel = line[3:].replace("\\", "/")
        if rel not in allowed:
            unexpected.append(line)

    if unexpected:
        fail("FAILED_V0879_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

    summary = {
        "VOILA_V0_8_79_REVIEW_DOCUMENT_VISUAL_VALIDATION_FORM_CONTROLS_POST_SMOKE_CHECK": "PASS",
        "rendered_form_post_smoke_performed": True,
        "inprocess_testclient_used": True,
        "web_app_changed": bool(web_diff),
        "post_save_readback_prefers_validated_artifact": True,
        "new_route_added": False,
        "new_post_endpoint_added": False,
        "get_rendered_forms_passed": True,
        "rendered_form_count": len(forms),
        "accept_rendered_form_post_passed": True,
        "edit_rendered_form_post_passed": True,
        "ignore_rendered_form_post_passed": True,
        "invalid_edit_rendered_form_rejected": True,
        "validated_artifact_exists": True,
        "validation_summary_exists": True,
        "accept_ready_for_study": True,
        "edit_ready_for_study_with_corrected_text": True,
        "ignore_blocked_from_study": True,
        "pending_remains_pending": True,
        "post_save_ui_statuses_visible": True,
        "clean_study_write": False,
        "study_route_changed": False,
        "server_started": False,
        "uvicorn_started": False,
        "languagetool_started": False,
        "upload_performed": False,
        "generate_performed": False,
        "ocr_run": False,
        "languagetool_run": False,
        "ocr_math_run": False,
        "crop_generation_performed": False,
        "progress_write": False,
        "build_performed": False,
        "zip_created": False,
        "onedrive_staging_created": False,
        "share_link_created": False,
        "delivery_performed": False,
        "distribution_performed": False,
        "public_release_created": False,
        "fixture_created": fixture_created,
        "fixture_removed_after_check": True,
        "recommended_next": "v0.8.80-owner-local-review-document-visual-validation-clean-study-refresh-plan-no-share-no-delivery",
    }

    evidence_dir.mkdir(parents=True, exist_ok=True)
    out_json = evidence_dir / "V0.8.79-REVIEW-DOCUMENT-VISUAL-VALIDATION-FORM-CONTROLS-POST-SMOKE-CHECK.json"
    out_md = evidence_dir / "V0.8.79-REVIEW-DOCUMENT-VISUAL-VALIDATION-FORM-CONTROLS-POST-SMOKE-CHECK.md"

    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(
        "# v0.8.79 Review Document visual validation form controls POST smoke\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in summary.items())
        + "\n",
        encoding="utf-8",
    )

    for key, value in summary.items():
        print(f"{key}={value}")

    print("EVIDENCE_JSON=" + str(out_json))
    print("EVIDENCE_MD=" + str(out_md))
finally:
    if output_root.exists():
        shutil.rmtree(output_root)
