"""Read-only study preview for Exam Prep local bank questions.

v0.4.49 previews normalized local-bank questions for a skill without changing
live study sessions, saving attempts, scoring answers, or updating progress.

This is a safe bridge toward future controlled local-bank consumption.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from exam_prep_local_bank_adapter import ADAPTER_SOURCE, build_local_bank_adapter_preview


STUDY_PREVIEW_VERSION = "v0.4.49"


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _question_preview(question: dict[str, Any]) -> dict[str, Any]:
    return {
        "question_id": _text(question.get("question_id")),
        "source_exercise_id": _text(question.get("source_exercise_id")),
        "course_id": _text(question.get("course_id")),
        "skill_id": _text(question.get("skill_id")),
        "question_type": _text(question.get("question_type")),
        "difficulty": _text(question.get("difficulty")),
        "question": _text(question.get("question")),
        "choices": list(question.get("choices", [])) if isinstance(question.get("choices"), list) else [],
        "correct_answer": _text(question.get("correct_answer")),
        "explanation": _text(question.get("explanation")),
        "source_excerpt": _text(question.get("source_excerpt")),
        "source": _text(question.get("source")),
        "ready_for_read_only_study_preview": True,
        "will_save_attempt": False,
        "will_update_progress": False,
        "will_score_answer": False,
    }


def _skill_counts(questions: list[dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for question in questions:
        counter[_text(question.get("skill_id")) or "(missing)"] += 1
    return dict(sorted(counter.items()))


def _select_skill_id(questions: list[dict[str, Any]], requested_skill_id: str | None) -> str:
    if requested_skill_id:
        return requested_skill_id

    counts = _skill_counts(questions)
    for skill_id in counts:
        if skill_id != "(missing)":
            return skill_id

    return ""


def build_local_bank_read_only_study_preview(
    root: str | Path,
    *,
    course_id: str | None = None,
    skill_id: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Build read-only study preview for local-bank questions."""

    adapter_preview = build_local_bank_adapter_preview(root, course_id=course_id)
    all_questions = [
        item
        for item in adapter_preview.get("questions", [])
        if isinstance(item, dict)
    ]

    selected_skill_id = _select_skill_id(all_questions, skill_id)
    skill_questions = [
        item
        for item in all_questions
        if _text(item.get("skill_id")) == selected_skill_id
    ]

    if limit is not None:
        skill_questions = skill_questions[:limit]

    active_source = _text(adapter_preview.get("active_source_adapter"))
    local_available = active_source == ADAPTER_SOURCE and bool(skill_questions)

    if not local_available:
        active_source = "legacy_fallback"

    return {
        "schema_version": "1",
        "study_preview_version": STUDY_PREVIEW_VERSION,
        "mode": "read_only_study_preview",
        "root": str(Path(root)),
        "course_id_filter": course_id or "",
        "requested_skill_id": skill_id or "",
        "selected_skill_id": selected_skill_id if local_available else "",
        "active_source": active_source,
        "local_bank_available": active_source == ADAPTER_SOURCE,
        "available_skill_counts": _skill_counts(all_questions),
        "preview_question_count": len(skill_questions) if local_available else 0,
        "questions": [_question_preview(item) for item in skill_questions] if local_available else [],
        "legacy_fallback_available": True,
        "legacy_fallback_policy": "Keep using legacy quiz/question data for live study sessions until a future milestone explicitly enables local bank consumption.",
        "will_save_attempt": False,
        "will_update_progress": False,
        "will_score_answer": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a read-only study preview from local bank questions.")
    parser.add_argument("--root", required=True, help="Root directory to search.")
    parser.add_argument("--course-id", default="", help="Optional course_id filter.")
    parser.add_argument("--skill-id", default="", help="Optional skill_id filter.")
    parser.add_argument("--limit", type=int, default=0, help="Optional maximum number of preview questions.")
    parser.add_argument("--strict-local", action="store_true", help="Exit non-zero when no local preview questions are available.")
    args = parser.parse_args()

    preview = build_local_bank_read_only_study_preview(
        args.root,
        course_id=args.course_id or None,
        skill_id=args.skill_id or None,
        limit=args.limit or None,
    )

    print(json.dumps(preview, ensure_ascii=True, indent=2))

    if args.strict_local and preview["active_source"] != ADAPTER_SOURCE:
        return 2
    if args.strict_local and preview["preview_question_count"] <= 0:
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

