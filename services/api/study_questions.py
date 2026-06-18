
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


QUESTION_TYPE_TEMPLATES = {
    "en": {
        "definition": "How does the source define “{concept}”?",
        "components": "What parts or components does the source describe for “{concept}”?",
        "purpose": "What purpose does the source describe for “{concept}”?",
        "requirement": "What requirement or recommendation does the source state for “{concept}”?",
        "condition": "Under what condition or situation does the source describe “{concept}”?",
        "cause_effect": "What cause, reason, or effect does the source describe for “{concept}”?",
        "comparison": "What comparison does the source make about “{concept}”?",
        "example": "What example does the source give for “{concept}”?",
        "process": "What process or sequence does the source describe for “{concept}”?",
        "numeric_check": "What numerical detail or measurement does the source give for “{concept}”?",
        "visual_interpretation": "What figure or table detail does the source provide for “{concept}”?",
        "technical_fact": "What technical point does the source state about “{concept}”?",
        "important_idea": "What important idea does the source support about “{concept}”?",
    },
    "ro": {
        "definition": "Cum definește sursa „{concept}”?",
        "components": "Ce părți sau componente descrie sursa pentru „{concept}”?",
        "purpose": "Ce scop sau rol descrie sursa pentru „{concept}”?",
        "requirement": "Ce cerință sau recomandare menționează sursa pentru „{concept}”?",
        "condition": "În ce condiție sau situație descrie sursa „{concept}”?",
        "cause_effect": "Ce cauză, motiv sau efect descrie sursa pentru „{concept}”?",
        "comparison": "Ce comparație face sursa despre „{concept}”?",
        "example": "Ce exemplu oferă sursa pentru „{concept}”?",
        "process": "Ce proces sau secvență descrie sursa pentru „{concept}”?",
        "numeric_check": "Ce detaliu numeric sau măsurătoare oferă sursa pentru „{concept}”?",
        "visual_interpretation": "Ce detaliu din figură sau tabel oferă sursa pentru „{concept}”?",
        "technical_fact": "Ce precizare tehnică face sursa despre „{concept}”?",
        "important_idea": "Ce idee importantă susține sursa despre „{concept}”?",
    },
    "ru": {
        "definition": "Как источник определяет «{concept}»?",
        "components": "Какие части или компоненты источник описывает для «{concept}»?",
        "purpose": "Какую цель или функцию источник описывает для «{concept}»?",
        "requirement": "Какое требование или рекомендацию источник указывает для «{concept}»?",
        "condition": "При каком условии или в какой ситуации источник описывает «{concept}»?",
        "cause_effect": "Какую причину, основание или следствие источник описывает для «{concept}»?",
        "comparison": "Какое сравнение источник делает относительно «{concept}»?",
        "example": "Какой пример источник приводит для «{concept}»?",
        "process": "Какой процесс или последовательность источник описывает для «{concept}»?",
        "numeric_check": "Какую числовую деталь или измерение источник приводит для «{concept}»?",
        "visual_interpretation": "Какую деталь рисунка или таблицы источник приводит для «{concept}»?",
        "technical_fact": "Какой технический момент источник указывает относительно «{concept}»?",
        "important_idea": "Какую важную идею источник подтверждает о «{concept}»?",
    },
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

    if " — " in concept:
        concept = concept.split(" — ", 1)[1]

    concept = re.sub(
        r"\([^)]*\b(credit|source|wikimedia|commons|nasa|ames|department of energy|modification of work)\b[^)]*\)",
        "",
        concept,
        flags=re.IGNORECASE,
    )
    concept = re.sub(r"\bcredit\s+[a-z]?\s*:.*$", "", concept, flags=re.IGNORECASE)
    concept = re.sub(r"\bmodification of work by\b.*$", "", concept, flags=re.IGNORECASE)

    concept = concept.rstrip(".?").strip()
    concept = concept.strip("'\"“”‘’ .,:;—–-()[]{}")
    concept = re.sub(r"[\)\]\}]+$", "", concept).strip(" .,:;—–-")

    lower = concept.lower()

    if not concept:
        return ""

    if any(
        phrase in lower
        for phrase in [
            "department of energy",
            "wikimedia commons",
            "nasa/ames",
            "ames research center",
            "modification of work",
            "credit a",
            "credit b",
            "credit c",
            "courtesy of",
        ]
    ):
        return ""

    if re.search(r"^\s*(fig\.|figure|table|caption)\b", lower):
        return ""

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


def question_type(question: dict, raw_question: str) -> str:
    explicit = str(question.get("question_type") or "").strip().lower()
    if explicit:
        return explicit

    raw = str(raw_question or "").strip().lower()

    if raw.startswith("how does the source define") or "define" in raw:
        return "definition"
    if raw.startswith("what purpose"):
        return "purpose"
    if raw.startswith("what requirement"):
        return "requirement"
    if raw.startswith("under what condition"):
        return "condition"
    if "comparison" in raw or "compare" in raw:
        return "comparison"
    if "example" in raw:
        return "example"
    if "process" in raw or "sequence" in raw:
        return "process"
    if "numerical" in raw or "measurement" in raw:
        return "numeric_check"
    if "figure" in raw or "table" in raw:
        return "visual_interpretation"

    return "technical_fact"


def localized_question_template(language: str, qtype: str) -> str:
    templates = QUESTION_TYPE_TEMPLATES.get(language) or QUESTION_TYPE_TEMPLATES["en"]
    return (
        templates.get(qtype)
        or templates.get("technical_fact")
        or QUESTION_TEMPLATES.get(language)
        or QUESTION_TEMPLATES["en"]
    )


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
    qtype = question_type(question, raw_question)

    if concept:
        template = localized_question_template(lang, qtype)
        return template.format(concept=concept)

    return raw_question
