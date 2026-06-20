from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from content_filter import should_exclude_study_item


DEFAULT_BKT = {
    "prior": 0.30,
    "learn": 0.18,
    "guess": 0.20,
    "slip": 0.10,
}


QUESTION_TYPE_BKT_PROFILES = {
    "definition": {"learn": 0.20, "guess": 0.22, "slip": 0.08, "difficulty": 0.85},
    "example": {"learn": 0.20, "guess": 0.24, "slip": 0.09, "difficulty": 0.90},
    "purpose": {"learn": 0.19, "guess": 0.20, "slip": 0.09, "difficulty": 1.00},
    "components": {"learn": 0.18, "guess": 0.18, "slip": 0.10, "difficulty": 1.05},
    "requirement": {"learn": 0.18, "guess": 0.18, "slip": 0.10, "difficulty": 1.05},
    "technical_fact": {"learn": 0.17, "guess": 0.18, "slip": 0.11, "difficulty": 1.05},
    "condition": {"learn": 0.17, "guess": 0.17, "slip": 0.11, "difficulty": 1.10},
    "cause_effect": {"learn": 0.16, "guess": 0.17, "slip": 0.12, "difficulty": 1.15},
    "comparison": {"learn": 0.16, "guess": 0.16, "slip": 0.12, "difficulty": 1.15},
    "process": {"learn": 0.16, "guess": 0.15, "slip": 0.12, "difficulty": 1.15},
    "numeric_check": {"learn": 0.14, "guess": 0.12, "slip": 0.14, "difficulty": 1.25},
    "visual_interpretation": {"learn": 0.14, "guess": 0.13, "slip": 0.14, "difficulty": 1.25},
}


def question_type_for(question: dict) -> str:
    source = question.get("source") if isinstance(question, dict) else None
    raw = ""

    if isinstance(question, dict):
        raw = str(question.get("question_type") or "").strip().lower()

    if not raw and isinstance(source, dict):
        raw = str(source.get("question_type") or "").strip().lower()

    return raw or "technical_fact"


def bkt_params_for_question(question: dict, concept: dict | None = None) -> dict:
    qtype = question_type_for(question)
    profile = QUESTION_TYPE_BKT_PROFILES.get(qtype, QUESTION_TYPE_BKT_PROFILES["technical_fact"])

    params = dict(DEFAULT_BKT)
    params.update(
        {
            "learn": profile.get("learn", DEFAULT_BKT["learn"]),
            "guess": profile.get("guess", DEFAULT_BKT["guess"]),
            "slip": profile.get("slip", DEFAULT_BKT["slip"]),
            "difficulty": profile.get("difficulty", 1.0),
            "question_type": qtype,
        }
    )

    return params


def ensure_concept_metadata(concept: dict) -> dict:
    concept.setdefault("question_type_stats", {})
    concept.setdefault("recent_misses", 0)
    concept.setdefault("last_question_type", None)
    concept.setdefault("last_correct", None)
    concept.setdefault("last_incorrect", None)
    concept.setdefault("review_due_at", None)
    concept.setdefault("review_delay_days", 0)
    concept.setdefault("review_bucket", "new_concept")
    concept.setdefault("last_review_scheduled_at", None)
    return concept


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso_datetime(value: str | None) -> datetime | None:
    raw = str(value or "").strip()

    if not raw:
        return None

    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"

        parsed = datetime.fromisoformat(raw)

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)
    except Exception:
        return None


def review_delay_days_for_concept(concept: dict) -> int:
    ensure_concept_metadata(concept)

    attempts = int(concept.get("attempts") or 0)

    if attempts <= 0:
        return 0

    mastery = float(concept.get("mastery", DEFAULT_BKT["prior"]))
    recent_misses = int(concept.get("recent_misses") or 0)

    if recent_misses > 0:
        return 0

    if mastery < 0.40:
        return 0

    if mastery < 0.75:
        return 1

    if mastery < 0.90:
        return 3

    return 7


def update_review_schedule(concept: dict, timestamp: str | None = None) -> dict:
    ensure_concept_metadata(concept)

    attempts = int(concept.get("attempts") or 0)

    if attempts <= 0:
        concept["review_due_at"] = None
        concept["review_delay_days"] = 0
        concept["review_bucket"] = "new_concept"
        concept["last_review_scheduled_at"] = timestamp or now_iso()
        return concept

    timestamp = timestamp or now_iso()
    base = parse_iso_datetime(timestamp) or datetime.now(timezone.utc)
    delay_days = review_delay_days_for_concept(concept)
    due_at = base + timedelta(days=delay_days)
    mastery = float(concept.get("mastery", DEFAULT_BKT["prior"]))

    if delay_days <= 0:
        bucket = "due_now"
    elif mastery >= 0.90:
        bucket = "mastered_review"
    else:
        bucket = "due_later"

    concept["review_due_at"] = due_at.isoformat()
    concept["review_delay_days"] = int(delay_days)
    concept["review_bucket"] = bucket
    concept["last_review_scheduled_at"] = timestamp

    return concept


def review_bucket_for_concept(concept: dict, now: datetime | None = None) -> str:
    ensure_concept_metadata(concept)

    attempts = int(concept.get("attempts") or 0)

    if attempts <= 0:
        return "new_concept"

    now = now or datetime.now(timezone.utc)
    due_at = parse_iso_datetime(concept.get("review_due_at"))
    bucket = str(concept.get("review_bucket") or "").strip() or "due_later"

    if due_at and due_at <= now:
        return "due_now"

    if bucket in {"due_now", "due_today", "due_later", "mastered_review", "new_concept"}:
        return bucket

    return "due_later"


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
                "question_type": str(item.get("question_type") or "technical_fact").strip() or "technical_fact",
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
        "last_correct": None,
        "last_incorrect": None,
        "last_question_type": None,
        "recent_misses": 0,
        "question_type_stats": {},
        "review_due_at": None,
        "review_delay_days": 0,
        "review_bucket": "new_concept",
        "last_review_scheduled_at": None,
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
        else:
            ensure_concept_metadata(concepts[concept_id])

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

    last_attempt = state.get("last_attempt") if isinstance(state, dict) else None
    last_concept_id = ""

    if isinstance(last_attempt, dict):
        last_concept_id = str(last_attempt.get("concept_id") or "")

    if last_concept_id and len(pool) > 1:
        alternatives = [
            question for question in pool
            if str(question.get("concept_id") or "") != last_concept_id
        ]

        if alternatives:
            pool = alternatives

    def score(question: dict) -> tuple[int, int, float, int, int, float, str]:
        concept = ensure_concept_metadata(concepts.get(question["concept_id"], {}))
        mastery = float(concept.get("mastery", DEFAULT_BKT["prior"]))
        attempts = int(concept.get("attempts", 0))
        recent_misses = int(concept.get("recent_misses", 0))

        if attempts > 0 and not concept.get("review_due_at"):
            update_review_schedule(concept)

        bucket = review_bucket_for_concept(concept)
        bucket_priority = {
            "due_now": 0,
            "due_today": 1,
            "due_later": 4,
            "mastered_review": 5,
            "new_concept": 3,
        }.get(bucket, 4)

        qtype = question_type_for(question)
        stats = concept.get("question_type_stats") or {}
        type_attempts = int((stats.get(qtype) or {}).get("attempts") or 0)
        difficulty = float(bkt_params_for_question(question, concept).get("difficulty", 1.0))

        return (
            bucket_priority,
            0 if recent_misses > 0 else 1,
            mastery,
            type_attempts,
            attempts,
            -difficulty,
            str(question.get("question_id") or ""),
        )

    selected = sorted(pool, key=score)[0]
    selected = dict(selected)

    selected["recommendation_reason"] = recommendation_reason_for_question(selected, state)

    return selected


def recommendation_reason_for_question(question: dict, state: dict) -> str:
    concepts = state.get("concepts", {}) if isinstance(state, dict) else {}
    concept = ensure_concept_metadata(concepts.get(question.get("concept_id"), {}))
    mastery = float(concept.get("mastery", DEFAULT_BKT["prior"]))
    attempts = int(concept.get("attempts", 0))
    recent_misses = int(concept.get("recent_misses", 0))
    qtype = question_type_for(question)

    if attempts == 0:
        return f"new concept · {qtype}"

    bucket = review_bucket_for_concept(concept)

    if bucket == "due_now":
        return f"due now · {qtype}"

    if bucket == "due_today":
        return f"due today · {qtype}"

    if recent_misses > 0:
        return f"recent mistakes · {qtype}"

    if mastery < 0.40:
        return f"low mastery · {qtype}"

    if mastery < 0.75:
        return f"in progress · {qtype}"

    if bucket == "mastered_review":
        return f"mastered review · {qtype}"

    return f"scheduled review · {qtype}"


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

    ensure_concept_metadata(concept)

    qtype = question_type_for(question)
    old_mastery = float(concept.get("mastery", DEFAULT_BKT["prior"]))
    params = bkt_params_for_question(question, concept)
    new_mastery = bkt_update(old_mastery, correct, params)
    timestamp = now_iso()

    concept["mastery"] = new_mastery
    concept["attempts"] = int(concept.get("attempts", 0)) + 1
    concept["correct"] = int(concept.get("correct", 0)) + (1 if correct else 0)
    concept["incorrect"] = int(concept.get("incorrect", 0)) + (0 if correct else 1)
    concept["last_seen"] = timestamp
    concept["last_question_type"] = qtype
    concept["status"] = mastery_status(new_mastery)
    concept["bkt"] = params

    if correct:
        concept["last_correct"] = timestamp
        concept["recent_misses"] = max(0, int(concept.get("recent_misses", 0)) - 1)
    else:
        concept["last_incorrect"] = timestamp
        concept["recent_misses"] = int(concept.get("recent_misses", 0)) + 1

    update_review_schedule(concept, timestamp)

    type_stats = concept.setdefault("question_type_stats", {})
    qtype_stats = type_stats.setdefault(
        qtype,
        {
            "attempts": 0,
            "correct": 0,
            "incorrect": 0,
        },
    )
    qtype_stats["attempts"] = int(qtype_stats.get("attempts", 0)) + 1
    qtype_stats["correct"] = int(qtype_stats.get("correct", 0)) + (1 if correct else 0)
    qtype_stats["incorrect"] = int(qtype_stats.get("incorrect", 0)) + (0 if correct else 1)

    attempt = {
        "timestamp": timestamp,
        "question_id": question_id,
        "lesson_id": question["lesson_id"],
        "concept_id": concept_id,
        "question_type": qtype,
        "correct": bool(correct),
        "mastery_before": old_mastery,
        "mastery_after": new_mastery,
        "bkt": params,
        "review_bucket": concept.get("review_bucket"),
        "review_due_at": concept.get("review_due_at"),
        "review_delay_days": concept.get("review_delay_days"),
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
    schedule_changed = False

    for concept_id, concept in state.get("concepts", {}).items():
        ensure_concept_metadata(concept)

        if int(concept.get("attempts") or 0) > 0 and not concept.get("review_due_at"):
            update_review_schedule(concept)
            schedule_changed = True

        mastery = float(concept.get("mastery", DEFAULT_BKT["prior"]))
        review_bucket = review_bucket_for_concept(concept)

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
                "last_correct": concept.get("last_correct"),
                "last_incorrect": concept.get("last_incorrect"),
                "last_question_type": concept.get("last_question_type"),
                "recent_misses": int(concept.get("recent_misses", 0)),
                "question_type_stats": concept.get("question_type_stats") or {},
                "review_due_at": concept.get("review_due_at"),
                "review_delay_days": int(concept.get("review_delay_days") or 0),
                "review_bucket": review_bucket,
                "last_review_scheduled_at": concept.get("last_review_scheduled_at"),
            }
        )

    if schedule_changed:
        state["updated_at"] = now_iso()
        save_state(output_dir, state)

    concepts.sort(key=lambda item: (item.get("review_bucket") != "due_now", item["mastery"], item["concept_id"]))

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

