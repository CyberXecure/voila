from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from content_filter import should_exclude_study_item


TECHNICAL_KEYWORDS = [
    "is used to", "are used to", "is used for", "are used for",
    "designed to", "intended to", "consists of", "comprises", "contains",
    "provides", "prevents", "reduces", "increases", "decreases",
    "must", "should", "required", "requires", "ensure", "checked",
    "inspection", "maintenance", "operation", "operates", "because",
    "therefore", "so that", "in order to", "when", "if", "during",
    "pressure", "temperature", "valve", "pump", "fuel", "oil", "engine",
    "cooling", "lubricating", "filter", "strainer", "separator",
    "compressor", "turbine", "bearing", "piston", "cylinder",
    "injection", "turbocharger", "scavenge", "exhaust", "vibration",
    "diesel cycle", "indicator diagram", "constant pressure", "constant volume",
]

GENERIC_TITLES = {
    "introduction",
    "overview",
    "general",
    "summary",
    "background",
    "principles",
}

BAD_SENTENCE_PATTERNS = [
    r"^figure\s+[0-9ivxlcdm]",
    r"^fig\.\s+[0-9ivxlcdm]",
    r"^table\s+[0-9ivxlcdm]",
    r"^\d+$",
    r"^chapter\s+\d+$",
    r"^part\s+\d+$",
    r"^source pdf pages",
    r"^word count",
]

TOPIC_RULES = [
    ("engine cycles", [
        "diesel cycle", "practical cycle", "indicator diagram",
        "constant pressure", "constant volume", "adiabatic",
        "heat rejected", "ideal efficiency", "pumping work",
    ]),
    ("marine diesel engines", [
        "diesel engine", "reciprocating engine", "motor ship",
        "merchant motor ship", "propulsion", "bore", "stroke",
    ]),
    ("fuel injection", [
        "fuel injection", "injection", "injector", "atomis", "atomiz",
        "blast injection",
    ]),
    ("two-stroke engines", [
        "two-stroke", "2-stroke", "crosshead",
    ]),
    ("four-stroke engines", [
        "four-stroke", "4-stroke", "trunk piston",
    ]),
    ("turbocharging", [
        "turbocharger", "turbocharging", "exhaust gas turbine", "compressor",
    ]),
    ("exhaust valves", [
        "exhaust valve", "exhaust valves",
    ]),
    ("scavenging", [
        "scavenge", "scavenging", "air flow",
    ]),
    ("cylinder lubrication", [
        "cylinder oil", "cylinder lubrication", "lubricator",
    ]),
    ("lubricating oil systems", [
        "lubricating oil", "lube oil", "lubrication system",
    ]),
    ("cooling systems", [
        "cooling water", "cooling system", "coolant",
    ]),
    ("vibration and balancing", [
        "vibration", "moment compensator", "counterweight", "axial vibration",
    ]),
    ("bearings", [
        "bearing", "bearings", "thrust bearing",
    ]),
    ("pistons and cylinders", [
        "piston", "cylinder liner", "cylinder cover", "cylinder head",
    ]),
    ("starting air systems", [
        "starting air", "air start", "starting valve",
    ]),
    ("governors and control", [
        "governor", "control system", "speed control",
    ]),
]


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_key(value: str) -> str:
    return normalize_space(value).lower()


def is_generic_title(title: str) -> bool:
    value = normalize_key(title)

    if not value:
        return True

    if "pounder" in value and "marine diesel engines" in value:
        return True

    if "marine diesel engines and gas turbines" in value:
        return True

    if value == "practical cycles":
        return False

    return value in GENERIC_TITLES or value.startswith("introduction ")


def clean_title(title: str) -> str:
    value = normalize_space(title)

    if value.upper() == value and len(value) > 4:
        value = value.title()

    return value


def split_sentences(text: str) -> list[str]:
    compact = normalize_space(text)

    if not compact:
        return []

    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", compact)
    sentences = []

    for part in parts:
        sentence = normalize_space(part)

        if 45 <= len(sentence) <= 360:
            sentences.append(sentence)

    return sentences


def extract_lessons(course_md: str) -> list[dict]:
    pattern = re.compile(
        r"^##\s+(L\d+)\s+—\s+(.+?)\s*$",
        re.MULTILINE,
    )

    matches = list(pattern.finditer(course_md))
    lessons = []

    for idx, match in enumerate(matches):
        lesson_id = match.group(1).strip()
        title = match.group(2).strip()

        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(course_md)
        block = course_md[start:end]

        pages = []
        pages_match = re.search(r"Source PDF pages:\s*([0-9,\s]+)", block)

        if pages_match:
            pages = [
                int(value.strip())
                for value in pages_match.group(1).split(",")
                if value.strip().isdigit()
            ]

        text_match = re.search(
            r"### Cleaned source text\s*```text\s*(.*?)\s*```",
            block,
            flags=re.DOTALL,
        )

        source_text = text_match.group(1).strip() if text_match else block.strip()

        lessons.append(
            {
                "lesson_id": lesson_id,
                "title": title,
                "source_pdf_pages": pages,
                "source_text": source_text,
            }
        )

    return lessons


def sentence_is_bad(sentence: str) -> bool:
    value = sentence.lower().strip()

    for pattern in BAD_SENTENCE_PATTERNS:
        if re.search(pattern, value):
            return True

    bad_fragments = [
        "generated by voila",
        "mode: source language",
        "text status:",
        "source:",
        "isbn",
        "copyright",
        "all rights reserved",
        "pounder’s marine diesel engines and gas turbines",
        "pounder's marine diesel engines and gas turbines",
        "pressure tdc volume",
        "tdc volume bdc",
        "volume bdc",
        "pressure tdc",
    ]

    if any(fragment in value for fragment in bad_fragments):
        return True

    words = re.findall(r"[A-Za-z]{3,}", sentence)

    if len(words) <= 6 and any(marker in value for marker in ["tdc", "bdc", "volume", "pressure"]):
        return True

    return False


def technical_score(sentence: str) -> int:
    lower = sentence.lower()
    score = 0

    for keyword in TECHNICAL_KEYWORDS:
        if keyword in lower:
            score += 1

    if re.search(r"\b\d+(?:\.\d+)?\s*(bar|kpa|mpa|mm|cm|m|kg|kw|mw|rpm|°c|deg|percent|%)\b", lower):
        score += 2

    if ";" in sentence:
        score += 1

    return score


def infer_concept_title(lesson_title: str, sentence: str) -> str:
    title = normalize_space(lesson_title)
    lower = normalize_key(sentence)

    if "term" in lower and "used to describe" in lower and "reciprocating engine" in lower:
        return "marine diesel engines"

    if "four-stroke engine" in lower or "four-stroke cycle" in lower:
        return "four-stroke engines"

    if "two-stroke engine" in lower or "two-stroke cycle" in lower:
        return "two-stroke engines"

    if (
        "diesel cycle" in lower
        or "indicator diagram" in lower
        or "theoretical cycle" in lower
        or "actual events in the cylinder" in lower
        or normalize_key(lesson_title) == "practical cycles"
    ):
        return "engine cycles"

    if "ideal efficiency" in lower and "cycle" in lower:
        return "engine cycles"

    if "heat is rejected" in lower and "constant volume" in lower:
        return "engine cycles"

    for topic, keywords in TOPIC_RULES:
        if any(keyword in lower for keyword in keywords):
            return topic

    if title and not is_generic_title(title):
        return clean_title(title)

    return "technical fundamentals"


def make_question(sentence: str, concept_title: str) -> tuple[str, str]:
    lower = sentence.lower()
    subject = concept_title

    if "term" in lower and "used to describe" in lower and "reciprocating engine" in lower:
        return (
            "How does the source define marine diesel engines?",
            "definition",
        )

    if "ideal efficiency" in lower and "cycle" in lower:
        return (
            "What does the source state about the ideal efficiency of the engine cycle?",
            "technical_fact",
        )

    if "heat is rejected" in lower and "constant volume" in lower:
        return (
            "How is heat rejected in the described engine cycle?",
            "cycle_process",
        )

    consists_match = re.search(
        r"^(.{8,90}?)\s+(?:consists|consist)\s+of\s+(.+)$",
        sentence,
        flags=re.IGNORECASE,
    )

    if consists_match:
        detected_subject = normalize_space(consists_match.group(1))
        return (
            f"What does the source say {detected_subject} consists of?",
            "components",
        )

    used_match = re.search(
        r"^(.{8,100}?)\s+(?:is|are|can be|may be)?\s*used\s+(?:to|for)\s+(.+)$",
        sentence,
        flags=re.IGNORECASE,
    )

    if used_match:
        detected_subject = normalize_space(used_match.group(1))
        detected_lower = detected_subject.lower()

        bad_subject_starts = (
            "today ",
            "the term",
            "this ",
            "these ",
            "it ",
            "in ",
            "when ",
            "where ",
        )

        if detected_lower.startswith(bad_subject_starts):
            detected_subject = subject

        return (
            f"What is the purpose of {detected_subject} according to the source?",
            "purpose",
        )

    if "designed to" in lower or "intended to" in lower:
        return (
            f"What function or purpose is described for {subject}?",
            "purpose",
        )

    if "should" in lower or "must" in lower or "required" in lower or "requires" in lower:
        return (
            f"What requirement or recommended action does the source state for {subject}?",
            "requirement",
        )

    if "prevent" in lower or "prevents" in lower or "avoid" in lower:
        return (
            "What problem is prevented or avoided according to the source?",
            "prevention",
        )

    if "because" in lower or "therefore" in lower or "so that" in lower or "in order to" in lower:
        return (
            f"What cause, reason, or result does the source describe for {subject}?",
            "cause_effect",
        )

    if "when" in lower or "if" in lower or "during" in lower:
        return (
            f"Under what condition or operating situation does the source describe {subject}?",
            "condition",
        )

    return (
        f"What technical point does the source state about {subject}?",
        "technical_fact",
    )


def lesson_passes_page_filter(pages: list[int], min_page: int) -> bool:
    if min_page <= 1:
        return True

    if not pages:
        return False

    return max(pages) >= min_page


def build_questions(lessons: list[dict], max_per_lesson: int, max_total: int, min_page: int) -> list[dict]:
    questions = []

    for lesson in lessons:
        lesson_id = lesson["lesson_id"]
        title = lesson["title"]
        source_text = lesson["source_text"]
        pages = lesson.get("source_pdf_pages", [])

        if not lesson_passes_page_filter(pages, min_page):
            continue

        if should_exclude_study_item(
            title=title,
            source_text=source_text,
            lesson_id=lesson_id,
        ):
            continue

        candidates = []

        for sentence in split_sentences(source_text):
            if sentence_is_bad(sentence):
                continue

            if should_exclude_study_item(
                title=title,
                question="",
                answer=sentence,
                source_text=sentence,
                lesson_id=lesson_id,
            ):
                continue

            score = technical_score(sentence)

            if score <= 0:
                continue

            concept_title = infer_concept_title(title, sentence)

            candidates.append(
                {
                    "sentence": sentence,
                    "score": score,
                    "concept_title": concept_title,
                }
            )

        candidates.sort(key=lambda item: item["score"], reverse=True)

        used_questions = set()
        lesson_count = 0

        for candidate in candidates:
            if lesson_count >= max_per_lesson:
                break

            if len(questions) >= max_total:
                break

            answer = candidate["sentence"]
            concept_title = candidate["concept_title"]
            question_text, question_type = make_question(answer, concept_title)
            question_key = question_text.lower()

            if question_key in used_questions:
                continue

            used_questions.add(question_key)
            question_id = f"SQ{len(questions) + 1:04d}"

            questions.append(
                {
                    "question_id": question_id,
                    "lesson_id": lesson_id,
                    "concept_id": f"{lesson_id} — {concept_title}",
                    "concept_title": concept_title,
                    "lesson_title": title,
                    "question_type": question_type,
                    "question": question_text,
                    "answer": answer,
                    "source_pdf_pages": pages,
                    "source_sentence": answer,
                    "generator": "study_quiz_builder_v0.3.5_source_only",
                }
            )

            lesson_count += 1

    return questions


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! source-based study quiz builder")
    parser.add_argument("output_dir", help="Voila output directory containing course.cleaned.md")
    parser.add_argument("--max-per-lesson", type=int, default=4)
    parser.add_argument("--max-total", type=int, default=350)
    parser.add_argument("--min-page", type=int, default=1)

    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    course_path = output_dir / "course.cleaned.md"

    if not course_path.exists():
        raise FileNotFoundError(f"course.cleaned.md not found: {course_path}")

    course_md = course_path.read_text(encoding="utf-8")
    lessons = extract_lessons(course_md)

    questions = build_questions(
        lessons=lessons,
        max_per_lesson=args.max_per_lesson,
        max_total=args.max_total,
        min_page=args.min_page,
    )

    quiz = {
        "version": "0.3.5",
        "mode": "source_only",
        "generator": "study_quiz_builder_v0.3.5",
        "min_page": args.min_page,
        "question_count": len(questions),
        "questions": questions,
    }

    output_path = output_dir / "quiz.study.json"
    output_path.write_text(
        json.dumps(quiz, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Voila! study quiz generated successfully.")
    print(f"Lessons parsed: {len(lessons)}")
    print(f"Min page: {args.min_page}")
    print(f"Questions generated: {len(questions)}")
    print(f"- {output_path}")


if __name__ == "__main__":
    main()

