
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
    }

    if re.search(r"[ăâîșşțţ]", value, re.IGNORECASE):
        scores["ro"] += 5

    if re.search(r"[éèêëàâîïôùûçœ]", value, re.IGNORECASE):
        scores["fr"] += 4

    if re.search(r"[äöüß]", value, re.IGNORECASE):
        scores["de"] += 4

    markers = {
        "ro": ["pentru", "este", "sunt", "care", "prin", "din", "funcție", "capitolul", "figura"],
        "en": ["the", "and", "with", "from", "figure", "chapter", "system", "pressure", "temperature"],
        "fr": ["pour", "avec", "dans", "figure", "chapitre", "pression", "température", "système"],
        "de": ["und", "mit", "der", "die", "das", "abbildung", "kapitel", "druck", "temperatur", "system"],
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
