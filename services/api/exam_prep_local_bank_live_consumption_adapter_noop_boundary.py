"""No-op adapter boundary for future guarded local-bank live consumption.

v0.4.71 introduces a final no-op boundary before any real guarded live-trial
adapter work. It reads the v0.4.70 decision gate and requires a separate
adapter-boundary flag.

This module does not consume local-bank questions live, start live sessions,
replace the effective source, persist attempts/sessions/progress, score live
sessions, or modify the Exam Prep UI.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_live_consumption_decision_gate import (
    CANDIDATES_PANEL_FLAG_NAME,
    CANDIDATES_PANEL_POLISH_FLAG_NAME,
    CANDIDATES_ROUTE_FLAG_NAME,
    DIAGNOSTICS_ROUTE_FLAG_NAME,
    LIVE_CONSUMPTION_DECISION_FLAG_NAME,
    LIVE_CONSUMPTION_DECISION_GATE_VERSION,
    LIVE_TRIAL_FLAG_NAME,
    build_live_consumption_decision_gate,
)


LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY_VERSION = "v0.4.71"
LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY_FLAG_NAME = (
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY"
)

REQUIRED_FLAGS_FOR_NOOP_ADAPTER_CANDIDATE = [
    LIVE_TRIAL_FLAG_NAME,
    DIAGNOSTICS_ROUTE_FLAG_NAME,
    CANDIDATES_ROUTE_FLAG_NAME,
    CANDIDATES_PANEL_FLAG_NAME,
    CANDIDATES_PANEL_POLISH_FLAG_NAME,
    LIVE_CONSUMPTION_DECISION_FLAG_NAME,
    LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY_FLAG_NAME,
]


def _flag_enabled(name: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    value = str(source.get(name, "")).strip().lower()
    return value in {"1", "true", "yes", "on"}


def _temporary_env(env: dict[str, str]):
    class _Context:
        def __enter__(self):
            self._old = {name: os.environ.get(name) for name in env}
            for name, value in env.items():
                os.environ[name] = value
            return self

        def __exit__(self, exc_type, exc, tb):
            for name, value in self._old.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value
            return False

    return _Context()


def build_live_consumption_adapter_noop_boundary(
    *,
    course_id: str = "v071-boundary",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    old_mastery_preview: float = 0.40,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a no-op adapter boundary without enabling live consumption."""

    source_env = env if env is not None else dict(os.environ)
    flag_states = {
        name: _flag_enabled(name, source_env)
        for name in REQUIRED_FLAGS_FOR_NOOP_ADAPTER_CANDIDATE
    }
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]

    decision_env = {
        name: "1"
        for name in REQUIRED_FLAGS_FOR_NOOP_ADAPTER_CANDIDATE
        if name != LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY_FLAG_NAME and flag_states.get(name)
    }

    with _temporary_env(decision_env):
        decision_gate = build_live_consumption_decision_gate(
            course_id=course_id,
            skill_id=skill_id,
            limit=limit,
            old_mastery_preview=old_mastery_preview,
            env=decision_env,
        )

    adapter_flag_enabled = flag_states.get(
        LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY_FLAG_NAME,
        False,
    )
    decision_eligible = decision_gate.get("decision_status") == "eligible_for_owner_decision"
    eligible = adapter_flag_enabled and decision_eligible and not missing_flags

    blocking_reasons: list[str] = []
    if missing_flags:
        blocking_reasons.append("required_flags_missing")
    if not decision_eligible:
        blocking_reasons.append("decision_gate_not_eligible")
    if not adapter_flag_enabled:
        blocking_reasons.append("adapter_noop_boundary_flag_disabled")

    adapter_status = "live_adapter_candidate_noop" if eligible else "legacy_fallback_only"

    live_adapter_candidate = None
    if eligible:
        live_adapter_candidate = {
            "candidate_id": f"live_adapter_noop::{course_id}::{skill_id}",
            "candidate_source": "local_exercise_bank_adapter",
            "candidate_mode": "noop_boundary_only",
            "course_id": course_id,
            "skill_id": skill_id,
            "max_questions_preview": max(1, min(int(limit or 5), 20)),
            "effective_source": "legacy_fallback",
            "future_live_trial_contract": {
                "must_keep_legacy_fallback": True,
                "must_require_owner_decision_gate": True,
                "must_require_quality_gate": True,
                "must_hide_answers_in_preview_ui": True,
                "must_not_accept_user_filesystem_root": True,
                "must_run_codeql_before_merge": True,
            },
            "will_consume_local_bank_live": False,
            "will_start_live_session": False,
            "will_replace_effective_source": False,
            "will_persist_attempts": False,
            "will_update_progress": False,
            "will_score_live_session": False,
        }

    return {
        "schema_version": "1",
        "adapter_noop_boundary_version": LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY_VERSION,
        "mode": "guarded_live_consumption_adapter_noop_boundary",
        "course_id": course_id,
        "skill_id": skill_id,
        "adapter_flag_name": LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY_FLAG_NAME,
        "adapter_flag_enabled": adapter_flag_enabled,
        "decision_gate_version": LIVE_CONSUMPTION_DECISION_GATE_VERSION,
        "decision_status": decision_gate.get("decision_status"),
        "adapter_status": adapter_status,
        "eligible_for_noop_adapter_candidate": eligible,
        "blocking_reasons": blocking_reasons,
        "required_flags_for_noop_adapter_candidate": REQUIRED_FLAGS_FOR_NOOP_ADAPTER_CANDIDATE,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "effective_source": "legacy_fallback",
        "fallback_source": "legacy_fallback",
        "live_adapter_candidate": live_adapter_candidate,
        "minimum_contract_for_first_real_live_trial": [
            "owner decision gate remains explicit",
            "legacy fallback remains available",
            "effective_source change requires separate milestone",
            "attempt persistence requires separate milestone",
            "progress update requires separate milestone",
            "live scoring requires separate milestone",
            "web routes must not accept user-provided filesystem roots",
            "answer/explanation preview leaks remain blocked",
            "CodeQL and final main checks must pass",
        ],
        "explicit_not_live_yet": [
            "adapter boundary is no-op only",
            "local-bank questions are not consumed live",
            "live study sessions are not replaced",
            "effective_source remains legacy_fallback",
            "attempts are not persisted",
            "progress is not updated",
            "sessions are not persisted",
            "live scoring is not enabled",
            "public Exam Prep navigation is not changed",
        ],
        "path_policy": "no_user_provided_filesystem_root",
        "will_consume_local_bank_live": False,
        "will_start_live_session": False,
        "will_replace_effective_source": False,
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
        "decision_gate": decision_gate,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build guarded live consumption adapter no-op boundary.")
    parser.add_argument("--course-id", default="v071-boundary")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--old-mastery-preview", type=float, default=0.40)
    parser.add_argument("--expect-noop-candidate", action="store_true")
    parser.add_argument("--expect-legacy-fallback", action="store_true")
    args = parser.parse_args()

    result = build_live_consumption_adapter_noop_boundary(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
        old_mastery_preview=args.old_mastery_preview,
    )

    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_noop_candidate and result["adapter_status"] != "live_adapter_candidate_noop":
        return 2

    if args.expect_legacy_fallback and result["adapter_status"] != "legacy_fallback_only":
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
