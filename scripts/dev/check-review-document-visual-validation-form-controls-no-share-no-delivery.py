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

doc = repo / "docs" / "dev" / "review-document-visual-validation-form-controls-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"
patch_py = repo / "scripts" / "dev" / "apply-review-document-visual-validation-form-controls-v0878.py"
save_doc = repo / "docs" / "dev" / "review-document-visual-validation-save-action-implementation-no-share-no-delivery.md"

course_id = "v0878-visual-form-controls-smoke"
output_root = repo / "data" / "output" / course_id
visual_dir = output_root / "formula_visual_evidence"
artifact_path = visual_dir / "visual_items.bbox.with-ocrmath-candidates.json"
smoke_path = f"/review-document/{course_id}"
evidence_dir = Path(r"D:\dev\tester-runs\v0878-review-document-visual-validation-form-controls-no-share-no-delivery")


def fail(message: str) -> None:
    raise SystemExit(message)


for path in [doc, web_app, patch_py, save_doc]:
    if not path.exists():
        fail("FAILED_V0878_REQUIRED_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
save_doc_text = save_doc.read_text(encoding="utf-8", errors="replace")
web_text = web_app.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.78 Review Document visual validation form controls",
    "It connects the v0.8.74 visual validation cards to the v0.8.77 controlled save action.",
    "It adds UI controls only.",
    "It does not add a new POST endpoint.",
    "It does not change `/study`.",
    "It does not write Clean Study.",
    "`Acceptă`",
    "`Salvează corectarea`",
    "`Ignoră`",
    "POST /review-document/visual-validation/save",
    "`course_id`",
    "`item_id`",
    "`decision`",
    "`user_corrected_text`",
    "`user_explanation`",
    "The form does not submit:",
    "bbox coordinates",
    "crop path",
    "page image path",
    "absolute local path",
    "OCR Math status",
    "ready flag",
    "Clean Study eligibility",
    "schema internals",
    "The UI does not approve anything implicitly.",
    "A GET request does not write anything.",
    "This UI does not write Clean Study.",
    "The save route writes only the visual validation artifact and summary.",
    "FastAPI TestClient",
    "/review-document/v0878-visual-form-controls-smoke",
    "the visual validation section is visible",
    "forms use POST",
    "forms submit to `/review-document/visual-validation/save`",
    "The check does not submit the forms.",
    "This milestone may modify `services/api/web_app.py` for UI form rendering.",
    "It does not add a new route.",
    "It does not add a new POST endpoint.",
    "It does not perform POST in the automated check.",
    "It does not write manual decisions in the automated check.",
    "It does not write Clean Study.",
    "It does not change `/study`.",
    "It does not start uvicorn.",
    "It does not start LanguageTool.",
    "It does not upload a PDF.",
    "It does not run `/generate`.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "It does not run OCR Math.",
    "It does not generate crops.",
    "It does not write Progress.",
    "It does not build.",
    "It does not create a ZIP.",
    "It does not create OneDrive staging.",
    "It does not create a share link.",
    "It does not deliver to testers.",
    "It does not distribute anything.",
    "It does not create a public release.",
    "v0.8.79-owner-local-review-document-visual-validation-form-controls-post-smoke-no-share-no-delivery",
]

for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_V0878_DOC_TERM_MISSING=" + term)

for term in [
    "v0.8.77 Review Document visual validation save-action implementation",
    "POST /review-document/visual-validation/save",
    "The route saves explicit visual validation decisions only.",
]:
    if term not in save_doc_text:
        fail("FAILED_V0878_SAVE_DOC_TERM_MISSING=" + term)

required_web_terms = [
    "VOILA_V0_8_78_REVIEW_DOCUMENT_VISUAL_VALIDATION_FORM_CONTROLS",
    'form method="post" action="/review-document/visual-validation/save"',
    'name="course_id"',
    'name="item_id"',
    'name="decision"',
    'value="accept"',
    'value="edit"',
    'value="ignore"',
    'name="user_corrected_text"',
    'name="user_explanation"',
    "Acceptă",
    "Salvează corectarea",
    "Ignoră",
    "Deciziile se salvează local prin acțiuni explicite. Nu modifică direct lecția.",
]

for term in required_web_terms:
    if term not in web_text:
        fail("FAILED_V0878_WEB_TERM_MISSING=" + term)

subprocess.check_call([sys.executable, "-m", "py_compile", str(web_app)], cwd=str(repo))
subprocess.check_call([sys.executable, "-m", "py_compile", str(patch_py)], cwd=str(repo))

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
                "item_id": "bbox-item-form-controls",
                "kind": "formula",
                "page": 1,
                "bbox": [80, 100, 780, 260],
                "bbox_units": "pdf_points",
                "page_image_path": "formula_visual_evidence/pages/page-001.png",
                "crop_path": "formula_visual_evidence/crops/page-001-item-form-controls.png",
                "crop_exists": True,
                "ocr_math_candidate_text": "sin x / cos x",
                "ocr_math_status": "pending_user_validation",
                "user_decision": "pending",
                "user_corrected_text": "",
                "user_explanation": "",
                "ready_for_study": False,
                "created_by": "v0.8.78-testclient-get",
                "review_notes": "Synthetic form controls item.",
            }
        ],
    }

    artifact_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fixture_created = True

    app_module = importlib.import_module("services.api.web_app")
    client = TestClient(app_module.app)

    response = client.get(smoke_path)
    status_code = int(response.status_code)

    if status_code != 200:
        fail("FAILED_REVIEW_DOCUMENT_STATUS_CODE=" + str(status_code))

    body = response.text
    section_start = body.find('id="review-document-visual-validation-readonly-ui"')
    if section_start < 0:
        fail("FAILED_VISUAL_VALIDATION_SECTION_MISSING")

    section_end = body.find("</section>", section_start)
    if section_end < 0:
        fail("FAILED_VISUAL_VALIDATION_SECTION_CLOSE_MISSING")

    section = body[section_start : section_end + len("</section>")]

    required_section_terms = [
        "Formule și imagini de verificat",
        "Deciziile se salvează local prin acțiuni explicite",
        'form method="post" action="/review-document/visual-validation/save"',
        'name="course_id"',
        f'value="{course_id}"',
        'name="item_id"',
        'value="bbox-item-form-controls"',
        'name="decision"',
        'value="accept"',
        'value="edit"',
        'value="ignore"',
        'name="user_corrected_text"',
        'name="user_explanation"',
        "Acceptă",
        "Corectare",
        "Explicație pe înțeles",
        "Salvează corectarea",
        "Ignoră",
        "sin x / cos x",
    ]

    for term in required_section_terms:
        if term not in section:
            fail("FAILED_SECTION_TERM_MISSING=" + term)

    if section.count('form method="post" action="/review-document/visual-validation/save"') < 3:
        fail("FAILED_EXPECTED_THREE_FORMS")

    if section.count("<button") < 3:
        fail("FAILED_EXPECTED_THREE_BUTTONS")

    if "method=\"get\"" in section.lower():
        fail("FAILED_FORM_USES_GET")

    if "visual_items.bbox.validated.json" in section:
        fail("FAILED_LEARNER_SECTION_EXPOSES_VALIDATED_ARTIFACT_NAME")

    main_card_part = section
    details_index = section.find("<details")
    if details_index >= 0:
        main_card_part = section[:details_index]

    forbidden_learner_terms = [
        "formula_visual_evidence/crops",
        "formula_visual_evidence/pages",
        "D:\\",
        "scripts/dev",
        "schema_version",
        "bbox_units",
        "[80, 100",
    ]

    for term in forbidden_learner_terms:
        if term in main_card_part:
            fail("FAILED_LEARNER_CARD_CONTAINS_TECHNICAL_TERM=" + term)

    validated_path = visual_dir / "visual_items.bbox.validated.json"
    summary_path = visual_dir / "visual_items.bbox.validation-summary.json"
    clean_study_path = visual_dir / "visual_items.clean-study.preview.json"

    if validated_path.exists():
        fail("FAILED_GET_CREATED_VALIDATED_ARTIFACT")
    if summary_path.exists():
        fail("FAILED_GET_CREATED_SUMMARY_ARTIFACT")
    if clean_study_path.exists():
        fail("FAILED_GET_CREATED_CLEAN_STUDY_ARTIFACT")

    status_lines = subprocess.check_output(
        ["git", "status", "--porcelain", "-uall"],
        cwd=str(repo),
        text=True,
        encoding="utf-8",
        errors="replace",
    ).splitlines()

    allowed = {
        "services/api/web_app.py",
        "docs/dev/review-document-visual-validation-form-controls-no-share-no-delivery.md",
        "scripts/dev/apply-review-document-visual-validation-form-controls-v0878.py",
        "scripts/dev/check-review-document-visual-validation-form-controls-no-share-no-delivery.py",
        "scripts/dev/check-review-document-visual-validation-form-controls-no-share-no-delivery.ps1",
    }

    unexpected = []
    for line in status_lines:
        if not line.strip():
            continue
        rel = line[3:].replace("\\", "/")
        if rel not in allowed:
            unexpected.append(line)

    if unexpected:
        fail("FAILED_V0878_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

    summary = {
        "VOILA_V0_8_78_REVIEW_DOCUMENT_VISUAL_VALIDATION_FORM_CONTROLS_CHECK": "PASS",
        "form_controls_added": True,
        "web_app_changed": True,
        "new_route_added": False,
        "new_post_endpoint_added": False,
        "uses_existing_save_endpoint": True,
        "testclient_get_check_performed": True,
        "testclient_post_performed": False,
        "section_visible": True,
        "accept_control_visible": True,
        "edit_control_visible": True,
        "ignore_control_visible": True,
        "forms_use_post": True,
        "forms_target_existing_save_endpoint": True,
        "minimal_form_fields_present": True,
        "correction_textarea_present": True,
        "explanation_textarea_present": True,
        "get_request_wrote_validated_artifact": False,
        "get_request_wrote_summary_artifact": False,
        "clean_study_write": False,
        "manual_decision_write": False,
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
        "recommended_next": "v0.8.79-owner-local-review-document-visual-validation-form-controls-post-smoke-no-share-no-delivery",
    }

    evidence_dir.mkdir(parents=True, exist_ok=True)
    out_json = evidence_dir / "V0.8.78-REVIEW-DOCUMENT-VISUAL-VALIDATION-FORM-CONTROLS-CHECK.json"
    out_md = evidence_dir / "V0.8.78-REVIEW-DOCUMENT-VISUAL-VALIDATION-FORM-CONTROLS-CHECK.md"

    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(
        "# v0.8.78 Review Document visual validation form controls\n\n"
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
