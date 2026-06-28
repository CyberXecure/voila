"""Guarded local-bank live-trial scaffold for Exam Prep.

v0.4.61 adds a disabled-by-default planning scaffold for a future guarded
local-bank live trial.

Important: this module does not wire local-bank questions into live study
sessions. It only produces a trial plan when:
- the v0.4.60 readiness report is ready
- the explicit live-trial flag is enabled

No attempts, sessions, scores, or progress are persisted.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_integration_readiness import (
    READINESS_REPORT_VERSION,
    build_integration_readiness_report,
)


GUARDED_TRIAL_VERSION = "v0.4.61"
LIVE_TRIAL_FLAG_NAME = "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL"


def _flag_enabled(env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    value = str(source.get(LIVE_TRIAL_FLAG_NAME, "")).strip().lower()
    return value in {"1", "true", "yes", "on"}


def build_guarded_live_trial_scaffold(
    *,
    course_id: str = "v061-sample",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    old_mastery_preview: float = 0.40,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a guarded live-trial plan without activating live behavior."""

    enabled = _flag_enabled(env)
    readiness = build_integration_readiness_report(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        old_mastery_preview=old_mastery_preview,
    )

    readiness_ready = readiness.get("readiness_status") == "ready_for_guarded_live_trial"
    can_prepare_trial_plan = enabled and readiness_ready

    if not enabled:
        trial_status = "disabled"
        blocking_reason = "guarded_live_trial_flag_disabled"
    elif not readiness_ready:
        trial_status = "blocked"
        blocking_reason = "integration_readiness_not_ready"
    else:
        trial_status = "guarded_trial_plan_ready"
        blocking_reason = ""

    trial_plan = None
    if can_prepare_trial_plan:
        trial_plan = {
            "trial_plan_id": f"guarded_local_bank_trial::{course_id}::{skill_id}",
            "course_id": course_id,
            "skill_id": skill_id,
            "source": "local_exercise_bank_adapter",
            "max_questions_preview": limit,
            "rollout_scope": "single_skill_guarded_trial",
            "requires_manual_owner_start": True,
            "requires_explicit_flag": True,
            "legacy_fallback_policy": "Fallback to legacy source if local-bank source fails readiness or validation.",
            "abort_conditions": [
                "quality_gate_fails",
                "source_selection_not_local",
                "attempt_envelope_invalid",
                "progress_preview_missing",
                "any_persistence_guard_not_false",
            ],
            "live_integration_touched": False,
        }

    return {
        "schema_version": "1",
        "guarded_trial_version": GUARDED_TRIAL_VERSION,
        "mode": "guarded_live_trial_scaffold",
        "flag_name": LIVE_TRIAL_FLAG_NAME,
        "flag_enabled": enabled,
        "readiness_report_version": READINESS_REPORT_VERSION,
        "readiness_status": readiness.get("readiness_status"),
        "trial_status": trial_status,
        "blocking_reason": blocking_reason,
        "can_prepare_trial_plan": can_prepare_trial_plan,
        "trial_plan": trial_plan,
        "guardrails": {
            "default_disabled": True,
            "requires_readiness_ready": True,
            "requires_explicit_live_trial_flag": True,
            "legacy_fallback_must_remain_available": True,
            "no_user_filesystem_root_in_web_routes": True,
            "owner_must_review_before_live_integration": True,
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
        "readiness_report": readiness,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build guarded local-bank live-trial scaffold.")
    parser.add_argument("--course-id", default="v061-sample")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--old-mastery-preview", type=float, default=0.40)
    parser.add_argument("--strict-disabled", action="store_true")
    parser.add_argument("--strict-plan-ready", action="store_true")
    args = parser.parse_args()

    result = build_guarded_live_trial_scaffold(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
        old_mastery_preview=args.old_mastery_preview,
    )

    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.strict_disabled and result["trial_status"] != "disabled":
        return 2

    if args.strict_plan_ready and result["trial_status"] != "guarded_trial_plan_ready":
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

