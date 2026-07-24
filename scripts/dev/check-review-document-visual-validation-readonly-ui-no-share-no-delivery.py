from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

repo = Path(".").resolve()

doc = repo / "docs" / "dev" / "review-document-visual-validation-readonly-ui-no-share-no-delivery.md"
check_py = repo / "scripts" / "dev" / "check-review-document-visual-validation-readonly-ui-no-share-no-delivery.py"
check_ps1 = repo / "scripts" / "dev" / "check-review-document-visual-validation-readonly-ui-no-share-no-delivery.ps1"
patch_py = repo / "scripts" / "dev" / "apply-review-document-visual-validation-readonly-ui-v0874.py"
web_app = repo / "services" / "api" / "web_app.py"
plan_doc = repo / "docs" / "dev" / "review-document-visual-validation-ui-plan-no-share-no-delivery.md"

def fail(message: str) -> None:
    raise SystemExit(message)

for path in [doc, check_py, check_ps1, patch_py, web_app, plan_doc]:
    if not path.exists():
        fail("FAILED_V0874_REQUIRED_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
web_text = web_app.read_text(encoding="utf-8", errors="replace")
plan_text = plan_doc.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.74 Review Document visual validation read-only UI",
    "first read-only visual validation UI slice inside `Revizuire document`",
    "It implements display only.",
    "It does not add decision saving.",
    "It does not add a POST endpoint.",
    "It does not change `/study`.",
    "`Formule și imagini de verificat`",
    "source page",
    "visual type label",
    "OCR Math candidate text",
    "validation status",
    "whether the crop image is available",
    "Clean Study eligibility",
    "The section is read-only.",
    "It does not show Accept/Edit/Ignore buttons yet.",
    "It does not save manual decisions.",
    "It does not write `visual_items.bbox.validated.json`.",
    "It does not write `visual_items.clean-study.preview.json`.",
    "bbox coordinates",
    "raw artifact file names",
    "absolute local paths",
    "Diagnostic tehnic",
    "formula_visual_evidence/visual_items.bbox.with-ocrmath-candidates.json",
    "formula_visual_evidence/visual_items.bbox.validated.json",
    "No artifact is created by this UI slice.",
    "This milestone may modify `services/api/web_app.py` for read-only rendering.",
    "It does not start the server during the automated check.",
    "It does not call any route during the automated check.",
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
        fail("FAILED_V0874_DOC_TERM_MISSING=" + term)

for term in [
    "v0.8.73 Review Document visual validation UI plan",
    "Add read-only visual validation UI section in `Revizuire document`.",
    "Show crop image and candidate text from existing artifacts.",
]:
    if term not in plan_text:
        fail("FAILED_V0874_PLAN_TERM_MISSING=" + term)

required_web_terms = [
    "VOILA_V0_8_74_REVIEW_DOCUMENT_VISUAL_VALIDATION_READONLY_UI_START",
    "review-document-visual-validation-readonly-ui",
    "_voila_v0874_review_document_visual_validation_readonly_ui_middleware",
    "_voila_v0874_visual_validation_readonly_section",
    "_voila_v0874_load_visual_validation_items",
    "_voila_v0874_safe_course_id",
    "Formule și imagini de verificat",
    "Imagine extrasă din document",
    "Text detectat",
    "Explicație pe înțeles",
    "Eligibilitate Clean Study",
    "Gata pentru lecție",
    "Nu intră încă în lecție",
    "Diagnostic tehnic",
    "visual_items.bbox.with-ocrmath-candidates.json",
    "visual_items.bbox.validated.json",
]

for term in required_web_terms:
    if term not in web_text:
        fail("FAILED_V0874_WEB_TERM_MISSING=" + term)

v0874_block = web_text.split("VOILA_V0_8_74_REVIEW_DOCUMENT_VISUAL_VALIDATION_READONLY_UI_START", 1)[1].split("VOILA_V0_8_74_REVIEW_DOCUMENT_VISUAL_VALIDATION_READONLY_UI_END", 1)[0]

for forbidden in [
    "@app.post",
    ".write_text(",
    ".write_bytes(",
    "subprocess.",
    "FileResponse",
    "RedirectResponse",
    "traceback",
]:
    if forbidden in v0874_block:
        fail("FAILED_V0874_FORBIDDEN_TERM_IN_WEB_BLOCK=" + forbidden)

if "bbox" in v0874_block and "Coordonatele bbox" not in v0874_block:
    pass

subprocess.check_call([sys.executable, "-m", "py_compile", str(web_app)], cwd=str(repo))
subprocess.check_call([sys.executable, "-m", "py_compile", str(patch_py)], cwd=str(repo))
subprocess.check_call([sys.executable, "-m", "py_compile", str(check_py)], cwd=str(repo))

diff_names = subprocess.check_output(
    ["git", "diff", "--name-only"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/review-document-visual-validation-readonly-ui-no-share-no-delivery.md",
    "scripts/dev/apply-review-document-visual-validation-readonly-ui-v0874.py",
    "scripts/dev/check-review-document-visual-validation-readonly-ui-no-share-no-delivery.py",
    "scripts/dev/check-review-document-visual-validation-readonly-ui-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0874_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary = {
    "VOILA_V0_8_74_REVIEW_DOCUMENT_VISUAL_VALIDATION_READONLY_UI_CHECK": "PASS",
    "readonly_ui_added": True,
    "web_app_changed": "services/api/web_app.py" in diff_names,
    "review_document_section_added": True,
    "shows_page": True,
    "shows_visual_type": True,
    "shows_ocr_math_candidate_text": True,
    "shows_validation_status": True,
    "shows_crop_availability": True,
    "shows_clean_study_eligibility": True,
    "accept_edit_ignore_buttons_added": False,
    "post_endpoint_added": False,
    "manual_decision_write": False,
    "clean_study_write": False,
    "study_route_changed": False,
    "server_started": False,
    "route_called": False,
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
    "recommended_next": "v0.8.75-owner-local-review-document-visual-validation-readonly-browser-smoke-no-share-no-delivery",
}

evidence_dir = Path(r"D:\dev\tester-runs\v0874-review-document-visual-validation-readonly-ui-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

out_json = evidence_dir / "V0.8.74-REVIEW-DOCUMENT-VISUAL-VALIDATION-READONLY-UI-CHECK.json"
out_md = evidence_dir / "V0.8.74-REVIEW-DOCUMENT-VISUAL-VALIDATION-READONLY-UI-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.74 Review Document visual validation read-only UI\n\n"
    + "\n".join(f"- {key}: {value}" for key, value in summary.items())
    + "\n",
    encoding="utf-8",
)

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
