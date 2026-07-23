from pathlib import Path
import importlib.util
import json
import subprocess
import sys

repo = Path(".").resolve()

doc = repo / "docs" / "dev" / "bbox-visual-item-example-and-validator-no-share-no-delivery.md"
contract_doc = repo / "docs" / "dev" / "bbox-visual-item-contract-no-share-no-delivery.md"
fixture = repo / "docs" / "dev" / "fixtures" / "bbox-visual-items" / "visual_items.bbox.example.json"
validator = repo / "scripts" / "dev" / "validate-bbox-visual-items.py"
check_py = repo / "scripts" / "dev" / "check-bbox-visual-item-example-and-validator-no-share-no-delivery.py"
check_ps1 = repo / "scripts" / "dev" / "check-bbox-visual-item-example-and-validator-no-share-no-delivery.ps1"

def fail(message: str) -> None:
    raise SystemExit(message)

for path in [doc, contract_doc, fixture, validator, check_py, check_ps1]:
    if not path.exists():
        fail("FAILED_V0868_REQUIRED_FILE_MISSING=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
contract_text = contract_doc.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "v0.8.68 BBox visual item example and validator",
    "tracked local example and standalone validator",
    "It does not generate crops.",
    "It does not run OCR Math.",
    "It does not change web routes.",
    "It does not change Study or Progress.",
    "visual_items.bbox.example.json",
    "validate-bbox-visual-items.py",
    "Study gate rules enforced",
    "Example and validator only.",
    "No server required.",
    "No web route change.",
    "No POST.",
    "No upload.",
    "No generate.",
    "No OCR run.",
    "No LanguageTool run.",
    "No crop generation.",
    "No OCR Math run.",
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
        fail("FAILED_V0868_DOC_TERM_MISSING=" + term)

required_contract_terms = [
    "formula_visual_evidence/visual_items.bbox.json",
    "A visual item may enter clean Study only when:",
    "Items with `user_decision=ignore` must never feed Study.",
    "Items with `user_decision=pending` must never feed Study.",
    "OCR Math may run only after a bbox/crop exists.",
]

for term in required_contract_terms:
    if term not in contract_text:
        fail("FAILED_V0868_CONTRACT_TERM_MISSING=" + term)

payload = json.loads(fixture.read_text(encoding="utf-8"))
if payload.get("schema_version") != "v0.8.67":
    fail("FAILED_V0868_FIXTURE_SCHEMA_VERSION_UNEXPECTED")

items = payload.get("items")
if not isinstance(items, list) or len(items) < 4:
    fail("FAILED_V0868_FIXTURE_ITEM_COUNT_TOO_SMALL")

decisions = {item.get("user_decision") for item in items if isinstance(item, dict)}
for expected in ["pending", "accept", "edit", "ignore"]:
    if expected not in decisions:
        fail("FAILED_V0868_FIXTURE_DECISION_MISSING=" + expected)

ready_count = sum(1 for item in items if isinstance(item, dict) and item.get("ready_for_study") is True)
if ready_count < 2:
    fail("FAILED_V0868_FIXTURE_READY_COUNT_TOO_SMALL")

spec = importlib.util.spec_from_file_location("validate_bbox_visual_items", validator)
if spec is None or spec.loader is None:
    fail("FAILED_V0868_VALIDATOR_IMPORT_SPEC")

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

ok, errors, summary = module.validate_file(fixture)
if not ok:
    fail("FAILED_V0868_FIXTURE_VALIDATION_ERRORS=" + json.dumps(errors, ensure_ascii=False))

if summary.get("item_count") != len(items):
    fail("FAILED_V0868_VALIDATOR_SUMMARY_ITEM_COUNT_UNEXPECTED")

if summary.get("ready_for_study_count") != ready_count:
    fail("FAILED_V0868_VALIDATOR_SUMMARY_READY_COUNT_UNEXPECTED")

invalid_payload = json.loads(json.dumps(payload))
invalid_payload["items"][0]["ready_for_study"] = True
invalid_payload["items"][0]["user_decision"] = "pending"
invalid_ok, invalid_errors = module.validate_visual_items_payload(invalid_payload)
if invalid_ok:
    fail("FAILED_V0868_INVALID_PENDING_READY_PAYLOAD_ACCEPTED")
if not any("pending_item_must_not_be_ready_for_study" in err for err in invalid_errors):
    fail("FAILED_V0868_INVALID_PENDING_READY_ERROR_MISSING")

invalid_payload_2 = json.loads(json.dumps(payload))
invalid_payload_2["items"][2]["user_decision"] = "edit"
invalid_payload_2["items"][2]["user_corrected_text"] = ""
invalid_payload_2["items"][2]["ready_for_study"] = True
invalid_payload_2["items"][2]["ocr_math_candidate_text"] = ""
invalid_ok_2, invalid_errors_2 = module.validate_visual_items_payload(invalid_payload_2)
if invalid_ok_2:
    fail("FAILED_V0868_INVALID_EDITED_EMPTY_TEXT_PAYLOAD_ACCEPTED")
if not any("edited_ready_item_requires_user_corrected_text" in err for err in invalid_errors_2):
    fail("FAILED_V0868_INVALID_EDITED_EMPTY_TEXT_ERROR_MISSING")

subprocess.check_call([sys.executable, "-m", "py_compile", str(validator)], cwd=str(repo))
subprocess.check_call([sys.executable, str(validator), str(fixture)], cwd=str(repo))

status_lines = subprocess.check_output(
    ["git", "status", "--porcelain", "-uall"],
    cwd=str(repo),
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/bbox-visual-item-example-and-validator-no-share-no-delivery.md",
    "docs/dev/fixtures/bbox-visual-items/visual_items.bbox.example.json",
    "scripts/dev/validate-bbox-visual-items.py",
    "scripts/dev/check-bbox-visual-item-example-and-validator-no-share-no-delivery.py",
    "scripts/dev/check-bbox-visual-item-example-and-validator-no-share-no-delivery.ps1",
}

unexpected = []
for line in status_lines:
    if not line.strip():
        continue
    rel = line[3:].replace("\\", "/")
    if rel not in allowed:
        unexpected.append(line)

if unexpected:
    fail("FAILED_V0868_UNEXPECTED_GIT_STATUS_PATHS=" + json.dumps(unexpected, ensure_ascii=False))

summary_out = {
    "VOILA_V0_8_68_BBOX_VISUAL_ITEM_EXAMPLE_AND_VALIDATOR_CHECK": "PASS",
    "example_and_validator_only": True,
    "implementation_performed": False,
    "canonical_artifact_contract": "formula_visual_evidence/visual_items.bbox.json",
    "tracked_example": "docs/dev/fixtures/bbox-visual-items/visual_items.bbox.example.json",
    "standalone_validator": "scripts/dev/validate-bbox-visual-items.py",
    "fixture_item_count": len(items),
    "fixture_ready_for_study_count": ready_count,
    "fixture_pending_decision_present": True,
    "fixture_accept_decision_present": True,
    "fixture_edit_decision_present": True,
    "fixture_ignore_decision_present": True,
    "validator_accepts_valid_fixture": True,
    "validator_rejects_pending_ready_item": True,
    "validator_rejects_edited_ready_item_without_text": True,
    "study_gate_rules_enforced": True,
    "web_route_change_performed": False,
    "server_started": False,
    "post_called": False,
    "upload_performed": False,
    "generate_performed": False,
    "ocr_run": False,
    "languagetool_run": False,
    "crop_generation_performed": False,
    "ocr_math_run": False,
    "study_write": False,
    "progress_write": False,
    "build_performed": False,
    "zip_created": False,
    "onedrive_staging_created": False,
    "share_link_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "recommended_next": "v0.8.69-owner-local-real-crop-artifact-from-bbox-no-share-no-delivery",
}

evidence_dir = Path(r"D:\dev\tester-runs\v0868-bbox-visual-item-example-and-validator-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

out_json = evidence_dir / "V0.8.68-BBOX-VISUAL-ITEM-EXAMPLE-AND-VALIDATOR-CHECK.json"
out_md = evidence_dir / "V0.8.68-BBOX-VISUAL-ITEM-EXAMPLE-AND-VALIDATOR-CHECK.md"

out_json.write_text(json.dumps(summary_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
out_md.write_text(
    "# v0.8.68 BBox visual item example and validator\n\n"
    + "\n".join(f"- {k}: {v}" for k, v in summary_out.items())
    + "\n",
    encoding="utf-8",
)

for k, v in summary_out.items():
    print(f"{k}={v}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
