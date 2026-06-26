"""Local-first pedagogy engine scaffold for Voila.

This module is intentionally deterministic and dependency-free. It creates
course-analysis, exercise-bank, and exam-blueprint JSON structures without any
cloud/API/LLM dependency.

The scaffold is not a replacement for the legacy quiz generator yet. It is a
safe content-supplier foundation that later milestones can connect to Exam Prep.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_ENGINE_VERSION = "v0.4.44"
_DEFAULT_LANGUAGE = "ro"


@dataclass(frozen=True)
class LocalPedagogyBundle:
    """Generated local pedagogy outputs."""

    course_analysis: dict[str, Any]
    exercise_bank: dict[str, Any]
    exam_blueprint: dict[str, Any]


_ROMANIAN_STOPWORDS = {
    "acest",
    "aceasta",
    "aceste",
    "acestea",
    "acolo",
    "aici",
    "ale",
    "are",
    "asupra",
    "care",
    "către",
    "cele",
    "celor",
    "este",
    "fără",
    "fiind",
    "într",
    "pentru",
    "prin",
    "sau",
    "sunt",
    "toate",
    "unor",
    "unei",
    "este",
    "mai",
    "mult",
    "poate",
    "trebuie",
    "dintre",
    "același",
}

_DEFINITION_MARKERS = (
    " este ",
    " sunt ",
    " reprezintă ",
    " reprezinta ",
    " se numește ",
    " se numeste ",
    " se definește ",
    " se defineste ",
    " constă ",
    " consta ",
)

_PROCESS_MARKERS = (
    " apoi ",
    " după ",
    " dupa ",
    " înainte ",
    " inainte ",
    " pas ",
    " etapă ",
    " etapa ",
    " proces ",
    " metoda ",
    " metodă ",
)

_FORMULA_MARKERS = (
    "=",
    "formula",
    "ecuație",
    "ecuatie",
    "calcul",
    "derivat",
    "integral",
    "funcție",
    "functie",
)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace while preserving sentence content."""

    return re.sub(r"\s+", " ", text or "").strip()


def split_sentences(text: str, *, limit: int = 240) -> list[str]:
    """Split text into a bounded list of sentence-like units."""

    cleaned = normalize_whitespace(text)
    if not cleaned:
        return []

    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    sentences = [part.strip() for part in parts if len(part.strip()) >= 12]
    return sentences[:limit]


def extract_key_concepts(sentences: list[str], *, max_concepts: int = 24) -> list[dict[str, Any]]:
    """Extract simple concept candidates from sentence text."""

    counter: Counter[str] = Counter()

    for sentence in sentences:
        words = re.findall(r"[A-Za-zĂÂÎȘŞȚŢăâîșşțţ0-9][A-Za-zĂÂÎȘŞȚŢăâîșşțţ0-9\-]{4,}", sentence)
        for raw_word in words:
            word = raw_word.strip(" -—:;,.()[]{}").lower()
            if len(word) < 5 or word in _ROMANIAN_STOPWORDS:
                continue
            counter[word] += 1

    concepts: list[dict[str, Any]] = []
    for index, (term, count) in enumerate(counter.most_common(max_concepts), start=1):
        concepts.append(
            {
                "skill_id": f"local_concept_{index:03d}_{slugify(term)}",
                "title": term,
                "frequency": count,
                "source": "local_term_frequency",
            }
        )

    return concepts


def classify_sentence(sentence: str) -> list[str]:
    """Classify a sentence by lightweight pedagogical signals."""

    lower = f" {sentence.lower()} "
    tags: list[str] = []

    if any(marker in lower for marker in _DEFINITION_MARKERS):
        tags.append("definition")
    if any(marker in lower for marker in _PROCESS_MARKERS):
        tags.append("process")
    if any(marker in lower for marker in _FORMULA_MARKERS):
        tags.append("formula_or_calculation")
    if "?" in sentence:
        tags.append("question_like")

    return tags or ["context"]


def slugify(text: str) -> str:
    """Create a stable ASCII-ish slug."""

    replacements = str.maketrans(
        {
            "ă": "a",
            "â": "a",
            "î": "i",
            "ș": "s",
            "ş": "s",
            "ț": "t",
            "ţ": "t",
            "Ă": "a",
            "Â": "a",
            "Î": "i",
            "Ș": "s",
            "Ş": "s",
            "Ț": "t",
            "Ţ": "t",
        }
    )
    value = text.translate(replacements).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "item"


def infer_learning_objectives(concepts: list[dict[str, Any]]) -> list[str]:
    """Create local learning objectives from detected concepts."""

    if not concepts:
        return [
            "Identifică ideile principale din materialul de curs.",
            "Revizuiește conceptele-cheie înainte de exerciții.",
        ]

    objectives: list[str] = []
    for concept in concepts[:6]:
        objectives.append(f"Explică noțiunea «{concept['title']}» în contextul materialului.")
    return objectives


def build_course_analysis(
    course_text: str,
    *,
    course_id: str = "local-course",
    source_path: str = "",
    language: str = _DEFAULT_LANGUAGE,
) -> dict[str, Any]:
    """Build deterministic local course analysis JSON."""

    sentences = split_sentences(course_text)
    concepts = extract_key_concepts(sentences)
    tagged_sentences = [
        {
            "id": f"sentence_{index:04d}",
            "text": sentence,
            "tags": classify_sentence(sentence),
        }
        for index, sentence in enumerate(sentences[:80], start=1)
    ]

    return {
        "schema_version": "1",
        "engine": "local_pedagogy_engine",
        "engine_version": _ENGINE_VERSION,
        "course_id": course_id,
        "source_path": source_path,
        "language": language,
        "summary": {
            "sentence_count": len(sentences),
            "concept_count": len(concepts),
            "definition_signal_count": sum(1 for item in tagged_sentences if "definition" in item["tags"]),
            "process_signal_count": sum(1 for item in tagged_sentences if "process" in item["tags"]),
            "formula_signal_count": sum(1 for item in tagged_sentences if "formula_or_calculation" in item["tags"]),
        },
        "learning_objectives": infer_learning_objectives(concepts),
        "key_concepts": concepts,
        "tagged_sentences": tagged_sentences,
        "next_step": "Generate exercise_bank.local.json from this analysis.",
    }


def _choice_pool(concepts: list[dict[str, Any]], correct: str) -> list[str]:
    titles = [str(item["title"]) for item in concepts if str(item["title"]) != correct]
    distractors = titles[:3]
    while len(distractors) < 3:
        distractors.append(f"opțiune locală {len(distractors) + 1}")
    return [correct] + distractors[:3]


def build_exercise_bank(course_analysis: dict[str, Any]) -> dict[str, Any]:
    """Build a local exercise bank scaffold from course analysis."""

    concepts = list(course_analysis.get("key_concepts", []))
    tagged_sentences = list(course_analysis.get("tagged_sentences", []))
    exercises: list[dict[str, Any]] = []

    for index, concept in enumerate(concepts[:12], start=1):
        title = str(concept.get("title", f"concept {index}"))
        skill_id = str(concept.get("skill_id", f"local_concept_{index:03d}"))
        exercises.append(
            {
                "id": f"local_ex_{index:04d}",
                "skill_id": skill_id,
                "type": "multiple_choice",
                "difficulty": "easy",
                "question": f"Care afirmație identifică cel mai bine conceptul «{title}»?",
                "choices": _choice_pool(concepts, title),
                "correct_answer": title,
                "explanation": "Exercițiu generat local ca verificare de recunoaștere a conceptului.",
                "source": "local_pedagogy_engine",
            }
        )

    definition_sentences = [item for item in tagged_sentences if "definition" in item.get("tags", [])]
    for offset, item in enumerate(definition_sentences[:8], start=1):
        exercises.append(
            {
                "id": f"local_def_{offset:04d}",
                "skill_id": "local_definition_review",
                "type": "short_answer",
                "difficulty": "medium",
                "question": "Explică pe scurt ideea principală din fragmentul sursă.",
                "correct_answer": item.get("text", ""),
                "explanation": "Răspunsul trebuie verificat cu fragmentul sursă atașat.",
                "source_excerpt": item.get("text", ""),
                "source": "local_pedagogy_engine",
            }
        )

    formula_sentences = [item for item in tagged_sentences if "formula_or_calculation" in item.get("tags", [])]
    for offset, item in enumerate(formula_sentences[:6], start=1):
        exercises.append(
            {
                "id": f"local_formula_{offset:04d}",
                "skill_id": "local_formula_review",
                "type": "formula_or_calculation",
                "difficulty": "medium",
                "question": "Identifică rolul relației/formulei semnalate în fragmentul sursă.",
                "correct_answer": "Răspuns conceptual bazat pe fragmentul sursă.",
                "explanation": "STEM v1 păstrează formula ca text/imagine sursă și cere verificare conceptuală.",
                "source_excerpt": item.get("text", ""),
                "source": "local_pedagogy_engine",
            }
        )

    if not exercises:
        exercises.append(
            {
                "id": "local_ex_0001",
                "skill_id": "local_general_review",
                "type": "short_answer",
                "difficulty": "easy",
                "question": "Care este ideea principală a materialului procesat?",
                "correct_answer": "Răspunsul se verifică pe baza materialului sursă.",
                "explanation": "Fallback local pentru documente fără suficiente semnale detectate.",
                "source": "local_pedagogy_engine",
            }
        )

    return {
        "schema_version": "1",
        "engine": "local_pedagogy_engine",
        "engine_version": _ENGINE_VERSION,
        "course_id": course_analysis.get("course_id", "local-course"),
        "source": "course_analysis.local.json",
        "exercise_count": len(exercises),
        "exercises": exercises,
        "legacy_fallback": "Use legacy quiz/question data when this local bank is missing or empty.",
    }


def build_exam_blueprint(
    course_analysis: dict[str, Any],
    exercise_bank: dict[str, Any],
) -> dict[str, Any]:
    """Build a local exam blueprint scaffold."""

    exercises = list(exercise_bank.get("exercises", []))
    type_counts: Counter[str] = Counter(str(item.get("type", "unknown")) for item in exercises)
    difficulty_counts: Counter[str] = Counter(str(item.get("difficulty", "unknown")) for item in exercises)

    return {
        "schema_version": "1",
        "engine": "local_pedagogy_engine",
        "engine_version": _ENGINE_VERSION,
        "course_id": course_analysis.get("course_id", "local-course"),
        "recommended_question_count": min(30, max(5, len(exercises))),
        "coverage": {
            "concepts": len(course_analysis.get("key_concepts", [])),
            "exercises": len(exercises),
            "types": dict(type_counts),
            "difficulty": dict(difficulty_counts),
        },
        "selection_policy": [
            "prefer weak skills when progress data exists",
            "avoid repeating the same question id in a session",
            "mix definitions, concepts, formulas, and short-answer checks when available",
            "fallback to legacy quiz/question source if local exercise bank is unavailable",
        ],
    }


def generate_local_pedagogy_bundle(
    course_text: str,
    output_dir: str | Path,
    *,
    course_id: str = "local-course",
    source_path: str = "",
    language: str = _DEFAULT_LANGUAGE,
) -> LocalPedagogyBundle:
    """Generate all local pedagogy JSON files in an output directory."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    analysis = build_course_analysis(
        course_text,
        course_id=course_id,
        source_path=source_path,
        language=language,
    )
    exercise_bank = build_exercise_bank(analysis)
    exam_blueprint = build_exam_blueprint(analysis, exercise_bank)

    files = {
        "course_analysis.local.json": analysis,
        "exercise_bank.local.json": exercise_bank,
        "exam_blueprint.local.json": exam_blueprint,
    }

    for filename, payload in files.items():
        (output / filename).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return LocalPedagogyBundle(
        course_analysis=analysis,
        exercise_bank=exercise_bank,
        exam_blueprint=exam_blueprint,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate local pedagogy scaffold JSON outputs.")
    parser.add_argument("--text", default="", help="Course text to analyze.")
    parser.add_argument("--input", default="", help="Optional UTF-8 text input path.")
    parser.add_argument("--output-dir", required=True, help="Output directory for local pedagogy JSON files.")
    parser.add_argument("--course-id", default="local-course", help="Stable course id.")
    parser.add_argument("--language", default=_DEFAULT_LANGUAGE, help="Course language code.")
    args = parser.parse_args()

    course_text = args.text
    source_path = args.input

    if args.input:
        course_text = Path(args.input).read_text(encoding="utf-8")

    bundle = generate_local_pedagogy_bundle(
        course_text,
        args.output_dir,
        course_id=args.course_id,
        source_path=source_path,
        language=args.language,
    )

    print(
        json.dumps(
            {
                "status": "ok",
                "engine_version": _ENGINE_VERSION,
                "concept_count": len(bundle.course_analysis.get("key_concepts", [])),
                "exercise_count": bundle.exercise_bank.get("exercise_count", 0),
                "output_dir": str(Path(args.output_dir)),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


