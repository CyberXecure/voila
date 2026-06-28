"""Guarded first live-trial question envelope sanitizer.

v0.4.80 defines a JSON-only local sanitizer for the future first live-trial
question envelope. It strips answer/explanation/raw fields from candidate
questions and returns a safe display envelope.

This is not live consumption. It adds no web route, does not patch web_app.py,
does not deliver local-bank questions live, does not persist attempts, does not
update progress, and does not score live answers.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_first_live_trial_contract import (
    FIRST_LIVE_TRIAL_CONTRACT_FLAG_NAME,
    FIRST_LIVE_TRIAL_CONTRACT_VERSION,
    OWNER_REVIEW_FLAGS,
    build_first_live_trial_contract,
)


QUESTION_ENVELOPE_SANITIZER_VERSION = "v0.4.80"
QUESTION_ENVELOPE_SANITIZER_FLAG_NAME = (
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_QUESTION_ENVELOPE_SANITIZER"
)

REQUIRED_OWNER_FLAGS = list(dict.fromkeys(OWNER_REVIEW_FLAGS + [QUESTION_ENVELOPE_SANITIZER_FLAG_NAME]))

FORBIDDEN_PRE_LIVE_FIELD_NAMES = [
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
]

SAFE_ENVELOPE_FIELD_NAMES = [
    "envelope_schema_version",
    "envelope_version",
    "question_id",
    "skill_id",
    "question_type",
    "difficulty",
    "source",
    "display_index",
    "prompt",
    "choices",
    "metadata_only",
    "answer_hidden_until_submission",
    "explanation_hidden_until_submission",
    "will_deliver_live",
    "will_save_attempt",
    "will_update_progress",
    "will_score_answer",
]


def _flag_enabled(name: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return str(source.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def _coerce_text(value: Any, *, max_length: int = 2000) -> str:
    if value is None:
        return ""
    text = str(value)
    if len(text) > max_length:
        return text[: max_length - 1] + "…"
    return text


def _coerce_choice_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value[:8]:
        text = _coerce_text(item, max_length=500).strip()
        if text:
            result.append(text)
    return result


def sanitize_first_live_trial_question_envelope(
    candidate: dict[str, Any],
    *,
    display_index: int = 1,
) -> dict[str, Any]:
    """Return a safe metadata/display envelope for a future live-trial question."""

    prompt = candidate.get("question")
    if prompt is None:
        prompt = candidate.get("prompt")

    envelope = {
        "envelope_schema_version": "1",
        "envelope_version": QUESTION_ENVELOPE_SANITIZER_VERSION,
        "question_id": _coerce_text(candidate.get("question_id") or candidate.get("id"), max_length=240),
        "skill_id": _coerce_text(candidate.get("skill_id"), max_length=240),
        "question_type": _coerce_text(candidate.get("question_type"), max_length=120),
        "difficulty": _coerce_text(candidate.get("difficulty"), max_length=120),
        "source": _coerce_text(candidate.get("source"), max_length=160),
        "display_index": int(display_index),
        "prompt": _coerce_text(prompt, max_length=2000),
        "choices": _coerce_choice_list(candidate.get("choices")),
        "metadata_only": True,
        "answer_hidden_until_submission": True,
        "explanation_hidden_until_submission": True,
        "will_deliver_live": False,
        "will_save_attempt": False,
        "will_update_progress": False,
        "will_score_answer": False,
    }

    return envelope


def _build_unsafe_sample_candidate() -> dict[str, Any]:
    return {
        "question_id": "local_bank::v080-sample::local_ex_0001",
        "skill_id": "local_concept_001_functiile",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "source": "local_exercise_bank_adapter",
        "question": "Care este rolul principal al funcției într-un context tehnic?",
        "choices": [
            "Să descrie o relație între intrări și rezultate.",
            "Să ascundă toate datele sursă.",
            "Să înlocuiască progresul cursantului.",
            "Să pornească o sesiune live.",
        ],
        "correct_answer": "Să descrie o relație între intrări și rezultate.",
        "correct_answer_preview": "prima opțiune",
        "answer": "A",
        "expected_answer": "A",
        "solution": "A",
        "explanation": "Funcția descrie relația dintre intrări și rezultate.",
        "explanation_preview": "relație intrare-ieșire",
        "source_excerpt": "unsafe source excerpt intentionally removed",
        "raw_snapshots": [{"unsafe": True}],
        "raw_contract": {"unsafe": True},
        "dry_run_items": [{"unsafe": True}],
        "selected_questions": [{"unsafe": True}],
    }


def build_first_live_trial_question_envelope_sanitizer_report(
    *,
    course_id: str = "v080-envelope",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_env = env if env is not None else dict(os.environ)
    flag_states = {name: _flag_enabled(name, source_env) for name in REQUIRED_OWNER_FLAGS}
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]
    sanitizer_flag_enabled = flag_states.get(QUESTION_ENVELOPE_SANITIZER_FLAG_NAME, False)

    contract = build_first_live_trial_contract(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        env=source_env,
    )
    contract_ready = contract.get("contract_status") == "contract_skeleton_ready_for_owner_review"

    unsafe_candidate = _build_unsafe_sample_candidate()
    sanitized_envelope = sanitize_first_live_trial_question_envelope(unsafe_candidate, display_index=1)
    stripped_field_names = [name for name in FORBIDDEN_PRE_LIVE_FIELD_NAMES if name in unsafe_candidate]
    leaked_field_names = [name for name in FORBIDDEN_PRE_LIVE_FIELD_NAMES if name in sanitized_envelope]

    if not sanitizer_flag_enabled:
        status = "disabled"
        blocking_reasons = ["question_envelope_sanitizer_flag_disabled"]
        envelope_available = False
    elif missing_flags:
        status = "blocked"
        blocking_reasons = ["required_owner_review_flags_missing"]
        envelope_available = False
    elif not contract_ready:
        status = "blocked"
        blocking_reasons = ["first_live_trial_contract_not_ready"]
        envelope_available = False
    elif leaked_field_names:
        status = "blocked"
        blocking_reasons = ["sanitized_envelope_contains_forbidden_fields"]
        envelope_available = False
    else:
        status = "question_envelope_sanitizer_ready_for_owner_review"
        blocking_reasons = []
        envelope_available = True

    return {
        "schema_version": "1",
        "question_envelope_sanitizer_version": QUESTION_ENVELOPE_SANITIZER_VERSION,
        "mode": "guarded_first_live_trial_question_envelope_sanitizer",
        "course_id": course_id,
        "skill_id": skill_id,
        "sanitizer_flag_name": QUESTION_ENVELOPE_SANITIZER_FLAG_NAME,
        "sanitizer_flag_enabled": sanitizer_flag_enabled,
        "status": status,
        "blocking_reasons": blocking_reasons,
        "required_owner_flags": REQUIRED_OWNER_FLAGS,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "depends_on_contract_version": FIRST_LIVE_TRIAL_CONTRACT_VERSION,
        "contract_flag_name": FIRST_LIVE_TRIAL_CONTRACT_FLAG_NAME,
        "contract_status": contract.get("contract_status"),
        "contract_ready": contract_ready,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "envelope_available_for_owner_review": envelope_available,
        "safe_envelope_field_names": SAFE_ENVELOPE_FIELD_NAMES,
        "forbidden_pre_live_field_names": FORBIDDEN_PRE_LIVE_FIELD_NAMES,
        "stripped_field_names": stripped_field_names,
        "leaked_field_names": leaked_field_names,
        "sanitized_envelope": sanitized_envelope if envelope_available else {},
        "sanitization_status": {
            "unsafe_sample_used_for_check_only": True,
            "forbidden_fields_stripped": len(stripped_field_names) >= 8,
            "leaked_forbidden_field_count": len(leaked_field_names),
            "answers_exposed_before_submission": False,
            "explanations_exposed_before_submission": False,
            "raw_snapshots_exposed": False,
            "source_excerpts_exposed": False,
            "raw_contract_exposed": False,
            "dry_run_items_exposed": False,
            "selected_questions_exposed": False,
            "metadata_only": True,
        },
        "implementation_scope": {
            "json_only_local_module": True,
            "adds_web_route": False,
            "patches_web_app": False,
            "adds_public_ui": False,
            "starts_live_session": False,
            "replaces_live_study_session": False,
            "delivers_local_bank_questions_live": False,
            "persists_attempts": False,
            "updates_progress": False,
            "scores_live_session": False,
            "requires_cloud_or_api": False,
        },
        "explicit_not_live_yet": [
            "question envelope sanitizer does not change effective_source",
            "sanitized envelopes are not delivered live",
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
    parser = argparse.ArgumentParser(description="Build guarded first live trial question envelope sanitizer report.")
    parser.add_argument("--course-id", default="v080-envelope")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--expect-ready", action="store_true")
    parser.add_argument("--expect-disabled", action="store_true")
    args = parser.parse_args()

    result = build_first_live_trial_question_envelope_sanitizer_report(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_ready and result["status"] != "question_envelope_sanitizer_ready_for_owner_review":
        return 2
    if args.expect_disabled and result["status"] != "disabled":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
