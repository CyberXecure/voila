import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path("services/api").resolve()))

import web_app

client = TestClient(web_app.app, raise_server_exceptions=False)

pdf = "Manualul Instalatiilor Electrice.pdf"

tests = [
    ("home", "/"),
    ("quick_tools", "/quick-tools"),
    ("course_tools", f"/course-tools?pdf={pdf}"),
    ("view_course", f"/view-course?pdf={pdf}"),
    ("review_ocr_text", f"/review-ocr-text?pdf={pdf}&page=15"),
    ("review_concepts", f"/review-concepts?pdf={pdf}"),
]

for name, url in tests:
    response = client.get(url)
    body = response.text

    print(name, response.status_code, len(body))
    print("  url:", url)
    print("  quick-tools:", "/quick-tools" in body)
    print("  course-tools:", "/course-tools?pdf=" in body)
    print("  review-ocr:", "/review-ocr-text?pdf=" in body)
    print("  review-concepts:", "/review-concepts?pdf=" in body)

    if response.status_code >= 500:
        print("  ERROR BODY:")
        print(body[:1200])

    print()
