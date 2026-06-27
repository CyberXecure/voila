"""Local pedagogy engine for Voila.

v0.4.55 keeps the engine deterministic and local-only, but upgrades question
variety beyond simple concept-recognition prompts.

The generated files remain compatible with the v0.4.45+ local exercise bank
discovery/adapter stack:

- course_analysis.local.json
- exercise_bank.local.json
- exam_blueprint.local.json
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


ENGINE_NAME = "local_pedagogy_engine"
ENGINE_VERSION = "v0.4.55"
QUESTION_VARIETY_VERSION = "v0.4.55"

STOPWORDS = {
    "sunt",
    "este",
    "prin",
    "doua",
    "două",
    "unei",
    "unui",
    "care",
    "apoi",
    "poate",
    "pentru",
    "calculul",
    "folosită",
    "folosita",
    "locală",
    "locala",
    "dintre",
    "între",
    "intre",
    "este",
    "definită",
    "definita",
    "descrie",
    "identifica",
    "identifică",
    "conceptul",
    "bine",
}


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_text.lower()).strip("_")
    return slug or "concept"


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-zĂÂÎȘȚăâîșț0-9']{4,}", text)


def _sentence_split(text: str) -> list[str]:
    sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", text.strip()) if item.strip()]
    if sentences:
        return sentences
    return [text.strip()] if text.strip() else []


def extract_concepts(text: str, limit: int = 16) -> list[dict[str, Any]]:
    """Extract deterministic concept candidates from text."""

    counts: Counter[str] = Counter()
    display: dict[str, str] = {}

    for word in _words(text):
        key = word.strip(".,;:!?()[]{}«»\"'").lower()
        if len(key) < 4 or key in STOPWORDS:
            continue
        counts[key] += 1
        display.setdefault(key, word.strip(".,;:!?()[]{}«»\"'"))

    concepts: list[dict[str, Any]] = []
    for index, (key, count) in enumerate(counts.most_common(limit), start=1):
        label = display.get(key, key)
        concepts.append(
            {
                "id": f"local_concept_{index:03d}_{_slugify(label)}",
                "label": label,
                "slug": _slugify(label),
                "frequency": count,
            }
        )

    if not concepts:
        concepts.append(
            {
                "id": "local_concept_001_general",
                "label": "concept",
                "slug": "general",
                "frequency": 1,
            }
        )

    return concepts


def extract_formulas(text: str) -> list[dict[str, Any]]:
    """Extract simple formula-like snippets."""

    candidates = []
    for match in re.finditer(r"[^.!?\n]*(?:=|lim|∫|√|\^|f'\(x\)|\d+\s*[+\-*/]\s*\d+)[^.!?\n]*", text):
        snippet = match.group(0).strip(" .;:")
        if snippet and len(snippet) <= 180:
            candidates.append(snippet)

    formulas = []
    for index, snippet in enumerate(dict.fromkeys(candidates), start=1):
        formulas.append(
            {
                "id": f"local_formula_{index:03d}",
                "formula": snippet,
                "skill_id": "local_formula_review",
            }
        )

    return formulas


def _concept_sentence(concept: dict[str, Any], sentences: list[str]) -> str:
    label = str(concept["label"]).lower()
    for sentence in sentences:
        if label in sentence.lower():
            return sentence
    return sentences[0] if sentences else f"Fragment despre {concept['label']}."


def _choice_pool(concepts: list[dict[str, Any]], answer: str, count: int = 4) -> list[str]:
    choices: list[str] = [answer]
    for concept in concepts:
        label = str(concept["label"])
        if label.lower() != answer.lower() and label not in choices:
            choices.append(label)
        if len(choices) >= count:
            break

    while len(choices) < count:
        choices.append(f"opțiune {len(choices) + 1}")

    return choices[:count]


def build_exercises(text: str, concepts: list[dict[str, Any]], formulas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build a varied local exercise bank."""

    sentences = _sentence_split(text)
    exercises: list[dict[str, Any]] = []
    exercise_index = 1

    def add(exercise: dict[str, Any]) -> None:
        nonlocal exercise_index
        exercise = dict(exercise)
        exercise["id"] = f"local_ex_{exercise_index:04d}"
        exercise_index += 1
        exercises.append(exercise)

    primary_concepts = concepts[:8]
    for index, concept in enumerate(primary_concepts, start=1):
        label = str(concept["label"])
        skill_id = str(concept["id"])
        sentence = _concept_sentence(concept, sentences)
        related = primary_concepts[index] if index < len(primary_concepts) else primary_concepts[0]

        add(
            {
                "skill_id": skill_id,
                "type": "multiple_choice",
                "difficulty": "easy",
                "question": f"Care afirmație identifică cel mai bine conceptul «{label}»?",
                "choices": _choice_pool(primary_concepts, label),
                "correct_answer": label,
                "explanation": "Exercițiu local de recunoaștere a conceptului, păstrat ca întrebare de încălzire.",
                "source_excerpt": sentence,
                "quality_tags": ["concept_recognition", "warmup"],
            }
        )

        add(
            {
                "skill_id": skill_id,
                "type": "short_answer",
                "difficulty": "medium",
                "question": f"Explică pe scurt, cu propriile cuvinte, rolul conceptului «{label}» în fragment.",
                "choices": [],
                "correct_answer": f"Conceptul «{label}» trebuie explicat prin legătura lui cu ideea principală din fragment.",
                "explanation": "Întrebarea cere reformulare și înțelegere, nu doar recunoaștere.",
                "source_excerpt": sentence,
                "quality_tags": ["explain_in_own_words", "understanding"],
            }
        )

        add(
            {
                "skill_id": skill_id,
                "type": "evidence_based",
                "difficulty": "medium",
                "question": f"Selectează ideea din fragment care susține cel mai bine conceptul «{label}».",
                "choices": _choice_pool(primary_concepts, label),
                "correct_answer": sentence,
                "explanation": "Răspunsul trebuie justificat printr-un indiciu textual din fragment.",
                "source_excerpt": sentence,
                "quality_tags": ["evidence", "source_grounded"],
            }
        )

        add(
            {
                "skill_id": skill_id,
                "type": "compare_concepts",
                "difficulty": "medium",
                "question": f"Compară conceptul «{label}» cu «{related['label']}» și precizează o diferență relevantă.",
                "choices": [],
                "correct_answer": f"Un răspuns bun explică diferența dintre «{label}» și «{related['label']}» pe baza contextului.",
                "explanation": "Întrebarea verifică relații între concepte, nu memorare izolată.",
                "source_excerpt": sentence,
                "quality_tags": ["compare", "concept_relation"],
            }
        )

        add(
            {
                "skill_id": skill_id,
                "type": "apply_concept",
                "difficulty": "medium",
                "question": f"Aplică ideea de «{label}» într-un exemplu simplu legat de fragment.",
                "choices": [],
                "correct_answer": f"Exemplul trebuie să folosească explicit conceptul «{label}» într-o situație coerentă.",
                "explanation": "Întrebarea verifică transferul conceptului într-un exemplu.",
                "source_excerpt": sentence,
                "quality_tags": ["apply", "transfer"],
            }
        )

    for formula in formulas[:4]:
        snippet = str(formula["formula"])
        add(
            {
                "skill_id": str(formula["skill_id"]),
                "type": "formula_interpretation",
                "difficulty": "medium",
                "question": f"Ce rol are formula sau notația următoare în fragment: {snippet}?",
                "choices": [],
                "correct_answer": "Formula trebuie interpretată ca relație sau procedeu de calcul în contextul fragmentului.",
                "explanation": "Întrebarea cere interpretarea formulei, nu OCR sau calcul numeric automat.",
                "source_excerpt": snippet,
                "quality_tags": ["formula", "interpretation"],
            }
        )

        add(
            {
                "skill_id": str(formula["skill_id"]),
                "type": "apply_formula",
                "difficulty": "hard",
                "question": "Descrie pașii generali prin care ai folosi formula identificată într-un exercițiu.",
                "choices": [],
                "correct_answer": "Un răspuns bun menționează identificarea variabilelor, înlocuirea lor și interpretarea rezultatului.",
                "explanation": "Întrebarea verifică pașii de aplicare, fără a necesita API sau CAS.",
                "source_excerpt": snippet,
                "quality_tags": ["formula", "apply"],
            }
        )

    return exercises


def build_course_analysis(
    text: str,
    *,
    course_id: str,
    source_path: str,
    language: str,
    concepts: list[dict[str, Any]],
    formulas: list[dict[str, Any]],
) -> dict[str, Any]:
    sentences = _sentence_split(text)
    return {
        "schema_version": "1",
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "question_variety_version": QUESTION_VARIETY_VERSION,
        "course_id": course_id,
        "source_path": source_path,
        "language": language,
        "concept_count": len(concepts),
        "formula_count": len(formulas),
        "sentence_count": len(sentences),
        "concepts": concepts,
        "formulas": formulas,
        "summary": "Analiză locală deterministă pentru generare de exerciții variate, fără API extern.",
        "legacy_fallback": "Legacy quiz/question data remains available when local analysis is unavailable.",
    }


def build_exercise_bank(
    *,
    course_id: str,
    language: str,
    exercises: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "1",
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "question_variety_version": QUESTION_VARIETY_VERSION,
        "course_id": course_id,
        "language": language,
        "exercise_count": len(exercises),
        "legacy_fallback": "Use legacy quiz/question data when no valid local exercise_bank.local.json is available.",
        "generation_profile": "varied_local_questions",
        "quality_goal": "Move beyond concept recognition toward explain/apply/compare/formula interpretation.",
        "exercises": exercises,
    }


def build_exam_blueprint(
    *,
    course_id: str,
    exercises: list[dict[str, Any]],
) -> dict[str, Any]:
    type_counts = Counter(str(item.get("type", "")) for item in exercises)
    skill_counts = Counter(str(item.get("skill_id", "")) for item in exercises)
    return {
        "schema_version": "1",
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "question_variety_version": QUESTION_VARIETY_VERSION,
        "course_id": course_id,
        "policy": "Use local exercise bank only when explicitly enabled; otherwise keep legacy fallback.",
        "selection_policy": [
            "legacy_fallback_is_default",
            "local_exercise_bank_requires_explicit_flag",
            "no_attempts_scoring_or_progress_updates",
        ],
        "legacy_fallback": "Legacy quiz/question data remains the default safe path.",
        "question_type_counts": dict(sorted(type_counts.items())),
        "skill_counts": dict(sorted(skill_counts.items())),
        "will_save_attempt": False,
        "will_update_progress": False,
        "will_score_answer": False,
        "requires_cloud_or_api": False,
    }


def generate_local_pedagogy_bundle(
    text: str,
    output_dir: str | Path,
    *,
    course_id: str = "local-course",
    source_path: str = "",
    language: str = "ro",
) -> dict[str, Any]:
    """Generate local pedagogy outputs into an internal or caller-provided output directory.

    This function is used by CLI diagnostics and internal temporary sample
    generation. Web routes must not pass user-provided filesystem roots here.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    concepts = extract_concepts(text)
    formulas = extract_formulas(text)
    exercises = build_exercises(text, concepts, formulas)

    analysis = build_course_analysis(
        text,
        course_id=course_id,
        source_path=source_path,
        language=language,
        concepts=concepts,
        formulas=formulas,
    )
    exercise_bank = build_exercise_bank(course_id=course_id, language=language, exercises=exercises)
    blueprint = build_exam_blueprint(course_id=course_id, exercises=exercises)

    (output_path / "course_analysis.local.json").write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_path / "exercise_bank.local.json").write_text(
        json.dumps(exercise_bank, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_path / "exam_blueprint.local.json").write_text(
        json.dumps(blueprint, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        "status": "ok",
        "engine_version": ENGINE_VERSION,
        "question_variety_version": QUESTION_VARIETY_VERSION,
        "concept_count": len(concepts),
        "exercise_count": len(exercises),
        "question_type_count": len({item.get("type") for item in exercises}),
        "output_dir": str(output_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate local pedagogy outputs.")
    parser.add_argument("--text", required=True, help="Input text to analyze.")
    parser.add_argument("--output-dir", required=True, help="Output directory for local pedagogy files.")
    parser.add_argument("--course-id", default="local-course", help="Course id.")
    parser.add_argument("--source-path", default="", help="Optional source path label.")
    parser.add_argument("--language", default="ro", help="Language code.")
    args = parser.parse_args()

    summary = generate_local_pedagogy_bundle(
        args.text,
        args.output_dir,
        course_id=args.course_id,
        source_path=args.source_path,
        language=args.language,
    )
    print(json.dumps(summary, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
