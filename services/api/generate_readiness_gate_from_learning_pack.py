from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# VOILA_V0_7_76_OWNER_LOCAL_GENERATE_READINESS_GATE_FROM_REBUILT_LEARNING_PACK_START
# Owner-local generate readiness gate from rebuilt document learning pack.
# Policy: write readiness artifact only. No /generate integration, no course
# regeneration, no build, no ZIP, no delivery, no distribution.

class GenerateReadinessGateError(RuntimeError):
    """Raised when the rebuilt learning pack is not ready for future generate integration."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        raise GenerateReadinessGateError("Invalid JSON artifact") from exc
    if not isinstance(data, dict):
        raise GenerateReadinessGateError("Artifact must be a JSON object")
    return data


def as_bool(value: Any) -> bool:
    return value is True


def int_value(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def require(condition: bool, message: str) -> None:
    if not condition:
        raise GenerateReadinessGateError(message)


def validate_rebuilt_learning_pack(pack: dict[str, Any]) -> dict[str, Any]:
    gate = pack.get("quality_gate")
    policy = pack.get("policy")
    evidence = pack.get("verified_user_evidence")
    teaching_plan = pack.get("teaching_plan")

    require(pack.get("artifact") == "document_learning_pack", "Expected document_learning_pack artifact")
    require(pack.get("rebuild_artifact_version") == "v0.7.75", "Expected v0.7.75 rebuilt learning pack")
    require(
        as_bool(pack.get("document_learning_pack_rebuilt_from_applied_ocr_review")),
        "Learning pack must be rebuilt from applied OCR Review",
    )
    require(isinstance(gate, dict), "quality_gate missing")
    require(isinstance(policy, dict), "policy missing")
    require(isinstance(evidence, dict), "verified_user_evidence missing")
    require(isinstance(teaching_plan, dict), "teaching_plan missing")

    concept_count = int_value(gate.get("concept_count"))
    review_item_count = int_value(gate.get("review_item_count"))
    pending_decision_count = int_value(gate.get("pending_decision_count"))
    verified_user_evidence_count = int_value(gate.get("verified_user_evidence_count"))

    require(concept_count >= 3, "Too few concepts for generate readiness")
    require(review_item_count > 0, "Missing OCR Review items")
    require(pending_decision_count == 0, "OCR Review still has pending decisions")
    require(gate.get("document_learning_status") == "PASS", "Document learning status must be PASS")
    require(as_bool(gate.get("generation_allowed")), "Generation must be allowed inside learning pack")
    require(verified_user_evidence_count > 0, "Verified user evidence must exist")
    require(as_bool(gate.get("confirmed_decisions_applied")), "Confirmed decisions must be applied")
    require(as_bool(gate.get("owner_review_confirmed")), "Owner review must be confirmed")
    require(as_bool(gate.get("document_learning_pack_rebuilt_from_applied_ocr_review")), "Gate rebuild flag missing")
    require(gate.get("generate_integration_enabled") is False, "Generate integration must still be disabled")
    require(gate.get("generator_route_changed") is False, "Generator route must be unchanged")
    require(gate.get("course_regeneration_performed") is False, "Course regeneration must not be performed")

    require(as_bool(policy.get("document_learning_pack_rebuild_performed")), "Learning pack rebuild policy must be true")
    require(policy.get("generate_integration_changed") is False, "Generate integration policy must be unchanged")
    require(policy.get("course_regeneration_performed") is False, "Course regeneration policy must be false")
    require(policy.get("build_performed") is False, "Build policy must be false")
    require(policy.get("zip_created") is False, "ZIP policy must be false")
    require(policy.get("delivery_performed") is False, "Delivery policy must be false")
    require(policy.get("distribution_performed") is False, "Distribution policy must be false")

    require(
        teaching_plan.get("teaching_plan_status") == "candidate_ready_for_future_generator",
        "Teaching plan must be candidate_ready_for_future_generator",
    )

    items = evidence.get("items")
    require(isinstance(items, list), "Verified evidence items must be a list")
    require(len(items) == verified_user_evidence_count, "Verified evidence item count mismatch")

    return {
        "concept_count": concept_count,
        "review_item_count": review_item_count,
        "pending_decision_count": pending_decision_count,
        "verified_user_evidence_count": verified_user_evidence_count,
        "document_learning_status": gate.get("document_learning_status"),
        "generation_allowed_in_pack": gate.get("generation_allowed"),
        "teaching_plan_status": teaching_plan.get("teaching_plan_status"),
    }


def build_generate_readiness_gate(
    rebuilt_learning_pack: dict[str, Any],
    *,
    source_path: Path | None = None,
) -> dict[str, Any]:
    summary = validate_rebuilt_learning_pack(rebuilt_learning_pack)

    return {
        "artifact": "owner_local_generate_readiness_gate",
        "artifact_version": "v0.7.76",
        "source_artifact": rebuilt_learning_pack.get("artifact"),
        "source_rebuild_artifact_version": rebuilt_learning_pack.get("rebuild_artifact_version"),
        "source_path": str(source_path or ""),
        "generated_at": utc_now(),
        "generate_readiness_status": "PASS",
        "ready_for_separate_generate_integration_milestone": True,
        "tester_readiness": "BLOCKED",
        "summary": summary,
        "quality_gate": {
            "rebuilt_learning_pack_required": True,
            "rebuilt_learning_pack_present": True,
            "document_learning_pack_rebuilt_from_applied_ocr_review": True,
            "document_learning_status": summary["document_learning_status"],
            "generation_allowed_in_pack": summary["generation_allowed_in_pack"],
            "verified_user_evidence_count": summary["verified_user_evidence_count"],
            "pending_decision_count": summary["pending_decision_count"],
            "teaching_plan_status": summary["teaching_plan_status"],
            "generate_readiness_status": "PASS",
            "ready_for_separate_generate_integration_milestone": True,
            "generate_integration_changed": False,
            "generator_route_changed": False,
            "course_regeneration_performed": False,
            "tester_readiness_blocked_until_generate_integration_and_browser_smoke": True,
        },
        "policy": {
            "owner_local_only": True,
            "writes_only_generate_readiness_artifacts": True,
            "document_learning_pack_rebuild_already_performed": True,
            "generate_integration_changed": False,
            "generator_route_changed": False,
            "course_regeneration_performed": False,
            "build_performed": False,
            "zip_created": False,
            "share_created": False,
            "delivery_performed": False,
            "distribution_performed": False,
        },
        "next_step_contract": {
            "allowed_next_milestone": "separate_owner_local_generate_integration_contract_or_guarded_hook",
            "must_not_skip_browser_smoke": True,
            "must_not_package_for_testers_before_generate_integration_passes": True,
        },
    }


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    gate = report.get("quality_gate", {})
    policy = report.get("policy", {})

    lines = [
        "# Generate Readiness Gate",
        "",
        f"Artifact version: `{report.get('artifact_version')}`",
        f"Source artifact: `{report.get('source_artifact')}`",
        f"Source rebuild version: `{report.get('source_rebuild_artifact_version')}`",
        f"Generate readiness status: `{report.get('generate_readiness_status')}`",
        f"Ready for separate generate integration milestone: `{report.get('ready_for_separate_generate_integration_milestone')}`",
        f"Tester readiness: `{report.get('tester_readiness')}`",
        "",
        "## Gate",
        "",
        f"Document learning status: `{gate.get('document_learning_status')}`",
        f"Generation allowed in pack: `{gate.get('generation_allowed_in_pack')}`",
        f"Verified user evidence count: `{gate.get('verified_user_evidence_count')}`",
        f"Pending decisions: `{gate.get('pending_decision_count')}`",
        f"Teaching plan status: `{gate.get('teaching_plan_status')}`",
        f"Generate integration changed: `{gate.get('generate_integration_changed')}`",
        f"Generator route changed: `{gate.get('generator_route_changed')}`",
        f"Course regeneration performed: `{gate.get('course_regeneration_performed')}`",
        "",
        "## Policy",
        "",
        f"Build performed: `{policy.get('build_performed')}`",
        f"ZIP created: `{policy.get('zip_created')}`",
        f"Share created: `{policy.get('share_created')}`",
        f"Delivery performed: `{policy.get('delivery_performed')}`",
        f"Distribution performed: `{policy.get('distribution_performed')}`",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_generate_readiness_gate_from_learning_pack(
    document_learning_pack_json: Path,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    source_path = Path(document_learning_pack_json)
    report = build_generate_readiness_gate(
        load_json(source_path),
        source_path=source_path,
    )

    target_dir = Path(output_dir).resolve() if output_dir else source_path.resolve().parent
    target_dir.mkdir(parents=True, exist_ok=True)

    json_path = target_dir / "generate_readiness_gate.json"
    md_path = target_dir / "generate_readiness_gate.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(report, md_path)

    return {
        "GENERATE_READINESS_GATE": "PASS",
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "source_rebuild_artifact_version": report["source_rebuild_artifact_version"],
        "document_learning_status": report["quality_gate"]["document_learning_status"],
        "generation_allowed_in_pack": report["quality_gate"]["generation_allowed_in_pack"],
        "verified_user_evidence_count": report["quality_gate"]["verified_user_evidence_count"],
        "ready_for_separate_generate_integration_milestone": report["ready_for_separate_generate_integration_milestone"],
        "generate_integration_changed": report["policy"]["generate_integration_changed"],
        "course_regeneration_performed": report["policy"]["course_regeneration_performed"],
        "tester_readiness": report["tester_readiness"],
        "scope": "owner-local generate readiness gate only; no generate integration, no course regeneration, no build, no ZIP, no delivery, no distribution",
    }


# VOILA_V0_7_76_OWNER_LOCAL_GENERATE_READINESS_GATE_FROM_REBUILT_LEARNING_PACK_END
