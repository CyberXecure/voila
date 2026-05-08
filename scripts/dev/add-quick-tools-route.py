from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

if '@app.get("/quick-tools")' not in text:
    route = r'''

@app.get("/quick-tools")
def quick_tools():
    from fastapi.responses import HTMLResponse
    from urllib.parse import quote

    input_dir = PROJECT_ROOT / "data" / "input"
    output_dir = PROJECT_ROOT / "data" / "output"

    pdfs = sorted(input_dir.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)

    cards = []

    for pdf in pdfs:
        out = output_dir / pdf.stem
        q = quote(pdf.name)

        exists = {
            "course": (out / "course.cleaned.html").exists(),
            "study": (out / "quiz.study.json").exists(),
            "figures": (out / "figures_hybrid" / "figures_hybrid.html").exists(),
            "ocr": (out / "ocr_pages.json").exists() or (out / "pages.json").exists(),
        }

        status = []
        for key, ok in exists.items():
            status.append(f"<span class='{key if ok else 'missing'}'>{key}: {'OK' if ok else '-'}</span>")

        cards.append(f"""
        <section class="card">
          <h2>{_nav_escape(pdf.name)}</h2>
          <p>{''.join(status)}</p>
          <div class="actions">
            <a class="primary" href="/course-tools?pdf={q}">Course Tools</a>
            <a href="/view-course?pdf={q}">Course</a>
            <a href="/study?pdf={q}">Study</a>
            <a href="/review-ocr-text?pdf={q}&page=1">Review OCR</a>
            <a href="/review-concepts?pdf={q}">Concepts</a>
          </div>
        </section>
        """)

    html_doc = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Quick Tools · Voila!</title>
  <style>
    :root {{
      --bg: #101819;
      --panel: #202d31;
      --text: #f6ead7;
      --muted: #c7ad94;
      --line: #3b4b50;
      --accent: #e0ad68;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: system-ui, -apple-system, Segoe UI, sans-serif;
      padding: 28px;
    }}

    .wrap {{
      max-width: 1300px;
      margin: 0 auto;
    }}

    h1 {{
      margin: 0 0 24px;
      font-size: clamp(36px, 6vw, 72px);
    }}

    .top {{
      display: flex;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 24px;
      flex-wrap: wrap;
    }}

    a {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 10px 14px;
      background: #26363b;
      color: var(--text);
      text-decoration: none;
      font-weight: 850;
      margin: 4px;
    }}

    a.primary {{
      background: var(--accent);
      color: white;
      border-color: transparent;
    }}

    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 22px;
      margin: 16px 0;
    }}

    .card h2 {{
      margin: 0 0 10px;
      font-size: 26px;
    }}

    .card p {{
      color: var(--muted);
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}

    span {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 10px;
    }}

    span.missing {{
      opacity: 0.5;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <h1>Quick Tools</h1>
      <a href="/">Library</a>
    </div>
    {''.join(cards) if cards else '<p>No PDFs found.</p>'}
  </div>
</body>
</html>
"""

    return HTMLResponse(html_doc)
'''
    text += "\n\n" + route

# Add Quick Tools link to homepage if possible.
if 'href="/quick-tools"' not in text:
    text = text.replace(
        "<body>",
        '<body>\n<a href="/quick-tools" style="position:fixed;right:18px;top:18px;z-index:9999;background:#e0ad68;color:white;padding:12px 16px;border-radius:999px;text-decoration:none;font-weight:900;">Quick Tools</a>',
        1,
    )

path.write_text(text, encoding="utf-8")
print("OK: Quick Tools route added and homepage shortcut injected.")
