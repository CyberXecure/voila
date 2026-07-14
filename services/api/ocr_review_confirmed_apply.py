from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# VOILA_V0_7_74_OWNER_LOCAL_OCR_REVIEW_CONFIRMED_DECISIONS_APPLY_ARTIFACT_START
# Owner-local confirmed OCR Review decisions apply artifact helper.
# Policy: create ocr_review_decisions.applied.json/md only after final confirmation.
# No document learning pack rebuild, no /generate integration, no build, no ZIP,
# no delivery, no distribution.

ALLOWED_CONFIRMED_DECISIONS = {
    "accepted",
    "edited",
    "ignored",
    "marked_definition",
    "marked_formula",
    "marked_notation",
    "marked_theorem",
    "marked_example",
    "marked_glossary_term",
    "marked_not_relevant",
}

VERIFIED_EVIDENCE_DECISIONS = {
    "accepted",
    "edited",
    "marked_definition",
    "marked_formula",
    "marked_notation",
    "marked_theorem",
    "marked_example",
    "marked_glossary_term",
}


class ConfirmedDecisionApplyError(RuntimeError):
    """Raised when OCR Review decisions are not ready for confirmed apply artifact."""


def compact(value: Any) -> str:
    return str(value or "").strip()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ConfirmedDecisionApplyError("Invalid JSON artifact") from exc

    if not isinstance(data, dict):
        raise ConfirmedDecisionApplyError("Artifact must be a JSON object")
    return data


def decision_items(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    decisions = artifact.get("decisions")
    if not isinstance(decisions, list):
        raise ConfirmedDecisionApplyError("Artifact missing decisions list")
    return [item for item in decisions if isinstance(item, dict)]


def bool_true(value: Any) -> bool:
    return value is True


def int_value(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return fallback


def calculated_pending_count(decisions: list[dict[str, Any]]) -> int:
    return sum(
        1
        for item in decisions
        if item.get("requires_user_decision", True)
        or compact(item.get("decision") or "pending") == "pending"
    )


def validate_confirmed_decisions(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    decisions = decision_items(artifact)
    if not decisions:
        raise ConfirmedDecisionApplyError("No OCR Review decisions found")

    if not bool_true(artifact.get("owner_review_confirmed")):
        raise ConfirmedDecisionApplyError("owner_review_confirmed must be true")

    if not bool_true(artifact.get("real_user_decisions_performed")):
        raise ConfirmedDecisionApplyError("real_user_decisions_performed must be true")

    pending_from_items = calculated_pending_count(decisions)
    pending_from_artifact = int_value(artifact.get("pending_decision_count"), pending_from_items)
    if pending_from_artifact != 0 or pending_from_items != 0:
        raise ConfirmedDecisionApplyError("pending_decision_count must be zero")

    quality_gate = artifact.get("quality_gate")
    if not isinstance(quality_gate, dict):
        raise ConfirmedDecisionApplyError("quality_gate must be present")

    if not bool_true(quality_gate.get("owner_review_confirmed")):
        raise ConfirmedDecisionApplyError("quality_gate.owner_review_confirmed must be true")

    if not bool_true(quality_gate.get("all_required_decisions_resolved")):
        raise ConfirmedDecisionApplyError("quality_gate.all_required_decisions_resolved must be true")

    seen: set[str] = set()
    for item in decisions:
        review_item_id = compact(item.get("review_item_id"))
        if not review_item_id:
            raise ConfirmedDecisionApplyError("Decision item missing review_item_id")
        if review_item_id in seen:
            raise ConfirmedDecisionApplyError(f"Duplicate review_item_id: {review_item_id}")
        seen.add(review_item_id)

        decision = compact(item.get("decision"))
        if decision not in ALLOWED_CONFIRMED_DECISIONS:
            raise ConfirmedDecisionApplyError(f"Unsupported confirmed decision for {review_item_id}: {decision}")

        if item.get("requires_user_decision", True):
            raise ConfirmedDecisionApplyError(f"Decision still requires user review: {review_item_id}")

        if item.get("real_user_decision") is not True:
            raise ConfirmedDecisionApplyError(f"Decision is not marked as real user decision: {review_item_id}")

        if decision == "edited" and not compact(item.get("corrected_text")):
            raise ConfirmedDecisionApplyError(f"Edited decision requires corrected_text: {review_item_id}")

    return decisions


def evidence_text_for_item(item: dict[str, Any]) -> str:
    decision = compact(item.get("decision"))
    if decision == "edited":
        return compact(item.get("corrected_text"))
    return (
        compact(item.get("corrected_text"))
        or compact(item.get("suggested_text"))
        or compact(item.get("source_text"))
    )


def confirmed_role_for_item(item: dict[str, Any]) -> str:
    return (
        compact(item.get("confirmed_learning_role"))
        or compact(item.get("suggested_learning_role"))
        or "unclassified"
    )


def normalize_applied_item(item: dict[str, Any]) -> dict[str, Any]:
    decision = compact(item.get("decision"))
    verified_evidence = decision in VERIFIED_EVIDENCE_DECISIONS
    applied = deepcopy(item)

    applied["requires_user_decision"] = False
    applied["real_user_decision"] = True
    applied["verified_user_evidence"] = verified_evidence
    applied["ready_for_learning_pack_rebuild"] = verified_evidence
    applied["applied_to_learning_pack"] = False
    applied["learning_pack_rebuild_performed"] = False
    applied["confirmed_learning_role"] = confirmed_role_for_item(item)
    applied["verified_evidence_text"] = evidence_text_for_item(item) if verified_evidence else ""
    applied["applied_artifact_source"] = "owner_local_confirmed_decisions_apply_v0.7.74"

    return applied


def build_confirmed_decisions_applied_report(
    decisions_artifact: dict[str, Any],
    *,
    source_path: Path | None = None,
) -> dict[str, Any]:
    decisions = validate_confirmed_decisions(decisions_artifact)
    applied_decisions = [normalize_applied_item(item) for item in decisions]
    verified_items = [item for item in applied_decisions if item.get("verified_user_evidence") is True]
    ignored_items = [item for item in applied_decisions if item.get("verified_user_evidence") is not True]

    decision_count = len(applied_decisions)
    generated_at = utc_now()

    return {
        "artifact": "ocr_review_confirmed_decisions_applied",
        "artifact_version": "v0.7.74",
        "source_artifact": "ocr_review_decisions.json",
        "source_path": str(source_path or ""),
        "generated_at": generated_at,
        "decision_count": decision_count,
        "pending_decision_count": 0,
        "resolved_decision_count": decision_count,
        "owner_review_confirmed": True,
        "owner_review_confirmed_at": decisions_artifact.get("owner_review_confirmed_at"),
        "real_user_decisions_performed": True,
        "confirmed_decisions_applied": True,
        "verified_user_evidence_count": len(verified_items),
        "ignored_or_not_relevant_count": len(ignored_items),
        "applied_decisions": applied_decisions,
        "verified_evidence_items": verified_items,
        "ignored_or_not_relevant_items": ignored_items,
        "quality_gate": {
            "all_required_decisions_resolved": True,
            "owner_review_confirmed": True,
            "confirmed_decisions_applied": True,
            "verified_user_evidence_available": len(verified_items) > 0,
            "generation_should_wait_for_review": True,
            "generation_block_reason": "learning_pack_rebuild_not_enabled_v0.7.74",
            "learning_pack_rebuild_required": True,
            "learning_pack_rebuild_performed": False,
        },
        "policy": {
            "owner_local_only": True,
            "requires_owner_review_confirmed": True,
            "requires_pending_decision_count_zero": True,
            "requires_real_user_decisions_performed": True,
            "writes_only_applied_decisions_artifacts": True,
            "document_learning_pack_rebuild_performed": False,
            "generate_integration_changed": False,
            "course_regeneration_performed": False,
            "build_performed": False,
            "zip_created": False,
            "delivery_performed": False,
            "distribution_performed": False,
        },
    }


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    gate = report.get("quality_gate", {})
    policy = report.get("policy", {})

    lines = [
        "# OCR Review Confirmed Decisions Applied",
        "",
        f"Artifact version: `{report.get('artifact_version')}`",
        f"Decision count: `{report.get('decision_count')}`",
        f"Pending decisions: `{report.get('pending_decision_count')}`",
        f"Resolved decisions: `{report.get('resolved_decision_count')}`",
        f"Owner review confirmed: `{report.get('owner_review_confirmed')}`",
        f"Real user decisions performed: `{report.get('real_user_decisions_performed')}`",
        f"Confirmed decisions applied: `{report.get('confirmed_decisions_applied')}`",
        f"Verified user evidence count: `{report.get('verified_user_evidence_count')}`",
        "",
        "## Gate",
        "",
        f"All required decisions resolved: `{gate.get('all_required_decisions_resolved')}`",
        f"Owner review confirmed: `{gate.get('owner_review_confirmed')}`",
        f"Generation should wait: `{gate.get('generation_should_wait_for_review')}`",
        f"Generation block reason: `{gate.get('generation_block_reason')}`",
        f"Learning pack rebuild performed: `{gate.get('learning_pack_rebuild_performed')}`",
        "",
        "## Policy",
        "",
        f"Document learning pack rebuild performed: `{policy.get('document_learning_pack_rebuild_performed')}`",
        f"Generate integration changed: `{policy.get('generate_integration_changed')}`",
        f"Course regeneration performed: `{policy.get('course_regeneration_performed')}`",
        f"Build performed: `{policy.get('build_performed')}`",
        f"ZIP created: `{policy.get('zip_created')}`",
        f"Delivery performed: `{policy.get('delivery_performed')}`",
        f"Distribution performed: `{policy.get('distribution_performed')}`",
        "",
        "## Verified evidence items",
        "",
    ]

    for item in report.get("verified_evidence_items", []):
        linked = ", ".join(str(term) for term in item.get("linked_concept_terms") or [])
        lines.extend(
            [
                f"### {item.get('review_item_id')}",
                "",
                f"- Decision: `{item.get('decision')}`",
                f"- Source: `{item.get('decision_source')}`",
                f"- Confirmed learning role: `{item.get('confirmed_learning_role')}`",
                f"- Ready for learning pack rebuild: `{item.get('ready_for_learning_pack_rebuild')}`",
                f"- Applied to learning pack: `{item.get('applied_to_learning_pack')}`",
                f"- Linked concepts: `{linked or 'n/a'}`",
                f"- Verified evidence text: {item.get('verified_evidence_text')}",
                "",
            ]
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_confirmed_decisions_applied_artifacts(
    decisions_path: Path,
    target_dir: Path | None = None,
) -> dict[str, Any]:
    decisions_path = Path(decisions_path)
    target_dir = Path(target_dir or decisions_path.parent)
    target_dir.mkdir(parents=True, exist_ok=True)

    report = build_confirmed_decisions_applied_report(
        load_json(decisions_path),
        source_path=decisions_path,
    )

    json_path = target_dir / "ocr_review_decisions.applied.json"
    md_path = target_dir / "ocr_review_decisions.applied.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(report, md_path)

    return {
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "decision_count": report["decision_count"],
        "pending_decision_count": report["pending_decision_count"],
        "resolved_decision_count": report["resolved_decision_count"],
        "owner_review_confirmed": report["owner_review_confirmed"],
        "real_user_decisions_performed": report["real_user_decisions_performed"],
        "confirmed_decisions_applied": report["confirmed_decisions_applied"],
        "verified_user_evidence_count": report["verified_user_evidence_count"],
        "generation_should_wait_for_review": report["quality_gate"]["generation_should_wait_for_review"],
        "generation_block_reason": report["quality_gate"]["generation_block_reason"],
        "document_learning_pack_rebuild_performed": report["policy"]["document_learning_pack_rebuild_performed"],
        "generate_integration_changed": report["policy"]["generate_integration_changed"],
        "scope": "owner-local OCR Review confirmed decisions apply artifact only; no learning pack rebuild, no generate integration, no build, no ZIP, no delivery, no distribution",
    }


# VOILA_V0_7_74_OWNER_LOCAL_OCR_REVIEW_CONFIRMED_DECISIONS_APPLY_ARTIFACT_END
