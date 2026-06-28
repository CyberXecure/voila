"""Dry-run attempt envelope for local-bank Exam Prep questions.

v0.4.57 wraps a dry-run question, submitted answer, evaluation result, and
feedback preview into an attempt-like object.

The envelope is intentionally non-persistent:
- no attempt storage
- no live score write
- no progress update
- no weak-review update
- no live study-session replacement
- no web route
- no user-provided filesystem root
- no cloud/API dependency
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from typing import Any

from exam_prep_local_bank_dry_run_answer_evaluation import (
    ANSWER_EVALUATION_VERSION,
    build_answer_evaluation_snapshot,
)


ATTEMPT_ENVELOPE_VERSION = "v0.4.57"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _question_snapshot(evaluation: dict[str, Any]) -> dict[str, Any]:
    return {
        "question_id": evaluation.get("question_id", ""),
        "dry_run_item_id": evaluation.get("dry_run_item_id", ""),
        "question_type": evaluation.get("question_type", ""),
        "skill_id": evaluation.get("skill_id", ""),
        "source": "local_exercise_bank_adapter",
    }


def build_attempt_envelope(
    evaluation: dict[str, Any],
    *,
    index: int,
    course_id: str,
    skill_id: str,
    sample_mode: str,
) -> dict[str, Any]:
    question_id = str(evaluation.get("question_id", "")).strip()
    dry_run_item_id = str(evaluation.get("dry_run_item_id", "")).strip()

    return {
        "schema_version": "1",
        "attempt_envelope_version": ATTEMPT_ENVELOPE_VERSION,
        "attempt_mode": "dry_run_non_persistent",
        "dry_run_attempt_id": f"dry_run_attempt::{course_id}::{index:04d}",
        "created_at": _utc_now_iso(),
        "course_id": course_id,
        "skill_id": skill_id,
        "sample_mode": sample_mode,
        "source": "local_exercise_bank_adapter",
        "attempt_id_base": question_id or dry_run_item_id or f"item_{index:04d}",
        "question_snapshot": _question_snapshot(evaluation),
        "submitted_answer": evaluation.get("answer", ""),
        "evaluation": {
            "answer_evaluation_version": ANSWER_EVALUATION_VERSION,
            "verdict": evaluation.get("verdict", ""),
            "score_preview": evaluation.get("score_preview", 0.0),
            "exact_match": evaluation.get("exact_match", False),
            "keyword_overlap": evaluation.get("keyword_overlap", 0.0),
            "feedback_preview": evaluation.get("feedback_preview", ""),
            "correct_answer_preview": evaluation.get("correct_answer_preview", ""),
        },
        "persistence": {
            "will_persist_attempt": False,
            "will_update_progress": False,
            "will_score_live_session": False,
            "will_update_weak_review": False,
        },
        "dry_run_only": True,
        "ready_for_future_live_shape_review": True,
        "will_persist_attempt": False,
        "will_update_progress": False,
        "will_score_live_session": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
    }


def build_attempt_envelope_snapshot(
    *,
    course_id: str = "v057-sample",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    sample_mode: str = "correct",
) -> dict[str, Any]:
    evaluation_snapshot = build_answer_evaluation_snapshot(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        sample_mode=sample_mode,
        enable_local_flag=True,
    )

    evaluations = [
        item for item in evaluation_snapshot.get("evaluations", [])
        if isinstance(item, dict)
    ]

    envelopes = [
        build_attempt_envelope(
            evaluation,
            index=index,
            course_id=course_id,
            skill_id=skill_id,
            sample_mode=sample_mode,
        )
        for index, evaluation in enumerate(evaluations, start=1)
    ]

    verdict_counts: dict[str, int] = {}
    for envelope in envelopes:
        verdict = str(envelope["evaluation"].get("verdict", ""))
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1

    return {
        "schema_version": "1",
        "attempt_envelope_version": ATTEMPT_ENVELOPE_VERSION,
        "mode": "dry_run_attempt_envelope_snapshot",
        "course_id": course_id,
        "skill_id": skill_id,
        "sample_mode": sample_mode,
        "selected_source": evaluation_snapshot.get("selected_source"),
        "envelope_count": len(envelopes),
        "verdict_counts": dict(sorted(verdict_counts.items())),
        "envelopes": envelopes,
        "path_policy": "no_user_provided_filesystem_root",
        "will_persist_attempts": False,
        "will_update_progress": False,
        "will_score_live_session": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
        "answer_evaluation_snapshot": evaluation_snapshot,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build dry-run local-bank attempt envelopes.")
    parser.add_argument("--course-id", default="v057-sample")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--sample-mode", choices=["correct", "partial", "wrong"], default="correct")
    parser.add_argument("--expect-correct", action="store_true")
    parser.add_argument("--expect-wrong", action="store_true")
    args = parser.parse_args()

    result = build_attempt_envelope_snapshot(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
        sample_mode=args.sample_mode,
    )

    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_correct:
        if result["envelope_count"] <= 0:
            return 2
        if result["verdict_counts"].get("correct", 0) != result["envelope_count"]:
            return 3

    if args.expect_wrong:
        if result["envelope_count"] <= 0:
            return 4
        if result["verdict_counts"].get("incorrect", 0) != result["envelope_count"]:
            return 5

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

