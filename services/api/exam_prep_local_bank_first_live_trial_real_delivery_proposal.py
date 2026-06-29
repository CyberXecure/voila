"""Guarded first live-trial real-delivery proposal gate v0.4.91.

JSON-only local proposal/reconfirmation gate after the v0.4.90 preflight audit.
This module does not implement real delivery. It documents the future activation
scope, exact owner reconfirmation phrases, rollback requirements, and keeps
may_deliver_live=False.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_first_live_trial_preflight_audit import (
    PREFLIGHT_AUDIT_FLAG_NAME,
    build_first_live_trial_preflight_audit,
)

PROPOSAL_GATE_VERSION = "v0.4.91"
PROPOSAL_GATE_FLAG_NAME = "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_REAL_DELIVERY_PROPOSAL_GATE"

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
    PREFLIGHT_AUDIT_FLAG_NAME,
    PROPOSAL_GATE_FLAG_NAME,
]

EXACT_OWNER_RECONFIRMATION_PHRASES = [
    "CONFIRM OWNER-ONLY NO-PERSISTENCE REAL DELIVERY",
    "CONFIRM ROLLBACK TO LEGACY_FALLBACK",
    "CONFIRM NO ATTEMPT OR PROGRESS PERSISTENCE",
    "CONFIRM MAX 5 LOCAL-BANK QUESTIONS",
    "CONFIRM SEPARATE REAL-DELIVERY MILESTONE",
]


def _flag_enabled(name: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return str(source.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def build_real_delivery_proposal_gate(
    *,
    course_id: str = "v091-real-delivery-proposal",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_env = env if env is not None else dict(os.environ)
    flag_states = {name: _flag_enabled(name, source_env) for name in REQUIRED_OWNER_FLAGS}
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]
    proposal_flag_enabled = flag_states.get(PROPOSAL_GATE_FLAG_NAME, False)

    preflight = build_first_live_trial_preflight_audit(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        env=source_env,
    )
    preflight_ready = preflight.get("status") == "preflight_audit_complete_waiting_for_explicit_owner_reconfirmation"
    preflight_summary = preflight.get("preflight_summary") if isinstance(preflight.get("preflight_summary"), dict) else {}

    proposal_checks = {
        "proposal_gate_flag_enabled": proposal_flag_enabled,
        "all_required_owner_flags_enabled": len(missing_flags) == 0,
        "preflight_audit_complete": preflight_ready,
        "preflight_requires_owner_reconfirmation": preflight.get("owner_reconfirmation_required") is True,
        "preflight_go_for_real_delivery_now_false": preflight_summary.get("go_for_real_delivery_now") is False,
        "preflight_real_delivery_allowed_now_false": preflight_summary.get("real_delivery_allowed_now") is False,
        "preflight_delivery_performed_false": preflight_summary.get("delivery_performed") is False,
        "effective_source_is_legacy": preflight.get("effective_source") == "legacy_fallback",
    }

    proposal = {
        "proposal_kind": "owner_only_no_persistence_real_delivery_proposal",
        "may_deliver_live": False,
        "go_for_real_delivery_now": False,
        "real_delivery_allowed_now": False,
        "delivery_performed": False,
        "delivered_question_count": 0,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "future_activation_scope": {
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
        },
        "future_rollback_plan": {
            "rollback_to_effective_source": "legacy_fallback",
            "disable_real_delivery_flag": True,
            "keep_noop_adapter_available": True,
            "final_owner_smoke_required": True,
        },
        "exact_owner_reconfirmation_phrases": EXACT_OWNER_RECONFIRMATION_PHRASES,
        "required_before_activation": [
            "new separate real-delivery milestone",
            "manual owner reconfirmation in chat",
            "no-persistence route implementation",
            "sanitized envelope verification",
            "rollback smoke test to legacy_fallback",
            "final main smoke after merge",
        ],
    }

    if not proposal_flag_enabled:
        status = "disabled"
        blocking_reasons = ["proposal_gate_flag_disabled"]
        ready = False
    elif missing_flags:
        status = "blocked"
        blocking_reasons = ["required_owner_review_flags_missing"]
        ready = False
    elif not preflight_ready:
        status = "blocked"
        blocking_reasons = ["preflight_audit_not_complete"]
        ready = False
    elif not all(proposal_checks.values()):
        status = "blocked"
        blocking_reasons = ["proposal_checks_failed"]
        ready = False
    else:
        status = "real_delivery_proposal_ready_waiting_for_owner_reconfirmation"
        blocking_reasons = []
        ready = True

    return {
        "schema_version": "1",
        "proposal_gate_version": PROPOSAL_GATE_VERSION,
        "mode": "guarded_first_live_trial_real_delivery_proposal_gate",
        "course_id": course_id,
        "skill_id": skill_id,
        "proposal_gate_flag_name": PROPOSAL_GATE_FLAG_NAME,
        "proposal_gate_flag_enabled": proposal_flag_enabled,
        "status": status,
        "blocking_reasons": blocking_reasons,
        "proposal_ready_waiting_for_owner_reconfirmation": ready,
        "required_owner_flags": REQUIRED_OWNER_FLAGS,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "preflight_audit_status": preflight.get("status"),
        "preflight_audit_complete": preflight_ready,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "proposal_checks": proposal_checks,
        "proposal": proposal if ready else {},
        "proposal_summary": {
            "proposal_ready_waiting_for_owner_reconfirmation": ready,
            "may_deliver_live": False,
            "go_for_real_delivery_now": False,
            "real_delivery_allowed_now": False,
            "delivery_performed": False,
            "delivered_question_count": 0,
            "requires_separate_real_delivery_milestone": True,
            "requires_exact_owner_reconfirmation": True,
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
            "proposal gate does not change effective_source",
            "proposal gate does not deliver local-bank questions live",
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
    parser.add_argument("--course-id", default="v091-real-delivery-proposal")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--expect-ready", action="store_true")
    parser.add_argument("--expect-disabled", action="store_true")
    args = parser.parse_args()
    result = build_real_delivery_proposal_gate(course_id=args.course_id, skill_id=args.skill_id, limit=args.limit)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    if args.expect_ready and result["status"] != "real_delivery_proposal_ready_waiting_for_owner_reconfirmation":
        return 2
    if args.expect_disabled and result["status"] != "disabled":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
