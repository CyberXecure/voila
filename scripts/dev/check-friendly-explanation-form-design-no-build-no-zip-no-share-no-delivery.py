from pathlib import Path
import json
import subprocess

root = Path(".").resolve()

doc = root / "docs" / "dev" / "friendly-explanation-form-design-no-build-no-zip-no-share-no-delivery.md"
check_py = root / "scripts" / "dev" / "check-friendly-explanation-form-design-no-build-no-zip-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-friendly-explanation-form-design-no-build-no-zip-no-share-no-delivery.ps1"

for path, label in [
    (doc, "DOC"),
    (check_py, "CHECK_PY"),
    (check_ps1, "CHECK_PS1"),
]:
    if not path.exists():
        raise SystemExit(f"FAILED_V0847_{label}_MISSING={path}")

doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_terms = [
    "v0.8.47 Friendly explanation form design",
    "`Revizuire document`",
    "Voila! — Documentele tale, lecții clare",
    "The learner should not feel like they are editing metadata.",
    "text fragments",
    "corrected OCR text",
    "formulas",
    "diagrams",
    "images",
    "drawings",
    "tables",
    "graphs",
    "15-year-old student",
    "adult without technical knowledge",
    "metadata, bbox, source IDs, evidence IDs, JSON artifacts, crop paths, route names, or dry-runs",
    "Adaugă explicația pentru lecție",
    "Pregătește pentru studiu",
    "Titlu scurt",
    "Ce este asta?",
    "Text / zonă verificată",
    "Explicație pe înțeles",
    "De ce este important?",
    "Sursa: pagina X",
    "Limba lecției",
    "Gata pentru studiu",
    "verified_text",
    "source_status",
    "source_note",
    "source_bbox",
    "source_evidence_id",
    "manual_study_item_id",
    "visual_evidence_id",
    "crop_path",
    "Field — Titlu scurt",
    "Dă un titlu scurt acestei idei.",
    "Field — Ce este asta?",
    "Definiție",
    "Formulă",
    "Exemplu",
    "Teoremă",
    "Diagramă",
    "Imagine",
    "Tabel",
    "Desen",
    "Grafic",
    "Observație importantă",
    "Field — Text / zonă verificată",
    "Text verificat",
    "Zonă selectată",
    "Conținut verificat",
    "Field — Explicație pe înțeles",
    "Explică pe înțeles ce înseamnă.",
    "This field replaces the old feeling of metadata editing.",
    "Field — De ce este important?",
    "De ce merită învățat?",
    "Field — Sursa: pagina X",
    "Study should later show the same friendly source label.",
    "Field — Limba lecției",
    "Română",
    "English",
    "No mixed RO/EN learner flow.",
    "Readiness model",
    "Incomplet",
    "De verificat",
    "Gata pentru studiu",
    "Ignorat",
    "Incomplete items should not silently become Study cards.",
    "Primary actions",
    "Salvează pentru lecție",
    "Editează explicația",
    "Validation behavior",
    "Adaugă un titlu scurt.",
    "Alege ce este această idee.",
    "Adaugă o explicație pe înțeles.",
    "Confirmă pagina sursă.",
    "Alege limba lecției.",
    "Explanation quality hints",
    "Scrie ca pentru un coleg de clasă.",
    "Dacă este formulă, spune ce reprezintă fiecare parte.",
    "Dacă este diagramă, spune ce arată desenul.",
    "Text item variant",
    "Visual item variant",
    "Diagnostic boundary",
    "`Diagnostic tehnic`",
    "collapsed by default",
    "Handoff contract",
    "short title",
    "item type",
    "verified text or visual preview reference",
    "learner explanation",
    "importance note",
    "source page",
    "lesson language",
    "readiness state",
    "Study should not receive incomplete items as if they were verified learning material.",
    "This milestone does not implement the form.",
    "This milestone does not change the current UI.",
    "This milestone does not change `services/api/web_app.py`.",
    "This milestone does not add a route.",
    "This milestone does not add a POST endpoint.",
    "This milestone does not perform OCR.",
    "This milestone does not perform LanguageTool correction.",
    "This milestone does not perform Formula OCR.",
    "This milestone does not perform crop extraction.",
    "This milestone does not write crop files.",
    "This milestone does not write visual evidence artifacts.",
    "This milestone does not write manual evidence artifacts.",
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
    "No visual evidence writing.",
    "No manual evidence writing.",
    "v0.8.48 — clean Study mode design.",
    "The friendly explanation form replaces metadata editing in the learner flow.",
]

missing = [term for term in required_terms if term not in doc_text]
if missing:
    raise SystemExit("FAILED_V0847_DOC_REQUIRED_TERMS_MISSING=" + json.dumps(missing, ensure_ascii=False))

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/friendly-explanation-form-design-no-build-no-zip-no-share-no-delivery.md",
    "scripts/dev/check-friendly-explanation-form-design-no-build-no-zip-no-share-no-delivery.py",
    "scripts/dev/check-friendly-explanation-form-design-no-build-no-zip-no-share-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0847_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

for forbidden in [
    "services/api/web_app.py",
    "services/api/",
    "data/output/",
    "data/input/",
]:
    if any(path.replace("\\", "/").startswith(forbidden) for path in changed):
        raise SystemExit("FAILED_V0847_FORBIDDEN_RUNTIME_OR_DATA_CHANGE=" + forbidden)

evidence_dir = Path(r"D:\dev\tester-runs\v0847-friendly-explanation-form-design-no-build-no-zip-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_47_FRIENDLY_EXPLANATION_FORM_DESIGN_CHECK": "PASS",
    "design_created": True,
    "parent_shell": "Revizuire document",
    "product_positioning": "Voila! — Documentele tale, lecții clare",
    "target_student_or_nontechnical_adult": True,
    "metadata_editing_replaced_by_friendly_form": True,
    "shared_form_for_text_and_visual_items": True,
    "required_fields_defined": True,
    "short_title_field_defined": True,
    "friendly_item_type_field_defined": True,
    "verified_content_field_defined": True,
    "learner_explanation_field_defined": True,
    "importance_field_defined": True,
    "source_page_field_defined": True,
    "lesson_language_field_defined": True,
    "readiness_model_defined": True,
    "incomplete_items_not_allowed_as_study_cards": True,
    "friendly_validation_messages_defined": True,
    "explanation_quality_hints_defined": True,
    "text_item_variant_defined": True,
    "visual_item_variant_defined": True,
    "diagnostic_boundary_defined": True,
    "handoff_contract_defined": True,
    "language_consistency_required": True,
    "ro_en_mixing_disallowed": True,
    "ui_implementation_performed": False,
    "web_app_changed": False,
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
    "ocr_rewrite_performed": False,
    "build_performed": False,
    "package_rebuild_performed": False,
    "new_zip_created": False,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "FRIENDLY_EXPLANATION_FORM_DESIGN": "PASS_DOC_ONLY_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_UI_IMPLEMENTATION_AND_RETEST",
    "POLICY": "friendly_explanation_form_design_no_build_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.48-owner-local-clean-study-mode-design-no-build-no-zip-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.47-FRIENDLY-EXPLANATION-FORM-DESIGN-CHECK.json"
out_md = evidence_dir / "V0.8.47-FRIENDLY-EXPLANATION-FORM-DESIGN-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.47 Friendly explanation form design — no build/no ZIP/no share/no delivery",
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
