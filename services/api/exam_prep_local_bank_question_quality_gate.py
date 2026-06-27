"""Dry-run quality gate for local-bank Exam Prep questions.

v0.4.54 validates local-bank dry-run questions before any future live study
consumption. The current local pedagogy scaffold intentionally produces simple
concept-recognition questions; this gate should detect that and mark the bank as
needs_improvement instead of pretending it is production-ready.

Safety invariants:
- no web route
- no user-provided filesystem root
- no attempt persistence
- no answer scoring
- no progress update
- no weak-review changes
- no live study-session replacement
- no cloud/API dependency
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from typing import Any

from exam_prep_local_bank_consumption_flag import CONSUMPTION_FLAG_NAME, LOCAL_SOURCE
from exam_prep_local_bank_dry_run_source_selection import build_dry_run_source_selection


QUALITY_GATE_VERSION = "v0.4.54"
REPETITIVE_PREFIX = "care afirmație identifică"
MIN_QUESTION_COUNT_FOR_PASS = 5
MIN_QUESTION_TYPE_DIVERSITY_FOR_PASS = 2
MAX_REPETITIVE_PREFIX_RATIO_FOR_PASS = 0.6


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _lower_text(value: Any) -> str:
    return _text(value).lower()


def _count_by(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for item in items:
        counter[_text(item.get(key)) or "(missing)"] += 1
    return dict(sorted(counter.items()))


def _required_field_issues(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    required_fields = (
        "question",
        "skill_id",
        "question_type",
        "correct_answer_preview",
        "explanation_preview",
        "source",
    )

    issues: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        missing = [field for field in required_fields if not _text(item.get(field))]
        if missing:
            issues.append(
                {
                    "index": index,
                    "dry_run_item_id": _text(item.get("dry_run_item_id")),
                    "missing_fields": missing,
                }
            )

    return issues


def _repetitive_prefix_count(items: list[dict[str, Any]]) -> int:
    return sum(
        1
        for item in items
        if _lower_text(item.get("question")).startswith(REPETITIVE_PREFIX)
    )


def _simple_question_count(items: list[dict[str, Any]]) -> int:
    simple_markers = (
        "care afirmație identifică",
        "cel mai bine conceptul",
        "conceptul «",
    )
    count = 0
    for item in items:
        question = _lower_text(item.get("question"))
        if any(marker in question for marker in simple_markers):
            count += 1
    return count


def build_quality_gate_snapshot(
    *,
    course_id: str = "v054-sample",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 12,
    enable_local_flag: bool = True,
) -> dict[str, Any]:
    """Build a read-only quality gate result for local-bank dry-run questions."""

    old_flag = os.environ.get(CONSUMPTION_FLAG_NAME)
    try:
        if enable_local_flag:
            os.environ[CONSUMPTION_FLAG_NAME] = "1"
        else:
            os.environ.pop(CONSUMPTION_FLAG_NAME, None)

        dry_run = build_dry_run_source_selection(
            course_id=course_id,
            skill_id=skill_id,
            limit=limit,
            require_local_when_enabled=enable_local_flag,
        )
    finally:
        if old_flag is None:
            os.environ.pop(CONSUMPTION_FLAG_NAME, None)
        else:
            os.environ[CONSUMPTION_FLAG_NAME] = old_flag

    items = [
        item
        for item in dry_run.get("dry_run_items", [])
        if isinstance(item, dict)
    ]

    question_count = len(items)
    question_type_counts = _count_by(items, "question_type")
    difficulty_counts = _count_by(items, "difficulty")
    skill_counts = _count_by(items, "skill_id")
    missing_field_issues = _required_field_issues(items)
    repetitive_count = _repetitive_prefix_count(items)
    simple_count = _simple_question_count(items)

    repetitive_ratio = (
        repetitive_count / question_count
        if question_count
        else 0.0
    )
    simple_ratio = (
        simple_count / question_count
        if question_count
        else 0.0
    )

    issues: list[str] = []

    if dry_run.get("selected_source") != LOCAL_SOURCE:
        issues.append("local_source_not_selected")

    if question_count < MIN_QUESTION_COUNT_FOR_PASS:
        issues.append("too_few_questions_for_quality_pass")

    if len(question_type_counts) < MIN_QUESTION_TYPE_DIVERSITY_FOR_PASS:
        issues.append("insufficient_question_type_diversity")

    if repetitive_ratio > MAX_REPETITIVE_PREFIX_RATIO_FOR_PASS:
        issues.append("repetitive_concept_recognition_prefix")

    if simple_ratio > MAX_REPETITIVE_PREFIX_RATIO_FOR_PASS:
        issues.append("questions_are_too_simple")

    if missing_field_issues:
        issues.append("missing_required_fields")

    quality_gate_pass = not issues
    quality_status = "pass" if quality_gate_pass else "needs_improvement"

    return {
        "schema_version": "1",
        "quality_gate_version": QUALITY_GATE_VERSION,
        "mode": "dry_run_question_quality_gate",
        "quality_status": quality_status,
        "quality_gate_pass": quality_gate_pass,
        "issues": issues,
        "course_id": course_id,
        "skill_id": skill_id,
        "requested_limit": limit,
        "selected_source": dry_run.get("selected_source"),
        "question_count": question_count,
        "question_type_counts": question_type_counts,
        "difficulty_counts": difficulty_counts,
        "skill_counts": skill_counts,
        "repetitive_prefix": REPETITIVE_PREFIX,
        "repetitive_prefix_count": repetitive_count,
        "repetitive_prefix_ratio": round(repetitive_ratio, 4),
        "simple_question_count": simple_count,
        "simple_question_ratio": round(simple_ratio, 4),
        "missing_required_field_issues": missing_field_issues,
        "minimum_question_count_for_pass": MIN_QUESTION_COUNT_FOR_PASS,
        "minimum_question_type_diversity_for_pass": MIN_QUESTION_TYPE_DIVERSITY_FOR_PASS,
        "maximum_repetitive_prefix_ratio_for_pass": MAX_REPETITIVE_PREFIX_RATIO_FOR_PASS,
        "path_policy": "no_user_provided_filesystem_root",
        "will_save_attempt": False,
        "will_update_progress": False,
        "will_score_answer": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
        "dry_run_source_selection": dry_run,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local-bank dry-run question quality gate.")
    parser.add_argument("--course-id", default="v054-sample", help="Diagnostic course id.")
    parser.add_argument("--skill-id", default="local_concept_001_functiile", help="Diagnostic skill id.")
    parser.add_argument("--limit", type=int, default=12, help="Maximum diagnostic dry-run items.")
    parser.add_argument("--disable-local-flag", action="store_true", help="Run with local source flag disabled.")
    parser.add_argument("--expect-needs-improvement", action="store_true", help="Exit non-zero unless gate detects needs_improvement.")
    parser.add_argument("--expect-pass", action="store_true", help="Exit non-zero unless gate passes.")
    args = parser.parse_args()

    result = build_quality_gate_snapshot(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
        enable_local_flag=not args.disable_local_flag,
    )

    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_needs_improvement and result["quality_status"] != "needs_improvement":
        return 2

    if args.expect_pass and not result["quality_gate_pass"]:
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

