"""Guarded first live-trial implementation readiness freeze v0.4.94.

JSON-only local freeze after the v0.4.93 activation/rollback playbook.

This module freezes the current no-op, preflight, reconfirmation, activation,
and rollback readiness chain. It does not make activation effective. It does not
implement real delivery. It adds no web route, does not patch web_app.py, does
not modify public UI, and keeps the real effective source as legacy_fallback.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_first_live_trial_activation_playbook import (
    ACTIVATION_PLAYBOOK_FLAG_NAME,
    build_activation_rollback_playbook,
)

READINESS_FREEZE_VERSION = "v0.4.94"
READINESS_FREEZE_FLAG_NAME = (
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_READINESS_FREEZE"
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
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DECISION_GATE",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_READY_CHECKPOINT",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_PREFLIGHT_AUDIT",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_REAL_DELIVERY_PROPOSAL_GATE",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_RECONFIRMATION_RECORD",
    ACTIVATION_PLAYBOOK_FLAG_NAME,
    READINESS_FREEZE_FLAG_NAME,
]

CHAIN_FREEZE_COMPONENTS = [
    "v0.4.77 contract skeleton",
    "v0.4.78 internal contract report route",
    "v0.4.79 hidden owner panel",
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
    "v0.4.90 preflight audit",
    "v0.4.91 real-delivery proposal gate",
    "v0.4.92 owner reconfirmation record draft",
    "v0.4.93 activation and rollback playbook",
    "v0.4.94 readiness freeze",
]


def _flag_enabled(name: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return str(source.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def build_implementation_readiness_freeze(
    *,
    course_id: str = "v094-readiness-freeze",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_env = env if env is not None else dict(os.environ)
    flag_states = {name: _flag_enabled(name, source_env) for name in REQUIRED_OWNER_FLAGS}
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]
    freeze_flag_enabled = flag_states.get(READINESS_FREEZE_FLAG_NAME, False)

    playbook = build_activation_rollback_playbook(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        env=source_env,
    )
    playbook_ready = playbook.get("status") == "activation_rollback_playbook_ready_activation_not_effective"
    playbook_summary = playbook.get("playbook_summary") if isinstance(playbook.get("playbook_summary"), dict) else {}

    freeze_checks = {
        "freeze_flag_enabled": freeze_flag_enabled,
        "all_required_owner_flags_enabled": len(missing_flags) == 0,
        "activation_playbook_ready": playbook_ready,
        "activation_effective_false": playbook.get("activation_effective") is False,
        "playbook_may_deliver_live_false": playbook_summary.get("may_deliver_live") is False,
        "playbook_go_for_real_delivery_now_false": playbook_summary.get("go_for_real_delivery_now") is False,
        "playbook_real_delivery_allowed_now_false": playbook_summary.get("real_delivery_allowed_now") is False,
        "playbook_delivery_performed_false": playbook_summary.get("delivery_performed") is False,
        "playbook_delivered_question_count_zero": int(playbook_summary.get("delivered_question_count") or 0) == 0,
        "effective_source_is_legacy": playbook.get("effective_source") == "legacy_fallback",
        "requires_new_explicit_real_delivery_milestone": playbook_summary.get("requires_new_explicit_real_delivery_milestone") is True,
        "requires_rollback_smoke": playbook_summary.get("requires_rollback_smoke") is True,
    }

    readiness_freeze = {
        "freeze_kind": "implementation_readiness_freeze",
        "readiness_freeze_version": READINESS_FREEZE_VERSION,
        "readiness_frozen": False,
        "no_more_gate_milestones_recommended": True,
        "next_step_policy": "STOP_OR_SEPARATE_REAL_DELIVERY_MILESTONE_ONLY",
        "allowed_next_steps": [
            "STOP",
            "separate_explicit_owner_only_real_delivery_implementation_milestone",
        ],
        "activation_effective": False,
        "may_deliver_live": False,
        "go_for_real_delivery_now": False,
        "real_delivery_allowed_now": False,
        "delivery_performed": False,
        "delivered_question_count": 0,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "frozen_chain_components": CHAIN_FREEZE_COMPONENTS,
        "real_delivery_requires": [
            "new separately named milestone",
            "explicit owner approval in chat",
            "owner-only fixed course_id",
            "owner-only fixed skill_id",
            "max 5 sanitized local-bank questions",
            "no attempt persistence",
            "no session persistence",
            "no progress update",
            "no live scoring persistence",
            "legacy_fallback rollback path",
            "rollback smoke after implementation",
            "final main smoke after merge",
        ],
        "do_not_continue_with_more_gates": True,
    }

    if not freeze_flag_enabled:
        status = "disabled"
        blocking_reasons = ["readiness_freeze_flag_disabled"]
        ready = False
    elif missing_flags:
        status = "blocked"
        blocking_reasons = ["required_owner_review_flags_missing"]
        ready = False
    elif not playbook_ready:
        status = "blocked"
        blocking_reasons = ["activation_rollback_playbook_not_ready"]
        ready = False
    elif not all(freeze_checks.values()):
        status = "blocked"
        blocking_reasons = ["readiness_freeze_checks_failed"]
        ready = False
    else:
        status = "implementation_readiness_frozen_waiting_for_stop_or_real_delivery_milestone"
        blocking_reasons = []
        ready = True
        readiness_freeze["readiness_frozen"] = True

    return {
        "schema_version": "1",
        "readiness_freeze_version": READINESS_FREEZE_VERSION,
        "mode": "guarded_first_live_trial_implementation_readiness_freeze",
        "course_id": course_id,
        "skill_id": skill_id,
        "freeze_flag_name": READINESS_FREEZE_FLAG_NAME,
        "freeze_flag_enabled": freeze_flag_enabled,
        "status": status,
        "blocking_reasons": blocking_reasons,
        "implementation_readiness_frozen": ready,
        "activation_effective": False,
        "required_owner_flags": REQUIRED_OWNER_FLAGS,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "activation_rollback_playbook_status": playbook.get("status"),
        "activation_rollback_playbook_ready": playbook_ready,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "freeze_checks": freeze_checks,
        "readiness_freeze": readiness_freeze if ready else {},
        "freeze_summary": {
            "implementation_readiness_frozen": ready,
            "no_more_gate_milestones_recommended": True,
            "next_step_policy": "STOP_OR_SEPARATE_REAL_DELIVERY_MILESTONE_ONLY",
            "activation_effective": False,
            "may_deliver_live": False,
            "go_for_real_delivery_now": False,
            "real_delivery_allowed_now": False,
            "delivery_performed": False,
            "delivered_question_count": 0,
            "requires_explicit_owner_approval_for_real_delivery": True,
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
            "readiness freeze does not change effective_source",
            "readiness freeze does not make activation effective",
            "readiness freeze does not deliver local-bank questions live",
            "may_deliver_live remains false",
            "go_for_real_delivery_now remains false",
            "real_delivery_allowed_now remains false",
            "delivery_performed remains false",
            "delivered_question_count remains zero",
            "local-bank questions are not consumed live",
            "live study sessions are not started",
            "attempts are not persisted",
            "progress is not updated",
            "sessions are not persisted",
            "live scoring is not enabled",
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--course-id", default="v094-readiness-freeze")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--expect-ready", action="store_true")
    parser.add_argument("--expect-disabled", action="store_true")
    args = parser.parse_args()
    result = build_implementation_readiness_freeze(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))
    if args.expect_ready and result["status"] != "implementation_readiness_frozen_waiting_for_stop_or_real_delivery_milestone":
        return 2
    if args.expect_disabled and result["status"] != "disabled":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
