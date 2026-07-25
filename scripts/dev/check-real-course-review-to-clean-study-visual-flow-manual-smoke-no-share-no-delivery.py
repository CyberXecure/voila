from __future__ import annotations

import base64
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

course_id = "03-pag-30-34-vectori-trigonometrie"
input_pdf = repo / "data" / "input" / (course_id + ".pdf")
output_dir = repo / "data" / "output" / course_id
visual_dir = output_dir / "formula_visual_evidence"
crop_dir = visual_dir / "crops"
candidate_path = visual_dir / "visual_items.bbox.with-ocrmath-candidates.json"
validated_path = visual_dir / "visual_items.bbox.validated.json"
clean_path = visual_dir / "visual_items.clean-study.preview.json"
clean_summary_path = visual_dir / "visual_items.clean-study.preview-summary.json"

doc = repo / "docs" / "dev" / "real-course-review-to-clean-study-visual-flow-manual-smoke-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"
evidence_dir = Path(r"D:\dev\tester-runs\v0888-real-course-review-to-clean-study-visual-flow-manual-smoke-no-share-no-delivery")
backup_dir = evidence_dir / "backup-formula_visual_evidence"

save_path = "/review-document/visual-validation/save"
refresh_path = "/review-document/visual-validation/refresh-clean-study-preview"


class FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.forms: list[dict[str, object]] = []
        self.current: dict[str, object] | None = None
        self.current_textarea: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {str(k).lower(): (v if v is not None else "") for k, v in attrs}
        tag = tag.lower()

        if tag == "form":
            self.current = {"attrs": attrs_dict, "fields": {}}
            self.current_textarea = None
            return

        if self.current is None:
            return

        fields = self.current.get("fields")
        if not isinstance(fields, dict):
            return

        if tag == "input":
            name = str(attrs_dict.get("name") or "")
            if name:
                fields[name] = str(attrs_dict.get("value") or "")

        if tag == "textarea":
            name = str(attrs_dict.get("name") or "")
            if name:
                fields[name] = ""
                self.current_textarea = name

    def handle_data(self, data: str) -> None:
        if self.current is None or self.current_textarea is None:
            return

        fields = self.current.get("fields")
        if isinstance(fields, dict):
            fields[self.current_textarea] = str(fields.get(self.current_textarea) or "") + data

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "textarea":
            self.current_textarea = None
            return

        if tag == "form" and self.current is not None:
            self.forms.append(self.current)
            self.current = None
            self.current_textarea = None


def fail(message: str) -> None:
    raise SystemExit(message)


def read_bytes_or_none(path: Path) -> bytes | None:
    if path.exists() and path.is_file():
        return path.read_bytes()
    return None


def progress_snapshot() -> dict[str, bytes | None]:
    candidates = [
        output_dir / "progress.json",
        output_dir / "study_progress.json",
        output_dir / "progress.preview.json",
    ]
    return {str(path): read_bytes_or_none(path) for path in candidates}


def assert_progress_unchanged(before: dict[str, bytes | None]) -> None:
    after = progress_snapshot()
    if after != before:
        fail("FAILED_V0888_PROGRESS_CHANGED")


def find_form(forms: list[dict[str, object]], action: str, **expected: str) -> dict[str, str]:
    matches: list[dict[str, str]] = []

    for form in forms:
        attrs = form.get("attrs")
        fields = form.get("fields")

        if not isinstance(attrs, dict) or not isinstance(fields, dict):
            continue

        if str(attrs.get("action") or "") != action:
            continue

        if str(attrs.get("method") or "").lower() != "post":
            continue

        ok = True
        for key, value in expected.items():
            if str(fields.get(key) or "") != value:
                ok = False
                break

        if ok:
            matches.append({str(k): str(v) for k, v in fields.items()})

    if len(matches) != 1:
        fail("FAILED_V0888_FORM_COUNT_UNEXPECTED=" + action + ":" + json.dumps(expected, ensure_ascii=False) + ":" + str(len(matches)))

    return matches[0]


for path in [doc, web_app]:
    if not path.exists():
        fail("FAILED_V0888_REQUIRED_FILE_MISSING=" + str(path))

if not input_pdf.exists():
    fail("FAILED_V0888_REAL_INPUT_PDF_MISSING=" + str(input_pdf))

if not output_dir.exists() or not output_dir.is_dir():
    fail("FAILED_V0888_REAL_OUTPUT_DIR_MISSING=" + str(output_dir))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
web_text = web_app.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.88 Real-course Review-to-Clean-Study visual flow manual smoke",
    "`03-pag-30-34-vectori-trigonometrie`",
    "This is not a package milestone.",
    "It does not build.",
    "It does not create a ZIP.",
    "It does not share or deliver anything.",
    "rendered visual validation forms",
    "accept/edit/ignore POST",
    "`visual_items.bbox.validated.json`",
    "`Actualizează lecția curată`",
    "explicit Clean Study refresh POST",
    "`visual_items.clean-study.preview.json`",
    "Clean Study preview read-only learner UI",
    "Before writing, it backs up the real course `formula_visual_evidence` directory if it exists.",
    "After the smoke, it restores the original state.",
    "Progress is not modified",
    "`/study` is not changed",
    "It does not modify `services/api/web_app.py`.",
    "It does not add a route.",
    "It does not add a POST endpoint.",
    "It does not start uvicorn.",
    "It does not start LanguageTool.",
    "It does not upload a PDF.",
    "It does not run `/generate`.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "It does not run OCR Math.",
    "It does not generate crops.",
    "It does not create OneDrive staging.",
    "It does not create a share link.",
    "It does not deliver to testers.",
    "It does not distribute anything.",
    "It does not create a public release.",
    "It still does not authorize a tester package.",
    "v0.8.89-owner-local-real-course-review-to-clean-study-visual-flow-final-readiness-audit-no-share-no-delivery",
]

for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_V0888_DOC_TERM_MISSING=" + term)

required_web_terms = [
    "VOILA_V0_8_77_REVIEW_DOCUMENT_VISUAL_VALIDATION_SAVE_ACTION_START",
    "VOILA_V0_8_78_REVIEW_DOCUMENT_VISUAL_VALIDATION_FORM_CONTROLS",
    "VOILA_V0_8_81_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_ACTION_START",
    '@app.post("/review-document/visual-validation/refresh-clean-study-preview")',
    "VOILA_V0_8_82_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_UI_CONTROL_START",
    "Actualizează lecția curată",
    "VOILA_V0_8_85_CLEAN_STUDY_PREVIEW_VISUAL_ITEMS_READONLY_UI_START",
    "Elemente vizuale validate",
]

for term in required_web_terms:
    if term not in web_text:
        fail("FAILED_V0888_WEB_TERM_MISSING=" + term)

web_diff = subprocess.check_output(
    ["git", "diff", "--name-only", "--", "services/api/web_app.py"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).strip()

if web_diff:
    fail("FAILED_V0888_WEB_APP_HAS_WORKTREE_DIFF=" + web_diff)

subprocess.check_call([sys.executable, "-m", "py_compile", str(web_app)], cwd=str(repo))

evidence_dir.mkdir(parents=True, exist_ok=True)
if backup_dir.exists():
    shutil.rmtree(backup_dir)

had_original_visual_dir = visual_dir.exists()
restored = False

progress_before = progress_snapshot()

try:
    if had_original_visual_dir:
        shutil.copytree(visual_dir, backup_dir)

    if visual_dir.exists():
        shutil.rmtree(visual_dir)

    crop_dir.mkdir(parents=True, exist_ok=True)

    one_pixel_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
    )
    (crop_dir / "v0888-accept.png").write_bytes(one_pixel_png)

    candidate_payload = {
        "schema_version": "v0.8.67",
        "course_id": course_id,
        "source_pdf": course_id + ".pdf",
        "items": [
            {
                "item_id": "v0888-accept",
                "kind": "formula",
                "page": 1,
                "bbox": [80, 100, 780, 260],
                "bbox_units": "pdf_points",
                "page_image_path": "formula_visual_evidence/pages/v0888-page-001.png",
                "crop_path": "formula_visual_evidence/crops/v0888-accept.png",
                "crop_exists": True,
                "ocr_math_candidate_text": "sin x / cos x",
                "ocr_math_status": "pending_user_validation",
                "user_decision": "pending",
                "user_corrected_text": "",
                "user_explanation": "",
                "ready_for_study": False,
                "created_by": "v0.8.88-real-course-smoke",
                "review_notes": "Temporary real-course smoke accepted item.",
            },
            {
                "item_id": "v0888-edit",
                "kind": "formula",
                "page": 2,
                "bbox": [90, 300, 790, 420],
                "bbox_units": "pdf_points",
                "page_image_path": "formula_visual_evidence/pages/v0888-page-002.png",
                "crop_path": "formula_visual_evidence/crops/v0888-missing-edit.png",
                "crop_exists": True,
                "ocr_math_candidate_text": "tan x = sin x / cos x",
                "ocr_math_status": "pending_user_validation",
                "user_decision": "pending",
                "user_corrected_text": "",
                "user_explanation": "",
                "ready_for_study": False,
                "created_by": "v0.8.88-real-course-smoke",
                "review_notes": "Temporary real-course smoke edited item.",
            },
            {
                "item_id": "v0888-ignore",
                "kind": "diagram",
                "page": 3,
                "bbox": [100, 500, 300, 580],
                "bbox_units": "pdf_points",
                "page_image_path": "formula_visual_evidence/pages/v0888-page-003.png",
                "crop_path": "formula_visual_evidence/crops/v0888-ignore.png",
                "crop_exists": True,
                "ocr_math_candidate_text": "Diagram de ignorat",
                "ocr_math_status": "pending_user_validation",
                "user_decision": "pending",
                "user_corrected_text": "",
                "user_explanation": "",
                "ready_for_study": False,
                "created_by": "v0.8.88-real-course-smoke",
                "review_notes": "Temporary real-course smoke ignored item.",
            },
        ],
    }

    candidate_path.write_text(json.dumps(candidate_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    app_module = importlib.import_module("services.api.web_app")
    from fastapi.testclient import TestClient

    client = TestClient(app_module.app)

    review_response = client.get("/review-document/" + course_id)
    if review_response.status_code != 200:
        fail("FAILED_V0888_REVIEW_DOCUMENT_GET=" + str(review_response.status_code))

    review_html = review_response.text
    for term in ["Formule și imagini de verificat", "Acceptă", "Salvează corectarea", "Ignoră"]:
        if term not in review_html:
            fail("FAILED_V0888_REVIEW_HTML_TERM_MISSING=" + term)

    parser = FormParser()
    parser.feed(review_html)

    accept_form = find_form(parser.forms, save_path, course_id=course_id, item_id="v0888-accept", decision="accept")
    edit_form = find_form(parser.forms, save_path, course_id=course_id, item_id="v0888-edit", decision="edit")
    ignore_form = find_form(parser.forms, save_path, course_id=course_id, item_id="v0888-ignore", decision="ignore")

    accept_response = client.post(save_path, data=accept_form)
    if accept_response.status_code != 200:
        fail("FAILED_V0888_ACCEPT_POST=" + str(accept_response.status_code))

    edit_form["user_corrected_text"] = r"\tan x = \frac{\sin x}{\cos x}"
    edit_form["user_explanation"] = "Formula corectată intră în lecția curată."
    edit_response = client.post(save_path, data=edit_form)
    if edit_response.status_code != 200:
        fail("FAILED_V0888_EDIT_POST=" + str(edit_response.status_code))

    ignore_response = client.post(save_path, data=ignore_form)
    if ignore_response.status_code != 200:
        fail("FAILED_V0888_IGNORE_POST=" + str(ignore_response.status_code))

    if not validated_path.exists():
        fail("FAILED_V0888_VALIDATED_ARTIFACT_MISSING")

    validated_payload = json.loads(validated_path.read_text(encoding="utf-8"))
    validated_items = validated_payload.get("items")
    if not isinstance(validated_items, list):
        fail("FAILED_V0888_VALIDATED_ITEMS_NOT_LIST")

    validated_by_id = {
        str(item.get("item_id")): item
        for item in validated_items
        if isinstance(item, dict)
    }

    if validated_by_id["v0888-accept"].get("ready_for_study") is not True:
        fail("FAILED_V0888_ACCEPT_NOT_READY")
    if validated_by_id["v0888-edit"].get("user_corrected_text") != r"\tan x = \frac{\sin x}{\cos x}":
        fail("FAILED_V0888_EDIT_CORRECTED_TEXT")
    if validated_by_id["v0888-ignore"].get("ready_for_study") is not False:
        fail("FAILED_V0888_IGNORE_READY_SHOULD_BE_FALSE")

    review_after_response = client.get("/review-document/" + course_id)
    if review_after_response.status_code != 200:
        fail("FAILED_V0888_REVIEW_AFTER_GET=" + str(review_after_response.status_code))

    review_after_html = review_after_response.text
    for term in ["Actualizează lecția curată", "/review-document/visual-validation/refresh-clean-study-preview"]:
        if term not in review_after_html:
            fail("FAILED_V0888_REFRESH_UI_TERM_MISSING=" + term)

    refresh_parser = FormParser()
    refresh_parser.feed(review_after_html)
    refresh_form = find_form(refresh_parser.forms, refresh_path, course_id=course_id)

    if refresh_form != {"course_id": course_id}:
        fail("FAILED_V0888_REFRESH_FORM_FIELDS_UNEXPECTED=" + json.dumps(refresh_form, ensure_ascii=False, sort_keys=True))

    if clean_path.exists() or clean_summary_path.exists():
        fail("FAILED_V0888_CLEAN_STUDY_EXISTS_BEFORE_REFRESH")

    refresh_response = client.post(refresh_path, data=refresh_form)
    if refresh_response.status_code != 200 or "CLEAN_STUDY_REFRESH=PASS" not in refresh_response.text:
        fail("FAILED_V0888_REFRESH_POST=" + str(refresh_response.status_code))

    if not clean_path.exists() or not clean_summary_path.exists():
        fail("FAILED_V0888_CLEAN_STUDY_ARTIFACTS_MISSING_AFTER_REFRESH")

    clean_payload = json.loads(clean_path.read_text(encoding="utf-8"))
    clean_items = clean_payload.get("items")
    if not isinstance(clean_items, list):
        fail("FAILED_V0888_CLEAN_ITEMS_NOT_LIST")

    included_ids = {
        str(item.get("source_visual_item_id"))
        for item in clean_items
        if isinstance(item, dict)
    }

    if included_ids != {"v0888-accept", "v0888-edit"}:
        fail("FAILED_V0888_INCLUDED_IDS_UNEXPECTED=" + json.dumps(sorted(included_ids), ensure_ascii=False))

    clean_json = json.dumps(clean_payload, ensure_ascii=False)
    if "v0888-ignore" not in json.dumps(clean_payload.get("excluded_items", []), ensure_ascii=False):
        fail("FAILED_V0888_IGNORE_NOT_EXCLUDED")

    clean_preview_response = client.get("/study-clean-preview/" + course_id)
    if clean_preview_response.status_code != 200:
        fail("FAILED_V0888_CLEAN_PREVIEW_GET=" + str(clean_preview_response.status_code))

    clean_html = clean_preview_response.text
    required_clean_terms = [
        "Elemente vizuale validate",
        "Sursa: pagina",
        "Întrebare",
        "Răspuns validat",
        "Explicație",
        "Verificat în Revizuire document.",
        "sin x / cos x",
        r"\tan x = \frac{\sin x}{\cos x}",
        "Formula corectată intră în lecția curată.",
        "data:image/png;base64,",
        "Imaginea validată nu este disponibilă momentan.",
    ]

    for term in required_clean_terms:
        if term not in clean_html:
            fail("FAILED_V0888_CLEAN_PREVIEW_TERM_MISSING=" + term)

    forbidden_clean_terms = [
        "formula_visual_evidence/crops/v0888-accept.png",
        "formula_visual_evidence/crops/v0888-missing-edit.png",
        "visual_items.clean-study.preview.json",
        "visual_items.bbox.validated.json",
        "source_visual_item_id",
        "study_item_id",
        "schema_version",
        "ready_for_study",
        "ready_for_clean_study",
        "user_decision",
        "ocr_math_status",
        "learning_source",
        str(repo),
        "D:\\",
    ]

    for term in forbidden_clean_terms:
        if term in clean_html:
            fail("FAILED_V0888_FORBIDDEN_CLEAN_PREVIEW_TERM_VISIBLE=" + term)

    assert_progress_unchanged(progress_before)

finally:
    if visual_dir.exists():
        shutil.rmtree(visual_dir)

    if had_original_visual_dir and backup_dir.exists():
        shutil.copytree(backup_dir, visual_dir)

    restored = True

assert_progress_unchanged(progress_before)

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/real-course-review-to-clean-study-visual-flow-manual-smoke-no-share-no-delivery.md",
    "scripts/dev/check-real-course-review-to-clean-study-visual-flow-manual-smoke-no-share-no-delivery.py",
    "scripts/dev/check-real-course-review-to-clean-study-visual-flow-manual-smoke-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0888_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary = {
    "VOILA_V0_8_88_REAL_COURSE_REVIEW_TO_CLEAN_STUDY_VISUAL_FLOW_MANUAL_SMOKE_CHECK": "PASS",
    "real_course_id": course_id,
    "real_input_pdf_exists": True,
    "real_output_dir_exists": True,
    "manual_smoke_performed": True,
    "web_app_changed": False,
    "route_added": False,
    "post_endpoint_added": False,
    "testclient_used": True,
    "review_document_get_passed": True,
    "rendered_visual_validation_forms_found": True,
    "accept_post_passed": True,
    "edit_post_passed": True,
    "ignore_post_passed": True,
    "temporary_validated_artifact_created": True,
    "refresh_form_found": True,
    "refresh_form_submits_only_course_id": True,
    "refresh_post_passed": True,
    "temporary_clean_study_preview_created": True,
    "clean_study_preview_get_passed": True,
    "accepted_item_visible": True,
    "edited_item_visible_with_corrected_text": True,
    "ignored_item_excluded": True,
    "safe_image_data_uri_rendered": True,
    "missing_crop_degraded_gracefully": True,
    "technical_metadata_hidden": True,
    "raw_json_hidden": True,
    "absolute_paths_hidden": True,
    "temporary_local_visual_artifact_write": True,
    "real_course_visual_artifacts_restored_after_check": restored,
    "persistent_smoke_artifacts_left_in_real_course": False,
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
    "tester_package_authorized": False,
    "recommended_next": "v0.8.89-owner-local-real-course-review-to-clean-study-visual-flow-final-readiness-audit-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.88-REAL-COURSE-REVIEW-TO-CLEAN-STUDY-VISUAL-FLOW-MANUAL-SMOKE-CHECK.json"
out_md = evidence_dir / "V0.8.88-REAL-COURSE-REVIEW-TO-CLEAN-STUDY-VISUAL-FLOW-MANUAL-SMOKE-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.88 Real-course Review-to-Clean-Study visual flow manual smoke\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
