from pathlib import Path
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path("services/api").resolve()))

import web_app
import document_language as dl

client = TestClient(web_app.app, raise_server_exceptions=False)

pdf = "test-multilingual.pdf"

for lang in ["auto", "ro", "en", "fr", "de", "ru"]:
    r = client.post("/document-language", json={"pdf": pdf, "language": lang})
    print("set", lang, "=>", r.status_code, r.json().get("document_language"))

r = client.get(f"/document-language?pdf={pdf}")
print("get:", r.status_code, r.json())

tests = [
    ("ro-RO", "Acesta este un text cu greseli si functionare incorecta."),
    ("en-US", "This is a text with erors and a incorect valve."),
    ("fr", "Ceci est un text avec des erors."),
    ("de-DE", "Das ist ein Text mit Fehlern und einem inkorekten System."),
    ("ru-RU", "Это текст с ашибками."),
]

for language, text in tests:
    r = client.post("/check-ocr-languagetool", json={"language": language, "text": text})
    data = r.json()
    print("")
    print(language, "status:", r.status_code, "ok:", data.get("ok"), "matches:", len(data.get("matches", [])))
    print("message:", data.get("message"))
