from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1"

BLOCKED_BY_PENDING_REVIEW = "OCR_REVIEW_PENDING_BLOCKED"
BLOCKED_BY_LOW_CONCEPT_COUNT = "LOW_QUALITY_BLOCKED"
PASS = "PASS"


def compact(text: str) -> str:
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


def concept_items(document_concepts: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in as_list(document_concepts.get("concepts")) if isinstance(item, dict)]


def review_items(ocr_review_queue: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not ocr_review_queue:
        return []
    return [item for item in as_list(ocr_review_queue.get("review_items")) if isinstance(item, dict)]


def decision_items(ocr_review_decisions: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not ocr_review_decisions:
        return []
    return [item for item in as_list(ocr_review_decisions.get("decisions")) if isinstance(item, dict)]


def pending_decisions(decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item for item in decisions if item.get("decision") == "pending" and item.get("requires_user_decision", True)]


def verified_decisions(decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    verified: list[dict[str, Any]] = []
    for item in decisions:
        decision = item.get("decision")
        if decision in {None, "", "pending", "ignored", "marked_not_relevant"}:
            continue
        verified.append(item)
    return verified


def pending_review_terms(items: list[dict[str, Any]], decisions: list[dict[str, Any]]) -> set[str]:
    terms: set[str] = set()

    for item in items:
        for term in as_list(item.get("linked_concept_terms")):
            cleaned = compact(term).lower()
            if cleaned:
                terms.add(cleaned)

    for item in decisions:
        if item.get("decision") in {None, "", "pending"}:
            for term in as_list(item.get("linked_concept_terms")):
                cleaned = compact(term).lower()
                if cleaned:
                    terms.add(cleaned)

    return terms


def concept_map(concepts: list[dict[str, Any]], review_terms: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(concepts, start=1):
        term = compact(item.get("term"))
        rows.append(
            {
                "concept_id": f"C{index:03d}",
                "term": term,
                "definition": compact(item.get("definition")),
                "source_pdf_pages": as_list(item.get("source_pdf_pages")),
                "evidence": compact(item.get("evidence")),
                "extraction_method": item.get("extraction_method"),
                "verified_by_user": False,
                "needs_review_before_generation": term.lower() in review_terms,
            }
        )
    return rows


def pending_review_summary(items: list[dict[str, Any]], decisions: list[dict[str, Any]]) -> dict[str, Any]:
    pending = pending_decisions(decisions)
    verified = verified_decisions(decisions)
    issue_types = sorted({compact(item.get("issue_type")) for item in items if compact(item.get("issue_type"))})
    roles = sorted({compact(item.get("suggested_learning_role")) for item in items if compact(item.get("suggested_learning_role"))})

    return {
        "review_item_count": len(items),
        "decision_count": len(decisions),
        "pending_decision_count": len(pending),
        "verified_decision_count": len(verified),
        "all_required_decisions_resolved": len(pending) == 0 and len(decisions) == len(items),
        "generation_should_wait_for_review": len(pending) > 0 or (len(items) > 0 and len(decisions) == 0),
        "issue_types": issue_types,
        "suggested_learning_roles": roles,
    }


def glossary_candidates(concepts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "term": compact(item.get("term")),
            "definition": compact(item.get("definition")),
            "source_pdf_pages": as_list(item.get("source_pdf_pages")),
            "candidate_status": "candidate_only_not_generator_ready",
        }
        for item in concepts
        if compact(item.get("term")) and compact(item.get("definition"))
    ]


def flashcard_candidates(concepts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for item in concepts:
        term = compact(item.get("term"))
        definition = compact(item.get("definition"))
        if not term or not definition:
            continue
        cards.append(
            {
                "front": f"Ce înseamnă: {term}?",
                "back": definition,
                "source_pdf_pages": as_list(item.get("source_pdf_pages")),
                "candidate_status": "candidate_only_not_generator_ready",
            }
        )
    return cards


def quiz_candidates(concepts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    for item in concepts:
        term = compact(item.get("term"))
        definition = compact(item.get("definition"))
        if not term or not definition:
            continue
        questions.append(
            {
                "question": f"Care este ideea principală pentru «{term}»?",
                "expected_answer": definition,
                "source_pdf_pages": as_list(item.get("source_pdf_pages")),
                "candidate_status": "candidate_only_not_generator_ready",
            }
        )
    return questions


def teaching_plan(concepts: list[dict[str, Any]], review_summary: dict[str, Any]) -> dict[str, Any]:
    ordered = sorted(
        concepts,
        key=lambda item: (as_list(item.get("source_pdf_pages")) or [999])[0],
    )

    lessons: list[dict[str, Any]] = []
    for index, item in enumerate(ordered, start=1):
        term = compact(item.get("term"))
        if not term:
            continue
        lessons.append(
            {
                "lesson_candidate_id": f"LC{index:03d}",
                "title": term,
                "objective": f"Înțelege conceptul «{term}» din documentul sursă.",
                "source_pdf_pages": as_list(item.get("source_pdf_pages")),
                "candidate_status": "blocked_until_review_resolved"
                if review_summary["generation_should_wait_for_review"]
                else "candidate_ready_for_future_generator",
            }
        )

    return {
        "lesson_sequence_candidates": lessons,
        "glossary_candidates": glossary_candidates(concepts),
        "flashcard_candidates": flashcard_candidates(concepts),
        "quiz_candidates": quiz_candidates(concepts),
        "teaching_plan_status": "blocked_until_review_resolved"
        if review_summary["generation_should_wait_for_review"]
        else "candidate_ready_for_future_generator",
    }


def quality_gate(concepts: list[dict[str, Any]], review_summary: dict[str, Any]) -> dict[str, Any]:
    reason_codes: list[str] = []

    if len(concepts) < 3:
        status = BLOCKED_BY_LOW_CONCEPT_COUNT
        reason_codes.append("too_few_document_concepts")
    elif review_summary["generation_should_wait_for_review"]:
        status = BLOCKED_BY_PENDING_REVIEW
        reason_codes.append("pending_ocr_review_decisions")
    else:
        status = PASS

    return {
        "document_learning_status": status,
        "generation_allowed": status == PASS,
        "concept_count": len(concepts),
        "minimum_recommended_concepts": 3,
        "pending_decision_count": review_summary["pending_decision_count"],
        "review_item_count": review_summary["review_item_count"],
        "reason_codes": reason_codes,
    }


def build_document_learning_pack(
    document_concepts: dict[str, Any],
    ocr_review_queue: dict[str, Any] | None = None,
    ocr_review_decisions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    concepts = concept_items(document_concepts)
    queue_items = review_items(ocr_review_queue)
    decisions = decision_items(ocr_review_decisions)
    review_summary = pending_review_summary(queue_items, decisions)
    review_terms = pending_review_terms(queue_items, decisions)
    review_summary["review_linked_concept_terms"] = sorted(review_terms)
    gate = quality_gate(concepts, review_summary)

    source_file = document_concepts.get("source_file")
    source_page_count = document_concepts.get("source_page_count")

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact": "document_learning_pack",
        "source_file": source_file,
        "source_page_count": source_page_count,
        "inputs": {
            "document_concepts_artifact": document_concepts.get("artifact"),
            "ocr_review_queue_artifact": ocr_review_queue.get("artifact") if ocr_review_queue else None,
            "ocr_review_decisions_artifact": ocr_review_decisions.get("artifact") if ocr_review_decisions else None,
        },
        "source_language": document_concepts.get("source_language"),
        "detected_domain": document_concepts.get("detected_domain"),
        "concept_summary": {
            "concept_count": len(concepts),
            "concepts": concept_map(concepts, review_terms),
        },
        "ocr_review_summary": review_summary,
        "verified_user_evidence": {
            "verified_decision_count": len(verified_decisions(decisions)),
            "items": verified_decisions(decisions),
            "pending_decisions_are_not_verified_evidence": True,
        },
        "teaching_plan": teaching_plan(concepts, review_summary),
        "quality_gate": gate,
        "learning_policy": {
            "learn_document_before_teaching": True,
            "ocr_review_is_user_assisted_document_learning": True,
            "user_corrections_become_verified_evidence": True,
            "pending_decisions_are_not_verified_evidence": True,
            "do_not_generate_from_unresolved_blocked_items": True,
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
    gate = report.get("quality_gate", {})
    review = report.get("ocr_review_summary", {})
    concepts = report.get("concept_summary", {}).get("concepts") or []

    lines = [
        "# Document Learning Pack",
        "",
        f"Source file: `{report.get('source_file')}`",
        f"Source pages: `{report.get('source_page_count')}`",
        f"Concept count: `{gate.get('concept_count')}`",
        f"Review item count: `{review.get('review_item_count')}`",
        f"Pending decisions: `{review.get('pending_decision_count')}`",
        f"Learning status: `{gate.get('document_learning_status')}`",
        f"Generation allowed: `{gate.get('generation_allowed')}`",
        "",
        "## Concepts",
        "",
    ]

    for concept in concepts:
        pages = ", ".join(str(page) for page in concept.get("source_pdf_pages") or [])
        lines.extend(
            [
                f"### {concept.get('concept_id')} · {concept.get('term')}",
                "",
                f"- Definition: {concept.get('definition')}",
                f"- Source pages: `{pages or 'n/a'}`",
                f"- Extraction method: `{concept.get('extraction_method')}`",
                "",
            ]
        )

    lines.extend(
        [
            "## OCR Review",
            "",
            f"- Review items: `{review.get('review_item_count')}`",
            f"- Decisions: `{review.get('decision_count')}`",
            f"- Pending decisions: `{review.get('pending_decision_count')}`",
            f"- Generation should wait: `{review.get('generation_should_wait_for_review')}`",
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
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_document_learning_pack(
    document_concepts_json: Path,
    output_dir: Path | None = None,
    ocr_review_queue_json: Path | None = None,
    ocr_review_decisions_json: Path | None = None,
) -> dict[str, Any]:
    concepts = load_json(document_concepts_json)
    queue = load_json(ocr_review_queue_json) if ocr_review_queue_json else None
    decisions = load_json(ocr_review_decisions_json) if ocr_review_decisions_json else None

    report = build_document_learning_pack(concepts, queue, decisions)

    target_dir = Path(output_dir).resolve() if output_dir else Path(document_concepts_json).resolve().parent
    target_dir.mkdir(parents=True, exist_ok=True)

    json_path = target_dir / "document_learning_pack.json"
    md_path = target_dir / "document_learning_pack.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, md_path)

    return {
        "DOCUMENT_LEARNING_PACK_ARTIFACT": "PASS",
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "concept_count": report["quality_gate"]["concept_count"],
        "review_item_count": report["quality_gate"]["review_item_count"],
        "pending_decision_count": report["quality_gate"]["pending_decision_count"],
        "document_learning_status": report["quality_gate"]["document_learning_status"],
        "generation_allowed": report["quality_gate"]["generation_allowed"],
        "scope": "owner-local document learning pack artifact only; no UI, no generate integration, no build, no ZIP, no delivery, no distribution",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build owner-local document learning pack from concepts and OCR Review artifacts")
    parser.add_argument("document_concepts_json", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--ocr-review-queue-json", type=Path, default=None)
    parser.add_argument("--ocr-review-decisions-json", type=Path, default=None)
    args = parser.parse_args()

    print(
        json.dumps(
            write_document_learning_pack(
                args.document_concepts_json,
                args.output_dir,
                args.ocr_review_queue_json,
                args.ocr_review_decisions_json,
            ),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
