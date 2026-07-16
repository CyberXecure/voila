from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


TECHNICAL_TERMS = {
    "steam trap": "A device used in steam systems to discharge condensate while limiting the loss of live steam.",
    "pumping trap": "A trap arrangement that uses steam pressure to drive accumulated water out of the trap.",
    "vacuum trap": "A trap associated with condensate removal under vacuum or low pressure conditions.",
    "non-return valve": "A valve that allows flow in one direction and prevents reverse flow.",
    "exhaust valve": "A valve used to release or exhaust fluid or vapour from a chamber.",
    "steam valve": "A valve that admits or controls steam flow.",
    "float": "A buoyant component that rises and falls with the liquid level.",
    "collar": "A fitted ring or shoulder used to engage or limit movement.",
    "magnet": "A component used to hold or release a mechanism by magnetic attraction.",
    "spring": "An elastic component that stores mechanical energy.",
    "spindle": "A shaft or stem used to transmit motion in a valve or mechanism.",
    "strainer": "A device used to retain larger foreign objects that could cause damage or blockage.",
    "filter": "A device intended to prevent unwanted solids from passing further through a system.",
    "basket strainer": "A strainer using a perforated metal or wire basket inside a container.",
    "perforated plate": "A plate containing holes through which fluid passes while larger solids are retained.",
    "bilge system": "A system used to collect and remove water or fluids from bilge spaces.",
    "knife edge strainer": "A strainer with discs and thin fingers that remove trapped particles by rotation.",
    "cartridge filter": "A filter using removable or renewable cartridge elements.",
    "magnetic filter": "A filter that captures ferrous wear particles using magnetic attraction.",
    "wire mesh": "A mesh made from wire, used as a straining or filtering medium.",
    "filter cartridge": "A replaceable or cleanable filter element.",
    "bimetallic steam trap": "A thermostatic steam trap using bimetallic elements that respond to temperature.",
    "thermodynamic type": "A steam trap type whose operation may be checked by its characteristic clicking action.",
    "thermostatic traps": "Steam traps using temperature-sensitive elements.",
    "mechanical traps": "Steam traps using mechanical components such as floats or buckets.",
}


KEYWORDS = [
    "should",
    "must",
    "advisable",
    "essential",
    "checked",
    "prevent",
    "protect",
    "operate",
    "fails",
    "wastes",
    "installed",
    "consists",
    "used",
    "cleaning",
    "renewed",
]


def get_text(lesson: dict) -> str:
    return str(lesson.get("source_text") or lesson.get("text_preview") or "").strip()


def split_sentences(text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", text).strip()
    if not compact:
        return []

    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", compact)
    return [part.strip() for part in parts if len(part.strip()) > 25]


def find_terms(text: str) -> list[dict]:
    lower = text.lower()
    found = []

    for term, definition in TECHNICAL_TERMS.items():
        pattern = r"\b" + re.escape(term.lower()) + r"s?\b"
        if re.search(pattern, lower):
            found.append(
                {
                    "term": term,
                    "definition": definition,
                }
            )

    return found


def key_points(text: str, limit: int = 7) -> list[str]:
    sentences = split_sentences(text)
    selected = []

    for sentence in sentences:
        lower = sentence.lower()
        if any(keyword in lower for keyword in KEYWORDS):
            selected.append(sentence)

        if len(selected) >= limit:
            break

    if not selected:
        selected = sentences[:limit]

    return selected[:limit]


def learning_objectives(lesson: dict, terms: list[dict]) -> list[str]:
    title = str(lesson.get("title") or "this lesson").lower()

    objectives = [
        f"Identify the main purpose of {title}.",
        "Recognize the main components, devices or maintenance actions described in the source text.",
        "Extract key technical ideas without translating or rewriting the original source language.",
    ]

    if terms:
        names = ", ".join(item["term"] for item in terms[:4])
        objectives.append(f"Define key technical terms such as {names}.")

    return objectives


def make_quiz(lesson: dict, terms: list[dict], points: list[str]) -> list[dict]:
    lesson_id = lesson.get("lesson_id")
    title = lesson.get("title")
    pages = lesson.get("source_pdf_pages", [])
    questions = []

    if terms:
        term = terms[0]
        questions.append(
            {
                "lesson_id": lesson_id,
                "question": f"What does '{term['term']}' refer to in the lesson '{title}'?",
                "answer": term["definition"],
                "source_pdf_pages": pages,
                "generation_method": "rule_based_no_ai",
            }
        )

    if points:
        questions.append(
            {
                "lesson_id": lesson_id,
                "question": f"Name one key point supported by the source text in '{title}'.",
                "answer": points[0],
                "source_pdf_pages": pages,
                "generation_method": "rule_based_no_ai",
            }
        )

    figures = lesson.get("figures") or []
    if figures:
        figure = figures[0]
        questions.append(
            {
                "lesson_id": lesson_id,
                "question": f"Which figure is associated with '{title}'?",
                "answer": f"Figure {figure.get('number')}: {figure.get('caption')}",
                "source_pdf_pages": pages,
                "generation_method": "rule_based_no_ai",
            }
        )

    return questions


def make_flashcards(lesson: dict, terms: list[dict]) -> list[dict]:
    cards = []
    lesson_id = lesson.get("lesson_id")
    pages = lesson.get("source_pdf_pages", [])

    for term in terms:
        cards.append(
            {
                "front": term["term"],
                "back": term["definition"],
                "lesson_id": lesson_id,
                "source_pdf_pages": pages,
                "generation_method": "rule_based_no_ai",
            }
        )

    for figure in lesson.get("figures") or []:
        cards.append(
            {
                "front": f"Figure {figure.get('number')}",
                "back": figure.get("caption"),
                "lesson_id": lesson_id,
                "source_pdf_pages": pages,
                "generation_method": "rule_based_no_ai",
            }
        )

    return cards


def write_course(outline: dict, output_path: Path) -> None:
    lines = []

    lines.append(f"# {outline.get('title')}")
    lines.append("")
    lines.append("Generated by Voila! v0.1")
    lines.append("")
    lines.append("Mode: source language, no translation, no AI generation")
    lines.append(f"Source: `{outline.get('source_file')}`")
    lines.append("")

    for lesson in outline.get("lessons", []):
        text = get_text(lesson)
        terms = find_terms(text)
        points = key_points(text)

        lines.append(f"## {lesson.get('lesson_id')} — {lesson.get('title')}")
        lines.append("")
        lines.append(f"Source PDF pages: {', '.join(map(str, lesson.get('source_pdf_pages', [])))}")
        lines.append(f"Word count: {lesson.get('word_count')}")
        lines.append("")

        figures = lesson.get("figures") or []
        if figures:
            lines.append("### Figures")
            lines.append("")
            for figure in figures:
                lines.append(f"- Figure {figure.get('number')}: {figure.get('caption')}")
            lines.append("")

        lines.append("### Learning objectives")
        lines.append("")
        for item in learning_objectives(lesson, terms):
            lines.append(f"- {item}")
        lines.append("")

        lines.append("### Key points extracted from source")
        lines.append("")
        for item in points:
            lines.append(f"- {item}")
        lines.append("")

        if terms:
            lines.append("### Terms found")
            lines.append("")
            for item in terms:
                lines.append(f"- **{item['term']}** — {item['definition']}")
            lines.append("")

        lines.append("### Original source text")
        lines.append("")
        lines.append("```text")
        lines.append(text)
        lines.append("```")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")



# VOILA_V0_7_77_COURSE_GENERATOR_LEARNING_PACK_INTEGRATION_START
def load_learning_pack(path: str | None) -> dict:
    if not path:
        return {}
    pack_path = Path(path)
    if not pack_path.is_file():
        return {}
    try:
        data = json.loads(pack_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def learning_pack_concepts(learning_pack: dict) -> list[dict]:
    concepts = learning_pack.get("concept_summary", {}).get("concepts", [])
    return [item for item in concepts if isinstance(item, dict)] if isinstance(concepts, list) else []


def learning_pack_evidence_items(learning_pack: dict) -> list[dict]:
    items = learning_pack.get("verified_user_evidence", {}).get("items", [])
    return [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []


def append_learning_pack_assets(
    glossary: list[dict],
    quiz: list[dict],
    flashcards: list[dict],
    learning_pack: dict,
) -> None:
    if not learning_pack:
        return

    concepts = learning_pack_concepts(learning_pack)
    evidence_items = learning_pack_evidence_items(learning_pack)

    for concept in concepts:
        term = str(concept.get("term") or "").strip()
        definition = str(concept.get("definition") or concept.get("teaching_note") or "").strip()
        pages = concept.get("source_pdf_pages") or []
        concept_id = str(concept.get("concept_id") or "").strip()
        if not term:
            continue

        glossary.append(
            {
                "term": term,
                "definition": definition or "Concept extracted from the verified document learning pack.",
                "lesson_id": concept_id or "document_learning_pack",
                "source_pdf_pages": pages,
                "generation_method": "v0.7.77_learning_pack_verified_evidence",
                "learning_pack_source": "document_learning_pack.json",
            }
        )

        flashcards.append(
            {
                "front": term,
                "back": definition or "Review this concept in the generated course.",
                "lesson_id": concept_id or "document_learning_pack",
                "source_pdf_pages": pages,
                "generation_method": "v0.7.77_learning_pack_verified_evidence",
                "learning_pack_source": "document_learning_pack.json",
            }
        )

        quiz.append(
            {
                "lesson_id": concept_id or "document_learning_pack",
                "question": f"What should you remember about '{term}' from this document?",
                "answer": definition or "Use the verified document learning pack evidence for this concept.",
                "source_pdf_pages": pages,
                "generation_method": "v0.7.77_learning_pack_verified_evidence",
                "learning_pack_source": "document_learning_pack.json",
            }
        )

    for item in evidence_items[:20]:
        text = str(item.get("verified_evidence_text") or item.get("corrected_text") or "").strip()
        role = str(item.get("confirmed_learning_role") or "verified_evidence").strip()
        review_item_id = str(item.get("review_item_id") or "").strip()
        if not text:
            continue
        quiz.append(
            {
                "lesson_id": review_item_id or "ocr_review_verified_evidence",
                "question": f"Which verified OCR Review evidence was marked as {role}?",
                "answer": text,
                "source_pdf_pages": item.get("source_pdf_pages") or [],
                "generation_method": "v0.7.77_learning_pack_verified_evidence",
                "learning_pack_source": "ocr_review_decisions.applied.json",
            }
        )


def write_learning_pack_course_section(learning_pack: dict, output_path: Path) -> None:
    if not learning_pack:
        return

    concepts = learning_pack_concepts(learning_pack)
    evidence_items = learning_pack_evidence_items(learning_pack)
    lines = [
        "",
        "## Document learning pack integration",
        "",
        "Integration: `v0.7.77 readiness-gated learning pack`",
        f"Learning pack rebuild version: `{learning_pack.get('rebuild_artifact_version')}`",
        f"Document learning status: `{learning_pack.get('quality_gate', {}).get('document_learning_status')}`",
        f"Verified user evidence count: `{learning_pack.get('quality_gate', {}).get('verified_user_evidence_count')}`",
        "",
        "### Verified document concepts",
        "",
    ]

    for concept in concepts[:20]:
        term = concept.get("term")
        definition = concept.get("definition") or concept.get("teaching_note") or ""
        lines.append(f"- **{term}** — {definition}")

    lines.extend(["", "### Verified OCR Review evidence", ""])
    for item in evidence_items[:20]:
        rid = item.get("review_item_id")
        role = item.get("confirmed_learning_role")
        text = item.get("verified_evidence_text") or item.get("corrected_text")
        lines.append(f"- `{rid}` · `{role}` — {text}")

    with output_path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


# VOILA_V0_7_77_COURSE_GENERATOR_LEARNING_PACK_INTEGRATION_END


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! rule-based course generator")
    parser.add_argument("normalized_outline_json", help="Path to course_outline.normalized.json")
    parser.add_argument("--learning-pack-json", default=None, help="Optional readiness-gated document_learning_pack.json")

    args = parser.parse_args()
    outline_path = Path(args.normalized_outline_json).resolve()

    if not outline_path.exists():
        raise FileNotFoundError(f"Normalized outline not found: {outline_path}")

    outline = json.loads(outline_path.read_text(encoding="utf-8"))
    learning_pack = load_learning_pack(args.learning_pack_json)
    output_dir = outline_path.parent

    glossary = []
    quiz = []
    flashcards = []

    seen_glossary = set()

    for lesson in outline.get("lessons", []):
        text = get_text(lesson)
        terms = find_terms(text)
        points = key_points(text)

        for term in terms:
            key = (term["term"], lesson.get("lesson_id"))
            if key not in seen_glossary:
                seen_glossary.add(key)
                glossary.append(
                    {
                        "term": term["term"],
                        "definition": term["definition"],
                        "lesson_id": lesson.get("lesson_id"),
                        "source_pdf_pages": lesson.get("source_pdf_pages", []),
                        "generation_method": "rule_based_no_ai",
                    }
                )

        quiz.extend(make_quiz(lesson, terms, points))
        flashcards.extend(make_flashcards(lesson, terms))

    course_path = output_dir / "course.md"
    append_learning_pack_assets(glossary, quiz, flashcards, learning_pack)

    glossary_path = output_dir / "glossary.json"
    quiz_path = output_dir / "quiz.json"
    flashcards_path = output_dir / "flashcards.json"

    write_course(outline, course_path)
    write_learning_pack_course_section(learning_pack, course_path)

    glossary_path.write_text(json.dumps(glossary, ensure_ascii=False, indent=2), encoding="utf-8")
    quiz_path.write_text(json.dumps(quiz, ensure_ascii=False, indent=2), encoding="utf-8")
    flashcards_path.write_text(json.dumps(flashcards, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Voila! course files generated successfully.")
    print(f"- {course_path}")
    print(f"- {glossary_path}")
    print(f"- {quiz_path}")
    print(f"- {flashcards_path}")


if __name__ == "__main__":
    main()
