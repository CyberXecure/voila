from pathlib import Path
import json
import subprocess

repo = Path(".").resolve()
web_app = repo / "services" / "api" / "web_app.py"
doc = repo / "docs" / "dev" / "hide-deprecated-visual-ocrmath-user-links-no-share-no-delivery.md"
v0865_doc = repo / "docs" / "dev" / "bbox-crop-ocrmath-pipeline-plan-no-share-no-delivery.md"

def fail(message: str) -> None:
    raise SystemExit(message)

for path in [web_app, doc, v0865_doc]:
    if not path.exists():
        fail("FAILED_V0866_REQUIRED_FILE_MISSING=" + str(path))

web_text = web_app.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")
v0865_text = v0865_doc.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.66 Hide deprecated visual/OCR Math user links",
    "Display-only UI/navigation change.",
    "Home link to old `figures_hybrid/figures_hybrid.html`",
    "Home link to old `figures/figures.html`",
    "Home link to old `/edit-crops`",
    "Course Tools card `OCR Math Diagnostic`",
    "Course Tools card `Figures`",
    "Course Tools card `Edit crops`",
    "Injected bottom/navigation link `OCR Math`",
    "No OCR logic change.",
    "No LanguageTool logic change.",
    "No crop generation logic change.",
    "No Study logic change.",
    "No Progress logic change.",
    "No build.",
    "No ZIP.",
    "No share link.",
    "No tester delivery.",
    "No public release.",
]

for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_V0866_DOC_TERM_MISSING=" + term)

required_v0865_terms = [
    "PDF -> OCR text -> LanguageTool suggestions -> page image -> bbox -> real crop -> OCR Math on crop -> manual validation -> clean Study",
    "Global OCR Math before bbox/crop is deprecated for the user-facing flow.",
    "The old shrink/preview/hybrid crop flow must be removed from user-facing navigation or clearly deprecated.",
]

for term in required_v0865_terms:
    if term not in v0865_text:
        fail("FAILED_V0866_V0865_PLAN_TERM_MISSING=" + term)

required_markers = [
    "VOILA_V0_8_66_HIDE_DEPRECATED_HOME_VISUAL_LINKS_START",
    "VOILA_V0_8_66_HIDE_DEPRECATED_COURSE_TOOLS_OCRMATH_CARD_START",
    "VOILA_V0_8_66_HIDE_DEPRECATED_COURSE_TOOLS_FIGURES_CARD_START",
    "VOILA_V0_8_66_HIDE_DEPRECATED_COURSE_TOOLS_EDIT_CROPS_CARD_START",
    "VOILA_V0_8_66_HIDE_DEPRECATED_BOTTOM_OCRMATH_LINK",
]

for marker in required_markers:
    if marker not in web_text:
        fail("FAILED_V0866_WEB_MARKER_MISSING=" + marker)

# Home primary actions section must no longer append old visual/crop links.
home_start = web_text.find("def home(")
home_quiz = web_text.find("if quiz_file.exists():", home_start)
if home_start == -1 or home_quiz == -1:
    fail("FAILED_V0866_HOME_SECTION_NOT_FOUND")

home_primary = web_text[home_start:home_quiz]
for forbidden in [
    'output_url(pdf.stem, "figures_hybrid", "figures_hybrid.html")',
    'output_url(pdf.stem, "figures", "figures.html")',
    'href="/edit-crops?pdf={quote(pdf.name)}"',
]:
    if forbidden in home_primary:
        fail("FAILED_V0866_HOME_DEPRECATED_LINK_STILL_PRIMARY=" + forbidden)

# Course Tools primary cards must no longer expose old/deprecated entries.
for forbidden in [
    'card(\n            "OCR Math Diagnostic"',
    'f"/owner/ocr-math-report/{quote(pdf_path.stem, safe=\'\')}/view"',
    'card(\n            _ut("ui.figures", "Figures")',
    'f"/view-figures?pdf={q}"',
    'card(\n            _ut("ui.edit_crops", "Edit crops")',
    'f"/edit-crops?pdf={q}"',
    'addLink(nav, "OCR Math"',
    'f"/owner/ocr-math-report/{_nav_quote(course_id)}/view"',
    '<a href="/owner/ocr-math-report/{quote(pdf_path.stem, safe=\'\')}/view">OCR Math</a>',
]:
    if forbidden in web_text:
        fail("FAILED_V0866_DEPRECATED_USER_LINK_STILL_PRESENT=" + forbidden)

# Technical routes must remain present. We hide links; we do not delete capability.
for required in [
    '@app.get("/owner/ocr-math-report/{course_id}/view"',
    '@app.get("/edit-crops")',
    '@app.get("/view-figures")',
    '@app.get("/course-tools")',
    '@app.get("/review-document"',
]:
    if required not in web_text:
        fail("FAILED_V0866_TECHNICAL_ROUTE_REMOVED=" + required)

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "services/api/web_app.py",
    "docs/dev/hide-deprecated-visual-ocrmath-user-links-no-share-no-delivery.md",
    "scripts/dev/check-hide-deprecated-visual-ocrmath-user-links-no-share-no-delivery.py",
    "scripts/dev/check-hide-deprecated-visual-ocrmath-user-links-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0866_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary = {
    "VOILA_V0_8_66_HIDE_DEPRECATED_VISUAL_OCRMATH_USER_LINKS_CHECK": "PASS",
    "display_only_patch": True,
    "home_old_figures_links_hidden": True,
    "home_old_edit_crops_link_hidden": True,
    "course_tools_global_ocr_math_card_hidden": True,
    "course_tools_old_figures_card_hidden": True,
    "course_tools_old_edit_crops_card_hidden": True,
    "bottom_nav_global_ocr_math_link_hidden": True,
    "technical_ocr_math_route_preserved": True,
    "technical_edit_crops_route_preserved": True,
    "technical_view_figures_route_preserved": True,
    "review_document_route_preserved": True,
    "canonical_bbox_crop_flow_preserved_as_plan": True,
    "server_started": False,
    "post_called": False,
    "upload_performed": False,
    "generate_performed": False,
    "ocr_run": False,
    "languagetool_run": False,
    "crop_generation_performed": False,
    "study_logic_changed": False,
    "progress_logic_changed": False,
    "build_performed": False,
    "zip_created": False,
    "onedrive_staging_created": False,
    "share_link_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "recommended_next": "v0.8.67-owner-local-bbox-visual-item-contract-no-share-no-delivery",
}

evidence_dir = Path(r"D:\dev\tester-runs\v0866-hide-deprecated-visual-ocrmath-user-links-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

out_json = evidence_dir / "V0.8.66-HIDE-DEPRECATED-VISUAL-OCRMATH-USER-LINKS-CHECK.json"
out_md = evidence_dir / "V0.8.66-HIDE-DEPRECATED-VISUAL-OCRMATH-USER-LINKS-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.66 Hide deprecated visual/OCR Math user links\n\n"
    + "\n".join(f"- {k}: {v}" for k, v in summary.items())
    + "\n",
    encoding="utf-8",
)

for k, v in summary.items():
    print(f"{k}={v}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
