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

doc = repo / "docs" / "dev" / "clean-study-preview-visual-items-readonly-ui-smoke-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"

course_id = "v0886-visual-ui"
output_root = repo / "data" / "output" / course_id
visual_dir = output_root / "formula_visual_evidence"
crop_dir = visual_dir / "crops"
clean_path = visual_dir / "visual_items.clean-study.preview.json"
clean_summary_path = visual_dir / "visual_items.clean-study.preview-summary.json"

evidence_dir = Path(r"D:\dev\tester-runs\v0886-clean-study-preview-visual-items-readonly-ui-smoke-no-share-no-delivery")


def fail(message: str) -> None:
    raise SystemExit(message)


for path in [doc, web_app]:
    if not path.exists():
        fail("FAILED_V0886_REQUIRED_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
web_text = web_app.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.86 Clean Study preview visual items read-only UI smoke",
    "This is a smoke-only milestone.",
    "It does not modify `services/api/web_app.py`.",
    "It does not add a route.",
    "It does not add a POST endpoint.",
    "formula_visual_evidence/visual_items.clean-study.preview.json",
    "render `GET /study-clean-preview/<course_id>`",
    "`Elemente vizuale validate`",
    "`Sursa: pagina`",
    "`Întrebare`",
    "`Răspuns validat`",
    "`Explicație`",
    "`Verificat în Revizuire document`",
    "raw crop path text",
    "`bbox`",
    "`crop_path`",
    "`source_visual_item_id`",
    "`study_item_id`",
    "`schema_version`",
    "absolute paths",
    "`ready_for_clean_study`",
    "`user_decision`",
    "`ocr_math_status`",
    "`learning_source`",
    "raw JSON",
    "It does not run `/generate`.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "It does not run OCR Math.",
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
    "v0.8.87-owner-local-review-to-clean-study-visual-flow-final-audit-no-share-no-delivery",
]

for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_V0886_DOC_TERM_MISSING=" + term)

required_web_terms = [
    "VOILA_V0_8_85_CLEAN_STUDY_PREVIEW_VISUAL_ITEMS_READONLY_UI_START",
    "_voila_v0885_visual_items_section_html",
    "_voila_v0885_install_clean_study_preview_visual_items_route_wrapper",
    "_VOILA_V0_8_85_CLEAN_STUDY_PREVIEW_VISUAL_ITEMS_ROUTE_WRAPPED",
    "visual_items.clean-study.preview.json",
    "Elemente vizuale validate",
]

for term in required_web_terms:
    if term not in web_text:
        fail("FAILED_V0886_WEB_TERM_MISSING=" + term)

web_diff = subprocess.check_output(
    ["git", "diff", "--name-only", "--", "services/api/web_app.py"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).strip()

if web_diff:
    fail("FAILED_V0886_WEB_APP_HAS_WORKTREE_DIFF=" + web_diff)

subprocess.check_call([sys.executable, "-m", "py_compile", str(web_app)], cwd=str(repo))

fixture_created = False
rendered_visual_ui_passed = False
safe_image_rendered = False
missing_crop_fallback_visible = False

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
                "study_item_id": "visual-study-accept",
                "source_visual_item_id": "visual-accept",
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
                "study_item_id": "visual-study-edit",
                "source_visual_item_id": "visual-edit",
                "source_pdf": course_id + ".pdf",
                "page": 2,
                "kind": "formula",
                "title": "Element vizual validat — pagina 2",
                "prompt": "Explică formula corectată din document. Sursa: pagina 2.",
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

    clean_summary = {
        "schema_version": "v0.8.81",
        "course_id": course_id,
        "clean_study_item_count": 2,
        "excluded_item_count": 0,
    }

    clean_path.write_text(json.dumps(clean_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    clean_summary_path.write_text(json.dumps(clean_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fixture_created = True

    before_clean = clean_path.read_text(encoding="utf-8")
    before_summary = clean_summary_path.read_text(encoding="utf-8")

    app_module = importlib.import_module("services.api.web_app")
    from fastapi.testclient import TestClient

    client = TestClient(app_module.app)

    response = client.get("/study-clean-preview/" + course_id)
    if response.status_code != 200:
        fail("FAILED_V0886_GET_STUDY_CLEAN_PREVIEW=" + str(response.status_code))

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
            fail("FAILED_V0886_HTML_TERM_MISSING=" + term)

    safe_image_rendered = "data:image/png;base64," in html
    missing_crop_fallback_visible = "Imaginea validată nu este disponibilă momentan." in html
    rendered_visual_ui_passed = True

    forbidden_html_terms = [
        "formula_visual_evidence/crops/page-001-item-accept.png",
        "formula_visual_evidence/crops/missing-edit.png",
        "visual-accept",
        "visual-edit",
        "visual-study-accept",
        "visual-study-edit",
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
            fail("FAILED_V0886_FORBIDDEN_HTML_TERM_VISIBLE=" + term)

    after_clean = clean_path.read_text(encoding="utf-8")
    after_summary = clean_summary_path.read_text(encoding="utf-8")

    if after_clean != before_clean or after_summary != before_summary:
        fail("FAILED_V0886_GET_MODIFIED_CLEAN_STUDY_ARTIFACTS")

    progress_candidates = [
        output_root / "progress.json",
        output_root / "study_progress.json",
        output_root / "progress.preview.json",
    ]

    if any(path.exists() for path in progress_candidates):
        fail("FAILED_V0886_GET_WROTE_PROGRESS")

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
    "docs/dev/clean-study-preview-visual-items-readonly-ui-smoke-no-share-no-delivery.md",
    "scripts/dev/check-clean-study-preview-visual-items-readonly-ui-smoke-no-share-no-delivery.py",
    "scripts/dev/check-clean-study-preview-visual-items-readonly-ui-smoke-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0886_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary = {
    "VOILA_V0_8_86_CLEAN_STUDY_PREVIEW_VISUAL_ITEMS_READONLY_UI_SMOKE_CHECK": "PASS",
    "smoke_only": True,
    "web_app_changed": False,
    "route_added": False,
    "post_endpoint_added": False,
    "testclient_get_check_performed": True,
    "rendered_visual_ui_passed": rendered_visual_ui_passed,
    "visual_items_section_visible": True,
    "accepted_item_visible": True,
    "edited_item_visible_with_corrected_text": True,
    "explanation_visible": True,
    "page_source_visible": True,
    "safe_image_data_uri_rendered": safe_image_rendered,
    "raw_crop_path_hidden": True,
    "missing_crop_degraded_gracefully": missing_crop_fallback_visible,
    "technical_metadata_hidden": True,
    "raw_json_hidden": True,
    "absolute_paths_hidden": True,
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
    "recommended_next": "v0.8.87-owner-local-review-to-clean-study-visual-flow-final-audit-no-share-no-delivery",
}

evidence_dir.mkdir(parents=True, exist_ok=True)

out_json = evidence_dir / "V0.8.86-CLEAN-STUDY-PREVIEW-VISUAL-ITEMS-READONLY-UI-SMOKE-CHECK.json"
out_md = evidence_dir / "V0.8.86-CLEAN-STUDY-PREVIEW-VISUAL-ITEMS-READONLY-UI-SMOKE-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.86 Clean Study preview visual items read-only UI smoke\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
