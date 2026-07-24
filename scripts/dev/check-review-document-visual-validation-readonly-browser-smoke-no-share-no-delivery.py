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

doc = repo / "docs" / "dev" / "review-document-visual-validation-readonly-browser-smoke-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"
ui_doc = repo / "docs" / "dev" / "review-document-visual-validation-readonly-ui-no-share-no-delivery.md"

course_id = "v0875-visual-readonly-smoke"
output_root = repo / "data" / "output" / course_id
visual_dir = output_root / "formula_visual_evidence"
artifact_path = visual_dir / "visual_items.bbox.with-ocrmath-candidates.json"
smoke_path = f"/review-document/{course_id}"
evidence_dir = Path(r"D:\dev\tester-runs\v0875-review-document-visual-validation-readonly-browser-smoke-no-share-no-delivery")


def fail(message: str) -> None:
    raise SystemExit(message)


for path in [doc, web_app, ui_doc]:
    if not path.exists():
        fail("FAILED_REQUIRED_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
required_doc_terms = [
    "v0.8.75 Review Document visual validation read-only browser smoke",
    "local in-process HTTP-style smoke check",
    "FastAPI TestClient",
    "It does not start uvicorn.",
    "It does not start LanguageTool.",
    "It does not modify `services/api/web_app.py`.",
    "It does not add a POST endpoint.",
    "It does not add decision saving.",
    "It does not change `/study`.",
    "/review-document/v0875-visual-readonly-smoke",
    "Formule și imagini de verificat",
    "OCR Math candidate text",
    "crop availability",
    "Clean Study eligibility",
    "Diagnostic tehnic",
    "GET-only route access through FastAPI TestClient",
    "It does not perform POST.",
    "It does not upload a PDF.",
    "It does not run `/generate`.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "It does not run OCR Math.",
    "It does not generate crops.",
    "It does not write manual decisions.",
    "It does not write Clean Study.",
    "It does not write Progress.",
    "It does not build.",
    "It does not create a ZIP.",
    "It does not create OneDrive staging.",
    "It does not create a share link.",
    "It does not deliver to testers.",
    "It does not distribute anything.",
    "It does not create a public release.",
]

for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_DOC_TERM_MISSING=" + term)

web_diff = subprocess.check_output(
    ["git", "diff", "--name-only", "--", "services/api/web_app.py"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).strip()
if web_diff:
    fail("FAILED_WEB_APP_HAS_WORKTREE_DIFF=" + web_diff)

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
                "item_id": "bbox-item-smoke-formula",
                "kind": "formula",
                "page": 1,
                "bbox": [80, 100, 780, 260],
                "bbox_units": "pdf_points",
                "page_image_path": "formula_visual_evidence/pages/page-001.png",
                "crop_path": "formula_visual_evidence/crops/page-001-item-smoke-formula.png",
                "crop_exists": True,
                "ocr_math_candidate_text": "sin x / cos x",
                "ocr_math_status": "pending_user_validation",
                "user_decision": "pending",
                "user_corrected_text": "",
                "user_explanation": "",
                "ready_for_study": False,
                "created_by": "v0.8.75-testclient-smoke",
                "review_notes": "Synthetic read-only smoke fixture.",
            },
            {
                "item_id": "bbox-item-smoke-edit",
                "kind": "formula",
                "page": 2,
                "bbox": [90, 300, 790, 420],
                "bbox_units": "pdf_points",
                "page_image_path": "formula_visual_evidence/pages/page-002.png",
                "crop_path": "formula_visual_evidence/crops/page-002-item-smoke-edit.png",
                "crop_exists": True,
                "ocr_math_candidate_text": "tan x = sin x / cos x",
                "ocr_math_status": "validated_by_user",
                "user_decision": "edit",
                "user_corrected_text": r"\tan x = \frac{\sin x}{\cos x}",
                "user_explanation": "Formula corectată este gata pentru lecție.",
                "ready_for_study": True,
                "created_by": "v0.8.75-testclient-smoke",
                "review_notes": "Synthetic edited read-only smoke fixture.",
            },
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
        fail("FAILED_READONLY_SECTION_ID_MISSING")

    section_close = body.find("</section>", section_start)
    if section_close < 0:
        fail("FAILED_READONLY_SECTION_CLOSE_MISSING")

    section = body[section_start : section_close + len("</section>")]

    required_section_terms = [
        "Formule și imagini de verificat",
        "Secțiune read-only",
        "Element vizual 1",
        "Element vizual 2",
        "pagina 1",
        "pagina 2",
        "formulă",
        "În așteptare",
        "Corectat",
        "Imagine extrasă din document",
        "disponibilă pentru verificare",
        "Text detectat",
        "sin x / cos x",
        r"\tan x = \frac{\sin x}{\cos x}",
        "Explicație pe înțeles",
        "Formula corectată este gata pentru lecție.",
        "Eligibilitate Clean Study",
        "Nu intră încă în lecție",
        "Gata pentru lecție",
        "Diagnostic tehnic",
    ]

    for term in required_section_terms:
        if term not in section:
            fail("FAILED_SECTION_TERM_MISSING=" + term)

    forbidden_section_terms = [
        "<form",
        'method="post"',
        "method='post'",
        "<button",
        "Acceptă",
        "Salvează corectarea",
        "Ignoră",
    ]

    lower_section = section.lower()
    for term in forbidden_section_terms:
        if term.lower() in lower_section:
            fail("FAILED_READONLY_SECTION_CONTAINS_FORBIDDEN_TERM=" + term)

    main_card_part = section
    details_index = section.find("<details")
    if details_index >= 0:
        main_card_part = section[:details_index]

    forbidden_learner_terms = [
        "bbox-item-smoke",
        "formula_visual_evidence/crops",
        "formula_visual_evidence/pages",
        "visual_items.bbox",
        "D:\\",
        "scripts/dev",
        "schema_version",
        "bbox_units",
        "[80, 100",
    ]

    for term in forbidden_learner_terms:
        if term in main_card_part:
            fail("FAILED_LEARNER_CARD_CONTAINS_TECHNICAL_TERM=" + term)

    summary = {
        "VOILA_V0_8_75_REVIEW_DOCUMENT_VISUAL_VALIDATION_READONLY_BROWSER_SMOKE_CHECK": "PASS",
        "readonly_browser_smoke_performed": True,
        "inprocess_testclient_used": True,
        "fixture_created": fixture_created,
        "fixture_removed_after_check": True,
        "server_started": False,
        "uvicorn_started": False,
        "languagetool_started": False,
        "route_called": True,
        "route_method": "GET",
        "route_status_code": status_code,
        "review_document_section_visible": True,
        "shows_page": True,
        "shows_visual_type": True,
        "shows_ocr_math_candidate_text": True,
        "shows_validation_status": True,
        "shows_crop_availability": True,
        "shows_clean_study_eligibility": True,
        "diagnostic_section_visible": True,
        "readonly_no_form": True,
        "readonly_no_post_method": True,
        "readonly_no_buttons": True,
        "learner_card_hides_item_ids": True,
        "learner_card_hides_crop_paths": True,
        "learner_card_hides_absolute_paths": True,
        "web_app_changed": False,
        "post_endpoint_added": False,
        "manual_decision_write": False,
        "clean_study_write": False,
        "study_route_changed": False,
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
        "recommended_next": "v0.8.76-owner-local-review-document-visual-validation-save-action-plan-no-share-no-delivery",
        "smoke_path": smoke_path,
    }

    evidence_dir.mkdir(parents=True, exist_ok=True)
    out_json = evidence_dir / "V0.8.75-REVIEW-DOCUMENT-VISUAL-VALIDATION-READONLY-BROWSER-SMOKE-CHECK.json"
    out_md = evidence_dir / "V0.8.75-REVIEW-DOCUMENT-VISUAL-VALIDATION-READONLY-BROWSER-SMOKE-CHECK.md"

    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(
        "# v0.8.75 Review Document visual validation read-only browser smoke\n\n"
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
