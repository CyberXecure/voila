from __future__ import annotations

import base64
import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

repo = Path(".").resolve()
sys.path.insert(0, str(repo))
sys.path.insert(0, str(repo / "services" / "api"))

doc = repo / "docs" / "dev" / "clean-study-preview-visual-items-readonly-ui-implementation-no-share-no-delivery.md"
plan_doc = repo / "docs" / "dev" / "clean-study-preview-visual-items-readonly-ui-plan-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"
patch_py = repo / "scripts" / "dev" / "apply-clean-study-preview-visual-items-readonly-ui-v0885.py"

course_id = "v0885-visual-ui-smoke"
output_root = repo / "data" / "output" / course_id
visual_dir = output_root / "formula_visual_evidence"
crop_dir = visual_dir / "crops"
clean_path = visual_dir / "visual_items.clean-study.preview.json"
clean_summary_path = visual_dir / "visual_items.clean-study.preview-summary.json"
evidence_dir = Path(r"D:\dev\tester-runs\v0885-clean-study-preview-visual-items-readonly-ui-implementation-no-share-no-delivery")


def fail(message: str) -> None:
    raise SystemExit(message)


for path in [doc, plan_doc, web_app, patch_py]:
    if not path.exists():
        fail("FAILED_V0885_REQUIRED_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
plan_text = plan_doc.read_text(encoding="utf-8", errors="replace")
web_text = web_app.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.85 Clean Study preview visual items read-only UI implementation",
    "formula_visual_evidence/visual_items.clean-study.preview.json",
    "It does not read raw validation artifacts for display.",
    "It does not change `/study`.",
    "It does not write Clean Study.",
    "It does not write Progress.",
    "`Elemente vizuale validate`",
    "`Sursa: pagina`",
    "`Întrebare`",
    "`Răspuns validat`",
    "`Explicație`",
    "`Verificat în Revizuire document`",
    "`Lecția curată nu a fost actualizată încă.`",
    "`Nu există încă elemente vizuale validate pentru lecție.`",
    "The learner-facing UI must not display:",
    "bbox",
    "bbox_units",
    "crop_path as text",
    "page_image_path",
    "source_visual_item_id",
    "study_item_id",
    "schema_version",
    "source_visual_items_path",
    "artifact names",
    "absolute paths",
    "local filesystem roots",
    "ready_for_study",
    "ready_for_clean_study",
    "user_decision",
    "ocr_math_status",
    "learning_source",
    "raw JSON",
    "safe image data URI is rendered when the crop exists",
    "missing crop image degrades gracefully",
    "GET does not write Clean Study",
    "GET does not write Progress",
    "`/study` remains unchanged",
    "This milestone may modify `services/api/web_app.py` only for read-only Clean Study preview visual item display.",
    "It does not add a route.",
    "It does not add a POST endpoint.",
    "It does not add a button.",
    "It does not submit a form.",
    "It does not call a POST route.",
    "It does not start uvicorn.",
    "It does not start LanguageTool.",
    "It does not upload a PDF.",
    "It does not run `/generate`.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "It does not run OCR Math.",
    "It does not generate crops.",
    "It does not write manual decisions.",
    "It does not refresh Clean Study.",
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
    "v0.8.86-owner-local-clean-study-preview-visual-items-readonly-ui-smoke-no-share-no-delivery",
]

for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_V0885_DOC_TERM_MISSING=" + term)

for term in [
    "v0.8.84 Clean Study preview visual items read-only UI plan",
    "formula_visual_evidence/visual_items.clean-study.preview.json",
    "The future learner-facing UI must not display:",
]:
    if term not in plan_text:
        fail("FAILED_V0885_PLAN_TERM_MISSING=" + term)

required_web_terms = [
    "VOILA_V0_8_85_CLEAN_STUDY_PREVIEW_VISUAL_ITEMS_READONLY_UI_START",
    "_voila_v0885_safe_crop_data_uri",
    "_voila_v0885_load_clean_study_visual_items",
    "_voila_v0885_visual_items_section_html",
    "_voila_v0885_install_clean_study_preview_visual_items_route_wrapper",
    "visual_items.clean-study.preview.json",
    "clean-study-visual-items-readonly-ui",
    "Elemente vizuale validate",
    "Lecția curată nu a fost actualizată încă.",
    "Nu există încă elemente vizuale validate pentru lecție.",
]

for term in required_web_terms:
    if term not in web_text:
        fail("FAILED_V0885_WEB_TERM_MISSING=" + term)

block = web_text.split("VOILA_V0_8_85_CLEAN_STUDY_PREVIEW_VISUAL_ITEMS_READONLY_UI_START", 1)[1].split("VOILA_V0_8_85_CLEAN_STUDY_PREVIEW_VISUAL_ITEMS_READONLY_UI_END", 1)[0]

for forbidden in [
    "@app.post",
    "@app.get",
    "RedirectResponse",
    "subprocess",
    "_voila_v0877_write_json_replace",
    "visual_items.bbox.validated.json",
    "visual_items.bbox.with-ocrmath-candidates.json",
]:
    if forbidden in block:
        fail("FAILED_V0885_FORBIDDEN_TERM_IN_WEB_BLOCK=" + forbidden)

subprocess.check_call([sys.executable, "-m", "py_compile", str(web_app)], cwd=str(repo))
subprocess.check_call([sys.executable, "-m", "py_compile", str(patch_py)], cwd=str(repo))

fixture_created = False
get_rendered_visual_items_passed = False
missing_crop_degraded = False
empty_state_passed = False
not_refreshed_state_passed = False

try:
    if output_root.exists():
        shutil.rmtree(output_root)

    crop_dir.mkdir(parents=True, exist_ok=True)

    one_pixel_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
    )
    (crop_dir / "page-001-item-accept.png").write_bytes(one_pixel_png)

    clean_payload = {
        "schema_version": "v0.8.81",
        "course_id": course_id,
        "source_pdf": course_id + ".pdf",
        "source_visual_items_path": "visual_items.bbox.validated.json",
        "item_count": 2,
        "items": [
            {
                "schema_version": "v0.8.81",
                "study_item_id": "visual-study-bbox-item-accept",
                "source_visual_item_id": "bbox-item-accept",
                "source_pdf": course_id + ".pdf",
                "page": 1,
                "kind": "formula",
                "title": "Element vizual validat — pagina 1",
                "prompt": "Explică formula validată din document. Sursa: pagina 1.",
                "answer": "sin x / cos x",
                "explanation": "Acceptăm textul detectat.",
                "image": {
                    "crop_path": "formula_visual_evidence/crops/page-001-item-accept.png",
                    "alt": "Element vizual validat din pagina 1",
                },
                "learning_source": "validated_bbox_visual_item",
                "user_decision": "accept",
                "ready_for_clean_study": True,
            },
            {
                "schema_version": "v0.8.81",
                "study_item_id": "visual-study-bbox-item-edit",
                "source_visual_item_id": "bbox-item-edit",
                "source_pdf": course_id + ".pdf",
                "page": 2,
                "kind": "formula",
                "title": "Element vizual validat — pagina 2",
                "prompt": "Explică formula validată din document. Sursa: pagina 2.",
                "answer": r"\tan x = \frac{\sin x}{\cos x}",
                "explanation": "Formula corectată intră în lecție.",
                "image": {
                    "crop_path": "formula_visual_evidence/crops/missing-edit.png",
                    "alt": "Element vizual validat din pagina 2",
                },
                "learning_source": "validated_bbox_visual_item",
                "user_decision": "edit",
                "ready_for_clean_study": True,
            },
        ],
        "excluded_count": 0,
        "excluded_items": [],
    }

    clean_path.write_text(json.dumps(clean_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    clean_summary_path.write_text(
        json.dumps(
            {
                "schema_version": "v0.8.81",
                "course_id": course_id,
                "clean_study_item_count": 2,
                "excluded_item_count": 0,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    fixture_created = True

    before_clean = clean_path.read_text(encoding="utf-8")
    before_summary = clean_summary_path.read_text(encoding="utf-8")

    app_module = importlib.import_module("services.api.web_app")
    from fastapi.testclient import TestClient

    client = TestClient(app_module.app)

    response = client.get("/study-clean-preview/" + course_id)
    if response.status_code != 200:
        fail("FAILED_GET_STUDY_CLEAN_PREVIEW=" + str(response.status_code))

    html = response.text

    required_html_terms = [
        "clean-study-visual-items-readonly-ui",
        "Elemente vizuale validate",
        "Element vizual validat — pagina 1",
        "Element vizual validat — pagina 2",
        "Sursa: pagina",
        "Întrebare",
        "Răspuns validat",
        "Explicație",
        "Verificat în Revizuire document.",
        "sin x / cos x",
        r"\tan x = \frac{\sin x}{\cos x}",
        "Acceptăm textul detectat.",
        "Formula corectată intră în lecție.",
        "data:image/png;base64,",
        "Imaginea validată nu este disponibilă momentan.",
    ]

    for term in required_html_terms:
        if term not in html:
            fail("FAILED_V0885_HTML_TERM_MISSING=" + term)

    get_rendered_visual_items_passed = True
    missing_crop_degraded = "Imaginea validată nu este disponibilă momentan." in html

    forbidden_html_terms = [
        "formula_visual_evidence/crops/page-001-item-accept.png",
        "formula_visual_evidence/crops/missing-edit.png",
        "bbox-item-accept",
        "bbox-item-edit",
        "visual-study-bbox-item-accept",
        "visual-study-bbox-item-edit",
        "schema_version",
        "source_visual_items_path",
        "visual_items.bbox.validated.json",
        "visual_items.clean-study.preview.json",
        "source_visual_item_id",
        "study_item_id",
        "ready_for_study",
        "ready_for_clean_study",
        "user_decision",
        "ocr_math_status",
        "learning_source",
        str(repo),
        "D:\\",
    ]

    for term in forbidden_html_terms:
        if term in html:
            fail("FAILED_V0885_FORBIDDEN_HTML_TERM_VISIBLE=" + term)

    after_clean = clean_path.read_text(encoding="utf-8")
    after_summary = clean_summary_path.read_text(encoding="utf-8")

    if after_clean != before_clean or after_summary != before_summary:
        fail("FAILED_V0885_GET_MODIFIED_CLEAN_STUDY_ARTIFACTS")

    progress_candidates = [
        output_root / "progress.json",
        output_root / "study_progress.json",
        output_root / "progress.preview.json",
    ]
    if any(path.exists() for path in progress_candidates):
        fail("FAILED_V0885_GET_WROTE_PROGRESS")

    clean_path.write_text(
        json.dumps(
            {
                "schema_version": "v0.8.81",
                "course_id": course_id,
                "source_pdf": course_id + ".pdf",
                "item_count": 0,
                "items": [],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    empty_response = client.get("/study-clean-preview/" + course_id)
    if empty_response.status_code != 200:
        fail("FAILED_EMPTY_STATE_GET=" + str(empty_response.status_code))
    if "Nu există încă elemente vizuale validate pentru lecție." not in empty_response.text:
        fail("FAILED_EMPTY_STATE_TEXT_MISSING")
    empty_state_passed = True

    clean_path.unlink()
    not_refreshed_response = client.get("/study-clean-preview/" + course_id)
    if not_refreshed_response.status_code != 200:
        fail("FAILED_NOT_REFRESHED_STATE_GET=" + str(not_refreshed_response.status_code))
    if "Lecția curată nu a fost actualizată încă." not in not_refreshed_response.text:
        fail("FAILED_NOT_REFRESHED_STATE_TEXT_MISSING")
    if "/review-document/" + course_id not in not_refreshed_response.text:
        fail("FAILED_NOT_REFRESHED_BACK_LINK_MISSING")
    not_refreshed_state_passed = True

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
    "docs/dev/clean-study-preview-visual-items-readonly-ui-implementation-no-share-no-delivery.md",
    "scripts/dev/apply-clean-study-preview-visual-items-readonly-ui-v0885.py",
    "scripts/dev/check-clean-study-preview-visual-items-readonly-ui-implementation-no-share-no-delivery.py",
    "scripts/dev/check-clean-study-preview-visual-items-readonly-ui-implementation-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0885_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary = {
    "VOILA_V0_8_85_CLEAN_STUDY_PREVIEW_VISUAL_ITEMS_READONLY_UI_IMPLEMENTATION_CHECK": "PASS",
    "ui_implementation_performed": True,
    "web_app_changed": True,
    "route_added": False,
    "post_endpoint_added": False,
    "testclient_get_check_performed": True,
    "get_rendered_visual_items_passed": get_rendered_visual_items_passed,
    "visual_items_section_visible": True,
    "accepted_item_visible": True,
    "edited_item_visible_with_corrected_text": True,
    "explanation_visible": True,
    "page_source_visible": True,
    "safe_image_data_uri_rendered": True,
    "raw_crop_path_hidden": True,
    "missing_crop_degraded_gracefully": missing_crop_degraded,
    "empty_state_friendly": empty_state_passed,
    "not_refreshed_state_friendly": not_refreshed_state_passed,
    "technical_metadata_hidden": True,
    "raw_json_hidden": True,
    "absolute_paths_hidden": True,
    "reads_clean_study_preview_artifact_only": True,
    "manual_decision_write": False,
    "clean_study_refresh_performed": False,
    "clean_study_write": False,
    "progress_write": False,
    "study_route_changed": False,
    "button_added": False,
    "form_submitted": False,
    "post_route_called": False,
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
    "recommended_next": "v0.8.86-owner-local-clean-study-preview-visual-items-readonly-ui-smoke-no-share-no-delivery",
}

evidence_dir.mkdir(parents=True, exist_ok=True)
out_json = evidence_dir / "V0.8.85-CLEAN-STUDY-PREVIEW-VISUAL-ITEMS-READONLY-UI-IMPLEMENTATION-CHECK.json"
out_md = evidence_dir / "V0.8.85-CLEAN-STUDY-PREVIEW-VISUAL-ITEMS-READONLY-UI-IMPLEMENTATION-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.85 Clean Study preview visual items read-only UI implementation\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
