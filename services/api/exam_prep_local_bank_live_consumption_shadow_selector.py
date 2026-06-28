"""Shadow source selector for future guarded local-bank live consumption.

v0.4.72 sits after the v0.4.71 adapter no-op boundary and compares the local
bank candidate against the legacy fallback path in shadow mode only.

It never changes the effective source. The effective source remains
legacy_fallback. No questions are delivered live, no attempts/sessions/progress
are persisted, and no live scoring is performed.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from typing import Any

from exam_prep_local_bank_live_consumption_adapter_noop_boundary import (
    LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY_VERSION,
    build_live_consumption_adapter_noop_boundary,
)
from exam_prep_local_bank_live_consumption_decision_gate import (
    REQUIRED_FLAGS_FOR_ELIGIBILITY,
)


SHADOW_SOURCE_SELECTOR_VERSION = "v0.4.72"
SHADOW_SELECTOR_FLAG_NAME = "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_SOURCE_SELECTOR"
ADAPTER_NOOP_BOUNDARY_FLAG_NAME = "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY"

REQUIRED_FLAGS_FOR_SHADOW_MODE = [
    *REQUIRED_FLAGS_FOR_ELIGIBILITY,
    ADAPTER_NOOP_BOUNDARY_FLAG_NAME,
    SHADOW_SELECTOR_FLAG_NAME,
]


def _flag_enabled(name: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    value = str(source.get(name, "")).strip().lower()
    return value in {"1", "true", "yes", "on"}


def _counter(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    values = [str(item.get(key, "")).strip() or "unknown" for item in items]
    return dict(sorted(Counter(values).items()))


def _extract_shadow_items(adapter_boundary: dict[str, Any]) -> list[dict[str, Any]]:
    decision_gate = adapter_boundary.get("decision_gate") or {}
    owner = decision_gate.get("owner_enablement_checklist") or {}
    readiness = (owner.get("snapshots") or {}).get("readiness") or {}
    source_selection = (readiness.get("snapshots") or {}).get("source_selection") or {}
    items = source_selection.get("dry_run_items") or []
    return [item for item in items if isinstance(item, dict)]


def build_shadow_source_selector(
    *,
    course_id: str = "v072-shadow",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    old_mastery_preview: float = 0.40,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build the shadow selector report without changing the effective source."""

    source_env = env if env is not None else dict(os.environ)
    flag_states = {name: _flag_enabled(name, source_env) for name in REQUIRED_FLAGS_FOR_SHADOW_MODE}
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]
    shadow_flag_enabled = flag_states.get(SHADOW_SELECTOR_FLAG_NAME, False)

    adapter_boundary = build_live_consumption_adapter_noop_boundary(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        old_mastery_preview=old_mastery_preview,
        env=source_env,
    )

    adapter_status = (
        adapter_boundary.get("boundary_status")
        or adapter_boundary.get("adapter_status")
        or ""
    )
    adapter_candidate_available = bool(
        adapter_boundary.get("adapter_candidate_available")
        or adapter_boundary.get("eligible_for_noop_adapter_candidate")
        or adapter_boundary.get("live_adapter_candidate")
        or adapter_boundary.get("adapter_candidate")
    )
    shadow_mode_ready = shadow_flag_enabled and adapter_candidate_available

    shadow_items = _extract_shadow_items(adapter_boundary) if shadow_mode_ready else []
    selected_shadow_items = shadow_items[: max(1, min(int(limit or 5), 20))]

    shadow_report = {
        "effective_source": "legacy_fallback",
        "shadow_source": "local_exercise_bank_adapter" if shadow_mode_ready else "",
        "shadow_mode_ready": shadow_mode_ready,
        "shadow_candidate_count": len(selected_shadow_items),
        "legacy_source_profile": {
            "source": "legacy_fallback",
            "remains_effective_source": True,
            "inspected_in_shadow": False,
        },
        "local_candidate_profile": {
            "source": "local_exercise_bank_adapter",
            "available": adapter_candidate_available,
            "question_count": len(selected_shadow_items),
            "question_type_counts": _counter(selected_shadow_items, "question_type"),
            "difficulty_counts": _counter(selected_shadow_items, "difficulty"),
            "skill_counts": _counter(selected_shadow_items, "skill_id"),
        },
        "coverage_comparison": {
            "compared_against_legacy_live_output": False,
            "reason": "legacy_fallback remains effective; shadow mode only inspects local candidate metadata.",
            "local_question_type_diversity": len(_counter(selected_shadow_items, "question_type")),
            "local_difficulty_diversity": len(_counter(selected_shadow_items, "difficulty")),
            "local_skill_diversity": len(_counter(selected_shadow_items, "skill_id")),
        },
        "selected_shadow_questions": [
            {
                "shadow_index": index,
                "question_id": item.get("question_id", ""),
                "skill_id": item.get("skill_id", ""),
                "question_type": item.get("question_type", ""),
                "difficulty": item.get("difficulty", ""),
                "source": item.get("source", "local_exercise_bank_adapter"),
                "dry_run_only": True,
                "will_deliver_live": False,
                "will_save_attempt": False,
                "will_update_progress": False,
                "will_score_answer": False,
            }
            for index, item in enumerate(selected_shadow_items, start=1)
        ],
    }

    if not shadow_flag_enabled:
        selector_status = "disabled"
        blocking_reasons = ["shadow_selector_flag_disabled"]
    elif not adapter_candidate_available:
        selector_status = "blocked"
        blocking_reasons = ["adapter_candidate_not_available"]
    else:
        selector_status = "shadow_selection_ready"
        blocking_reasons = []

    return {
        "schema_version": "1",
        "shadow_selector_version": SHADOW_SOURCE_SELECTOR_VERSION,
        "mode": "guarded_live_consumption_source_selector_shadow_mode",
        "course_id": course_id,
        "skill_id": skill_id,
        "shadow_selector_flag_name": SHADOW_SELECTOR_FLAG_NAME,
        "shadow_selector_flag_enabled": shadow_flag_enabled,
        "required_flags_for_shadow_mode": REQUIRED_FLAGS_FOR_SHADOW_MODE,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "adapter_noop_boundary_version": LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY_VERSION,
        "adapter_boundary_status": adapter_status,
        "selector_status": selector_status,
        "blocking_reasons": blocking_reasons,
        "effective_source": "legacy_fallback",
        "shadow_source": shadow_report["shadow_source"],
        "shadow_selection_report": shadow_report,
        "explicit_not_live_yet": [
            "shadow selector does not change effective_source",
            "local-bank questions are not delivered live",
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
        "adapter_noop_boundary": adapter_boundary,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build guarded live-consumption shadow source selector report.")
    parser.add_argument("--course-id", default="v072-shadow")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--old-mastery-preview", type=float, default=0.40)
    parser.add_argument("--expect-shadow-ready", action="store_true")
    parser.add_argument("--expect-disabled", action="store_true")
    args = parser.parse_args()

    result = build_shadow_source_selector(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
        old_mastery_preview=args.old_mastery_preview,
    )

    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_shadow_ready and result["selector_status"] != "shadow_selection_ready":
        return 2

    if args.expect_disabled and result["selector_status"] != "disabled":
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
