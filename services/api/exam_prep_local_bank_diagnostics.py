"""Read-only diagnostics for Exam Prep local bank adapter output.

v0.4.48 is diagnostics-only. It reports availability and shape of normalized
local bank questions without changing live Exam Prep routes, UI, scoring,
progress, weak review, or legacy generator behavior.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from exam_prep_local_bank_adapter import ADAPTER_SOURCE, build_local_bank_adapter_preview


DIAGNOSTICS_VERSION = "v0.4.48"
REQUIRED_NORMALIZED_FIELDS = (
    "question_id",
    "source_exercise_id",
    "course_id",
    "skill_id",
    "question_type",
    "difficulty",
    "question",
    "correct_answer",
    "explanation",
    "source",
)


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _has_text(value: Any) -> bool:
    return bool(_text(value))


def _count_by(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for item in items:
        value = _text(item.get(key)) or "(missing)"
        counter[value] += 1
    return dict(sorted(counter.items()))


def validate_normalized_questions(questions: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate normalized adapter records for diagnostics."""

    missing: list[dict[str, Any]] = []
    duplicate_ids: list[str] = []
    seen_ids: set[str] = set()

    for index, question in enumerate(questions):
        missing_fields = [
            field
            for field in REQUIRED_NORMALIZED_FIELDS
            if not _has_text(question.get(field))
        ]

        question_id = _text(question.get("question_id"))
        if question_id:
            if question_id in seen_ids:
                duplicate_ids.append(question_id)
            seen_ids.add(question_id)

        if missing_fields:
            missing.append(
                {
                    "index": index,
                    "question_id": question_id,
                    "missing_fields": missing_fields,
                }
            )

    return {
        "valid": not missing and not duplicate_ids,
        "missing_required_fields": missing,
        "duplicate_question_ids": duplicate_ids,
        "checked_question_count": len(questions),
    }


def build_exam_prep_local_bank_diagnostics(
    root: str | Path,
    *,
    course_id: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Build read-only diagnostics over local bank adapter output."""

    preview = build_local_bank_adapter_preview(root, course_id=course_id, limit=limit)
    questions = [
        item
        for item in preview.get("questions", [])
        if isinstance(item, dict)
    ]
    validation = validate_normalized_questions(questions)

    active_source = _text(preview.get("active_source_adapter"))
    local_available = active_source == ADAPTER_SOURCE and bool(questions)

    warnings: list[str] = []
    if not local_available:
        warnings.append("No valid local adapter questions are available; Exam Prep should use legacy fallback.")
    if not validation["valid"]:
        warnings.append("Normalized local questions failed diagnostics validation.")

    return {
        "schema_version": "1",
        "diagnostics_version": DIAGNOSTICS_VERSION,
        "mode": "read_only_diagnostics",
        "course_id_filter": course_id or "",
        "root": str(Path(root)),
        "active_source_adapter": active_source or "legacy_fallback",
        "local_bank_available": local_available,
        "local_question_count": len(questions),
        "legacy_fallback_available": bool(preview.get("legacy_fallback_available", True)),
        "legacy_fallback_policy": preview.get(
            "legacy_fallback_policy",
            "Use legacy quiz/question data when no valid local source exists.",
        ),
        "coverage": {
            "question_types": _count_by(questions, "question_type"),
            "difficulty": _count_by(questions, "difficulty"),
            "skills": _count_by(questions, "skill_id"),
        },
        "sample_question_ids": [_text(item.get("question_id")) for item in questions[:10]],
        "validation": validation,
        "warnings": warnings,
        "will_modify_progress": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_scoring": False,
        "will_modify_weak_review": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build read-only Exam Prep local bank diagnostics.")
    parser.add_argument("--root", required=True, help="Root directory to search.")
    parser.add_argument("--course-id", default="", help="Optional course_id filter.")
    parser.add_argument("--limit", type=int, default=0, help="Optional maximum number of normalized questions.")
    parser.add_argument("--strict-local", action="store_true", help="Exit non-zero when no local diagnostics are available.")
    args = parser.parse_args()

    diagnostics = build_exam_prep_local_bank_diagnostics(
        args.root,
        course_id=args.course_id or None,
        limit=args.limit or None,
    )

    print(json.dumps(diagnostics, ensure_ascii=True, indent=2))

    if args.strict_local and not diagnostics["local_bank_available"]:
        return 2
    if args.strict_local and not diagnostics["validation"]["valid"]:
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

