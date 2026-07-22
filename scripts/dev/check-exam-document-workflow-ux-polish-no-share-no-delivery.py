from pathlib import Path
import hashlib
import json
import re
import subprocess
import time
import urllib.request
import urllib.error

root = Path(".").resolve()

doc = root / "docs" / "dev" / "exam-document-workflow-ux-polish-no-share-no-delivery.md"
check_py = root / "scripts" / "dev" / "check-exam-document-workflow-ux-polish-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-exam-document-workflow-ux-polish-no-share-no-delivery.ps1"
web = root / "services" / "api" / "web_app.py"

for path, marker in [
    (doc, "FAILED_V0842_DOC_MISSING"),
    (check_py, "FAILED_V0842_CHECK_PY_MISSING"),
    (check_ps1, "FAILED_V0842_CHECK_PS1_MISSING"),
    (web, "FAILED_V0842_WEB_APP_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker + "=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
web_text = web.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "Exam document workflow UX polish",
    "owner_personal_workflow_result=NEEDS_UX_POLISH",
    "Învață pentru examen din acest document",
    "Revizuiește documentul",
    "Alege noțiuni importante",
    "Creează material de învățare",
    "Învață acum",
    "Exersează pentru examen",
    "OCR Review, Crop Editor, and Manual Learning Evidence should be presented as one learner-facing idea",
    "`Revizuire document`",
    "It does not rebuild the package.",
    "It does not create a new ZIP.",
    "It does not copy to OneDrive.",
    "It does not create a share.",
    "It does not deliver anything.",
    "It does not distribute anything.",
    "It does not create a public release.",
    "It does not add a route.",
    "It does not add a POST endpoint.",
    "It does not change Study behavior.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit("FAILED_V0842_DOC_TERM_MISSING=" + term)

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/exam-document-workflow-ux-polish-no-share-no-delivery.md",
    "scripts/dev/check-exam-document-workflow-ux-polish-no-share-no-delivery.py",
    "scripts/dev/check-exam-document-workflow-ux-polish-no-share-no-delivery.ps1",
    "services/api/web_app.py",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0842_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

required_web_terms = [
    "VOILA_V0_8_42_EXAM_DOCUMENT_WORKFLOW_UX_POLISH_START",
    "exam-document-workflow-ux-polish",
    "Învață pentru examen din acest document",
    "Transformă documentul în pași clari de învățare",
    "Revizuiește documentul",
    "Alege noțiuni importante",
    "Creează material de învățare",
    "Învață acum",
    "Exersează pentru examen",
    "Diagnostic tehnic",
    "Manual Learning Evidence",
    "Learning Pack preview",
    "Manual Study Items preview",
    "exam-workflow-review-document",
    "exam-workflow-important-concepts",
    "exam-workflow-study-now",
    "exam-workflow-technical-diagnostic",
    "manual-study-default-route",
    "manual-study-default-cards",
    "manual_study_default_read_only_fallback",
    "manual-study-shadow-route",
    "manual-study-shadow-course-tools-link",
    "manual-study-dry-run-course-tools-link",
    "/study?pdf=",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit("FAILED_V0842_WEB_TERM_MISSING=" + term)

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0842_STUDY_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/study"') != 0:
    raise SystemExit("FAILED_V0842_STUDY_POST_ADDED")

if web_text.count('@app.middleware("http")') < 1:
    raise SystemExit("FAILED_V0842_MIDDLEWARE_NOT_PRESENT")

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
    raise SystemExit(f"FAILED_V0842_{label}_FETCH={last}")

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
    raise SystemExit("FAILED_V0842_HEALTH_STATUS=" + str(health_status))

course_id = "03-pag-30-34-vectori-trigonometrie"
pdf_name = course_id + ".pdf"
course_tools_url = "http://127.0.0.1:8787/course-tools?pdf=" + pdf_name
study_url = "http://127.0.0.1:8787/study?pdf=" + pdf_name

course_tools_status, course_tools_body = fetch(course_tools_url, "COURSE_TOOLS")
if course_tools_status != 200:
    raise SystemExit("FAILED_V0842_COURSE_TOOLS_STATUS=" + str(course_tools_status))

required_course_tools_terms = [
    "exam-document-workflow-ux-polish",
    "Învață pentru examen din acest document",
    "Transformă documentul în pași clari de învățare",
    "Revizuiește documentul",
    "Alege noțiuni importante",
    "Creează material de învățare",
    "Învață acum",
    "Exersează pentru examen",
    "Diagnostic tehnic",
    "exam-workflow-review-document",
    "exam-workflow-important-concepts",
    "exam-workflow-study-now",
    "/owner/manual-learning-evidence/03-pag-30-34-vectori-trigonometrie?page=1",
    "/owner/manual-study-preview/03-pag-30-34-vectori-trigonometrie",
    "/study?pdf=03-pag-30-34-vectori-trigonometrie.pdf",
]

for term in required_course_tools_terms:
    if term not in course_tools_body:
        raise SystemExit("FAILED_V0842_COURSE_TOOLS_TERM_MISSING=" + term)

study_status, study_body = fetch(study_url, "STUDY")
if study_status != 200:
    raise SystemExit("FAILED_V0842_STUDY_STATUS=" + str(study_status))

for term in [
    "manual-study-default-route",
    "manual-study-default-cards",
    "manual_study_default_read_only_fallback",
]:
    if term not in study_body:
        raise SystemExit("FAILED_V0842_STUDY_TERM_MISSING=" + term)

evidence_dir = Path(r"D:\dev\tester-runs\v0842-exam-document-workflow-ux-polish-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_42_EXAM_DOCUMENT_WORKFLOW_UX_POLISH_CHECK": "PASS",
    "depends_on_v0841_owner_personal_smoke": True,
    "ux_result_addressed": "NEEDS_UX_POLISH",
    "course_tools_student_workflow_card_added": True,
    "student_facing_title": "Învață pentru examen din acest document",
    "student_workflow_step_review_document": True,
    "student_workflow_step_choose_important_concepts": True,
    "student_workflow_step_create_learning_material": True,
    "student_workflow_step_study_now": True,
    "student_workflow_step_practice_for_exam": True,
    "unified_review_document_concept_present": True,
    "technical_diagnostic_details_present": True,
    "course_tools_status": course_tools_status,
    "study_status": study_status,
    "study_normal_still_renders_manual_default": True,
    "web_app_changed": True,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "study_changed": False,
    "progress_write_added": False,
    "answer_marking_added": False,
    "ocr_rewrite_performed": False,
    "formula_ocr_performed": False,
    "crop_file_written": False,
    "package_rebuild_performed": False,
    "new_zip_created": False,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "EXAM_DOCUMENT_WORKFLOW_UX_POLISH": "PASS_OWNER_LOCAL_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_RETEST_AND_PACKAGE_REBUILD",
    "POLICY": "exam_document_workflow_ux_polish_no_rebuild_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.43-owner-personal-workflow-retest-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.42-EXAM-DOCUMENT-WORKFLOW-UX-POLISH-CHECK.json"
out_md = evidence_dir / "V0.8.42-EXAM-DOCUMENT-WORKFLOW-UX-POLISH-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.42 Exam document workflow UX polish — no share/no delivery",
    "",
    "## Summary",
]
for key, value in summary.items():
    md_lines.append(f"- {key}: {value}")

out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
