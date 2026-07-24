from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import subprocess
import sys

repo = Path(".").resolve()

doc = repo / "docs" / "dev" / "manual-visual-validation-gate-no-share-no-delivery.md"
gate = repo / "scripts" / "dev" / "apply-bbox-visual-validation-decisions.py"
validator = repo / "scripts" / "dev" / "validate-bbox-visual-items.py"
v0870_doc = repo / "docs" / "dev" / "ocrmath-on-crop-candidate-no-share-no-delivery.md"
web_app = repo / "services" / "api" / "web_app.py"

def fail(message: str) -> None:
    raise SystemExit(message)

for path in [doc, gate, validator, v0870_doc, web_app]:
    if not path.exists():
        fail("FAILED_V0871_REQUIRED_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
v0870_text = v0870_doc.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.71 Manual visual validation gate",
    "controlled local manual validation gate",
    "scripts/dev/apply-bbox-visual-validation-decisions.py",
    "visual_items.bbox.with-ocrmath-candidates.json",
    "visual_items.bbox.validated.json",
    "visual_items.bbox.validation-summary.json",
    "Allowed decisions are:",
    "`accept`",
    "`edit`",
    "`ignore`",
    "No implicit approval is allowed.",
    "Items without decisions remain:",
    "`user_decision=pending`",
    "`ready_for_study=false`",
    "Pending and ignored items must not feed Study.",
    "This milestone does not connect the gate to the web UI.",
    "It does not modify `services/api/web_app.py`.",
    "It does not run `/generate`.",
    "It does not run OCR.",
    "It does not run LanguageTool.",
    "It does not run OCR Math.",
    "It does not ingest validated items into Study.",
    "Controlled local manual visual validation gate only.",
    "No web route change.",
    "No server required.",
    "No POST.",
    "No upload.",
    "No generate.",
    "No OCR run.",
    "No LanguageTool run.",
    "No OCR Math run.",
    "No Study ingestion.",
    "No Study write.",
    "No Progress write.",
    "No build.",
    "No ZIP.",
    "No OneDrive staging.",
    "No share link.",
    "No tester delivery.",
    "No distribution.",
    "No public release.",
]

for term in required_doc_terms:
    if term not in doc_text:
        fail("FAILED_V0871_DOC_TERM_MISSING=" + term)

for term in [
    "visual_items.bbox.with-ocrmath-candidates.json",
    "OCR Math on crop produces only a candidate.",
    "`user_decision` remains `pending`",
    "`ready_for_study` remains `false`",
]:
    if term not in v0870_text:
        fail("FAILED_V0871_V0870_TERM_MISSING=" + term)

web_before = web_app.read_text(encoding="utf-8", errors="replace")

subprocess.check_call([sys.executable, "-m", "py_compile", str(gate)], cwd=str(repo))
subprocess.check_call([sys.executable, "-m", "py_compile", str(validator)], cwd=str(repo))

evidence_dir = Path(r"D:\dev\tester-runs\v0871-manual-visual-validation-gate-no-share-no-delivery")
work_dir = evidence_dir / "work"
output_root = work_dir / "output"
work_dir.mkdir(parents=True, exist_ok=True)
output_root.mkdir(parents=True, exist_ok=True)

candidate_path = work_dir / "visual_items.bbox.with-ocrmath-candidates.json"
decisions_path = work_dir / "manual-visual-decisions.json"

candidate_payload = {
    "schema_version": "v0.8.67",
    "course_id": "synthetic-manual-visual-validation",
    "source_pdf": "synthetic-manual-visual-validation.pdf",
    "items": [
        {
            "item_id": "bbox-item-accept",
            "kind": "formula",
            "page": 1,
            "bbox": [80, 100, 780, 260],
            "bbox_units": "pdf_points",
            "page_image_path": "formula_visual_evidence/pages/page-001.png",
            "crop_path": "formula_visual_evidence/crops/page-001-item-accept.png",
            "crop_exists": True,
            "ocr_math_candidate_text": "sin x / cos x",
            "ocr_math_status": "pending_user_validation",
            "user_decision": "pending",
            "user_corrected_text": "",
            "user_explanation": "",
            "ready_for_study": False,
            "created_by": "v0.8.71-check",
            "review_notes": "Synthetic accept candidate."
        },
        {
            "item_id": "bbox-item-edit",
            "kind": "formula",
            "page": 1,
            "bbox": [90, 300, 790, 420],
            "bbox_units": "pdf_points",
            "page_image_path": "formula_visual_evidence/pages/page-001.png",
            "crop_path": "formula_visual_evidence/crops/page-001-item-edit.png",
            "crop_exists": True,
            "ocr_math_candidate_text": "tan x = sin x / cos x",
            "ocr_math_status": "pending_user_validation",
            "user_decision": "pending",
            "user_corrected_text": "",
            "user_explanation": "",
            "ready_for_study": False,
            "created_by": "v0.8.71-check",
            "review_notes": "Synthetic edit candidate."
        },
        {
            "item_id": "bbox-item-ignore",
            "kind": "unknown",
            "page": 1,
            "bbox": [100, 500, 300, 580],
            "bbox_units": "pdf_points",
            "page_image_path": "formula_visual_evidence/pages/page-001.png",
            "crop_path": "formula_visual_evidence/crops/page-001-item-ignore.png",
            "crop_exists": True,
            "ocr_math_candidate_text": "",
            "ocr_math_status": "not_applicable",
            "user_decision": "pending",
            "user_corrected_text": "",
            "user_explanation": "",
            "ready_for_study": False,
            "created_by": "v0.8.71-check",
            "review_notes": "Synthetic ignore candidate."
        },
        {
            "item_id": "bbox-item-undecided",
            "kind": "diagram",
            "page": 1,
            "bbox": [400, 500, 700, 760],
            "bbox_units": "pdf_points",
            "page_image_path": "formula_visual_evidence/pages/page-001.png",
            "crop_path": "formula_visual_evidence/crops/page-001-item-undecided.png",
            "crop_exists": True,
            "ocr_math_candidate_text": "Diagram ABC",
            "ocr_math_status": "pending_user_validation",
            "user_decision": "pending",
            "user_corrected_text": "",
            "user_explanation": "",
            "ready_for_study": False,
            "created_by": "v0.8.71-check",
            "review_notes": "Synthetic undecided candidate."
        }
    ]
}

decisions_payload = {
    "schema_version": "v0.8.71",
    "course_id": "synthetic-manual-visual-validation",
    "decisions": [
        {
            "item_id": "bbox-item-accept",
            "user_decision": "accept",
            "user_explanation": "Acceptăm candidatul OCR Math ca suficient pentru studiu.",
            "review_notes": "Accepted in v0.8.71 local check."
        },
        {
            "item_id": "bbox-item-edit",
            "user_decision": "edit",
            "user_corrected_text": "\\tan x = \\frac{\\sin x}{\\cos x}",
            "user_explanation": "Corectăm formula înainte de Study.",
            "review_notes": "Edited in v0.8.71 local check."
        },
        {
            "item_id": "bbox-item-ignore",
            "user_decision": "ignore",
            "user_explanation": "",
            "review_notes": "Ignored in v0.8.71 local check."
        }
    ]
}

candidate_path.write_text(json.dumps(candidate_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
decisions_path.write_text(json.dumps(decisions_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

subprocess.check_call(
    [
        sys.executable,
        str(gate),
        "--visual-items",
        str(candidate_path),
        "--decisions",
        str(decisions_path),
        "--output-root",
        str(output_root),
    ],
    cwd=str(repo),
)

validated_path = output_root / "formula_visual_evidence" / "visual_items.bbox.validated.json"
summary_path = output_root / "formula_visual_evidence" / "visual_items.bbox.validation-summary.json"

for path in [validated_path, summary_path]:
    if not path.exists():
        fail("FAILED_V0871_EXPECTED_ARTIFACT_MISSING=" + str(path))

validated = json.loads(validated_path.read_text(encoding="utf-8"))
items = {item["item_id"]: item for item in validated.get("items", []) if isinstance(item, dict)}

if items["bbox-item-accept"].get("user_decision") != "accept":
    fail("FAILED_V0871_ACCEPT_DECISION_NOT_APPLIED")
if items["bbox-item-accept"].get("ocr_math_status") != "validated_by_user":
    fail("FAILED_V0871_ACCEPT_STATUS_NOT_VALIDATED")
if items["bbox-item-accept"].get("ready_for_study") is not True:
    fail("FAILED_V0871_ACCEPT_NOT_READY")

if items["bbox-item-edit"].get("user_decision") != "edit":
    fail("FAILED_V0871_EDIT_DECISION_NOT_APPLIED")
if items["bbox-item-edit"].get("ocr_math_status") != "validated_by_user":
    fail("FAILED_V0871_EDIT_STATUS_NOT_VALIDATED")
if items["bbox-item-edit"].get("ready_for_study") is not True:
    fail("FAILED_V0871_EDIT_NOT_READY")
if not str(items["bbox-item-edit"].get("user_corrected_text") or "").strip():
    fail("FAILED_V0871_EDIT_CORRECTED_TEXT_EMPTY")

if items["bbox-item-ignore"].get("user_decision") != "ignore":
    fail("FAILED_V0871_IGNORE_DECISION_NOT_APPLIED")
if items["bbox-item-ignore"].get("ready_for_study") is not False:
    fail("FAILED_V0871_IGNORE_READY_SHOULD_BE_FALSE")

if items["bbox-item-undecided"].get("user_decision") != "pending":
    fail("FAILED_V0871_UNDECIDED_NOT_PENDING")
if items["bbox-item-undecided"].get("ready_for_study") is not False:
    fail("FAILED_V0871_UNDECIDED_READY_SHOULD_BE_FALSE")

summary = json.loads(summary_path.read_text(encoding="utf-8"))
if summary.get("ready_for_study_count") != 2:
    fail("FAILED_V0871_READY_COUNT_UNEXPECTED")
if summary.get("accepted_count") != 1:
    fail("FAILED_V0871_ACCEPTED_COUNT_UNEXPECTED")
if summary.get("edited_count") != 1:
    fail("FAILED_V0871_EDITED_COUNT_UNEXPECTED")
if summary.get("ignored_count") != 1:
    fail("FAILED_V0871_IGNORED_COUNT_UNEXPECTED")
if summary.get("pending_count") != 1:
    fail("FAILED_V0871_PENDING_COUNT_UNEXPECTED")

spec = importlib.util.spec_from_file_location("validate_bbox_visual_items", validator)
if spec is None or spec.loader is None:
    fail("FAILED_V0871_VALIDATOR_IMPORT_SPEC")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ok, errors, validator_summary = module.validate_file(validated_path)
if not ok:
    fail("FAILED_V0871_VALIDATED_ARTIFACT_VALIDATOR_ERRORS=" + json.dumps(errors, ensure_ascii=False))

bad_decisions_path = work_dir / "bad-manual-visual-decisions.json"
bad_decisions = {
    "schema_version": "v0.8.71",
    "course_id": "synthetic-manual-visual-validation",
    "decisions": [
        {
            "item_id": "bbox-item-edit",
            "user_decision": "edit",
            "user_corrected_text": "",
            "user_explanation": "Invalid edit without correction."
        }
    ]
}
bad_decisions_path.write_text(json.dumps(bad_decisions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

bad_run = subprocess.run(
    [
        sys.executable,
        str(gate),
        "--visual-items",
        str(candidate_path),
        "--decisions",
        str(bad_decisions_path),
        "--output-root",
        str(output_root / "bad"),
    ],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
    capture_output=True,
)
if bad_run.returncode == 0:
    fail("FAILED_V0871_BAD_EDIT_WITHOUT_TEXT_ACCEPTED")
if "FAILED_EDIT_REQUIRES_USER_CORRECTED_TEXT" not in (bad_run.stdout + bad_run.stderr):
    fail("FAILED_V0871_BAD_EDIT_EXPECTED_ERROR_MISSING")

web_after = web_app.read_text(encoding="utf-8", errors="replace")
if web_before != web_after:
    fail("FAILED_V0871_WEB_APP_CHANGED_DURING_CHECK")

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/manual-visual-validation-gate-no-share-no-delivery.md",
    "scripts/dev/apply-bbox-visual-validation-decisions.py",
    "scripts/dev/check-manual-visual-validation-gate-no-share-no-delivery.py",
    "scripts/dev/check-manual-visual-validation-gate-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0871_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary_out = {
    "VOILA_V0_8_71_MANUAL_VISUAL_VALIDATION_GATE_CHECK": "PASS",
    "manual_visual_validation_gate_added": True,
    "implementation_performed": True,
    "controlled_local_validation_performed": True,
    "accepted_item_ready_for_study": True,
    "edited_item_ready_for_study": True,
    "ignored_item_blocked_from_study": True,
    "undecided_item_remains_pending": True,
    "ready_for_study_count": 2,
    "accepted_count": 1,
    "edited_count": 1,
    "ignored_count": 1,
    "pending_count": 1,
    "validated_artifact_exists": True,
    "validation_summary_exists": True,
    "validated_artifact_validator_pass": True,
    "invalid_edit_without_text_rejected": True,
    "web_route_change_performed": False,
    "web_app_changed": False,
    "server_started": False,
    "post_called": False,
    "upload_performed": False,
    "generate_performed": False,
    "ocr_run": False,
    "languagetool_run": False,
    "ocr_math_run": False,
    "study_ingestion_performed": False,
    "study_write": False,
    "progress_write": False,
    "build_performed": False,
    "zip_created": False,
    "onedrive_staging_created": False,
    "share_link_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "recommended_next": "v0.8.72-owner-local-clean-study-visual-item-ingestion-no-share-no-delivery",
    "evidence_output_root": str(output_root),
}

evidence_dir.mkdir(parents=True, exist_ok=True)
out_json = evidence_dir / "V0.8.71-MANUAL-VISUAL-VALIDATION-GATE-CHECK.json"
out_md = evidence_dir / "V0.8.71-MANUAL-VISUAL-VALIDATION-GATE-CHECK.md"

out_json.write_text(json.dumps(summary_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.71 Manual visual validation gate\n\n"
    + "\n".join(f"- {k}: {v}" for k, v in summary_out.items())
    + "\n",
    encoding="utf-8",
)

for k, v in summary_out.items():
    print(f"{k}={v}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
