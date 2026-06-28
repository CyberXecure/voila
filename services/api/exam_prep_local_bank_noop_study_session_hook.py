"""No-op study-session hook for guarded local-bank live trial.

v0.4.63 adds a hook-shaped boundary that a future study session can call.
The hook is intentionally no-op:
- OFF keeps the legacy path unchanged
- ON reports the local_source_candidate from v0.4.62
- it never consumes local-bank questions live
- it never persists attempts/sessions/progress
- it never replaces live study sessions or legacy source
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_guarded_adapter_boundary import (
    ADAPTER_BOUNDARY_VERSION,
    build_guarded_adapter_boundary,
)
from exam_prep_local_bank_guarded_live_trial import LIVE_TRIAL_FLAG_NAME


NOOP_HOOK_VERSION = "v0.4.63"


def _flag_enabled(env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    value = str(source.get(LIVE_TRIAL_FLAG_NAME, "")).strip().lower()
    return value in {"1", "true", "yes", "on"}


def build_noop_study_session_hook(
    *,
    course_id: str = "v063-sample",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    old_mastery_preview: float = 0.40,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a no-op hook result without changing study-session behavior."""

    enabled = _flag_enabled(env)
    boundary = build_guarded_adapter_boundary(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        old_mastery_preview=old_mastery_preview,
        env={LIVE_TRIAL_FLAG_NAME: "1"} if enabled else {},
    )

    candidate_available = bool(boundary.get("local_source_candidate_available"))
    candidate = boundary.get("local_source_candidate") if candidate_available else None

    if candidate_available:
        hook_status = "local_source_candidate_reported_noop"
        hook_message = "Local-bank candidate is reported, but live study session remains legacy."
    else:
        hook_status = "legacy_path_unchanged"
        hook_message = "Guarded local-bank hook is disabled; legacy path is unchanged."

    return {
        "schema_version": "1",
        "noop_hook_version": NOOP_HOOK_VERSION,
        "mode": "guarded_live_trial_noop_study_session_hook",
        "flag_name": LIVE_TRIAL_FLAG_NAME,
        "flag_enabled": enabled,
        "adapter_boundary_version": ADAPTER_BOUNDARY_VERSION,
        "hook_status": hook_status,
        "hook_message": hook_message,
        "course_id": course_id,
        "skill_id": skill_id,
        "effective_source": "legacy_fallback",
        "reported_candidate_available": candidate_available,
        "reported_local_source_candidate": candidate,
        "study_session_contract": {
            "legacy_path_unchanged": True,
            "local_candidate_report_only": True,
            "future_live_hook_must_require_explicit_flag": True,
            "future_live_hook_must_keep_legacy_fallback": True,
            "future_live_hook_must_not_accept_user_filesystem_root": True,
        },
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
        "adapter_boundary": boundary,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build guarded local-bank no-op study-session hook result.")
    parser.add_argument("--course-id", default="v063-sample")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--old-mastery-preview", type=float, default=0.40)
    parser.add_argument("--strict-legacy", action="store_true")
    parser.add_argument("--strict-candidate-report", action="store_true")
    args = parser.parse_args()

    result = build_noop_study_session_hook(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
        old_mastery_preview=args.old_mastery_preview,
    )

    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.strict_legacy and result["hook_status"] != "legacy_path_unchanged":
        return 2

    if args.strict_candidate_report and result["hook_status"] != "local_source_candidate_reported_noop":
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

