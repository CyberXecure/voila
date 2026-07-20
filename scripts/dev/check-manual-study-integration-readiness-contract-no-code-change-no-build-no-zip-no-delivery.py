from pathlib import Path
import json
import subprocess

root = Path(".").resolve()

web = root / "services" / "api" / "web_app.py"
doc = root / "docs" / "dev" / "manual-study-integration-readiness-contract-no-code-change-no-build-no-zip-no-delivery.md"

for path, marker in [
    (web, "FAILED_V0817_WEB_APP_MISSING"),
    (doc, "FAILED_V0817_DOC_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker)

web_text = web.read_text(encoding="utf-8", errors="replace")
doc_text = doc.read_text(encoding="utf-8", errors="replace")

required_existing_web_terms = [
    "VOILA_V0_8_13_MANUAL_STUDY_ROUTE_READ_ONLY_PREVIEW_START",
    "VOILA_V0_8_14_MANUAL_STUDY_PREVIEW_COURSE_TOOLS_LINK_START",
    "VOILA_V0_8_15_MANUAL_STUDY_PREVIEW_NAVIGATION_POLISH_CSS_START",
    '@app.get("/owner/manual-study-preview/{course_id}")',
    "manual_study_items.preview.json",
    "manual_study_items_preview_viewer",
    "manual-study-preview-route",
    "manual-study-preview-card-navigation",
]

for term in required_existing_web_terms:
    if term not in web_text:
        raise SystemExit(f"FAILED_V0817_EXISTING_WEB_TERM_MISSING={term}")

required_doc_terms = [
    "Manual Study integration readiness contract",
    "It does not integrate Manual Study into `/study`.",
    "`manual_study_items.preview.json`",
    "`study_items.preview.json`",
    "Entry criteria before touching `/study`",
    "`manual_learning_evidence.json` exists.",
    "Accepted evidence has `status=accepted_owner_verified`.",
    "Accepted evidence has `owner_verified=true`.",
    "Quality gate passes for required fields.",
    "`manual_learning_pack.preview.json` exists.",
    "`manual_study_items.preview.json` exists.",
    "Manual Study Preview route loads with HTTP 200.",
    "Course Tools shows Manual Study Preview link/status.",
    "Existing `/study` route is preserved",
    "Rollback path is documented before integration.",
    "Progress write remains disabled",
    "Answer marking remains disabled",
    "Safety gates for future integration",
    "No unverified evidence is included.",
    "No rejected evidence is included.",
    "No pending evidence is included.",
    "No legacy Study artifact is overwritten.",
    "No Progress file is written.",
    "No answer marking is added.",
    "All manual Study items are traceable to `source_evidence_id`.",
    "Rollback contract",
    "Reverting the future integration commit.",
    "Removing or ignoring `manual_study_items.preview.json`.",
    "Keeping the existing `/study` route behavior available.",
    "Keeping legacy `study_items.preview.json` unchanged.",
    "Keeping progress data unchanged.",
    "This milestone is contract/check only.",
    "It does not modify `services/api/web_app.py`.",
    "It does not add a route.",
    "It does not add a write endpoint.",
    "It does not connect Manual Study to `/study`.",
    "It does not write progress.",
    "It does not mark answers.",
    "No UI implementation change.",
    "No new POST endpoint.",
    "No Progress write.",
    "No answer marking.",
    "No Study integration.",
    "No Course integration.",
    "No OCR rewrite.",
    "No Formula OCR.",
    "No crop file write.",
    "No build.",
    "No ZIP.",
    "No share.",
    "No delivery.",
    "No distribution.",
    "v0.8.18-owner-local-manual-study-integration-dry-run-toggle-no-progress-no-build-no-zip-no-delivery",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit(f"FAILED_V0817_DOC_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/manual-study-integration-readiness-contract-no-code-change-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-manual-study-integration-readiness-contract-no-code-change-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-manual-study-integration-readiness-contract-no-code-change-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0817_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

if web_text.count('@app.get("/owner/manual-study-preview/{course_id}"') != 1:
    raise SystemExit("FAILED_V0817_MANUAL_STUDY_PREVIEW_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/owner/manual-study-preview') != 0:
    raise SystemExit("FAILED_V0817_MANUAL_STUDY_PREVIEW_POST_ADDED")

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0817_STUDY_ROUTE_COUNT_CHANGED")

for forbidden in [
    '@app.post("/owner/manual-study-preview',
    "manual_progress",
    "progress_write = True",
    "answer_marking = True",
    "replaces_study_route = True",
    "course_generation_changed = True",
    "study_changed = True",
    "progress_changed = True",
    "ocr_rewrite_performed = True",
    "formula_ocr_performed = True",
    '"study_changed": True',
    '"progress_changed": True',
]:
    if forbidden in web_text:
        raise SystemExit(f"FAILED_V0817_FORBIDDEN_WEB_TERM_FOUND={forbidden}")

summary = {
    "VOILA_V0_8_17_MANUAL_STUDY_INTEGRATION_READINESS_CONTRACT_CHECK": "PASS",
    "depends_on_v0813_manual_study_preview": True,
    "depends_on_v0814_course_tools_link": True,
    "depends_on_v0815_navigation_polish": True,
    "depends_on_v0816_browser_readiness_audit": True,
    "contract_doc_added": True,
    "entry_criteria_defined": True,
    "safety_gates_defined": True,
    "rollback_contract_defined": True,
    "future_integration_source": "manual_study_items.preview.json",
    "legacy_study_artifact_protected": True,
    "web_app_changed": False,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "manual_study_connected_to_real_study": False,
    "replaces_existing_study_route": False,
    "progress_write_added": False,
    "answer_marking_added": False,
    "study_artifact_written": False,
    "legacy_study_items_preview_unchanged": True,
    "crop_file_written": False,
    "course_generation_changed": False,
    "study_changed": False,
    "progress_changed": False,
    "ocr_rewrite_performed": False,
    "formula_ocr_performed": False,
    "build_performed": False,
    "zip_created": False,
    "share_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "TESTER_READINESS": "BLOCKED_CONTRACT_ONLY_NO_STUDY_INTEGRATION_NO_PACKAGE",
    "POLICY": "manual_study_integration_readiness_contract_no_code_change_no_build_no_zip_no_share_no_delivery_no_distribution",
    "RECOMMENDED_NEXT": "v0.8.18-owner-local-manual-study-integration-dry-run-toggle-no-progress-no-build-no-zip-no-delivery",
}

evidence = Path(r"D:\dev\tester-runs\v0817-manual-study-integration-readiness-contract")
evidence.mkdir(parents=True, exist_ok=True)

out_json = evidence / "V0.8.17-MANUAL-STUDY-INTEGRATION-READINESS-CONTRACT-CHECK.json"
out_md = evidence / "V0.8.17-MANUAL-STUDY-INTEGRATION-READINESS-CONTRACT-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.17 Manual Study integration readiness contract",
    "",
    "## Summary",
]
for key, value in summary.items():
    md_lines.append(f"- {key}: {value}")

out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
