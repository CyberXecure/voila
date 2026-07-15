from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import document_learning_pack as dlp


# VOILA_V0_7_75_OWNER_LOCAL_DOCUMENT_LEARNING_PACK_REBUILD_FROM_APPLIED_OCR_REVIEW_START
# Owner-local document learning pack rebuild from applied OCR Review evidence.
# Policy: rebuild document_learning_pack.json/md from verified OCR Review evidence only.
# No /generate integration, no course regeneration, no build, no ZIP, no delivery, no distribution.

class AppliedReviewLearningPackError(RuntimeError):
    """Raised when applied OCR Review evidence is not ready for learning-pack rebuild."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        raise AppliedReviewLearningPackError("Invalid JSON artifact") from exc
    if not isinstance(data, dict):
        raise AppliedReviewLearningPackError("Artifact must be a JSON object")
    return data


def as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def bool_true(value: Any) -> bool:
    return value is True


def validate_applied_review_artifact(applied_review: dict[str, Any]) -> list[dict[str, Any]]:
    if applied_review.get("artifact") != "ocr_review_confirmed_decisions_applied":
        raise AppliedReviewLearningPackError("Expected ocr_review_confirmed_decisions_applied artifact")
    if applied_review.get("artifact_version") != "v0.7.74":
        raise AppliedReviewLearningPackError("Expected v0.7.74 applied OCR Review artifact")
    if not bool_true(applied_review.get("owner_review_confirmed")):
        raise AppliedReviewLearningPackError("owner_review_confirmed must be true")
    if not bool_true(applied_review.get("real_user_decisions_performed")):
        raise AppliedReviewLearningPackError("real_user_decisions_performed must be true")
    if not bool_true(applied_review.get("confirmed_decisions_applied")):
        raise AppliedReviewLearningPackError("confirmed_decisions_applied must be true")
    if int(applied_review.get("pending_decision_count") or 0) != 0:
        raise AppliedReviewLearningPackError("pending_decision_count must be zero")

    gate = applied_review.get("quality_gate")
    if not isinstance(gate, dict):
        raise AppliedReviewLearningPackError("quality_gate missing from applied OCR Review artifact")
    if not bool_true(gate.get("all_required_decisions_resolved")):
        raise AppliedReviewLearningPackError("all_required_decisions_resolved must be true")
    if not bool_true(gate.get("owner_review_confirmed")):
        raise AppliedReviewLearningPackError("quality_gate.owner_review_confirmed must be true")
    if not bool_true(gate.get("confirmed_decisions_applied")):
        raise AppliedReviewLearningPackError("quality_gate.confirmed_decisions_applied must be true")

    verified = as_dict_list(applied_review.get("verified_evidence_items"))
    if not verified:
        raise AppliedReviewLearningPackError("verified_evidence_items must not be empty")

    for item in verified:
        if item.get("verified_user_evidence") is not True:
            raise AppliedReviewLearningPackError("verified evidence item missing verified_user_evidence=true")
        if item.get("ready_for_learning_pack_rebuild") is not True:
            raise AppliedReviewLearningPackError("verified evidence item not ready for learning pack rebuild")
        if item.get("real_user_decision") is not True:
            raise AppliedReviewLearningPackError("verified evidence item is not real user decision")
        if item.get("requires_user_decision") is not False:
            raise AppliedReviewLearningPackError("verified evidence item still requires user decision")

    return verified


def decisions_artifact_for_learning_pack(applied_review: dict[str, Any]) -> dict[str, Any]:
    applied_decisions = as_dict_list(applied_review.get("applied_decisions"))
    if not applied_decisions:
        raise AppliedReviewLearningPackError("applied_decisions must not be empty")

    return {
        "artifact": "ocr_review_decisions_applied_for_document_learning_pack",
        "artifact_version": "v0.7.75",
        "source_artifact": applied_review.get("artifact"),
        "source_artifact_version": applied_review.get("artifact_version"),
        "decision_count": len(applied_decisions),
        "pending_decision_count": 0,
        "resolved_decision_count": len(applied_decisions),
        "owner_review_confirmed": True,
        "real_user_decisions_performed": True,
        "confirmed_decisions_applied": True,
        "decisions": applied_decisions,
        "quality_gate": {
            "all_required_decisions_resolved": True,
            "owner_review_confirmed": True,
            "confirmed_decisions_applied": True,
            "generation_should_wait_for_review": False,
            "source": "applied_ocr_review_v0.7.74",
        },
    }


def enrich_pack_with_applied_review(
    pack: dict[str, Any],
    applied_review: dict[str, Any],
    verified_items: list[dict[str, Any]],
) -> dict[str, Any]:
    pack["rebuild_artifact_version"] = "v0.7.75"
    pack["artifact_rebuild_source"] = "ocr_review_decisions.applied.json"
    pack["document_learning_pack_rebuilt_from_applied_ocr_review"] = True

    inputs = pack.get("inputs")
    if not isinstance(inputs, dict):
        inputs = {}
    inputs["ocr_review_decisions_applied_artifact"] = applied_review.get("artifact")
    inputs["ocr_review_decisions_applied_artifact_version"] = applied_review.get("artifact_version")
    pack["inputs"] = inputs

    review_summary = pack.get("ocr_review_summary")
    if not isinstance(review_summary, dict):
        review_summary = {}
    review_summary["confirmed_decisions_applied"] = True
    review_summary["owner_review_confirmed"] = True
    review_summary["verified_user_evidence_count_from_applied_review"] = len(verified_items)
    review_summary["applied_review_source_artifact"] = applied_review.get("artifact")
    pack["ocr_review_summary"] = review_summary

    pack["verified_user_evidence"] = {
        "verified_decision_count": len(verified_items),
        "source_artifact": "ocr_review_decisions.applied.json",
        "source_artifact_version": applied_review.get("artifact_version"),
        "items": verified_items,
        "verified_user_evidence_from_applied_ocr_review": True,
        "pending_decisions_are_not_verified_evidence": True,
    }

    gate = pack.get("quality_gate")
    if not isinstance(gate, dict):
        gate = {}
    gate["document_learning_pack_rebuilt_from_applied_ocr_review"] = True
    gate["confirmed_decisions_applied"] = True
    gate["owner_review_confirmed"] = True
    gate["verified_user_evidence_count"] = len(verified_items)
    gate["generate_integration_enabled"] = False
    gate["generator_route_changed"] = False
    gate["course_regeneration_performed"] = False
    pack["quality_gate"] = gate

    learning_policy = pack.get("learning_policy")
    if not isinstance(learning_policy, dict):
        learning_policy = {}
    learning_policy["applied_ocr_review_evidence_used"] = True
    learning_policy["verified_user_evidence_from_final_ocr_review"] = True
    learning_policy["document_learning_pack_rebuilt_before_teaching"] = True
    learning_policy["generate_integration_requires_separate_milestone"] = True
    pack["learning_policy"] = learning_policy

    pack["policy"] = {
        "owner_local_only": True,
        "document_learning_pack_rebuild_performed": True,
        "rebuild_source": "ocr_review_decisions.applied.json",
        "generate_integration_changed": False,
        "course_regeneration_performed": False,
        "build_performed": False,
        "zip_created": False,
        "delivery_performed": False,
        "distribution_performed": False,
    }

    return pack


def build_document_learning_pack_from_applied_review(
    document_concepts: dict[str, Any],
    ocr_review_queue: dict[str, Any],
    applied_review: dict[str, Any],
) -> dict[str, Any]:
    verified_items = validate_applied_review_artifact(applied_review)
    decisions_for_pack = decisions_artifact_for_learning_pack(applied_review)
    pack = dlp.build_document_learning_pack(
        document_concepts,
        ocr_review_queue,
        decisions_for_pack,
    )
    return enrich_pack_with_applied_review(pack, applied_review, verified_items)


def append_rebuild_markdown_section(report: dict[str, Any], md_path: Path) -> None:
    gate = report.get("quality_gate", {})
    policy = report.get("policy", {})
    evidence = report.get("verified_user_evidence", {})

    with Path(md_path).open("a", encoding="utf-8") as handle:
        handle.write("\n## v0.7.75 Applied OCR Review rebuild\n\n")
        handle.write(f"Rebuilt from applied OCR Review: `{report.get('document_learning_pack_rebuilt_from_applied_ocr_review')}`\n\n")
        handle.write(f"Verified user evidence count: `{evidence.get('verified_decision_count')}`\n\n")
        handle.write(f"Document learning status: `{gate.get('document_learning_status')}`\n\n")
        handle.write(f"Generation allowed inside pack: `{gate.get('generation_allowed')}`\n\n")
        handle.write(f"Generate integration enabled: `{gate.get('generate_integration_enabled')}`\n\n")
        handle.write(f"Course regeneration performed: `{policy.get('course_regeneration_performed')}`\n\n")
        handle.write(f"Build performed: `{policy.get('build_performed')}`\n\n")
        handle.write(f"ZIP created: `{policy.get('zip_created')}`\n\n")
        handle.write(f"Delivery performed: `{policy.get('delivery_performed')}`\n\n")


def write_document_learning_pack_from_applied_review(
    document_concepts_json: Path,
    output_dir: Path,
    ocr_review_queue_json: Path,
    ocr_review_decisions_applied_json: Path,
) -> dict[str, Any]:
    concepts = load_json(Path(document_concepts_json))
    queue = load_json(Path(ocr_review_queue_json))
    applied_review = load_json(Path(ocr_review_decisions_applied_json))

    report = build_document_learning_pack_from_applied_review(
        concepts,
        queue,
        applied_review,
    )

    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / "document_learning_pack.json"
    md_path = target_dir / "document_learning_pack.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    dlp.write_markdown(report, md_path)
    append_rebuild_markdown_section(report, md_path)

    return {
        "DOCUMENT_LEARNING_PACK_REBUILD_FROM_APPLIED_OCR_REVIEW": "PASS",
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "concept_count": report["quality_gate"]["concept_count"],
        "review_item_count": report["quality_gate"]["review_item_count"],
        "pending_decision_count": report["quality_gate"]["pending_decision_count"],
        "document_learning_status": report["quality_gate"]["document_learning_status"],
        "generation_allowed": report["quality_gate"]["generation_allowed"],
        "verified_user_evidence_count": report["quality_gate"]["verified_user_evidence_count"],
        "document_learning_pack_rebuild_performed": report["policy"]["document_learning_pack_rebuild_performed"],
        "generate_integration_changed": report["policy"]["generate_integration_changed"],
        "course_regeneration_performed": report["policy"]["course_regeneration_performed"],
        "scope": "owner-local document learning pack rebuild from applied OCR Review only; no generate integration, no build, no ZIP, no delivery, no distribution",
    }


# VOILA_V0_7_75_OWNER_LOCAL_DOCUMENT_LEARNING_PACK_REBUILD_FROM_APPLIED_OCR_REVIEW_END
