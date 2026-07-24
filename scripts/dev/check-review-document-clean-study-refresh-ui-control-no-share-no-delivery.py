from __future__ import annotations

import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

repo = Path(".").resolve()
sys.path.insert(0, str(repo))
sys.path.insert(0, str(repo / "services" / "api"))

doc = repo / "docs" / "dev" / "review-document-clean-study-refresh-ui-control-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"
patch_py = repo / "scripts" / "dev" / "apply-review-document-clean-study-refresh-ui-control-v0882.py"

course_id = "v0882-clean-study-refresh-ui-control-smoke"
output_root = repo / "data" / "output" / course_id
visual_dir = output_root / "formula_visual_evidence"
validated_path = visual_dir / "visual_items.bbox.validated.json"
clean_path = visual_dir / "visual_items.clean-study.preview.json"
clean_summary_path = visual_dir / "visual_items.clean-study.preview-summary.json"
refresh_path = "/review-document/visual-validation/refresh-clean-study-preview"
evidence_dir = Path(r"D:\dev\tester-runs\v0882-review-document-clean-study-refresh-ui-control-no-share-no-delivery")


def fail(message: str) -> None:
    raise SystemExit(message)


for path in [doc, web_app, patch_py]:
    if not path.exists():
        fail("FAILED_V0882_REQUIRED_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
web_text = web_app.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.82 Review Document Clean Study refresh UI control",
    "`Actualizează lecția curată`",
    "POST /review-document/visual-validation/refresh-clean-study-preview",
    "This milestone may modify `services/api/web_app.py` only to render the UI control.",
    "It does not add a new route.",
    "It does not add a new POST endpoint.",
    "It does not change the v0.8.81 refresh action.",
    "It does not change `/study`.",
    "It does not write Progress.",
    "It does not run refresh during GET.",
    "It does not write Clean Study during GET.",
    "`Deschide lecția curată`",
    "`method=\"post\"`",
    "The form sends only:",
    "`course_id`",
    "The form does not submit item data.",
    "The form does not submit crop paths.",
    "The form does not submit ready flags.",
    "The form does not submit OCR Math status.",
    "The form does not submit bbox data.",
    "FastAPI TestClient with GET only",
    "no Clean Study artifact is written by GET",
    "no Progress write occurs",
    "`/study` is unchanged",
    "This milestone does not submit the refresh form.",
    "It does not call the refresh POST route.",
    "It does not start uvicorn.",
    "It does not start LanguageTool.",
    "It does not upload a PDF.",
    "It does not run `/generate`.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "It does not run OCR Math.",
    "It does not generate crops.",
    "It does not write manual decisions.",
    "It does not write Clean Study.",
    "It does not write Progress.",
    "It does not change `/study`.",
    "It does not build.",
    "It does not create a ZIP.",
    "It does not create OneDrive staging.",
    "It does not create a share link.",
    "It does not deliver to testers.",
    "It does not distribute anything.",
    "It does not create a public release.",
    "v0.8.83-owner-local-review-document-clean-study-refresh-rendered-form-post-smoke-no-share-no-delivery",
]

for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_V0882_DOC_TERM_MISSING=" + term)

required_web_terms = [
    "VOILA_V0_8_82_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_UI_CONTROL_START",
    "_voila_v0882_clean_study_refresh_control_html",
    "_voila_v0882_review_document_clean_study_refresh_ui_control_middleware",
    "review-document-clean-study-refresh-control",
    "data-voila-clean-study-refresh-form",
    "Actualizează lecția curată",
    "Deschide lecția curată",
    "/review-document/visual-validation/refresh-clean-study-preview",
    "Nu modifică documentul original",
    "nu scrie Progress",
    "nu publică și nu partajează nimic",
]

for term in required_web_terms:
    if term not in web_text:
        fail("FAILED_V0882_WEB_TERM_MISSING=" + term)

if web_text.count('@app.post("/review-document/visual-validation/refresh-clean-study-preview")') != 1:
    fail("FAILED_V0882_REFRESH_POST_ROUTE_COUNT_UNEXPECTED")

block = web_text.split("VOILA_V0_8_82_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_UI_CONTROL_START", 1)[1].split("VOILA_V0_8_82_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_UI_CONTROL_END", 1)[0]

for forbidden in [
    "@app.post",
    "@app.get",
    "RedirectResponse",
    "subprocess",
    "request.body",
    "request.form",
    "visual_items.clean-study.preview.json",
    "visual_items.clean-study.preview-summary.json",
    "_voila_v0877_write_json_replace",
]:
    if forbidden in block:
        fail("FAILED_V0882_FORBIDDEN_TERM_IN_WEB_BLOCK=" + forbidden)

subprocess.check_call([sys.executable, "-m", "py_compile", str(web_app)], cwd=str(repo))
subprocess.check_call([sys.executable, "-m", "py_compile", str(patch_py)], cwd=str(repo))

fixture_created = False
get_rendered_control_passed = False
clean_study_write = False
progress_write = False

try:
    if output_root.exists():
        shutil.rmtree(output_root)

    visual_dir.mkdir(parents=True, exist_ok=True)
    validated_path.write_text(
        json.dumps(
            {
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
                        "created_by": "v0.8.82-testclient-get-only",
                        "review_notes": "Accepted item.",
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

    required_html_terms = [
        "review-document-clean-study-refresh-control",
        "data-voila-clean-study-refresh-form",
        "Actualizează lecția curată",
        'method="post"',
        'action="/review-document/visual-validation/refresh-clean-study-preview"',
        'name="course_id"',
        'value="' + course_id + '"',
        "Deschide lecția curată",
        "/study-clean-preview/" + course_id,
        "Elementele acceptate și corectate pot intra în lecție",
        "Elementele ignorate sau încă nevalidate rămân în afara lecției",
        "Actualizarea este locală",
        "Nu modifică documentul original",
        "nu scrie Progress",
        "nu publică și nu partajează nimic",
    ]

    for term in required_html_terms:
        if term not in html:
            fail("FAILED_V0882_HTML_TERM_MISSING=" + term)

    forbidden_html_terms = [
        "formula_visual_evidence/crops/page-001-item-accept.png",
        "bbox-item-accept</",
        "ready_for_study",
        "ocr_math_status",
        "bbox_units",
        str(repo),
    ]

    for term in forbidden_html_terms:
        if term in html:
            fail("FAILED_V0882_FORBIDDEN_HTML_TERM_VISIBLE=" + term)

    control_start = html.find("review-document-clean-study-refresh-control")
    if control_start < 0:
        fail("FAILED_CONTROL_NOT_FOUND")

    control_html = html[control_start: control_start + 2500]

    forbidden_form_fields = [
        'name="item_id"',
        'name="crop_path"',
        'name="bbox"',
        'name="ready_for_study"',
        'name="ocr_math_status"',
        'name="user_decision"',
        'name="user_corrected_text"',
        'name="user_explanation"',
    ]

    for term in forbidden_form_fields:
        if term in control_html:
            fail("FAILED_V0882_REFRESH_FORM_SUBMITS_FORBIDDEN_FIELD=" + term)

    get_rendered_control_passed = True

    clean_study_write = clean_path.exists() or clean_summary_path.exists()
    if clean_study_write:
        fail("FAILED_V0882_GET_WROTE_CLEAN_STUDY")

    progress_candidates = [
        output_root / "progress.json",
        output_root / "study_progress.json",
        output_root / "progress.preview.json",
    ]
    progress_write = any(path.exists() for path in progress_candidates)
    if progress_write:
        fail("FAILED_V0882_GET_WROTE_PROGRESS")
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
    "services/api/web_app.py",
    "docs/dev/review-document-clean-study-refresh-ui-control-no-share-no-delivery.md",
    "scripts/dev/apply-review-document-clean-study-refresh-ui-control-v0882.py",
    "scripts/dev/check-review-document-clean-study-refresh-ui-control-no-share-no-delivery.py",
    "scripts/dev/check-review-document-clean-study-refresh-ui-control-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0882_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary = {
    "VOILA_V0_8_82_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_UI_CONTROL_CHECK": "PASS",
    "ui_control_added": True,
    "web_app_changed": True,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "uses_existing_v0881_refresh_post_route": True,
    "testclient_get_check_performed": True,
    "get_rendered_control_passed": get_rendered_control_passed,
    "refresh_button_visible": True,
    "refresh_form_method_post": True,
    "refresh_form_action_existing_endpoint": True,
    "refresh_form_submits_only_course_id": True,
    "item_payload_submitted": False,
    "crop_path_submitted": False,
    "bbox_submitted": False,
    "ready_flag_submitted": False,
    "ocr_math_status_submitted": False,
    "rendered_form_post_submitted": False,
    "refresh_post_called": False,
    "manual_decision_write": False,
    "clean_study_write": False,
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
    "recommended_next": "v0.8.83-owner-local-review-document-clean-study-refresh-rendered-form-post-smoke-no-share-no-delivery",
}

evidence_dir.mkdir(parents=True, exist_ok=True)
out_json = evidence_dir / "V0.8.82-REVIEW-DOCUMENT-CLEAN-STUDY-REFRESH-UI-CONTROL-CHECK.json"
out_md = evidence_dir / "V0.8.82-REVIEW-DOCUMENT-CLEAN-STUDY-REFRESH-UI-CONTROL-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.82 Review Document Clean Study refresh UI control\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
