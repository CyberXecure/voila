from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# Add Review button next to Study / Progress in PDF cards.
if "Review weak" not in text:
    text = text.replace(
'''            actions.append(
                f'<a class="btn" href="/study?pdf={quote(pdf.name)}">Study</a>'
            )
            actions.append(
                f'<a class="btn" href="/progress?pdf={quote(pdf.name)}">Progress</a>'
            )
''',
'''            actions.append(
                f'<a class="btn" href="/study?pdf={quote(pdf.name)}">Study</a>'
            )
            actions.append(
                f'<a class="btn" href="/review?pdf={quote(pdf.name)}">Review weak</a>'
            )
            actions.append(
                f'<a class="btn" href="/progress?pdf={quote(pdf.name)}">Progress</a>'
            )
'''
    )

route = r'''

def choose_review_question_from_view(view: dict) -> dict | None:
    questions = view.get("questions") or []
    state = view.get("state") or {}
    concepts = view.get("concepts") or []

    if not questions:
        return None

    weak_concept_ids = {
        str(item.get("concept_id"))
        for item in concepts
        if float(item.get("mastery", 0)) < 0.75
    }

    if not weak_concept_ids:
        weak_concept_ids = {
            str(item.get("concept_id"))
            for item in concepts
            if float(item.get("mastery", 0)) < 0.90
        }

    attempts = state.get("attempts") or []
    answered_ids = {
        str(item.get("question_id"))
        for item in attempts
        if item.get("question_id")
    }

    concept_by_id = {
        str(item.get("concept_id")): item
        for item in concepts
    }

    candidates = [
        question for question in questions
        if str(question.get("concept_id")) in weak_concept_ids
    ]

    if not candidates:
        candidates = questions

    unanswered = [
        question for question in candidates
        if str(question.get("question_id")) not in answered_ids
    ]

    pool = unanswered if unanswered else candidates

    def score(question: dict) -> tuple[float, int]:
        concept_id = str(question.get("concept_id"))
        concept = concept_by_id.get(concept_id) or {}
        mastery = float(concept.get("mastery", 0.30))
        attempts_count = int(concept.get("attempts", 0))
        return (mastery, attempts_count)

    return sorted(pool, key=score)[0] if pool else None


@app.get("/review", response_class=HTMLResponse)
def review(pdf: str = Query(...)) -> HTMLResponse:
    pdf_path = validate_pdf_name(pdf)
    output_dir = OUTPUT_DIR / pdf_path.stem

    try:
        view = get_study_view(output_dir)
    except Exception as exc:
        body = f"""
        <h1>Voila! Review</h1>
        <div class="notice">
          Cannot open Review Mode for <strong>{html.escape(pdf_path.name)}</strong>.
        </div>
        <p>Error: <code>{html.escape(str(exc))}</code></p>
        """
        return page("Voila! Review", body)

    concepts = view.get("concepts") or []
    weak = [item for item in concepts if float(item.get("mastery", 0)) < 0.40]
    review_items = [item for item in concepts if 0.40 <= float(item.get("mastery", 0)) < 0.75]
    almost = [item for item in concepts if 0.75 <= float(item.get("mastery", 0)) < 0.90]

    current = choose_review_question_from_view(view)
    last_attempt = view.get("last_attempt")

    last_html = ""

    if last_attempt:
        result = "Correct" if last_attempt.get("correct") else "Incorrect"
        before = round(float(last_attempt.get("mastery_before", 0)) * 100)
        after = round(float(last_attempt.get("mastery_after", 0)) * 100)

        last_html = f"""
        <div class="notice">
          Last review answer: <strong>{result}</strong>.
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

        concept_id = html.escape(str(current.get("concept_id") or current.get("lesson_id") or ""))
        question = html.escape(str(current.get("question") or ""))
        answer_id = html.escape(str(current.get("question_id") or ""))

        question_html = f"""
        <article class="card">
          <h2>Review question</h2>
          <div class="meta">Focused concept: <strong>{concept_id}</strong></div>
          <p style="font-size: 20px;"><strong>{question}</strong></p>
          {answer_html}

          <div class="actions">
            <form method="post" action="/review-answer">
              <input type="hidden" name="pdf_name" value="{html.escape(pdf_path.name)}">
              <input type="hidden" name="question_id" value="{answer_id}">
              <input type="hidden" name="correct" value="true">
              <button class="primary" type="submit">Correct</button>
            </form>

            <form method="post" action="/review-answer">
              <input type="hidden" name="pdf_name" value="{html.escape(pdf_path.name)}">
              <input type="hidden" name="question_id" value="{answer_id}">
              <input type="hidden" name="correct" value="false">
              <button type="submit">Incorrect</button>
            </form>
          </div>
        </article>
        """
    else:
        question_html = """
        <article class="card">
          <h2>No review questions available</h2>
          <p>Generate a study quiz first.</p>
        </article>
        """

    def mini_list(title: str, items: list, empty: str) -> str:
        rows = []

        for item in items[:8]:
            concept_id = html.escape(str(item.get("concept_id") or ""))
            mastery = int(item.get("mastery_percent") or 0)
            attempts = int(item.get("attempts") or 0)

            rows.append(
                f"""
                <article class="card">
                  <h2>{concept_id}</h2>
                  <p style="font-size: 28px; margin: 8px 0;"><strong>{mastery}%</strong></p>
                  <div class="meta">Attempts: {attempts}</div>
                </article>
                """
            )

        if not rows:
            rows.append(
                f"""
                <article class="card">
                  <h2>{html.escape(title)}</h2>
                  <p>{html.escape(empty)}</p>
                </article>
                """
            )

        return f"""
        <h2 style="margin-top: 28px;">{html.escape(title)}</h2>
        <div class="grid">
          {''.join(rows)}
        </div>
        """

    body = f"""
    <h1>Voila! Review weak concepts</h1>

    <div class="notice">
      PDF: <strong>{html.escape(pdf_path.name)}</strong><br>
      Needs review: <strong>{len(weak)}</strong> ·
      In progress: <strong>{len(review_items)}</strong> ·
      Almost mastered: <strong>{len(almost)}</strong>
    </div>

    {last_html}

    <div class="grid">
      {question_html}
    </div>

    <div class="actions" style="margin-top: 24px;">
      <a class="btn primary" href="/review?pdf={quote(pdf_path.name)}">Next review</a>
      <a class="btn" href="/study?pdf={quote(pdf_path.name)}">Study</a>
      <a class="btn" href="/progress?pdf={quote(pdf_path.name)}">Progress</a>
      <a class="btn" href="/">Back to Voila!</a>
    </div>

    {mini_list("Needs review", weak, "No weak concepts yet.")}
    {mini_list("In progress", review_items, "No concepts in progress yet.")}
    {mini_list("Almost mastered", almost, "No almost-mastered concepts yet.")}
    """

    return page("Voila! Review", body)


@app.post("/review-answer")
def review_answer(
    pdf_name: str = Form(...),
    question_id: str = Form(...),
    correct: bool = Form(...),
) -> RedirectResponse:
    pdf_path = validate_pdf_name(pdf_name)
    output_dir = OUTPUT_DIR / pdf_path.stem

    record_answer(output_dir, question_id, correct)

    return RedirectResponse(
        url="/review?pdf=" + quote(pdf_path.name),
        status_code=303,
    )

'''

if '@app.get("/review"' not in text:
    if '\n@app.get("/progress"' in text:
        text = text.replace('\n@app.get("/progress"', route + '\n@app.get("/progress"', 1)
    elif '\n@app.get("/study"' in text:
        text = text.replace('\n@app.get("/study"', route + '\n@app.get("/study"', 1)
    else:
        raise SystemExit("Could not find insertion point for Review route.")

path.write_text(text, encoding="utf-8")
print("OK: Review weak concepts added.")
