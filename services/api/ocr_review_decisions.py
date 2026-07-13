from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1"

ALLOWED_DECISIONS = [
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
]


def compact(text: str) -> str:
    return " ".join(str(text or "").split()).strip()


def review_items_from_queue(queue: dict[str, Any]) -> list[dict[str, Any]]:
    items = queue.get("review_items")
    return items if isinstance(items, list) else []


def build_pending_decision(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "review_item_id": item.get("review_item_id"),
        "decision": "pending",
        "allowed_decisions": ALLOWED_DECISIONS,
        "source_pdf_page": item.get("source_pdf_page"),
        "source_text": item.get("source_text"),
        "suggested_text": item.get("suggested_text"),
        "corrected_text": "",
        "original_issue_type": item.get("issue_type"),
        "suggested_learning_role": item.get("suggested_learning_role"),
        "confirmed_learning_role": "",
        "linked_concept_terms": item.get("linked_concept_terms") or [],
        "user_note": "",
        "requires_user_decision": bool(item.get("requires_user_decision", True)),
        "applied_to_learning_pack": False,
        "created_at": None,
        "updated_at": None,
    }


def build_ocr_review_decisions(queue: dict[str, Any]) -> dict[str, Any]:
    review_items = review_items_from_queue(queue)
    decisions = [build_pending_decision(item) for item in review_items]
    pending_count = sum(1 for item in decisions if item.get("decision") == "pending")

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact": "ocr_review_decisions",
        "source_queue_artifact": queue.get("artifact"),
        "source_file": queue.get("source_file"),
        "source_page_count": queue.get("source_page_count"),
        "source_review_item_count": len(review_items),
        "decision_count": len(decisions),
        "pending_decision_count": pending_count,
        "decisions": decisions,
        "quality_gate": {
            "all_required_decisions_resolved": pending_count == 0,
            "generation_should_wait_for_review": pending_count > 0,
            "reason_codes": ["pending_user_review_decisions"] if pending_count else [],
        },
        "learning_policy": {
            "ocr_review_is_user_assisted_document_learning": True,
            "user_corrections_become_verified_evidence": True,
            "feed_back_into_document_learning_pack": True,
            "do_not_generate_from_unresolved_blocked_items": True,
            "pending_decisions_are_not_verified_evidence": True,
        },
        "policy": {
            "no_ui_implementation": True,
            "no_generate_integration": True,
            "no_lesson_generation": True,
            "no_quiz_generation": True,
            "no_flashcard_generation": True,
            "no_glossary_generation": True,
            "no_build": True,
            "no_zip": True,
            "no_delivery": True,
            "no_distribution": True,
        },
    }


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# OCR Review Decisions",
        "",
        f"Source file: `{report.get('source_file')}`",
        f"Source pages: `{report.get('source_page_count')}`",
        f"Source review items: `{report.get('source_review_item_count')}`",
        f"Decision count: `{report.get('decision_count')}`",
        f"Pending decisions: `{report.get('pending_decision_count')}`",
        f"Generation should wait: `{report.get('quality_gate', {}).get('generation_should_wait_for_review')}`",
        "",
        "## Pending decisions",
        "",
    ]

    for item in report.get("decisions") or []:
        linked = ", ".join(item.get("linked_concept_terms") or [])
        lines.extend(
            [
                f"### {item.get('review_item_id')} · page {item.get('source_pdf_page')}",
                "",
                f"- Decision: `{item.get('decision')}`",
                f"- Original issue type: `{item.get('original_issue_type')}`",
                f"- Suggested learning role: `{item.get('suggested_learning_role')}`",
                f"- Confirmed learning role: `{item.get('confirmed_learning_role') or 'pending'}`",
                f"- Applied to learning pack: `{item.get('applied_to_learning_pack')}`",
                f"- Linked concepts: `{linked or 'n/a'}`",
                f"- Source text: {item.get('source_text')}",
                f"- Suggested text: {item.get('suggested_text')}",
                "",
            ]
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_ocr_review_decisions(queue_json: Path, output_dir: Path | None = None) -> dict[str, Any]:
    queue_json = Path(queue_json).resolve()
    if not queue_json.exists():
        raise FileNotFoundError(f"ocr_review_queue.json not found: {queue_json}")

    queue = json.loads(queue_json.read_text(encoding="utf-8"))
    report = build_ocr_review_decisions(queue)

    target_dir = Path(output_dir).resolve() if output_dir else queue_json.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    json_path = target_dir / "ocr_review_decisions.json"
    md_path = target_dir / "ocr_review_decisions.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, md_path)

    return {
        "OCR_REVIEW_DECISIONS_ARTIFACT": "PASS",
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "decision_count": report["decision_count"],
        "pending_decision_count": report["pending_decision_count"],
        "generation_should_wait_for_review": report["quality_gate"]["generation_should_wait_for_review"],
        "scope": "owner-local OCR Review decisions artifact only; no UI, no generate integration, no build, no ZIP, no delivery, no distribution",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build owner-local OCR Review decisions artifact from ocr_review_queue.json")
    parser.add_argument("ocr_review_queue_json", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    print(json.dumps(write_ocr_review_decisions(args.ocr_review_queue_json, args.output_dir), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
