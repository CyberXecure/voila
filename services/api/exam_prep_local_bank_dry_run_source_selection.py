"""Dry-run local-bank source selection for Exam Prep study sessions.

v0.4.53 introduces a dry-run helper that models which source would be selected
for future Exam Prep study sessions.

It uses the v0.4.52 controlled consumption flag but does not wire the selected
source into live study sessions.

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
from typing import Any

from exam_prep_local_bank_consumption_flag import (
    CONSUMPTION_FLAG_NAME,
    LEGACY_SOURCE,
    LOCAL_SOURCE,
    build_controlled_consumption_snapshot,
)


DRY_RUN_VERSION = "v0.4.53"


def _question_to_dry_run_item(question: dict[str, Any], index: int) -> dict[str, Any]:
    """Convert a selected preview question into a dry-run study item."""

    return {
        "dry_run_item_id": f"dry_run::{index:04d}",
        "question_id": str(question.get("question_id", "")).strip(),
        "source_exercise_id": str(question.get("source_exercise_id", "")).strip(),
        "course_id": str(question.get("course_id", "")).strip(),
        "skill_id": str(question.get("skill_id", "")).strip(),
        "question_type": str(question.get("question_type", "")).strip(),
        "difficulty": str(question.get("difficulty", "")).strip(),
        "question": str(question.get("question", "")).strip(),
        "choices": list(question.get("choices", [])) if isinstance(question.get("choices"), list) else [],
        "correct_answer_preview": str(question.get("correct_answer", "")).strip(),
        "explanation_preview": str(question.get("explanation", "")).strip(),
        "source": str(question.get("source", "")).strip(),
        "dry_run_only": True,
        "will_save_attempt": False,
        "will_update_progress": False,
        "will_score_answer": False,
    }


def build_dry_run_source_selection(
    *,
    course_id: str = "v053-sample",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 3,
    require_local_when_enabled: bool = False,
) -> dict[str, Any]:
    """Build a dry-run study source selection snapshot."""

    snapshot = build_controlled_consumption_snapshot(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
    )

    selected_source = str(snapshot.get("selected_source", LEGACY_SOURCE))
    selected_questions = [
        item
        for item in snapshot.get("selected_questions", [])
        if isinstance(item, dict)
    ]

    dry_run_items = [
        _question_to_dry_run_item(question, index)
        for index, question in enumerate(selected_questions, start=1)
    ]

    if selected_source == LOCAL_SOURCE and dry_run_items:
        dry_run_status = "local_bank_selected_for_dry_run"
    elif selected_source == LOCAL_SOURCE:
        dry_run_status = "local_bank_selected_but_empty"
    else:
        dry_run_status = "legacy_fallback_selected_for_dry_run"

    if require_local_when_enabled and snapshot.get("flag_enabled") and selected_source != LOCAL_SOURCE:
        dry_run_status = "flag_enabled_but_local_source_not_selected"

    return {
        "schema_version": "1",
        "dry_run_version": DRY_RUN_VERSION,
        "mode": "dry_run_source_selection",
        "flag_name": CONSUMPTION_FLAG_NAME,
        "flag_enabled": bool(snapshot.get("flag_enabled", False)),
        "default_source": LEGACY_SOURCE,
        "selected_source": selected_source,
        "dry_run_status": dry_run_status,
        "selection_reason": snapshot.get("selection_reason", ""),
        "course_id": course_id,
        "skill_id": skill_id,
        "requested_limit": limit,
        "dry_run_item_count": len(dry_run_items),
        "dry_run_items": dry_run_items,
        "legacy_fallback_available": bool(snapshot.get("legacy_fallback_available", True)),
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
        "source_selection_snapshot": snapshot,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run local-bank source selection for Exam Prep.")
    parser.add_argument("--course-id", default="v053-sample", help="Diagnostic course id.")
    parser.add_argument("--skill-id", default="local_concept_001_functiile", help="Diagnostic skill id.")
    parser.add_argument("--limit", type=int, default=3, help="Maximum diagnostic dry-run items.")
    parser.add_argument("--strict-local", action="store_true", help="Exit non-zero unless local source is selected.")
    parser.add_argument("--strict-legacy", action="store_true", help="Exit non-zero unless legacy fallback is selected.")
    args = parser.parse_args()

    result = build_dry_run_source_selection(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
        require_local_when_enabled=args.strict_local,
    )

    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.strict_local and result["selected_source"] != LOCAL_SOURCE:
        return 2
    if args.strict_local and result["dry_run_item_count"] <= 0:
        return 3
    if args.strict_legacy and result["selected_source"] != LEGACY_SOURCE:
        return 4

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

