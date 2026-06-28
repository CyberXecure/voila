"""Dry-run progress impact preview for local-bank Exam Prep sessions.

v0.4.59 simulates how a dry-run local-bank session summary could affect mastery
for a skill. It does not write progress, persist sessions, persist attempts,
score live study sessions, or replace live Exam Prep behavior.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from exam_prep_local_bank_dry_run_session_summary import (
    SESSION_SUMMARY_VERSION,
    build_session_summary,
)


PROGRESS_IMPACT_PREVIEW_VERSION = "v0.4.59"


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def compute_mastery_delta(
    *,
    correct_count: int,
    partial_count: int,
    incorrect_count: int,
    total_questions: int,
) -> float:
    """Compute a deterministic preview-only mastery delta."""

    if total_questions <= 0:
        return 0.0

    raw_delta = (
        (correct_count * 0.05)
        + (partial_count * 0.02)
        - (incorrect_count * 0.03)
    )
    normalized_delta = raw_delta / max(total_questions, 1)
    return round(normalized_delta, 4)


def build_progress_impact_preview(
    *,
    course_id: str = "v059-sample",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    sample_mode: str = "correct",
    old_mastery_preview: float = 0.40,
) -> dict[str, Any]:
    """Build a non-persistent progress impact preview."""

    session = build_session_summary(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        sample_mode=sample_mode,
    )

    total_questions = int(session.get("total_questions", 0) or 0)
    correct_count = int(session.get("correct_count", 0) or 0)
    partial_count = int(session.get("partial_count", 0) or 0)
    incorrect_count = int(session.get("incorrect_count", 0) or 0)

    old_mastery = clamp01(float(old_mastery_preview))
    delta = compute_mastery_delta(
        correct_count=correct_count,
        partial_count=partial_count,
        incorrect_count=incorrect_count,
        total_questions=total_questions,
    )
    new_mastery = clamp01(old_mastery + delta)

    if delta > 0:
        direction = "increase"
    elif delta < 0:
        direction = "decrease"
    else:
        direction = "unchanged"

    return {
        "schema_version": "1",
        "progress_impact_preview_version": PROGRESS_IMPACT_PREVIEW_VERSION,
        "mode": "dry_run_progress_impact_preview",
        "course_id": course_id,
        "skill_id": skill_id,
        "sample_mode": sample_mode,
        "selected_source": session.get("selected_source"),
        "session_summary_version": SESSION_SUMMARY_VERSION,
        "total_questions": total_questions,
        "correct_count": correct_count,
        "partial_count": partial_count,
        "incorrect_count": incorrect_count,
        "old_mastery_preview": round(old_mastery, 4),
        "mastery_delta_preview": delta,
        "new_mastery_preview": round(new_mastery, 4),
        "impact_direction": direction,
        "impact_reason": (
            "Preview-only delta from dry-run local-bank session summary; no progress is written."
        ),
        "progress_delta_preview": {
            "skill_id": skill_id,
            "old_mastery_preview": round(old_mastery, 4),
            "new_mastery_preview": round(new_mastery, 4),
            "mastery_delta_preview": delta,
            "correct_count": correct_count,
            "partial_count": partial_count,
            "incorrect_count": incorrect_count,
            "total_questions": total_questions,
        },
        "path_policy": "no_user_provided_filesystem_root",
        "will_persist_progress": False,
        "will_persist_session": False,
        "will_persist_attempts": False,
        "will_update_progress": False,
        "will_score_live_session": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
        "dry_run_session_summary": session,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build dry-run progress impact preview.")
    parser.add_argument("--course-id", default="v059-sample")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--sample-mode", choices=["correct", "partial", "wrong"], default="correct")
    parser.add_argument("--old-mastery-preview", type=float, default=0.40)
    parser.add_argument("--expect-increase", action="store_true")
    parser.add_argument("--expect-decrease", action="store_true")
    args = parser.parse_args()

    result = build_progress_impact_preview(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
        sample_mode=args.sample_mode,
        old_mastery_preview=args.old_mastery_preview,
    )

    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_increase and result["impact_direction"] != "increase":
        return 2

    if args.expect_decrease and result["impact_direction"] != "decrease":
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

