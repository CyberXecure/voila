from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

if "from study_engine import" not in text:
    text = text.replace(
        "from fastapi.staticfiles import StaticFiles\n",
        "from fastapi.staticfiles import StaticFiles\n\nfrom study_engine import get_study_view, record_answer, reset_study_state\n",
    )

text = text.replace(
'''        log_file = out_dir / "last_run.log"
''',
'''        log_file = out_dir / "last_run.log"
        quiz_file = out_dir / "quiz.json"
'''
)

text = text.replace(
'''        if log_file.exists():
            actions.append(
                f'<a class="btn" target="_blank" href="/log?pdf={quote(pdf.name)}">Logs</a>'
            )
''',
'''        if quiz_file.exists():
            actions.append(
                f'<a class="btn" target="_blank" href="/study?pdf={quote(pdf.name)}">Study</a>'
            )

        if log_file.exists():
            actions.append(
                f'<a class="btn" target="_blank" href="/log?pdf={quote(pdf.name)}">Logs</a>'
            )
'''
)

routes = r'''

@app.get("/study", response_class=HTMLResponse)
def study(pdf: str = Query(...)) -> HTMLResponse:
    pdf_path = validate_pdf_name(pdf)
    output_dir = OUTPUT_DIR / pdf_path.stem

    try:
        view = get_study_view(output_dir)
    except Exception as exc:
        body = f"""
        <h1>Study Mode</h1>
        <div class="notice">
          Cannot open Study Mode for <strong>{html.escape(pdf_path.name)}</strong>.
        </div>
        <p>Error: <code>{html.escape(str(exc))}</code></p>
        """
        return page("Voila! Study", body)

    current = view.get("current_question")
    concepts = view.get("concepts", [])
    last_attempt = view.get("last_attempt")

    last_html = ""

    if last_attempt:
        result = "Correct" if last_attempt.get("correct") else "Incorrect"
        before = round(float(last_attempt.get("mastery_before", 0)) * 100)
        after = round(float(last_attempt.get("mastery_after", 0)) * 100)

        last_html = f"""
        <div class="notice">
          Last answer: <strong>{result}</strong>.
          Mastery changed from <strong>{before}%</strong> to <strong>{after}%</strong>.
        </div>
        """

    if current:
        answer_html = ""

        if current.get("answer"):
            answer_html = f"""
            <details>
              <summary>Show expected answer / explanation</summary>
              <p>{html.escape(str(current.get("answer")))}</p>
            </details>
            """

        question_html = f"""
        <article class="card">
          <h2>Recommended question</h2>
          <div class="meta">Lesson / concept: <strong>{html.escape(str(current.get("lesson_id")))}</strong></div>
          <p style="font-size: 20px;"><strong>{html.escape(str(current.get("question")))}</strong></p>
          {answer_html}

          <div class="actions">
            <form method="post" action="/study-answer">
              <input type="hidden" name="pdf_name" value="{html.escape(pdf_path.name)}">
              <input type="hidden" name="question_id" value="{html.escape(str(current.get("question_id")))}">
              <input type="hidden" name="correct" value="true">
              <button class="primary" type="submit">Correct</button>
            </form>

            <form method="post" action="/study-answer">
              <input type="hidden" name="pdf_name" value="{html.escape(pdf_path.name)}">
              <input type="hidden" name="question_id" value="{html.escape(str(current.get("question_id")))}">
              <input type="hidden" name="correct" value="false">
              <button type="submit">Incorrect</button>
            </form>
          </div>
        </article>
        """
    else:
        question_html = """
        <article class="card">
          <h2>No questions available</h2>
          <p>Generate course files first, then Study Mode will use quiz.json.</p>
        </article>
        """

    concept_cards = []

    for concept in concepts:
        mastery = int(concept.get("mastery_percent", 0))
        concept_id = html.escape(str(concept.get("concept_id", "")))
        status = html.escape(str(concept.get("status", "")))
        attempts = int(concept.get("attempts", 0))
        correct_count = int(concept.get("correct", 0))
        incorrect_count = int(concept.get("incorrect", 0))

        concept_cards.append(
            f"""
            <article class="card">
              <h2>{concept_id}</h2>
              <div class="meta">Status: <strong>{status}</strong></div>
              <p style="font-size: 28px; margin: 8px 0;"><strong>{mastery}%</strong></p>
              <div class="meta">
                Attempts: {attempts}<br>
                Correct: {correct_count}<br>
                Incorrect: {incorrect_count}
              </div>
            </article>
            """
        )

    reset_form = f"""
    <form method="post" action="/study-reset">
      <input type="hidden" name="pdf_name" value="{html.escape(pdf_path.name)}">
      <button type="submit">Reset study progress</button>
    </form>
    """

    body = f"""
    <h1>Voila! Study Mode</h1>
    <div class="notice">
      PDF: <strong>{html.escape(pdf_path.name)}</strong><br>
      Questions: <strong>{view.get("total_questions")}</strong> ·
      Answered: <strong>{view.get("answered_count")}</strong> ·
      Overall mastery: <strong>{view.get("overall_mastery_percent")}%</strong> ·
      Status: <strong>{html.escape(str(view.get("overall_status")))}</strong>
    </div>

    {last_html}

    <div class="grid">
      {question_html}
    </div>

    <h2 style="margin-top: 28px;">Concept mastery</h2>
    <div class="grid">
      {''.join(concept_cards)}
    </div>

    <div class="actions" style="margin-top: 24px;">
      <a class="btn" href="/">Back to Voila!</a>
      {reset_form}
    </div>
    """

    return page("Voila! Study", body)


@app.post("/study-answer")
def study_answer(
    pdf_name: str = Form(...),
    question_id: str = Form(...),
    correct: bool = Form(...),
) -> RedirectResponse:
    pdf_path = validate_pdf_name(pdf_name)
    output_dir = OUTPUT_DIR / pdf_path.stem

    record_answer(output_dir, question_id, correct)

    return RedirectResponse(
        url="/study?pdf=" + quote(pdf_path.name),
        status_code=303,
    )


@app.post("/study-reset")
def study_reset(pdf_name: str = Form(...)) -> RedirectResponse:
    pdf_path = validate_pdf_name(pdf_name)
    output_dir = OUTPUT_DIR / pdf_path.stem

    reset_study_state(output_dir)

    return RedirectResponse(
        url="/study?pdf=" + quote(pdf_path.name),
        status_code=303,
    )

'''

if "@app.get(\"/study\"" not in text:
    text = text.replace("\n@app.get(\"/log\")", routes + "\n@app.get(\"/log\")")

path.write_text(text, encoding="utf-8")
print("OK: web_app.py updated with Study Mode.")
