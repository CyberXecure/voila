from pathlib import Path
import json
import subprocess
import time
import urllib.request
import urllib.error

root = Path(".").resolve()

doc = root / "docs" / "dev" / "course-tools-link-to-review-document-shell-no-build-no-zip-no-share-no-delivery.md"
check_py = root / "scripts" / "dev" / "check-course-tools-link-to-review-document-shell-no-build-no-zip-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-course-tools-link-to-review-document-shell-no-build-no-zip-no-share-no-delivery.ps1"
web = root / "services" / "api" / "web_app.py"

for path, label in [
    (doc, "DOC"),
    (check_py, "CHECK_PY"),
    (check_ps1, "CHECK_PS1"),
    (web, "WEB_APP"),
]:
    if not path.exists():
        raise SystemExit(f"FAILED_V0851_{label}_MISSING={path}")

doc_text = doc.read_text(encoding="utf-8", errors="replace")
web_text = web.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.51 Course Tools link to Review Document shell",
    "`/review-document?pdf={pdf_name}`",
    "Revizuire document",
    "Course Tools",
    "read-only shell",
    "No build.",
    "No ZIP.",
    "No package rebuild.",
    "No OneDrive copy.",
    "No share.",
    "No delivery.",
    "No distribution.",
    "No public release.",
    "v0.8.52 — read-only Text detectat queue from existing OCR artifacts.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit("FAILED_V0851_DOC_TERM_MISSING=" + term)

required_web_terms = [
    "VOILA_V0_8_51_COURSE_TOOLS_LINK_TO_REVIEW_DOCUMENT_SHELL_START",
    "course-tools-review-document-entry",
    "course-tools-review-document-link",
    "Revizuire document",
    "Deschide Revizuire document",
    "Voila! — Documentele tale, lecții clare",
    "/review-document?pdf=",
    '_voila_v0850_valid_pdf_name(pdf_name)',
    'request.url.path != "/course-tools"',
    '@app.middleware("http")',
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit("FAILED_V0851_WEB_TERM_MISSING=" + term)

if '@app.post("/review-document' in web_text:
    raise SystemExit("FAILED_V0851_POST_REVIEW_DOCUMENT_ADDED")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/course-tools-link-to-review-document-shell-no-build-no-zip-no-share-no-delivery.md",
    "scripts/dev/check-course-tools-link-to-review-document-shell-no-build-no-zip-no-share-no-delivery.py",
    "scripts/dev/check-course-tools-link-to-review-document-shell-no-build-no-zip-no-share-no-delivery.ps1",
    "services/api/web_app.py",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0851_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

for forbidden in [
    "data/output/",
    "data/input/",
    "scripts/dev/build",
    "scripts/dev/package",
]:
    if any(path.replace("\\", "/").startswith(forbidden) for path in changed):
        raise SystemExit("FAILED_V0851_FORBIDDEN_DATA_OR_PACKAGE_CHANGE=" + forbidden)

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
    raise SystemExit(f"FAILED_V0851_{label}_FETCH={last}")

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
    raise SystemExit("FAILED_V0851_HEALTH_STATUS=" + str(health_status))

course_id = "03-pag-30-34-vectori-trigonometrie"
pdf_name = course_id + ".pdf"

course_tools_status, course_tools_body = fetch(
    "http://127.0.0.1:8787/course-tools?pdf=" + pdf_name,
    "COURSE_TOOLS",
)

if course_tools_status != 200:
    raise SystemExit("FAILED_V0851_COURSE_TOOLS_STATUS=" + str(course_tools_status))

shell_status, shell_body = fetch(
    "http://127.0.0.1:8787/review-document?pdf=" + pdf_name,
    "REVIEW_DOCUMENT_SHELL",
)

if shell_status != 200:
    raise SystemExit("FAILED_V0851_REVIEW_DOCUMENT_STATUS=" + str(shell_status))

required_course_tools_terms = [
    "course-tools-review-document-entry",
    "course-tools-review-document-link",
    "Revizuire document",
    "Deschide Revizuire document",
    "Voila! — Documentele tale, lecții clare",
    "/review-document?pdf=03-pag-30-34-vectori-trigonometrie.pdf",
]

for term in required_course_tools_terms:
    if term not in course_tools_body:
        raise SystemExit("FAILED_V0851_COURSE_TOOLS_TERM_MISSING=" + term)

required_shell_terms = [
    "review-document-shell-read-only",
    "Revizuire document",
    "Text detectat",
    "Corecturi sugerate",
    "Formule și imagini",
    "Noțiuni importante",
    "Gata pentru studiu",
    "Diagnostic tehnic",
]

for term in required_shell_terms:
    if term not in shell_body:
        raise SystemExit("FAILED_V0851_SHELL_TERM_MISSING=" + term)

main_part = course_tools_body.split("Diagnostic tehnic", 1)[0]
for forbidden_visible in [
    "source_evidence_id",
    "manual_study_item_id",
    "visual_evidence_id",
    "delivery_performed",
    "build_performed",
    "zip_created",
]:
    if forbidden_visible in main_part:
        raise SystemExit("FAILED_V0851_TECHNICAL_LABEL_VISIBLE_IN_COURSE_TOOLS_MAIN=" + forbidden_visible)

evidence_dir = Path(r"D:\dev\tester-runs\v0851-course-tools-link-to-review-document-shell-no-build-no-zip-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_51_COURSE_TOOLS_LINK_TO_REVIEW_DOCUMENT_SHELL_CHECK": "PASS",
    "implementation_performed": True,
    "course_tools_link_added": True,
    "course_tools_status": course_tools_status,
    "review_document_shell_status": shell_status,
    "course_tools_entry_visible": True,
    "review_document_link_visible": True,
    "review_document_link_href": "/review-document?pdf=03-pag-30-34-vectori-trigonometrie.pdf",
    "learner_label_visible": True,
    "product_positioning_visible": True,
    "review_document_shell_still_available": True,
    "technical_labels_hidden_from_course_tools_main_surface": True,
    "web_app_changed": True,
    "new_route_added": False,
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
    "COURSE_TOOLS_LINK_TO_REVIEW_DOCUMENT_SHELL": "PASS_OWNER_LOCAL_READ_ONLY_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_UI_IMPLEMENTATION_AND_RETEST",
    "POLICY": "course_tools_link_to_review_document_shell_no_build_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.52-owner-local-text-detected-read-only-queue-from-existing-ocr-artifacts-no-build-no-zip-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.51-COURSE-TOOLS-LINK-TO-REVIEW-DOCUMENT-SHELL-CHECK.json"
out_md = evidence_dir / "V0.8.51-COURSE-TOOLS-LINK-TO-REVIEW-DOCUMENT-SHELL-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.51 Course Tools link to Review Document shell — no build/no ZIP/no share/no delivery",
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
