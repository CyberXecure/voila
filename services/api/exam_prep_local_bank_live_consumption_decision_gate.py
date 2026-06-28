"""Decision gate for future guarded local-bank live consumption.

v0.4.70 introduces an explicit decision gate after the v0.4.69 owner
enablement checklist.

This gate is still not live consumption. It only reports whether the system is
eligible for an owner decision. It never consumes local-bank questions live,
starts live sessions, persists attempts/sessions/progress, scores live sessions,
or replaces the legacy source.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_owner_enablement_checklist import (
    CANDIDATES_PANEL_FLAG_NAME,
    CANDIDATES_PANEL_POLISH_FLAG_NAME,
    CANDIDATES_ROUTE_FLAG_NAME,
    DIAGNOSTICS_ROUTE_FLAG_NAME,
    LIVE_TRIAL_FLAG_NAME,
    OWNER_ENABLEMENT_CHECKLIST_VERSION,
    build_owner_enablement_checklist,
)


LIVE_CONSUMPTION_DECISION_GATE_VERSION = "v0.4.70"
LIVE_CONSUMPTION_DECISION_FLAG_NAME = "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_DECISION_GATE"

REQUIRED_FLAGS_FOR_ELIGIBILITY = [
    LIVE_TRIAL_FLAG_NAME,
    DIAGNOSTICS_ROUTE_FLAG_NAME,
    CANDIDATES_ROUTE_FLAG_NAME,
    CANDIDATES_PANEL_FLAG_NAME,
    CANDIDATES_PANEL_POLISH_FLAG_NAME,
    LIVE_CONSUMPTION_DECISION_FLAG_NAME,
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


def build_live_consumption_decision_gate(
    *,
    course_id: str = "v070-gate",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    old_mastery_preview: float = 0.40,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build the decision gate report without enabling live consumption."""

    source_env = env if env is not None else dict(os.environ)
    flag_states = {name: _flag_enabled(name, source_env) for name in REQUIRED_FLAGS_FOR_ELIGIBILITY}
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]

    owner_flags = {
        LIVE_TRIAL_FLAG_NAME: "1",
        DIAGNOSTICS_ROUTE_FLAG_NAME: "1",
        CANDIDATES_ROUTE_FLAG_NAME: "1",
        CANDIDATES_PANEL_FLAG_NAME: "1",
        CANDIDATES_PANEL_POLISH_FLAG_NAME: "1",
    }

    checklist_env = {
        name: "1"
        for name in owner_flags
        if flag_states.get(name)
    }

    with _temporary_env(checklist_env):
        checklist = build_owner_enablement_checklist(
            course_id=course_id,
            skill_id=skill_id,
            limit=limit,
            old_mastery_preview=old_mastery_preview,
            env={name: "1" for name in checklist_env},
        )

    checklist_ready = checklist.get("checklist_status") == "ready_for_owner_review"
    decision_flag_enabled = flag_states.get(LIVE_CONSUMPTION_DECISION_FLAG_NAME, False)
    eligible = checklist_ready and decision_flag_enabled and not missing_flags

    blocking_reasons: list[str] = []
    if missing_flags:
        blocking_reasons.append("required_flags_missing")
    if not checklist_ready:
        blocking_reasons.append("owner_enablement_checklist_not_ready")
    if not decision_flag_enabled:
        blocking_reasons.append("decision_gate_flag_disabled")

    decision_status = "eligible_for_owner_decision" if eligible else "blocked"

    return {
        "schema_version": "1",
        "decision_gate_version": LIVE_CONSUMPTION_DECISION_GATE_VERSION,
        "mode": "guarded_local_bank_live_consumption_decision_gate",
        "course_id": course_id,
        "skill_id": skill_id,
        "decision_flag_name": LIVE_CONSUMPTION_DECISION_FLAG_NAME,
        "decision_flag_enabled": decision_flag_enabled,
        "decision_status": decision_status,
        "eligible_for_owner_decision": eligible,
        "blocking_reasons": blocking_reasons,
        "required_flags_for_eligibility": REQUIRED_FLAGS_FOR_ELIGIBILITY,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "owner_enablement_checklist_version": OWNER_ENABLEMENT_CHECKLIST_VERSION,
        "owner_enablement_status": checklist.get("checklist_status"),
        "owner_enablement_ready": checklist_ready,
        "owner_decision_options": [
            "keep_disabled",
            "continue_preview_only",
            "plan_v0_4_71_guarded_live_consumption_adapter_noop",
        ],
        "recommended_owner_decision": (
            "continue_preview_only"
            if eligible
            else "keep_disabled_until_blocking_reasons_are_resolved"
        ),
        "explicit_not_live_yet": [
            "decision gate does not enable live consumption",
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
        "owner_enablement_checklist": checklist,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build guarded local-bank live consumption decision gate.")
    parser.add_argument("--course-id", default="v070-gate")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--old-mastery-preview", type=float, default=0.40)
    parser.add_argument("--expect-eligible", action="store_true")
    parser.add_argument("--expect-blocked", action="store_true")
    args = parser.parse_args()

    result = build_live_consumption_decision_gate(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
        old_mastery_preview=args.old_mastery_preview,
    )

    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_eligible and result["decision_status"] != "eligible_for_owner_decision":
        return 2

    if args.expect_blocked and result["decision_status"] != "blocked":
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
