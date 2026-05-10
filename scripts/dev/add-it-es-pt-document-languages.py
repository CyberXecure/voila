from pathlib import Path

path = Path("services/api/document_language.py")
text = path.read_text(encoding="utf-8")

# Add Italian / Spanish / Portuguese language profiles.
insert_after = '''    "ru": {
        "label": "Русский",
        "ocr_lang": "rus+eng",
        "languagetool_lang": "ru-RU",
        "study_lang": "ru",
    },
'''

insert_block = '''    "ru": {
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
'''

if '"it": {' not in text:
    if insert_after not in text:
        raise SystemExit("Nu găsesc blocul ru în SUPPORTED_LANGUAGES.")
    text = text.replace(insert_after, insert_block)

# Add aliases.
alias_marker = '''        "russian": "ru",
        "rus": "ru",
        "ru-ru": "ru",
'''

alias_replacement = '''        "russian": "ru",
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
'''

if '"italian": "it"' not in text:
    if alias_marker not in text:
        raise SystemExit("Nu găsesc alias_marker.")
    text = text.replace(alias_marker, alias_replacement)

# Expand score languages.
text = text.replace(
'''    scores = {
        "ro": 0,
        "en": 0,
        "fr": 0,
        "de": 0,
    }
''',
'''    scores = {
        "ro": 0,
        "en": 0,
        "fr": 0,
        "de": 0,
        "it": 0,
        "es": 0,
        "pt": 0,
    }
'''
)

# Add accent hints.
if 'scores["it"] += 3' not in text:
    text = text.replace(
'''    if re.search(r"[äöüß]", value, re.IGNORECASE):
        scores["de"] += 4
''',
'''    if re.search(r"[äöüß]", value, re.IGNORECASE):
        scores["de"] += 4

    if re.search(r"[àèéìíîòóùú]", value, re.IGNORECASE):
        scores["it"] += 3

    if re.search(r"[áéíóúñü¿¡]", value, re.IGNORECASE):
        scores["es"] += 3

    if re.search(r"[ãõçáàâéêíóôú]", value, re.IGNORECASE):
        scores["pt"] += 3
'''
    )

# Expand markers.
old_markers = '''        "de": ["und", "mit", "der", "die", "das", "abbildung", "kapitel", "druck", "temperatur", "system"],
'''

new_markers = '''        "de": ["und", "mit", "der", "die", "das", "abbildung", "kapitel", "druck", "temperatur", "system"],
        "it": ["per", "con", "della", "delle", "figura", "capitolo", "pressione", "temperatura", "sistema"],
        "es": ["para", "con", "del", "de la", "figura", "capítulo", "presión", "temperatura", "sistema"],
        "pt": ["para", "com", "do", "da", "figura", "capítulo", "pressão", "temperatura", "sistema"],
'''

if '"it": ["per"' not in text:
    if old_markers not in text:
        raise SystemExit("Nu găsesc markerul de markers.")
    text = text.replace(old_markers, new_markers)

path.write_text(text, encoding="utf-8")
print("OK: document_language.py extended with Italian, Spanish, Portuguese.")
