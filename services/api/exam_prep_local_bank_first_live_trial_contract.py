"""Guarded first local-bank live trial contract skeleton.

v0.4.77 creates a JSON-only contract object for future owner review.
It is not live consumption and does not add a route, patch web_app.py, replace
study sessions, persist attempts/progress/sessions, or score live answers.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_shadow_consolidation_status import (
    SHADOW_CONSOLIDATION_STATUS_VERSION,
    build_shadow_consolidation_status,
)

FIRST_LIVE_TRIAL_CONTRACT_VERSION = "v0.4.77"
FIRST_LIVE_TRIAL_CONTRACT_FLAG_NAME = "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT"

OWNER_REVIEW_FLAGS = [
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
    FIRST_LIVE_TRIAL_CONTRACT_FLAG_NAME,
]


def _flag_enabled(name: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return str(source.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


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


def build_first_live_trial_contract(
    *,
    course_id: str = "v077-contract",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_env = env if env is not None else dict(os.environ)
    flag_states = {name: _flag_enabled(name, source_env) for name in OWNER_REVIEW_FLAGS}
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]
    contract_flag_enabled = flag_states.get(FIRST_LIVE_TRIAL_CONTRACT_FLAG_NAME, False)

    shadow_env = {name: "1" for name in OWNER_REVIEW_FLAGS if flag_states.get(name)}
    with _temporary_env(shadow_env):
        consolidation = build_shadow_consolidation_status(
            course_id=course_id,
            skill_id=skill_id,
            limit=limit,
            env={name: "1" for name in shadow_env},
        )

    consolidation_ready = consolidation.get("status") == "complete_shadow_chain_ready_for_review"

    if not contract_flag_enabled:
        contract_status = "disabled"
        blocking_reasons = ["first_live_trial_contract_flag_disabled"]
    elif missing_flags:
        contract_status = "blocked"
        blocking_reasons = ["required_owner_review_flags_missing"]
    elif not consolidation_ready:
        contract_status = "blocked"
        blocking_reasons = ["shadow_consolidation_not_ready"]
    else:
        contract_status = "contract_skeleton_ready_for_owner_review"
        blocking_reasons = []

    contract_sections = {
        "source_selection": {
            "current_effective_source": "legacy_fallback",
            "candidate_source": "local_exercise_bank_adapter",
            "fallback_source": "legacy_fallback",
            "may_select_candidate_live_now": False,
            "selection_mode": "contract_skeleton_only",
            "future_selection_requirements": [
                "explicit future live implementation flag",
                "quality gate pass immediately before candidate use",
                "sanitized live question envelope",
                "abort path tested",
                "legacy fallback available",
            ],
        },
        "session_boundary": {
            "will_start_live_session": False,
            "will_replace_live_study_session": False,
            "future_session_requirements": [
                "owner-only fixed smoke scope before general use",
                "explicit session id policy",
                "explicit rollback or abort behavior",
                "no public navigation change before owner approval",
            ],
        },
        "attempt_persistence": {
            "will_persist_attempts": False,
            "requires_separate_milestone": True,
            "future_attempt_requirements": [
                "attempt schema",
                "question id policy",
                "answer payload policy",
                "idempotency policy",
                "retention or no-retention decision",
            ],
        },
        "progress_updates": {
            "will_update_progress": False,
            "will_persist_progress": False,
            "requires_separate_milestone": True,
            "future_progress_requirements": [
                "progress impact schema",
                "mastery delta policy",
                "weak-review integration policy",
                "rollback behavior",
                "owner validation report",
            ],
        },
        "live_scoring": {
            "will_score_live_session": False,
            "requires_separate_milestone": True,
            "future_scoring_requirements": [
                "question-type-specific scoring rules",
                "accepted answer normalization",
                "manual review fallback",
                "score confidence policy",
                "no score persistence until explicitly enabled",
            ],
        },
        "sanitization": {
            "answers_exposed_before_submission": False,
            "explanations_exposed_before_submission": False,
            "raw_snapshots_exposed": False,
            "source_excerpts_exposed": False,
            "requires_safe_dom_rendering": True,
            "forbidden_pre_live_keys": [
                "correct_answer",
                "correct_answer_preview",
                "explanation",
                "explanation_preview",
                "source_excerpt",
                "raw_snapshots",
                "dry_run_items",
                "selected_questions",
            ],
        },
    }

    return {
        "schema_version": "1",
        "first_live_trial_contract_version": FIRST_LIVE_TRIAL_CONTRACT_VERSION,
        "mode": "guarded_first_live_trial_contract_skeleton",
        "course_id": course_id,
        "skill_id": skill_id,
        "contract_flag_name": FIRST_LIVE_TRIAL_CONTRACT_FLAG_NAME,
        "contract_flag_enabled": contract_flag_enabled,
        "contract_status": contract_status,
        "blocking_reasons": blocking_reasons,
        "required_owner_review_flags": OWNER_REVIEW_FLAGS,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "depends_on_shadow_consolidation_version": SHADOW_CONSOLIDATION_STATUS_VERSION,
        "shadow_consolidation_status": consolidation.get("status"),
        "shadow_consolidation_ready": consolidation_ready,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "contract_sections": contract_sections,
        "implementation_scope": {
            "json_only_contract_object": True,
            "adds_web_route": False,
            "patches_web_app": False,
            "adds_public_ui": False,
            "starts_live_session": False,
            "replaces_live_study_session": False,
            "persists_attempts": False,
            "updates_progress": False,
            "scores_live_session": False,
            "requires_cloud_or_api": False,
        },
        "next_allowed_milestone_options": [
            "keep_contract_skeleton_only",
            "add_owner_only_contract_report_route_disabled_by_default",
            "add_live_trial_question_envelope_sanitizer_disabled_by_default",
        ],
        "explicit_not_live_yet": [
            "contract skeleton does not change effective_source",
            "local-bank questions are not delivered live",
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
    parser = argparse.ArgumentParser(description="Build guarded first live trial contract skeleton.")
    parser.add_argument("--course-id", default="v077-contract")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--expect-ready", action="store_true")
    parser.add_argument("--expect-disabled", action="store_true")
    args = parser.parse_args()

    result = build_first_live_trial_contract(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_ready and result["contract_status"] != "contract_skeleton_ready_for_owner_review":
        return 2
    if args.expect_disabled and result["contract_status"] != "disabled":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
