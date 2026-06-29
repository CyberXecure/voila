#!/usr/bin/env python
"""Build a temporary local-bank smoke fixture from a real Voila course.

This helper is used only by the v0.5.1 owner-only real-course delivery smoke.
It reads committed/local course artifacts, writes a temporary exercise bank under
.tmp, and prints a JSON summary for the PowerShell smoke script.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


TARGET_NAMES = {
    "course.cleaned.md",
    "course.md",
    "course_outline.json",
    "quiz.json",
    "flashcards.json",
    "pages.json",
    "glossary.json",
}

EXCLUDED = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".tmp",
    ".release-cache",
    "node_modules",
}


def configure_stdout_utf8() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def excluded(path: Path) -> bool:
    return bool(set(path.parts) & EXCLUDED)


def slugify(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return text[:80] or "real-course"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def as_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def collect_question_like(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []

    if isinstance(value, dict):
        keys = set(value.keys())
        has_prompt = bool(keys & {"question", "prompt", "text", "title"})
        has_answer_or_options = bool(keys & {"answer", "correct_answer", "expected_answer", "choices", "options"})
        if has_prompt and has_answer_or_options:
            found.append(value)

        for nested in value.values():
            found.extend(collect_question_like(nested))

    elif isinstance(value, list):
        for item in value:
            found.extend(collect_question_like(item))

    return found


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+", text)
    clean: list[str] = []
    for part in parts:
        part = part.strip()
        if 80 <= len(part) <= 420:
            clean.append(part)
    return clean


def normalize_exercise(raw: dict[str, Any], index: int, skill_id: str) -> dict[str, Any]:
    question = as_text(
        raw.get("question")
        or raw.get("prompt")
        or raw.get("text")
        or raw.get("title"),
        f"Întrebarea real-course {index}?",
    )

    choices = raw.get("choices")
    if choices is None:
        choices = raw.get("options")
    normalized_choices = [as_text(item) for item in as_list(choices)]
    normalized_choices = [item for item in normalized_choices if item]

    correct_answer = as_text(
        raw.get("correct_answer")
        or raw.get("answer")
        or raw.get("expected_answer")
        or (normalized_choices[0] if normalized_choices else "Răspuns derivat din cursul real."),
        "Răspuns derivat din cursul real.",
    )

    return {
        "id": f"real_course_q{index}",
        "skill_id": skill_id,
        "type": "multiple_choice" if len(normalized_choices) >= 2 else "short_answer",
        "difficulty": as_text(raw.get("difficulty"), "medium"),
        "question": question[:500],
        "choices": normalized_choices[:5],
        "correct_answer": correct_answer[:500],
        "explanation": as_text(raw.get("explanation"), "Explicație ascunsă derivată din cursul real.")[:500],
        "source_excerpt": as_text(raw.get("source_excerpt") or raw.get("context") or question, question)[:500],
    }


def find_real_course_artifact_groups(root: Path) -> list[dict[str, Any]]:
    groups: dict[str, set[str]] = {}

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if excluded(rel):
            continue
        if path.name not in TARGET_NAMES:
            continue
        groups.setdefault(str(rel.parent), set()).add(path.name)

    summaries: list[dict[str, Any]] = []
    for parent, files in groups.items():
        file_set = set(files)
        normalized_parent = parent.replace("/", "\\")
        score = 0
        if normalized_parent.startswith("data\\output"):
            score += 20
        if "course.cleaned.md" in file_set:
            score += 5
        if "course.md" in file_set:
            score += 4
        if "course_outline.json" in file_set:
            score += 3
        if "quiz.json" in file_set:
            score += 3
        if "pages.json" in file_set:
            score += 2

        summaries.append({
            "path": parent,
            "score": score,
            "files": sorted(file_set),
        })

    summaries.sort(key=lambda item: item["score"], reverse=True)
    return summaries


def build_exercises_from_real_course(source_dir: Path, skill_id: str) -> list[dict[str, Any]]:
    raw_questions: list[dict[str, Any]] = []

    quiz_path = source_dir / "quiz.json"
    quiz_payload = load_json(quiz_path)
    if quiz_payload is not None:
        raw_questions.extend(collect_question_like(quiz_payload))

    exercises: list[dict[str, Any]] = []
    seen_questions: set[str] = set()

    for raw in raw_questions:
        question_marker = as_text(raw.get("question") or raw.get("prompt") or raw.get("text")).lower()
        if not question_marker or question_marker in seen_questions:
            continue
        seen_questions.add(question_marker)
        exercises.append(normalize_exercise(raw, len(exercises) + 1, skill_id))
        if len(exercises) >= 7:
            break

    if len(exercises) < 5:
        course_text = ""
        for name in ["course.cleaned.md", "course.md"]:
            candidate = source_dir / name
            if candidate.exists():
                course_text = candidate.read_text(encoding="utf-8", errors="replace")
                break

        for sentence in split_sentences(course_text):
            if len(exercises) >= 7:
                break
            exercises.append({
                "id": f"real_course_sentence_q{len(exercises) + 1}",
                "skill_id": skill_id,
                "type": "short_answer",
                "difficulty": "medium",
                "question": f"Ce idee importantă reiese din fragmentul: {sentence[:220]}",
                "choices": [],
                "correct_answer": sentence[:500],
                "explanation": "Răspuns ascuns derivat din cursul real.",
                "source_excerpt": sentence[:500],
            })

    return exercises


def build_temporary_bank(root: Path, smoke_root: Path) -> dict[str, Any]:
    groups = find_real_course_artifact_groups(root)
    if not groups:
        raise SystemExit("No real course artifacts found.")

    selected = groups[0]
    source_dir = root / selected["path"]
    course_id = slugify(source_dir.name)
    skill_id = "real_course_smoke_001"

    exercises = build_exercises_from_real_course(source_dir, skill_id=skill_id)

    if len(exercises) < 5:
        raise SystemExit(f"Not enough real-course material to build smoke bank: {len(exercises)} exercises")

    smoke_course_root = smoke_root / "course"
    smoke_course_root.mkdir(parents=True, exist_ok=True)

    bank = {
        "schema_version": "1",
        "engine": "local_pedagogy_engine",
        "course_id": course_id,
        "exercise_count": len(exercises),
        "generated_by": "v0.5.1 owner-only real-course local-bank delivery smoke",
        "legacy_fallback": "Legacy fallback remains available for rollback.",
        "source_real_course_path": str(source_dir.relative_to(root)),
        "exercises": exercises,
    }

    bank_path = smoke_course_root / "exercise_bank.local.json"
    bank_path.write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "selected_real_course_path": str(source_dir.relative_to(root)),
        "temporary_bank_path": str(bank_path.relative_to(root)),
        "course_id": course_id,
        "skill_id": skill_id,
        "exercise_count": len(exercises),
        "selected_files": selected["files"],
    }


def main() -> int:
    configure_stdout_utf8()

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--smoke-root",
        default=".tmp/v051-owner-only-real-course-local-bank-delivery-smoke",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    smoke_root = Path(args.smoke_root)
    if not smoke_root.is_absolute():
        smoke_root = (root / smoke_root).resolve()

    summary = build_temporary_bank(root, smoke_root)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
