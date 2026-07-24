from __future__ import annotations

import copy
import importlib
import json
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

repo = Path(".").resolve()
sys.path.insert(0, str(repo))
sys.path.insert(0, str(repo / "services" / "api"))

doc = repo / "docs" / "dev" / "review-document-clean-study-refresh-rendered-form-post-smoke-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"

course_id = "v0883-clean-study-refresh-rendered-form-post-smoke"
output_root = repo / "data" / "output" / course_id
visual_dir = output_root / "formula_visual_evidence"
validated_path = visual_dir / "visual_items.bbox.validated.json"
candidate_path = visual_dir / "visual_items.bbox.with-ocrmath-candidates.json"
clean_path = visual_dir / "visual_items.clean-study.preview.json"
clean_summary_path = visual_dir / "visual_items.clean-study.preview-summary.json"
refresh_path = "/review-document/visual-validation/refresh-clean-study-preview"
evidence_dir = Path(r"D:\dev\tester-runs\v0883-review-document-clean-study-refresh-rendered-form-post-smoke-no-share-no-delivery")


class FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.forms: list[dict[str, object]] = []
        self.current: dict[str, object] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {str(k).lower(): (v if v is not None else "") for k, v in attrs}
        if tag.lower() == "form":
            self.current = {"attrs": attrs_dict, "fields": {}}
            return

        if tag.lower() == "input" and self.current is not None:
            name = str(attrs_dict.get("name") or "")
            if not name:
                return
            fields = self.current.get("fields")
            if isinstance(fields, dict):
                fields[name] = str(attrs_dict.get("value") or "")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "form" and self.current is not None:
            self.forms.append(self.current)
            self.current = None


def fail(message: str) -> None:
    raise SystemExit(message)


for path in [doc, web_app]:
    if not path.exists():
        fail("FAILED_V0883_REQUIRED_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
web_text = web_app.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.83 Review Document Clean Study refresh rendered-form POST smoke",
    "rendered `Actualizează lecția curată` form",
    "It does not modify `services/api/web_app.py`.",
    "It does not add a route.",
    "It does not add a POST endpoint.",
    "render `GET /review-document/<course_id>`",
    "find the rendered Clean Study refresh form",
    "verify the form submits only `course_id`",
    "verify GET does not write Clean Study",
    "submit the rendered form through FastAPI TestClient",
    "verify Clean Study preview artifacts are written only after explicit POST",
    "POST /review-document/visual-validation/refresh-clean-study-preview",
    "`method=\"post\"`",
    "`/review-document/visual-validation/refresh-clean-study-preview`",
    "`course_id`",
    "item data",
    "item IDs",
    "crop paths",
    "bbox data",
    "ready flags",
    "OCR Math status",
    "user decisions",
    "corrected text",
    "explanation text",
    "formula_visual_evidence/visual_items.clean-study.preview.json",
    "formula_visual_evidence/visual_items.clean-study.preview-summary.json",
    "formula_visual_evidence/visual_items.bbox.validated.json",
    "The route must not write Progress.",
    "The route must not change `/study`.",
    "accepted item is included",
    "edited item is included with corrected text",
    "ignored item is excluded",
    "pending item is excluded",
    "malformed item is excluded",
    "older candidate artifact is not used for refresh",
    "This milestone does not modify `services/api/web_app.py`.",
    "It does not add UI.",
    "It does not start uvicorn.",
    "It does not start LanguageTool.",
    "It does not upload a PDF.",
    "It does not run `/generate`.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "It does not run OCR Math.",
    "It does not generate crops.",
    "It does not write manual decisions.",
    "It does not write Progress.",
    "It does not change `/study`.",
    "It does not build.",
    "It does not create a ZIP.",
    "It does not create OneDrive staging.",
    "It does not create a share link.",
    "It does not deliver to testers.",
    "It does not distribute anything.",
    "It does not create a public release.",
    "v0.8.84-owner-local-clean-study-preview-visual-items-readonly-ui-plan-no-share-no-delivery",
]

for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_V0883_DOC_TERM_MISSING=" + term)

required_web_terms = [
    "VOILA_V0_8_81_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_ACTION_START",
    '@app.post("/review-document/visual-validation/refresh-clean-study-preview")',
    "VOILA_V0_8_82_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_UI_CONTROL_START",
    "review-document-clean-study-refresh-control",
    "data-voila-clean-study-refresh-form",
    "Actualizează lecția curată",
    "/review-document/visual-validation/refresh-clean-study-preview",
]

for term in required_web_terms:
    if term not in web_text:
        fail("FAILED_V0883_WEB_TERM_MISSING=" + term)

if web_text.count('@app.post("/review-document/visual-validation/refresh-clean-study-preview")') != 1:
    fail("FAILED_V0883_REFRESH_POST_ROUTE_COUNT_UNEXPECTED")

web_diff = subprocess.check_output(
    ["git", "diff", "--name-only", "--", "services/api/web_app.py"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).strip()

if web_diff:
    fail("FAILED_V0883_WEB_APP_HAS_WORKTREE_DIFF=" + web_diff)

subprocess.check_call([sys.executable, "-m", "py_compile", str(web_app)], cwd=str(repo))

fixture_created = False
ui_refresh_form_found = False
get_did_not_write_clean_study = False
rendered_form_post_passed = False

try:
    if output_root.exists():
        shutil.rmtree(output_root)

    visual_dir.mkdir(parents=True, exist_ok=True)

    validated_payload = {
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
                "ocr_math_status": "validated_by_user",
                "user_decision": "accept",
                "user_corrected_text": "",
                "user_explanation": "Acceptăm textul detectat.",
                "ready_for_study": True,
                "created_by": "v0.8.83-testclient-rendered-form-post",
                "review_notes": "Accepted item.",
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
                "ocr_math_status": "validated_by_user",
                "user_decision": "edit",
                "user_corrected_text": r"\tan x = \frac{\sin x}{\cos x}",
                "user_explanation": "Formula corectată intră în lecție.",
                "ready_for_study": True,
                "created_by": "v0.8.83-testclient-rendered-form-post",
                "review_notes": "Edited item.",
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
                "ocr_math_status": "not_applicable",
                "user_decision": "ignore",
                "user_corrected_text": "",
                "user_explanation": "Ignorat.",
                "ready_for_study": False,
                "created_by": "v0.8.83-testclient-rendered-form-post",
                "review_notes": "Ignored item.",
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
                "created_by": "v0.8.83-testclient-rendered-form-post",
                "review_notes": "Pending item.",
            },
            {
                "item_id": "bbox-item-malformed",
                "kind": "formula",
                "page": 5,
                "bbox": [10, 20, 30, 40],
                "bbox_units": "pdf_points",
                "page_image_path": "formula_visual_evidence/pages/page-005.png",
                "crop_path": "",
                "crop_exists": False,
                "ocr_math_candidate_text": "",
                "ocr_math_status": "validated_by_user",
                "user_decision": "accept",
                "user_corrected_text": "",
                "user_explanation": "",
                "ready_for_study": True,
                "created_by": "v0.8.83-testclient-rendered-form-post",
                "review_notes": "Malformed ready item without crop/text.",
            },
        ],
    }

    original_validated_payload = copy.deepcopy(validated_payload)

    validated_path.write_text(json.dumps(validated_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    candidate_path.write_text(
        json.dumps(
            {
                "schema_version": "v0.8.67",
                "course_id": course_id,
                "source_pdf": "must-not-be-read.pdf",
                "items": [
                    {
                        "item_id": "candidate-only-item-must-not-appear",
                        "kind": "formula",
                        "page": 9,
                        "bbox": [1, 2, 3, 4],
                        "bbox_units": "pdf_points",
                        "page_image_path": "formula_visual_evidence/pages/unused.png",
                        "crop_path": "formula_visual_evidence/crops/unused.png",
                        "crop_exists": True,
                        "ocr_math_candidate_text": "SHOULD_NOT_APPEAR",
                        "ocr_math_status": "pending_user_validation",
                        "user_decision": "pending",
                        "user_corrected_text": "",
                        "user_explanation": "",
                        "ready_for_study": False,
                        "created_by": "v0.8.83-testclient-rendered-form-post",
                        "review_notes": "Candidate artifact should not be read.",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    fixture_created = True

    app_module = importlib.import_module("services.api.web_app")
    from fastapi.testclient import TestClient

    client = TestClient(app_module.app)

    response = client.get("/review-document/" + course_id)
    if response.status_code != 200:
        fail("FAILED_GET_REVIEW_DOCUMENT=" + str(response.status_code))

    html = response.text

    for term in [
        "review-document-clean-study-refresh-control",
        "data-voila-clean-study-refresh-form",
        "Actualizează lecția curată",
        "/review-document/visual-validation/refresh-clean-study-preview",
        "Deschide lecția curată",
        "/study-clean-preview/" + course_id,
    ]:
        if term not in html:
            fail("FAILED_V0883_HTML_TERM_MISSING=" + term)

    parser = FormParser()
    parser.feed(html)

    matching_forms = []
    for form in parser.forms:
        attrs = form.get("attrs")
        fields = form.get("fields")
        if not isinstance(attrs, dict) or not isinstance(fields, dict):
            continue

        if (
            str(attrs.get("action") or "") == refresh_path
            and str(attrs.get("method") or "").lower() == "post"
            and str(attrs.get("data-voila-clean-study-refresh-form") or "") == "1"
        ):
            matching_forms.append(form)

    if len(matching_forms) != 1:
        fail("FAILED_REFRESH_RENDERED_FORM_COUNT=" + str(len(matching_forms)))

    refresh_form = matching_forms[0]
    fields = refresh_form.get("fields")
    if not isinstance(fields, dict):
        fail("FAILED_REFRESH_FORM_FIELDS_NOT_DICT")

    if fields != {"course_id": course_id}:
        fail("FAILED_REFRESH_FORM_FIELDS_UNEXPECTED=" + json.dumps(fields, ensure_ascii=False, sort_keys=True))

    forbidden_fields = {
        "item_id",
        "crop_path",
        "bbox",
        "ready_for_study",
        "ocr_math_status",
        "user_decision",
        "user_corrected_text",
        "user_explanation",
        "page_image_path",
        "source_pdf",
    }

    submitted_forbidden = sorted(name for name in fields if name in forbidden_fields)
    if submitted_forbidden:
        fail("FAILED_REFRESH_FORM_SUBMITS_FORBIDDEN_FIELDS=" + json.dumps(submitted_forbidden, ensure_ascii=False))

    ui_refresh_form_found = True

    if clean_path.exists() or clean_summary_path.exists():
        fail("FAILED_GET_WROTE_CLEAN_STUDY_BEFORE_POST")

    get_did_not_write_clean_study = True

    post_response = client.post(refresh_path, data=fields)
    if post_response.status_code != 200:
        fail("FAILED_RENDERED_REFRESH_POST_STATUS=" + str(post_response.status_code))

    if "CLEAN_STUDY_REFRESH=PASS" not in post_response.text:
        fail("FAILED_RENDERED_REFRESH_POST_PASS_TEXT_MISSING")

    if "Elemente adăugate în lecție: 2" not in post_response.text:
        fail("FAILED_RENDERED_REFRESH_POST_INCLUDED_COUNT_TEXT_MISSING")

    if "Elemente rămase în afara lecției: 3" not in post_response.text:
        fail("FAILED_RENDERED_REFRESH_POST_EXCLUDED_COUNT_TEXT_MISSING")

    rendered_form_post_passed = True

    if not clean_path.exists():
        fail("FAILED_CLEAN_STUDY_PREVIEW_MISSING_AFTER_RENDERED_POST")

    if not clean_summary_path.exists():
        fail("FAILED_CLEAN_STUDY_SUMMARY_MISSING_AFTER_RENDERED_POST")

    validated_after = json.loads(validated_path.read_text(encoding="utf-8"))
    if validated_after != original_validated_payload:
        fail("FAILED_VALIDATED_ARTIFACT_MODIFIED_BY_REFRESH_POST")

    clean_payload = json.loads(clean_path.read_text(encoding="utf-8"))
    clean_summary = json.loads(clean_summary_path.read_text(encoding="utf-8"))

    clean_items = clean_payload.get("items")
    if not isinstance(clean_items, list):
        fail("FAILED_CLEAN_ITEMS_NOT_LIST")

    included_ids = {item.get("source_visual_item_id") for item in clean_items if isinstance(item, dict)}
    if included_ids != {"bbox-item-accept", "bbox-item-edit"}:
        fail("FAILED_INCLUDED_IDS_UNEXPECTED=" + json.dumps(sorted(included_ids), ensure_ascii=False))

    by_id = {item.get("source_visual_item_id"): item for item in clean_items if isinstance(item, dict)}

    if by_id["bbox-item-accept"].get("answer") != "sin x / cos x":
        fail("FAILED_ACCEPT_ITEM_ANSWER")
    if by_id["bbox-item-edit"].get("answer") != r"\tan x = \frac{\sin x}{\cos x}":
        fail("FAILED_EDIT_ITEM_CORRECTED_TEXT")
    if by_id["bbox-item-edit"].get("explanation") != "Formula corectată intră în lecție.":
        fail("FAILED_EDIT_ITEM_EXPLANATION")

    clean_json = json.dumps(clean_payload, ensure_ascii=False)
    if "SHOULD_NOT_APPEAR" in clean_json or "candidate-only-item-must-not-appear" in clean_json:
        fail("FAILED_CANDIDATE_ARTIFACT_USED_FOR_REFRESH")

    excluded = clean_payload.get("excluded_items")
    if not isinstance(excluded, list):
        fail("FAILED_EXCLUDED_ITEMS_NOT_LIST")

    excluded_ids = {item.get("source_visual_item_id") for item in excluded if isinstance(item, dict)}
    for expected in ["bbox-item-ignore", "bbox-item-pending", "bbox-item-malformed"]:
        if expected not in excluded_ids:
            fail("FAILED_EXPECTED_EXCLUDED_ITEM_MISSING=" + expected)

    if clean_summary.get("clean_study_item_count") != 2:
        fail("FAILED_SUMMARY_CLEAN_ITEM_COUNT")
    if clean_summary.get("excluded_item_count") != 3:
        fail("FAILED_SUMMARY_EXCLUDED_ITEM_COUNT")
    if clean_summary.get("accepted_count") != 1:
        fail("FAILED_SUMMARY_ACCEPTED_COUNT")
    if clean_summary.get("edited_count") != 1:
        fail("FAILED_SUMMARY_EDITED_COUNT")
    if clean_summary.get("progress_write_performed") is not False:
        fail("FAILED_SUMMARY_PROGRESS_WRITE_FLAG")
    if clean_summary.get("study_route_changed") is not False:
        fail("FAILED_SUMMARY_STUDY_ROUTE_FLAG")

    progress_candidates = [
        output_root / "progress.json",
        output_root / "study_progress.json",
        output_root / "progress.preview.json",
    ]
    if any(path.exists() for path in progress_candidates):
        fail("FAILED_PROGRESS_WRITTEN_BY_RENDERED_REFRESH_POST")

finally:
    if output_root.exists():
        shutil.rmtree(output_root)

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/review-document-clean-study-refresh-rendered-form-post-smoke-no-share-no-delivery.md",
    "scripts/dev/check-review-document-clean-study-refresh-rendered-form-post-smoke-no-share-no-delivery.py",
    "scripts/dev/check-review-document-clean-study-refresh-rendered-form-post-smoke-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0883_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary = {
    "VOILA_V0_8_83_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_RENDERED_FORM_POST_SMOKE_CHECK": "PASS",
    "rendered_form_post_smoke_performed": True,
    "web_app_changed": False,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "uses_existing_v0881_refresh_post_route": True,
    "testclient_get_check_performed": True,
    "testclient_rendered_form_post_check_performed": True,
    "ui_refresh_form_found": ui_refresh_form_found,
    "refresh_button_visible": True,
    "refresh_form_method_post": True,
    "refresh_form_action_existing_endpoint": True,
    "refresh_form_submits_only_course_id": True,
    "item_payload_submitted": False,
    "item_id_submitted": False,
    "crop_path_submitted": False,
    "bbox_submitted": False,
    "ready_flag_submitted": False,
    "ocr_math_status_submitted": False,
    "user_decision_submitted": False,
    "corrected_text_submitted": False,
    "explanation_text_submitted": False,
    "clean_study_write_on_get": False,
    "get_did_not_write_clean_study": get_did_not_write_clean_study,
    "rendered_refresh_post_called": True,
    "rendered_form_post_passed": rendered_form_post_passed,
    "clean_study_write_after_explicit_post": True,
    "clean_study_preview_artifact_exists": True,
    "clean_study_preview_summary_exists": True,
    "reads_validated_artifact_only": True,
    "candidate_artifact_not_used_for_refresh": True,
    "accepted_item_included": True,
    "edited_item_included_with_corrected_text": True,
    "ignored_item_excluded": True,
    "pending_item_excluded": True,
    "malformed_item_excluded": True,
    "validated_visual_decisions_artifact_preserved": True,
    "clean_study_item_count": 2,
    "excluded_item_count": 3,
    "manual_decision_write": False,
    "progress_write": False,
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
    "build_performed": False,
    "zip_created": False,
    "onedrive_staging_created": False,
    "share_link_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "fixture_created": fixture_created,
    "fixture_removed_after_check": True,
    "recommended_next": "v0.8.84-owner-local-clean-study-preview-visual-items-readonly-ui-plan-no-share-no-delivery",
}

evidence_dir.mkdir(parents=True, exist_ok=True)
out_json = evidence_dir / "V0.8.83-REVIEW-DOCUMENT-CLEAN-STUDY-REFRESH-RENDERED-FORM-POST-SMOKE-CHECK.json"
out_md = evidence_dir / "V0.8.83-REVIEW-DOCUMENT-CLEAN-STUDY-REFRESH-RENDERED-FORM-POST-SMOKE-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.83 Review Document Clean Study refresh rendered-form POST smoke\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
