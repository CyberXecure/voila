from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# Review OCR Text: top navigation
start = text.find('@app.get("/review-ocr-text")')
end = text.find('@app.post("/review-ocr-text/save")', start)

if start != -1 and end != -1:
    segment = text[start:end]

    if 'Course tools</a>' not in segment:
        segment = segment.replace(
            '<a href="/">Back</a>',
            '<a href="/course-tools?pdf={quote(pdf_name)}">Course tools</a>\n        <a href="/">Library</a>',
            1,
        )

    if 'Open course</a>' not in segment:
        segment = segment.replace(
            '<a href="/study?pdf={quote(pdf_name)}">Study</a>',
            '<a href="/view-course?pdf={quote(pdf_name)}">Open course</a>\n        <a href="/study?pdf={quote(pdf_name)}">Study</a>',
            1,
        )

    text = text[:start] + segment + text[end:]


# Review Study Concepts: import quote and add cross-links
start = text.find('@app.get("/review-concepts")')
end = text.find('@app.post("/review-concepts/save")', start)

if start != -1 and end != -1:
    segment = text[start:end]

    if 'from urllib.parse import quote' not in segment:
        segment = segment.replace(
            'from fastapi.responses import HTMLResponse',
            'from fastapi.responses import HTMLResponse\n    from urllib.parse import quote',
            1,
        )

    if 'Course tools</a>' not in segment:
        segment = segment.replace(
            '<a href="/">Back</a>',
            '<a href="/course-tools?pdf={quote(pdf_name)}">Course tools</a>\n        <a href="/">Library</a>',
            1,
        )

    if 'Review OCR Text</a>' not in segment:
        segment = segment.replace(
            '<a href="/study?pdf={_html_escape(pdf_name)}">Study</a>',
            '<a href="/review-ocr-text?pdf={quote(pdf_name)}&page=1">Review OCR Text</a>\n        <a href="/view-course?pdf={quote(pdf_name)}">Open course</a>\n        <a href="/study?pdf={quote(pdf_name)}">Study</a>',
            1,
        )

    text = text[:start] + segment + text[end:]

path.write_text(text, encoding="utf-8")
print("OK: Review OCR/Text and Review Concepts navigation links patched.")
