from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

if '@app.get("/lessons"' not in text:
    block = r'''

# VOILA_LESSONS_ROUTES_V1

@app.get("/lessons", response_class=HTMLResponse)
def voila_lessons(pdf: str = Query(...)) -> HTMLResponse:
    import html
    from urllib.parse import quote
    import lesson_tools

    pdf_path = validate_pdf_name(pdf)
    output_dir = OUTPUT_DIR / pdf_path.stem
    lessons = lesson_tools.build_lessons(output_dir)

    q_pdf = quote(pdf_path.name)

    rows = []

    for index, lesson in enumerate(lessons, start=1):
        lesson_id = str(lesson.get("lesson_id") or "")
        title = str(lesson.get("title") or lesson_id)
        pages = ", ".join(str(p) for p in lesson.get("pages") or []) or "-"
        preview = str(lesson.get("preview") or "")
        questions_count = int(lesson.get("questions_count") or 0)

        rows.append(f"""
        <article class="card">
          <div class="meta">#{index} · ID: <code>{html.escape(lesson_id)}</code> · {_ut("questions", "Questions")}: <strong>{questions_count}</strong> · Pages: <strong>{html.escape(pages)}</strong></div>
          <h2>{html.escape(title)}</h2>
          <p>{html.escape(preview)}</p>
          <div class="actions">
            <a class="btn primary" href="/lesson?pdf={q_pdf}&lesson_id={quote(lesson_id)}">Deschide lecția</a>
            <a class="btn" href="/study-lesson?pdf={q_pdf}&lesson_id={quote(lesson_id)}">Studiază lecția</a>
          </div>
        </article>
        """)

    content = "\n".join(rows) if rows else """
    <article class="card">
      <h2>Nu există lecții disponibile</h2>
      <p>Generează mai întâi cursul / quiz-ul pentru acest PDF.</p>
    </article>
    """

    body = f"""
    <h1>Lecții</h1>

    <div class="notice">
      PDF: <strong>{html.escape(pdf_path.name)}</strong><br>
      Lecții găsite: <strong>{len(lessons)}</strong>
    </div>

    <div class="actions">
      <a class="btn" href="/course-tools?pdf={q_pdf}">Course Tools</a>
      <a class="btn" href="/view-course?pdf={q_pdf}">Open course</a>
      <a class="btn" href="/study?pdf={q_pdf}">{_ut("study", "Study")}</a>
      <a class="btn" href="/">Library</a>
    </div>

    <div class="grid">
      {content}
    </div>
    """

    return page("Voila! Lessons", body)


@app.get("/lesson", response_class=HTMLResponse)
def voila_lesson(pdf: str = Query(...), lesson_id: str = Query(...)) -> HTMLResponse:
    import html
    from urllib.parse import quote
    import lesson_tools

    pdf_path = validate_pdf_name(pdf)
    output_dir = OUTPUT_DIR / pdf_path.stem

    lesson = lesson_tools.get_lesson(output_dir, lesson_id)

    q_pdf = quote(pdf_path.name)
    q_lesson = quote(str(lesson_id or ""))

    if not lesson:
        body = f"""
        <h1>Lecție negăsită</h1>
        <p>Nu am găsit lecția <code>{html.escape(str(lesson_id))}</code>.</p>
        <p><a class="btn" href="/lessons?pdf={q_pdf}">Înapoi la lecții</a></p>
        """
        return page("Voila! Lesson", body)

    title = str(lesson.get("title") or lesson_id)
    pages = ", ".join(str(p) for p in lesson.get("pages") or []) or "-"
    source_text = str(lesson.get("source_text") or "").strip()

    if source_text:
        lesson_body = ""
        chunks = [chunk.strip() for chunk in source_text.split("\n\n") if chunk.strip()]

        for chunk in chunks[:12]:
            lesson_body += f"<p>{html.escape(chunk)}</p>\n"
    else:
        lesson_body = "<p>Nu există text sursă disponibil pentru această lecție.</p>"

    body = f"""
    <h1>{html.escape(title)}</h1>

    <div class="notice">
      PDF: <strong>{html.escape(pdf_path.name)}</strong><br>
      Lesson ID: <code>{html.escape(str(lesson_id))}</code><br>
      Pages: <strong>{html.escape(pages)}</strong><br>
      {_ut("questions", "Questions")}: <strong>{int(lesson.get("questions_count") or 0)}</strong>
    </div>

    <div class="actions">
      <a class="btn" href="/lessons?pdf={q_pdf}">← Lecții</a>
      <a class="btn primary" href="/study-lesson?pdf={q_pdf}&lesson_id={q_lesson}">Studiază lecția</a>
      <a class="btn" href="/view-course?pdf={q_pdf}">Open course</a>
    </div>

    <article class="card">
      {lesson_body}
    </article>
    """

    return page("Voila! Lesson", body)


@app.get("/study-lesson", response_class=HTMLResponse)
def voila_study_lesson(pdf: str = Query(...), lesson_id: str = Query(...)) -> HTMLResponse:
    import html
    from urllib.parse import quote
    import lesson_tools
    import study_questions
    from study_engine import load_state, choose_next_question

    pdf_path = validate_pdf_name(pdf)
    output_dir = OUTPUT_DIR / pdf_path.stem

    questions = lesson_tools.questions_for_lesson(output_dir, lesson_id)
    state = load_state(output_dir, questions)
    current = choose_next_question(questions, state)

    q_pdf = quote(pdf_path.name)
    q_lesson = quote(str(lesson_id or ""))

    lesson = lesson_tools.get_lesson(output_dir, lesson_id)
    title = str((lesson or {}).get("title") or lesson_id)

    if current:
        question_text = study_questions.build_study_question(PROJECT_ROOT, pdf_path.name, current)
        answer_text = str(current.get("answer") or "")

        question_html = f"""
        <article class="card">
          <div class="meta">{_ut("lesson_concept", "Lesson / concept")}: <strong>{html.escape(title)}</strong></div>
          <h2>{_ut("recommended_question", "Recommended question")}</h2>
          <p style="font-size: 20px;"><strong>{html.escape(question_text)}</strong></p>

          <details>
            <summary>{_ut("show_expected_answer", "Show expected answer / explanation")}</summary>
            <p>{html.escape(answer_text)}</p>
          </details>

          <div class="actions">
            <form method="post" action="/study-lesson-answer">
              <input type="hidden" name="pdf_name" value="{html.escape(pdf_path.name)}">
              <input type="hidden" name="lesson_id" value="{html.escape(str(lesson_id))}">
              <input type="hidden" name="question_id" value="{html.escape(str(current.get("question_id")))}">
              <input type="hidden" name="correct" value="true">
              <button class="primary" type="submit">{_ut("correct", "Correct")}</button>
            </form>

            <form method="post" action="/study-lesson-answer">
              <input type="hidden" name="pdf_name" value="{html.escape(pdf_path.name)}">
              <input type="hidden" name="lesson_id" value="{html.escape(str(lesson_id))}">
              <input type="hidden" name="question_id" value="{html.escape(str(current.get("question_id")))}">
              <input type="hidden" name="correct" value="false">
              <button type="submit">{_ut("incorrect", "Incorrect")}</button>
            </form>
          </div>
        </article>
        """
    else:
        question_html = f"""
        <article class="card">
          <h2>{_ut("no_questions_available", "No questions available")}</h2>
          <p>Nu există întrebări pentru lecția selectată.</p>
        </article>
        """

    body = f"""
    <h1>{_ut("study", "Study")} · {html.escape(title)}</h1>

    <div class="notice">
      PDF: <strong>{html.escape(pdf_path.name)}</strong><br>
      Lesson ID: <code>{html.escape(str(lesson_id))}</code><br>
      {_ut("questions", "Questions")}: <strong>{len(questions)}</strong>
    </div>

    <div class="actions">
      <a class="btn" href="/lesson?pdf={q_pdf}&lesson_id={q_lesson}">Citește lecția</a>
      <a class="btn" href="/lessons?pdf={q_pdf}">← Lecții</a>
      <a class="btn" href="/study?pdf={q_pdf}">Study general</a>
    </div>

    {question_html}
    """

    return page("Voila! Study Lesson", body)


@app.post("/study-lesson-answer")
def voila_study_lesson_answer(
    pdf_name: str = Form(...),
    lesson_id: str = Form(...),
    question_id: str = Form(...),
    correct: bool = Form(...),
) -> RedirectResponse:
    from urllib.parse import quote
    from study_engine import record_answer

    pdf_path = validate_pdf_name(pdf_name)
    output_dir = OUTPUT_DIR / pdf_path.stem

    record_answer(output_dir, question_id, correct)

    return RedirectResponse(
        f"/study-lesson?pdf={quote(pdf_path.name)}&lesson_id={quote(str(lesson_id))}",
        status_code=303,
    )
'''
    text = text.rstrip() + "\n\n" + block + "\n"

path.write_text(text, encoding="utf-8")
print("OK: lessons routes added.")
