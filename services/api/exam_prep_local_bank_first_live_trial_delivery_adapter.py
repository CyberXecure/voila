"""Guarded first live-trial no-persistence delivery adapter no-op.

v0.4.83 adds a JSON-only no-op adapter boundary for a future first live trial.
The adapter accepts the v0.4.82 no-persistence delivery contract, but does not
deliver anything. It returns delivery_performed=False by design.

This milestone still does not deliver questions live. It adds no web route,
does not patch web_app.py, does not modify public UI, and keeps the real
effective source as legacy_fallback.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_first_live_trial_delivery_contract import (
    NO_PERSISTENCE_DELIVERY_CONTRACT_FLAG_NAME,
    NO_PERSISTENCE_DELIVERY_CONTRACT_VERSION,
    build_no_persistence_delivery_contract,
)


NOOP_DELIVERY_ADAPTER_VERSION = "v0.4.83"
NOOP_DELIVERY_ADAPTER_FLAG_NAME = (
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DELIVERY_ADAPTER_NOOP"
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
    NO_PERSISTENCE_DELIVERY_CONTRACT_FLAG_NAME,
    NOOP_DELIVERY_ADAPTER_FLAG_NAME,
]


def _flag_enabled(name: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return str(source.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def build_noop_delivery_adapter_result(
    *,
    course_id: str = "v083-adapter-noop",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_env = env if env is not None else dict(os.environ)
    flag_states = {name: _flag_enabled(name, source_env) for name in REQUIRED_OWNER_FLAGS}
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]
    adapter_flag_enabled = flag_states.get(NOOP_DELIVERY_ADAPTER_FLAG_NAME, False)

    contract_report = build_no_persistence_delivery_contract(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        env=source_env,
    )
    contract_ready = (
        contract_report.get("status")
        == "no_persistence_delivery_contract_ready_for_owner_review"
    )
    delivery_contract = contract_report.get("delivery_contract")
    if not isinstance(delivery_contract, dict):
        delivery_contract = {}

    contract_summary = contract_report.get("contract_summary")
    if not isinstance(contract_summary, dict):
        contract_summary = {}

    candidate_question_count = int(contract_summary.get("candidate_question_count") or 0)

    adapter_result = {
        "adapter_schema_version": "1",
        "noop_delivery_adapter_version": NOOP_DELIVERY_ADAPTER_VERSION,
        "adapter_kind": "owner_only_no_persistence_delivery_adapter_noop",
        "course_id": course_id,
        "skill_id": skill_id,
        "requested_delivery_contract_version": delivery_contract.get("delivery_contract_version", ""),
        "requested_delivery_mode": delivery_contract.get("delivery_mode", "contract_only_not_live"),
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "candidate_question_count": candidate_question_count,
        "delivery_attempted": False,
        "delivery_performed": False,
        "delivered_question_count": 0,
        "delivered_question_ids": [],
        "would_deliver_if_future_enabled": candidate_question_count > 0,
        "noop_reason": "v0.4.83 validates adapter boundary only; real delivery remains disabled",
        "abort_to_effective_source": "legacy_fallback",
        "will_start_live_session": False,
        "will_replace_effective_source": False,
        "will_persist_session": False,
        "will_persist_attempts": False,
        "will_update_progress": False,
        "will_score_live_session": False,
    }

    adapter_contract_boundary = {
        "accepts_delivery_contract": True,
        "requires_no_persistence_policy": True,
        "requires_abort_policy": True,
        "requires_legacy_fallback": True,
        "requires_owner_only_scope": True,
        "requires_candidate_questions": True,
        "blocks_delivery_now": True,
        "returns_noop_result": True,
    }

    if not adapter_flag_enabled:
        status = "disabled"
        blocking_reasons = ["noop_delivery_adapter_flag_disabled"]
        adapter_ready = False
    elif missing_flags:
        status = "blocked"
        blocking_reasons = ["required_owner_review_flags_missing"]
        adapter_ready = False
    elif not contract_ready:
        status = "blocked"
        blocking_reasons = ["no_persistence_delivery_contract_not_ready"]
        adapter_ready = False
    elif candidate_question_count < 1:
        status = "blocked"
        blocking_reasons = ["no_candidate_questions_available"]
        adapter_ready = False
    elif adapter_result["delivery_performed"] is not False:
        status = "blocked"
        blocking_reasons = ["noop_adapter_must_not_deliver"]
        adapter_ready = False
    else:
        status = "noop_delivery_adapter_ready_for_owner_review"
        blocking_reasons = []
        adapter_ready = True

    return {
        "schema_version": "1",
        "noop_delivery_adapter_version": NOOP_DELIVERY_ADAPTER_VERSION,
        "mode": "guarded_first_live_trial_no_persistence_delivery_adapter_noop",
        "course_id": course_id,
        "skill_id": skill_id,
        "adapter_flag_name": NOOP_DELIVERY_ADAPTER_FLAG_NAME,
        "adapter_flag_enabled": adapter_flag_enabled,
        "status": status,
        "blocking_reasons": blocking_reasons,
        "ready_for_owner_review": adapter_ready,
        "required_owner_flags": REQUIRED_OWNER_FLAGS,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "depends_on_no_persistence_delivery_contract_version": NO_PERSISTENCE_DELIVERY_CONTRACT_VERSION,
        "no_persistence_delivery_contract_status": contract_report.get("status"),
        "no_persistence_delivery_contract_ready": contract_ready,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "adapter_contract_boundary": adapter_contract_boundary,
        "adapter_result": adapter_result if adapter_ready else {},
        "adapter_summary": {
            "delivery_attempted": False,
            "delivery_performed": False,
            "delivered_question_count": 0,
            "candidate_question_count": candidate_question_count,
            "noop_only": True,
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
            "noop delivery adapter does not change effective_source",
            "noop delivery adapter does not deliver local-bank questions live",
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
    parser = argparse.ArgumentParser(description="Build guarded first live trial no-persistence delivery adapter noop result.")
    parser.add_argument("--course-id", default="v083-adapter-noop")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--expect-ready", action="store_true")
    parser.add_argument("--expect-disabled", action="store_true")
    args = parser.parse_args()

    result = build_noop_delivery_adapter_result(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_ready and result["status"] != "noop_delivery_adapter_ready_for_owner_review":
        return 2
    if args.expect_disabled and result["status"] != "disabled":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
