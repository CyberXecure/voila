
from __future__ import annotations

from pathlib import Path
from collections import OrderedDict


def _safe_str(value) -> str:
    return str(value or "").strip()


def _source_of(question: dict) -> dict:
    source = question.get("source") or {}
    return source if isinstance(source, dict) else {}


def _lesson_id(question: dict) -> str:
    source = _source_of(question)

    return (
        _safe_str(question.get("lesson_id"))
        or _safe_str(source.get("lesson_id"))
        or _safe_str(question.get("concept_id"))
        or _safe_str(source.get("concept_id"))
        or "lesson"
    )


def _lesson_title(question: dict) -> str:
    source = _source_of(question)

    return (
        _safe_str(source.get("concept_title"))
        or _safe_str(source.get("lesson_title"))
        or _safe_str(source.get("title"))
        or _safe_str(question.get("concept_title"))
        or _safe_str(question.get("lesson_title"))
        or _lesson_id(question)
    )


def _pages(question: dict) -> list[int]:
    source = _source_of(question)

    raw_pages = (
        source.get("source_pdf_pages")
        or source.get("pages")
        or question.get("source_pdf_pages")
        or question.get("pages")
        or []
    )

    result = []

    if isinstance(raw_pages, (str, int)):
        raw_pages = [raw_pages]

    for item in raw_pages:
        try:
            result.append(int(item))
        except Exception:
            pass

    return sorted(set(result))


def _source_text(question: dict) -> str:
    source = _source_of(question)

    return (
        _safe_str(source.get("source_text"))
        or _safe_str(source.get("text"))
        or _safe_str(question.get("source_text"))
        or _safe_str(question.get("answer"))
        or ""
    )


def load_study_questions(output_dir: Path | str) -> list[dict]:
    output_dir = Path(output_dir)

    try:
        from study_engine import load_questions
        return load_questions(output_dir)
    except Exception:
        return []


def build_lessons(output_dir: Path | str) -> list[dict]:
    output_dir = Path(output_dir)
    questions = load_study_questions(output_dir)

    grouped: OrderedDict[str, dict] = OrderedDict()

    for question in questions:
        if not isinstance(question, dict):
            continue

        lesson_id = _lesson_id(question)
        title = _lesson_title(question)

        if lesson_id not in grouped:
            grouped[lesson_id] = {
                "lesson_id": lesson_id,
                "title": title,
                "questions": [],
                "pages": set(),
                "source_texts": [],
            }

        item = grouped[lesson_id]
        item["questions"].append(question)
        item["pages"].update(_pages(question))

        source_text = _source_text(question)

        if source_text and source_text not in item["source_texts"]:
            item["source_texts"].append(source_text)

    lessons = []

    for item in grouped.values():
        source_text = "\n\n".join(item["source_texts"]).strip()

        lessons.append(
            {
                "lesson_id": item["lesson_id"],
                "title": item["title"],
                "questions_count": len(item["questions"]),
                "pages": sorted(item["pages"]),
                "source_text": source_text,
                "preview": source_text[:420].replace("\n", " ").strip(),
            }
        )

    return lessons


def get_lesson(output_dir: Path | str, lesson_id: str) -> dict | None:
    lesson_id = _safe_str(lesson_id)

    for lesson in build_lessons(output_dir):
        if lesson["lesson_id"] == lesson_id:
            return lesson

    return None


def questions_for_lesson(output_dir: Path | str, lesson_id: str) -> list[dict]:
    lesson_id = _safe_str(lesson_id)

    return [
        question
        for question in load_study_questions(output_dir)
        if _lesson_id(question) == lesson_id
    ]
