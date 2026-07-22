from pathlib import Path
import json
import subprocess

root = Path(".").resolve()

doc = root / "docs" / "dev" / "review-document-shell-design-no-build-no-zip-no-share-no-delivery.md"
check_py = root / "scripts" / "dev" / "check-review-document-shell-design-no-build-no-zip-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-review-document-shell-design-no-build-no-zip-no-share-no-delivery.ps1"

for path, label in [
    (doc, "DOC"),
    (check_py, "CHECK_PY"),
    (check_ps1, "CHECK_PS1"),
]:
    if not path.exists():
        raise SystemExit(f"FAILED_V0844_{label}_MISSING={path}")

doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_terms = [
    "v0.8.44 Review Document shell design",
    "`Revizuire document`",
    "Voila! — Documentele tale, lecții clare",
    "15-year-old student",
    "adult without technical knowledge",
    "Text detectat",
    "Corecturi sugerate",
    "Formule și imagini",
    "Noțiuni importante",
    "Gata pentru studiu",
    "OCR Review",
    "Crop Editor",
    "Manual Learning Evidence",
    "Learning Pack dry-run",
    "Manual Study Items preview",
    "Internally, those systems can still exist.",
    "Externally, the learner sees one flow: `Revizuire document`.",
    "Step 1 — Text detectat",
    "page-based blocks",
    "Acceptă textul",
    "Corectează textul",
    "Step 2 — Corecturi sugerate",
    "LanguageTool suggestions",
    "Acceptă sugestia",
    "Păstrează textul",
    "Step 3 — Formule și imagini",
    "formula review",
    "image review",
    "diagram review",
    "crop review",
    "Selectează zona din pagină",
    "Ce reprezintă?",
    "Explicație pe înțeles",
    "Salvează pentru lecție",
    "raw bbox values",
    "Step 4 — Noțiuni importante",
    "Adaugă la lecție",
    "Titlu scurt",
    "Text verificat",
    "Pagina sursă",
    "Gata pentru studiu",
    "accepted_owner_verified",
    "manual_learning_evidence.json",
    "manual_study_items.preview.json",
    "source_evidence_id",
    "manual_study_item_id",
    "Step 5 — Gata pentru studiu",
    "Creează lecția",
    "Învață acum",
    "Exersează pentru examen",
    "Limba lecției",
    "Română",
    "English",
    "should not mix RO and EN",
    "Background engines",
    "OCR",
    "LanguageTool",
    "formula detection",
    "crop extraction",
    "Se citește documentul",
    "Se verifică textul",
    "Se caută formule și imagini",
    "Lecția este gata pentru studiu",
    "top progress stepper",
    "main review workspace",
    "guidance panel",
    "Diagnostic tehnic",
    "collapsed by default",
    "Study handoff contract",
    "question",
    "answer",
    "explanation",
    "source page",
    "lesson language",
    "This milestone does not implement the shell.",
    "This milestone does not change the current UI.",
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
    "v0.8.45 — learner-facing OCR text + LanguageTool review queue design.",
    "v0.8.48 — clean Study mode design.",
    "It hides technical engines behind a guided learner-first workflow.",
]

missing = [term for term in required_terms if term not in doc_text]
if missing:
    raise SystemExit("FAILED_V0844_DOC_REQUIRED_TERMS_MISSING=" + json.dumps(missing, ensure_ascii=False))

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/review-document-shell-design-no-build-no-zip-no-share-no-delivery.md",
    "scripts/dev/check-review-document-shell-design-no-build-no-zip-no-share-no-delivery.py",
    "scripts/dev/check-review-document-shell-design-no-build-no-zip-no-share-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0844_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

for forbidden in [
    "services/api/web_app.py",
    "services/api/",
    "data/output/",
    "data/input/",
]:
    if any(path.replace("\\", "/").startswith(forbidden) for path in changed):
        raise SystemExit("FAILED_V0844_FORBIDDEN_RUNTIME_OR_DATA_CHANGE=" + forbidden)

evidence_dir = Path(r"D:\dev\tester-runs\v0844-review-document-shell-design-no-build-no-zip-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_44_REVIEW_DOCUMENT_SHELL_DESIGN_CHECK": "PASS",
    "design_created": True,
    "shell_name": "Revizuire document",
    "product_positioning": "Voila! — Documentele tale, lecții clare",
    "target_student_or_nontechnical_adult": True,
    "learner_steps_defined": True,
    "step_text_detected_defined": True,
    "step_languagetool_corrections_defined": True,
    "step_formulas_images_crops_defined": True,
    "step_important_concepts_defined": True,
    "step_ready_for_study_defined": True,
    "ocr_review_crop_editor_manual_evidence_unified_in_shell": True,
    "language_selector_required": True,
    "ro_en_mixing_disallowed": True,
    "background_engines_hidden": True,
    "diagnostic_boundary_defined": True,
    "study_handoff_contract_defined": True,
    "friendly_labels_defined": True,
    "technical_labels_hidden_from_main_flow": True,
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
    "REVIEW_DOCUMENT_SHELL_DESIGN": "PASS_DOC_ONLY_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_UI_IMPLEMENTATION_AND_RETEST",
    "POLICY": "review_document_shell_design_no_build_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.45-owner-local-ocr-languagetool-review-queue-design-no-build-no-zip-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.44-REVIEW-DOCUMENT-SHELL-DESIGN-CHECK.json"
out_md = evidence_dir / "V0.8.44-REVIEW-DOCUMENT-SHELL-DESIGN-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.44 Review Document shell design — no build/no ZIP/no share/no delivery",
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
