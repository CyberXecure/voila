from pathlib import Path

path = Path("services/api/static/ocr_review_monaco.js")
text = path.read_text(encoding="utf-8")

# Extend labels.
text = text.replace(
'''    de: "Deutsch",
    ru: "Русский"
''',
'''    de: "Deutsch",
    ru: "Русский",
    it: "Italiano",
    es: "Español",
    pt: "Português"
'''
)

# Extend LanguageTool map.
text = text.replace(
'''    de: "de-DE",
    ru: "ru-RU"
''',
'''    de: "de-DE",
    ru: "ru-RU",
    it: "it",
    es: "es",
    pt: "pt"
'''
)

# Extend detector scores.
text = text.replace(
'''    const scores = { ro: 0, en: 0, fr: 0, de: 0 };
''',
'''    const scores = { ro: 0, en: 0, fr: 0, de: 0, it: 0, es: 0, pt: 0 };
'''
)

# Add accent hints.
if "scores.it += 3" not in text:
    text = text.replace(
'''    if (/[äöüß]/i.test(text)) scores.de += 4;
''',
'''    if (/[äöüß]/i.test(text)) scores.de += 4;
    if (/[àèéìíîòóùú]/i.test(text)) scores.it += 3;
    if (/[áéíóúñü¿¡]/i.test(text)) scores.es += 3;
    if (/[ãõçáàâéêíóôú]/i.test(text)) scores.pt += 3;
'''
    )

# Extend markers.
old = '''      de: ["und", "mit", "der", "die", "das", "abbildung", "kapitel", "druck", "temperatur", "system"]
'''

new = '''      de: ["und", "mit", "der", "die", "das", "abbildung", "kapitel", "druck", "temperatur", "system"],
      it: ["per", "con", "della", "delle", "figura", "capitolo", "pressione", "temperatura", "sistema"],
      es: ["para", "con", "del", "de la", "figura", "capítulo", "presión", "temperatura", "sistema"],
      pt: ["para", "com", "do", "da", "figura", "capítulo", "pressão", "temperatura", "sistema"]
'''

if 'it: ["per"' not in text:
    if old not in text:
        raise SystemExit("Nu găsesc markers JS.")
    text = text.replace(old, new)

# Extend aliases.
alias_old = '''      "ru-ru": "ru",
      "rus": "ru"
'''

alias_new = '''      "ru-ru": "ru",
      "rus": "ru",
      "it-it": "it",
      "ita": "it",
      "es-es": "es",
      "spa": "es",
      "pt-pt": "pt",
      "pt-br": "pt",
      "por": "pt"
'''

if '"it-it": "it"' not in text:
    if alias_old not in text:
        raise SystemExit("Nu găsesc aliases JS.")
    text = text.replace(alias_old, alias_new)

path.write_text(text, encoding="utf-8")
print("OK: Monaco OCR language selector extended with IT/ES/PT.")
