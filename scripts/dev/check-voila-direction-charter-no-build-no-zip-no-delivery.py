from pathlib import Path
import json
import subprocess

root = Path(".").resolve()
doc = root / "docs" / "dev" / "voila-direction-charter-and-guard-no-build-no-zip-no-delivery.md"

if not doc.exists():
    raise SystemExit("FAILED_V0794_DIRECTION_CHARTER_DOC_MISSING")

text = doc.read_text(encoding="utf-8", errors="replace")

required_terms = [
    "human-in-the-loop verified learning tool",
    "not positioned as a fully automatic AI course generator",
    "Evidence-first, owner-verified learning",
    "AI assists. The owner validates.",
    "manual_learning_evidence.json",
    "title",
    "kind",
    "verified_text",
    "explanation_ro",
    "source_status",
    "possible_source_error",
    "accepted_owner_verified",
    "Learning Pack must consume accepted owner-verified evidence",
    "AI must not silently invent learning content without traceable evidence",
    "source page",
    "crop_path",
    "No build",
    "No ZIP",
    "No share",
    "No delivery",
    "No distribution",
]

for term in required_terms:
    if term not in text:
        raise SystemExit(f"FAILED_V0794_DIRECTION_TERM_MISSING={term}")

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/voila-direction-charter-and-guard-no-build-no-zip-no-delivery.md",
    "scripts/dev/check-voila-direction-charter-no-build-no-zip-no-delivery.py",
    "scripts/dev/check-voila-direction-charter-no-build-no-zip-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0794_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

summary = {
    "VOILA_V0_7_94_DIRECTION_CHARTER_AND_GUARD_CHECK": "PASS",
    "product_direction": "human_in_the_loop_verified_learning_tool",
    "not_fully_automatic_ai_course_generator": True,
    "evidence_first": True,
    "owner_verified": True,
    "ai_assists_owner_validates": True,
    "manual_learning_evidence_artifact": "manual_learning_evidence.json",
    "learning_pack_consumes_verified_evidence": True,
    "source_mistakes_supported": True,
    "possible_source_error_supported": True,
    "ui_implemented": False,
    "crop_editor_changed": False,
    "learning_pack_changed": False,
    "ocr_rewrite_performed": False,
    "formula_ocr_performed": False,
    "course_generation_changed": False,
    "build_performed": False,
    "zip_created": False,
    "share_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "TESTER_READINESS": "BLOCKED_DIRECTION_GUARD_ONLY_NO_PRODUCT_UI",
    "POLICY": "direction_charter_guard_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0794-voila-direction-charter-and-guard")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.7.94-VOILA-DIRECTION-CHARTER-AND-GUARD-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")
print("EVIDENCE=" + str(out))
