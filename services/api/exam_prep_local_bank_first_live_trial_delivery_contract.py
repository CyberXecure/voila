"""Guarded first live-trial no-persistence delivery contract.

v0.4.82 defines the owner-only contract for a future first live delivery that
would use sanitized local-bank question envelopes, but with no attempt,
session, progress, or scoring persistence.

This milestone still does not deliver questions live. It adds no web route,
does not patch web_app.py, does not modify public UI, and keeps the real
effective source as legacy_fallback.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_first_live_trial_dry_run_session import (
    DRY_RUN_SESSION_ENVELOPE_FLAG_NAME,
    DRY_RUN_SESSION_ENVELOPE_VERSION,
    build_dry_run_session_envelope,
)


NO_PERSISTENCE_DELIVERY_CONTRACT_VERSION = "v0.4.82"
NO_PERSISTENCE_DELIVERY_CONTRACT_FLAG_NAME = (
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DELIVERY_CONTRACT"
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
    DRY_RUN_SESSION_ENVELOPE_FLAG_NAME,
    NO_PERSISTENCE_DELIVERY_CONTRACT_FLAG_NAME,
]


def _flag_enabled(name: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return str(source.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def _question_count(session_envelope: dict[str, Any]) -> int:
    questions = session_envelope.get("question_envelopes")
    if not isinstance(questions, list):
        return 0
    return len(questions)


def build_no_persistence_delivery_contract(
    *,
    course_id: str = "v082-delivery-contract",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_env = env if env is not None else dict(os.environ)
    flag_states = {name: _flag_enabled(name, source_env) for name in REQUIRED_OWNER_FLAGS}
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]
    delivery_contract_flag_enabled = flag_states.get(NO_PERSISTENCE_DELIVERY_CONTRACT_FLAG_NAME, False)

    dry_run = build_dry_run_session_envelope(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        env=source_env,
    )
    dry_run_ready = dry_run.get("status") == "dry_run_session_envelope_ready_for_owner_review"
    dry_run_session = dry_run.get("session_envelope") if isinstance(dry_run.get("session_envelope"), dict) else {}
    question_count = _question_count(dry_run_session)

    delivery_preconditions = {
        "owner_only_scope": True,
        "fixed_course_id": course_id,
        "fixed_skill_id": skill_id,
        "question_limit": min(max(int(limit), 0), 5),
        "dry_run_session_envelope_ready": dry_run_ready,
        "sanitized_question_envelopes_available": question_count > 0,
        "legacy_fallback_available": True,
        "attempt_persistence_disabled": True,
        "session_persistence_disabled": True,
        "progress_update_disabled": True,
        "live_scoring_disabled": True,
        "public_ui_change_disabled": True,
    }

    delivery_contract = {
        "contract_schema_version": "1",
        "delivery_contract_version": NO_PERSISTENCE_DELIVERY_CONTRACT_VERSION,
        "delivery_contract_kind": "owner_only_no_persistence_delivery_contract",
        "course_id": course_id,
        "skill_id": skill_id,
        "effective_source": "legacy_fallback",
        "candidate_delivery_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "candidate_question_count": question_count,
        "max_question_count": 5,
        "may_deliver_live_now": False,
        "delivery_mode": "contract_only_not_live",
        "delivery_scope": {
            "owner_only": True,
            "fixed_course_id": True,
            "fixed_skill_id": True,
            "max_questions": 5,
            "public_ui": False,
        },
        "no_persistence_policy": {
            "persist_session": False,
            "persist_attempts": False,
            "persist_progress": False,
            "update_progress": False,
            "score_live_session": False,
            "retain_user_answers": False,
        },
        "abort_policy": {
            "abort_to_effective_source": "legacy_fallback",
            "abort_if_missing_owner_flag": True,
            "abort_if_dry_run_not_ready": True,
            "abort_if_question_count_below_minimum": True,
            "abort_if_forbidden_fields_detected": True,
            "abort_if_persistence_requested": True,
            "abort_if_progress_update_requested": True,
            "abort_if_live_scoring_requested": True,
        },
        "future_delivery_requirements": [
            "separate explicit delivery implementation milestone",
            "route or session hook must remain owner-only",
            "sanitized question envelope only",
            "no answers or explanations before submission",
            "no attempts/session/progress persistence",
            "no live scoring persistence",
            "legacy_fallback abort path",
        ],
    }

    if not delivery_contract_flag_enabled:
        status = "disabled"
        blocking_reasons = ["no_persistence_delivery_contract_flag_disabled"]
        ready_for_owner_review = False
    elif missing_flags:
        status = "blocked"
        blocking_reasons = ["required_owner_review_flags_missing"]
        ready_for_owner_review = False
    elif not dry_run_ready:
        status = "blocked"
        blocking_reasons = ["dry_run_session_envelope_not_ready"]
        ready_for_owner_review = False
    elif question_count < 1:
        status = "blocked"
        blocking_reasons = ["no_sanitized_questions_available"]
        ready_for_owner_review = False
    else:
        status = "no_persistence_delivery_contract_ready_for_owner_review"
        blocking_reasons = []
        ready_for_owner_review = True

    return {
        "schema_version": "1",
        "no_persistence_delivery_contract_version": NO_PERSISTENCE_DELIVERY_CONTRACT_VERSION,
        "mode": "guarded_first_live_trial_no_persistence_delivery_contract",
        "course_id": course_id,
        "skill_id": skill_id,
        "delivery_contract_flag_name": NO_PERSISTENCE_DELIVERY_CONTRACT_FLAG_NAME,
        "delivery_contract_flag_enabled": delivery_contract_flag_enabled,
        "status": status,
        "blocking_reasons": blocking_reasons,
        "ready_for_owner_review": ready_for_owner_review,
        "required_owner_flags": REQUIRED_OWNER_FLAGS,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "depends_on_dry_run_session_envelope_version": DRY_RUN_SESSION_ENVELOPE_VERSION,
        "dry_run_session_envelope_status": dry_run.get("status"),
        "dry_run_session_envelope_ready": dry_run_ready,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "delivery_preconditions": delivery_preconditions,
        "delivery_contract": delivery_contract if ready_for_owner_review else {},
        "contract_summary": {
            "may_deliver_live_now": False,
            "delivery_mode": "contract_only_not_live",
            "candidate_question_count": question_count,
            "owner_only": True,
            "no_persistence": True,
            "legacy_fallback_available": True,
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
            "no-persistence delivery contract does not change effective_source",
            "contract does not deliver local-bank questions live",
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
    parser = argparse.ArgumentParser(description="Build guarded first live trial no-persistence delivery contract.")
    parser.add_argument("--course-id", default="v082-delivery-contract")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--expect-ready", action="store_true")
    parser.add_argument("--expect-disabled", action="store_true")
    args = parser.parse_args()

    result = build_no_persistence_delivery_contract(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_ready and result["status"] != "no_persistence_delivery_contract_ready_for_owner_review":
        return 2
    if args.expect_disabled and result["status"] != "disabled":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
