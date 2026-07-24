from __future__ import annotations

import copy
import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

repo = Path(".").resolve()
sys.path.insert(0, str(repo))
sys.path.insert(0, str(repo / "services" / "api"))

doc = repo / "docs" / "dev" / "review-document-visual-validation-clean-study-refresh-implementation-no-share-no-delivery.md"
plan_doc = repo / "docs" / "dev" / "review-document-visual-validation-clean-study-refresh-plan-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"
patch_py = repo / "scripts" / "dev" / "apply-review-document-clean-study-refresh-action-v0881.py"

course_id = "v0881-clean-study-refresh-smoke"
output_root = repo / "data" / "output" / course_id
visual_dir = output_root / "formula_visual_evidence"
validated_path = visual_dir / "visual_items.bbox.validated.json"
candidate_path = visual_dir / "visual_items.bbox.with-ocrmath-candidates.json"
clean_path = visual_dir / "visual_items.clean-study.preview.json"
clean_summary_path = visual_dir / "visual_items.clean-study.preview-summary.json"
refresh_path = "/review-document/visual-validation/refresh-clean-study-preview"
evidence_dir = Path(r"D:\dev\tester-runs\v0881-review-document-visual-validation-clean-study-refresh-implementation-no-share-no-delivery")


def fail(message: str) -> None:
    raise SystemExit(message)


for path in [doc, plan_doc, web_app, patch_py]:
    if not path.exists():
        fail("FAILED_V0881_REQUIRED_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
plan_text = plan_doc.read_text(encoding="utf-8", errors="replace")
web_text = web_app.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.81 Review Document visual validation Clean Study refresh implementation",
    "POST /review-document/visual-validation/refresh-clean-study-preview",
    "The route rebuilds only the Clean Study visual preview artifact.",
    "It does not write the default `/study` output.",
    "It does not write Progress.",
    "formula_visual_evidence/visual_items.bbox.validated.json",
    "It does not read `visual_items.bbox.with-ocrmath-candidates.json` when rebuilding Clean Study.",
    "It does not trust client-submitted item data.",
    "It does not trust client-submitted crop paths.",
    "It does not trust client-submitted ready flags.",
    "formula_visual_evidence/visual_items.clean-study.preview.json",
    "formula_visual_evidence/visual_items.clean-study.preview-summary.json",
    "`ready_for_study=true`",
    "`user_decision=accept` or `user_decision=edit`",
    "`crop_exists=true`",
    "accepted items have non-empty `ocr_math_candidate_text`",
    "edited items have non-empty `user_corrected_text`",
    "`user_decision=ignore`",
    "`user_decision=pending`",
    "malformed items",
    "The route accepts only `course_id` from the form.",
    "The route uses safe course ID validation.",
    "The route does not join client-controlled paths.",
    "The route does not accept client-submitted item payloads.",
    "The route returns friendly escaped HTML responses.",
    "The route does not redirect to user-controlled URLs.",
    "The route does not expose stack traces.",
    "FastAPI TestClient",
    "accepted item is included",
    "edited item is included with corrected text",
    "ignored item is excluded",
    "pending item is excluded",
    "malformed item is excluded",
    "validated visual decisions artifact remains preserved",
    "`/study` is unchanged",
    "Progress is unchanged",
    "This milestone may modify `services/api/web_app.py` for the explicit refresh action.",
    "It does not add UI buttons.",
    "It does not submit rendered UI forms.",
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
    "v0.8.82-owner-local-review-document-clean-study-refresh-ui-control-no-share-no-delivery",
]

for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_V0881_DOC_TERM_MISSING=" + term)

for term in [
    "v0.8.80 Review Document visual validation Clean Study refresh plan",
    "Clean Study preview should be refreshed by a separate explicit owner-local action.",
    "POST /review-document/visual-validation/refresh-clean-study-preview",
]:
    if term not in plan_text:
        fail("FAILED_V0881_PLAN_TERM_MISSING=" + term)

required_web_terms = [
    "VOILA_V0_8_81_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_ACTION_START",
    '@app.post("/review-document/visual-validation/refresh-clean-study-preview")',
    "_voila_v0881_review_document_clean_study_refresh_action",
    "_voila_v0881_build_clean_study_payload",
    "_voila_v0881_parse_refresh_form",
    "visual_items.bbox.validated.json",
    "visual_items.clean-study.preview.json",
    "visual_items.clean-study.preview-summary.json",
    "CLEAN_STUDY_REFRESH=PASS",
]

for term in required_web_terms:
    if term not in web_text:
        fail("FAILED_V0881_WEB_TERM_MISSING=" + term)

block = web_text.split("VOILA_V0_8_81_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_ACTION_START", 1)[1].split("VOILA_V0_8_81_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_ACTION_END", 1)[0]

for forbidden in [
    "RedirectResponse",
    "traceback",
    "subprocess",
    "FileResponse",
    "request.query_params",
    "with-ocrmath-candidates.json",
]:
    if forbidden in block:
        fail("FAILED_V0881_FORBIDDEN_TERM_IN_WEB_BLOCK=" + forbidden)

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
                "created_by": "v0.8.81-testclient-refresh",
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
                "created_by": "v0.8.81-testclient-refresh",
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
                "created_by": "v0.8.81-testclient-refresh",
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
                "created_by": "v0.8.81-testclient-refresh",
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
                "created_by": "v0.8.81-testclient-refresh",
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
                        "created_by": "v0.8.81-testclient-refresh",
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
    client = TestClient(app_module.app)

    response = client.post(refresh_path, data={"course_id": course_id})
    if response.status_code != 200 or "CLEAN_STUDY_REFRESH=PASS" not in response.text:
        fail("FAILED_REFRESH_POST=" + str(response.status_code))

    if not clean_path.exists():
        fail("FAILED_CLEAN_STUDY_PREVIEW_MISSING")

    if not clean_summary_path.exists():
        fail("FAILED_CLEAN_STUDY_SUMMARY_MISSING")

    validated_after = json.loads(validated_path.read_text(encoding="utf-8"))
    if validated_after != original_validated_payload:
        fail("FAILED_VALIDATED_ARTIFACT_MODIFIED")

    clean_payload = json.loads(clean_path.read_text(encoding="utf-8"))
    clean_summary = json.loads(clean_summary_path.read_text(encoding="utf-8"))

    items = clean_payload.get("items")
    if not isinstance(items, list):
        fail("FAILED_CLEAN_ITEMS_NOT_LIST")

    ids = {item.get("source_visual_item_id") for item in items if isinstance(item, dict)}
    if ids != {"bbox-item-accept", "bbox-item-edit"}:
        fail("FAILED_CLEAN_ITEM_IDS_UNEXPECTED=" + json.dumps(sorted(ids), ensure_ascii=False))

    by_id = {item.get("source_visual_item_id"): item for item in items if isinstance(item, dict)}

    if by_id["bbox-item-accept"].get("answer") != "sin x / cos x":
        fail("FAILED_ACCEPT_ANSWER")
    if by_id["bbox-item-edit"].get("answer") != r"\tan x = \frac{\sin x}{\cos x}":
        fail("FAILED_EDIT_ANSWER")
    if by_id["bbox-item-edit"].get("explanation") != "Formula corectată intră în lecție.":
        fail("FAILED_EDIT_EXPLANATION")

    if "SHOULD_NOT_APPEAR" in json.dumps(clean_payload, ensure_ascii=False):
        fail("FAILED_CANDIDATE_ARTIFACT_WAS_READ")

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
        fail("FAILED_SUMMARY_EXCLUDED_COUNT")
    if clean_summary.get("accepted_count") != 1:
        fail("FAILED_SUMMARY_ACCEPTED_COUNT")
    if clean_summary.get("edited_count") != 1:
        fail("FAILED_SUMMARY_EDITED_COUNT")
    if clean_summary.get("progress_write_performed") is not False:
        fail("FAILED_SUMMARY_PROGRESS_WRITE_FLAG")
    if clean_summary.get("study_route_changed") is not False:
        fail("FAILED_SUMMARY_STUDY_ROUTE_FLAG")

    status_lines = subprocess.check_output(
        ["git", "status", "--porcelain", "-uall"],
        cwd=str(repo),
        text=True,
        encoding="utf-8",
        errors="replace",
    ).splitlines()

    allowed = {
        "services/api/web_app.py",
        "docs/dev/review-document-visual-validation-clean-study-refresh-implementation-no-share-no-delivery.md",
        "scripts/dev/apply-review-document-clean-study-refresh-action-v0881.py",
        "scripts/dev/check-review-document-visual-validation-clean-study-refresh-implementation-no-share-no-delivery.py",
        "scripts/dev/check-review-document-visual-validation-clean-study-refresh-implementation-no-share-no-delivery.ps1",
    }

    unexpected = []
    for line in status_lines:
        if not line.strip():
            continue
        rel = line[3:].replace("\\", "/")
        if rel not in allowed:
            unexpected.append(line)

    if unexpected:
        fail("FAILED_V0881_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

    summary = {
        "VOILA_V0_8_81_REVIEW_DOCUMENT_VISUAL_VALIDATION_CLEAN_STUDY_REFRESH_IMPLEMENTATION_CHECK": "PASS",
        "refresh_action_implemented": True,
        "web_app_changed": True,
        "route_added": True,
        "post_endpoint_added": True,
        "testclient_post_check_performed": True,
        "refresh_post_passed": True,
        "reads_validated_artifact_only": True,
        "candidate_artifact_not_used_for_refresh": True,
        "clean_study_preview_artifact_exists": True,
        "clean_study_preview_summary_exists": True,
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
        "recommended_next": "v0.8.82-owner-local-review-document-clean-study-refresh-ui-control-no-share-no-delivery",
    }

    evidence_dir.mkdir(parents=True, exist_ok=True)
    out_json = evidence_dir / "V0.8.81-REVIEW-DOCUMENT-VISUAL-VALIDATION-CLEAN-STUDY-REFRESH-IMPLEMENTATION-CHECK.json"
    out_md = evidence_dir / "V0.8.81-REVIEW-DOCUMENT-VISUAL-VALIDATION-CLEAN-STUDY-REFRESH-IMPLEMENTATION-CHECK.md"

    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(
        "# v0.8.81 Review Document visual validation Clean Study refresh implementation\n\n"
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
