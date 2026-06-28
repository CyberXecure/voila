"""Guarded first live-trial dry-run session envelope.

v0.4.81 groups sanitized question envelopes into a dry-run session envelope
for owner review. This is not live delivery and not a real study session.

It adds no web route, does not patch web_app.py, does not deliver local-bank
questions live, does not persist attempts/sessions/progress, and does not score
live answers.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from exam_prep_local_bank_first_live_trial_question_envelope import (
    QUESTION_ENVELOPE_SANITIZER_FLAG_NAME,
    QUESTION_ENVELOPE_SANITIZER_VERSION,
    build_first_live_trial_question_envelope_sanitizer_report,
    sanitize_first_live_trial_question_envelope,
)


DRY_RUN_SESSION_ENVELOPE_VERSION = "v0.4.81"
DRY_RUN_SESSION_ENVELOPE_FLAG_NAME = (
    "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_DRY_RUN_SESSION_ENVELOPE"
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
    QUESTION_ENVELOPE_SANITIZER_FLAG_NAME,
    DRY_RUN_SESSION_ENVELOPE_FLAG_NAME,
]

FORBIDDEN_SESSION_FIELD_NAMES = [
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


def _flag_enabled(name: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return str(source.get(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def _unsafe_candidates(limit: int) -> list[dict[str, Any]]:
    base = [
        ("multiple_choice", "easy", "Care este rolul principal al funcției într-un context tehnic?"),
        ("short_answer", "medium", "Explică pe scurt diferența dintre o intrare și un rezultat."),
        ("evidence_based", "medium", "Alege indiciul care susține ideea de relație între intrări și rezultate."),
        ("compare_concepts", "medium", "Compară funcția cu o procedură repetabilă."),
        ("apply_concept", "medium", "Aplică ideea de funcție într-un exemplu de proces de învățare."),
    ]
    candidates: list[dict[str, Any]] = []
    for idx, (question_type, difficulty, prompt) in enumerate(base[: max(1, min(limit, len(base)))], start=1):
        candidates.append(
            {
                "question_id": f"local_bank::v081-session::local_ex_{idx:04d}",
                "skill_id": "local_concept_001_functiile",
                "question_type": question_type,
                "difficulty": difficulty,
                "source": "local_exercise_bank_adapter",
                "question": prompt,
                "choices": [
                    "Variantă de lucru sigură.",
                    "Variantă care ar porni live scoring.",
                    "Variantă care ar salva progresul.",
                    "Variantă care ar expune răspunsul.",
                ]
                if question_type == "multiple_choice"
                else [],
                "correct_answer": "unsafe correct answer intentionally stripped",
                "correct_answer_preview": "unsafe answer preview intentionally stripped",
                "answer": "unsafe answer intentionally stripped",
                "expected_answer": "unsafe expected answer intentionally stripped",
                "solution": "unsafe solution intentionally stripped",
                "explanation": "unsafe explanation intentionally stripped",
                "explanation_preview": "unsafe explanation preview intentionally stripped",
                "source_excerpt": "unsafe source excerpt intentionally stripped",
                "raw_snapshots": [{"unsafe": True}],
                "raw_contract": {"unsafe": True},
                "dry_run_items": [{"unsafe": True}],
                "selected_questions": [{"unsafe": True}],
            }
        )
    return candidates


def build_dry_run_session_envelope(
    *,
    course_id: str = "v081-session",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_env = env if env is not None else dict(os.environ)
    flag_states = {name: _flag_enabled(name, source_env) for name in REQUIRED_OWNER_FLAGS}
    missing_flags = [name for name, enabled in flag_states.items() if not enabled]
    session_flag_enabled = flag_states.get(DRY_RUN_SESSION_ENVELOPE_FLAG_NAME, False)

    sanitizer_report = build_first_live_trial_question_envelope_sanitizer_report(
        course_id=course_id,
        skill_id=skill_id,
        limit=limit,
        env=source_env,
    )
    sanitizer_ready = sanitizer_report.get("status") == "question_envelope_sanitizer_ready_for_owner_review"

    candidates = _unsafe_candidates(limit)
    question_envelopes = [
        sanitize_first_live_trial_question_envelope(candidate, display_index=index)
        for index, candidate in enumerate(candidates, start=1)
    ]

    session_json = json.dumps(question_envelopes, ensure_ascii=True, sort_keys=True)
    leaked_field_names = [name for name in FORBIDDEN_SESSION_FIELD_NAMES if f'"{name}"' in session_json]

    if not session_flag_enabled:
        status = "disabled"
        blocking_reasons = ["dry_run_session_envelope_flag_disabled"]
        session_available = False
    elif missing_flags:
        status = "blocked"
        blocking_reasons = ["required_owner_review_flags_missing"]
        session_available = False
    elif not sanitizer_ready:
        status = "blocked"
        blocking_reasons = ["question_envelope_sanitizer_not_ready"]
        session_available = False
    elif leaked_field_names:
        status = "blocked"
        blocking_reasons = ["session_envelope_contains_forbidden_fields"]
        session_available = False
    else:
        status = "dry_run_session_envelope_ready_for_owner_review"
        blocking_reasons = []
        session_available = True

    session_envelope = {
        "session_schema_version": "1",
        "session_envelope_version": DRY_RUN_SESSION_ENVELOPE_VERSION,
        "session_kind": "owner_only_dry_run_session_envelope",
        "course_id": course_id,
        "skill_id": skill_id,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "question_count": len(question_envelopes),
        "question_envelopes": question_envelopes,
        "metadata_only": True,
        "will_deliver_live": False,
        "will_start_live_session": False,
        "will_persist_session": False,
        "will_save_attempts": False,
        "will_update_progress": False,
        "will_score_answers": False,
    }

    return {
        "schema_version": "1",
        "dry_run_session_envelope_version": DRY_RUN_SESSION_ENVELOPE_VERSION,
        "mode": "guarded_first_live_trial_dry_run_session_envelope",
        "course_id": course_id,
        "skill_id": skill_id,
        "session_flag_name": DRY_RUN_SESSION_ENVELOPE_FLAG_NAME,
        "session_flag_enabled": session_flag_enabled,
        "status": status,
        "blocking_reasons": blocking_reasons,
        "required_owner_flags": REQUIRED_OWNER_FLAGS,
        "flag_states": flag_states,
        "missing_flags": missing_flags,
        "depends_on_question_envelope_sanitizer_version": QUESTION_ENVELOPE_SANITIZER_VERSION,
        "question_envelope_sanitizer_status": sanitizer_report.get("status"),
        "question_envelope_sanitizer_ready": sanitizer_ready,
        "effective_source": "legacy_fallback",
        "candidate_source": "local_exercise_bank_adapter",
        "fallback_source": "legacy_fallback",
        "session_envelope_available_for_owner_review": session_available,
        "session_envelope": session_envelope if session_available else {},
        "session_profile": {
            "question_count": len(question_envelopes),
            "question_type_counts": {
                item["question_type"]: sum(1 for q in question_envelopes if q["question_type"] == item["question_type"])
                for item in question_envelopes
            },
            "skill_counts": {
                skill_id: len(question_envelopes),
            },
            "all_questions_metadata_only": all(q.get("metadata_only") is True for q in question_envelopes),
        },
        "sanitization_status": {
            "forbidden_session_field_names": FORBIDDEN_SESSION_FIELD_NAMES,
            "leaked_forbidden_field_names": leaked_field_names,
            "leaked_forbidden_field_count": len(leaked_field_names),
            "answers_exposed_before_submission": False,
            "explanations_exposed_before_submission": False,
            "raw_snapshots_exposed": False,
            "source_excerpts_exposed": False,
            "raw_contract_exposed": False,
            "dry_run_items_exposed": False,
            "selected_questions_exposed": False,
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
            "dry-run session envelope does not change effective_source",
            "dry-run session envelope is not delivered live",
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
    parser = argparse.ArgumentParser(description="Build guarded first live trial dry-run session envelope.")
    parser.add_argument("--course-id", default="v081-session")
    parser.add_argument("--skill-id", default="local_concept_001_functiile")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--expect-ready", action="store_true")
    parser.add_argument("--expect-disabled", action="store_true")
    args = parser.parse_args()

    result = build_dry_run_session_envelope(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_ready and result["status"] != "dry_run_session_envelope_ready_for_owner_review":
        return 2
    if args.expect_disabled and result["status"] != "disabled":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
