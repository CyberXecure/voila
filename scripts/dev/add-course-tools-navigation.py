from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

if '@app.get("/course-tools")' not in text:
    route = r'''

def _nav_safe_pdf_name(value: str) -> str:
    from pathlib import Path
    return Path(str(value or "")).name


def _nav_output_dir(pdf_name: str) -> Path:
    from pathlib import Path
    return PROJECT_ROOT / "data" / "output" / Path(pdf_name).stem


def _nav_quote(value: str) -> str:
    from urllib.parse import quote
    return quote(str(value or ""))


def _nav_escape(value: str) -> str:
    import html
    return html.escape(str(value or ""), quote=True)


def _voila_tools_bar(pdf_name: str, active: str = "") -> str:
    q = _nav_quote(pdf_name)

    links = [
        ("Tools", f"/course-tools?pdf={q}", "tools"),
        ("Course", f"/view-course?pdf={q}", "course"),
        ("Study", f"/study?pdf={q}", "study"),
        ("Review OCR Text", f"/review-ocr-text?pdf={q}&page=1", "ocr"),
        ("Review Concepts", f"/review-concepts?pdf={q}", "concepts"),
        ("Figures", f"/view-figures?pdf={q}", "figures"),
        ("Edit crops", f"/edit-crops?pdf={q}", "crops"),
        ("Progress", f"/progress?pdf={q}", "progress"),
        ("Library", "/", "library"),
    ]

    items = []

    for label, href, key in links:
        cls = "active" if key == active else ""
        items.append(f'<a class="{cls}" href="{href}">{label}</a>')

    return """
<nav class="voila-tools-bar">
  """ + "\n  ".join(items) + """
</nav>
"""


def _inject_voila_tools_bar(html_doc: str, pdf_name: str, active: str = "") -> str:
    import re

    if "voila-tools-bar" in html_doc:
        return html_doc

    css = """
<style>
  .voila-tools-bar {
    position: sticky;
    top: 0;
    z-index: 5000;
    display: flex;
    gap: 10px;
    align-items: center;
    overflow-x: auto;
    padding: 12px;
    background: rgba(16, 24, 25, 0.96);
    border-bottom: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 12px 34px rgba(0,0,0,0.28);
  }

  .voila-tools-bar a {
    white-space: nowrap;
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 999px;
    padding: 10px 14px;
    background: rgba(255,255,255,0.06);
    color: #f6ead7;
    text-decoration: none;
    font-family: system-ui, -apple-system, Segoe UI, sans-serif;
    font-size: 14px;
    font-weight: 850;
  }

  .voila-tools-bar a.active {
    background: #e0ad68;
    color: white;
    border-color: transparent;
  }
</style>
"""

    bar = _voila_tools_bar(pdf_name, active)

    if "</head>" in html_doc:
        html_doc = html_doc.replace("</head>", css + "\n</head>", 1)

    html_doc = re.sub(
        r"(<body[^>]*>)",
        r"\1\n" + bar,
        html_doc,
        count=1,
        flags=re.IGNORECASE,
    )

    return html_doc


@app.get("/course-tools")
def course_tools(pdf: str = ""):
    from fastapi.responses import HTMLResponse

    pdf_name = _nav_safe_pdf_name(pdf)

    if not pdf_name:
        return HTMLResponse("<h1>Missing PDF name</h1>", status_code=400)

    output_dir = _nav_output_dir(pdf_name)
    q = _nav_quote(pdf_name)

    checks = {
        "course": (output_dir / "course.cleaned.html").exists(),
        "study": (output_dir / "quiz.study.json").exists(),
        "figures": (output_dir / "figures_hybrid" / "figures_hybrid.html").exists(),
        "ocr": (output_dir / "ocr_pages.json").exists() or (output_dir / "pages.json").exists(),
        "concepts": (output_dir / "quiz.study.json").exists(),
    }

    def card(title: str, description: str, href: str, enabled: bool = True) -> str:
        cls = "" if enabled else "disabled"
        suffix = "" if enabled else "<span>Not generated yet</span>"
        safe_href = href if enabled else "#"

        return f"""
        <a class="card {cls}" href="{safe_href}">
          <h2>{_nav_escape(title)}</h2>
          <p>{_nav_escape(description)}</p>
          {suffix}
        </a>
        """

    cards = [
        card("Open course", "Read the generated course with navigation.", f"/view-course?pdf={q}", checks["course"]),
        card("Study mode", "Practice questions generated from the course.", f"/study?pdf={q}", checks["study"]),
        card("Review OCR Text", "Correct OCR text page by page.", f"/review-ocr-text?pdf={q}&page=1", checks["ocr"]),
        card("Review Study Concepts", "Correct lesson and concept titles.", f"/review-concepts?pdf={q}", checks["concepts"]),
        card("Figures", "View extracted figures.", f"/view-figures?pdf={q}", checks["figures"]),
        card("Edit crops", "Manually edit figure crops.", f"/edit-crops?pdf={q}", checks["figures"]),
        card("Progress", "View study progress.", f"/progress?pdf={q}", checks["study"]),
        card("Library", "Return to the main course library.", "/", True),
    ]

    css = """
<style>
  :root {
    --bg: #101819;
    --panel: #202d31;
    --panel2: #26363b;
    --text: #f6ead7;
    --muted: #c7ad94;
    --line: #3b4b50;
    --accent: #e0ad68;
  }

  * { box-sizing: border-box; }

  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: system-ui, -apple-system, Segoe UI, sans-serif;
    padding: 28px;
  }

  .wrap {
    max-width: 1300px;
    margin: 0 auto;
  }

  h1 {
    margin: 0 0 8px;
    font-size: clamp(36px, 6vw, 72px);
    line-height: 1.05;
  }

  .muted {
    color: var(--muted);
    font-size: 18px;
    margin-bottom: 28px;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 18px;
  }

  .card {
    display: block;
    min-height: 170px;
    padding: 24px;
    border-radius: 24px;
    background: var(--panel);
    border: 1px solid var(--line);
    color: var(--text);
    text-decoration: none;
    box-shadow: 0 18px 48px rgba(0,0,0,0.22);
  }

  .card:hover {
    border-color: var(--accent);
    transform: translateY(-1px);
  }

  .card h2 {
    margin: 0 0 10px;
    font-size: 26px;
  }

  .card p {
    color: var(--muted);
    font-size: 17px;
    line-height: 1.45;
  }

  .card.disabled {
    opacity: 0.45;
    pointer-events: none;
  }

  .card span {
    display: inline-block;
    margin-top: 10px;
    color: var(--muted);
    font-weight: 800;
  }
</style>
"""

    html_doc = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Course Tools · Voila!</title>
  {css}
</head>
<body>
  <div class="wrap">
    <h1>Course Tools</h1>
    <div class="muted">PDF: <b>{_nav_escape(pdf_name)}</b></div>
    <div class="grid">
      {''.join(cards)}
    </div>
  </div>
</body>
</html>
"""

    return HTMLResponse(html_doc)


@app.get("/view-course")
def view_course(pdf: str = ""):
    from fastapi.responses import HTMLResponse

    pdf_name = _nav_safe_pdf_name(pdf)

    if not pdf_name:
        return HTMLResponse("<h1>Missing PDF name</h1>", status_code=400)

    output_dir = _nav_output_dir(pdf_name)
    course_html = output_dir / "course.cleaned.html"

    if not course_html.exists():
        return HTMLResponse("<h1>Course HTML not found</h1>", status_code=404)

    html_doc = course_html.read_text(encoding="utf-8", errors="ignore")
    html_doc = _inject_voila_tools_bar(html_doc, pdf_name, "course")

    return HTMLResponse(html_doc)


@app.get("/view-figures")
def view_figures(pdf: str = ""):
    from fastapi.responses import HTMLResponse

    pdf_name = _nav_safe_pdf_name(pdf)

    if not pdf_name:
        return HTMLResponse("<h1>Missing PDF name</h1>", status_code=400)

    output_dir = _nav_output_dir(pdf_name)
    figures_html = output_dir / "figures_hybrid" / "figures_hybrid.html"

    if not figures_html.exists():
        return HTMLResponse("<h1>Figures HTML not found</h1>", status_code=404)

    html_doc = figures_html.read_text(encoding="utf-8", errors="ignore")

    base = "/output/" + _nav_quote(output_dir.name) + "/figures_hybrid/"
    html_doc = html_doc.replace('src="crops/', f'src="{base}crops/')
    html_doc = html_doc.replace("src='crops/", f"src='{base}crops/")

    html_doc = _inject_voila_tools_bar(html_doc, pdf_name, "figures")

    return HTMLResponse(html_doc)
'''

    text += "\n\n" + route

path.write_text(text, encoding="utf-8")
print("OK: Course Tools navigation hub added.")
