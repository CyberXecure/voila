from pathlib import Path
import json
import subprocess

root = Path(".").resolve()

doc = root / "docs" / "dev" / "clean-study-mode-design-no-build-no-zip-no-share-no-delivery.md"
check_py = root / "scripts" / "dev" / "check-clean-study-mode-design-no-build-no-zip-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-clean-study-mode-design-no-build-no-zip-no-share-no-delivery.ps1"

for path, label in [
    (doc, "DOC"),
    (check_py, "CHECK_PY"),
    (check_ps1, "CHECK_PS1"),
]:
    if not path.exists():
        raise SystemExit(f"FAILED_V0848_{label}_MISSING={path}")

doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_terms = [
    "v0.8.48 Clean Study mode design",
    "Voila! — Documentele tale, lecții clare",
    "technical Manual Study debug page",
    "15-year-old student",
    "adult without technical knowledge",
    "metadata, bbox, source IDs, evidence IDs, JSON artifacts, crop paths, route names, dry-runs, fallback states, package policy markers, or delivery flags",
    "Revizuire document",
    "Text detectat",
    "Corecturi sugerate",
    "Formule și imagini",
    "Noțiuni importante",
    "Gata pentru studiu",
    "Ce trebuie să învăț acum din document?",
    "Învață lecția",
    "Study curat",
    "Parcurge noțiunile verificate din document, una câte una.",
    "current card",
    "total cards",
    "lesson language",
    "source page",
    "question",
    "answer",
    "explanation",
    "optional visual preview",
    "Clean Study card structure",
    "Tip",
    "Titlu scurt",
    "Întrebare",
    "Răspuns",
    "Explicație pe înțeles",
    "Sursa: pagina X",
    "manual_study_default_enabled",
    "fallback_legacy_study_available",
    "manual_study_connected_to_real_study",
    "source_evidence_id",
    "manual_study_item_id",
    "visual_evidence_id",
    "source_bbox",
    "bbox",
    "crop_path",
    "artifact path",
    "JSON file name",
    "route name",
    "package policy marker",
    "Card types",
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
    "Text card design",
    "Visual card design",
    "Question and answer model",
    "Arată răspunsul",
    "Ascunde răspunsul",
    "Answer reveal behavior",
    "The answer area should be read-only in Study.",
    "Editing should happen back in `Revizuire document`",
    "Source trust",
    "Revino la sursă",
    "Language consistency",
    "Română",
    "English",
    "No mixed RO/EN learner flow.",
    "Navigation model",
    "Card X din Y",
    "Progress model",
    "This milestone does not design grading, scoring, mastery, or Progress writes.",
    "Exam practice handoff",
    "Exersează pentru examen",
    "Empty and warning states",
    "Nu ai încă noțiuni gata pentru studiu.",
    "Unele noțiuni mai trebuie verificate înainte să apară în Study.",
    "Diagnostic boundary",
    "`Diagnostic tehnic`",
    "collapsed by default",
    "Clean Study handoff contract",
    "readiness state",
    "Clean Study should reject or hide items that are:",
    "incomplete",
    "unresolved",
    "ignored",
    "missing explanation",
    "missing source page",
    "wrong lesson language",
    "This milestone does not implement Clean Study.",
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
    "This milestone does not write Progress.",
    "This milestone does not mark answers.",
    "This milestone does not create Study cards.",
    "This milestone does not change Study behavior.",
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
    "v0.8.49 — owner-local learner workflow implementation preflight.",
    "Clean Study is not a technical Manual Study debug surface.",
    "Clean Study is the learner-facing place where reviewed document material becomes a clear lesson.",
]

missing = [term for term in required_terms if term not in doc_text]
if missing:
    raise SystemExit("FAILED_V0848_DOC_REQUIRED_TERMS_MISSING=" + json.dumps(missing, ensure_ascii=False))

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/clean-study-mode-design-no-build-no-zip-no-share-no-delivery.md",
    "scripts/dev/check-clean-study-mode-design-no-build-no-zip-no-share-no-delivery.py",
    "scripts/dev/check-clean-study-mode-design-no-build-no-zip-no-share-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0848_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

for forbidden in [
    "services/api/web_app.py",
    "services/api/",
    "data/output/",
    "data/input/",
]:
    if any(path.replace("\\", "/").startswith(forbidden) for path in changed):
        raise SystemExit("FAILED_V0848_FORBIDDEN_RUNTIME_OR_DATA_CHANGE=" + forbidden)

evidence_dir = Path(r"D:\dev\tester-runs\v0848-clean-study-mode-design-no-build-no-zip-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_48_CLEAN_STUDY_MODE_DESIGN_CHECK": "PASS",
    "design_created": True,
    "clean_study_mode_defined": True,
    "product_positioning": "Voila! — Documentele tale, lecții clare",
    "target_student_or_nontechnical_adult": True,
    "study_is_clean_learner_surface": True,
    "manual_study_debug_surface_rejected": True,
    "only_reviewed_material_should_reach_study": True,
    "main_study_screen_defined": True,
    "clean_study_card_structure_defined": True,
    "friendly_card_types_defined": True,
    "text_card_design_defined": True,
    "visual_card_design_defined": True,
    "question_answer_model_defined": True,
    "answer_reveal_model_defined": True,
    "answer_area_read_only_required": True,
    "source_trust_visible": True,
    "language_consistency_required": True,
    "ro_en_mixing_disallowed": True,
    "navigation_model_defined": True,
    "raw_anchor_lists_disallowed": True,
    "light_progress_model_defined": True,
    "progress_writes_out_of_scope": True,
    "exam_practice_handoff_defined": True,
    "empty_warning_states_defined": True,
    "diagnostic_boundary_defined": True,
    "handoff_contract_defined": True,
    "incomplete_unresolved_ignored_items_hidden_or_rejected": True,
    "technical_ids_hidden_from_main_flow": True,
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
    "CLEAN_STUDY_MODE_DESIGN": "PASS_DOC_ONLY_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_UI_IMPLEMENTATION_AND_RETEST",
    "POLICY": "clean_study_mode_design_no_build_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.49-owner-local-learner-workflow-implementation-preflight-no-build-no-zip-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.48-CLEAN-STUDY-MODE-DESIGN-CHECK.json"
out_md = evidence_dir / "V0.8.48-CLEAN-STUDY-MODE-DESIGN-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.48 Clean Study mode design — no build/no ZIP/no share/no delivery",
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
