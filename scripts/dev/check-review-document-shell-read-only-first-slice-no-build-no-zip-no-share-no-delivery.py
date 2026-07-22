from pathlib import Path
import json
import re
import subprocess
import time
import urllib.request
import urllib.error

root = Path(".").resolve()

doc = root / "docs" / "dev" / "review-document-shell-read-only-first-slice-no-build-no-zip-no-share-no-delivery.md"
check_py = root / "scripts" / "dev" / "check-review-document-shell-read-only-first-slice-no-build-no-zip-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-review-document-shell-read-only-first-slice-no-build-no-zip-no-share-no-delivery.ps1"
web = root / "services" / "api" / "web_app.py"

for path, label in [
    (doc, "DOC"),
    (check_py, "CHECK_PY"),
    (check_ps1, "CHECK_PS1"),
    (web, "WEB_APP"),
]:
    if not path.exists():
        raise SystemExit(f"FAILED_V0850_{label}_MISSING={path}")

doc_text = doc.read_text(encoding="utf-8", errors="replace")
web_text = web.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.50 Review Document shell read-only first slice",
    "`/review-document?pdf={pdf_name}`",
    "`/review-document/{course_id}`",
    "Revizuire document",
    "Text detectat",
    "Corecturi sugerate",
    "Formule și imagini",
    "Noțiuni importante",
    "Gata pentru studiu",
    "Diagnostic tehnic",
    "No build.",
    "No ZIP.",
    "No package rebuild.",
    "No OneDrive copy.",
    "No share.",
    "No delivery.",
    "No distribution.",
    "No public release.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit("FAILED_V0850_DOC_TERM_MISSING=" + term)

required_web_terms = [
    "VOILA_V0_8_50_REVIEW_DOCUMENT_SHELL_READ_ONLY_FIRST_SLICE_START",
    '@app.get("/review-document"',
    '@app.get("/review-document/{course_id}"',
    "review-document-shell-read-only",
    "Revizuire document",
    "Voila! — Documentele tale, lecții clare",
    "Text detectat",
    "Corecturi sugerate",
    "Formule și imagini",
    "Noțiuni importante",
    "Gata pentru studiu",
    "Limba lecției",
    "Română",
    "English",
    "Diagnostic tehnic",
    "Înapoi la Course Tools",
    "data-testid=\"review-step-text-detected\"",
    "data-testid=\"review-step-corrections\"",
    "data-testid=\"review-step-visuals\"",
    "data-testid=\"review-step-important-concepts\"",
    "data-testid=\"review-step-ready-study\"",
    "data-testid=\"review-document-technical-diagnostic\"",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit("FAILED_V0850_WEB_TERM_MISSING=" + term)

if '@app.post("/review-document' in web_text:
    raise SystemExit("FAILED_V0850_POST_REVIEW_DOCUMENT_ADDED")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/review-document-shell-read-only-first-slice-no-build-no-zip-no-share-no-delivery.md",
    "scripts/dev/check-review-document-shell-read-only-first-slice-no-build-no-zip-no-share-no-delivery.py",
    "scripts/dev/check-review-document-shell-read-only-first-slice-no-build-no-zip-no-share-no-delivery.ps1",
    "services/api/web_app.py",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0850_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

for forbidden in [
    "data/output/",
    "data/input/",
    "scripts/dev/build",
    "scripts/dev/package",
]:
    if any(path.replace("\\", "/").startswith(forbidden) for path in changed):
        raise SystemExit("FAILED_V0850_FORBIDDEN_DATA_OR_PACKAGE_CHANGE=" + forbidden)

def fetch(url, label, attempts=30):
    last = ""
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                return response.status, response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8", errors="replace")
        except Exception as exc:
            last = str(exc)
            time.sleep(2)
    raise SystemExit(f"FAILED_V0850_{label}_FETCH={last}")

subprocess.run(
    ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(root / "scripts" / "dev" / "stop-voila.ps1")],
    cwd=str(root),
    check=True,
)

subprocess.run(
    ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(root / "scripts" / "dev" / "start-voila.ps1"), "-Silent"],
    cwd=str(root),
    check=True,
)

health_status, health_body = fetch("http://127.0.0.1:8787/health", "HEALTH")
if health_status != 200:
    raise SystemExit("FAILED_V0850_HEALTH_STATUS=" + str(health_status))

course_id = "03-pag-30-34-vectori-trigonometrie"
pdf_name = course_id + ".pdf"

query_status, query_body = fetch(
    "http://127.0.0.1:8787/review-document?pdf=" + pdf_name,
    "REVIEW_DOCUMENT_QUERY",
)

if query_status != 200:
    raise SystemExit("FAILED_V0850_REVIEW_QUERY_STATUS=" + str(query_status))

alias_status, alias_body = fetch(
    "http://127.0.0.1:8787/review-document/" + course_id,
    "REVIEW_DOCUMENT_ALIAS",
)

if alias_status != 200:
    raise SystemExit("FAILED_V0850_REVIEW_ALIAS_STATUS=" + str(alias_status))

required_page_terms = [
    "review-document-shell-read-only",
    "Revizuire document",
    "Voila! — Documentele tale, lecții clare",
    "03-pag-30-34-vectori-trigonometrie.pdf",
    "Limba lecției",
    "Română",
    "English",
    "Text detectat",
    "Corecturi sugerate",
    "Formule și imagini",
    "Noțiuni importante",
    "Gata pentru studiu",
    "Ghid pentru student",
    "Diagnostic tehnic",
    "Înapoi la Course Tools",
    "/course-tools?pdf=03-pag-30-34-vectori-trigonometrie.pdf",
]

for term in required_page_terms:
    if term not in query_body:
        raise SystemExit("FAILED_V0850_PAGE_TERM_MISSING=" + term)

if '<form' in query_body.lower():
    raise SystemExit("FAILED_V0850_FORM_PRESENT_ON_READ_ONLY_SHELL")

if 'method="post"' in query_body.lower() or "method='post'" in query_body.lower():
    raise SystemExit("FAILED_V0850_POST_FORM_PRESENT_ON_READ_ONLY_SHELL")

diagnostic_match = re.search(r"<details[^>]*data-testid=\"review-document-technical-diagnostic\"", query_body)
if not diagnostic_match:
    raise SystemExit("FAILED_V0850_DIAGNOSTIC_DETAILS_MISSING")

for forbidden_visible in [
    "source_evidence_id",
    "manual_study_item_id",
    "visual_evidence_id",
    "delivery_performed",
    "build_performed",
    "zip_created",
]:
    before_diag = query_body.split("Diagnostic tehnic", 1)[0]
    if forbidden_visible in before_diag:
        raise SystemExit("FAILED_V0850_TECHNICAL_LABEL_VISIBLE_BEFORE_DIAGNOSTIC=" + forbidden_visible)

evidence_dir = Path(r"D:\dev\tester-runs\v0850-review-document-shell-read-only-first-slice-no-build-no-zip-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_50_REVIEW_DOCUMENT_SHELL_READ_ONLY_FIRST_SLICE_CHECK": "PASS",
    "implementation_performed": True,
    "read_only_shell_added": True,
    "primary_route": "/review-document?pdf={pdf_name}",
    "alias_route": "/review-document/{course_id}",
    "query_route_status": query_status,
    "alias_route_status": alias_status,
    "health_ok": True,
    "product_positioning_visible": True,
    "shell_title_visible": True,
    "document_name_visible": True,
    "lesson_language_visible": True,
    "step_text_detected_visible": True,
    "step_corrections_visible": True,
    "step_formulas_images_visible": True,
    "step_important_concepts_visible": True,
    "step_ready_for_study_visible": True,
    "guidance_panel_visible": True,
    "diagnostic_collapsed_present": True,
    "course_tools_back_link_visible": True,
    "read_only_no_form_present": True,
    "technical_labels_hidden_from_main_surface": True,
    "web_app_changed": True,
    "new_route_added": True,
    "new_post_endpoint_added": False,
    "study_changed": False,
    "progress_write_added": False,
    "answer_marking_added": False,
    "ocr_started": False,
    "languagetool_started": False,
    "ocr_performed": False,
    "languagetool_correction_performed": False,
    "formula_ocr_performed": False,
    "crop_extraction_performed": False,
    "crop_file_written": False,
    "visual_evidence_written": False,
    "manual_evidence_written": False,
    "study_cards_created": False,
    "ocr_rewrite_performed": False,
    "build_performed": False,
    "package_rebuild_performed": False,
    "new_zip_created": False,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "REVIEW_DOCUMENT_SHELL_READ_ONLY_FIRST_SLICE": "PASS_OWNER_LOCAL_READ_ONLY_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_UI_IMPLEMENTATION_AND_RETEST",
    "POLICY": "review_document_shell_read_only_first_slice_no_build_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.51-owner-local-course-tools-link-to-review-document-shell-no-build-no-zip-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.50-REVIEW-DOCUMENT-SHELL-READ-ONLY-FIRST-SLICE-CHECK.json"
out_md = evidence_dir / "V0.8.50-REVIEW-DOCUMENT-SHELL-READ-ONLY-FIRST-SLICE-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.50 Review Document shell read-only first slice — no build/no ZIP/no share/no delivery",
    "",
    "## Summary",
]
for key, value in summary.items():
    md_lines.append(f"- {key}: {value}")
out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

for key, value in summary.items():
    print(f"{key}={value}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
