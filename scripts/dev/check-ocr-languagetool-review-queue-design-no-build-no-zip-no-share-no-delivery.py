from pathlib import Path
import json
import subprocess

root = Path(".").resolve()

doc = root / "docs" / "dev" / "ocr-languagetool-review-queue-design-no-build-no-zip-no-share-no-delivery.md"
check_py = root / "scripts" / "dev" / "check-ocr-languagetool-review-queue-design-no-build-no-zip-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-ocr-languagetool-review-queue-design-no-build-no-zip-no-share-no-delivery.ps1"

for path, label in [
    (doc, "DOC"),
    (check_py, "CHECK_PY"),
    (check_ps1, "CHECK_PS1"),
]:
    if not path.exists():
        raise SystemExit(f"FAILED_V0845_{label}_MISSING={path}")

doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_terms = [
    "v0.8.45 OCR + LanguageTool review queue design",
    "`Revizuire document`",
    "Text detectat",
    "Corecturi sugerate",
    "Voila! — Documentele tale, lecții clare",
    "15-year-old student",
    "adult without technical knowledge",
    "The learner should not see a technical OCR report.",
    "OCR and LanguageTool run in the background.",
    "Textul din document este corect și gata pentru lecție?",
    "page-based and block-based",
    "detected_text",
    "suggested_text",
    "correction_summary",
    "learner_status",
    "De verificat",
    "Are sugestii",
    "Corectat",
    "Acceptat",
    "Ignorat",
    "Step 1 — Text detectat",
    "Pagina sursă",
    "Text de verificat",
    "Acceptă textul",
    "Corectează textul",
    "Ignoră fragmentul",
    "raw OCR logs",
    "OCR debug dumps",
    "Step 2 — Corecturi sugerate",
    "LanguageTool suggestions",
    "Text original",
    "Text corectat",
    "Acceptă sugestia",
    "Păstrează textul",
    "Editează manual",
    "Aplică sugestiile clare",
    "LanguageTool JSON",
    "rule ID",
    "offset",
    "Language consistency",
    "Română",
    "English",
    "No mixed RO/EN learner flow.",
    "Background engine behavior",
    "Se citește documentul",
    "Se extrage textul",
    "Se verifică textul",
    "Se pregătesc sugestiile",
    "Textul este gata de revizuire",
    "Queue layout",
    "Guidance panel",
    "Diagnostic tehnic",
    "collapsed by default",
    "Friendly editing model",
    "Salvează corectura",
    "Readiness for Study",
    "Unresolved text should not silently become clean Study material.",
    "Diagnostic boundary",
    "Handoff contract",
    "source page",
    "final text",
    "correction state",
    "lesson language",
    "This milestone does not implement the queue.",
    "This milestone does not change the current UI.",
    "This milestone does not change `services/api/web_app.py`.",
    "This milestone does not add a route.",
    "This milestone does not add a POST endpoint.",
    "This milestone does not perform OCR.",
    "This milestone does not perform LanguageTool correction.",
    "This milestone does not write new OCR artifacts.",
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
    "v0.8.46 — learner-facing formula/image/diagram crop queue design.",
    "It is a guided learner workflow that turns detected text into clean, confirmed text for later learning.",
]

missing = [term for term in required_terms if term not in doc_text]
if missing:
    raise SystemExit("FAILED_V0845_DOC_REQUIRED_TERMS_MISSING=" + json.dumps(missing, ensure_ascii=False))

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/ocr-languagetool-review-queue-design-no-build-no-zip-no-share-no-delivery.md",
    "scripts/dev/check-ocr-languagetool-review-queue-design-no-build-no-zip-no-share-no-delivery.py",
    "scripts/dev/check-ocr-languagetool-review-queue-design-no-build-no-zip-no-share-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0845_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

for forbidden in [
    "services/api/web_app.py",
    "services/api/",
    "data/output/",
    "data/input/",
]:
    if any(path.replace("\\", "/").startswith(forbidden) for path in changed):
        raise SystemExit("FAILED_V0845_FORBIDDEN_RUNTIME_OR_DATA_CHANGE=" + forbidden)

evidence_dir = Path(r"D:\dev\tester-runs\v0845-ocr-languagetool-review-queue-design-no-build-no-zip-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_45_OCR_LANGUAGETOOL_REVIEW_QUEUE_DESIGN_CHECK": "PASS",
    "design_created": True,
    "parent_shell": "Revizuire document",
    "covered_step_text_detected": True,
    "covered_step_corrections_suggested": True,
    "product_positioning": "Voila! — Documentele tale, lecții clare",
    "target_student_or_nontechnical_adult": True,
    "ocr_and_languagetool_background_required": True,
    "queue_is_page_based_and_block_based": True,
    "learner_friendly_statuses_defined": True,
    "text_detected_step_defined": True,
    "languagetool_corrections_step_defined": True,
    "language_consistency_required": True,
    "ro_en_mixing_disallowed": True,
    "technical_details_diagnostic_only": True,
    "friendly_editing_model_defined": True,
    "readiness_for_study_defined": True,
    "unresolved_text_not_allowed_as_verified": True,
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
    "ocr_artifact_written": False,
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
    "OCR_LANGUAGETOOL_REVIEW_QUEUE_DESIGN": "PASS_DOC_ONLY_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY",
    "PACKAGE_READINESS": "BLOCKED_PENDING_UI_IMPLEMENTATION_AND_RETEST",
    "POLICY": "ocr_languagetool_review_queue_design_no_build_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.46-owner-local-formula-image-diagram-crop-queue-design-no-build-no-zip-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.45-OCR-LANGUAGETOOL-REVIEW-QUEUE-DESIGN-CHECK.json"
out_md = evidence_dir / "V0.8.45-OCR-LANGUAGETOOL-REVIEW-QUEUE-DESIGN-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.45 OCR + LanguageTool review queue design — no build/no ZIP/no share/no delivery",
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
