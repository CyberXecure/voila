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

doc = repo / "docs" / "dev" / "review-document-visual-validation-save-action-implementation-no-share-no-delivery.md"
plan_doc = repo / "docs" / "dev" / "review-document-visual-validation-save-action-plan-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"
patch_py = repo / "scripts" / "dev" / "apply-review-document-visual-validation-save-action-v0877.py"

course_id = "v0877-visual-save-action-smoke"
output_root = repo / "data" / "output" / course_id
visual_dir = output_root / "formula_visual_evidence"
candidate_path = visual_dir / "visual_items.bbox.with-ocrmath-candidates.json"
validated_path = visual_dir / "visual_items.bbox.validated.json"
summary_path = visual_dir / "visual_items.bbox.validation-summary.json"
clean_study_path = visual_dir / "visual_items.clean-study.preview.json"
save_path = "/review-document/visual-validation/save"
evidence_dir = Path(r"D:\dev\tester-runs\v0877-review-document-visual-validation-save-action-implementation-no-share-no-delivery")


def fail(message: str) -> None:
    raise SystemExit(message)


for path in [doc, plan_doc, web_app, patch_py]:
    if not path.exists():
        fail("FAILED_V0877_REQUIRED_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
plan_text = plan_doc.read_text(encoding="utf-8", errors="replace")
web_text = web_app.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.77 Review Document visual validation save-action implementation",
    "POST /review-document/visual-validation/save",
    "The route saves explicit visual validation decisions only.",
    "It does not write Clean Study.",
    "It does not change `/study`.",
    "`accept`",
    "`edit`",
    "`ignore`",
    "No implicit approval is allowed.",
    "`course_id`",
    "`item_id`",
    "`decision`",
    "`user_corrected_text`",
    "`user_explanation`",
    "The route does not trust client-submitted crop paths, bbox coordinates, page numbers, OCR Math status, ready flags, or Clean Study eligibility.",
    "formula_visual_evidence/visual_items.bbox.validated.json",
    "formula_visual_evidence/visual_items.bbox.with-ocrmath-candidates.json",
    "formula_visual_evidence/visual_items.bbox.validation-summary.json",
    "`crop_exists=true`",
    "`ocr_math_candidate_text` is non-empty",
    "trimmed `user_corrected_text`",
    "`user_decision=accept`",
    "`user_decision=edit`",
    "`user_decision=ignore`",
    "`ocr_math_status=validated_by_user`",
    "`ocr_math_status=not_applicable`",
    "`ready_for_study=true`",
    "`ready_for_study=false`",
    "This save action does not write Clean Study.",
    "`course_id` and `item_id` use a safe ASCII allowlist.",
    "`item_id` is used only as an identifier, never as a path.",
    "The route does not join client-controlled file paths.",
    "The route does not redirect to user-controlled URLs.",
    "Reflected values are escaped.",
    "Stack traces are not exposed.",
    "FastAPI TestClient",
    "invalid edit without corrected text",
    "Clean Study is not written",
    "This milestone may modify `services/api/web_app.py` for the controlled POST save action.",
    "It does not add UI buttons.",
    "It does not start uvicorn.",
    "It does not start LanguageTool.",
    "It does not upload a PDF.",
    "It does not run `/generate`.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "It does not run OCR Math.",
    "It does not generate crops.",
    "It does not write Clean Study.",
    "It does not write Progress.",
    "It does not build.",
    "It does not create a ZIP.",
    "It does not create OneDrive staging.",
    "It does not create a share link.",
    "It does not deliver to testers.",
    "It does not distribute anything.",
    "It does not create a public release.",
    "v0.8.78-owner-local-review-document-visual-validation-form-controls-no-share-no-delivery",
]

for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_V0877_DOC_TERM_MISSING=" + term)

for term in [
    "v0.8.76 Review Document visual validation save-action plan",
    "POST /review-document/visual-validation/save",
    "No implicit approval is allowed.",
    "The route must not join client-controlled paths.",
    "The route must not expose stack traces.",
]:
    if term not in plan_text:
        fail("FAILED_V0877_PLAN_TERM_MISSING=" + term)

required_web_terms = [
    "VOILA_V0_8_77_REVIEW_DOCUMENT_VISUAL_VALIDATION_SAVE_ACTION_START",
    '@app.post("/review-document/visual-validation/save")',
    "_voila_v0877_review_document_visual_validation_save_action",
    "_voila_v0877_safe_identifier",
    "_voila_v0877_safe_output_dir",
    "_voila_v0877_parse_save_form",
    "_voila_v0877_write_json_replace",
    "visual_items.bbox.validated.json",
    "visual_items.bbox.validation-summary.json",
    "visual_items.bbox.with-ocrmath-candidates.json",
    "DECIZIE_SALVATA=PASS",
    "validated_by_user",
    "not_applicable",
    "ready_for_study",
]

for term in required_web_terms:
    if term not in web_text:
        fail("FAILED_V0877_WEB_TERM_MISSING=" + term)

block = web_text.split("VOILA_V0_8_77_REVIEW_DOCUMENT_VISUAL_VALIDATION_SAVE_ACTION_START", 1)[1].split("VOILA_V0_8_77_REVIEW_DOCUMENT_VISUAL_VALIDATION_SAVE_ACTION_END", 1)[0]

for forbidden in [
    "RedirectResponse",
    "traceback",
    "subprocess",
    "FileResponse",
    "request.query_params",
]:
    if forbidden in block:
        fail("FAILED_V0877_FORBIDDEN_TERM_IN_WEB_BLOCK=" + forbidden)

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
                "created_by": "v0.8.77-testclient-post",
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
                "created_by": "v0.8.77-testclient-post",
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
                "created_by": "v0.8.77-testclient-post",
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
                "created_by": "v0.8.77-testclient-post",
                "review_notes": "Synthetic pending item.",
            },
        ],
    }

    candidate_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fixture_created = True

    app_module = importlib.import_module("services.api.web_app")
    client = TestClient(app_module.app)

    accept_response = client.post(
        save_path,
        data={
            "course_id": course_id,
            "item_id": "bbox-item-accept",
            "decision": "accept",
            "user_corrected_text": "",
            "user_explanation": "Acceptăm textul detectat.",
        },
    )
    if accept_response.status_code != 200 or "DECIZIE_SALVATA=PASS" not in accept_response.text:
        fail("FAILED_ACCEPT_POST=" + str(accept_response.status_code))

    edit_response = client.post(
        save_path,
        data={
            "course_id": course_id,
            "item_id": "bbox-item-edit",
            "decision": "edit",
            "user_corrected_text": r"\tan x = \frac{\sin x}{\cos x}",
            "user_explanation": "Formula corectată intră în lecție.",
        },
    )
    if edit_response.status_code != 200 or "DECIZIE_SALVATA=PASS" not in edit_response.text:
        fail("FAILED_EDIT_POST=" + str(edit_response.status_code))

    ignore_response = client.post(
        save_path,
        data={
            "course_id": course_id,
            "item_id": "bbox-item-ignore",
            "decision": "ignore",
            "user_corrected_text": "",
            "user_explanation": "Nu este relevant pentru lecție.",
        },
    )
    if ignore_response.status_code != 200 or "DECIZIE_SALVATA=PASS" not in ignore_response.text:
        fail("FAILED_IGNORE_POST=" + str(ignore_response.status_code))

    invalid_edit_response = client.post(
        save_path,
        data={
            "course_id": course_id,
            "item_id": "bbox-item-pending",
            "decision": "edit",
            "user_corrected_text": "",
            "user_explanation": "",
        },
    )
    if invalid_edit_response.status_code != 400:
        fail("FAILED_INVALID_EDIT_NOT_REJECTED=" + str(invalid_edit_response.status_code))

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
        fail("FAILED_ACCEPT_STATE")
    if accept_item.get("ocr_math_status") != "validated_by_user":
        fail("FAILED_ACCEPT_STATUS")

    if edit_item.get("user_decision") != "edit" or edit_item.get("ready_for_study") is not True:
        fail("FAILED_EDIT_STATE")
    if edit_item.get("user_corrected_text") != r"\tan x = \frac{\sin x}{\cos x}":
        fail("FAILED_EDIT_CORRECTED_TEXT")
    if edit_item.get("ocr_math_status") != "validated_by_user":
        fail("FAILED_EDIT_STATUS")

    if ignore_item.get("user_decision") != "ignore" or ignore_item.get("ready_for_study") is not False:
        fail("FAILED_IGNORE_STATE")
    if ignore_item.get("ocr_math_status") != "not_applicable":
        fail("FAILED_IGNORE_STATUS")

    if pending_item.get("user_decision") != "pending" or pending_item.get("ready_for_study") is not False:
        fail("FAILED_PENDING_CHANGED_BY_INVALID_EDIT")

    summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary_payload.get("clean_study_write_performed") is not False:
        fail("FAILED_SUMMARY_CLEAN_STUDY_WRITE_FLAG")
    if summary_payload.get("ignored_count") != 1:
        fail("FAILED_SUMMARY_IGNORED_COUNT")
    if summary_payload.get("pending_count") != 1:
        fail("FAILED_SUMMARY_PENDING_COUNT")

    status_lines = subprocess.check_output(
        ["git", "status", "--porcelain", "-uall"],
        cwd=str(repo),
        text=True,
        encoding="utf-8",
        errors="replace",
    ).splitlines()

    allowed = {
        "services/api/web_app.py",
        "docs/dev/review-document-visual-validation-save-action-implementation-no-share-no-delivery.md",
        "scripts/dev/apply-review-document-visual-validation-save-action-v0877.py",
        "scripts/dev/check-review-document-visual-validation-save-action-implementation-no-share-no-delivery.py",
        "scripts/dev/check-review-document-visual-validation-save-action-implementation-no-share-no-delivery.ps1",
    }

    unexpected = []
    for line in status_lines:
        if not line.strip():
            continue
        rel = line[3:].replace("\\", "/")
        if rel not in allowed:
            unexpected.append(line)

    if unexpected:
        fail("FAILED_V0877_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

    summary = {
        "VOILA_V0_8_77_REVIEW_DOCUMENT_VISUAL_VALIDATION_SAVE_ACTION_IMPLEMENTATION_CHECK": "PASS",
        "save_action_implemented": True,
        "web_app_changed": True,
        "route_added": True,
        "post_endpoint_added": True,
        "testclient_post_check_performed": True,
        "accept_post_passed": True,
        "edit_post_passed": True,
        "ignore_post_passed": True,
        "invalid_edit_without_text_rejected": True,
        "validated_artifact_exists": True,
        "validation_summary_exists": True,
        "accept_ready_for_study": True,
        "edit_ready_for_study_with_corrected_text": True,
        "ignore_blocked_from_study": True,
        "pending_remains_pending": True,
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
        "recommended_next": "v0.8.78-owner-local-review-document-visual-validation-form-controls-no-share-no-delivery",
    }

    evidence_dir.mkdir(parents=True, exist_ok=True)
    out_json = evidence_dir / "V0.8.77-REVIEW-DOCUMENT-VISUAL-VALIDATION-SAVE-ACTION-IMPLEMENTATION-CHECK.json"
    out_md = evidence_dir / "V0.8.77-REVIEW-DOCUMENT-VISUAL-VALIDATION-SAVE-ACTION-IMPLEMENTATION-CHECK.md"

    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(
        "# v0.8.77 Review Document visual validation save-action implementation\n\n"
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
