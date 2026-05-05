from __future__ import annotations

import html
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from study_engine import get_study_view, record_answer, reset_study_state


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = PROJECT_ROOT / "data" / "input"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"

APP_TITLE = "Voila! Local"


app = FastAPI(title=APP_TITLE)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
INPUT_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")


def page(title: str, body: str) -> HTMLResponse:
    doc = f"""<!doctype html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #e8dfd0;
      --paper: #f5ecd9;
      --paper-soft: #efe3cc;
      --text: #2f2a24;
      --muted: #75695c;
      --heading: #241e19;
      --accent: #8a5a32;
      --accent-strong: #65401f;
      --border: #d7c5a8;
      --ok: #2f6f6d;
      --danger: #9f3a2f;
      --shadow: rgba(62, 45, 28, 0.16);
    }}

    html[data-theme="dark"] {{
      --bg: #151a1d;
      --paper: #20272b;
      --paper-soft: #263035;
      --text: #d8d0c3;
      --muted: #a79d90;
      --heading: #f1e7d8;
      --accent: #d7a86e;
      --accent-strong: #f0c98d;
      --border: #3a444a;
      --ok: #72b8b2;
      --danger: #d66b5d;
      --shadow: rgba(0, 0, 0, 0.34);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      background:
        radial-gradient(circle at top left, rgba(138, 90, 50, 0.14), transparent 34%),
        linear-gradient(180deg, var(--paper-soft) 0%, var(--bg) 100%);
      color: var(--text);
      font-family: "Segoe UI", Arial, sans-serif;
      line-height: 1.6;
      font-size: 16px;
    }}

    html[data-theme="dark"] body {{
      background:
        radial-gradient(circle at top left, rgba(215, 168, 110, 0.10), transparent 34%),
        linear-gradient(180deg, #1b2226 0%, var(--bg) 100%);
    }}

    .wrap {{
      max-width: 1120px;
      margin: 34px auto;
      padding: 0 20px;
    }}

    header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      margin-bottom: 24px;
    }}

    .brand h1 {{
      margin: 0;
      color: var(--heading);
      font-size: 36px;
      letter-spacing: -0.04em;
    }}

    .brand p {{
      margin: 5px 0 0;
      color: var(--muted);
    }}

    .theme-toggle {{
      border: 1px solid var(--border);
      background: var(--paper);
      color: var(--text);
      border-radius: 999px;
      padding: 10px 14px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 8px 24px var(--shadow);
    }}

    .panel {{
      background: var(--paper);
      border: 1px solid var(--border);
      border-radius: 24px;
      box-shadow: 0 22px 58px var(--shadow);
      padding: 26px;
    }}

    .notice {{
      background: var(--paper-soft);
      border: 1px solid var(--border);
      color: var(--muted);
      border-radius: 16px;
      padding: 14px 16px;
      margin-bottom: 20px;
    }}


    .upload-box {{
      background: var(--paper-soft);
      border: 1px dashed var(--accent);
      border-radius: 18px;
      padding: 18px;
      margin-bottom: 20px;
    }}

    .upload-box h2 {{
      margin: 0 0 8px;
      color: var(--heading);
      font-size: 20px;
    }}

    .upload-form {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 12px;
      margin-top: 12px;
    }}

    input[type="file"] {{
      border: 1px solid var(--border);
      background: var(--paper);
      color: var(--text);
      border-radius: 999px;
      padding: 6px 12px 6px 6px;
      max-width: 100%;
      min-width: 420px;
      cursor: pointer;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }}

    input[type="file"]::file-selector-button {{
      border: 1px solid var(--border);
      background: var(--paper-soft);
      color: var(--text);
      border-radius: 999px;
      padding: 9px 15px;
      margin-right: 12px;
      font-weight: 700;
      cursor: pointer;
    }}

    input[type="file"]::file-selector-button:hover {{
      border-color: var(--accent);
      background: var(--accent);
      color: #fffaf0;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(310px, 1fr));
      gap: 18px;
    }}

    .card {{
      background: var(--paper-soft);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 18px;
    }}

    .card h2 {{
      margin: 0 0 8px;
      color: var(--heading);
      font-size: 20px;
      line-height: 1.25;
      word-break: break-word;
    }}

    .meta {{
      color: var(--muted);
      font-size: 14px;
      margin: 6px 0 14px;
    }}

    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 14px;
    }}

    button,
    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--border);
      background: var(--paper);
      color: var(--text);
      border-radius: 999px;
      padding: 9px 13px;
      font-size: 14px;
      font-weight: 700;
      text-decoration: none;
      cursor: pointer;
    }}

    button.primary,
    .btn.primary {{
      background: var(--accent);
      border-color: var(--accent);
      color: #fffaf0;
    }}

    .status {{
      display: inline-block;
      border-radius: 999px;
      padding: 4px 9px;
      font-size: 13px;
      font-weight: 700;
      background: rgba(47, 111, 109, 0.13);
      color: var(--ok);
      border: 1px solid rgba(47, 111, 109, 0.28);
    }}

    .status.missing {{
      color: var(--danger);
      background: rgba(159, 58, 47, 0.10);
      border-color: rgba(159, 58, 47, 0.25);
    }}

    code {{
      background: var(--paper-soft);
      border: 1px solid var(--border);
      padding: 2px 6px;
      border-radius: 7px;
    }}
  </style>
  <script>
    (function () {{
      const saved = localStorage.getItem("voila-ui-theme");
      const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
      document.documentElement.setAttribute("data-theme", saved || (prefersDark ? "dark" : "light"));
    }})();
  </script>
</head>
<body>
  <div class="wrap">
    <header>
      <div class="brand">
        <h1>Voila!</h1>
        <p>Your local PDF learning studio</p>
      </div>
      <button class="theme-toggle" id="themeToggle" type="button">Toggle theme</button>
    </header>

    <section class="panel">
      {body}
    </section>
  </div>

  <script>
    (function () {{
      const root = document.documentElement;
      const button = document.getElementById("themeToggle");

      function label() {{
        const theme = root.getAttribute("data-theme");
        button.textContent = theme === "dark" ? "☀ Light mode" : "🌙 Dark mode";
      }}

      button.addEventListener("click", function () {{
        const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", next);
        localStorage.setItem("voila-ui-theme", next);
        label();
      }});

      label();
    }})();
  </script>
</body>
</html>
"""
    return HTMLResponse(doc)


def output_url(*parts: str) -> str:
    rel = "/".join(quote(str(part).replace("\\", "/"), safe="") for part in parts)
    return "/output/" + rel


def pdfs() -> list[Path]:
    return sorted(INPUT_DIR.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)


def validate_pdf_name(pdf_name: str) -> Path:
    pdf_path = INPUT_DIR / pdf_name

    if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
        raise FileNotFoundError(f"PDF not found in data/input: {pdf_name}")

    if pdf_path.resolve().parent != INPUT_DIR.resolve():
        raise ValueError("Invalid PDF path.")

    return pdf_path



def safe_upload_name(filename: str) -> str:
    name = Path(filename or "").name
    suffix = Path(name).suffix.lower()

    if suffix != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    stem = Path(name).stem
    stem = re.sub(r"[^A-Za-z0-9._ -]+", "_", stem).strip(" ._")

    if not stem:
        stem = "document"

    return stem + ".pdf"


def run_step(label: str, args: list[str], log_lines: list[str], optional: bool = False) -> None:
    cmd = [sys.executable, *args]

    log_lines.append("")
    log_lines.append(f"=== {label} ===")
    log_lines.append(" ".join(str(part) for part in cmd))

    result = subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.stdout:
        log_lines.append(result.stdout.strip())

    if result.stderr:
        log_lines.append("STDERR:")
        log_lines.append(result.stderr.strip())

    if result.returncode != 0:
        message = f"Step failed: {label} / exit code {result.returncode}"

        if optional:
            log_lines.append("WARNING: " + message)
            return

        raise RuntimeError(message)


def generate_for_pdf(pdf_path: Path) -> Path:
    output_dir = OUTPUT_DIR / pdf_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    log_lines: list[str] = []
    log_lines.append(f"Voila! local generation")
    log_lines.append(f"Input PDF: {pdf_path}")

    pages_json = output_dir / "pages.json"
    outline_json = output_dir / "course_outline.json"
    normalized_json = output_dir / "course_outline.normalized.json"
    course_cleaned = output_dir / "course.cleaned.md"

    run_step(
        "1. PDF extract",
        [
            str(PROJECT_ROOT / "services" / "api" / "pdf_extract.py"),
            str(pdf_path),
            "--output-dir",
            str(OUTPUT_DIR),
        ],
        log_lines,
    )

    run_step(
        "2. OCR report",
        [str(PROJECT_ROOT / "services" / "api" / "ocr_report.py"), str(pages_json)],
        log_lines,
    )

    run_step(
        "3. Course outline",
        [str(PROJECT_ROOT / "services" / "api" / "outline_builder.py"), str(pages_json)],
        log_lines,
    )

    run_step(
        "4. Normalize outline",
        [str(PROJECT_ROOT / "services" / "api" / "normalize_outline.py"), str(outline_json)],
        log_lines,
    )

    run_step(
        "5. Generate course files",
        [str(PROJECT_ROOT / "services" / "api" / "course_generator.py"), str(normalized_json)],
        log_lines,
    )

    run_step(
        "6. Polish course",
        [str(PROJECT_ROOT / "services" / "api" / "course_polisher.py"), str(normalized_json)],
        log_lines,
    )

    run_step(
        "7. Final cleanup",
        [str(PROJECT_ROOT / "services" / "api" / "course_cleaned_finalizer.py"), str(course_cleaned)],
        log_lines,
    )

    run_step(
        "8. Export figures",
        [str(PROJECT_ROOT / "services" / "api" / "figure_exporter_hybrid.py"), str(pdf_path)],
        log_lines,
        optional=True,
    )

    run_step(
        "9. Export HTML course",
        [str(PROJECT_ROOT / "services" / "api" / "html_exporter.py"), str(course_cleaned)],
        log_lines,
    )

    log_path = output_dir / "last_run.log"
    log_path.write_text("\n".join(log_lines), encoding="utf-8")

    return output_dir


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def home(generated: str | None = Query(default=None), uploaded: str | None = Query(default=None)) -> HTMLResponse:
    cards = []

    upload_box = """
        <div class="upload-box">
          <h2>Upload PDF</h2>
          <div class="meta">Choose a PDF from your computer. It will be saved locally in <code>data/input</code>.</div>
          <form class="upload-form" method="post" action="/upload" enctype="multipart/form-data">
            <input type="file" name="file" accept="application/pdf" required>
            <button class="primary" type="submit">Upload PDF</button>
          </form>
        </div>
        """

    for pdf in pdfs():
        out_dir = OUTPUT_DIR / pdf.stem
        course_html = out_dir / "course.cleaned.html"
        figures_html = out_dir / "figures" / "figures.html"
        hybrid_figures_html = out_dir / "figures_hybrid" / "figures_hybrid.html"
        hybrid_manifest = out_dir / "figures_hybrid" / "figures_manifest.hybrid.json"
        log_file = out_dir / "last_run.log"
        quiz_file = out_dir / "quiz.json"

        size_mb = pdf.stat().st_size / (1024 * 1024)

        status = (
            '<span class="status">Course generated</span>'
            if course_html.exists()
            else '<span class="status missing">Not generated yet</span>'
        )

        actions = [
            f"""
            <form method="post" action="/generate">
              <input type="hidden" name="pdf_name" value="{html.escape(pdf.name)}">
              <button class="primary" type="submit">Generate course</button>
            </form>
            """
        ]

        if course_html.exists():
            actions.append(
                f'<a class="btn" target="_blank" href="{output_url(pdf.stem, "course.cleaned.html")}">Open course</a>'
            )

        if hybrid_figures_html.exists():
            actions.append(
                f'<a class="btn" target="_blank" href="{output_url(pdf.stem, "figures_hybrid", "figures_hybrid.html")}">Figures</a>'
            )

        elif figures_html.exists():
            actions.append(
                f'<a class="btn" target="_blank" href="{output_url(pdf.stem, "figures", "figures.html")}">Figures</a>'
            )

        if hybrid_manifest.exists():
            actions.append(
                f'<a class="btn" target="_blank" href="http://127.0.0.1:8790/?pdf={quote(pdf.name)}">Edit crops</a>'
            )

        if quiz_file.exists():
            actions.append(
                f'<a class="btn" target="_blank" href="/study?pdf={quote(pdf.name)}">Study</a>'
            )

        if log_file.exists():
            actions.append(
                f'<a class="btn" target="_blank" href="/log?pdf={quote(pdf.name)}">Logs</a>'
            )

        cards.append(
            f"""
            <article class="card">
              <h2>{html.escape(pdf.name)}</h2>
              <div class="meta">{size_mb:.2f} MB · {status}</div>
              <div class="actions">
                {''.join(actions)}
              </div>
            </article>
            """
        )

    if not cards:
        body = upload_box + """
        <div class="notice">
          No PDF files found. Put a PDF in <code>data/input</code>, then refresh this page.
        </div>
        """
    else:
        notice = ""

        if uploaded:
            notice += f"""
            <div class="notice">
              Uploaded: <strong>{html.escape(uploaded)}</strong>
            </div>
            """

        if generated:
            notice += f"""
            <div class="notice">
              Generated: <strong>{html.escape(generated)}</strong>
            </div>
            """

        body = upload_box + f"""
        {notice}
        <div class="notice">
          Source Mode: no translation, local processing, original PDF text preserved.
        </div>
        <div class="grid">
          {''.join(cards)}
        </div>
        """

    return page(APP_TITLE, body)


@app.post("/generate")
def generate(pdf_name: str = Form(...)) -> RedirectResponse:
    pdf_path = validate_pdf_name(pdf_name)
    generate_for_pdf(pdf_path)

    return RedirectResponse(
        url="/?generated=" + quote(pdf_name),
        status_code=303,
    )


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)) -> RedirectResponse:
    filename = safe_upload_name(file.filename or "document.pdf")
    destination = INPUT_DIR / filename

    if destination.exists():
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = INPUT_DIR / f"{destination.stem}_{stamp}.pdf"

    with destination.open("wb") as handle:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)

    return RedirectResponse(
        url="/?uploaded=" + quote(destination.name),
        status_code=303,
    )



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


@app.get("/log")
def log(pdf: str = Query(...)) -> PlainTextResponse:
    pdf_path = validate_pdf_name(pdf)
    log_path = OUTPUT_DIR / pdf_path.stem / "last_run.log"

    if not log_path.exists():
        return PlainTextResponse("No log file found yet.", status_code=404)

    return PlainTextResponse(log_path.read_text(encoding="utf-8"))


