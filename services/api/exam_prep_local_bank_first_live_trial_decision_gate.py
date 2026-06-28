"""Guarded first live-trial explicit decision gate.

v0.4.86 adds a JSON-only decision gate over the first live-trial chain. It
verifies that the owner smoke/no-op adapter chain is ready for a next decision,
but still blocks real delivery now.

This milestone does not deliver questions live. It adds no web route, does not
patch web_app.py, does not modify public UI, and keeps the real effective source
as legacy_fallback.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_first_live_trial_delivery_adapter import (
    NOOP_DELIVERY_ADAPTER_FLAG_NAME,
    build_noop_delivery_adapter_result,
)


DECISION_GATE_VERSION = "v0.4.86"
DECISION_GATE_FLAG_NAME = (
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DECISION_GATE"
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
    NOOP_DELIVERY_ADAPTER_FLAG_NAME,
    DECISION_GATE_FLAG_NAME,
]

ALLOWED_DECISION_VALUES = [
    "keep_noop_only",
    "prepare_owner_panel_review",
    "prepare_future_real_delivery_milestone",
]


def _flag_enabled(name: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return str(source.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def build_first_live_trial_decision_gate(
    *,
    course_id: str = "v086-decision-gate",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    requested_decision: str = "keep_noop_only",
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_env = env if env is not None else dict(os.environ)
    flag_states = {name: _flag_enabled(name, source_env) for name in REQUIRED_OWNER_FLAGS}
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]
    decision_gate_flag_enabled = flag_states.get(DECISION_GATE_FLAG_NAME, False)

    adapter = build_noop_delivery_adapter_result(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        env=source_env,
    )
    adapter_ready = adapter.get("status") == "noop_delivery_adapter_ready_for_owner_review"
    adapter_summary = adapter.get("adapter_summary")
    if not isinstance(adapter_summary, dict):
        adapter_summary = {}

    candidate_question_count = int(adapter_summary.get("candidate_question_count") or 0)
    delivery_attempted = adapter_summary.get("delivery_attempted") is True
    delivery_performed = adapter_summary.get("delivery_performed") is True
    delivered_question_count = int(adapter_summary.get("delivered_question_count") or 0)

    readiness_checks = {
        "decision_gate_flag_enabled": decision_gate_flag_enabled,
        "all_required_owner_flags_enabled": len(missing_flags) == 0,
        "noop_adapter_ready": adapter_ready,
        "candidate_question_count_positive": candidate_question_count > 0,
        "delivery_attempted_false": delivery_attempted is False,
        "delivery_performed_false": delivery_performed is False,
        "delivered_question_count_zero": delivered_question_count == 0,
        "legacy_fallback_available": adapter_summary.get("legacy_fallback_available") is True,
        "requested_decision_supported": requested_decision in ALLOWED_DECISION_VALUES,
    }

    decision_gate_policy = {
        "real_delivery_allowed_now": False,
        "may_flip_effective_source_now": False,
        "may_start_live_session_now": False,
        "may_persist_session_now": False,
        "may_persist_attempts_now": False,
        "may_update_progress_now": False,
        "may_score_live_session_now": False,
        "requires_separate_real_delivery_milestone": True,
        "requires_owner_reconfirmation_before_real_delivery": True,
        "requires_rollback_to_legacy_fallback": True,
    }

    if not decision_gate_flag_enabled:
        status = "disabled"
        blocking_reasons = ["decision_gate_flag_disabled"]
        ready_for_next_decision = False
    elif missing_flags:
        status = "blocked"
        blocking_reasons = ["required_owner_review_flags_missing"]
        ready_for_next_decision = False
    elif requested_decision not in ALLOWED_DECISION_VALUES:
        status = "blocked"
        blocking_reasons = ["unsupported_requested_decision"]
        ready_for_next_decision = False
    elif not adapter_ready:
        status = "blocked"
        blocking_reasons = ["noop_delivery_adapter_not_ready"]
        ready_for_next_decision = False
    elif delivery_attempted or delivery_performed or delivered_question_count != 0:
        status = "blocked"
        blocking_reasons = ["unexpected_delivery_activity_detected"]
        ready_for_next_decision = False
    else:
        status = "decision_gate_ready_for_owner_review"
        blocking_reasons = []
        ready_for_next_decision = True

    owner_decision_result = {
        "requested_decision": requested_decision,
        "accepted_decision": requested_decision if ready_for_next_decision else "",
        "real_delivery_allowed_now": False,
        "delivery_attempted": False,
        "delivery_performed": False,
        "delivered_question_count": 0,
        "effective_source_after_decision": "legacy_fallback",
        "next_allowed_action": {
            "keep_noop_only": "stop_here_keep_noop_chain",
            "prepare_owner_panel_review": "add_or_reuse_owner_review_panel",
            "prepare_future_real_delivery_milestone": "create_separate_explicit_real_delivery_milestone",
        }.get(requested_decision, ""),
    }

    return {
        "schema_version": "1",
        "decision_gate_version": DECISION_GATE_VERSION,
        "mode": "guarded_first_live_trial_no_persistence_decision_gate",
        "course_id": course_id,
        "skill_id": skill_id,
        "decision_gate_flag_name": DECISION_GATE_FLAG_NAME,
        "decision_gate_flag_enabled": decision_gate_flag_enabled,
        "status": status,
        "blocking_reasons": blocking_reasons,
        "ready_for_next_decision": ready_for_next_decision,
        "requested_decision": requested_decision,
        "allowed_decision_values": ALLOWED_DECISION_VALUES,
        "required_owner_flags": REQUIRED_OWNER_FLAGS,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "depends_on_noop_delivery_adapter_flag": NOOP_DELIVERY_ADAPTER_FLAG_NAME,
        "noop_delivery_adapter_status": adapter.get("status"),
        "noop_delivery_adapter_ready": adapter_ready,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "readiness_checks": readiness_checks,
        "decision_gate_policy": decision_gate_policy,
        "owner_decision_result": owner_decision_result if ready_for_next_decision else {},
        "decision_summary": {
            "ready_for_next_decision": ready_for_next_decision,
            "real_delivery_allowed_now": False,
            "delivery_attempted": False,
            "delivery_performed": False,
            "delivered_question_count": 0,
            "candidate_question_count": candidate_question_count,
            "effective_source_after_decision": "legacy_fallback",
        },
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
            "decision gate does not change effective_source",
            "decision gate does not deliver local-bank questions live",
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
    parser = argparse.ArgumentParser(description="Build guarded first live trial no-persistence decision gate.")
    parser.add_argument("--course-id", default="v086-decision-gate")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--requested-decision", default="keep_noop_only")
    parser.add_argument("--expect-ready", action="store_true")
    parser.add_argument("--expect-disabled", action="store_true")
    args = parser.parse_args()

    result = build_first_live_trial_decision_gate(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
        requested_decision=args.requested_decision,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_ready and result["status"] != "decision_gate_ready_for_owner_review":
        return 2
    if args.expect_disabled and result["status"] != "disabled":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
