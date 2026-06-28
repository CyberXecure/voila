"""Guarded first live-trial owner-ready checkpoint.

v0.4.89 consolidates the guarded first-live-trial chain into a final owner-ready
checkpoint and stop/go summary before any real delivery milestone.

This milestone does not deliver questions live. It adds no web route, does not
patch web_app.py, does not modify public UI, and keeps the real effective source
as legacy_fallback.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_first_live_trial_decision_gate import (
    DECISION_GATE_FLAG_NAME,
    DECISION_GATE_VERSION,
    build_first_live_trial_decision_gate,
)


OWNER_READY_CHECKPOINT_VERSION = "v0.4.89"
OWNER_READY_CHECKPOINT_FLAG_NAME = (
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_READY_CHECKPOINT"
)

REQUIRED_OWNER_FLAGS = [
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL_POLISH",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_DECISION_GATE",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_SOURCE_SELECTOR",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_ROUTE",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_OWNER_PANEL",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_QUESTION_ENVELOPE_SANITIZER",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_DRY_RUN_SESSION_ENVELOPE",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DELIVERY_CONTRACT",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DELIVERY_ADAPTER_NOOP",
    DECISION_GATE_FLAG_NAME,
    OWNER_READY_CHECKPOINT_FLAG_NAME,
]

CHAIN_COMPONENTS = [
    "v0.4.77 contract skeleton",
    "v0.4.78 contract report route",
    "v0.4.79 contract owner panel",
    "v0.4.80 question envelope sanitizer",
    "v0.4.81 dry-run session envelope",
    "v0.4.82 no-persistence delivery contract",
    "v0.4.83 no-op delivery adapter",
    "v0.4.84 no-op delivery route scaffold",
    "v0.4.85 owner smoke route",
    "v0.4.86 explicit decision gate",
    "v0.4.87 owner decision report route",
    "v0.4.88 owner decision panel",
    "v0.4.89 owner-ready checkpoint",
]


def _flag_enabled(name: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return str(source.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def build_owner_ready_checkpoint(
    *,
    course_id: str = "v089-owner-ready-checkpoint",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_env = env if env is not None else dict(os.environ)
    flag_states = {name: _flag_enabled(name, source_env) for name in REQUIRED_OWNER_FLAGS}
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]
    checkpoint_flag_enabled = flag_states.get(OWNER_READY_CHECKPOINT_FLAG_NAME, False)

    decision = build_first_live_trial_decision_gate(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        requested_decision="keep_noop_only",
        env=source_env,
    )
    decision_ready = decision.get("status") == "decision_gate_ready_for_owner_review"
    decision_summary = decision.get("decision_summary")
    if not isinstance(decision_summary, dict):
        decision_summary = {}
    readiness = decision.get("readiness_checks")
    if not isinstance(readiness, dict):
        readiness = {}
    policy = decision.get("decision_gate_policy")
    if not isinstance(policy, dict):
        policy = {}

    real_delivery_allowed_now = bool(decision_summary.get("real_delivery_allowed_now", False))
    delivery_performed = bool(decision_summary.get("delivery_performed", False))
    delivered_question_count = int(decision_summary.get("delivered_question_count") or 0)
    candidate_question_count = int(decision_summary.get("candidate_question_count") or 0)

    checkpoint_checks = {
        "checkpoint_flag_enabled": checkpoint_flag_enabled,
        "all_required_owner_flags_enabled": len(missing_flags) == 0,
        "decision_gate_ready": decision_ready,
        "candidate_question_count_positive": candidate_question_count > 0,
        "real_delivery_allowed_now_false": real_delivery_allowed_now is False,
        "delivery_performed_false": delivery_performed is False,
        "delivered_question_count_zero": delivered_question_count == 0,
        "effective_source_after_decision_legacy": decision_summary.get("effective_source_after_decision") == "legacy_fallback",
        "requires_separate_real_delivery_milestone": policy.get("requires_separate_real_delivery_milestone") is True,
        "requires_owner_reconfirmation_before_real_delivery": policy.get("requires_owner_reconfirmation_before_real_delivery") is True,
        "requires_rollback_to_legacy_fallback": policy.get("requires_rollback_to_legacy_fallback") is True,
    }

    stop_go_summary = {
        "owner_ready_checkpoint_complete": False,
        "stop_go_label": "STOP",
        "go_for_real_delivery_now": False,
        "recommended_action": "stop_here_or_create_separate_explicit_real_delivery_milestone",
        "current_safe_state": "noop_chain_ready_no_real_delivery",
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "real_delivery_allowed_now": False,
        "delivery_performed": False,
        "delivered_question_count": 0,
        "requires_new_milestone_for_real_delivery": True,
        "requires_owner_reconfirmation_before_real_delivery": True,
    }

    if not checkpoint_flag_enabled:
        status = "disabled"
        blocking_reasons = ["owner_ready_checkpoint_flag_disabled"]
        checkpoint_complete = False
    elif missing_flags:
        status = "blocked"
        blocking_reasons = ["required_owner_review_flags_missing"]
        checkpoint_complete = False
    elif not decision_ready:
        status = "blocked"
        blocking_reasons = ["decision_gate_not_ready"]
        checkpoint_complete = False
    elif real_delivery_allowed_now or delivery_performed or delivered_question_count != 0:
        status = "blocked"
        blocking_reasons = ["unexpected_real_delivery_activity_detected"]
        checkpoint_complete = False
    else:
        status = "owner_ready_checkpoint_complete_no_go_for_real_delivery"
        blocking_reasons = []
        checkpoint_complete = True

    if checkpoint_complete:
        stop_go_summary["owner_ready_checkpoint_complete"] = True

    return {
        "schema_version": "1",
        "owner_ready_checkpoint_version": OWNER_READY_CHECKPOINT_VERSION,
        "mode": "guarded_first_live_trial_owner_ready_checkpoint",
        "course_id": course_id,
        "skill_id": skill_id,
        "checkpoint_flag_name": OWNER_READY_CHECKPOINT_FLAG_NAME,
        "checkpoint_flag_enabled": checkpoint_flag_enabled,
        "status": status,
        "blocking_reasons": blocking_reasons,
        "owner_ready_checkpoint_complete": checkpoint_complete,
        "required_owner_flags": REQUIRED_OWNER_FLAGS,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "depends_on_decision_gate_version": DECISION_GATE_VERSION,
        "decision_gate_status": decision.get("status"),
        "decision_gate_ready": decision_ready,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "chain_components": CHAIN_COMPONENTS,
        "checkpoint_checks": checkpoint_checks,
        "stop_go_summary": stop_go_summary,
        "owner_readiness_summary": {
            "ready_for_next_decision": checkpoint_complete,
            "accepted_decision": "keep_noop_only",
            "real_delivery_allowed_now": False,
            "go_for_real_delivery_now": False,
            "delivery_performed": False,
            "delivered_question_count": 0,
            "candidate_question_count": candidate_question_count,
            "safe_to_keep_noop_chain": True,
            "safe_to_prepare_future_real_delivery_milestone": checkpoint_complete,
            "safe_to_activate_real_delivery_in_this_milestone": False,
        },
        "required_before_real_delivery": [
            "separate explicit real delivery milestone",
            "owner reconfirmation",
            "rollback path to legacy_fallback",
            "no-persistence route implementation review",
            "sanitized question envelope verification",
            "manual owner smoke test",
        ],
        "implementation_scope": {
            "json_only_local_module": True,
            "adds_web_route": False,
            "patches_web_app": False,
            "adds_public_ui": False,
            "starts_live_session": False,
            "replaces_live_study_session": False,
            "delivers_local_bank_questions_live": False,
            "persists_sessions": False,
            "persists_attempts": False,
            "updates_progress": False,
            "scores_live_session": False,
            "requires_cloud_or_api": False,
        },
        "explicit_not_live_yet": [
            "owner-ready checkpoint does not change effective_source",
            "owner-ready checkpoint does not deliver local-bank questions live",
            "go_for_real_delivery_now remains false",
            "real_delivery_allowed_now remains false",
            "delivery_performed remains false",
            "delivered_question_count remains zero",
            "local-bank questions are not consumed live",
            "live study sessions are not started",
            "effective_source remains legacy_fallback",
            "attempts are not persisted",
            "progress is not updated",
            "sessions are not persisted",
            "live scoring is not enabled",
            "public Exam Prep navigation is not changed",
        ],
        "path_policy": "no_user_provided_filesystem_root",
        "will_consume_local_bank_live": False,
        "will_deliver_local_bank_questions_live": False,
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
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build guarded first live trial owner-ready checkpoint.")
    parser.add_argument("--course-id", default="v089-owner-ready-checkpoint")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--expect-ready", action="store_true")
    parser.add_argument("--expect-disabled", action="store_true")
    args = parser.parse_args()

    result = build_owner_ready_checkpoint(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_ready and result["status"] != "owner_ready_checkpoint_complete_no_go_for_real_delivery":
        return 2
    if args.expect_disabled and result["status"] != "disabled":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
