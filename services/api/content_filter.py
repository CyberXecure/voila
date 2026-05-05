from __future__ import annotations

import re


NON_STUDY_SECTION_PATTERNS = [
    # Romanian
    "prefață",
    "prefata",
    "cuvânt înainte",
    "cuvant inainte",
    "postfață",
    "postfata",
    "cuprins",
    "bibliografie",
    "referințe",
    "referinte",
    "mulțumiri",
    "multumiri",
    "index",
    "coperta",
    "drepturi de autor",

    # English
    "preface",
    "foreword",
    "afterword",
    "postscript",
    "contents",
    "table of contents",
    "bibliography",
    "references",
    "further reading",
    "acknowledgements",
    "acknowledgments",
    "index",
    "copyright",
    "publisher",
    "publishing",
    "reprinted",
    "isbn",
    "library of congress",
    "british library",
    "all rights reserved",
    "permissions",
    "trademark",
    "elsevier",
    "butterworth",
    "heinemann",
    "linacre house",
    "wheeler road",
    "burlington",
    "oxford",
]


GENERIC_QUESTION_PATTERNS = [
    "name one key point supported by the source text",
    "what is one key point supported by the source text",
    "what is mentioned in the source text",
    "summarize one point from",
    "what is one detail from",
    "identify one statement from",
]


def normalize(value: str) -> str:
    value = str(value or "").lower()
    value = value.replace("ă", "a")
    value = value.replace("â", "a")
    value = value.replace("î", "i")
    value = value.replace("ș", "s")
    value = value.replace("ş", "s")
    value = value.replace("ț", "t")
    value = value.replace("ţ", "t")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def is_non_study_title(value: str) -> bool:
    text = normalize(value)

    if not text:
        return False

    exact_titles = {
        "preface",
        "foreword",
        "afterword",
        "postscript",
        "contents",
        "table of contents",
        "bibliography",
        "references",
        "further reading",
        "acknowledgements",
        "acknowledgments",
        "index",
        "prefata",
        "cuvant inainte",
        "postfata",
        "cuprins",
        "bibliografie",
        "referinte",
        "multumiri",
    }

    if text in exact_titles:
        return True

    if text.startswith("index "):
        return True

    if text.startswith("references "):
        return True

    if text.startswith("bibliography "):
        return True

    if text.startswith("contents "):
        return True

    return False


def is_non_study_text(value: str) -> bool:
    text = normalize(value)

    if not text:
        return False

    hits = 0

    for pattern in NON_STUDY_SECTION_PATTERNS:
        if normalize(pattern) in text:
            hits += 1

    # One very strong marker is enough for publisher/copyright/front matter.
    strong_markers = [
        "copyright",
        "all rights reserved",
        "isbn",
        "library of congress",
        "british library",
        "elsevier",
        "butterworth",
        "heinemann",
        "reprinted",
        "table of contents",
        "bibliography",
        "references",
        "further reading",
    ]

    for marker in strong_markers:
        if marker in text:
            return True

    # Multiple weaker markers usually indicate front/back matter.
    if hits >= 2:
        return True

    return False


def is_generic_question(question: str) -> bool:
    text = normalize(question)

    for pattern in GENERIC_QUESTION_PATTERNS:
        if normalize(pattern) in text:
            return True

    return False


def should_exclude_study_item(
    *,
    title: str = "",
    question: str = "",
    answer: str = "",
    source_text: str = "",
    lesson_id: str = "",
) -> bool:
    if is_non_study_title(title):
        return True

    if is_generic_question(question):
        return True

    combined = " ".join(
        [
            str(title or ""),
            str(question or ""),
            str(answer or ""),
            str(source_text or ""),
            str(lesson_id or ""),
        ]
    )

    if is_non_study_text(combined):
        return True

    return False

