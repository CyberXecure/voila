import sys
from pathlib import Path

sys.path.insert(0, str(Path("services/api").resolve()))
import web_app

pdf = "Manualul Instalatiilor Electrice.pdf"

tests = [
    ("quick_tools", web_app.quick_tools()),
    ("course_tools", web_app.course_tools(pdf=pdf)),
    ("view_course", web_app.view_course(pdf=pdf)),
    ("view_figures", web_app.view_figures(pdf=pdf)),
    ("review_ocr_text", web_app.review_ocr_text(pdf=pdf, page=15)),
    ("review_concepts", web_app.review_concepts(pdf=pdf)),
]

for name, response in tests:
    body = response.body.decode("utf-8", errors="replace")
    print(name, response.status_code, len(body))
    print("  /quick-tools:", "/quick-tools" in body)
    print("  /course-tools:", "/course-tools?pdf=" in body)
    print("  /view-course:", "/view-course?pdf=" in body)
    print("  /review-ocr-text:", "/review-ocr-text?pdf=" in body)
    print("  /review-concepts:", "/review-concepts?pdf=" in body)
    print()
