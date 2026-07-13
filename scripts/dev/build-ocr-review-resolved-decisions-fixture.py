from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


FIXTURE_NOTE = "Synthetic resolved fixture for v0.7.68 smoke only; not a real user decision."


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def compact(text: Any) -> str:
    return " ".join(str(text or "").split()).strip()


def resolve_decision(item: dict[str, Any]) -> dict[str, Any]:
    resolved = dict(item)
    suggested_text = compact(resolved.get("suggested_text"))
    source_text = compact(resolved.get("source_text"))

    resolved["decision"] = "accepted"
    resolved["corrected_text"] = suggested_text or source_text
    resolved["confirmed_learning_role"] = compact(resolved.get("suggested_learning_role")) or "glossary_term"
    resolved["requires_user_decision"] = False
    resolved["applied_to_learning_pack"] = True
    resolved["user_note"] = FIXTURE_NOTE
    resolved["fixture_only_not_real_user_decision"] = True
    resolved["decision_source"] = "synthetic_resolved_fixture"
    resolved["updated_at"] = None
    return resolved


def build_resolved_fixture(source: dict[str, Any]) -> dict[str, Any]:
    decisions = [resolve_decision(item) for item in as_list(source.get("decisions")) if isinstance(item, dict)]
    decision_count = len(decisions)

    output = dict(source)
    output["artifact"] = "ocr_review_decisions"
    output["decision_count"] = decision_count
    output["pending_decision_count"] = 0
    output["resolved_decision_count"] = decision_count
    output["decisions"] = decisions
    output["fixture"] = {
        "fixture_only": True,
        "real_user_decisions_performed": False,
        "source": "v0.7.68 synthetic resolved decisions smoke fixture",
        "must_not_be_used_for_real_generation": True,
        "purpose": "prove document_learning_pack can pass when required OCR Review decisions are resolved",
    }
    output["quality_gate"] = {
        "all_required_decisions_resolved": True,
        "generation_should_wait_for_review": False,
        "reason_codes": [],
        "fixture_only": True,
    }

    learning_policy = output.get("learning_policy")
    if not isinstance(learning_policy, dict):
        learning_policy = {}
    learning_policy["synthetic_fixture_not_real_user_evidence"] = True
    learning_policy["real_user_review_still_required_for_actual_delivery"] = True
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
    lines = [
        "# OCR Review Resolved Decisions Fixture",
        "",
        "This is a synthetic smoke fixture.",
        "",
        "It is not a real user decision artifact.",
        "",
        f"Decision count: `{report.get('decision_count')}`",
        f"Pending decision count: `{report.get('pending_decision_count')}`",
        f"Resolved decision count: `{report.get('resolved_decision_count')}`",
        f"All required decisions resolved: `{report.get('quality_gate', {}).get('all_required_decisions_resolved')}`",
        f"Generation should wait: `{report.get('quality_gate', {}).get('generation_should_wait_for_review')}`",
        "",
        "## Policy",
        "",
        "- Fixture only.",
        "- Real user decisions were not performed.",
        "- Must not be used for real generation.",
        "- No UI.",
        "- No `/generate` integration.",
        "- No build.",
        "- No ZIP.",
        "- No delivery.",
        "- No distribution.",
        "",
        "## Decisions",
        "",
    ]

    for item in as_list(report.get("decisions")):
        lines.extend(
            [
                f"### {item.get('review_item_id')}",
                "",
                f"- Decision: `{item.get('decision')}`",
                f"- Confirmed learning role: `{item.get('confirmed_learning_role')}`",
                f"- Fixture only: `{item.get('fixture_only_not_real_user_decision')}`",
                f"- Corrected text: {item.get('corrected_text')}",
                "",
            ]
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_resolved_fixture(source_json: Path, output_dir: Path | None = None) -> dict[str, Any]:
    source_json = Path(source_json).resolve()
    if not source_json.exists():
        raise FileNotFoundError(f"Source OCR Review decisions JSON not found: {source_json}")

    source = json.loads(source_json.read_text(encoding="utf-8"))
    if not isinstance(source, dict):
        raise ValueError("Expected OCR Review decisions JSON object")

    fixture = build_resolved_fixture(source)
    target_dir = Path(output_dir).resolve() if output_dir else source_json.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    json_path = target_dir / "ocr_review_decisions.resolved-fixture.json"
    md_path = target_dir / "ocr_review_decisions.resolved-fixture.md"

    json_path.write_text(json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(fixture, md_path)

    return {
        "OCR_REVIEW_RESOLVED_DECISIONS_FIXTURE": "PASS",
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "decision_count": fixture["decision_count"],
        "pending_decision_count": fixture["pending_decision_count"],
        "resolved_decision_count": fixture["resolved_decision_count"],
        "all_required_decisions_resolved": fixture["quality_gate"]["all_required_decisions_resolved"],
        "generation_should_wait_for_review": fixture["quality_gate"]["generation_should_wait_for_review"],
        "fixture_only": fixture["fixture"]["fixture_only"],
        "real_user_decisions_performed": fixture["fixture"]["real_user_decisions_performed"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build synthetic resolved OCR Review decisions fixture for local smoke only")
    parser.add_argument("ocr_review_decisions_json", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    print(json.dumps(write_resolved_fixture(args.ocr_review_decisions_json, args.output_dir), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
