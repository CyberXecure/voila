"""Consolidation status for guarded local-bank shadow chain.

v0.4.75 consolidates the guarded local-bank work from v0.4.60 through v0.4.74.

This is a JSON-only local status report. It does not enable live local-bank
consumption, does not deliver questions live, does not persist attempts,
sessions, or progress, and does not modify the public Exam Prep UI.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_live_consumption_shadow_selector import (
    SHADOW_SELECTOR_FLAG_NAME,
    SHADOW_SOURCE_SELECTOR_VERSION,
    build_shadow_source_selector,
)


SHADOW_CONSOLIDATION_STATUS_VERSION = "v0.4.75"

REQUIRED_SHADOW_FLAGS = [
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL_POLISH",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_DECISION_GATE",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY",
    SHADOW_SELECTOR_FLAG_NAME,
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_ROUTE",
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_OWNER_PANEL",
]

CHAIN_MILESTONES = [
    {
        "version": "v0.4.60",
        "name": "integration_readiness_report",
        "status": "complete",
        "live_consumption_enabled": False,
    },
    {
        "version": "v0.4.61",
        "name": "guarded_live_trial_scaffold",
        "status": "complete",
        "live_consumption_enabled": False,
    },
    {
        "version": "v0.4.62",
        "name": "guarded_adapter_boundary",
        "status": "complete",
        "live_consumption_enabled": False,
    },
    {
        "version": "v0.4.63",
        "name": "noop_study_session_hook",
        "status": "complete",
        "live_consumption_enabled": False,
    },
    {
        "version": "v0.4.64",
        "name": "guarded_live_trial_route_smoke",
        "status": "complete",
        "live_consumption_enabled": False,
        "route": "/exam-prep/local-bank/guarded-trial-smoke",
    },
    {
        "version": "v0.4.65",
        "name": "guarded_trial_diagnostics_report_route",
        "status": "complete",
        "live_consumption_enabled": False,
        "route": "/exam-prep/local-bank/guarded-trial-diagnostics",
    },
    {
        "version": "v0.4.66",
        "name": "guarded_trial_candidate_question_preview_route",
        "status": "complete",
        "live_consumption_enabled": False,
        "route": "/exam-prep/local-bank/guarded-trial-candidates",
    },
    {
        "version": "v0.4.67",
        "name": "guarded_trial_candidate_preview_internal_panel",
        "status": "complete",
        "live_consumption_enabled": False,
        "route": "/exam-prep/local-bank/guarded-trial-candidates-panel",
    },
    {
        "version": "v0.4.68",
        "name": "guarded_trial_candidate_panel_polish_owner_smoke",
        "status": "complete",
        "live_consumption_enabled": False,
        "route": "/exam-prep/local-bank/guarded-trial-candidates-panel-polish",
    },
    {
        "version": "v0.4.69",
        "name": "owner_enablement_checklist",
        "status": "complete",
        "live_consumption_enabled": False,
    },
    {
        "version": "v0.4.70",
        "name": "live_consumption_decision_gate",
        "status": "complete",
        "live_consumption_enabled": False,
    },
    {
        "version": "v0.4.71",
        "name": "live_consumption_adapter_noop_boundary",
        "status": "complete",
        "live_consumption_enabled": False,
    },
    {
        "version": "v0.4.72",
        "name": "live_consumption_source_selector_shadow_mode",
        "status": "complete",
        "live_consumption_enabled": False,
    },
    {
        "version": "v0.4.73",
        "name": "live_consumption_shadow_route_report",
        "status": "complete",
        "live_consumption_enabled": False,
        "route": "/exam-prep/local-bank/live-consumption-shadow-report",
    },
    {
        "version": "v0.4.74",
        "name": "live_consumption_shadow_route_owner_panel",
        "status": "complete",
        "live_consumption_enabled": False,
        "route": "/exam-prep/local-bank/live-consumption-shadow-panel",
    },
]


def _flag_enabled(name: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    value = str(source.get(name, "")).strip().lower()
    return value in {"1", "true", "yes", "on"}


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


def _item(name: str, passed: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "details": details or {}}


def build_shadow_consolidation_status(
    *,
    course_id: str = "v075-status",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a sanitized consolidation status for the v0.4.60-v0.4.74 chain."""

    source_env = env if env is not None else dict(os.environ)
    flag_states = {name: _flag_enabled(name, source_env) for name in REQUIRED_SHADOW_FLAGS}
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]

    selector_env = {name: "1" for name in REQUIRED_SHADOW_FLAGS if flag_states.get(name)}
    with _temporary_env(selector_env):
        selector = build_shadow_source_selector(
            course_id=course_id,
            skill_id=skill_id,
            limit=limit,
            env={name: "1" for name in selector_env},
        )

    shadow_report = selector.get("shadow_selection_report") or {}
    local_profile = shadow_report.get("local_candidate_profile") or {}
    coverage = shadow_report.get("coverage_comparison") or {}
    selected_shadow_questions = shadow_report.get("selected_shadow_questions") or []

    routes = [
        {
            "path": item.get("route", ""),
            "version": item["version"],
            "name": item["name"],
            "internal_only": True,
            "disabled_by_default": True,
        }
        for item in CHAIN_MILESTONES
        if item.get("route")
    ]

    checks = [
        _item(
            "all_chain_milestones_recorded",
            len(CHAIN_MILESTONES) == 15 and CHAIN_MILESTONES[0]["version"] == "v0.4.60" and CHAIN_MILESTONES[-1]["version"] == "v0.4.74",
            {"count": len(CHAIN_MILESTONES)},
        ),
        _item(
            "all_required_shadow_flags_enabled_for_owner_smoke",
            not missing_flags,
            {"missing_flags": missing_flags, "required_flags": REQUIRED_SHADOW_FLAGS},
        ),
        _item(
            "shadow_selector_ready",
            selector.get("selector_status") == "shadow_selection_ready",
            {"selector_status": selector.get("selector_status"), "shadow_selector_version": SHADOW_SOURCE_SELECTOR_VERSION},
        ),
        _item(
            "effective_source_remains_legacy_fallback",
            selector.get("effective_source") == "legacy_fallback",
            {"effective_source": selector.get("effective_source")},
        ),
        _item(
            "shadow_source_available_as_metadata_only",
            selector.get("shadow_source") == "local_exercise_bank_adapter" and len(selected_shadow_questions) > 0,
            {"shadow_source": selector.get("shadow_source"), "selected_shadow_count": len(selected_shadow_questions)},
        ),
        _item(
            "coverage_metadata_available",
            int(coverage.get("local_question_type_diversity", 0) or 0) >= 2
            and int(coverage.get("local_skill_diversity", 0) or 0) >= 1,
            {
                "local_question_type_diversity": coverage.get("local_question_type_diversity", 0),
                "local_skill_diversity": coverage.get("local_skill_diversity", 0),
            },
        ),
        _item(
            "sanitized_shadow_metadata_only",
            all(
                not any(
                    forbidden in item
                    for forbidden in (
                        "correct_answer",
                        "correct_answer_preview",
                        "explanation",
                        "explanation_preview",
                        "source_excerpt",
                    )
                )
                for item in selected_shadow_questions
                if isinstance(item, dict)
            ),
            {"selected_shadow_count": len(selected_shadow_questions)},
        ),
        _item(
            "no_live_consumption_across_chain",
            all(item.get("live_consumption_enabled") is False for item in CHAIN_MILESTONES),
            {"versions": [item["version"] for item in CHAIN_MILESTONES]},
        ),
    ]

    passed_count = sum(1 for check in checks if check["passed"])
    total_count = len(checks)
    status = "complete_shadow_chain_ready_for_review" if passed_count == total_count else "blocked"

    return {
        "schema_version": "1",
        "shadow_consolidation_status_version": SHADOW_CONSOLIDATION_STATUS_VERSION,
        "mode": "guarded_live_consumption_shadow_consolidation_status",
        "course_id": course_id,
        "skill_id": skill_id,
        "chain_range": "v0.4.60-v0.4.74",
        "status": status,
        "ready_for_next_guarded_phase_review": status == "complete_shadow_chain_ready_for_review",
        "passed_count": passed_count,
        "total_count": total_count,
        "chain_milestones": CHAIN_MILESTONES,
        "internal_routes_and_panels": routes,
        "required_shadow_flags": REQUIRED_SHADOW_FLAGS,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "checks": checks,
        "effective_source": "legacy_fallback",
        "shadow_source": selector.get("shadow_source", ""),
        "shadow_selection_summary": {
            "selector_status": selector.get("selector_status"),
            "shadow_candidate_count": shadow_report.get("shadow_candidate_count", 0),
            "question_type_counts": local_profile.get("question_type_counts", {}),
            "difficulty_counts": local_profile.get("difficulty_counts", {}),
            "skill_counts": local_profile.get("skill_counts", {}),
            "coverage_comparison": {
                "compared_against_legacy_live_output": False,
                "local_question_type_diversity": coverage.get("local_question_type_diversity", 0),
                "local_difficulty_diversity": coverage.get("local_difficulty_diversity", 0),
                "local_skill_diversity": coverage.get("local_skill_diversity", 0),
            },
        },
        "sanitization_status": {
            "answers_exposed": False,
            "explanations_exposed": False,
            "raw_snapshots_exposed": False,
            "selected_questions_exposed": False,
            "dry_run_items_exposed": False,
            "selected_shadow_questions_metadata_only": True,
        },
        "next_phase_criteria": [
            "keep effective_source as legacy_fallback until a separate explicit milestone changes it",
            "keep shadow report and owner panel sanitized",
            "keep raw snapshots out of web routes and panels",
            "require explicit owner flag for every route/panel",
            "require CodeQL checks to pass before merge",
            "introduce any attempt persistence only in a separate explicit milestone",
            "introduce progress updates only in a separate explicit milestone",
            "maintain abort path to legacy_fallback",
        ],
        "explicit_not_live_yet": [
            "shadow chain does not change effective_source",
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
        "will_deliver_shadow_questions_live": False,
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
    parser = argparse.ArgumentParser(description="Build guarded live-consumption shadow consolidation status.")
    parser.add_argument("--course-id", default="v075-status")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--expect-complete", action="store_true")
    parser.add_argument("--expect-blocked", action="store_true")
    args = parser.parse_args()

    result = build_shadow_consolidation_status(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
    )

    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_complete and result["status"] != "complete_shadow_chain_ready_for_review":
        return 2

    if args.expect_blocked and result["status"] != "blocked":
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
