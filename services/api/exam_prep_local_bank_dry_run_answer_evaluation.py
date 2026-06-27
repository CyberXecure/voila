"""Dry-run answer evaluation for local-bank Exam Prep questions.

v0.4.56 evaluates answers to dry-run local-bank items locally and
deterministically. It is intentionally read-only and does not persist attempts,
score live sessions, update progress, or replace the legacy generator.

Evaluation strategy:
- multiple_choice: normalized exact match against correct_answer_preview
- open-answer types: normalized exact match or keyword overlap heuristic

This is a scaffold for evaluation behavior, not live Exam Prep scoring.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import unicodedata
from typing import Any

from exam_prep_local_bank_consumption_flag import CONSUMPTION_FLAG_NAME, LOCAL_SOURCE
from exam_prep_local_bank_dry_run_source_selection import build_dry_run_source_selection


ANSWER_EVALUATION_VERSION = "v0.4.56"

OPEN_ANSWER_TYPES = {
    "short_answer",
    "evidence_based",
    "compare_concepts",
    "apply_concept",
    "formula_interpretation",
    "apply_formula",
}

TOKEN_STOPWORDS = {
    "este",
    "sunt",
    "prin",
    "care",
    "unui",
    "unei",
    "pentru",
    "trebuie",
    "raspuns",
    "răspuns",
    "bun",
    "conceptul",
    "fragment",
    "context",
    "explica",
    "explică",
    "mention",
    "menționează",
    "identifica",
    "identifică",
}


def _strip_diacritics(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_answer(value: Any) -> str:
    text = _strip_diacritics(str(value or "").lower())
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _tokens(value: Any) -> set[str]:
    normalized = normalize_answer(value)
    return {
        token
        for token in normalized.split()
        if len(token) >= 4 and token not in TOKEN_STOPWORDS
    }


def _sample_answer(item: dict[str, Any], sample_mode: str) -> str:
    correct = str(item.get("correct_answer_preview", "")).strip()
    if sample_mode == "correct":
        return correct

    if sample_mode == "partial":
        tokens = correct.split()
        if len(tokens) >= 6:
            return " ".join(tokens[:6])
        return correct

    return "nu stiu"


def evaluate_dry_run_answer(item: dict[str, Any], answer: str) -> dict[str, Any]:
    """Evaluate one dry-run answer locally."""

    question_type = str(item.get("question_type", "")).strip()
    correct_preview = str(item.get("correct_answer_preview", "")).strip()
    normalized_answer = normalize_answer(answer)
    normalized_correct = normalize_answer(correct_preview)

    exact_match = bool(normalized_correct) and normalized_answer == normalized_correct
    keyword_overlap = 0.0
    answer_tokens = _tokens(answer)
    correct_tokens = _tokens(correct_preview)

    if correct_tokens:
        keyword_overlap = len(answer_tokens & correct_tokens) / len(correct_tokens)

    if question_type == "multiple_choice":
        correct = exact_match
        verdict = "correct" if correct else "incorrect"
        score = 1.0 if correct else 0.0
        feedback = (
            "Răspuns corect prin potrivire normalizată."
            if correct
            else "Răspuns incorect pentru alegerea multiplă."
        )
    elif question_type in OPEN_ANSWER_TYPES:
        if exact_match:
            verdict = "correct"
            score = 1.0
            feedback = "Răspuns corect prin potrivire normalizată cu răspunsul de referință."
        elif keyword_overlap >= 0.55:
            verdict = "partially_correct"
            score = 0.5
            feedback = "Răspuns parțial corect: există suprapunere de idei-cheie, dar formularea este incompletă."
        else:
            verdict = "incorrect"
            score = 0.0
            feedback = "Răspuns insuficient: lipsesc ideile-cheie cerute de răspunsul de referință."
    else:
        if exact_match:
            verdict = "correct"
            score = 1.0
            feedback = "Răspuns corect prin potrivire normalizată."
        elif keyword_overlap >= 0.55:
            verdict = "partially_correct"
            score = 0.5
            feedback = "Răspuns parțial corect."
        else:
            verdict = "incorrect"
            score = 0.0
            feedback = "Răspuns incorect sau insuficient."

    return {
        "dry_run_item_id": item.get("dry_run_item_id", ""),
        "question_id": item.get("question_id", ""),
        "question_type": question_type,
        "skill_id": item.get("skill_id", ""),
        "answer": answer,
        "correct_answer_preview": correct_preview,
        "normalized_answer": normalized_answer,
        "normalized_correct_answer": normalized_correct,
        "exact_match": exact_match,
        "keyword_overlap": round(keyword_overlap, 4),
        "verdict": verdict,
        "score_preview": score,
        "feedback_preview": feedback,
        "dry_run_only": True,
        "will_persist_attempt": False,
        "will_update_progress": False,
        "will_score_live_session": False,
    }


def build_answer_evaluation_snapshot(
    *,
    course_id: str = "v056-sample",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
    sample_mode: str = "correct",
    enable_local_flag: bool = True,
) -> dict[str, Any]:
    """Build a dry-run answer evaluation snapshot."""

    old_flag = os.environ.get(CONSUMPTION_FLAG_NAME)
    try:
        if enable_local_flag:
            os.environ[CONSUMPTION_FLAG_NAME] = "1"
        else:
            os.environ.pop(CONSUMPTION_FLAG_NAME, None)

        dry_run = build_dry_run_source_selection(
            course_id=course_id,
            skill_id=skill_id,
            limit=limit,
            require_local_when_enabled=enable_local_flag,
        )
    finally:
        if old_flag is None:
            os.environ.pop(CONSUMPTION_FLAG_NAME, None)
        else:
            os.environ[CONSUMPTION_FLAG_NAME] = old_flag

    items = [
        item
        for item in dry_run.get("dry_run_items", [])
        if isinstance(item, dict)
    ]

    evaluations = [
        evaluate_dry_run_answer(item, _sample_answer(item, sample_mode))
        for item in items
    ]

    correct_count = sum(1 for item in evaluations if item["verdict"] == "correct")
    partial_count = sum(1 for item in evaluations if item["verdict"] == "partially_correct")
    incorrect_count = sum(1 for item in evaluations if item["verdict"] == "incorrect")
    evaluation_count = len(evaluations)
    average_score = (
        sum(float(item["score_preview"]) for item in evaluations) / evaluation_count
        if evaluation_count
        else 0.0
    )

    return {
        "schema_version": "1",
        "answer_evaluation_version": ANSWER_EVALUATION_VERSION,
        "mode": "dry_run_answer_evaluation",
        "sample_mode": sample_mode,
        "course_id": course_id,
        "skill_id": skill_id,
        "requested_limit": limit,
        "selected_source": dry_run.get("selected_source"),
        "evaluation_count": evaluation_count,
        "correct_count": correct_count,
        "partial_count": partial_count,
        "incorrect_count": incorrect_count,
        "average_score_preview": round(average_score, 4),
        "evaluations": evaluations,
        "path_policy": "no_user_provided_filesystem_root",
        "will_persist_attempts": False,
        "will_update_progress": False,
        "will_score_live_session": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
        "dry_run_source_selection": dry_run,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate dry-run local-bank answers locally.")
    parser.add_argument("--course-id", default="v056-sample", help="Diagnostic course id.")
    parser.add_argument("--skill-id", default="local_concept_001_functiile", help="Diagnostic skill id.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum diagnostic evaluation items.")
    parser.add_argument("--sample-mode", choices=["correct", "partial", "wrong"], default="correct")
    parser.add_argument("--disable-local-flag", action="store_true", help="Run with local source flag disabled.")
    parser.add_argument("--expect-all-correct", action="store_true", help="Exit non-zero unless all evaluations are correct.")
    parser.add_argument("--expect-all-wrong", action="store_true", help="Exit non-zero unless all evaluations are incorrect.")
    args = parser.parse_args()

    result = build_answer_evaluation_snapshot(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
        sample_mode=args.sample_mode,
        enable_local_flag=not args.disable_local_flag,
    )

    print(json.dumps(result, ensure_ascii=True, indent=2))

    if args.expect_all_correct:
        if result["selected_source"] != LOCAL_SOURCE:
            return 2
        if result["evaluation_count"] <= 0:
            return 3
        if result["correct_count"] != result["evaluation_count"]:
            return 4

    if args.expect_all_wrong:
        if result["evaluation_count"] <= 0:
            return 5
        if result["incorrect_count"] != result["evaluation_count"]:
            return 6

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

