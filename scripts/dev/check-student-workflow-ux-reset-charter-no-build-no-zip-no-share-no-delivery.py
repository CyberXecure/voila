from pathlib import Path
import json
import subprocess

root = Path(".").resolve()

doc = root / "docs" / "dev" / "student-workflow-ux-reset-charter-no-build-no-zip-no-share-no-delivery.md"
check_py = root / "scripts" / "dev" / "check-student-workflow-ux-reset-charter-no-build-no-zip-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-student-workflow-ux-reset-charter-no-build-no-zip-no-share-no-delivery.ps1"

for path, label in [
    (doc, "DOC"),
    (check_py, "CHECK_PY"),
    (check_ps1, "CHECK_PS1"),
]:
    if not path.exists():
        raise SystemExit(f"FAILED_V0843_{label}_MISSING={path}")

doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_terms = [
    "v0.8.43 Student workflow UX reset charter",
    "Voila! — Documentele tale, lecții clare",
    "15-year-old student",
    "adult without technical knowledge",
    "Încarcă documentul",
    "Revizuiește documentul",
    "Alege ce merită învățat",
    "Creează lecția",
    "Învață",
    "Exersează pentru examen",
    "OCR Review, Crop Editor, and Manual Learning Evidence must become one learner-facing workflow",
    "`Revizuire document`",
    "full document OCR text review",
    "LanguageTool correction review",
    "formula review",
    "image/crop review",
    "diagram/drawing review",
    "manual explanation entry",
    "All engines should run in the background",
    "Corectează",
    "Acceptă",
    "Ignoră",
    "Adaugă la lecție",
    "Explică pe înțeles",
    "Gata pentru studiu",
    "Text detectat",
    "Sugestii de corectare",
    "Selectează zona din pagină",
    "Spune ce reprezintă",
    "Salvează pentru lecție",
    "Titlu scurt",
    "Ce este asta?",
    "Text verificat",
    "Explicație pe înțeles",
    "Pagina sursă",
    "Definiție",
    "Formulă",
    "Exemplu",
    "Teoremă",
    "Diagramă",
    "Imagine",
    "Tabel",
    "Clean Study mode",
    "Întrebare",
    "Răspuns",
    "Explicație",
    "Sursa: pagina X",
    "manual_study_default_enabled",
    "source_evidence_id",
    "manual_study_item_id",
    "source_bbox",
    "Diagnostic tehnic",
    "Language consistency",
    "Română",
    "English",
    "No mixed RO/EN learner flow",
    "Background engines",
    "Se citește documentul",
    "Se verifică textul",
    "Se caută formule și imagini",
    "Alege ce intră în lecție",
    "Lecția este gata pentru studiu",
    "No build.",
    "No ZIP.",
    "No package rebuild.",
    "No OneDrive copy.",
    "No share.",
    "No delivery.",
    "No distribution.",
    "No public release.",
    "No route changes.",
    "No POST endpoints.",
    "No Study behavior change.",
    "No Progress write.",
    "No answer marking.",
    "No OCR rewrite.",
    "No Formula OCR.",
    "No crop writing.",
    "v0.8.44 — Design shell for `Revizuire document`",
    "v0.8.48 — Clean Study mode",
    "We do not throw away the engines.",
    "We hide the engines behind a simple, guided, learner-first workflow.",
]

missing = [term for term in required_terms if term not in doc_text]
if missing:
    raise SystemExit("FAILED_V0843_DOC_REQUIRED_TERMS_MISSING=" + json.dumps(missing, ensure_ascii=False))

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/student-workflow-ux-reset-charter-no-build-no-zip-no-share-no-delivery.md",
    "scripts/dev/check-student-workflow-ux-reset-charter-no-build-no-zip-no-share-no-delivery.py",
    "scripts/dev/check-student-workflow-ux-reset-charter-no-build-no-zip-no-share-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0843_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

for forbidden in [
    "services/api/web_app.py",
    "services/api/",
    "data/output/",
    "data/input/",
]:
    if any(path.replace("\\", "/").startswith(forbidden) for path in changed):
        raise SystemExit("FAILED_V0843_FORBIDDEN_RUNTIME_OR_DATA_CHANGE=" + forbidden)

evidence_dir = Path(r"D:\dev\tester-runs\v0843-student-workflow-ux-reset-charter-no-build-no-zip-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_43_STUDENT_WORKFLOW_UX_RESET_CHARTER_CHECK": "PASS",
    "charter_created": True,
    "product_positioning": "Voila! — Documentele tale, lecții clare",
    "target_student_or_nontechnical_adult": True,
    "learner_workflow_defined": True,
    "review_document_unifies_ocr_crop_manual_evidence": True,
    "background_engines_required": True,
    "ocr_text_and_languagetool_in_review_scope": True,
    "formula_diagram_crop_in_review_scope": True,
    "manual_explanations_friendly_form_required": True,
    "clean_study_mode_required": True,
    "diagnostic_boundary_defined": True,
    "language_consistency_ro_or_en_required": True,
    "mixed_ro_en_learner_flow_disallowed": True,
    "ui_implementation_performed": False,
    "web_app_changed": False,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "study_changed": False,
    "progress_write_added": False,
    "answer_marking_added": False,
    "ocr_rewrite_performed": False,
    "formula_ocr_performed": False,
    "crop_file_written": False,
    "build_performed": False,
    "package_rebuild_performed": False,
    "new_zip_created": False,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "STUDENT_WORKFLOW_UX_RESET_CHARTER": "PASS_DOC_ONLY_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_NEW_UI_DESIGN_AND_RETEST",
    "POLICY": "student_workflow_ux_reset_charter_no_build_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.44-owner-local-review-document-shell-design-no-build-no-zip-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.43-STUDENT-WORKFLOW-UX-RESET-CHARTER-CHECK.json"
out_md = evidence_dir / "V0.8.43-STUDENT-WORKFLOW-UX-RESET-CHARTER-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.43 Student workflow UX reset charter — no build/no ZIP/no share/no delivery",
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
