"""Read-only local exercise bank source adapter for Exam Prep.

This module converts validated local exercise_bank.local.json records into a
stable Exam Prep-compatible question shape.

v0.4.47 is adapter-only: it does not change live Exam Prep routes, scoring,
progress thresholds, weak review behavior, or UI. It preserves legacy fallback
and simply provides normalized records future milestones can consume.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from local_exercise_bank import choose_best_exercise_bank, load_json


ADAPTER_VERSION = "v0.4.47"
ADAPTER_SOURCE = "local_exercise_bank_adapter"
def configure_stdout_utf8() -> None:
    """Make CLI JSON output safe on Windows consoles using cp1252."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def _as_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _normalize_choices(value: Any) -> list[str]:
    choices: list[str] = []
    for item in _as_list(value):
        text = _as_text(item)
        if text:
            choices.append(text)

    seen: set[str] = set()
    unique: list[str] = []
    for choice in choices:
        marker = choice.lower()
        if marker in seen:
            continue
        seen.add(marker)
        unique.append(choice)

    return unique


def normalize_local_exercise(
    exercise: dict[str, Any],
    *,
    course_id: str,
    source_bank_path: str,
    index: int,
) -> dict[str, Any]:
    """Normalize one local exercise into an Exam Prep-compatible record."""

    source_exercise_id = _as_text(exercise.get("id"), f"local_ex_{index:04d}")
    skill_id = _as_text(exercise.get("skill_id"), "local_general_review")
    question_type = _as_text(exercise.get("type"), "short_answer")
    difficulty = _as_text(exercise.get("difficulty"), "medium")
    question = _as_text(exercise.get("question"), "Revizuiește fragmentul sursă.")
    correct_answer = _as_text(exercise.get("correct_answer"), _as_text(exercise.get("answer"), ""))
    explanation = _as_text(exercise.get("explanation"), "Exercițiu local normalizat pentru Exam Prep.")
    source_excerpt = _as_text(exercise.get("source_excerpt"), "")

    normalized_id = f"local_bank::{course_id}::{source_exercise_id}"

    return {
        "schema_version": "1",
        "adapter_version": ADAPTER_VERSION,
        "question_id": normalized_id,
        "source_exercise_id": source_exercise_id,
        "course_id": course_id,
        "skill_id": skill_id,
        "question_type": question_type,
        "difficulty": difficulty,
        "question": question,
        "choices": _normalize_choices(exercise.get("choices")),
        "correct_answer": correct_answer,
        "explanation": explanation,
        "source_excerpt": source_excerpt,
        "source": ADAPTER_SOURCE,
        "source_bank_path": source_bank_path,
        "ready_for_exam_prep_preview": True,
        "will_modify_progress": False,
        "will_replace_legacy_generator": False,
    }


def normalize_local_exercise_bank(
    bank_payload: dict[str, Any],
    *,
    source_bank_path: str,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Normalize a local exercise bank payload."""

    course_id = _as_text(bank_payload.get("course_id"), "local-course")
    exercises = bank_payload.get("exercises", [])
    if not isinstance(exercises, list):
        return []

    normalized: list[dict[str, Any]] = []
    for index, exercise in enumerate(exercises, start=1):
        if not isinstance(exercise, dict):
            continue
        normalized.append(
            normalize_local_exercise(
                exercise,
                course_id=course_id,
                source_bank_path=source_bank_path,
                index=index,
            )
        )
        if limit is not None and len(normalized) >= limit:
            break

    return normalized


def build_local_bank_adapter_preview(
    root: str | Path,
    *,
    course_id: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Build a read-only adapter preview from the best local exercise bank."""

    selected = choose_best_exercise_bank(root, course_id=course_id)

    if selected is None:
        return {
            "schema_version": "1",
            "adapter_version": ADAPTER_VERSION,
            "mode": "read_only_adapter_preview",
            "active_source_adapter": "legacy_fallback",
            "course_id_filter": course_id or "",
            "source_bank_path": "",
            "question_count": 0,
            "questions": [],
            "legacy_fallback_available": True,
            "legacy_fallback_policy": "Use legacy quiz/question data when no valid local exercise_bank.local.json is available.",
            "will_modify_progress": False,
            "will_modify_exam_prep_ui": False,
            "will_replace_legacy_generator": False,
            "requires_cloud_or_api": False,
        }

    bank_payload = load_json(selected.path)
    normalized = normalize_local_exercise_bank(
        bank_payload,
        source_bank_path=str(selected.path),
        limit=limit,
    )

    return {
        "schema_version": "1",
        "adapter_version": ADAPTER_VERSION,
        "mode": "read_only_adapter_preview",
        "active_source_adapter": ADAPTER_SOURCE,
        "course_id_filter": course_id or "",
        "source_bank_path": str(selected.path),
        "question_count": len(normalized),
        "questions": normalized,
        "legacy_fallback_available": True,
        "legacy_fallback_policy": "Keep legacy quiz/question data available until a future milestone explicitly enables local bank consumption.",
        "will_modify_progress": False,
        "will_modify_exam_prep_ui": False,
        "will_replace_legacy_generator": False,
        "requires_cloud_or_api": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize local exercise bank records for Exam Prep preview.")
    parser.add_argument("--root", required=True, help="Root directory to search.")
    parser.add_argument("--course-id", default="", help="Optional course_id filter.")
    parser.add_argument("--limit", type=int, default=0, help="Optional maximum number of normalized questions.")
    parser.add_argument("--strict-local", action="store_true", help="Exit non-zero when no local bank is adapted.")
    args = parser.parse_args()

    preview = build_local_bank_adapter_preview(
        args.root,
        course_id=args.course_id or None,
        limit=args.limit or None,
    )

    print(json.dumps(preview, ensure_ascii=True, indent=2))

    if args.strict_local and preview["active_source_adapter"] != ADAPTER_SOURCE:
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())




