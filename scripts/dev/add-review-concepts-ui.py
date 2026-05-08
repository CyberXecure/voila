from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

if '@app.get("/review-concepts")' not in text:
    route = r'''

def _safe_pdf_name(value: str) -> str:
    return Path(value).name


def _output_dir_for_pdf_name(pdf_name: str) -> Path:
    safe_name = _safe_pdf_name(pdf_name)
    return PROJECT_ROOT / "data" / "output" / Path(safe_name).stem


def _load_json_file(path: Path, default):
    if not path.exists():
        return default

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _save_json_file(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _html_escape(value: str) -> str:
    import html
    return html.escape(str(value or ""), quote=True)


def _is_suspicious_concept_title(title: str) -> bool:
    title = str(title or "").strip()
    lower = title.lower()

    if not title:
        return True

    if len(title) < 4:
        return True

    letters = len(re.findall(r"[A-Za-zĂÂÎȘȚăâîșț]", title))
    digits = len(re.findall(r"\d", title))

    if digits > letters:
        return True

    if re.search(r"\b(jj|ixii|v0|01g|lll|iiii|xii!)\b", lower):
        return True

    if re.search(r"[^\w\săâîșțĂÂÎȘȚ.,:;()/-]", title):
        return True

    if len(re.findall(r"[A-Za-zĂÂÎȘȚăâîșț]{3,}", title)) < 1:
        return True

    return False


@app.get("/review-concepts")
def review_concepts(pdf: str = ""):
    from fastapi.responses import HTMLResponse

    pdf_name = _safe_pdf_name(pdf)

    if not pdf_name:
        return HTMLResponse("<h1>Missing PDF name</h1>", status_code=400)

    output_dir = _output_dir_for_pdf_name(pdf_name)
    quiz_path = output_dir / "quiz.study.json"
    overrides_path = output_dir / "study_concept_overrides.json"

    quiz = _load_json_file(quiz_path, {"questions": []})
    overrides = _load_json_file(overrides_path, {"overrides": {}}).get("overrides", {})

    grouped = {}

    for question in quiz.get("questions", []):
        lesson_id = question.get("lesson_id") or ""
        concept_title = question.get("concept_title") or question.get("lesson_title") or ""

        if not lesson_id:
            continue

        if lesson_id not in grouped:
            grouped[lesson_id] = {
                "lesson_id": lesson_id,
                "concept_title": concept_title,
                "questions": [],
                "pages": set(),
            }

        grouped[lesson_id]["questions"].append(question)

        for page in question.get("source_pdf_pages") or []:
            grouped[lesson_id]["pages"].add(page)

    rows = []

    for lesson_id in sorted(grouped.keys()):
        item = grouped[lesson_id]
        current = item["concept_title"]
        override = overrides.get(lesson_id, {})
        effective = override.get("concept_title") or current
        suspicious = _is_suspicious_concept_title(effective)

        badge = '<span class="badge bad">Suspect</span>' if suspicious else '<span class="badge ok">OK</span>'

        pages = ", ".join(str(p) for p in sorted(item["pages"])) if item["pages"] else "-"
        sample_question = ""
        sample_answer = ""

        if item["questions"]:
            sample_question = item["questions"][0].get("question") or ""
            sample_answer = item["questions"][0].get("answer") or ""

        rows.append(f"""
        <section class="concept-card {'suspicious' if suspicious else ''}">
          <div class="concept-head">
            <div>
              <h2>{_html_escape(lesson_id)} — {_html_escape(effective)}</h2>
              <p>{badge} · Questions: <b>{len(item['questions'])}</b> · Pages: {_html_escape(pages)}</p>
            </div>
          </div>

          <form method="post" action="/review-concepts/save" class="concept-form">
            <input type="hidden" name="pdf" value="{_html_escape(pdf_name)}">
            <input type="hidden" name="lesson_id" value="{_html_escape(lesson_id)}">

            <label>Correct concept title</label>
            <input name="title" value="{_html_escape(effective)}">

            <div class="actions">
              <button type="submit">Save title override</button>
              <a class="ghost" href="/study?pdf={_html_escape(pdf_name)}">Study</a>
            </div>
          </form>

          <details>
            <summary>Question sample</summary>
            <p><b>Q:</b> {_html_escape(sample_question)}</p>
            <p><b>A:</b> {_html_escape(sample_answer)}</p>
          </details>
        </section>
        """)

    content = "\n".join(rows) if rows else "<p>No study questions found. Generate Study first.</p>"

    html_doc = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Review Study Concepts · Voila!</title>
  <style>
    :root {{
      --bg: #101819;
      --panel: #202d31;
      --panel2: #243237;
      --text: #f6ead7;
      --muted: #c7ad94;
      --line: #3b4b50;
      --accent: #e0ad68;
      --bad: #b45b46;
      --ok: #5cae9f;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      font-family: system-ui, -apple-system, Segoe UI, sans-serif;
      background: var(--bg);
      color: var(--text);
      padding: 32px;
    }}

    .wrap {{
      max-width: 1400px;
      margin: 0 auto;
    }}

    .top {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      margin-bottom: 24px;
    }}

    h1 {{
      font-size: clamp(32px, 5vw, 58px);
      margin: 0;
      line-height: 1.05;
    }}

    .top-actions {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}

    a, button {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 12px 18px;
      background: var(--panel2);
      color: var(--text);
      text-decoration: none;
      font-weight: 800;
      cursor: pointer;
      font-size: 16px;
    }}

    button {{
      background: var(--accent);
      color: white;
      border-color: transparent;
    }}

    .ghost {{
      background: transparent;
    }}

    .concept-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 24px;
      margin: 18px 0;
    }}

    .concept-card.suspicious {{
      border-color: rgba(180, 91, 70, 0.9);
      box-shadow: 0 0 0 2px rgba(180, 91, 70, 0.14);
    }}

    .concept-card h2 {{
      margin: 0 0 8px;
      font-size: 28px;
    }}

    .concept-card p {{
      color: var(--muted);
      font-size: 18px;
      line-height: 1.5;
    }}

    .badge {{
      display: inline-block;
      padding: 6px 12px;
      border-radius: 999px;
      font-weight: 900;
      color: white;
    }}

    .badge.bad {{ background: var(--bad); }}
    .badge.ok {{ background: var(--ok); }}

    .concept-form {{
      margin-top: 18px;
      display: grid;
      gap: 10px;
    }}

    label {{
      color: var(--muted);
      font-weight: 800;
    }}

    input {{
      width: 100%;
      border-radius: 16px;
      border: 1px solid var(--line);
      background: #142022;
      color: var(--text);
      padding: 14px 16px;
      font-size: 20px;
      font-weight: 700;
    }}

    .actions {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 6px;
    }}

    details {{
      margin-top: 18px;
      color: var(--muted);
    }}

    summary {{
      cursor: pointer;
      font-weight: 900;
      color: var(--text);
    }}

    .floating-nav {{
      position: fixed;
      left: 50%;
      bottom: 18px;
      transform: translateX(-50%);
      display: flex;
      gap: 10px;
      background: rgba(32, 45, 49, 0.96);
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 10px;
      box-shadow: 0 18px 48px rgba(0,0,0,0.35);
      z-index: 999;
    }}

    @media (max-width: 760px) {{
      body {{ padding: 18px; }}
      .top {{ display: block; }}
      .top-actions {{ margin-top: 16px; }}
      .concept-card {{ padding: 18px; }}
      .concept-card h2 {{ font-size: 22px; }}
      .floating-nav {{
        width: calc(100% - 24px);
        overflow-x: auto;
        justify-content: flex-start;
      }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div>
        <h1>Review Study Concepts</h1>
        <p>PDF: <b>{_html_escape(pdf_name)}</b></p>
      </div>
      <div class="top-actions">
        <a href="/">Back</a>
        <a href="/study?pdf={_html_escape(pdf_name)}">Study</a>
        <a href="/progress?pdf={_html_escape(pdf_name)}">Progress</a>
      </div>
    </div>

    {content}
  </div>

  <nav class="floating-nav">
    <a href="/">Back</a>
    <a href="/study?pdf={_html_escape(pdf_name)}">Study</a>
    <a href="#top" onclick="window.scrollTo({{top:0,behavior:'smooth'}}); return false;">↑ Top</a>
    <a href="#bottom" onclick="window.scrollTo({{top:document.body.scrollHeight,behavior:'smooth'}}); return false;">↓ Bottom</a>
  </nav>
</body>
</html>
"""

    return HTMLResponse(html_doc)


@app.post("/review-concepts/save")
def save_review_concept(pdf: str = Form(...), lesson_id: str = Form(...), title: str = Form(...)):
    from fastapi.responses import RedirectResponse
    from urllib.parse import quote

    pdf_name = _safe_pdf_name(pdf)
    output_dir = _output_dir_for_pdf_name(pdf_name)
    overrides_path = output_dir / "study_concept_overrides.json"

    payload = _load_json_file(
        overrides_path,
        {
            "version": "1.0",
            "overrides": {},
        },
    )

    payload.setdefault("overrides", {})[lesson_id] = {
        "concept_title": title.strip(),
        "lesson_title": title.strip(),
        "source": "manual_ui",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    _save_json_file(overrides_path, payload)

    try:
        from ocr_corrections_engine import apply_title_overrides
        apply_title_overrides(output_dir)
    except Exception:
        pass

    return RedirectResponse(
        "/review-concepts?pdf=" + quote(pdf_name),
        status_code=303,
    )
'''

    text += route

path.write_text(text, encoding="utf-8")
print("OK: Review Study Concepts routes added.")
