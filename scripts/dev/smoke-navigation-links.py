import sys
from pathlib import Path

sys.path.insert(0, str(Path("services/api").resolve()))
import web_app

pdf = "Manualul Instalatiilor Electrice.pdf"

tests = [
    ("course_tools", web_app.course_tools(pdf=pdf)),
    ("view_course", web_app.view_course(pdf=pdf)),
    ("review_ocr_text", web_app.review_ocr_text(pdf=pdf, page=15)),
    ("review_concepts", web_app.review_concepts(pdf=pdf)),
]

for name, response in tests:
    body = response.body.decode("utf-8", errors="replace")
    print(name, response.status_code, len(body))
    print("  Course tools:", "/course-tools?pdf=" in body)
    print("  Review OCR:", "/review-ocr-text?pdf=" in body)
    print("  Review Concepts:", "/review-concepts?pdf=" in body)
    print("  Study:", "/study?pdf=" in body)
