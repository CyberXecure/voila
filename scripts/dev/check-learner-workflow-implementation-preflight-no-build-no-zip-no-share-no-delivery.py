from pathlib import Path
import json
import subprocess

root = Path(".").resolve()

doc = root / "docs" / "dev" / "learner-workflow-implementation-preflight-no-build-no-zip-no-share-no-delivery.md"
check_py = root / "scripts" / "dev" / "check-learner-workflow-implementation-preflight-no-build-no-zip-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-learner-workflow-implementation-preflight-no-build-no-zip-no-share-no-delivery.ps1"

for path, label in [
    (doc, "DOC"),
    (check_py, "CHECK_PY"),
    (check_ps1, "CHECK_PS1"),
]:
    if not path.exists():
        raise SystemExit(f"FAILED_V0849_{label}_MISSING={path}")

required_design_docs = [
    root / "docs" / "dev" / "student-workflow-ux-reset-charter-no-build-no-zip-no-share-no-delivery.md",
    root / "docs" / "dev" / "review-document-shell-design-no-build-no-zip-no-share-no-delivery.md",
    root / "docs" / "dev" / "ocr-languagetool-review-queue-design-no-build-no-zip-no-share-no-delivery.md",
    root / "docs" / "dev" / "formula-image-diagram-crop-queue-design-no-build-no-zip-no-share-no-delivery.md",
    root / "docs" / "dev" / "friendly-explanation-form-design-no-build-no-zip-no-share-no-delivery.md",
    root / "docs" / "dev" / "clean-study-mode-design-no-build-no-zip-no-share-no-delivery.md",
]

missing_design_docs = [str(p) for p in required_design_docs if not p.exists()]
if missing_design_docs:
    raise SystemExit("FAILED_V0849_REQUIRED_DESIGN_DOCS_MISSING=" + json.dumps(missing_design_docs, ensure_ascii=False))

doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_terms = [
    "v0.8.49 Learner workflow implementation preflight",
    "v0.8.43 — Student workflow UX reset charter",
    "v0.8.44 — Review Document shell design",
    "v0.8.45 — OCR + LanguageTool review queue design",
    "v0.8.46 — Formula/image/diagram/crop queue design",
    "v0.8.47 — Friendly explanation form design",
    "v0.8.48 — Clean Study mode design",
    "Voila! — Documentele tale, lecții clare",
    "Încarcă documentul",
    "Revizuiește documentul",
    "Alege ce merită învățat",
    "Creează lecția",
    "Învață",
    "Exersează pentru examen",
    "additive guided surface first",
    "Revizuire document",
    "Text detectat",
    "Corecturi sugerate",
    "Formule și imagini",
    "Noțiuni importante",
    "Gata pentru studiu",
    "Învață lecția",
    "Route strategy",
    "`/review-document?pdf={pdf_name}`",
    "`/review-document/{course_id}`",
    "v0.8.50-owner-local-review-document-shell-read-only-first-slice-no-build-no-zip-no-share-no-delivery",
    "add read-only learner shell",
    "do not write data",
    "do not run OCR",
    "do not run LanguageTool",
    "do not run crop extraction",
    "do not change Study behavior",
    "Implementation slice order",
    "read-only `Revizuire document` shell",
    "Course Tools link to learner shell",
    "read-only Text detectat queue from existing OCR artifacts",
    "read-only Corecturi sugerate queue from existing LanguageTool artifacts",
    "read-only Formule și imagini queue from existing visual/crop artifacts",
    "friendly explanation form read-only/static draft shell",
    "safe local save for explanation drafts",
    "clean Study read-only preview",
    "owner personal workflow smoke",
    "File strategy",
    "services/api/web_app.py",
    "Safety guardrails",
    "no build",
    "no ZIP",
    "no package rebuild",
    "no OneDrive copy",
    "no share",
    "no delivery",
    "no distribution",
    "no public release",
    "Existing engines",
    "OCR text artifacts",
    "LanguageTool correction artifacts",
    "OCR Math report artifacts",
    "visual evidence artifacts",
    "manual learning evidence artifacts",
    "manual learning pack preview",
    "manual study items preview",
    "Background engine rule",
    "Se citește documentul",
    "Se extrage textul",
    "Se verifică textul",
    "Se caută formule și imagini",
    "Pregătim noțiunile importante",
    "Lecția este gata pentru studiu",
    "Language rule",
    "Română",
    "English",
    "No mixed RO/EN learner flow.",
    "Diagnostic boundary",
    "`Diagnostic tehnic`",
    "collapsed by default",
    "Study protection",
    "existing Study behavior must remain protected",
    "Manual Study fallback must remain protected",
    "no Progress writes",
    "no answer marking",
    "Data write protection",
    "Early implementation slices should be read-only.",
    "Test strategy",
    "technical labels are hidden from the main learner surface",
    "Manual smoke strategy",
    "Home → Course Tools → Revizuire document → Text detectat → Corecturi sugerate → Formule și imagini → Noțiuni importante → Gata pentru studiu → Study curat",
    "PACKAGE_READINESS=BLOCKED_PENDING_UI_IMPLEMENTATION_AND_RETEST",
    "This milestone does not implement the learner shell.",
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
    "v0.8.50 — owner-local Review Document shell read-only first slice.",
    "The first code slice must be additive, read-only, local, guarded, and learner-facing.",
]

missing = [term for term in required_terms if term not in doc_text]
if missing:
    raise SystemExit("FAILED_V0849_DOC_REQUIRED_TERMS_MISSING=" + json.dumps(missing, ensure_ascii=False))

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/learner-workflow-implementation-preflight-no-build-no-zip-no-share-no-delivery.md",
    "scripts/dev/check-learner-workflow-implementation-preflight-no-build-no-zip-no-share-no-delivery.py",
    "scripts/dev/check-learner-workflow-implementation-preflight-no-build-no-zip-no-share-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0849_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

for forbidden in [
    "services/api/web_app.py",
    "services/api/",
    "data/output/",
    "data/input/",
]:
    if any(path.replace("\\", "/").startswith(forbidden) for path in changed):
        raise SystemExit("FAILED_V0849_FORBIDDEN_RUNTIME_OR_DATA_CHANGE=" + forbidden)

evidence_dir = Path(r"D:\dev\tester-runs\v0849-learner-workflow-implementation-preflight-no-build-no-zip-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_49_LEARNER_WORKFLOW_IMPLEMENTATION_PREFLIGHT_CHECK": "PASS",
    "preflight_created": True,
    "depends_on_v0843_to_v0848_design_chain": True,
    "product_positioning": "Voila! — Documentele tale, lecții clare",
    "learner_workflow_confirmed": True,
    "implementation_principle_additive_guided_surface_first": True,
    "route_strategy_defined": True,
    "candidate_route_review_document_pdf_defined": True,
    "candidate_route_review_document_course_id_defined": True,
    "first_implementation_slice_recommended": "v0.8.50-owner-local-review-document-shell-read-only-first-slice-no-build-no-zip-no-share-no-delivery",
    "implementation_slice_order_defined": True,
    "file_strategy_defined": True,
    "safety_guardrails_defined": True,
    "existing_engines_preserved": True,
    "background_engine_rule_defined": True,
    "language_rule_defined": True,
    "ro_en_mixing_disallowed": True,
    "diagnostic_boundary_defined": True,
    "study_protection_defined": True,
    "data_write_protection_defined": True,
    "test_strategy_defined": True,
    "manual_smoke_strategy_defined": True,
    "package_readiness": "BLOCKED_PENDING_UI_IMPLEMENTATION_AND_RETEST",
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
    "LEARNER_WORKFLOW_IMPLEMENTATION_PREFLIGHT": "PASS_DOC_ONLY_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_UI_IMPLEMENTATION_AND_RETEST",
    "POLICY": "learner_workflow_implementation_preflight_no_build_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.50-owner-local-review-document-shell-read-only-first-slice-no-build-no-zip-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.49-LEARNER-WORKFLOW-IMPLEMENTATION-PREFLIGHT-CHECK.json"
out_md = evidence_dir / "V0.8.49-LEARNER-WORKFLOW-IMPLEMENTATION-PREFLIGHT-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.49 Learner workflow implementation preflight — no build/no ZIP/no share/no delivery",
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
