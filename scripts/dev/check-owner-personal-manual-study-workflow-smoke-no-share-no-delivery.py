from pathlib import Path
import json
import subprocess

root = Path(".").resolve()

doc = root / "docs" / "dev" / "owner-personal-manual-study-workflow-smoke-no-share-no-delivery.md"
runner = root / "scripts" / "dev" / "run-owner-personal-manual-study-workflow-smoke-no-share-no-delivery.ps1"
check_py = root / "scripts" / "dev" / "check-owner-personal-manual-study-workflow-smoke-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-owner-personal-manual-study-workflow-smoke-no-share-no-delivery.ps1"
web = root / "services" / "api" / "web_app.py"

for path, marker in [
    (doc, "FAILED_V0841_DOC_MISSING"),
    (runner, "FAILED_V0841_RUNNER_MISSING"),
    (check_py, "FAILED_V0841_CHECK_PY_MISSING"),
    (check_ps1, "FAILED_V0841_CHECK_PS1_MISSING"),
    (web, "FAILED_V0841_WEB_APP_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker + "=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
runner_text = runner.read_text(encoding="utf-8", errors="replace")
web_text = web.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "Owner personal Manual Study workflow smoke",
    "Home → Course Tools → Manual Learning Evidence / evidence workflow → export previews → Study normal → Manual Study default",
    "NEEDS_UX_POLISH",
    "BLOCKED",
    "PASS_OWNER_PERSONAL_CLEAR",
    "This milestone records owner personal smoke evidence only.",
    "It does not rebuild the package.",
    "It does not create a new ZIP.",
    "It does not copy to OneDrive.",
    "It does not create a share.",
    "It does not deliver anything.",
    "Any future tester delivery requires a separate explicit owner-approved milestone.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit("FAILED_V0841_DOC_TERM_MISSING=" + term)

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/owner-personal-manual-study-workflow-smoke-no-share-no-delivery.md",
    "scripts/dev/run-owner-personal-manual-study-workflow-smoke-no-share-no-delivery.ps1",
    "scripts/dev/check-owner-personal-manual-study-workflow-smoke-no-share-no-delivery.py",
    "scripts/dev/check-owner-personal-manual-study-workflow-smoke-no-share-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0841_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

required_runner_terms = [
    "VOILA_V0_8_41_OWNER_PERSONAL_MANUAL_STUDY_WORKFLOW_SMOKE_RECORDED",
    "owner_personal_workflow_result",
    "PASS_OWNER_PERSONAL_CLEAR",
    "NEEDS_UX_POLISH",
    "BLOCKED",
    "Read-Host",
    "Home",
    "Course Tools",
    "Manual Learning Evidence",
    "Study normal",
    "Manual Study default",
    "share_created",
    "delivery_performed",
    "public_release_created",
]

for term in required_runner_terms:
    if term not in runner_text:
        raise SystemExit("FAILED_V0841_RUNNER_TERM_MISSING=" + term)

required_web_terms = [
    "manual-study-default-route",
    "manual-study-default-cards",
    "manual_study_default_read_only_fallback",
    "manual-study-shadow-route",
    "manual-study-shadow-course-tools-link",
    "manual-study-dry-run-course-tools-link",
    "/study?pdf=",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit("FAILED_V0841_WEB_TERM_MISSING=" + term)

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0841_STUDY_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/study"') != 0:
    raise SystemExit("FAILED_V0841_STUDY_POST_ADDED")

evidence_json = Path(r"D:\dev\tester-runs\v0841-owner-personal-manual-study-workflow-smoke-no-share-no-delivery\V0.8.41-OWNER-PERSONAL-MANUAL-STUDY-WORKFLOW-SMOKE.json")
evidence_md = Path(r"D:\dev\tester-runs\v0841-owner-personal-manual-study-workflow-smoke-no-share-no-delivery\V0.8.41-OWNER-PERSONAL-MANUAL-STUDY-WORKFLOW-SMOKE.md")

if not evidence_json.exists():
    raise SystemExit("FAILED_V0841_OWNER_PERSONAL_SMOKE_EVIDENCE_MISSING=" + str(evidence_json))

evidence = json.loads(evidence_json.read_text(encoding="utf-8", errors="replace"))

if evidence.get("VOILA_V0_8_41_OWNER_PERSONAL_MANUAL_STUDY_WORKFLOW_SMOKE_RECORDED") != "PASS":
    raise SystemExit("FAILED_V0841_EVIDENCE_NOT_RECORDED")

result = evidence.get("owner_personal_workflow_result")
if result not in {"PASS_OWNER_PERSONAL_CLEAR", "NEEDS_UX_POLISH", "BLOCKED"}:
    raise SystemExit("FAILED_V0841_INVALID_OWNER_PERSONAL_WORKFLOW_RESULT=" + str(result))

for key, expected in {
    "package_rebuild_performed": False,
    "new_zip_created": False,
    "onedrive_copy_created": False,
    "share_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
}.items():
    if evidence.get(key) != expected:
        raise SystemExit(f"FAILED_V0841_POLICY_VALUE={key}; ACTUAL={evidence.get(key)!r}; EXPECTED={expected!r}")

if evidence.get("health_ok") is not True:
    raise SystemExit("FAILED_V0841_HEALTH_NOT_OK_IN_OWNER_EVIDENCE")

if not evidence_md.exists():
    raise SystemExit("FAILED_V0841_OWNER_PERSONAL_SMOKE_MD_MISSING=" + str(evidence_md))

summary = {
    "VOILA_V0_8_41_OWNER_PERSONAL_MANUAL_STUDY_WORKFLOW_SMOKE_CHECK": "PASS",
    "owner_personal_workflow_result": result,
    "owner_smoke_evidence_recorded": True,
    "health_ok": evidence.get("health_ok"),
    "study_normal_renders_manual_default": evidence.get("study_normal_renders_manual_default"),
    "manual_study_cards_visible_and_useful": evidence.get("manual_study_cards_visible_and_useful"),
    "answer_details_remain_read_only": evidence.get("answer_details_remain_read_only"),
    "source_metadata_visible": evidence.get("source_metadata_visible"),
    "tester_ready_without_extra_explanation": evidence.get("tester_ready_without_extra_explanation"),
    "biggest_blocker_or_unclear_step": evidence.get("biggest_blocker_or_unclear_step"),
    "owner_notes": evidence.get("owner_notes"),
    "package_rebuild_performed": False,
    "new_zip_created": False,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "OWNER_PERSONAL_MANUAL_STUDY_WORKFLOW_SMOKE": "PASS_EVIDENCE_RECORDED_NO_SHARE_NO_DELIVERY",
    "POLICY": "owner_personal_manual_study_workflow_smoke_no_share_no_delivery",
}

out_dir = Path(r"D:\dev\tester-runs\v0841-owner-personal-manual-study-workflow-smoke-no-share-no-delivery")
out_json = out_dir / "V0.8.41-OWNER-PERSONAL-MANUAL-STUDY-WORKFLOW-SMOKE-CHECK.json"
out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")

print("EVIDENCE_JSON=" + str(evidence_json))
print("EVIDENCE_MD=" + str(evidence_md))
print("CHECK_JSON=" + str(out_json))
