"""Owner enablement checklist for guarded local-bank Exam Prep trial.

v0.4.69 records the explicit owner-facing prerequisites before any future
milestone may attempt real guarded live consumption.

This module is JSON-only, local-only, and does not enable live local-bank
consumption. It does not persist attempts/sessions/progress, score live
sessions, or modify the Exam Prep UI.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_guarded_adapter_boundary import build_guarded_adapter_boundary
from exam_prep_local_bank_guarded_live_trial import (
    LIVE_TRIAL_FLAG_NAME,
    build_guarded_live_trial_scaffold,
)
from exam_prep_local_bank_integration_readiness import build_integration_readiness_report
from exam_prep_local_bank_noop_study_session_hook import build_noop_study_session_hook


OWNER_ENABLEMENT_CHECKLIST_VERSION = "v0.4.69"
DIAGNOSTICS_ROUTE_FLAG_NAME = "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE"
CANDIDATES_ROUTE_FLAG_NAME = "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE"
CANDIDATES_PANEL_FLAG_NAME = "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL"
CANDIDATES_PANEL_POLISH_FLAG_NAME = "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL_POLISH"

REQUIRED_OWNER_FLAGS = [
    LIVE_TRIAL_FLAG_NAME,
    DIAGNOSTICS_ROUTE_FLAG_NAME,
    CANDIDATES_ROUTE_FLAG_NAME,
    CANDIDATES_PANEL_FLAG_NAME,
    CANDIDATES_PANEL_POLISH_FLAG_NAME,
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
    return {
        "name": name,
        "passed": bool(passed),
        "details": details or {},
    }


def build_owner_enablement_checklist(
    *,
    course_id: str = "v069-owner",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    old_mastery_preview: float = 0.40,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build the owner enablement checklist without enabling live consumption."""

    source_env = env if env is not None else dict(os.environ)
    flag_states = {name: _flag_enabled(name, source_env) for name in REQUIRED_OWNER_FLAGS}
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]

    with _temporary_env({name: "1" for name in REQUIRED_OWNER_FLAGS if flag_states.get(name)}):
        readiness = build_integration_readiness_report(
            course_id=course_id,
            skill_id=skill_id,
            limit=limit,
            old_mastery_preview=old_mastery_preview,
        )
        trial = build_guarded_live_trial_scaffold(
            course_id=course_id,
            skill_id=skill_id,
            limit=limit,
            old_mastery_preview=old_mastery_preview,
            env={LIVE_TRIAL_FLAG_NAME: "1"} if flag_states.get(LIVE_TRIAL_FLAG_NAME) else {},
        )
        boundary = build_guarded_adapter_boundary(
            course_id=course_id,
            skill_id=skill_id,
            limit=limit,
            old_mastery_preview=old_mastery_preview,
            env={LIVE_TRIAL_FLAG_NAME: "1"} if flag_states.get(LIVE_TRIAL_FLAG_NAME) else {},
        )
        hook = build_noop_study_session_hook(
            course_id=course_id,
            skill_id=skill_id,
            limit=limit,
            old_mastery_preview=old_mastery_preview,
            env={LIVE_TRIAL_FLAG_NAME: "1"} if flag_states.get(LIVE_TRIAL_FLAG_NAME) else {},
        )

    checklist_items = [
        _item(
            "all_required_owner_flags_enabled",
            not missing_flags,
            {"required_flags": REQUIRED_OWNER_FLAGS, "missing_flags": missing_flags},
        ),
        _item(
            "integration_readiness_ready",
            readiness.get("readiness_status") == "ready_for_guarded_live_trial",
            {"readiness_status": readiness.get("readiness_status")},
        ),
        _item(
            "guarded_trial_plan_ready",
            trial.get("trial_status") == "guarded_trial_plan_ready",
            {"trial_status": trial.get("trial_status"), "flag_enabled": trial.get("flag_enabled")},
        ),
        _item(
            "adapter_boundary_candidate_available",
            boundary.get("boundary_status") == "local_source_candidate_available",
            {"boundary_status": boundary.get("boundary_status")},
        ),
        _item(
            "noop_hook_reports_candidate_only",
            hook.get("hook_status") == "local_source_candidate_reported_noop"
            and hook.get("effective_source") == "legacy_fallback",
            {
                "hook_status": hook.get("hook_status"),
                "effective_source": hook.get("effective_source"),
            },
        ),
        _item(
            "candidate_preview_route_flag_enabled",
            flag_states.get(CANDIDATES_ROUTE_FLAG_NAME, False),
            {"flag_name": CANDIDATES_ROUTE_FLAG_NAME},
        ),
        _item(
            "candidate_panel_flags_enabled",
            flag_states.get(CANDIDATES_PANEL_FLAG_NAME, False)
            and flag_states.get(CANDIDATES_PANEL_POLISH_FLAG_NAME, False),
            {
                "panel_flag": CANDIDATES_PANEL_FLAG_NAME,
                "panel_polish_flag": CANDIDATES_PANEL_POLISH_FLAG_NAME,
            },
        ),
        _item(
            "legacy_fallback_remains_effective_source",
            hook.get("effective_source") == "legacy_fallback",
            {"effective_source": hook.get("effective_source")},
        ),
    ]

    passed_count = sum(1 for item in checklist_items if item["passed"])
    total_count = len(checklist_items)
    all_passed = passed_count == total_count

    next_minimum_criteria = [
        "owner explicitly enables all guarded local-bank trial flags locally",
        "readiness_status remains ready_for_guarded_live_trial",
        "diagnostics route smoke passes",
        "candidate question preview route smoke passes",
        "candidate preview panel and polished panel owner smoke pass",
        "answers and explanations remain hidden in preview UI",
        "effective_source remains legacy_fallback until a separate live-consumption milestone",
        "legacy fallback remains available",
        "no user-provided filesystem root is accepted by web routes",
        "CodeQL and final main checks pass",
    ]

    return {
        "schema_version": "1",
        "owner_enablement_checklist_version": OWNER_ENABLEMENT_CHECKLIST_VERSION,
        "mode": "guarded_local_bank_owner_enablement_checklist",
        "course_id": course_id,
        "skill_id": skill_id,
        "checklist_status": "ready_for_owner_review" if all_passed else "blocked",
        "ready_for_owner_review": all_passed,
        "passed_count": passed_count,
        "total_count": total_count,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "checklist_items": checklist_items,
        "minimum_criteria_for_v0_4_70": next_minimum_criteria,
        "explicit_not_live_yet": [
            "local-bank questions are not consumed live",
            "live study sessions are not replaced",
            "effective_source remains legacy_fallback",
            "attempts are not persisted",
            "progress is not updated",
            "sessions are not persisted",
            "live scoring is not enabled",
            "public Exam Prep navigation is not changed",
        ],
        "path_policy": "no_user_provided_filesystem_root",
        "will_consume_local_bank_live": False,
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
        "snapshots": {
            "readiness": readiness,
            "guarded_trial": trial,
            "adapter_boundary": boundary,
            "noop_hook": hook,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build guarded local-bank owner enablement checklist.")
    parser.add_argument("--course-id", default="v069-owner")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--old-mastery-preview", type=float, default=0.40)
    parser.add_argument("--expect-ready", action="store_true")
    args = parser.parse_args()

    result = build_owner_enablement_checklist(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
        old_mastery_preview=args.old_mastery_preview,
    )

    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_ready and result["checklist_status"] != "ready_for_owner_review":
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
