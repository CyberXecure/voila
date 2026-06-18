
from __future__ import annotations

from pathlib import Path
import re


QUESTION_TEMPLATES = {
    "ro": "Ce idee importantă susține sursa despre „{concept}”?",
    "en": "What important idea does the source support about “{concept}”?",
    "fr": "Quelle idée importante la source soutient-elle à propos de « {concept} » ?",
    "de": "Welche wichtige Idee unterstützt die Quelle zu „{concept}“?",
    "ru": "Какую важную идею источник поддерживает относительно «{concept}»?",
    "it": "Quale idea importante sostiene la fonte su “{concept}”?",
    "es": "¿Qué idea importante sostiene la fuente sobre «{concept}»?",
    "pt": "Que ideia importante a fonte sustenta sobre “{concept}”?",
}


LEGACY_PATTERNS = [
    r"^What technical point does the source state about\s+(.+?)\??$",
    r"^Under what condition or operating situation does the source describe\s+(.+?)\??$",
    r"^Name one key point supported by the source text in\s+['\"“”‘’](.+?)['\"“”‘’]\.?$",
    r"^Name one key point supported by the source text in\s+(.+?)\.?$",
    r"^What does the source state about\s+(.+?)\??$",
    r"^What does the text say about\s+(.+?)\??$",
    r"^What is stated about\s+(.+?)\??$",
    r"^What is the source saying about\s+(.+?)\??$",
]


def _clean_concept(value: str) -> str:
    concept = str(value or "").strip()
    concept = concept.rstrip(".?").strip()
    concept = concept.strip("'\"“”‘’")
    return concept


def extract_concept(question: dict) -> str:
    raw_question = str(question.get("question") or question.get("prompt") or "").strip()

    for pattern in LEGACY_PATTERNS:
        match = re.match(pattern, raw_question, flags=re.IGNORECASE)

        if match:
            concept = _clean_concept(match.group(1))
            if concept:
                return concept

    for key in [
        "concept_title",
        "lesson_title",
        "title",
        "concept",
        "concept_id",
        "lesson_id",
    ]:
        value = _clean_concept(question.get(key) or "")
        if value:
            return value

    return ""


def document_language(project_root: Path | str, pdf_name: str, fallback_text: str = "") -> str:
    try:
        import document_language as dl

        cfg = dl.get_document_language(project_root, pdf_name)
        lang = str(cfg.get("document_language") or "auto")

        if lang == "auto":
            lang = dl.detect_language_from_text(fallback_text)

        if lang in QUESTION_TEMPLATES:
            return lang
    except Exception:
        pass

    return "en"


def ui_language(project_root: Path | str) -> str:
    try:
        import i18n

        lang = str(i18n.get_ui_language(project_root).get("ui_language") or "en")
        if lang in QUESTION_TEMPLATES:
            return lang
    except Exception:
        pass

    return "en"


def build_study_question(
    project_root: Path | str,
    pdf_name: str,
    question: dict,
) -> str:
    if not isinstance(question, dict):
        return ""

    raw_question = str(question.get("question") or question.get("prompt") or "").strip()
    concept = extract_concept(question)

    fallback_text = " ".join(
        str(question.get(key) or "")
        for key in ["source_text", "answer", "question", "concept_title", "lesson_title"]
    )

    # Display language follows the UI language, not the document language.
    # The source answer/content remains in the original document language.
    lang = ui_language(project_root)

    if concept:
        template = QUESTION_TEMPLATES.get(lang, QUESTION_TEMPLATES["en"])
        return template.format(concept=concept)

    return raw_question
