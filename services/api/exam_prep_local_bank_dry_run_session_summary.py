"""Dry-run session summary for local-bank Exam Prep attempt envelopes.

v0.4.58 groups non-persistent dry-run attempt envelopes into a session-like
summary. It computes preview-only totals and feedback, without writing attempts,
scoring live sessions, or updating progress.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from typing import Any

from exam_prep_local_bank_dry_run_attempt_envelope import (
    ATTEMPT_ENVELOPE_VERSION,
    build_attempt_envelope_snapshot,
)


SESSION_SUMMARY_VERSION = "v0.4.58"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _feedback_summary(verdict_counts: dict[str, int], total: int, average_score: float) -> str:
    if total <= 0:
        return "Nu există încercări dry-run de rezumat."

    correct = int(verdict_counts.get("correct", 0))
    partial = int(verdict_counts.get("partially_correct", 0))
    incorrect = int(verdict_counts.get("incorrect", 0))

    if correct == total:
        return "Toate răspunsurile dry-run sunt corecte în acest scenariu de test."
    if incorrect == total:
        return "Toate răspunsurile dry-run sunt incorecte în acest scenariu de test."
    return (
        f"Rezumat dry-run: {correct} corecte, {partial} parțiale, "
        f"{incorrect} incorecte, scor mediu preview {average_score:.2f}."
    )


def build_session_summary(
    *,
    course_id: str = "v058-sample",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    sample_mode: str = "correct",
) -> dict[str, Any]:
    """Build one non-persistent dry-run session summary."""

    envelope_snapshot = build_attempt_envelope_snapshot(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        sample_mode=sample_mode,
    )

    envelopes = [
        item for item in envelope_snapshot.get("envelopes", [])
        if isinstance(item, dict)
    ]

    total_questions = len(envelopes)
    verdict_counts: dict[str, int] = {}
    score_total = 0.0

    for envelope in envelopes:
        evaluation = envelope.get("evaluation", {})
        verdict = str(evaluation.get("verdict", "")).strip() or "unknown"
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        score_total += float(evaluation.get("score_preview", 0.0) or 0.0)

    average_score = score_total / total_questions if total_questions else 0.0

    return {
        "schema_version": "1",
        "session_summary_version": SESSION_SUMMARY_VERSION,
        "mode": "dry_run_session_summary",
        "dry_run_session_id": f"dry_run_session::{course_id}::{skill_id}::{sample_mode}",
        "created_at": _utc_now_iso(),
        "course_id": course_id,
        "skill_id": skill_id,
        "sample_mode": sample_mode,
        "selected_source": envelope_snapshot.get("selected_source"),
        "attempt_envelope_version": ATTEMPT_ENVELOPE_VERSION,
        "total_questions": total_questions,
        "verdict_counts": dict(sorted(verdict_counts.items())),
        "correct_count": int(verdict_counts.get("correct", 0)),
        "partial_count": int(verdict_counts.get("partially_correct", 0)),
        "incorrect_count": int(verdict_counts.get("incorrect", 0)),
        "average_score_preview": round(average_score, 4),
        "feedback_summary": _feedback_summary(verdict_counts, total_questions, average_score),
        "envelopes": envelopes,
        "path_policy": "no_user_provided_filesystem_root",
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
        "attempt_envelope_snapshot": envelope_snapshot,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a dry-run local-bank session summary.")
    parser.add_argument("--course-id", default="v058-sample")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--sample-mode", choices=["correct", "partial", "wrong"], default="correct")
    parser.add_argument("--expect-correct", action="store_true")
    parser.add_argument("--expect-wrong", action="store_true")
    args = parser.parse_args()

    result = build_session_summary(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
        sample_mode=args.sample_mode,
    )

    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_correct:
        if result["total_questions"] <= 0:
            return 2
        if result["correct_count"] != result["total_questions"]:
            return 3

    if args.expect_wrong:
        if result["total_questions"] <= 0:
            return 4
        if result["incorrect_count"] != result["total_questions"]:
            return 5

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

