from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# Add Progress button next to Study in the main UI.
old = '''        if quiz_file.exists():
            actions.append(
                f'<a class="btn" target="_blank" href="/study?pdf={quote(pdf.name)}">Study</a>'
            )
'''

new = '''        if quiz_file.exists():
            actions.append(
                f'<a class="btn" target="_blank" href="/study?pdf={quote(pdf.name)}">Study</a>'
            )
            actions.append(
                f'<a class="btn" target="_blank" href="/progress?pdf={quote(pdf.name)}">Progress</a>'
            )
'''

if old in text and "/progress?pdf=" not in text:
    text = text.replace(old, new)

# Add Progress route before Study route.
route = r'''

@app.get("/progress", response_class=HTMLResponse)
def progress(pdf: str = Query(...)) -> HTMLResponse:
    pdf_path = validate_pdf_name(pdf)
    output_dir = OUTPUT_DIR / pdf_path.stem

    try:
        view = get_study_view(output_dir)
    except Exception as exc:
        body = f"""
        <h1>Voila! Progress</h1>
        <div class="notice">
          Cannot open Progress Dashboard for <strong>{html.escape(pdf_path.name)}</strong>.
        </div>
        <p>Error: <code>{html.escape(str(exc))}</code></p>
        """
        return page("Voila! Progress", body)

    concepts = view.get("concepts", [])
    total_questions = int(view.get("total_questions") or 0)
    answered_count = int(view.get("answered_count") or 0)
    overall_mastery = int(view.get("overall_mastery_percent") or 0)
    overall_status = html.escape(str(view.get("overall_status") or "No status"))

    weak = [item for item in concepts if float(item.get("mastery", 0)) < 0.40]
    review = [item for item in concepts if 0.40 <= float(item.get("mastery", 0)) < 0.75]
    almost = [item for item in concepts if 0.75 <= float(item.get("mastery", 0)) < 0.90]
    mastered = [item for item in concepts if float(item.get("mastery", 0)) >= 0.90]

    if total_questions > 0:
        answered_percent = round((answered_count / total_questions) * 100)
    else:
        answered_percent = 0

    def concept_list(title: str, items: list, empty: str) -> str:
        rows = []

        for item in items[:12]:
            concept_id = html.escape(str(item.get("concept_id") or ""))
            mastery = int(item.get("mastery_percent") or 0)
            attempts = int(item.get("attempts") or 0)
            correct = int(item.get("correct") or 0)
            incorrect = int(item.get("incorrect") or 0)
            status = html.escape(str(item.get("status") or ""))

            rows.append(
                f"""
                <article class="card">
                  <h2>{concept_id}</h2>
                  <div class="meta">Status: <strong>{status}</strong></div>
                  <p style="font-size: 30px; margin: 8px 0;"><strong>{mastery}%</strong></p>
                  <div style="height: 12px; background: var(--paper-soft); border: 1px solid var(--border); border-radius: 999px; overflow: hidden;">
                    <div style="height: 100%; width: {mastery}%; background: var(--accent);"></div>
                  </div>
                  <div class="meta" style="margin-top: 10px;">
                    Attempts: {attempts}<br>
                    Correct: {correct}<br>
                    Incorrect: {incorrect}
                  </div>
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
        <h2 style="margin-top: 30px;">{html.escape(title)}</h2>
        <div class="grid">
          {''.join(rows)}
        </div>
        """

    recommended = None

    if weak:
        recommended = weak[0]
    elif review:
        recommended = review[0]
    elif almost:
        recommended = almost[0]
    elif concepts:
        recommended = concepts[0]

    if recommended:
        recommended_html = f"""
        <div class="notice">
          Recommended next focus:
          <strong>{html.escape(str(recommended.get("concept_id") or ""))}</strong>
          — mastery <strong>{int(recommended.get("mastery_percent") or 0)}%</strong>.
        </div>
        """
    else:
        recommended_html = """
        <div class="notice">
          No study recommendation yet. Generate a study quiz first.
        </div>
        """

    body = f"""
    <h1>Voila! Progress Dashboard</h1>

    <div class="notice">
      PDF: <strong>{html.escape(pdf_path.name)}</strong><br>
      Overall mastery: <strong>{overall_mastery}%</strong> ·
      Status: <strong>{overall_status}</strong><br>
      Questions answered: <strong>{answered_count}</strong> / <strong>{total_questions}</strong>
      ({answered_percent}%)
    </div>

    {recommended_html}

    <div class="grid">
      <article class="card">
        <h2>Overall mastery</h2>
        <p style="font-size: 34px; margin: 8px 0;"><strong>{overall_mastery}%</strong></p>
        <div style="height: 14px; background: var(--paper-soft); border: 1px solid var(--border); border-radius: 999px; overflow: hidden;">
          <div style="height: 100%; width: {overall_mastery}%; background: var(--accent);"></div>
        </div>
        <div class="meta" style="margin-top: 10px;">{overall_status}</div>
      </article>

      <article class="card">
        <h2>Study coverage</h2>
        <p style="font-size: 34px; margin: 8px 0;"><strong>{answered_percent}%</strong></p>
        <div class="meta">
          Answered: {answered_count}<br>
          Total questions: {total_questions}
        </div>
      </article>

      <article class="card">
        <h2>Concept status</h2>
        <div class="meta">
          Needs review: <strong>{len(weak)}</strong><br>
          In progress: <strong>{len(review)}</strong><br>
          Almost mastered: <strong>{len(almost)}</strong><br>
          Mastered: <strong>{len(mastered)}</strong>
        </div>
      </article>
    </div>

    <div class="actions" style="margin-top: 24px;">
      <a class="btn primary" href="/study?pdf={quote(pdf_path.name)}">Continue Study</a>
      <a class="btn" href="/">Back to Voila!</a>
    </div>

    {concept_list("Needs review", weak, "No weak concepts yet.")}
    {concept_list("In progress", review, "No concepts in this range yet.")}
    {concept_list("Almost mastered", almost, "No almost-mastered concepts yet.")}
    {concept_list("Mastered", mastered, "No mastered concepts yet.")}
    """

    return page("Voila! Progress", body)

'''

if '@app.get("/progress"' not in text:
    text = text.replace('\n@app.get("/study"', route + '\n@app.get("/study"')

path.write_text(text, encoding="utf-8")
print("OK: Progress Dashboard added.")
