from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1"

ALLOWED_DECISIONS = {
    "pending",
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

REQUIRES_TEXT_DECISIONS = {"edited"}


class DecisionPatchError(ValueError):
    pass


def compact(text: Any) -> str:
    return " ".join(str(text or "").split()).strip()


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def load_json(path: Path) -> dict[str, Any]:
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"JSON input not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def decision_items(decisions_artifact: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in as_list(decisions_artifact.get("decisions")) if isinstance(item, dict)]


def patch_items(decision_patch: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in as_list(decision_patch.get("decisions")) if isinstance(item, dict)]


def real_user_patch(decision_patch: dict[str, Any]) -> bool:
    return bool(decision_patch.get("real_user_decisions_performed")) and bool(decision_patch.get("owner_review_confirmed"))


def validate_patch(decisions_artifact: dict[str, Any], decision_patch: dict[str, Any]) -> None:
    existing_ids = {
        compact(item.get("review_item_id"))
        for item in decision_items(decisions_artifact)
        if compact(item.get("review_item_id"))
    }

    seen: set[str] = set()

    for item in patch_items(decision_patch):
        review_item_id = compact(item.get("review_item_id"))
        if not review_item_id:
            raise DecisionPatchError("Patch item missing review_item_id")
        if review_item_id not in existing_ids:
            raise DecisionPatchError(f"Patch references unknown review_item_id: {review_item_id}")
        if review_item_id in seen:
            raise DecisionPatchError(f"Duplicate patch review_item_id: {review_item_id}")
        seen.add(review_item_id)

        decision = compact(item.get("decision"))
        if decision not in ALLOWED_DECISIONS:
            raise DecisionPatchError(f"Unsupported decision for {review_item_id}: {decision}")

        corrected_text = compact(item.get("corrected_text"))
        if decision in REQUIRES_TEXT_DECISIONS and not corrected_text:
            raise DecisionPatchError(f"Decision {decision} requires corrected_text for {review_item_id}")


def normalize_confirmed_role(patch_item: dict[str, Any], original_item: dict[str, Any]) -> str:
    return (
        compact(patch_item.get("confirmed_learning_role"))
        or compact(patch_item.get("suggested_learning_role"))
        or compact(original_item.get("suggested_learning_role"))
        or ""
    )


def normalize_corrected_text(patch_item: dict[str, Any], original_item: dict[str, Any]) -> str:
    return (
        compact(patch_item.get("corrected_text"))
        or compact(patch_item.get("suggested_text"))
        or compact(original_item.get("suggested_text"))
        or compact(original_item.get("source_text"))
    )


def applied_to_learning_pack(decision: str) -> bool:
    return decision not in {"pending", "ignored", "marked_not_relevant"}


def apply_one_decision(
    original_item: dict[str, Any],
    patch_item: dict[str, Any],
    *,
    real_user_decisions_performed: bool,
) -> dict[str, Any]:
    updated = copy.deepcopy(original_item)
    decision = compact(patch_item.get("decision"))

    updated["decision"] = decision
    updated["corrected_text"] = normalize_corrected_text(patch_item, original_item)
    updated["confirmed_learning_role"] = normalize_confirmed_role(patch_item, original_item)
    updated["user_note"] = compact(patch_item.get("user_note"))
    updated["requires_user_decision"] = decision == "pending"
    updated["applied_to_learning_pack"] = applied_to_learning_pack(decision)
    updated["updated_at"] = None

    if real_user_decisions_performed:
        updated["decision_source"] = "owner_user_decision_patch"
        updated["real_user_decision"] = True
        updated["fixture_only_not_real_user_decision"] = False
    else:
        updated["decision_source"] = "owner_local_synthetic_or_unconfirmed_patch"
        updated["real_user_decision"] = False
        updated["fixture_only_not_real_user_decision"] = True

    return updated


def apply_decision_patch(decisions_artifact: dict[str, Any], decision_patch: dict[str, Any]) -> dict[str, Any]:
    validate_patch(decisions_artifact, decision_patch)

    real_user_decisions_performed = real_user_patch(decision_patch)
    patch_by_id = {
        compact(item.get("review_item_id")): item
        for item in patch_items(decision_patch)
    }

    output = copy.deepcopy(decisions_artifact)
    updated_decisions: list[dict[str, Any]] = []
    applied_count = 0

    for item in decision_items(decisions_artifact):
        review_item_id = compact(item.get("review_item_id"))
        patch_item = patch_by_id.get(review_item_id)
        if patch_item is None:
            updated_decisions.append(copy.deepcopy(item))
            continue

        updated_decisions.append(
            apply_one_decision(
                item,
                patch_item,
                real_user_decisions_performed=real_user_decisions_performed,
            )
        )
        applied_count += 1

    pending_count = sum(
        1
        for item in updated_decisions
        if item.get("decision") == "pending" and item.get("requires_user_decision", True)
    )
    resolved_count = len(updated_decisions) - pending_count

    output["schema_version"] = decisions_artifact.get("schema_version") or SCHEMA_VERSION
    output["artifact"] = "ocr_review_decisions"
    output["decision_count"] = len(updated_decisions)
    output["pending_decision_count"] = pending_count
    output["resolved_decision_count"] = resolved_count
    output["applied_patch_decision_count"] = applied_count
    output["decisions"] = updated_decisions
    output["decision_patch"] = {
        "artifact": decision_patch.get("artifact") or "ocr_review_user_decision_patch",
        "real_user_decisions_performed": real_user_decisions_performed,
        "owner_review_confirmed": bool(decision_patch.get("owner_review_confirmed")),
        "synthetic_or_unconfirmed_patch": not real_user_decisions_performed,
        "patch_item_count": len(patch_by_id),
        "applied_patch_decision_count": applied_count,
    }
    output["quality_gate"] = {
        "all_required_decisions_resolved": pending_count == 0,
        "generation_should_wait_for_review": pending_count > 0,
        "reason_codes": ["pending_user_review_decisions"] if pending_count else [],
        "real_user_decisions_performed": real_user_decisions_performed,
        "synthetic_or_unconfirmed_patch": not real_user_decisions_performed,
    }

    learning_policy = output.get("learning_policy")
    if not isinstance(learning_policy, dict):
        learning_policy = {}
    learning_policy["ocr_review_is_user_assisted_document_learning"] = True
    learning_policy["user_corrections_become_verified_evidence"] = real_user_decisions_performed
    learning_policy["synthetic_or_unconfirmed_patch_is_not_verified_evidence"] = not real_user_decisions_performed
    learning_policy["real_user_review_required_for_actual_delivery"] = not real_user_decisions_performed
    learning_policy["pending_decisions_are_not_verified_evidence"] = True
    output["learning_policy"] = learning_policy

    policy = output.get("policy")
    if not isinstance(policy, dict):
        policy = {}
    policy["no_ui_implementation"] = True
    policy["no_generate_integration"] = True
    policy["no_build"] = True
    policy["no_zip"] = True
    policy["no_delivery"] = True
    policy["no_distribution"] = True
    output["policy"] = policy

    return output


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    patch = report.get("decision_patch", {})
    gate = report.get("quality_gate", {})

    lines = [
        "# OCR Review Decisions Applied",
        "",
        f"Decision count: `{report.get('decision_count')}`",
        f"Pending decisions: `{report.get('pending_decision_count')}`",
        f"Resolved decisions: `{report.get('resolved_decision_count')}`",
        f"Applied patch decisions: `{report.get('applied_patch_decision_count')}`",
        f"All required decisions resolved: `{gate.get('all_required_decisions_resolved')}`",
        f"Generation should wait: `{gate.get('generation_should_wait_for_review')}`",
        f"Real user decisions performed: `{patch.get('real_user_decisions_performed')}`",
        f"Synthetic or unconfirmed patch: `{patch.get('synthetic_or_unconfirmed_patch')}`",
        "",
        "## Policy",
        "",
        "- No UI implementation.",
        "- No `/generate` integration.",
        "- No build.",
        "- No ZIP.",
        "- No delivery.",
        "- No distribution.",
        "",
        "## Applied decisions",
        "",
    ]

    for item in as_list(report.get("decisions")):
        lines.extend(
            [
                f"### {item.get('review_item_id')}",
                "",
                f"- Decision: `{item.get('decision')}`",
                f"- Source: `{item.get('decision_source')}`",
                f"- Real user decision: `{item.get('real_user_decision')}`",
                f"- Fixture/unconfirmed: `{item.get('fixture_only_not_real_user_decision')}`",
                f"- Confirmed learning role: `{item.get('confirmed_learning_role')}`",
                f"- Applied to learning pack: `{item.get('applied_to_learning_pack')}`",
                f"- Corrected text: {item.get('corrected_text')}",
                "",
            ]
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_applied_decisions(
    decisions_json: Path,
    decision_patch_json: Path,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    decisions_artifact = load_json(decisions_json)
    decision_patch = load_json(decision_patch_json)
    report = apply_decision_patch(decisions_artifact, decision_patch)

    target_dir = Path(output_dir).resolve() if output_dir else Path(decisions_json).resolve().parent
    target_dir.mkdir(parents=True, exist_ok=True)

    json_path = target_dir / "ocr_review_decisions.applied.json"
    md_path = target_dir / "ocr_review_decisions.applied.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, md_path)

    return {
        "OCR_REVIEW_USER_DECISION_APPLY_HELPER": "PASS",
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "decision_count": report["decision_count"],
        "pending_decision_count": report["pending_decision_count"],
        "resolved_decision_count": report["resolved_decision_count"],
        "applied_patch_decision_count": report["applied_patch_decision_count"],
        "all_required_decisions_resolved": report["quality_gate"]["all_required_decisions_resolved"],
        "generation_should_wait_for_review": report["quality_gate"]["generation_should_wait_for_review"],
        "real_user_decisions_performed": report["decision_patch"]["real_user_decisions_performed"],
        "synthetic_or_unconfirmed_patch": report["decision_patch"]["synthetic_or_unconfirmed_patch"],
        "scope": "owner-local OCR Review decision apply helper only; no UI, no generate integration, no build, no ZIP, no delivery, no distribution",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply owner-local OCR Review decision patch")
    parser.add_argument("ocr_review_decisions_json", type=Path)
    parser.add_argument("decision_patch_json", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    print(
        json.dumps(
            write_applied_decisions(args.ocr_review_decisions_json, args.decision_patch_json, args.output_dir),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
