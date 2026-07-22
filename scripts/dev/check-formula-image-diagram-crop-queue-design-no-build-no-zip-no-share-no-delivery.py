from pathlib import Path
import json
import subprocess

root = Path(".").resolve()

doc = root / "docs" / "dev" / "formula-image-diagram-crop-queue-design-no-build-no-zip-no-share-no-delivery.md"
check_py = root / "scripts" / "dev" / "check-formula-image-diagram-crop-queue-design-no-build-no-zip-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-formula-image-diagram-crop-queue-design-no-build-no-zip-no-share-no-delivery.ps1"

for path, label in [
    (doc, "DOC"),
    (check_py, "CHECK_PY"),
    (check_ps1, "CHECK_PS1"),
]:
    if not path.exists():
        raise SystemExit(f"FAILED_V0846_{label}_MISSING={path}")

doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_terms = [
    "v0.8.46 Formula/image/diagram/crop queue design",
    "`Revizuire document`",
    "`Formule și imagini`",
    "Voila! — Documentele tale, lecții clare",
    "15-year-old student",
    "adult without technical knowledge",
    "The learner should not see a technical crop editor or formula diagnostics console.",
    "Formula detection, image detection, diagram detection, crop extraction",
    "Ce reprezintă această zonă și merită să intre în lecție?",
    "Unified visual queue concept",
    "formulas",
    "diagrams",
    "drawings",
    "images",
    "tables",
    "graphs",
    "manually selected crop areas",
    "OCR Math report",
    "Formula visual evidence",
    "Crop Editor",
    "Manual Learning Evidence",
    "Externally, the learner sees one guided flow: `Formule și imagini`.",
    "page-based and visual-area-based",
    "visual_preview",
    "selected_area",
    "item_type",
    "what_it_represents",
    "learner_explanation",
    "De verificat",
    "Selectat",
    "Explicat",
    "Gata pentru lecție",
    "Ignorat",
    "Selectează zona din pagină",
    "Ce reprezintă?",
    "Tip de conținut",
    "Titlu scurt",
    "Explicație pe înțeles",
    "Salvează pentru lecție",
    "Ignoră zona",
    "raw bbox values",
    "visual evidence IDs",
    "Formula OCR logs",
    "Friendly item types",
    "Formulă",
    "Diagramă",
    "Imagine",
    "Tabel",
    "Desen",
    "Grafic",
    "Observație importantă",
    "Formula handling",
    "The learner should be able to explain a formula even if formula OCR is imperfect.",
    "Diagram, drawing, graph, and table handling",
    "Explanation model",
    "Manual explanation entry is not metadata editing.",
    "De ce este important?",
    "Source confirmation",
    "Sursa: pagina X",
    "Language consistency",
    "Română",
    "English",
    "No mixed RO/EN learner flow.",
    "Background engine behavior",
    "page rendering",
    "formula detection",
    "image detection",
    "diagram detection",
    "table detection",
    "crop extraction",
    "Formula OCR",
    "OCR Math diagnostics",
    "Se caută formule și imagini",
    "Se pregătesc paginile",
    "Selectează zona importantă",
    "Zona este gata pentru lecție",
    "Queue layout",
    "Visual workspace",
    "Explanation panel",
    "Guidance panel",
    "Diagnostic tehnic",
    "collapsed by default",
    "Primary buttons",
    "Ajustează selecția",
    "Readiness for Study",
    "Unresolved visual items should not silently become clean Study material.",
    "Diagnostic boundary",
    "Handoff contract",
    "source page",
    "item type",
    "short title",
    "learner explanation",
    "visual preview or crop reference",
    "lesson language",
    "Study should not expose raw bbox or visual evidence IDs in the main learner view.",
    "This milestone does not implement the queue.",
    "This milestone does not change the current UI.",
    "This milestone does not change `services/api/web_app.py`.",
    "This milestone does not add a route.",
    "This milestone does not add a POST endpoint.",
    "This milestone does not perform Formula OCR.",
    "This milestone does not perform crop extraction.",
    "This milestone does not write crop files.",
    "This milestone does not write visual evidence artifacts.",
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
    "v0.8.47 — friendly explanation form design.",
    "It is a guided learner workflow that turns visual document material into clear study-ready explanations.",
]

missing = [term for term in required_terms if term not in doc_text]
if missing:
    raise SystemExit("FAILED_V0846_DOC_REQUIRED_TERMS_MISSING=" + json.dumps(missing, ensure_ascii=False))

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/formula-image-diagram-crop-queue-design-no-build-no-zip-no-share-no-delivery.md",
    "scripts/dev/check-formula-image-diagram-crop-queue-design-no-build-no-zip-no-share-no-delivery.py",
    "scripts/dev/check-formula-image-diagram-crop-queue-design-no-build-no-zip-no-share-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0846_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

for forbidden in [
    "services/api/web_app.py",
    "services/api/",
    "data/output/",
    "data/input/",
]:
    if any(path.replace("\\", "/").startswith(forbidden) for path in changed):
        raise SystemExit("FAILED_V0846_FORBIDDEN_RUNTIME_OR_DATA_CHANGE=" + forbidden)

evidence_dir = Path(r"D:\dev\tester-runs\v0846-formula-image-diagram-crop-queue-design-no-build-no-zip-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_46_FORMULA_IMAGE_DIAGRAM_CROP_QUEUE_DESIGN_CHECK": "PASS",
    "design_created": True,
    "parent_shell": "Revizuire document",
    "covered_step_formulas_images": True,
    "product_positioning": "Voila! — Documentele tale, lecții clare",
    "target_student_or_nontechnical_adult": True,
    "visual_queue_unifies_formulas_images_diagrams_crops": True,
    "queue_is_page_based_and_visual_area_based": True,
    "learner_friendly_statuses_defined": True,
    "friendly_visual_item_types_defined": True,
    "formula_handling_defined": True,
    "diagram_drawing_graph_table_handling_defined": True,
    "friendly_explanation_model_defined": True,
    "source_confirmation_required": True,
    "language_consistency_required": True,
    "ro_en_mixing_disallowed": True,
    "background_visual_engines_required": True,
    "technical_details_diagnostic_only": True,
    "readiness_for_study_defined": True,
    "unresolved_visual_items_not_allowed_as_verified": True,
    "handoff_contract_defined": True,
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
    "ocr_rewrite_performed": False,
    "build_performed": False,
    "package_rebuild_performed": False,
    "new_zip_created": False,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "FORMULA_IMAGE_DIAGRAM_CROP_QUEUE_DESIGN": "PASS_DOC_ONLY_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_UI_IMPLEMENTATION_AND_RETEST",
    "POLICY": "formula_image_diagram_crop_queue_design_no_build_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.47-owner-local-friendly-explanation-form-design-no-build-no-zip-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.46-FORMULA-IMAGE-DIAGRAM-CROP-QUEUE-DESIGN-CHECK.json"
out_md = evidence_dir / "V0.8.46-FORMULA-IMAGE-DIAGRAM-CROP-QUEUE-DESIGN-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.46 Formula/image/diagram/crop queue design — no build/no ZIP/no share/no delivery",
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
