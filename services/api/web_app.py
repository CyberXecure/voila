from __future__ import annotations

import html
import json
import shutil
import datetime as dt
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




def crop_editor_is_running() -> bool:
    import socket

    try:
        with socket.create_connection(("127.0.0.1", 8790), timeout=0.5):
            return True
    except OSError:
        return False


def ensure_crop_editor_running() -> None:
    import subprocess
    import sys
    import time

    if crop_editor_is_running():
        return

    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "crop_editor_app:app",
            "--app-dir",
            str(PROJECT_ROOT / "services" / "api"),
            "--host",
            "127.0.0.1",
            "--port",
            "8790",
            "--log-level",
            "info",
        ],
        cwd=str(PROJECT_ROOT),
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    for _ in range(30):
        if crop_editor_is_running():
            return
        time.sleep(0.5)


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
      .floating-nav button {{
        min-width: 84px;
        padding: 7px 10px;
        font-size: 12px;
      }}
    }}
      .floating-nav button {{
        min-width: 84px;
        padding: 7px 10px;
        font-size: 12px;
      }}
    }}

  
    /* Voila fixed navigation */
    body {{
      padding-bottom: 108px;
    }}

    .app-fixed-nav {{
      position: fixed;
      left: 50%;
      bottom: calc(18px + env(safe-area-inset-bottom));
      transform: translateX(-50%);
      z-index: 2147483000;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      max-width: calc(100vw - 32px);
      padding: 10px;
      background: rgba(24, 33, 35, 0.88);
      border: 1px solid var(--border);
      border-radius: 999px;
      box-shadow: 0 18px 48px rgba(0,0,0,0.36);
      backdrop-filter: blur(10px);
    }}

    .app-fixed-nav a,
    .app-fixed-nav button {{
      border: 1px solid var(--border);
      background: var(--paper-soft);
      color: var(--text);
      border-radius: 999px;
      padding: 9px 14px;
      font-weight: 800;
      cursor: pointer;
      text-decoration: none;
      font-size: 14px;
      white-space: nowrap;
      line-height: 1;
    }}

    .app-fixed-nav a.primary,
    .app-fixed-nav button.primary {{
      background: var(--accent);
      color: #fffaf0;
      border-color: var(--accent);
    }}

    .app-fixed-nav button.danger {{
      background: rgba(151, 75, 58, 0.92);
      color: #fffaf0;
      border-color: rgba(151, 75, 58, 0.92);
    }}

    .app-fixed-nav a:hover,
    .app-fixed-nav button:hover {{
      transform: translateY(-1px);
      filter: brightness(1.04);
    }}


    .app-fixed-nav[hidden] {{
      display: none !important;
    }}

    .app-fixed-nav [hidden] {{
      display: none !important;
    }}

    @media (max-width: 760px) {{
      body {{
        padding-bottom: 142px;
      }}

      .app-fixed-nav {{
        left: 10px;
        right: 10px;
        bottom: calc(10px + env(safe-area-inset-bottom));
        transform: none;
        max-width: none;
        flex-wrap: wrap;
        justify-content: center;
        border-radius: 22px;
        padding: 10px;
      }}

      .app-fixed-nav a,
      .app-fixed-nav button {{
        flex: 1 1 30%;
        min-width: 92px;
        padding: 10px 8px;
        font-size: 13px;
        text-align: center;
      }}
    }}
    /* End Voila fixed navigation */

  
    .inline-form {{
      display: inline;
      margin: 0;
    }}

    .btn.danger,
    button.danger {{
      background: rgba(151, 75, 58, 0.92);
      color: #fffaf0;
      border-color: rgba(151, 75, 58, 0.92);
    }}

  
    .btn.danger,
    button.danger {{
      background: rgba(151, 75, 58, 0.92);
      color: #fffaf0;
      border-color: rgba(151, 75, 58, 0.92);
    }}

    .delete-library-form {{
      display: inline-flex;
      margin: 0;
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

    <nav id="appFixedNav" class="app-fixed-nav" aria-label="Voila quick navigation">
      <a class="primary" href="/">Back</a>
      <a id="fixedStudyLink" href="/" hidden>Study</a>
      <a id="fixedReviewLink" href="/" hidden>Review</a>
      <a id="fixedProgressLink" href="/" hidden>Progress</a>
      <button type="button" onclick="window.scrollTo({{ top: 0, behavior: 'smooth' }})">↑ Top</button>
      <button type="button" onclick="window.scrollTo({{ top: document.documentElement.scrollHeight, behavior: 'smooth' }})">↓ Bottom</button>
      <button id="fixedResetButton" class="danger" type="button" hidden>Reset</button>
    </nav>

    <script>
      (function () {{
        const params = new URLSearchParams(window.location.search);
        const pdf = params.get("pdf");
        const path = window.location.pathname;

        const studyLink = document.getElementById("fixedStudyLink");
        const reviewLink = document.getElementById("fixedReviewLink");
        const progressLink = document.getElementById("fixedProgressLink");
        const resetButton = document.getElementById("fixedResetButton");

        if (pdf) {{
          const encodedPdf = encodeURIComponent(pdf);

          if (studyLink && path !== "/study") {{
            studyLink.href = "/study?pdf=" + encodedPdf;
            studyLink.hidden = false;
          }}

          if (progressLink && path !== "/progress") {{
            progressLink.href = "/progress?pdf=" + encodedPdf;
            progressLink.hidden = false;
          }}

          if (resetButton && (path === "/study" || path === "/progress")) {{
            resetButton.hidden = false;

            resetButton.addEventListener("click", function () {{
              const ok = window.confirm("Reset study progress for this PDF?");

              if (!ok) {{
                return;
              }}

              const form = document.createElement("form");
              form.method = "POST";
              form.action = "/study-reset";

              const input = document.createElement("input");
              input.type = "hidden";
              input.name = "pdf_name";
              input.value = pdf;

              form.appendChild(input);
              document.body.appendChild(form);
              form.submit();
            }});
          }}
        }}
      }})();
    </script>


    <script id="same-tab-navigation">
      (function () {{
        document.addEventListener("click", function (event) {{
          const link = event.target.closest("a");

          if (!link) {{
            return;
          }}

          const href = link.getAttribute("href") || "";

          if (
            href.startsWith("/") ||
            href.startsWith("http://127.0.0.1") ||
            href.startsWith("http://localhost")
          ) {{
            link.removeAttribute("target");
          }}
        }});
      }})();
    </script>


    


    <script id="hide-fixed-nav-on-home">
      (function () {{
        function hideHomeNav() {{
          const path = window.location.pathname;
          const nav = document.getElementById("appFixedNav");

          if ((path === "/" || path === "") && nav) {{
            nav.remove();
            document.body.style.paddingBottom = "0";
          }}
        }}

        hideHomeNav();

        if (document.readyState === "loading") {{
          document.addEventListener("DOMContentLoaded", hideHomeNav);
        }} else {{
          hideHomeNav();
        }}
      }})();
    </script>


    <script id="delete-from-library-injector">
      (function () {{
        function injectDeleteButtons() {{
          const path = window.location.pathname;

          if (path !== "/" && path !== "") {{
            return;
          }}

          const cards = document.querySelectorAll(".card");

          cards.forEach(function (card) {{
            if (card.querySelector(".delete-library-form")) {{
              return;
            }}

            const title = card.querySelector("h2, h3");

            if (!title) {{
              return;
            }}

            const pdfName = (title.innerText || "").replace(/\\s+/g, " ").trim();

            if (!pdfName.toLowerCase().endsWith(".pdf")) {{
              return;
            }}

            const form = document.createElement("form");
            form.className = "delete-library-form";
            form.method = "POST";
            form.action = "/delete-from-library";
            form.onsubmit = function () {{
              return window.confirm("Remove this PDF and its generated course from the library? Files will be moved to data/trash, not permanently deleted.");
            }};

            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "pdf_name";
            input.value = pdfName;

            const button = document.createElement("button");
            button.className = "btn danger";
            button.type = "submit";
            button.textContent = "Delete from library";

            form.appendChild(input);
            form.appendChild(button);

            const actions = card.querySelector(".actions");

            if (actions) {{
              actions.appendChild(form);
            }} else {{
              card.appendChild(form);
            }}
          }});
        }}

        injectDeleteButtons();

        if (document.readyState === "loading") {{
          document.addEventListener("DOMContentLoaded", injectDeleteButtons);
        }} else {{
          injectDeleteButtons();
        }}
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



def study_min_page_for_pdf(pdf_path: Path) -> int:
    config_path = PROJECT_ROOT / "data" / "study_config.json"

    if not config_path.exists():
        return 1

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        min_page = int(config.get("default_min_page") or 1)
        per_pdf = config.get("per_pdf") or {}
        pdf_config = per_pdf.get(pdf_path.stem) or {}

        if "min_page" in pdf_config:
            min_page = int(pdf_config["min_page"])

        return max(1, min_page)
    except Exception:
        return 1


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

    study_min_page = study_min_page_for_pdf(pdf_path)

    run_step(
        "8. Build study quiz",
        [
            str(PROJECT_ROOT / "services" / "api" / "study_quiz_builder.py"),
            str(output_dir),
            "--min-page",
            str(study_min_page),
            "--max-per-lesson",
            "4",
            "--max-total",
            "350",
        ],
        log_lines,
    )

    run_step(
        "9. Export figures",
        [str(PROJECT_ROOT / "services" / "api" / "figure_exporter_smart.py"), str(pdf_path)],
        log_lines,
        optional=True,
    )

    run_step(
        "10. Export HTML course",
        [str(PROJECT_ROOT / "services" / "api" / "html_exporter.py"), str(course_cleaned)],
        log_lines,
    )

    run_step(
        "10b. Scanned PDF fallback",
        [
            str(PROJECT_ROOT / "services" / "api" / "scanned_course_fallback.py"),
            str(pdf_path),
            str(output_dir),
            "--zoom",
            "1.45",
        ],
        log_lines,
        optional=True,
    )

    course_html = output_dir / "course.cleaned.html"

    run_step(
        "11. Inject course navigation",
        [
            str(PROJECT_ROOT / "services" / "api" / "course_nav_injector.py"),
            str(course_html),
            pdf_path.name,
        ],
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
                f'<a class="btn" href="{output_url(pdf.stem, "course.cleaned.html")}">Open course</a>'
            )

        if hybrid_figures_html.exists():
            actions.append(
                f'<a class="btn" href="{output_url(pdf.stem, "figures_hybrid", "figures_hybrid.html")}">Figures</a>'
            )

        elif figures_html.exists():
            actions.append(
                f'<a class="btn" href="{output_url(pdf.stem, "figures", "figures.html")}">Figures</a>'
            )

        if hybrid_manifest.exists():
            actions.append(
                f'<a class="btn" href="/edit-crops?pdf={quote(pdf.name)}">Edit crops</a>'
            )

        if quiz_file.exists():
            actions.append(
                f'<a class="btn" href="/study?pdf={quote(pdf.name)}">Study</a>'
            )
            actions.append(
                f'<a class="btn" href="/review?pdf={quote(pdf.name)}">Review weak</a>'
            )
            actions.append(
                f'<a class="btn" href="/progress?pdf={quote(pdf.name)}">Progress</a>'
            )

        if log_file.exists():
            actions.append(
                f'<a class="btn" href="/log?pdf={quote(pdf.name)}">Logs</a>'
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





def trash_course_output(output_dir: Path) -> Path | None:
    if not output_dir.exists():
        return None

    trash_dir = PROJECT_ROOT / "data" / "trash" / "courses"
    trash_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = trash_dir / f"{output_dir.name}_{stamp}"

    shutil.move(str(output_dir), str(target))

    return target



def trash_input_pdf(pdf_path: Path) -> Path | None:
    if not pdf_path.exists():
        return None

    trash_dir = PROJECT_ROOT / "data" / "trash" / "pdfs"
    trash_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = trash_dir / f"{pdf_path.stem}_{stamp}{pdf_path.suffix}"

    shutil.move(str(pdf_path), str(target))

    return target


@app.post("/delete-course")
def delete_course(pdf_name: str = Form(...)) -> RedirectResponse:
    pdf_path = validate_pdf_name(pdf_name)
    output_dir = OUTPUT_DIR / pdf_path.stem

    trash_course_output(output_dir)
    trash_input_pdf(pdf_path)

    return RedirectResponse(
        url="/",
        status_code=303,
    )



def move_to_trash(source: Path, trash_subdir: str) -> Path | None:
    if not source.exists():
        return None

    trash_dir = PROJECT_ROOT / "data" / "trash" / trash_subdir
    trash_dir.mkdir(parents=True, exist_ok=True)

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")

    if source.is_dir():
        target = trash_dir / f"{source.name}_{stamp}"
    else:
        target = trash_dir / f"{source.stem}_{stamp}{source.suffix}"

    shutil.move(str(source), str(target))

    return target


@app.post("/delete-from-library")
def delete_from_library(pdf_name: str = Form(...)) -> RedirectResponse:
    pdf_path = validate_pdf_name(pdf_name)
    output_dir = OUTPUT_DIR / pdf_path.stem

    move_to_trash(output_dir, "courses")
    move_to_trash(pdf_path, "pdfs")

    return RedirectResponse(
        url="/",
        status_code=303,
    )



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








@app.get("/edit-crops")
def edit_crops(pdf: str = ""):
    from fastapi.responses import HTMLResponse, RedirectResponse
    from urllib.parse import quote

    ensure_crop_editor_running()

    if not crop_editor_is_running():
        return HTMLResponse(
            """
            <h1>Crop Editor did not start</h1>
            <p>Port 8790 is not responding. Start it manually:</p>
            <pre>python -m uvicorn crop_editor_app:app --app-dir services/api --host 127.0.0.1 --port 8790</pre>
            """,
            status_code=503,
        )

    if pdf:
        return RedirectResponse("http://127.0.0.1:8790/?pdf=" + quote(pdf))

    return RedirectResponse("http://127.0.0.1:8790/")

