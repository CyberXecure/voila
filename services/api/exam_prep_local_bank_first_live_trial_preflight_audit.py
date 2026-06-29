"""Guarded first live-trial preflight audit v0.4.90.

JSON-only local preflight audit before any separate real-delivery milestone.
No web route, no web_app.py patch, no public UI, no live delivery, no persistence,
no progress update, no live scoring, and no cloud/API requirement.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_first_live_trial_owner_checkpoint import build_owner_ready_checkpoint

PREFLIGHT_AUDIT_VERSION = "v0.4.90"
PREFLIGHT_AUDIT_FLAG_NAME = "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_PREFLIGHT_AUDIT"
OWNER_READY_CHECKPOINT_FLAG_NAME = "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_READY_CHECKPOINT"

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
    OWNER_READY_CHECKPOINT_FLAG_NAME,
    PREFLIGHT_AUDIT_FLAG_NAME,
]

OWNER_RECONFIRMATION_PHRASES = [
    "CONFIRM OWNER-ONLY NO-PERSISTENCE REAL DELIVERY",
    "CONFIRM ROLLBACK TO LEGACY_FALLBACK",
    "CONFIRM NO ATTEMPT OR PROGRESS PERSISTENCE",
    "CONFIRM MAX 5 LOCAL-BANK QUESTIONS",
]


def _flag_enabled(name: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return str(source.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def build_first_live_trial_preflight_audit(
    *,
    course_id: str = "v090-preflight-audit",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_env = env if env is not None else dict(os.environ)
    flag_states = {name: _flag_enabled(name, source_env) for name in REQUIRED_OWNER_FLAGS}
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]
    checkpoint = build_owner_ready_checkpoint(course_id=course_id, skill_id=skill_id, limit=limit, env=source_env)
    checkpoint_ready = checkpoint.get("status") == "owner_ready_checkpoint_complete_no_go_for_real_delivery"
    stop_go = checkpoint.get("stop_go_summary") if isinstance(checkpoint.get("stop_go_summary"), dict) else {}

    preflight_flag_enabled = flag_states.get(PREFLIGHT_AUDIT_FLAG_NAME, False)
    checks = {
        "preflight_flag_enabled": preflight_flag_enabled,
        "all_required_owner_flags_enabled": len(missing_flags) == 0,
        "owner_ready_checkpoint_complete": checkpoint_ready,
        "stop_go_label_is_stop": stop_go.get("stop_go_label") == "STOP",
        "go_for_real_delivery_now_false": stop_go.get("go_for_real_delivery_now") is False,
        "real_delivery_allowed_now_false": stop_go.get("real_delivery_allowed_now") is False,
        "delivery_performed_false": stop_go.get("delivery_performed") is False,
        "delivered_question_count_zero": int(stop_go.get("delivered_question_count") or 0) == 0,
        "effective_source_is_legacy": checkpoint.get("effective_source") == "legacy_fallback",
        "requires_new_milestone_for_real_delivery": stop_go.get("requires_new_milestone_for_real_delivery") is True,
        "requires_owner_reconfirmation_before_real_delivery": stop_go.get("requires_owner_reconfirmation_before_real_delivery") is True,
    }

    if not preflight_flag_enabled:
        status = "disabled"
        blocking_reasons = ["preflight_audit_flag_disabled"]
        complete = False
    elif missing_flags:
        status = "blocked"
        blocking_reasons = ["required_owner_review_flags_missing"]
        complete = False
    elif not checkpoint_ready or not all(checks.values()):
        status = "blocked"
        blocking_reasons = ["preflight_checks_failed"]
        complete = False
    else:
        status = "preflight_audit_complete_waiting_for_explicit_owner_reconfirmation"
        blocking_reasons = []
        complete = True

    return {
        "schema_version": "1",
        "preflight_audit_version": PREFLIGHT_AUDIT_VERSION,
        "mode": "guarded_first_live_trial_preflight_audit",
        "course_id": course_id,
        "skill_id": skill_id,
        "preflight_flag_name": PREFLIGHT_AUDIT_FLAG_NAME,
        "preflight_flag_enabled": preflight_flag_enabled,
        "status": status,
        "blocking_reasons": blocking_reasons,
        "preflight_audit_complete": complete,
        "required_owner_flags": REQUIRED_OWNER_FLAGS,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "owner_ready_checkpoint_status": checkpoint.get("status"),
        "owner_ready_checkpoint_complete": checkpoint_ready,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "preflight_checks": checks,
        "preflight_summary": {
            "preflight_audit_complete": complete,
            "preflight_label": "READY_FOR_SEPARATE_OWNER_DECISION_ONLY",
            "go_for_real_delivery_now": False,
            "real_delivery_allowed_now": False,
            "delivery_performed": False,
            "delivered_question_count": 0,
            "effective_source": "legacy_fallback",
            "requires_owner_reconfirmation": True,
            "requires_exact_reconfirmation_phrase": True,
        },
        "owner_reconfirmation_required": True,
        "owner_reconfirmation_phrases": OWNER_RECONFIRMATION_PHRASES,
        "real_delivery_milestone_requirements": [
            "separate explicit real-delivery milestone name",
            "manual owner reconfirmation in chat",
            "owner-only fixed course_id",
            "owner-only fixed skill_id",
            "max 5 sanitized local-bank questions",
            "no attempt persistence",
            "no session persistence",
            "no progress update",
            "no live scoring persistence",
            "rollback path to legacy_fallback",
            "final owner smoke after merge",
        ],
        "recommended_next_milestone": {
            "name": "v0.4.91-guarded-first-live-trial-owner-only-real-delivery-proposal",
            "may_deliver_live": False,
            "purpose": "prepare owner reconfirmation and rollback checklist before any real delivery implementation",
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
            "preflight audit does not change effective_source",
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
    parser.add_argument("--course-id", default="v090-preflight-audit")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--expect-ready", action="store_true")
    parser.add_argument("--expect-disabled", action="store_true")
    args = parser.parse_args()
    result = build_first_live_trial_preflight_audit(course_id=args.course_id, skill_id=args.skill_id, limit=args.limit)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    if args.expect_ready and result["status"] != "preflight_audit_complete_waiting_for_explicit_owner_reconfirmation":
        return 2
    if args.expect_disabled and result["status"] != "disabled":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
