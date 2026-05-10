
from __future__ import annotations

from pathlib import Path
import json
import re


SUPPORTED_LANGUAGES = {
    "auto": {
        "label": "Auto detect",
        "ocr_lang": "eng",
        "languagetool_lang": "auto",
        "study_lang": "auto",
    },
    "ro": {
        "label": "Română",
        "ocr_lang": "ron+eng",
        "languagetool_lang": "ro-RO",
        "study_lang": "ro",
    },
    "en": {
        "label": "English",
        "ocr_lang": "eng",
        "languagetool_lang": "en-US",
        "study_lang": "en",
    },
    "fr": {
        "label": "Français",
        "ocr_lang": "fra+eng",
        "languagetool_lang": "fr",
        "study_lang": "fr",
    },
    "de": {
        "label": "Deutsch",
        "ocr_lang": "deu+eng",
        "languagetool_lang": "de-DE",
        "study_lang": "de",
    },
    "ru": {
        "label": "Русский",
        "ocr_lang": "rus+eng",
        "languagetool_lang": "ru-RU",
        "study_lang": "ru",
    },
    "it": {
        "label": "Italiano",
        "ocr_lang": "ita+eng",
        "languagetool_lang": "it",
        "study_lang": "it",
    },
    "es": {
        "label": "Español",
        "ocr_lang": "spa+eng",
        "languagetool_lang": "es",
        "study_lang": "es",
    },
    "pt": {
        "label": "Português",
        "ocr_lang": "por+eng",
        "languagetool_lang": "pt",
        "study_lang": "pt",
    },
}


def normalize_language(value: str | None) -> str:
    value = str(value or "").strip().lower()

    aliases = {
        "romanian": "ro",
        "romana": "ro",
        "română": "ro",
        "ron": "ro",
        "ro-ro": "ro",
        "english": "en",
        "eng": "en",
        "en-us": "en",
        "en-gb": "en",
        "french": "fr",
        "fra": "fr",
        "fr-fr": "fr",
        "german": "de",
        "deu": "de",
        "de-de": "de",
        "russian": "ru",
        "rus": "ru",
        "ru-ru": "ru",
        "italian": "it",
        "italiano": "it",
        "ita": "it",
        "it-it": "it",
        "spanish": "es",
        "espanol": "es",
        "español": "es",
        "spa": "es",
        "es-es": "es",
        "portuguese": "pt",
        "portugues": "pt",
        "português": "pt",
        "por": "pt",
        "pt-pt": "pt",
        "pt-br": "pt",
    }

    value = aliases.get(value, value)

    if value not in SUPPORTED_LANGUAGES:
        return "auto"

    return value


def detect_language_from_text(text: str) -> str:
    value = str(text or "").lower()

    if re.search(r"[а-яё]", value, re.IGNORECASE):
        return "ru"

    scores = {
        "ro": 0,
        "en": 0,
        "fr": 0,
        "de": 0,
        "it": 0,
        "es": 0,
        "pt": 0,
    }

    if re.search(r"[ăâîșşțţ]", value, re.IGNORECASE):
        scores["ro"] += 5

    if re.search(r"[éèêëàâîïôùûçœ]", value, re.IGNORECASE):
        scores["fr"] += 4

    if re.search(r"[äöüß]", value, re.IGNORECASE):
        scores["de"] += 4

    if re.search(r"[àèéìíîòóùú]", value, re.IGNORECASE):
        scores["it"] += 3

    if re.search(r"[áéíóúñü¿¡]", value, re.IGNORECASE):
        scores["es"] += 3

    if re.search(r"[ãõçáàâéêíóôú]", value, re.IGNORECASE):
        scores["pt"] += 3

    markers = {
        "ro": ["pentru", "este", "sunt", "care", "prin", "din", "funcție", "capitolul", "figura"],
        "en": ["the", "and", "with", "from", "figure", "chapter", "system", "pressure", "temperature"],
        "fr": ["pour", "avec", "dans", "figure", "chapitre", "pression", "température", "système"],
        "de": ["und", "mit", "der", "die", "das", "abbildung", "kapitel", "druck", "temperatur", "system"],
        "it": ["per", "con", "della", "delle", "figura", "capitolo", "pressione", "temperatura", "sistema"],
        "es": ["para", "con", "del", "de la", "figura", "capítulo", "presión", "temperatura", "sistema"],
        "pt": ["para", "com", "do", "da", "figura", "capítulo", "pressão", "temperatura", "sistema"],
    }

    for lang, words in markers.items():
        for word in words:
            if word in value:
                scores[lang] += 1

    best = max(scores, key=lambda key: scores[key])

    if scores[best] <= 0:
        return "en"

    return best


def output_dir(project_root: Path | str, pdf_name: str) -> Path:
    project_root = Path(project_root)
    return project_root / "data" / "output" / Path(str(pdf_name or "")).stem


def config_path(project_root: Path | str, pdf_name: str) -> Path:
    return output_dir(project_root, pdf_name) / "document_language.json"


def get_document_language(project_root: Path | str, pdf_name: str) -> dict:
    path = config_path(project_root, pdf_name)

    language = "auto"

    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            language = normalize_language(data.get("document_language"))
        except Exception:
            language = "auto"

    profile = SUPPORTED_LANGUAGES[language].copy()

    return {
        "ok": True,
        "pdf": str(pdf_name or ""),
        "document_language": language,
        **profile,
        "supported": SUPPORTED_LANGUAGES,
    }


def set_document_language(project_root: Path | str, pdf_name: str, language: str) -> dict:
    language = normalize_language(language)
    out_dir = output_dir(project_root, pdf_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    profile = SUPPORTED_LANGUAGES[language].copy()

    data = {
        "pdf": str(pdf_name or ""),
        "document_language": language,
        **profile,
    }

    config_path(project_root, pdf_name).write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        "ok": True,
        **data,
        "supported": SUPPORTED_LANGUAGES,
    }


def get_ocr_lang(project_root: Path | str, pdf_name: str, fallback_text: str = "") -> str:
    cfg = get_document_language(project_root, pdf_name)
    lang = cfg.get("document_language") or "auto"

    if lang == "auto":
        lang = detect_language_from_text(fallback_text)

    return SUPPORTED_LANGUAGES.get(lang, SUPPORTED_LANGUAGES["en"])["ocr_lang"]


def get_languagetool_lang(project_root: Path | str, pdf_name: str, fallback_text: str = "") -> str:
    cfg = get_document_language(project_root, pdf_name)
    lang = cfg.get("document_language") or "auto"

    if lang == "auto":
        lang = detect_language_from_text(fallback_text)

    return SUPPORTED_LANGUAGES.get(lang, SUPPORTED_LANGUAGES["en"])["languagetool_lang"]


# VOILA_QUESTION_TEMPLATES_V1

QUESTION_TEMPLATES = {
    "ro": {
        "technical_point": "Ce idee tehnică precizează sursa despre {concept}?",
        "answer_prefix": "Sursa precizează că",
    },
    "en": {
        "technical_point": "What technical point does the source state about {concept}?",
        "answer_prefix": "The source states that",
    },
    "fr": {
        "technical_point": "Quel point technique la source indique-t-elle à propos de {concept} ?",
        "answer_prefix": "La source indique que",
    },
    "de": {
        "technical_point": "Welchen technischen Punkt nennt die Quelle zu {concept}?",
        "answer_prefix": "Die Quelle gibt an, dass",
    },
    "ru": {
        "technical_point": "Какой технический аспект источник указывает относительно {concept}?",
        "answer_prefix": "Источник указывает, что",
    },
    "it": {
        "technical_point": "Quale punto tecnico indica la fonte su {concept}?",
        "answer_prefix": "La fonte indica che",
    },
    "es": {
        "technical_point": "¿Qué punto técnico indica la fuente sobre {concept}?",
        "answer_prefix": "La fuente indica que",
    },
    "pt": {
        "technical_point": "Que ponto técnico a fonte indica sobre {concept}?",
        "answer_prefix": "A fonte indica que",
    },
}


def get_question_template(project_root: Path | str, pdf_name: str, fallback_text: str = "") -> dict:
    cfg = get_document_language(project_root, pdf_name)
    lang = cfg.get("document_language") or "auto"

    if lang == "auto":
        lang = detect_language_from_text(fallback_text)

    return QUESTION_TEMPLATES.get(lang, QUESTION_TEMPLATES["en"])
