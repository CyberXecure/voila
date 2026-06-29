"""Guarded first live-trial owner reconfirmation record v0.4.92.

JSON-only local owner reconfirmation record / real-delivery authorization draft
after the v0.4.91 proposal gate.

This module does not make authorization effective. It does not implement real
delivery. It adds no web route, does not patch web_app.py, does not modify public
UI, and keeps the real effective source as legacy_fallback.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_first_live_trial_real_delivery_proposal import (
    PROPOSAL_GATE_FLAG_NAME,
    build_real_delivery_proposal_gate,
)

RECONFIRMATION_RECORD_VERSION = "v0.4.92"
RECONFIRMATION_RECORD_FLAG_NAME = (
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_RECONFIRMATION_RECORD"
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
    PROPOSAL_GATE_FLAG_NAME,
    RECONFIRMATION_RECORD_FLAG_NAME,
]

AUTHORIZATION_PHRASES = [
    "CONFIRM OWNER-ONLY NO-PERSISTENCE REAL DELIVERY",
    "CONFIRM ROLLBACK TO LEGACY_FALLBACK",
    "CONFIRM NO ATTEMPT OR PROGRESS PERSISTENCE",
    "CONFIRM MAX 5 LOCAL-BANK QUESTIONS",
    "CONFIRM SEPARATE REAL-DELIVERY MILESTONE",
]


def _flag_enabled(name: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return str(source.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def build_owner_reconfirmation_record(
    *,
    course_id: str = "v092-owner-reconfirmation-record",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_env = env if env is not None else dict(os.environ)
    flag_states = {name: _flag_enabled(name, source_env) for name in REQUIRED_OWNER_FLAGS}
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]
    record_flag_enabled = flag_states.get(RECONFIRMATION_RECORD_FLAG_NAME, False)

    proposal_gate = build_real_delivery_proposal_gate(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        env=source_env,
    )
    proposal_ready = (
        proposal_gate.get("status")
        == "real_delivery_proposal_ready_waiting_for_owner_reconfirmation"
    )
    proposal = proposal_gate.get("proposal") if isinstance(proposal_gate.get("proposal"), dict) else {}
    proposal_summary = (
        proposal_gate.get("proposal_summary")
        if isinstance(proposal_gate.get("proposal_summary"), dict)
        else {}
    )

    record_checks = {
        "record_flag_enabled": record_flag_enabled,
        "all_required_owner_flags_enabled": len(missing_flags) == 0,
        "proposal_gate_ready": proposal_ready,
        "proposal_may_deliver_live_false": proposal_summary.get("may_deliver_live") is False,
        "proposal_go_for_real_delivery_now_false": proposal_summary.get("go_for_real_delivery_now") is False,
        "proposal_real_delivery_allowed_now_false": proposal_summary.get("real_delivery_allowed_now") is False,
        "proposal_delivery_performed_false": proposal_summary.get("delivery_performed") is False,
        "proposal_delivered_question_count_zero": int(proposal_summary.get("delivered_question_count") or 0) == 0,
        "effective_source_is_legacy": proposal_gate.get("effective_source") == "legacy_fallback",
        "requires_separate_real_delivery_milestone": proposal_summary.get("requires_separate_real_delivery_milestone") is True,
        "requires_exact_owner_reconfirmation": proposal_summary.get("requires_exact_owner_reconfirmation") is True,
    }

    authorization_draft = {
        "authorization_record_kind": "owner_reconfirmation_record_draft",
        "authorization_record_version": RECONFIRMATION_RECORD_VERSION,
        "authorization_effective": False,
        "may_deliver_live": False,
        "go_for_real_delivery_now": False,
        "real_delivery_allowed_now": False,
        "delivery_performed": False,
        "delivered_question_count": 0,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "required_exact_phrases": AUTHORIZATION_PHRASES,
        "future_authorized_scope": {
            "owner_only": True,
            "fixed_course_id": course_id,
            "fixed_skill_id": skill_id,
            "max_questions": 5,
            "sanitized_question_envelopes_only": True,
            "no_public_ui": True,
            "no_attempt_persistence": True,
            "no_session_persistence": True,
            "no_progress_update": True,
            "no_live_scoring_persistence": True,
            "rollback_to_legacy_fallback": True,
        },
        "record_is_not_activation": True,
        "requires_next_milestone_to_activate": True,
        "next_milestone_must_be_explicit_real_delivery": True,
    }

    if not record_flag_enabled:
        status = "disabled"
        blocking_reasons = ["owner_reconfirmation_record_flag_disabled"]
        ready = False
    elif missing_flags:
        status = "blocked"
        blocking_reasons = ["required_owner_review_flags_missing"]
        ready = False
    elif not proposal_ready:
        status = "blocked"
        blocking_reasons = ["real_delivery_proposal_gate_not_ready"]
        ready = False
    elif not all(record_checks.values()):
        status = "blocked"
        blocking_reasons = ["owner_reconfirmation_record_checks_failed"]
        ready = False
    else:
        status = "owner_reconfirmation_record_ready_authorization_not_effective"
        blocking_reasons = []
        ready = True

    return {
        "schema_version": "1",
        "owner_reconfirmation_record_version": RECONFIRMATION_RECORD_VERSION,
        "mode": "guarded_first_live_trial_owner_reconfirmation_record",
        "course_id": course_id,
        "skill_id": skill_id,
        "record_flag_name": RECONFIRMATION_RECORD_FLAG_NAME,
        "record_flag_enabled": record_flag_enabled,
        "status": status,
        "blocking_reasons": blocking_reasons,
        "owner_reconfirmation_record_ready": ready,
        "authorization_effective": False,
        "required_owner_flags": REQUIRED_OWNER_FLAGS,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "real_delivery_proposal_gate_status": proposal_gate.get("status"),
        "real_delivery_proposal_gate_ready": proposal_ready,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "record_checks": record_checks,
        "authorization_draft": authorization_draft if ready else {},
        "record_summary": {
            "owner_reconfirmation_record_ready": ready,
            "authorization_effective": False,
            "may_deliver_live": False,
            "go_for_real_delivery_now": False,
            "real_delivery_allowed_now": False,
            "delivery_performed": False,
            "delivered_question_count": 0,
            "requires_next_explicit_real_delivery_milestone": True,
            "requires_final_owner_reconfirmation_in_chat": True,
        },
        "source_proposal_summary": {
            "proposal_ready_waiting_for_owner_reconfirmation": proposal_gate.get(
                "proposal_ready_waiting_for_owner_reconfirmation", False
            ),
            "proposal_kind": proposal.get("proposal_kind", ""),
            "future_activation_scope_present": bool(proposal.get("future_activation_scope")),
            "future_rollback_plan_present": bool(proposal.get("future_rollback_plan")),
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
            "owner reconfirmation record does not change effective_source",
            "owner reconfirmation record does not make authorization effective",
            "owner reconfirmation record does not deliver local-bank questions live",
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
    parser.add_argument("--course-id", default="v092-owner-reconfirmation-record")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--expect-ready", action="store_true")
    parser.add_argument("--expect-disabled", action="store_true")
    args = parser.parse_args()
    result = build_owner_reconfirmation_record(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))
    if args.expect_ready and result["status"] != "owner_reconfirmation_record_ready_authorization_not_effective":
        return 2
    if args.expect_disabled and result["status"] != "disabled":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
