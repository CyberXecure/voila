from pathlib import Path
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path("services/api").resolve()))

import web_app

client = TestClient(web_app.app, raise_server_exceptions=False)

pdf = "Manualul Instalatiilor Electrice.pdf"

tests = [
    f"/review-ocr-corrected?pdf={pdf}&page=41",
    f"/ocr-page-image?pdf={pdf}&page=41&zoom=1.2",
]

for url in tests:
    r = client.get(url)
    print(url)
    print("status:", r.status_code)
    print("content-type:", r.headers.get("content-type"))
    print("length:", len(r.content))
    print()
