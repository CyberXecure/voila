"""Guarded local-bank adapter boundary for future Exam Prep live trial.

v0.4.62 creates a boundary object that a future study-session integration can
use to decide whether a local-bank source candidate is available.

It does not connect to live study routes and does not persist attempts, sessions,
scores, or progress.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_guarded_live_trial import (
    GUARDED_TRIAL_VERSION,
    LIVE_TRIAL_FLAG_NAME,
    build_guarded_live_trial_scaffold,
)


ADAPTER_BOUNDARY_VERSION = "v0.4.62"


def _flag_enabled(env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    value = str(source.get(LIVE_TRIAL_FLAG_NAME, "")).strip().lower()
    return value in {"1", "true", "yes", "on"}


def build_guarded_adapter_boundary(
    *,
    course_id: str = "v062-sample",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    old_mastery_preview: float = 0.40,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a guarded adapter boundary without live-session integration."""

    enabled = _flag_enabled(env)

    old_flag = os.environ.get(LIVE_TRIAL_FLAG_NAME)
    try:
        if enabled:
            os.environ[LIVE_TRIAL_FLAG_NAME] = "1"
        else:
            os.environ.pop(LIVE_TRIAL_FLAG_NAME, None)

        trial = build_guarded_live_trial_scaffold(
            course_id=course_id,
            skill_id=skill_id,
            limit=limit,
            old_mastery_preview=old_mastery_preview,
        )
    finally:
        if old_flag is None:
            os.environ.pop(LIVE_TRIAL_FLAG_NAME, None)
        else:
            os.environ[LIVE_TRIAL_FLAG_NAME] = old_flag

    trial_ready = trial.get("trial_status") == "guarded_trial_plan_ready"
    boundary_status = "local_source_candidate_available" if trial_ready else "legacy_fallback_only"
    candidate = None

    if trial_ready:
        trial_plan = trial.get("trial_plan") or {}
        candidate = {
            "candidate_id": f"local_bank_candidate::{course_id}::{skill_id}",
            "candidate_source": "local_exercise_bank_adapter",
            "course_id": course_id,
            "skill_id": skill_id,
            "max_questions_preview": trial_plan.get("max_questions_preview", limit),
            "adapter_mode": "guarded_boundary_candidate",
            "requires_guarded_trial_flag": True,
            "requires_readiness_ready": True,
            "legacy_fallback_policy": trial_plan.get(
                "legacy_fallback_policy",
                "Fallback to legacy source if local-bank source fails readiness or validation.",
            ),
            "will_start_live_session": False,
            "will_replace_current_source": False,
            "will_persist_attempts": False,
            "will_update_progress": False,
            "will_score_live_session": False,
        }

    return {
        "schema_version": "1",
        "adapter_boundary_version": ADAPTER_BOUNDARY_VERSION,
        "mode": "guarded_live_trial_adapter_boundary",
        "flag_name": LIVE_TRIAL_FLAG_NAME,
        "flag_enabled": enabled,
        "guarded_trial_version": GUARDED_TRIAL_VERSION,
        "trial_status": trial.get("trial_status"),
        "boundary_status": boundary_status,
        "local_source_candidate_available": candidate is not None,
        "local_source_candidate": candidate,
        "fallback_source": "legacy_fallback",
        "adapter_contract": {
            "future_live_adapter_must_check_flag": True,
            "future_live_adapter_must_check_readiness": True,
            "future_live_adapter_must_keep_legacy_fallback": True,
            "future_live_adapter_must_not_accept_user_filesystem_root": True,
            "future_live_adapter_must_require_owner_review": True,
        },
        "path_policy": "no_user_provided_filesystem_root",
        "will_start_live_session": False,
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
        "guarded_live_trial": trial,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build guarded local-bank adapter boundary.")
    parser.add_argument("--course-id", default="v062-sample")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--old-mastery-preview", type=float, default=0.40)
    parser.add_argument("--strict-fallback", action="store_true")
    parser.add_argument("--strict-candidate", action="store_true")
    args = parser.parse_args()

    result = build_guarded_adapter_boundary(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
        old_mastery_preview=args.old_mastery_preview,
    )

    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.strict_fallback and result["boundary_status"] != "legacy_fallback_only":
        return 2

    if args.strict_candidate and result["boundary_status"] != "local_source_candidate_available":
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

