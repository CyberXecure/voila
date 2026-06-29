"""Guarded first live-trial activation and rollback playbook v0.4.93.

JSON-only local activation plan / rollback playbook after the v0.4.92 owner
reconfirmation record.

This module does not make activation effective. It does not implement real
delivery. It adds no web route, does not patch web_app.py, does not modify
public UI, and keeps the real effective source as legacy_fallback.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_first_live_trial_owner_reconfirmation import (
    RECONFIRMATION_RECORD_FLAG_NAME,
    build_owner_reconfirmation_record,
)

ACTIVATION_PLAYBOOK_VERSION = "v0.4.93"
ACTIVATION_PLAYBOOK_FLAG_NAME = (
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_ACTIVATION_ROLLBACK_PLAYBOOK"
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
    RECONFIRMATION_RECORD_FLAG_NAME,
    ACTIVATION_PLAYBOOK_FLAG_NAME,
]

ROLLBACK_SMOKE_REQUIREMENTS = [
    "disable future real-delivery flag",
    "verify effective_source=legacy_fallback",
    "verify delivery_performed=false after rollback",
    "verify delivered_question_count=0 after rollback",
    "verify no attempts were persisted",
    "verify no progress was updated",
    "verify no public UI links were added",
]


def _flag_enabled(name: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return str(source.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def build_activation_rollback_playbook(
    *,
    course_id: str = "v093-activation-rollback-playbook",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_env = env if env is not None else dict(os.environ)
    flag_states = {name: _flag_enabled(name, source_env) for name in REQUIRED_OWNER_FLAGS}
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]
    playbook_flag_enabled = flag_states.get(ACTIVATION_PLAYBOOK_FLAG_NAME, False)

    record = build_owner_reconfirmation_record(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        env=source_env,
    )
    record_ready = record.get("status") == "owner_reconfirmation_record_ready_authorization_not_effective"
    record_summary = record.get("record_summary") if isinstance(record.get("record_summary"), dict) else {}

    playbook_checks = {
        "playbook_flag_enabled": playbook_flag_enabled,
        "all_required_owner_flags_enabled": len(missing_flags) == 0,
        "owner_reconfirmation_record_ready": record_ready,
        "authorization_effective_false": record.get("authorization_effective") is False,
        "record_may_deliver_live_false": record_summary.get("may_deliver_live") is False,
        "record_go_for_real_delivery_now_false": record_summary.get("go_for_real_delivery_now") is False,
        "record_real_delivery_allowed_now_false": record_summary.get("real_delivery_allowed_now") is False,
        "record_delivery_performed_false": record_summary.get("delivery_performed") is False,
        "record_delivered_question_count_zero": int(record_summary.get("delivered_question_count") or 0) == 0,
        "effective_source_is_legacy": record.get("effective_source") == "legacy_fallback",
        "requires_next_explicit_real_delivery_milestone": record_summary.get("requires_next_explicit_real_delivery_milestone") is True,
        "requires_final_owner_reconfirmation_in_chat": record_summary.get("requires_final_owner_reconfirmation_in_chat") is True,
    }

    activation_playbook = {
        "playbook_kind": "owner_only_no_persistence_real_delivery_activation_rollback_playbook",
        "activation_effective": False,
        "may_deliver_live": False,
        "go_for_real_delivery_now": False,
        "real_delivery_allowed_now": False,
        "delivery_performed": False,
        "delivered_question_count": 0,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "future_real_delivery_milestone_constraints": {
            "must_be_separate_milestone": True,
            "must_be_owner_only": True,
            "must_use_fixed_course_id": course_id,
            "must_use_fixed_skill_id": skill_id,
            "max_questions": 5,
            "must_use_sanitized_question_envelopes_only": True,
            "must_not_add_public_ui": True,
            "must_not_persist_attempts": True,
            "must_not_persist_sessions": True,
            "must_not_update_progress": True,
            "must_not_persist_live_scoring": True,
        },
        "activation_sequence": [
            "confirm exact owner phrases in chat",
            "create separate explicitly named real-delivery implementation milestone",
            "add a new disabled-by-default real-delivery flag",
            "keep no-op adapter and legacy_fallback rollback path available",
            "limit to owner-only fixed course_id and skill_id",
            "limit to max 5 sanitized local-bank questions",
            "run no-persistence route smoke",
            "run rollback smoke to legacy_fallback",
        ],
        "rollback_sequence": [
            "turn off future real-delivery flag",
            "force effective_source back to legacy_fallback",
            "verify no session persisted",
            "verify no attempts persisted",
            "verify no progress updated",
            "verify delivery_performed=false after rollback",
            "run owner smoke and preflight audit again",
        ],
        "rollback_smoke_requirements": ROLLBACK_SMOKE_REQUIREMENTS,
        "activation_is_not_approved_here": True,
        "requires_new_milestone_to_activate": True,
    }

    if not playbook_flag_enabled:
        status = "disabled"
        blocking_reasons = ["activation_playbook_flag_disabled"]
        ready = False
    elif missing_flags:
        status = "blocked"
        blocking_reasons = ["required_owner_review_flags_missing"]
        ready = False
    elif not record_ready:
        status = "blocked"
        blocking_reasons = ["owner_reconfirmation_record_not_ready"]
        ready = False
    elif not all(playbook_checks.values()):
        status = "blocked"
        blocking_reasons = ["activation_playbook_checks_failed"]
        ready = False
    else:
        status = "activation_rollback_playbook_ready_activation_not_effective"
        blocking_reasons = []
        ready = True

    return {
        "schema_version": "1",
        "activation_playbook_version": ACTIVATION_PLAYBOOK_VERSION,
        "mode": "guarded_first_live_trial_activation_rollback_playbook",
        "course_id": course_id,
        "skill_id": skill_id,
        "playbook_flag_name": ACTIVATION_PLAYBOOK_FLAG_NAME,
        "playbook_flag_enabled": playbook_flag_enabled,
        "status": status,
        "blocking_reasons": blocking_reasons,
        "activation_rollback_playbook_ready": ready,
        "activation_effective": False,
        "required_owner_flags": REQUIRED_OWNER_FLAGS,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "owner_reconfirmation_record_status": record.get("status"),
        "owner_reconfirmation_record_ready": record_ready,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "playbook_checks": playbook_checks,
        "activation_playbook": activation_playbook if ready else {},
        "playbook_summary": {
            "activation_rollback_playbook_ready": ready,
            "activation_effective": False,
            "may_deliver_live": False,
            "go_for_real_delivery_now": False,
            "real_delivery_allowed_now": False,
            "delivery_performed": False,
            "delivered_question_count": 0,
            "requires_new_explicit_real_delivery_milestone": True,
            "requires_rollback_smoke": True,
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
            "activation playbook does not change effective_source",
            "activation playbook does not make activation effective",
            "activation playbook does not deliver local-bank questions live",
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
    parser.add_argument("--course-id", default="v093-activation-rollback-playbook")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--expect-ready", action="store_true")
    parser.add_argument("--expect-disabled", action="store_true")
    args = parser.parse_args()
    result = build_activation_rollback_playbook(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))
    if args.expect_ready and result["status"] != "activation_rollback_playbook_ready_activation_not_effective":
        return 2
    if args.expect_disabled and result["status"] != "disabled":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
