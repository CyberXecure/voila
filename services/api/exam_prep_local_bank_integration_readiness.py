"""Local-bank integration readiness report for Exam Prep.

v0.4.60 verifies the local-bank dry-run chain before any future guarded live
trial. It does not enable live consumption and does not write attempts,
sessions, scores, or progress.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_consumption_flag import (
    CONSUMPTION_FLAG_NAME,
    LOCAL_SOURCE,
    build_controlled_consumption_snapshot,
)
from exam_prep_local_bank_dry_run_answer_evaluation import (
    ANSWER_EVALUATION_VERSION,
    build_answer_evaluation_snapshot,
)
from exam_prep_local_bank_dry_run_attempt_envelope import (
    ATTEMPT_ENVELOPE_VERSION,
    build_attempt_envelope_snapshot,
)
from exam_prep_local_bank_dry_run_progress_impact import (
    PROGRESS_IMPACT_PREVIEW_VERSION,
    build_progress_impact_preview,
)
from exam_prep_local_bank_dry_run_session_summary import (
    SESSION_SUMMARY_VERSION,
    build_session_summary,
)
from exam_prep_local_bank_dry_run_source_selection import (
    DRY_RUN_VERSION,
    build_dry_run_source_selection,
)
from exam_prep_local_bank_question_quality_gate import (
    QUALITY_GATE_VERSION,
    build_quality_gate_snapshot,
)


READINESS_REPORT_VERSION = "v0.4.60"


def _ok(name: str, passed: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "passed": bool(passed),
        "details": details or {},
    }


def build_integration_readiness_report(
    *,
    course_id: str = "v060-sample",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    old_mastery_preview: float = 0.40,
) -> dict[str, Any]:
    """Build an integration readiness report without enabling live consumption."""

    consumption = build_controlled_consumption_snapshot(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        env={CONSUMPTION_FLAG_NAME: "1"},
    )
    old_flag = os.environ.get(CONSUMPTION_FLAG_NAME)
    try:
        os.environ[CONSUMPTION_FLAG_NAME] = "1"
        source_selection = build_dry_run_source_selection(
            course_id=course_id,
            skill_id=skill_id,
            limit=limit,
            require_local_when_enabled=True,
        )
    finally:
        if old_flag is None:
            os.environ.pop(CONSUMPTION_FLAG_NAME, None)
        else:
            os.environ[CONSUMPTION_FLAG_NAME] = old_flag
    quality_gate = build_quality_gate_snapshot(
        course_id=course_id,
        skill_id=skill_id,
        limit=max(limit, 12),
        enable_local_flag=True,
    )
    answer_evaluation = build_answer_evaluation_snapshot(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        sample_mode="correct",
        enable_local_flag=True,
    )
    attempt_envelope = build_attempt_envelope_snapshot(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        sample_mode="correct",
    )
    session_summary = build_session_summary(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        sample_mode="correct",
    )
    progress_impact = build_progress_impact_preview(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        sample_mode="correct",
        old_mastery_preview=old_mastery_preview,
    )

    checks = [
        _ok(
            "controlled_consumption_flag",
            consumption.get("selected_source") == LOCAL_SOURCE
            and consumption.get("flag_enabled") is True
            and consumption.get("will_enable_live_consumption") is False,
            {
                "flag_name": CONSUMPTION_FLAG_NAME,
                "selected_source": consumption.get("selected_source"),
                "flag_enabled": consumption.get("flag_enabled"),
            },
        ),
        _ok(
            "dry_run_source_selection",
            source_selection.get("dry_run_version") == DRY_RUN_VERSION
            and source_selection.get("selected_source") == LOCAL_SOURCE
            and int(source_selection.get("dry_run_item_count", 0)) > 0
            and source_selection.get("will_enable_live_consumption") is False,
            {
                "dry_run_version": source_selection.get("dry_run_version"),
                "dry_run_item_count": source_selection.get("dry_run_item_count"),
            },
        ),
        _ok(
            "question_quality_gate",
            quality_gate.get("quality_gate_version") == QUALITY_GATE_VERSION
            and quality_gate.get("quality_gate_pass") is True
            and quality_gate.get("quality_status") == "pass",
            {
                "quality_status": quality_gate.get("quality_status"),
                "question_count": quality_gate.get("question_count"),
                "question_type_counts": quality_gate.get("question_type_counts"),
            },
        ),
        _ok(
            "answer_evaluation",
            answer_evaluation.get("answer_evaluation_version") == ANSWER_EVALUATION_VERSION
            and int(answer_evaluation.get("evaluation_count", 0)) > 0
            and answer_evaluation.get("correct_count") == answer_evaluation.get("evaluation_count")
            and answer_evaluation.get("will_persist_attempts") is False,
            {
                "evaluation_count": answer_evaluation.get("evaluation_count"),
                "correct_count": answer_evaluation.get("correct_count"),
            },
        ),
        _ok(
            "attempt_envelope",
            attempt_envelope.get("attempt_envelope_version") == ATTEMPT_ENVELOPE_VERSION
            and int(attempt_envelope.get("envelope_count", 0)) > 0
            and attempt_envelope.get("will_persist_attempts") is False,
            {
                "envelope_count": attempt_envelope.get("envelope_count"),
                "verdict_counts": attempt_envelope.get("verdict_counts"),
            },
        ),
        _ok(
            "session_summary",
            session_summary.get("session_summary_version") == SESSION_SUMMARY_VERSION
            and int(session_summary.get("total_questions", 0)) > 0
            and session_summary.get("will_persist_session") is False,
            {
                "total_questions": session_summary.get("total_questions"),
                "average_score_preview": session_summary.get("average_score_preview"),
            },
        ),
        _ok(
            "progress_impact_preview",
            progress_impact.get("progress_impact_preview_version") == PROGRESS_IMPACT_PREVIEW_VERSION
            and progress_impact.get("impact_direction") == "increase"
            and progress_impact.get("will_persist_progress") is False
            and progress_impact.get("will_update_progress") is False,
            {
                "old_mastery_preview": progress_impact.get("old_mastery_preview"),
                "new_mastery_preview": progress_impact.get("new_mastery_preview"),
                "mastery_delta_preview": progress_impact.get("mastery_delta_preview"),
            },
        ),
    ]

    all_passed = all(check["passed"] for check in checks)
    blocking_checks = [check["name"] for check in checks if not check["passed"]]

    if all_passed:
        readiness_status = "ready_for_guarded_live_trial"
    elif blocking_checks:
        readiness_status = "blocked"
    else:
        readiness_status = "needs_review"

    return {
        "schema_version": "1",
        "readiness_report_version": READINESS_REPORT_VERSION,
        "mode": "local_bank_integration_readiness_report",
        "course_id": course_id,
        "skill_id": skill_id,
        "readiness_status": readiness_status,
        "ready_for_guarded_live_trial": all_passed,
        "blocking_checks": blocking_checks,
        "checks": checks,
        "next_step": (
            "Future milestone may add a guarded live trial behind explicit flags."
            if all_passed
            else "Resolve blocking checks before guarded live trial planning."
        ),
        "guardrails": {
            "requires_future_live_trial_milestone": True,
            "requires_explicit_live_flag": True,
            "requires_no_user_filesystem_root_in_web_routes": True,
            "legacy_fallback_must_remain_available": True,
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
        "snapshots": {
            "consumption": consumption,
            "source_selection": source_selection,
            "quality_gate": quality_gate,
            "answer_evaluation": answer_evaluation,
            "attempt_envelope": attempt_envelope,
            "session_summary": session_summary,
            "progress_impact": progress_impact,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build local-bank integration readiness report.")
    parser.add_argument("--course-id", default="v060-sample")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--old-mastery-preview", type=float, default=0.40)
    parser.add_argument("--expect-ready", action="store_true")
    args = parser.parse_args()

    result = build_integration_readiness_report(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
        old_mastery_preview=args.old_mastery_preview,
    )

    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_ready and result["readiness_status"] != "ready_for_guarded_live_trial":
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
