from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from content_filter import should_exclude_study_item


DEFAULT_BKT = {
    "prior": 0.30,
    "learn": 0.18,
    "guess": 0.20,
    "slip": 0.10,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp_probability(value: float) -> float:
    return max(0.01, min(0.99, float(value)))


def mastery_status(value: float) -> str:
    if value < 0.40:
        return "Needs review"

    if value < 0.75:
        return "In progress"

    if value < 0.90:
        return "Almost mastered"

    return "Mastered"


def normalize_quiz(raw: Any) -> list[dict]:
    if isinstance(raw, dict):
        if isinstance(raw.get("questions"), list):
            items = raw["questions"]
        elif isinstance(raw.get("quiz"), list):
            items = raw["quiz"]
        else:
            items = []
    elif isinstance(raw, list):
        items = raw
    else:
        items = []

    questions = []

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue

        question = str(item.get("question") or item.get("prompt") or "").strip()

        if not question:
            continue

        lesson_id = str(item.get("lesson_id") or item.get("lesson") or "general").strip()

        answer = (
            item.get("answer")
            or item.get("correct_answer")
            or item.get("expected_answer")
            or item.get("explanation")
            or ""
        )

        title = str(item.get("title") or item.get("lesson_title") or "").strip()

        source_text = " ".join(
            str(item.get(key) or "")
            for key in [
                "title",
                "lesson_title",
                "text",
                "source_text",
                "text_preview",
                "context",
                "source",
            ]
        )

        if should_exclude_study_item(
            title=title,
            question=question,
            answer=answer,
            source_text=source_text,
            lesson_id=lesson_id,
        ):
            continue

        questions.append(
            {
                "question_id": str(item.get("question_id") or item.get("id") or f"Q{index:03d}"),
                "lesson_id": lesson_id,
                "concept_id": str(item.get("concept_id") or item.get("concept") or lesson_id).strip(),
                "question": question,
                "answer": str(answer).strip(),
                "source": item,
            }
        )

    return questions


def load_questions(output_dir: Path) -> list[dict]:
    study_quiz_path = output_dir / "quiz.study.json"
    default_quiz_path = output_dir / "quiz.json"

    if study_quiz_path.exists():
        quiz_path = study_quiz_path
    else:
        quiz_path = default_quiz_path

    if not quiz_path.exists():
        return []

    raw = json.loads(quiz_path.read_text(encoding="utf-8"))
    return normalize_quiz(raw)


def state_path(output_dir: Path) -> Path:
    return output_dir / "study_state.json"


def default_concept_state(concept_id: str) -> dict:
    return {
        "concept_id": concept_id,
        "mastery": DEFAULT_BKT["prior"],
        "attempts": 0,
        "correct": 0,
        "incorrect": 0,
        "last_seen": None,
        "status": mastery_status(DEFAULT_BKT["prior"]),
        "bkt": dict(DEFAULT_BKT),
    }


def load_state(output_dir: Path, questions: list[dict]) -> dict:
    path = state_path(output_dir)

    if path.exists():
        state = json.loads(path.read_text(encoding="utf-8"))
    else:
        state = {
            "version": "0.3",
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "concepts": {},
            "attempts": [],
        }

    concepts = state.setdefault("concepts", {})

    if not isinstance(concepts, dict):
        concepts = {}
        state["concepts"] = concepts

    valid_question_ids = {
        str(question.get("question_id") or "")
        for question in questions
        if question.get("question_id")
    }
    valid_concept_ids = {
        str(question.get("concept_id") or "")
        for question in questions
        if question.get("concept_id")
    }

    if valid_concept_ids:
        state["concepts"] = {
            concept_id: concept
            for concept_id, concept in concepts.items()
            if concept_id in valid_concept_ids
        }
        concepts = state["concepts"]

    for question in questions:
        concept_id = question["concept_id"]

        if concept_id not in concepts:
            concepts[concept_id] = default_concept_state(concept_id)

    attempts = state.setdefault("attempts", [])

    if valid_question_ids and valid_concept_ids:
        state["attempts"] = [
            attempt
            for attempt in attempts
            if str(attempt.get("question_id") or "") in valid_question_ids
            and str(attempt.get("concept_id") or "") in valid_concept_ids
        ]

        last_attempt = state.get("last_attempt")

        if isinstance(last_attempt, dict):
            last_question_id = str(last_attempt.get("question_id") or "")
            last_concept_id = str(last_attempt.get("concept_id") or "")

            if (
                last_question_id not in valid_question_ids
                or last_concept_id not in valid_concept_ids
            ):
                state.pop("last_attempt", None)

    state["updated_at"] = now_iso()

    return state


def save_state(output_dir: Path, state: dict) -> None:
    path = state_path(output_dir)
    path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def bkt_update(mastery: float, correct: bool, params: dict) -> float:
    prior = clamp_probability(mastery)
    learn = clamp_probability(params.get("learn", DEFAULT_BKT["learn"]))
    guess = clamp_probability(params.get("guess", DEFAULT_BKT["guess"]))
    slip = clamp_probability(params.get("slip", DEFAULT_BKT["slip"]))

    if correct:
        numerator = prior * (1.0 - slip)
        denominator = numerator + ((1.0 - prior) * guess)
    else:
        numerator = prior * slip
        denominator = numerator + ((1.0 - prior) * (1.0 - guess))

    if denominator <= 0:
        posterior = prior
    else:
        posterior = numerator / denominator

    next_mastery = posterior + ((1.0 - posterior) * learn)

    return clamp_probability(next_mastery)


def answered_question_ids(state: dict) -> set[str]:
    return {
        str(attempt.get("question_id"))
        for attempt in state.get("attempts", [])
        if attempt.get("question_id")
    }


def choose_next_question(questions: list[dict], state: dict) -> dict | None:
    if not questions:
        return None

    answered = answered_question_ids(state)

    unanswered = [
        question for question in questions
        if question["question_id"] not in answered
    ]

    pool = unanswered if unanswered else questions

    concepts = state.get("concepts", {})

    def score(question: dict) -> tuple[float, int]:
        concept = concepts.get(question["concept_id"], {})
        mastery = float(concept.get("mastery", DEFAULT_BKT["prior"]))
        attempts = int(concept.get("attempts", 0))

        return (mastery, attempts)

    return sorted(pool, key=score)[0]


def record_answer(output_dir: Path, question_id: str, correct: bool) -> dict:
    questions = load_questions(output_dir)
    state = load_state(output_dir, questions)

    question = None

    for item in questions:
        if item["question_id"] == question_id:
            question = item
            break

    if not question:
        raise ValueError(f"Question not found: {question_id}")

    concept_id = question["concept_id"]
    concept = state["concepts"].setdefault(concept_id, default_concept_state(concept_id))

    old_mastery = float(concept.get("mastery", DEFAULT_BKT["prior"]))
    params = concept.get("bkt") or dict(DEFAULT_BKT)
    new_mastery = bkt_update(old_mastery, correct, params)

    concept["mastery"] = new_mastery
    concept["attempts"] = int(concept.get("attempts", 0)) + 1
    concept["correct"] = int(concept.get("correct", 0)) + (1 if correct else 0)
    concept["incorrect"] = int(concept.get("incorrect", 0)) + (0 if correct else 1)
    concept["last_seen"] = now_iso()
    concept["status"] = mastery_status(new_mastery)
    concept["bkt"] = params

    attempt = {
        "timestamp": now_iso(),
        "question_id": question_id,
        "lesson_id": question["lesson_id"],
        "concept_id": concept_id,
        "correct": bool(correct),
        "mastery_before": old_mastery,
        "mastery_after": new_mastery,
    }

    state["attempts"].append(attempt)
    state["last_attempt"] = attempt
    state["updated_at"] = now_iso()

    save_state(output_dir, state)

    return state


def reset_study_state(output_dir: Path) -> None:
    path = state_path(output_dir)

    if path.exists():
        path.unlink()


def get_study_view(output_dir: Path) -> dict:
    questions = load_questions(output_dir)
    state = load_state(output_dir, questions)
    save_state(output_dir, state)

    concepts = []

    for concept_id, concept in state.get("concepts", {}).items():
        mastery = float(concept.get("mastery", DEFAULT_BKT["prior"]))

        concepts.append(
            {
                "concept_id": concept_id,
                "mastery": mastery,
                "mastery_percent": round(mastery * 100),
                "status": mastery_status(mastery),
                "attempts": int(concept.get("attempts", 0)),
                "correct": int(concept.get("correct", 0)),
                "incorrect": int(concept.get("incorrect", 0)),
                "last_seen": concept.get("last_seen"),
            }
        )

    concepts.sort(key=lambda item: (item["mastery"], item["concept_id"]))

    if concepts:
        overall_mastery = sum(item["mastery"] for item in concepts) / len(concepts)
    else:
        overall_mastery = 0.0

    current_question = choose_next_question(questions, state)

    return {
        "questions": questions,
        "state": state,
        "concepts": concepts,
        "current_question": current_question,
        "total_questions": len(questions),
        "answered_count": len(answered_question_ids(state)),
        "overall_mastery": overall_mastery,
        "overall_mastery_percent": round(overall_mastery * 100),
        "overall_status": mastery_status(overall_mastery) if concepts else "No quiz yet",
        "last_attempt": state.get("last_attempt"),
    }

