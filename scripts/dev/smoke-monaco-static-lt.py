from pathlib import Path
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path("services/api").resolve()))

import web_app

client = TestClient(web_app.app, raise_server_exceptions=False)

pdf = "Manualul Instalatiilor Electrice.pdf"

r = client.get(f"/review-ocr-corrected?pdf={pdf}&page=41")
print("review status:", r.status_code)
print("has monaco js:", "/voila-static/ocr_review_monaco.js" in r.text)
print("has monaco css:", "/voila-static/ocr_review_monaco.css" in r.text)

r = client.get("/voila-static/ocr_review_monaco.js")
print("js status:", r.status_code, r.headers.get("content-type"), len(r.text))

r = client.get("/voila-static/ocr_review_monaco.css")
print("css status:", r.status_code, r.headers.get("content-type"), len(r.text))

r = client.post(
    "/check-ocr-languagetool",
    json={
        "language": "ro-RO",
        "text": "Acesta este un text cu greseli si functionare incorecta."
    },
)

print("lt status:", r.status_code)
print("lt content-type:", r.headers.get("content-type"))
print("lt raw:", r.text[:1200])

try:
    print("lt json:", r.json())
except Exception as exc:
    print("lt json parse failed:", exc)
