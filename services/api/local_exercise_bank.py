"""Local exercise bank discovery for Voila.

This module is a non-destructive bridge between the v0.4.44 local pedagogy
engine scaffold and future Exam Prep integration.

It discovers and validates exercise_bank.local.json files, but it does not
replace the legacy quiz/question path. Callers can use the result to decide
whether to use local exercises or fall back to legacy data.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DISCOVERY_VERSION = "v0.4.45"
LOCAL_EXERCISE_BANK_FILENAME = "exercise_bank.local.json"


@dataclass(frozen=True)
class ExerciseBankValidation:
    """Validation result for a local exercise bank."""

    valid: bool
    errors: list[str]
    warnings: list[str]
    exercise_count: int


@dataclass(frozen=True)
class ExerciseBankCandidate:
    """Discovered local exercise bank candidate."""

    path: Path
    course_id: str
    exercise_count: int
    validation: ExerciseBankValidation


def load_json(path: str | Path) -> dict[str, Any]:
    """Load a UTF-8 JSON object."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def _as_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_exercise_bank(payload: dict[str, Any]) -> ExerciseBankValidation:
    """Validate the minimum local exercise bank contract.

    Required top-level fields are intentionally minimal so legacy fallback can
    remain available during early integration.
    """

    errors: list[str] = []
    warnings: list[str] = []

    if payload.get("schema_version") != "1":
        errors.append("schema_version must be '1'")

    if payload.get("engine") != "local_pedagogy_engine":
        errors.append("engine must be local_pedagogy_engine")

    course_id = payload.get("course_id")
    if not _as_non_empty_string(course_id):
        errors.append("course_id must be a non-empty string")

    exercises = payload.get("exercises")
    if not isinstance(exercises, list):
        errors.append("exercises must be a list")
        exercises = []

    declared_count = payload.get("exercise_count")
    if declared_count is not None and declared_count != len(exercises):
        warnings.append("exercise_count does not match exercises length")

    legacy_fallback = payload.get("legacy_fallback", "")
    if not _as_non_empty_string(legacy_fallback) or "legacy" not in legacy_fallback.lower():
        warnings.append("legacy_fallback should mention legacy fallback behavior")

    required_exercise_keys = ("id", "skill_id", "type", "question", "correct_answer")
    seen_ids: set[str] = set()

    for index, exercise in enumerate(exercises):
        if not isinstance(exercise, dict):
            errors.append(f"exercise[{index}] must be an object")
            continue

        for key in required_exercise_keys:
            if not _as_non_empty_string(exercise.get(key)):
                errors.append(f"exercise[{index}].{key} must be a non-empty string")

        exercise_id = str(exercise.get("id", "")).strip()
        if exercise_id:
            if exercise_id in seen_ids:
                errors.append(f"duplicate exercise id: {exercise_id}")
            seen_ids.add(exercise_id)

    if not exercises:
        warnings.append("exercise bank is empty; caller should use legacy fallback")

    return ExerciseBankValidation(
        valid=not errors,
        errors=errors,
        warnings=warnings,
        exercise_count=len(exercises),
    )


def discover_exercise_bank_files(root: str | Path) -> list[Path]:
    """Discover local exercise bank files under a root directory."""

    root_path = Path(root)
    if not root_path.exists():
        return []

    if root_path.is_file():
        if root_path.name == LOCAL_EXERCISE_BANK_FILENAME:
            return [root_path]
        return []

    return sorted(root_path.rglob(LOCAL_EXERCISE_BANK_FILENAME))


def discover_local_exercise_banks(
    root: str | Path,
    *,
    course_id: str | None = None,
) -> list[ExerciseBankCandidate]:
    """Discover and validate local exercise bank candidates."""

    candidates: list[ExerciseBankCandidate] = []

    for path in discover_exercise_bank_files(root):
        try:
            payload = load_json(path)
            validation = validate_exercise_bank(payload)
            payload_course_id = str(payload.get("course_id", "")).strip()
        except Exception as exc:  # pragma: no cover - defensive CLI path
            validation = ExerciseBankValidation(
                valid=False,
                errors=[str(exc)],
                warnings=[],
                exercise_count=0,
            )
            payload_course_id = ""

        if course_id and payload_course_id != course_id:
            continue

        candidates.append(
            ExerciseBankCandidate(
                path=path,
                course_id=payload_course_id,
                exercise_count=validation.exercise_count,
                validation=validation,
            )
        )

    return candidates


def choose_best_exercise_bank(
    root: str | Path,
    *,
    course_id: str | None = None,
) -> ExerciseBankCandidate | None:
    """Choose the first valid non-empty local exercise bank candidate."""

    candidates = discover_local_exercise_banks(root, course_id=course_id)
    valid_candidates = [
        candidate
        for candidate in candidates
        if candidate.validation.valid and candidate.exercise_count > 0
    ]

    if not valid_candidates:
        return None

    return sorted(valid_candidates, key=lambda item: (item.course_id, str(item.path)))[0]


def candidate_to_dict(candidate: ExerciseBankCandidate) -> dict[str, Any]:
    """Serialize a candidate for diagnostics."""

    return {
        "path": str(candidate.path),
        "course_id": candidate.course_id,
        "exercise_count": candidate.exercise_count,
        "valid": candidate.validation.valid,
        "errors": candidate.validation.errors,
        "warnings": candidate.validation.warnings,
    }


def discovery_summary(root: str | Path, *, course_id: str | None = None) -> dict[str, Any]:
    """Return a JSON-serializable discovery summary."""

    candidates = discover_local_exercise_banks(root, course_id=course_id)
    selected = choose_best_exercise_bank(root, course_id=course_id)

    return {
        "status": "ok",
        "discovery_version": DISCOVERY_VERSION,
        "root": str(Path(root)),
        "course_id_filter": course_id or "",
        "banks_found": len(candidates),
        "valid_banks": sum(1 for item in candidates if item.validation.valid),
        "selected_bank": str(selected.path) if selected else "",
        "selected_exercise_count": selected.exercise_count if selected else 0,
        "fallback_policy": "Use legacy quiz/question data when no valid local exercise_bank.local.json is available.",
        "candidates": [candidate_to_dict(item) for item in candidates],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover and validate local exercise_bank.local.json files.")
    parser.add_argument("--root", required=True, help="Root directory to search.")
    parser.add_argument("--course-id", default="", help="Optional course_id filter.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when no valid local bank is found.")
    args = parser.parse_args()

    summary = discovery_summary(args.root, course_id=args.course_id or None)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.strict and not summary["selected_bank"]:
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

