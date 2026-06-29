"""Owner-only local-bank first real delivery for Voila Exam Prep v0.5.0.

This is the first separately approved real-delivery implementation after the
v0.4.94 readiness freeze.

Safety scope:
- owner-only
- local exercise bank only
- maximum 5 sanitized questions
- no public UI
- no web_app.py patch
- no attempts/session/progress persistence
- no live scoring persistence
- rollback to legacy_fallback by default or on any failed guard
- no cloud/API/LLM dependency

v0.5.1 keeps the delivery target and readiness guard target separable:
- readiness guard uses the canonical v0.5.0/v0.4.94 context
- delivery may target a real course smoke context
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from exam_prep_local_bank_adapter import build_local_bank_adapter_preview
from exam_prep_local_bank_first_live_trial_question_envelope import (
    sanitize_first_live_trial_question_envelope,
)
from exam_prep_local_bank_first_live_trial_readiness_freeze import (
    READINESS_FREEZE_VERSION,
    build_implementation_readiness_freeze,
)


OWNER_ONLY_FIRST_REAL_DELIVERY_VERSION = "v0.5.0"
OWNER_ONLY_FIRST_REAL_DELIVERY_FLAG_NAME = (
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_OWNER_ONLY_FIRST_REAL_DELIVERY"
)
OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK_FLAG_NAME = (
    "VOILA_FORCE_EXAM_PREP_LOCAL_BANK_OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK"
)
MAX_OWNER_ONLY_REAL_DELIVERY_QUESTIONS = 5
READINESS_GUARD_COURSE_ID = "v050-owner-only-local-bank-first-real-delivery"
READINESS_GUARD_SKILL_ID = "local_concept_001_functiile"


def configure_stdout_utf8() -> None:
    """Make CLI JSON output safe on Windows consoles."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def _flag_enabled(name: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return str(source.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def _safe_limit(limit: int | None) -> int:
    try:
        requested = int(limit if limit is not None else MAX_OWNER_ONLY_REAL_DELIVERY_QUESTIONS)
    except (TypeError, ValueError):
        requested = MAX_OWNER_ONLY_REAL_DELIVERY_QUESTIONS
    return min(max(requested, 0), MAX_OWNER_ONLY_REAL_DELIVERY_QUESTIONS)


def _fallback_result(
    *,
    course_id: str,
    skill_id: str,
    requested_limit: int,
    status: str,
    blocking_reasons: list[str],
    flag_enabled: bool,
    rollback_requested: bool,
    readiness_course_id: str = READINESS_GUARD_COURSE_ID,
    readiness_skill_id: str = READINESS_GUARD_SKILL_ID,
    readiness_freeze: dict[str, Any] | None = None,
    local_bank_preview: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "1",
        "owner_only_first_real_delivery_version": OWNER_ONLY_FIRST_REAL_DELIVERY_VERSION,
        "mode": "owner_only_local_bank_first_real_delivery",
        "course_id": course_id,
        "skill_id": skill_id,
        "readiness_guard_course_id": readiness_course_id,
        "readiness_guard_skill_id": readiness_skill_id,
        "delivery_flag_name": OWNER_ONLY_FIRST_REAL_DELIVERY_FLAG_NAME,
        "delivery_flag_enabled": flag_enabled,
        "rollback_flag_name": OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK_FLAG_NAME,
        "rollback_requested": rollback_requested,
        "status": status,
        "blocking_reasons": blocking_reasons,
        "activation_effective": False,
        "may_deliver_live": False,
        "real_delivery_allowed_now": False,
        "delivery_attempted": False,
        "delivery_performed": False,
        "delivered_question_count": 0,
        "delivered_question_ids": [],
        "requested_limit": requested_limit,
        "max_question_count": MAX_OWNER_ONLY_REAL_DELIVERY_QUESTIONS,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "questions": [],
        "readiness_freeze_status": (readiness_freeze or {}).get("status", ""),
        "readiness_freeze_version": READINESS_FREEZE_VERSION,
        "local_bank_preview_status": (local_bank_preview or {}).get("mode", ""),
        "local_bank_question_count": int((local_bank_preview or {}).get("question_count") or 0),
        "rollback_result": {
            "rolled_back_to": "legacy_fallback",
            "delivery_performed": False,
            "delivered_question_count": 0,
            "effective_source": "legacy_fallback",
        },
        "implementation_scope": {
            "json_only_local_module": True,
            "adds_web_route": False,
            "patches_web_app": False,
            "adds_public_ui": False,
            "owner_only": True,
            "uses_local_bank": False,
            "max_questions": MAX_OWNER_ONLY_REAL_DELIVERY_QUESTIONS,
            "persists_sessions": False,
            "persists_attempts": False,
            "updates_progress": False,
            "scores_live_session": False,
            "requires_cloud_or_api": False,
        },
        "no_persistence_policy": {
            "persist_session": False,
            "persist_attempts": False,
            "persist_progress": False,
            "update_progress": False,
            "score_live_session": False,
            "retain_user_answers": False,
        },
    }


def _safe_delivered_question(candidate: dict[str, Any], display_index: int) -> dict[str, Any]:
    envelope = sanitize_first_live_trial_question_envelope(candidate, display_index=display_index)

    return {
        "delivery_schema_version": "1",
        "question_id": envelope.get("question_id", ""),
        "skill_id": envelope.get("skill_id", ""),
        "question_type": envelope.get("question_type", ""),
        "difficulty": envelope.get("difficulty", ""),
        "source": "local_exercise_bank_adapter",
        "display_index": display_index,
        "prompt": envelope.get("prompt", ""),
        "choices": envelope.get("choices", []),
        "answer_hidden_until_submission": True,
        "explanation_hidden_until_submission": True,
        "will_save_attempt": False,
        "will_update_progress": False,
        "will_score_answer": False,
    }


def build_owner_only_first_real_delivery(
    *,
    root: str | Path = ".",
    course_id: str = "v050-owner-only-local-bank-first-real-delivery",
    skill_id: str = "local_concept_001_functiile",
    readiness_course_id: str = READINESS_GUARD_COURSE_ID,
    readiness_skill_id: str = READINESS_GUARD_SKILL_ID,
    limit: int = MAX_OWNER_ONLY_REAL_DELIVERY_QUESTIONS,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_env = env if env is not None else dict(os.environ)
    requested_limit = _safe_limit(limit)
    flag_enabled = _flag_enabled(OWNER_ONLY_FIRST_REAL_DELIVERY_FLAG_NAME, source_env)
    rollback_requested = _flag_enabled(
        OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK_FLAG_NAME,
        source_env,
    )

    if not flag_enabled:
        return _fallback_result(
            course_id=course_id,
            skill_id=skill_id,
            readiness_course_id=readiness_course_id,
            readiness_skill_id=readiness_skill_id,
            requested_limit=requested_limit,
            status="disabled",
            blocking_reasons=["owner_only_first_real_delivery_flag_disabled"],
            flag_enabled=flag_enabled,
            rollback_requested=rollback_requested,
        )

    if rollback_requested:
        return _fallback_result(
            course_id=course_id,
            skill_id=skill_id,
            readiness_course_id=readiness_course_id,
            readiness_skill_id=readiness_skill_id,
            requested_limit=requested_limit,
            status="rolled_back_to_legacy_fallback",
            blocking_reasons=["rollback_flag_enabled"],
            flag_enabled=flag_enabled,
            rollback_requested=rollback_requested,
        )

    readiness_freeze = build_implementation_readiness_freeze(
        course_id=readiness_course_id,
        skill_id=readiness_skill_id,
        limit=requested_limit,
        env=source_env,
    )
    readiness_ready = (
        readiness_freeze.get("status")
        == "implementation_readiness_frozen_waiting_for_stop_or_real_delivery_milestone"
        and readiness_freeze.get("implementation_readiness_frozen") is True
        and readiness_freeze.get("effective_source") == "legacy_fallback"
    )

    if not readiness_ready:
        return _fallback_result(
            course_id=course_id,
            skill_id=skill_id,
            readiness_course_id=readiness_course_id,
            readiness_skill_id=readiness_skill_id,
            requested_limit=requested_limit,
            status="blocked",
            blocking_reasons=["v0_4_94_readiness_freeze_not_ready"],
            flag_enabled=flag_enabled,
            rollback_requested=rollback_requested,
            readiness_freeze=readiness_freeze,
        )

    local_bank_preview = build_local_bank_adapter_preview(
        root,
        course_id=course_id,
        limit=requested_limit,
    )
    candidates = local_bank_preview.get("questions")
    if not isinstance(candidates, list):
        candidates = []

    skill_candidates = [
        candidate
        for candidate in candidates
        if isinstance(candidate, dict) and str(candidate.get("skill_id", "")).strip() == skill_id
    ][:requested_limit]

    if not skill_candidates:
        return _fallback_result(
            course_id=course_id,
            skill_id=skill_id,
            readiness_course_id=readiness_course_id,
            readiness_skill_id=readiness_skill_id,
            requested_limit=requested_limit,
            status="blocked",
            blocking_reasons=["no_matching_local_bank_questions_available"],
            flag_enabled=flag_enabled,
            rollback_requested=rollback_requested,
            readiness_freeze=readiness_freeze,
            local_bank_preview=local_bank_preview,
        )

    delivered_questions = [
        _safe_delivered_question(candidate, display_index=index)
        for index, candidate in enumerate(skill_candidates, start=1)
    ]
    delivered_question_ids = [
        str(question.get("question_id", ""))
        for question in delivered_questions
        if str(question.get("question_id", "")).strip()
    ]

    return {
        "schema_version": "1",
        "owner_only_first_real_delivery_version": OWNER_ONLY_FIRST_REAL_DELIVERY_VERSION,
        "mode": "owner_only_local_bank_first_real_delivery",
        "course_id": course_id,
        "skill_id": skill_id,
        "readiness_guard_course_id": readiness_course_id,
        "readiness_guard_skill_id": readiness_skill_id,
        "delivery_flag_name": OWNER_ONLY_FIRST_REAL_DELIVERY_FLAG_NAME,
        "delivery_flag_enabled": flag_enabled,
        "rollback_flag_name": OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK_FLAG_NAME,
        "rollback_requested": rollback_requested,
        "status": "owner_only_first_real_delivery_performed",
        "blocking_reasons": [],
        "activation_effective": True,
        "may_deliver_live": True,
        "real_delivery_allowed_now": True,
        "delivery_attempted": True,
        "delivery_performed": True,
        "delivered_question_count": len(delivered_questions),
        "delivered_question_ids": delivered_question_ids,
        "requested_limit": requested_limit,
        "max_question_count": MAX_OWNER_ONLY_REAL_DELIVERY_QUESTIONS,
        "effective_source": "local_bank",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "questions": delivered_questions,
        "readiness_freeze_status": readiness_freeze.get("status", ""),
        "readiness_freeze_version": READINESS_FREEZE_VERSION,
        "local_bank_preview_status": local_bank_preview.get("mode", ""),
        "local_bank_question_count": int(local_bank_preview.get("question_count") or 0),
        "rollback_result": {
            "rolled_back_to": "legacy_fallback",
            "delivery_performed": False,
            "delivered_question_count": 0,
            "effective_source": "legacy_fallback",
        },
        "implementation_scope": {
            "json_only_local_module": True,
            "adds_web_route": False,
            "patches_web_app": False,
            "adds_public_ui": False,
            "owner_only": True,
            "uses_local_bank": True,
            "max_questions": MAX_OWNER_ONLY_REAL_DELIVERY_QUESTIONS,
            "persists_sessions": False,
            "persists_attempts": False,
            "updates_progress": False,
            "scores_live_session": False,
            "requires_cloud_or_api": False,
        },
        "no_persistence_policy": {
            "persist_session": False,
            "persist_attempts": False,
            "persist_progress": False,
            "update_progress": False,
            "score_live_session": False,
            "retain_user_answers": False,
        },
    }


def _assert_no_forbidden_delivery_fields(result: dict[str, Any]) -> bool:
    forbidden = {
        "correct_answer",
        "correct_answer_preview",
        "answer",
        "expected_answer",
        "solution",
        "explanation",
        "explanation_preview",
        "source_excerpt",
        "raw_snapshots",
        "raw_contract",
        "dry_run_items",
        "selected_questions",
    }

    def walk(value: Any) -> bool:
        if isinstance(value, dict):
            for key, nested in value.items():
                if key in forbidden:
                    return False
                if not walk(nested):
                    return False
        elif isinstance(value, list):
            for item in value:
                if not walk(item):
                    return False
        return True

    return walk(result.get("questions", []))


def main() -> int:
    configure_stdout_utf8()

    parser = argparse.ArgumentParser(description="Build owner-only local-bank first real delivery result.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--course-id", default="v050-owner-only-local-bank-first-real-delivery")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--readiness-course-id", default=READINESS_GUARD_COURSE_ID)
    parser.add_argument("--readiness-skill-id", default=READINESS_GUARD_SKILL_ID)
    parser.add_argument("--limit", type=int, default=MAX_OWNER_ONLY_REAL_DELIVERY_QUESTIONS)
    parser.add_argument("--expect-disabled", action="store_true")
    parser.add_argument("--expect-delivered", action="store_true")
    parser.add_argument("--expect-rollback", action="store_true")
    args = parser.parse_args()

    result = build_owner_only_first_real_delivery(
        root=args.root,
        course_id=args.course_id,
        skill_id=args.skill_id,
        readiness_course_id=args.readiness_course_id,
        readiness_skill_id=args.readiness_skill_id,
        limit=args.limit,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_disabled:
        if result["status"] != "disabled":
            return 2
        if result["delivery_performed"] is not False:
            return 3
        if result["effective_source"] != "legacy_fallback":
            return 4

    if args.expect_rollback:
        if result["status"] != "rolled_back_to_legacy_fallback":
            return 5
        if result["delivery_performed"] is not False:
            return 6
        if result["effective_source"] != "legacy_fallback":
            return 7

    if args.expect_delivered:
        if result["status"] != "owner_only_first_real_delivery_performed":
            return 8
        if result["delivery_performed"] is not True:
            return 9
        if result["effective_source"] != "local_bank":
            return 10
        if not (1 <= int(result["delivered_question_count"]) <= MAX_OWNER_ONLY_REAL_DELIVERY_QUESTIONS):
            return 11
        if result["implementation_scope"]["adds_public_ui"] is not False:
            return 12
        if result["implementation_scope"]["patches_web_app"] is not False:
            return 13
        if result["no_persistence_policy"]["persist_attempts"] is not False:
            return 14
        if not _assert_no_forbidden_delivery_fields(result):
            return 15

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
