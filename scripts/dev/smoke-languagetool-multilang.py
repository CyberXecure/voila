from pathlib import Path
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path("services/api").resolve()))

import web_app
import document_language as dl

client = TestClient(web_app.app, raise_server_exceptions=False)

print("Supported languages:")
for key, value in dl.SUPPORTED_LANGUAGES.items():
    print("-", key, value["label"], value["ocr_lang"], value["languagetool_lang"])

tests = [
    ("ro-RO", "Acesta este un text cu greseli si functionare incorecta."),
    ("en-US", "This is a text with erors and a incorect valve."),
    ("fr", "Ceci est un text avec des erors."),
    ("de-DE", "Das ist ein Text mit Fehlern und einem inkorekten System."),
    ("ru-RU", "Это текст с ашибками."),
    ("it", "Questo e un testo con erori."),
    ("es", "Este es un texto con erores."),
    ("pt", "Este e um texto com erors."),
]

for language, text in tests:
    r = client.post("/check-ocr-languagetool", json={"language": language, "text": text})
    data = r.json()
    print("")
    print(language, "status:", r.status_code, "ok:", data.get("ok"), "matches:", len(data.get("matches", [])))
    print("message:", data.get("message"))
