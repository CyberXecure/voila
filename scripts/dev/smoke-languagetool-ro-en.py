from pathlib import Path
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path("services/api").resolve()))

import web_app

client = TestClient(web_app.app, raise_server_exceptions=False)

tests = [
    {
        "language": "ro-RO",
        "text": "Acesta este un text cu greseli si functionare incorecta."
    },
    {
        "language": "en-US",
        "text": "This is a text with erors and a incorect valve."
    },
]

for item in tests:
    r = client.post("/check-ocr-languagetool", json=item)
    data = r.json()
    print("")
    print("language:", item["language"])
    print("status:", r.status_code)
    print("ok:", data.get("ok"))
    print("matches:", len(data.get("matches", [])))
    print("message:", data.get("message"))
    for m in data.get("matches", [])[:3]:
        print("-", m.get("message"), "=>", m.get("replacements", [])[:3])
