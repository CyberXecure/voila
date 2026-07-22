from pathlib import Path
import json
import subprocess
import time
import urllib.request
import urllib.error

root = Path(".").resolve()

doc = root / "docs" / "dev" / "friendly-explanation-form-read-only-static-draft-shell-no-build-no-zip-no-share-no-delivery.md"
check_py = root / "scripts" / "dev" / "check-friendly-explanation-form-read-only-static-draft-shell-no-build-no-zip-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-friendly-explanation-form-read-only-static-draft-shell-no-build-no-zip-no-share-no-delivery.ps1"
web = root / "services" / "api" / "web_app.py"

for path, label in [
    (doc, "DOC"),
    (check_py, "CHECK_PY"),
    (check_ps1, "CHECK_PS1"),
    (web, "WEB_APP"),
]:
    if not path.exists():
        raise SystemExit(f"FAILED_V0855_{label}_MISSING={path}")

doc_text = doc.read_text(encoding="utf-8", errors="replace")
web_text = web.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.55 Friendly explanation form read-only static draft shell",
    "Explicație prietenoasă",
    "Titlu scurt",
    "Ce este asta?",
    "Text / zonă verificată",
    "Explicație pe înțeles",
    "De ce este important?",
    "Sursa: pagina X",
    "Limba lecției",
    "Gata pentru studiu",
    "does not save anything",
    "does not add a POST endpoint",
    "does not create explanation drafts",
    "does not write manual evidence",
    "does not create Study cards",
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
        raise SystemExit("FAILED_V0855_DOC_TERM_MISSING=" + term)

required_web_terms = [
    "VOILA_V0_8_55_FRIENDLY_EXPLANATION_FORM_READ_ONLY_STATIC_DRAFT_SHELL_START",
    "review-document-friendly-explanation-shell",
    "friendly-explanation-read-only-field",
    "friendly-explanation-read-only-status",
    "friendly-explanation-diagnostic",
    "Explicație prietenoasă",
    "Titlu scurt",
    "Ce este asta?",
    "Text / zonă verificată",
    "Explicație pe înțeles",
    "De ce este important?",
    "Sursa: pagina X",
    "Limba lecției",
    "Gata pentru studiu",
    "Machetă statică",
    "Doar citire",
    "Fără salvare",
    "Nu există POST",
    "Nu s-a scris niciun artefact",
    '@app.middleware("http")',
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit("FAILED_V0855_WEB_TERM_MISSING=" + term)

if '@app.post("/review-document' in web_text:
    raise SystemExit("FAILED_V0855_POST_REVIEW_DOCUMENT_ADDED")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/friendly-explanation-form-read-only-static-draft-shell-no-build-no-zip-no-share-no-delivery.md",
    "scripts/dev/check-friendly-explanation-form-read-only-static-draft-shell-no-build-no-zip-no-share-no-delivery.py",
    "scripts/dev/check-friendly-explanation-form-read-only-static-draft-shell-no-build-no-zip-no-share-no-delivery.ps1",
    "services/api/web_app.py",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0855_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

for forbidden in [
    "data/output/",
    "data/input/",
    "scripts/dev/build",
    "scripts/dev/package",
]:
    if any(path.replace("\\", "/").startswith(forbidden) for path in changed):
        raise SystemExit("FAILED_V0855_FORBIDDEN_DATA_OR_PACKAGE_CHANGE=" + forbidden)

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
    raise SystemExit(f"FAILED_V0855_{label}_FETCH={last}")

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
    raise SystemExit("FAILED_V0855_HEALTH_STATUS=" + str(health_status))

course_id = "03-pag-30-34-vectori-trigonometrie"
pdf_name = course_id + ".pdf"

shell_status, shell_body = fetch(
    "http://127.0.0.1:8787/review-document?pdf=" + pdf_name,
    "REVIEW_DOCUMENT_SHELL",
)

if shell_status != 200:
    raise SystemExit("FAILED_V0855_REVIEW_DOCUMENT_STATUS=" + str(shell_status))

alias_status, alias_body = fetch(
    "http://127.0.0.1:8787/review-document/" + course_id,
    "REVIEW_DOCUMENT_ALIAS",
)

if alias_status != 200:
    raise SystemExit("FAILED_V0855_REVIEW_DOCUMENT_ALIAS_STATUS=" + str(alias_status))

required_shell_terms = [
    "review-document-shell-read-only",
    "review-document-text-detected-queue",
    "review-document-corrections-suggested-queue",
    "review-document-formulas-images-queue",
    "review-document-friendly-explanation-shell",
    "Explicație prietenoasă",
    "Titlu scurt",
    "Ce este asta?",
    "Text / zonă verificată",
    "Explicație pe înțeles",
    "De ce este important?",
    "Sursa: pagina X",
    "Limba lecției",
    "Gata pentru studiu",
    "Machetă statică",
    "Doar citire",
    "Fără salvare",
    "friendly-explanation-diagnostic",
    "Diagnostic tehnic pentru Explicație prietenoasă",
    "Nu există POST",
    "Nu s-a scris niciun artefact",
]

for term in required_shell_terms:
    if term not in shell_body:
        raise SystemExit("FAILED_V0855_SHELL_TERM_MISSING=" + term)

for term in [
    "review-document-friendly-explanation-shell",
    "Explicație prietenoasă",
    "Gata pentru studiu",
]:
    if term not in alias_body:
        raise SystemExit("FAILED_V0855_ALIAS_TERM_MISSING=" + term)

if '<form' in shell_body.lower():
    raise SystemExit("FAILED_V0855_FORM_PRESENT_ON_STATIC_READ_ONLY_SHELL")

if 'method="post"' in shell_body.lower() or "method='post'" in shell_body.lower():
    raise SystemExit("FAILED_V0855_POST_FORM_PRESENT_ON_STATIC_READ_ONLY_SHELL")

main_part = shell_body.split("Diagnostic tehnic", 1)[0]
for forbidden_visible in [
    "metadata",
    "bbox",
    "crop_path",
    "visual_evidence_id",
    "source_evidence_id",
    "manual_study_item_id",
    "json",
    "delivery_performed",
    "build_performed",
    "zip_created",
]:
    if forbidden_visible in main_part.lower():
        raise SystemExit("FAILED_V0855_TECHNICAL_LABEL_VISIBLE_IN_MAIN_SURFACE=" + forbidden_visible)

evidence_dir = Path(r"D:\dev\tester-runs\v0855-friendly-explanation-form-read-only-static-draft-shell-no-build-no-zip-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_55_FRIENDLY_EXPLANATION_FORM_READ_ONLY_STATIC_DRAFT_SHELL_CHECK": "PASS",
    "implementation_performed": True,
    "friendly_explanation_shell_added": True,
    "static_read_only_draft_shell": True,
    "shell_status": shell_status,
    "alias_status": alias_status,
    "friendly_explanation_section_visible": True,
    "required_fields_visible": True,
    "read_only_status_visible": True,
    "no_form_present": True,
    "diagnostic_boundary_visible": True,
    "main_surface_technical_labels_hidden": True,
    "text_detected_queue_still_visible": True,
    "corrections_suggested_queue_still_visible": True,
    "formulas_images_queue_still_visible": True,
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
    "explanation_draft_created": False,
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
    "FRIENDLY_EXPLANATION_FORM_READ_ONLY_STATIC_DRAFT_SHELL": "PASS_OWNER_LOCAL_READ_ONLY_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_UI_IMPLEMENTATION_AND_RETEST",
    "POLICY": "friendly_explanation_form_read_only_static_draft_shell_no_build_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.56-owner-local-safe-local-save-for-explanation-drafts-no-build-no-zip-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.55-FRIENDLY-EXPLANATION-FORM-READ-ONLY-STATIC-DRAFT-SHELL-CHECK.json"
out_md = evidence_dir / "V0.8.55-FRIENDLY-EXPLANATION-FORM-READ-ONLY-STATIC-DRAFT-SHELL-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.55 Friendly explanation form read-only static draft shell — no build/no ZIP/no share/no delivery",
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
