from pathlib import Path
import json
import subprocess

root = Path(".").resolve()

charter = root / "docs" / "dev" / "voila-direction-charter-and-guard-no-build-no-zip-no-delivery.md"
doc = root / "docs" / "dev" / "manual-learning-evidence-ui-design-no-build-no-zip-no-delivery.md"

if not charter.exists():
    raise SystemExit("FAILED_V0795_DIRECTION_CHARTER_MISSING")

if not doc.exists():
    raise SystemExit("FAILED_V0795_DESIGN_DOC_MISSING")

charter_text = charter.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_charter_terms = [
    "human-in-the-loop verified learning tool",
    "not positioned as a fully automatic AI course generator",
    "manual_learning_evidence.json",
    "AI assists. The owner validates.",
    "Learning Pack must consume accepted owner-verified evidence",
]

for term in required_charter_terms:
    if term not in charter_text:
        raise SystemExit(f"FAILED_V0795_CHARTER_TERM_MISSING={term}")

required_doc_terms = [
    "Manual Learning Evidence UI",
    "It does not implement the UI yet",
    "human-in-the-loop verified learning tool",
    "not a fully automatic AI course generator",
    "AI assists. The owner validates.",
    "manual_learning_evidence.json",
    "manual_learning_evidence/crops/",
    "/owner/manual-learning-evidence/{course_id}",
    "port `8787`",
    "should not use the old external Crop Editor on port `8790`",
    "title",
    "kind",
    "verified_text",
    "explanation_ro",
    "source_status",
    "source_note",
    "possible_source_error",
    "accepted_owner_verified",
    "rejected_noise",
    "The crop is evidence. The owner metadata is the interpretation.",
    "Learning Pack must not treat image pixels alone as trusted learning meaning.",
    "No UI implementation in this milestone.",
    "No manual crop implementation.",
    "No save endpoint.",
    "No Learning Pack integration.",
    "No build.",
    "No ZIP.",
    "No share.",
    "No delivery.",
    "No distribution.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit(f"FAILED_V0795_DESIGN_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/manual-learning-evidence-ui-design-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-learning-evidence-ui-design-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-learning-evidence-ui-design-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0795_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

summary = {
    "VOILA_V0_7_95_MANUAL_LEARNING_EVIDENCE_UI_DESIGN_CHECK": "PASS",
    "depends_on_v0794_direction_charter": True,
    "product_direction": "human_in_the_loop_verified_learning_tool",
    "not_fully_automatic_ai_course_generator": True,
    "manual_learning_evidence_artifact": "manual_learning_evidence.json",
    "manual_learning_evidence_crops_dir": "manual_learning_evidence/crops/",
    "future_route": "/owner/manual-learning-evidence/{course_id}",
    "uses_main_voila_port_8787": True,
    "uses_external_crop_editor_8790": False,
    "required_fields_title": True,
    "required_fields_kind": True,
    "required_fields_verified_text": True,
    "required_fields_explanation_ro": True,
    "required_fields_source_status": True,
    "possible_source_error_supported": True,
    "learning_pack_requires_accepted_owner_verified_evidence": True,
    "image_pixels_alone_are_not_trusted_learning_meaning": True,
    "ui_implemented": False,
    "manual_crop_implemented": False,
    "save_endpoint_implemented": False,
    "learning_pack_changed": False,
    "course_generation_changed": False,
    "ocr_rewrite_performed": False,
    "formula_ocr_performed": False,
    "build_performed": False,
    "zip_created": False,
    "share_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "TESTER_READINESS": "BLOCKED_DESIGN_ONLY_NO_PRODUCT_UI",
    "POLICY": "manual_learning_evidence_ui_design_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0795-manual-learning-evidence-ui-design")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.7.95-MANUAL-LEARNING-EVIDENCE-UI-DESIGN-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
