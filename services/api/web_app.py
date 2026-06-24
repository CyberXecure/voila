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
import exam_prep


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = PROJECT_ROOT / "data" / "input"
VOILA_LIMITED_TESTER_DEMO = True
VOILA_TESTER_DEMO_MAX_PAGES = 12
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


def _ui_texts() -> dict:
    try:
        import i18n
        return i18n.get_ui_language(PROJECT_ROOT).get("translations", {})
    except Exception:
        return {}


def _ut(key: str, fallback: str) -> str:
    return str(_ui_texts().get(key) or fallback)


def _utf(key: str, fallback: str, **kwargs) -> str:
    template = _ut(key, fallback)
    try:
        return template.format(**kwargs)
    except Exception:
        return fallback.format(**kwargs)


def _build_study_question_display(question: dict, pdf_name: str) -> str:
    try:
        import study_questions
        return study_questions.build_study_question(PROJECT_ROOT, pdf_name, question)
    except Exception:
        try:
            return _study_question_display(str(question.get("question") or ""))
        except Exception:
            return str(question.get("question") or "")


def _study_question_display(value: str) -> str:
    import re

    raw = str(value or "").strip()

    patterns = [
        r"^What technical point does the source state about\s+(.+?)\??$",
        r"^Under what condition or operating situation does the source describe\s+(.+?)\??$",
        r"^Name one key point supported by the source text in\s+['\"“”‘’](.+?)['\"“”‘’]\.?$",
        r"^Name one key point supported by the source text in\s+(.+?)\.?$",
        r"^What does the source state about\s+(.+?)\??$",
        r"^What does the text say about\s+(.+?)\??$",
        r"^What is stated about\s+(.+?)\??$",
        r"^What is the source saying about\s+(.+?)\??$",
    ]

    for pattern in patterns:
        match = re.match(pattern, raw, flags=re.IGNORECASE)

        if not match:
            continue

        concept = match.group(1).strip()
        concept = concept.rstrip(".?").strip()
        concept = concept.strip("'\"“”‘’")

        if concept:
            return _utf(
                "study_question_important_idea",
                "What important idea does the source support about “{concept}”?",
                concept=concept,
            )

    return raw


def _study_status_label(value: str) -> str:
    raw = str(value or "").strip()
    key = raw.lower().replace(" ", "_").replace("-", "_")

    mapping = {
        "needs_review": _ut("needs_review", "Needs review"),
        "in_progress": _ut("in_progress", "In progress"),
        "almost_mastered": _ut("almost_mastered", "Almost mastered"),
        "mastered": _ut("mastered", "Mastered"),
    }

    return mapping.get(key, raw)

def _ui_language_code() -> str:
    try:
        import i18n

        return str(i18n.get_ui_language(PROJECT_ROOT).get("ui_language") or "en").lower()
    except Exception:
        return "en"


def _study_recommendation_reason_label(value: str) -> str:
    raw = str(value or "").strip()

    if not raw:
        return ""

    parts = [part.strip() for part in raw.split("·")]
    reason_key = parts[0].lower() if parts else raw.lower()
    qtype = parts[1].lower() if len(parts) > 1 else ""

    lang = _ui_language_code()

    reason_labels = {
        "ro": {
            "new concept": "concept nou",
            "recent mistakes": "greșeli recente",
            "low mastery": "nivel redus",
            "in progress": "în progres",
            "due now": "scadent acum",
            "due today": "scadent azi",
            "due later": "programat mai târziu",
            "mastered review": "revizuire de consolidare",
            "scheduled review": "revizuire programată",
        },
        "en": {
            "new concept": "new concept",
            "recent mistakes": "recent mistakes",
            "low mastery": "low mastery",
            "in progress": "in progress",
            "due now": "due now",
            "due today": "due today",
            "due later": "due later",
            "mastered review": "mastered review",
            "scheduled review": "scheduled review",
        },
    }

    type_labels = {
        "ro": {
            "definition": "definiție",
            "components": "componente",
            "purpose": "scop",
            "requirement": "cerință",
            "condition": "condiție",
            "cause_effect": "cauză/efect",
            "comparison": "comparație",
            "example": "exemplu",
            "process": "proces",
            "numeric_check": "verificare numerică",
            "visual_interpretation": "interpretare vizuală",
            "technical_fact": "precizare tehnică",
        },
        "en": {
            "definition": "definition",
            "components": "components",
            "purpose": "purpose",
            "requirement": "requirement",
            "condition": "condition",
            "cause_effect": "cause/effect",
            "comparison": "comparison",
            "example": "example",
            "process": "process",
            "numeric_check": "numeric check",
            "visual_interpretation": "visual interpretation",
            "technical_fact": "technical fact",
        },
    }

    labels_lang = "ro" if lang == "ro" else "en"

    reason = reason_labels[labels_lang].get(reason_key, parts[0] if parts else raw)

    if not qtype:
        return reason

    qtype_label = type_labels[labels_lang].get(qtype, qtype.replace("_", " "))

    return f"{reason} · {qtype_label}"



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

    .top-nav {{
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 10px;
      flex-wrap: wrap;
    }}

    .nav-pill {{
      min-height: 42px;
      box-sizing: border-box;
      border-radius: 999px;
      padding: 10px 14px;
      text-decoration: none;
      font-weight: 800;
      line-height: 1.2;
      white-space: nowrap;
    }}

    .nav-pill-primary {{
      background: var(--accent);
      border: 1px solid var(--accent);
      color: #fffaf0;
    }}

    .nav-pill-exam {{
      background: #8b5cf6;
      border: 1px solid #8b5cf6;
      color: #fffaf0;
    }}

    .top-nav .theme-toggle {{
      margin: 0;
      background: var(--paper);
      border-color: var(--border);
      color: var(--text);
    }}

    @media (max-width: 760px) {{
      header {{
        align-items: flex-start;
      }}

      .top-nav {{
        justify-content: flex-start;
        width: 100%;
      }}
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

    .library-delete-actions {{
      margin-top: 16px;
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


<style>
  .primary-tool {{
    background: #e0ad68 !important;
    color: #fff !important;
    border-color: transparent !important;
    font-weight: 900 !important;
  }}

  .tool-link {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    padding: 10px 14px;
    margin: 4px;
    text-decoration: none;
  }}
</style>


</head>
<body>
  <div class="wrap">
    <header>
      <div class="brand">
        <h1>{_ut("ui.heading.home", "Voila!")}</h1>
        <p>{_ut("ui.message.local_pdf_learning_studio", "Your local PDF learning studio")}</p>
      </div>
      <nav class="top-nav" aria-label="Primary">
        <a class="nav-pill nav-pill-primary" href="/quick-tools">{_ut("ui.quick_tools", "Quick Tools")}</a>
        <a class="nav-pill nav-pill-exam" href="/exam-prep">{_ut("ui.exam_prep", "Exam Prep")}</a>
        <button class="theme-toggle nav-pill" id="themeToggle" type="button">{_ut("ui.toggle_theme", "Toggle theme")}</button>
      </nav>
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
      <a class="primary" href="/">{_ut("ui.link.back", "Back")}</a>
      <a id="fixedStudyLink" href="/" hidden>{_ut("ui.study", _ut("study", "Study"))}</a>
      <a id="fixedReviewLink" href="/" hidden>{_ut("ui.review_weak", "Review due")}</a>
      <a id="fixedProgressLink" href="/" hidden>{_ut("ui.progress", _ut("progress", "Progress"))}</a>
      <button type="button" onclick="window.scrollTo({{ top: 0, behavior: 'smooth' }})">↑ {_ut("top", "Top")}</button>
      <button type="button" onclick="window.scrollTo({{ top: document.documentElement.scrollHeight, behavior: 'smooth' }})">↓ {_ut("bottom", "Bottom")}</button>
      <button id="fixedResetButton" class="danger" type="button" hidden>{_ut("reset", "Reset")}</button>
    </nav>

    <script>
      (function () {{
        const params = new URLSearchParams(window.location.search);
        const floatingNav = document.getElementById("floatingNav");
        const simpleDashboardPaths = new Set(["/", "/exam-prep", "/quick-tools"]);
        if (floatingNav && simpleDashboardPaths.has(window.location.pathname)) {{
          floatingNav.hidden = true;
        }}
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

          if (reviewLink && path !== "/review") {{
            reviewLink.href = "/review?pdf=" + encodedPdf;
            reviewLink.hidden = false;
          }}

          if (progressLink && path !== "/progress") {{
            progressLink.href = "/progress?pdf=" + encodedPdf;
            progressLink.hidden = false;
          }}

          if (resetButton && (path === "/study" || path === "/progress")) {{
            resetButton.hidden = false;

            resetButton.addEventListener("click", function () {{
              const ok = window.confirm("{_ut("reset_confirm", "Reset study progress for this PDF?")}");

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
              return window.confirm("{_ut("ui.delete_from_library_confirm", "Remove this PDF and its generated course from the library? Files will be moved to data/trash, not permanently deleted.")}");
            }};

            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "pdf_name";
            input.value = pdfName;

            const button = document.createElement("button");
            button.className = "btn danger";
            button.type = "submit";
            button.textContent = "{_ut("ui.delete_from_library", "Delete from library")}";

            form.appendChild(input);
            form.appendChild(button);

            const deleteActions = card.querySelector(".library-delete-actions");
            const actions = deleteActions || card.querySelector(".actions");

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


def limited_tester_demo_page_count(pdf_path: Path) -> int:
    import fitz

    doc = fitz.open(pdf_path)
    try:
        return int(doc.page_count)
    finally:
        doc.close()


def limited_tester_demo_message(page_count: int | None = None) -> str:
    base = (
        f"Voila! Limited Tester Demo is limited to "
        f"{VOILA_TESTER_DEMO_MAX_PAGES} pages per PDF. "
        "Please use a small non-confidential sample document."
    )
    if page_count is not None:
        return f"{base} This PDF has {page_count} pages."
    return base


def limited_tester_demo_limit_response(detail: str) -> HTMLResponse:
    return HTMLResponse(
        f"""
        <h1>Voila! Limited Tester Demo</h1>
        <p>{html.escape(detail)}</p>
        <p>Do not use confidential, personal, legal, medical, financial, safety-critical or sensitive documents.</p>
        <p><a href="/">Back to Voila</a></p>
        """,
        status_code=400,
    )


def enforce_limited_tester_demo_pdf_limit(pdf_path: Path) -> None:
    if not VOILA_LIMITED_TESTER_DEMO:
        return

    page_count = limited_tester_demo_page_count(pdf_path)

    if page_count > VOILA_TESTER_DEMO_MAX_PAGES:
        raise HTTPException(
            status_code=400,
            detail=limited_tester_demo_message(page_count),
        )


def safe_upload_name(filename: str) -> str:
    name = Path(filename or "").name
    suffix = Path(name).suffix.lower()

    if suffix != ".pdf":
        raise HTTPException(status_code=400, detail=_ut("error.only_pdf_files_supported", "Only PDF files are supported."))

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



@app.get("/exam-prep", response_class=HTMLResponse)
def exam_prep_home() -> HTMLResponse:
    dashboard = exam_prep.bac_matematica_m1_dashboard()

    def exam_prep_status_label(mastery: float, attempts: int) -> str:
        if attempts <= 0:
            return _ut("exam_prep.status.no_attempts", "Not started")
        if mastery < 0.40:
            return _ut("exam_prep.status.needs_review", "Needs review")
        if mastery < 0.75:
            return _ut("exam_prep.status.in_progress", "In progress")
        if mastery < 0.90:
            return _ut("exam_prep.status.almost_consolidated", "Almost mastered")
        return _ut("exam_prep.status.consolidated", "Mastered")

    rows = []
    for skill in dashboard.get("skills", []):
        mastery = float(skill.get("mastery") or 0.0)
        attempts = int(skill.get("attempts") or 0)
        correct = int(skill.get("correct") or 0)
        mastery_percent = int(round(mastery * 100))
        status_label = html.escape(exam_prep_status_label(mastery, attempts))

        rows.append(
            f"""
            <article class="card">
              <h2>{html.escape(str(skill.get("name") or ""))}</h2>
              <p>{html.escape(str(skill.get("description") or ""))}</p>
              <div class="meta">
                {_ut("exam_prep.consolidated", "Mastery")}: <strong>{mastery_percent}%</strong><br>
                {_ut("exam_prep.status_label", "Status")}: <strong>{status_label}</strong><br>
                {_ut("exam_prep.attempts", "Attempts")}: <strong>{attempts}</strong><br>
                {_ut("exam_prep.correct", "Correct")}: <strong>{correct}</strong>
              </div>
            </article>
            """
        )

    body = f"""
    <h1>{_ut("ui.exam_prep_title", "Voila! Exam Prep")}</h1>

    <div class="notice">
      <strong>{_ut("exam_prep.bac_matematica_m1", "Baccalaureate → Mathematics M1")}</strong><br>
      {_ut("exam_prep.foundation_description", "Foundation dashboard for skill-based exam preparation. Progress is updated from Study Mode.")}
    </div>

    <section class="grid">
      {''.join(rows)}
    </section>

    <div class="actions" style="margin-top: 24px;">
      <a class="btn primary" href="/">{_ut("ui.link.back_to_voila", "Back to Voila!")}</a>
    </div>
    """

    return page(_ut("ui.exam_prep_title", "Voila! Exam Prep"), body)
@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def home(generated: str | None = Query(default=None), uploaded: str | None = Query(default=None)) -> HTMLResponse:
    cards = []
    no_file_selected = html.escape(_ut("ui.no_file_selected", "No file selected"), quote=True)

    upload_box = f"""
        <div class="upload-box">
          <h2>{_ut("ui.upload_pdf", "Upload PDF")}</h2>
          <div class="meta">{_ut("message.choose_pdf_from_computer", "Choose a PDF from your computer. It will be saved locally in <code>data/input</code>.")}</div>
          <div class="meta">{_ut("message.limited_tester_demo_notice", "<strong>Voila! Limited Tester Demo:</strong> maximum 12 pages per PDF. Use only small, non-confidential sample documents.")}</div>
          <form class="upload-form" method="post" action="/upload" enctype="multipart/form-data">
            <input id="pdfUploadInput" style="position:absolute;left:-9999px;width:1px;height:1px;opacity:0;" type="file" name="file" accept="application/pdf" required onchange="document.getElementById('selectedFileName').textContent = this.files && this.files[0] ? this.files[0].name : '{no_file_selected}';">
            <label class="btn" for="pdfUploadInput">{_ut("ui.choose_file", "Choose file")}</label>
            <span id="selectedFileName" class="meta">{_ut("ui.no_file_selected", "No file selected")}</span>
            <button class="primary" type="submit">{_ut("ui.upload_pdf", "Upload PDF")}</button>
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
            f'<span class="status">{_ut("ui.generated", "Generated")}</span>'
            if course_html.exists()
            else f'<span class="status missing">{_ut("status.not_generated_yet", "Not generated yet")}</span>'
        )
        generate_label = (
            _ut("ui.regenerate_course", "Regenerate course")
            if course_html.exists()
            else _ut("ui.generate_course", "Generate course")
        )
        actions = [
            f"""
            <form method="post" action="/generate">
              <input type="hidden" name="pdf_name" value="{html.escape(pdf.name)}">
              <button class="primary" type="submit">{generate_label}</button>
            </form>
            """
        ]

        if course_html.exists():
            actions.append(
                f'<a class="btn" href="{output_url(pdf.stem, "course.cleaned.html")}">{_ut("ui.open_course", _ut("open_course", "Open course"))}</a>'
            )

        if hybrid_figures_html.exists():
            actions.append(
                f'<a class="btn" href="{output_url(pdf.stem, "figures_hybrid", "figures_hybrid.html")}">{_ut("ui.figures", "Figures")}</a>'
            )

        elif figures_html.exists():
            actions.append(
                f'<a class="btn" href="{output_url(pdf.stem, "figures", "figures.html")}">{_ut("ui.figures", "Figures")}</a>'
            )

        if hybrid_manifest.exists():
            actions.append(
                f'<a class="btn" href="/edit-crops?pdf={quote(pdf.name)}">{_ut("ui.edit_crops", "Edit crops")}</a>'
            )

        if quiz_file.exists():
            actions.append(
                f'<a class="btn" href="/study?pdf={quote(pdf.name)}">{_ut("ui.study", _ut("study", "Study"))}</a>'
            )
            actions.append(
                f'<a class="btn" href="/progress?pdf={quote(pdf.name)}">{_ut("ui.progress", _ut("progress", "Progress"))}</a>'
            )
            actions.append(
                f'<a class="btn" href="/exam-prep">{_ut("ui.exam_prep", "Exam Prep")}</a>'
            )
            actions.append(
                f'<a class="btn" href="/review?pdf={quote(pdf.name)}">{_ut("ui.review_weak", "Review weak")}</a>'
            )

        if log_file.exists():
            actions.append(
                f'<a class="btn" href="/log?pdf={quote(pdf.name)}">{_ut("ui.logs", "Logs")}</a>'
            )
        cards.append(
            f"""
            <article class="card">
              <h2>{html.escape(pdf.name)}</h2>
              <div class="meta">{size_mb:.2f} MB · {status}</div>
              <div class="actions">
                {''.join(actions)}
              </div>
              <div class="actions library-delete-actions"></div>
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
              {_ut("status.uploaded", "Uploaded")}: <strong>{html.escape(uploaded)}</strong>
            </div>
            """

        if generated:
            notice += f"""
            <div class="notice">
              {_ut("ui.generated", "Generated")}: <strong>{html.escape(generated)}</strong>
            </div>
            """

        body = upload_box + f"""
        {notice}
        <div class="notice">
          {_ut("ui.source_mode", "Source Mode")}: {_ut("message.source_mode_description", "No translation, local processing, original PDF text preserved.")}
        </div>
        <div class="grid">
          {''.join(cards)}
        </div>
        """

    return page(APP_TITLE, body)


@app.post("/generate")
def generate(pdf_name: str = Form(...)):
    pdf_path = validate_pdf_name(pdf_name)
    try:
        enforce_limited_tester_demo_pdf_limit(pdf_path)
    except HTTPException as exc:
        return limited_tester_demo_limit_response(str(exc.detail))
    generate_for_pdf(pdf_path)

    return RedirectResponse(
        url="/?generated=" + quote(pdf_name),
        status_code=303,
    )


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
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

    try:
        enforce_limited_tester_demo_pdf_limit(destination)
    except HTTPException as exc:
        destination.unlink(missing_ok=True)
        return limited_tester_demo_limit_response(str(exc.detail))

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

    current = view.get("current_question")
    if isinstance(current, dict) and current.get("question_id"):
        return current

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
        <h1>{_ut("ui.heading.review", "Voila! Review")}</h1>
        <div class="notice">
          Cannot open Review Mode for <strong>{html.escape(pdf_path.name)}</strong>.
        </div>
        <p>Error: <code>{html.escape(str(exc))}</code></p>
        """
        return page("Voila! Review", body)

    concepts = view.get("concepts") or []

    def review_bucket_label(value: str) -> str:
        raw = str(value or "").strip().lower()
        mapping = {
            "due_now": _ut("due_now", "Due now"),
            "due_today": _ut("due_today", "Due today"),
            "due_later": _ut("due_later", "Due later"),
            "mastered_review": _ut("mastered_review", "Mastered review"),
            "new_concept": _ut("new_concept", "New concept"),
        }
        return mapping.get(raw, raw.replace("_", " ") if raw else _ut("not_available", "Not available"))

    def review_timestamp_label(value) -> str:
        raw = str(value or "").strip()
        if not raw:
            return _ut("not_available", "Not available")
        return raw.replace("T", " ").replace("Z", "")[:19]

    due_now = [item for item in concepts if str(item.get("review_bucket") or "") == "due_now"]
    due_today = [item for item in concepts if str(item.get("review_bucket") or "") == "due_today"]
    due_later = [item for item in concepts if str(item.get("review_bucket") or "") == "due_later"]
    mastered_review = [item for item in concepts if str(item.get("review_bucket") or "") == "mastered_review"]
    new_concepts = [item for item in concepts if str(item.get("review_bucket") or "") == "new_concept"]

    current = choose_review_question_from_view(view)
    last_attempt = view.get("last_attempt")

    last_html = ""

    if last_attempt:
        result = _ut("correct", "Correct") if last_attempt.get("correct") else _ut("incorrect", "Incorrect")
        before = round(float(last_attempt.get("mastery_before", 0)) * 100)
        after = round(float(last_attempt.get("mastery_after", 0)) * 100)

        last_html = f"""
        <div class="notice">
          {_ut("last_review_answer", "Last review answer")}: <strong>{result}</strong>.
          {_ut("mastery_changed", "Mastery changed from")} <strong>{before}%</strong> {_ut("to", "to")} <strong>{after}%</strong>.
        </div>
        """

    if current:
        answer_html = ""

        if current.get("answer"):
            answer_html = f"""
            <details>
              <summary>{_ut("show_expected_answer", "Show expected answer / explanation")}</summary>
              <p>{html.escape(str(current.get("answer")))}</p>
            </details>
            """

        concept_id = html.escape(str(current.get("concept_id") or current.get("lesson_id") or ""))
        question = html.escape(str(current.get("question") or ""))
        answer_id = html.escape(str(current.get("question_id") or ""))
        recommendation_reason = html.escape(_study_recommendation_reason_label(str(current.get("recommendation_reason") or "")))

        reason_html = ""
        if recommendation_reason:
            reason_html = f'<div class="meta">{_ut("recommended_because", "Recommended because")}: <strong>{recommendation_reason}</strong></div>'

        question_html = f"""
        <article class="card">
          <h2>{_ut("ui.heading.review_question", "Review question")}</h2>
          <div class="meta">{_ut("status.focused_concept", "Focused concept")}: <strong>{concept_id}</strong></div>
          {reason_html}
          <p style="font-size: 20px;"><strong>{question}</strong></p>
          {answer_html}

          <div class="actions">
            <form method="post" action="/review-answer">
              <input type="hidden" name="pdf_name" value="{html.escape(pdf_path.name)}">
              <input type="hidden" name="question_id" value="{answer_id}">
              <input type="hidden" name="correct" value="true">
              <button class="primary" type="submit">{_ut("correct", "Correct")}</button>
            </form>

            <form method="post" action="/review-answer">
              <input type="hidden" name="pdf_name" value="{html.escape(pdf_path.name)}">
              <input type="hidden" name="question_id" value="{answer_id}">
              <input type="hidden" name="correct" value="false">
              <button type="submit">{_ut("incorrect", "Incorrect")}</button>
            </form>
          </div>
        </article>
        """
    else:
        question_html = """
        <article class="card">
          <h2>{_ut("ui.heading.no_review_questions", "No review questions available")}</h2>
          <p>{_ut("ui.message.generate_study_quiz_first", "Generate a study quiz first.")}</p>
        </article>
        """

    def mini_list(title: str, items: list, empty: str) -> str:
        rows = []

        for item in items[:8]:
            concept_id = html.escape(str(item.get("concept_id") or ""))
            mastery = int(item.get("mastery_percent") or 0)
            attempts = int(item.get("attempts") or 0)
            bucket = html.escape(review_bucket_label(item.get("review_bucket")))
            next_review = html.escape(review_timestamp_label(item.get("review_due_at")))

            rows.append(
                f"""
                <article class="card">
                  <h2>{concept_id}</h2>
                  <p style="font-size: 28px; margin: 8px 0;"><strong>{mastery}%</strong></p>
                  <div class="meta">
                    {_ut("status.attempts", "Attempts")}: {attempts}<br>
                    {_ut("review_bucket", "Review bucket")}: <strong>{bucket}</strong><br>
                    {_ut("next_review", "Next review")}: <strong>{next_review}</strong>
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
        <h2 style="margin-top: 28px;">{html.escape(title)}</h2>
        <div class="grid">
          {''.join(rows)}
        </div>
        """

    body = f"""
    <h1>{_ut("ui.heading.review_due_concepts", "Voila! Review due concepts")}</h1>

    <div class="notice">
      PDF: <strong>{html.escape(pdf_path.name)}</strong><br>
      {_ut("due_now", "Due now")}: <strong>{len(due_now)}</strong> ·
      {_ut("due_today", "Due today")}: <strong>{len(due_today)}</strong> ·
      {_ut("due_later", "Due later")}: <strong>{len(due_later)}</strong> ·
      {_ut("mastered_review", "Mastered review")}: <strong>{len(mastered_review)}</strong> ·
      {_ut("new_concept", "New concept")}: <strong>{len(new_concepts)}</strong>
    </div>

    {last_html}

    <div class="grid">
      {question_html}
    </div>

    <div class="actions" style="margin-top: 24px;">
      <a class="btn primary" href="/review?pdf={quote(pdf_path.name)}">{_ut("ui.link.next_review", "Next review")}</a>
      <a class="btn" href="/study?pdf={quote(pdf_path.name)}">{_ut("ui.link.study", "Study")}</a>
      <a class="btn" href="/progress?pdf={quote(pdf_path.name)}">{_ut("ui.link.progress", "Progress")}</a>
      <a class="btn" href="/">{_ut("ui.link.back_to_voila", "Back to Voila!")}</a>
    </div>

    {mini_list(_ut("due_now", "Due now"), due_now, _ut("no_due_now_concepts_yet", "No concepts due now."))}
    {mini_list(_ut("due_today", "Due today"), due_today, _ut("no_due_today_concepts_yet", "No concepts due today."))}
    {mini_list(_ut("due_later", "Due later"), due_later, _ut("no_due_later_concepts_yet", "No concepts scheduled later."))}
    {mini_list(_ut("mastered_review", "Mastered review"), mastered_review, _ut("no_mastered_review_concepts_yet", "No mastered-review concepts yet."))}
    {mini_list(_ut("new_concept", "New concept"), new_concepts, _ut("no_new_concepts_yet", "No new concepts yet."))}
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
        <h1>{_ut("ui.heading.progress", "Voila! Progress")}</h1>
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
    overall_status = html.escape(_study_status_label(str(view.get("overall_status") or "No status")))

    weak = [item for item in concepts if float(item.get("mastery", 0)) < 0.40]
    review = [item for item in concepts if 0.40 <= float(item.get("mastery", 0)) < 0.75]
    almost = [item for item in concepts if 0.75 <= float(item.get("mastery", 0)) < 0.90]
    mastered = [item for item in concepts if float(item.get("mastery", 0)) >= 0.90]

    if total_questions > 0:
        answered_percent = round((answered_count / total_questions) * 100)
    else:
        answered_percent = 0

    def progress_question_type_label(value: str) -> str:
        raw = str(value or "").strip().lower()

        if not raw:
            return _ut("not_available", "Not available")

        lang = _ui_language_code()
        labels = {
            "ro": {
                "definition": "definiție",
                "components": "componente",
                "purpose": "scop",
                "requirement": "cerință",
                "condition": "condiție",
                "cause_effect": "cauză/efect",
                "comparison": "comparație",
                "example": "exemplu",
                "process": "proces",
                "numeric_check": "verificare numerică",
                "visual_interpretation": "interpretare vizuală",
                "technical_fact": "precizare tehnică",
            },
            "en": {
                "definition": "definition",
                "components": "components",
                "purpose": "purpose",
                "requirement": "requirement",
                "condition": "condition",
                "cause_effect": "cause/effect",
                "comparison": "comparison",
                "example": "example",
                "process": "process",
                "numeric_check": "numeric check",
                "visual_interpretation": "visual interpretation",
                "technical_fact": "technical fact",
            },
        }

        lang_key = "ro" if lang == "ro" else "en"
        return labels[lang_key].get(raw, raw.replace("_", " "))


    def progress_timestamp_label(value) -> str:
        raw = str(value or "").strip()

        if not raw:
            return _ut("not_available", "Not available")

        return raw.replace("T", " ").replace("Z", "")[:19]


    def progress_review_bucket_label(value: str) -> str:
        raw = str(value or "").strip().lower()

        if not raw:
            return _ut("not_available", "Not available")

        labels = {
            "ro": {
                "due_now": "scadent acum",
                "due_today": "scadent azi",
                "due_later": "programat mai târziu",
                "mastered_review": "revizuire de consolidare",
                "new_concept": "concept nou",
            },
            "en": {
                "due_now": "due now",
                "due_today": "due today",
                "due_later": "due later",
                "mastered_review": "mastered review",
                "new_concept": "new concept",
            },
        }

        lang_key = "ro" if _ui_language_code() == "ro" else "en"
        return labels[lang_key].get(raw, raw.replace("_", " "))


    def progress_question_type_stats_label(stats) -> str:
        if not isinstance(stats, dict) or not stats:
            return _ut("not_available", "Not available")

        rows = []

        for qtype, values in sorted(stats.items()):
            if not isinstance(values, dict):
                continue

            attempts = int(values.get("attempts") or 0)
            correct = int(values.get("correct") or 0)
            incorrect = int(values.get("incorrect") or 0)

            if attempts <= 0:
                continue

            rows.append(
                f"{html.escape(progress_question_type_label(str(qtype)))}: "
                f"{attempts} / {correct}✓ / {incorrect}✗"
            )

        return "<br>".join(rows) if rows else _ut("not_available", "Not available")


    def concept_list(title: str, items: list, empty: str) -> str:
        rows = []

        for item in items[:12]:
            concept_id = html.escape(str(item.get("concept_id") or ""))
            mastery = int(item.get("mastery_percent") or 0)
            attempts = int(item.get("attempts") or 0)
            correct = int(item.get("correct") or 0)
            incorrect = int(item.get("incorrect") or 0)
            status = html.escape(_study_status_label(str(item.get("status") or "")))
            recent_misses = int(item.get("recent_misses") or 0)
            last_question_type = html.escape(progress_question_type_label(item.get("last_question_type")))
            last_correct = html.escape(progress_timestamp_label(item.get("last_correct")))
            last_incorrect = html.escape(progress_timestamp_label(item.get("last_incorrect")))
            type_stats = progress_question_type_stats_label(item.get("question_type_stats") or {})
            review_bucket = html.escape(progress_review_bucket_label(item.get("review_bucket")))
            next_review = html.escape(progress_timestamp_label(item.get("review_due_at")))
            review_delay_days = int(item.get("review_delay_days") or 0)

            rows.append(
                f"""
                <article class="card">
                  <h2>{concept_id}</h2>
                  <div class="meta">{_ut("status.status", "Status")}: <strong>{status}</strong></div>
                  <p style="font-size: 30px; margin: 8px 0;"><strong>{mastery}%</strong></p>
                  <div style="height: 12px; background: var(--paper-soft); border: 1px solid var(--border); border-radius: 999px; overflow: hidden;">
                    <div style="height: 100%; width: {mastery}%; background: var(--accent);"></div>
                  </div>
                  <div class="meta" style="margin-top: 10px;">
                    {_ut("status.attempts", _ut("attempts", "Attempts"))}: {attempts}<br>
                    {_ut("correct", "Correct")}: {correct}<br>
                    {_ut("incorrect", "Incorrect")}: {incorrect}
                  </div>
                  <details style="margin-top: 12px;">
                    <summary>{_ut("bkt_diagnostics", "BKT diagnostics")}</summary>
                    <div class="meta" style="margin-top: 10px;">
                      {_ut("recent_misses", "Recent misses")}: <strong>{recent_misses}</strong><br>
                      {_ut("last_question_type", "Last question type")}: <strong>{last_question_type}</strong><br>
                      {_ut("last_correct", "Last correct")}: <strong>{last_correct}</strong><br>
                      {_ut("last_incorrect", "Last incorrect")}: <strong>{last_incorrect}</strong><br>
                      {_ut("question_type_stats", "Question-type stats")}:<br>
                      {type_stats}<br>
                      <br>
                      {_ut("review_schedule", "Review schedule")}:<br>
                      {_ut("review_bucket", "Review bucket")}: <strong>{review_bucket}</strong><br>
                      {_ut("next_review", "Next review")}: <strong>{next_review}</strong><br>
                      {_ut("review_delay_days", "Review delay days")}: <strong>{review_delay_days}</strong>
                    </div>
                  </details>
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

    current_question = view.get("current_question") or {}
    recommended_reason_html = ""
    next_question_type_html = ""

    if isinstance(current_question, dict) and current_question:
        reason = html.escape(_study_recommendation_reason_label(str(current_question.get("recommendation_reason") or "")))
        qtype = html.escape(progress_question_type_label(str(current_question.get("question_type") or "")))

        if reason:
            recommended_reason_html = f'<br>{_ut("recommended_because", "Recommended because")}: <strong>{reason}</strong>'

        if qtype:
            next_question_type_html = f'<br>{_ut("next_question_type", "Next question type")}: <strong>{qtype}</strong>'

    if recommended:
        recommended_html = f"""
        <div class="notice">
          {_ut("recommended_next_focus", "Recommended next focus")}:
          <strong>{html.escape(str(recommended.get("concept_id") or ""))}</strong>
          — {_ut("mastery_label", "mastery")} <strong>{int(recommended.get("mastery_percent") or 0)}%</strong>.
          {recommended_reason_html}
          {next_question_type_html}
        </div>
        """
    else:
        recommended_html = """
        <div class="notice">
          {_ut("no_study_recommendation", "No study recommendation yet. Generate a study quiz first.")}
        </div>
        """

    body = f"""
    <h1>{_ut("ui.heading.progress_dashboard", "Voila! Progress Dashboard")}</h1>

    <div class="notice">
      PDF: <strong>{html.escape(pdf_path.name)}</strong><br>
      {_ut("status.overall_mastery", _ut("overall_mastery", "Overall mastery"))}: <strong>{overall_mastery}%</strong> ·
      {_ut("status.status", "Status")}: <strong>{overall_status}</strong><br>
      {_ut("questions_answered", "Questions answered")}: <strong>{answered_count}</strong> / <strong>{total_questions}</strong>
      ({answered_percent}%)
    </div>

    {recommended_html}

    <div class="grid">
      <article class="card">
        <h2>{_ut("status.overall_mastery", _ut("overall_mastery", "Overall mastery"))}</h2>
        <p style="font-size: 34px; margin: 8px 0;"><strong>{overall_mastery}%</strong></p>
        <div style="height: 14px; background: var(--paper-soft); border: 1px solid var(--border); border-radius: 999px; overflow: hidden;">
          <div style="height: 100%; width: {overall_mastery}%; background: var(--accent);"></div>
        </div>
        <div class="meta" style="margin-top: 10px;">{overall_status}</div>
      </article>

      <article class="card">
        <h2>{_ut("status.study_coverage", _ut("study_coverage", "Study coverage"))}</h2>
        <p style="font-size: 34px; margin: 8px 0;"><strong>{answered_percent}%</strong></p>
        <div class="meta">
          {_ut("answered", "Answered")}: <strong>{answered_count}</strong><br>
          {_ut("total_questions", "Total questions")}: <strong>{total_questions}</strong>
        </div>
      </article>

      <article class="card">
        <h2>{_ut("status.concept_status", "Concept status")}</h2>
        <div class="meta">
          {_ut("needs_review", "Needs review")}: <strong>{len(weak)}</strong><br>
          {_ut("in_progress", "In progress")}: <strong>{len(review)}</strong><br>
          {_ut("almost_mastered", "Almost mastered")}: <strong>{len(almost)}</strong><br>
          {_ut("mastered", "Mastered")}: <strong>{len(mastered)}</strong>
        </div>
      </article>
    </div>

    <div class="actions" style="margin-top: 24px;">
      <a class="btn primary" href="/study?pdf={quote(pdf_path.name)}">{_ut("ui.link.continue_study", "Continue Study")}</a>
      <a class="btn" href="/review?pdf={quote(pdf_path.name)}">{_ut("ui.review_weak", "Review due")}</a>
      <a class="btn" href="/">{_ut("ui.link.back_to_voila", "Back to Voila!")}</a>
    </div>

    {concept_list(_ut("needs_review", "Needs review"), weak, _ut("no_weak_concepts_yet", "No weak concepts yet."))}
    {concept_list(_ut("in_progress", "In progress"), review, _ut("no_concepts_in_this_range_yet", "No concepts in this range yet."))}
    {concept_list(_ut("almost_mastered", "Almost mastered"), almost, _ut("no_almost_mastered_concepts_yet", "No almost-mastered concepts yet."))}
    {concept_list(_ut("mastered", "Mastered"), mastered, _ut("no_mastered_concepts_yet", "No mastered concepts yet."))}
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
        <h1>{_ut("ui.study_mode", "Study Mode")}</h1>
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
        result = _ut("correct", "Correct") if last_attempt.get("correct") else _ut("incorrect", "Incorrect")
        before = round(float(last_attempt.get("mastery_before", 0)) * 100)
        after = round(float(last_attempt.get("mastery_after", 0)) * 100)

        last_html = f"""
        <div class="notice">
          {_ut("last_answer", "Last answer")}: <strong>{result}</strong>.
          {_ut("mastery_changed", "Mastery changed from")} <strong>{before}%</strong> {_ut("to", "to")} <strong>{after}%</strong>.
        </div>
        """

    if current:
        answer_html = ""

        if current.get("answer"):
            answer_html = f"""
            <details>
              <summary>{_ut("show_expected_answer", "Show expected answer / explanation")}</summary>
              <p>{html.escape(str(current.get("answer")))}</p>
            </details>
            """

        recommendation_reason = html.escape(_study_recommendation_reason_label(str(current.get("recommendation_reason") or "")))
        reason_html = ""
        if recommendation_reason:
            reason_html = f'<div class="meta">{_ut("recommended_because", "Recommended because")}: <strong>{recommendation_reason}</strong></div>'

        question_html = f"""
        <article class="card">
          <h2>{_ut("recommended_question", "Recommended question")}</h2>
          <div class="meta">{_ut("lesson_concept", "Lesson / concept")}: <strong>{html.escape(str(current.get("lesson_id")))}</strong></div>
          {reason_html}
          <p style="font-size: 20px;"><strong>{html.escape(_build_study_question_display(current, pdf_path.name))}</strong></p>
          {answer_html}

          <div class="actions">
            <form method="post" action="/study-answer">
              <input type="hidden" name="pdf_name" value="{html.escape(pdf_path.name)}">
              <input type="hidden" name="question_id" value="{html.escape(str(current.get("question_id")))}">
              <input type="hidden" name="correct" value="true">
              <button class="primary" type="submit">{_ut("correct", "Correct")}</button>
            </form>

            <form method="post" action="/study-answer">
              <input type="hidden" name="pdf_name" value="{html.escape(pdf_path.name)}">
              <input type="hidden" name="question_id" value="{html.escape(str(current.get("question_id")))}">
              <input type="hidden" name="correct" value="false">
              <button type="submit">{_ut("incorrect", "Incorrect")}</button>
            </form>
          </div>
        </article>
        """
    else:
        question_html = """
        <article class="card">
          <h2>{_ut("no_questions_available", "No questions available")}</h2>
          <p>{_ut("generate_course_files_first", "Generate course files first, then Study Mode will use quiz.json.")}</p>
        </article>
        """

    concept_cards = []

    for concept in concepts:
        mastery = int(concept.get("mastery_percent", 0))
        concept_id = html.escape(str(concept.get("concept_id", "")))
        status = html.escape(_study_status_label(str(concept.get("status", ""))))
        attempts = int(concept.get("attempts", 0))
        correct_count = int(concept.get("correct", 0))
        incorrect_count = int(concept.get("incorrect", 0))

        concept_cards.append(
            f"""
            <article class="card">
              <h2>{concept_id}</h2>
              <div class="meta">{_ut("status.status", "Status")}: <strong>{status}</strong></div>
              <p style="font-size: 28px; margin: 8px 0;"><strong>{mastery}%</strong></p>
              <div class="meta">
                {_ut("status.attempts", _ut("attempts", "Attempts"))}: {attempts}<br>
                {_ut("correct", "Correct")}: {correct_count}<br>
                {_ut("incorrect", "Incorrect")}: {incorrect_count}
              </div>
            </article>
            """
        )

    reset_form = f"""
    <form method="post" action="/study-reset">
      <input type="hidden" name="pdf_name" value="{html.escape(pdf_path.name)}">
      <button type="submit">{_ut("reset_study_progress", "Reset study progress")}</button>
    </form>
    """

    body = f"""
    <h1>Voila! {_ut("study", "Study")}</h1>
    <div class="notice">
      PDF: <strong>{html.escape(pdf_path.name)}</strong><br>
      {_ut("questions", "Questions")}: <strong>{view.get("total_questions")}</strong> ·
      {_ut("answered", "Answered")}: <strong>{view.get("answered_count")}</strong> ·
      {_ut("status.overall_mastery", _ut("overall_mastery", "Overall mastery"))}: <strong>{view.get("overall_mastery_percent")}%</strong> ·
      {_ut("status.status", _ut("status", "Status"))}: <strong>{html.escape(_study_status_label(str(view.get("overall_status") or "")))}</strong>
    </div>

    {last_html}

    <div class="grid">
      {question_html}
    </div>

    <h2 style="margin-top: 28px;">{_ut("concept_mastery", "Concept mastery")}</h2>
    <div class="grid">
      {''.join(concept_cards)}
    </div>

    <div class="actions" style="margin-top: 24px;">
      <a class="btn" href="/">{_ut("ui.link.back_to_voila", "Back to Voila!")}</a>
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
        return PlainTextResponse(_ut("message.no_log_file_found_yet", "No log file found yet."), status_code=404)

    return PlainTextResponse(log_path.read_text(encoding="utf-8"))








@app.get("/edit-crops")
def edit_crops(pdf: str = ""):
    from fastapi.responses import HTMLResponse, RedirectResponse
    from urllib.parse import quote

    ensure_crop_editor_running()

    if not crop_editor_is_running():
        return HTMLResponse(
            """
            <h1>{_ut("ui.heading.crop_editor_not_started", "Crop Editor did not start")}</h1>
            <p>{_ut("ui.message.crop_editor_port_not_responding", "Port 8790 is not responding. Start it manually:")}</p>
            <pre>python -m uvicorn crop_editor_app:app --app-dir services/api --host 127.0.0.1 --port 8790</pre>
            """,
            status_code=503,
        )

    if pdf:
        return RedirectResponse("http://127.0.0.1:8790/?pdf=" + quote(pdf))

    return RedirectResponse("http://127.0.0.1:8790/")



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
    from urllib.parse import quote

    pdf_name = _safe_pdf_name(pdf)

    if not pdf_name:
        return HTMLResponse("<h1>" + _ut("error.missing_pdf_name", "Missing PDF name") + "</h1>", status_code=400)

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

            <label>{_ut("ui.label.correct_concept_title", "Correct concept title")}</label>
            <input name="title" value="{_html_escape(effective)}">

            <div class="actions">
              <button type="submit">{_ut("ui.save_title_override", "Save title override")}</button>
              <a class="ghost" href="/study?pdf={_html_escape(pdf_name)}">{_ut("ui.link.study", "Study")}</a>
            </div>
          </form>

          <details>
            <summary>Question sample</summary>
            <p><b>Q:</b> {_html_escape(sample_question)}</p>
            <p><b>A:</b> {_html_escape(sample_answer)}</p>
          </details>
        </section>
        """)

    content = "\n".join(rows) if rows else "<p>" + _ut("ui.message.no_study_questions_found", "No study questions found. Generate Study first.") + "</p>"

    html_doc = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{_ut("ui.review_study_concepts", "Review Study Concepts")} · Voila!</title>
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
        <h1>{_ut("ui.review_study_concepts", "Review Study Concepts")}</h1>
        <p>PDF: <b>{_html_escape(pdf_name)}</b></p>
      </div>
      <div class="top-actions">
        <a href="/course-tools?pdf={quote(pdf_name)}">{_ut("ui.link.course_tools", "Course tools")}</a>
        <a href="/">{_ut("library", "Library")}</a>
        <a href="/review-ocr-corrected?pdf={quote(pdf_name)}&page=1">{_ut("ui.review_ocr_text", "Review OCR Text")}</a>
        <a href="/view-course?pdf={quote(pdf_name)}">{_ut("ui.open_course", _ut("open_course", "Open course"))}</a>
        <a href="/study?pdf={quote(pdf_name)}">{_ut("ui.link.study", "Study")}</a>
        <a href="/progress?pdf={_html_escape(pdf_name)}">{_ut("ui.link.progress", "Progress")}</a>
      </div>
    </div>

    {content}
  </div>

  <nav class="floating-nav">
    <a href="/">{_ut("ui.link.back", "Back")}</a>
    <a href="/study?pdf={_html_escape(pdf_name)}">{_ut("ui.link.study", "Study")}</a>
    <a href="#top" onclick="window.scrollTo({{top:0,behavior:'smooth'}}); return false;">↑ {_ut("ui.link.top", "Top")}</a>
    <a href="#bottom" onclick="window.scrollTo({{top:document.body.scrollHeight,behavior:'smooth'}}); return false;">↓ {_ut("ui.link.bottom", "Bottom")}</a>
  </nav>
</body>
</html>
"""

    return HTMLResponse(html_doc)



@app.post("/review-concepts/save")
def save_review_concept(
    pdf: str = Form(...),
    lesson_id: str = Form(...),
    title: str = Form(...),
):
    from datetime import datetime, timezone
    from fastapi.responses import HTMLResponse, RedirectResponse
    from urllib.parse import quote
    import traceback

    try:
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

        clean_title = str(title or "").strip()

        if not clean_title:
            return HTMLResponse(
                "<h1>Empty title</h1><p>" + _ut("ui.message.concept_title_cannot_be_empty", "Concept title cannot be empty.") + "</p>",
                status_code=400,
            )

        payload.setdefault("overrides", {})[lesson_id] = {
            "concept_title": clean_title,
            "lesson_title": clean_title,
            "source": "manual_ui",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        _save_json_file(overrides_path, payload)

        try:
            from ocr_corrections_engine import apply_title_overrides
            apply_title_overrides(output_dir)
        except Exception:
            # Keep override saved even if rebuild/update fails.
            pass

        return RedirectResponse(
            "/review-concepts?pdf=" + quote(pdf_name),
            status_code=303,
        )

    except Exception:
        error = traceback.format_exc()
        return HTMLResponse(
            f"""
            <h1>{_ut("error.save_title_override_failed", "Save title override failed")}</h1>
            <p>{_ut("ui.message.correction_not_saved_exception", "The correction was not saved because the server raised an exception.")}</p>
            <pre style="white-space: pre-wrap; background:#111; color:#f6ead7; padding:16px; border-radius:12px;">{error}</pre>
            <p><a href="/">{_ut("ui.link.back_to_voila", "Back to Voila")}</a></p>
            """,
            status_code=500,
        )


def _load_ocr_review_pages(output_dir: Path) -> list[dict]:
    candidates = [
        output_dir / "ocr_pages.json",
        output_dir / "pages.json",
    ]

    for path in candidates:
        if not path.exists():
            continue

        data = _load_json_file(path, {})

        if isinstance(data, dict):
            pages = data.get("pages") or data.get("items") or []
        elif isinstance(data, list):
            pages = data
        else:
            pages = []

        usable = []

        for idx, page in enumerate(pages, start=1):
            if not isinstance(page, dict):
                continue

            page_number = int(page.get("page_number") or page.get("pdf_page") or idx)
            page_text = str(page.get("text") or page.get("content") or "")

            usable.append(
                {
                    "page_number": page_number,
                    "text": page_text,
                }
            )

        if usable:
            return usable

    return []


def _write_ocr_review_pages(output_dir: Path, pages: list[dict]) -> None:
    payload = {
        "version": "voila_ocr_text_review_v1",
        "text_source": "manual_reviewed_ocr",
        "pages": pages,
    }

    for target_name in ["ocr_pages.json", "pages.json"]:
        target = output_dir / target_name

        if target.exists():
            backup = output_dir / f"{target_name}.before_text_review.json"

            if not backup.exists():
                backup.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")

        _save_json_file(target, payload)

    md_lines = [
        f"# Reviewed OCR pages for {output_dir.name}",
        "",
        "Generated by Voila! OCR Text Review.",
        "",
    ]

    for page in pages:
        md_lines.extend(
            [
                f"## Page {page['page_number']}",
                "",
                str(page.get("text") or "").strip(),
                "",
            ]
        )

    for target_name in ["ocr_pages.md", "pages.md"]:
        target = output_dir / target_name

        if target.exists():
            backup = output_dir / f"{target_name}.before_text_review.md"

            if not backup.exists():
                backup.write_text(target.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

        target.write_text("\n".join(md_lines), encoding="utf-8")


def _ocr_page_image_url(output_dir: Path, page_number: int) -> str:
    candidates = [
        output_dir / "ocr" / "page_images" / f"page_{page_number:04d}.png",
        output_dir / "scanned_pages" / f"page_{page_number:04d}.jpg",
    ]

    for candidate in candidates:
        if candidate.exists():
            rel = candidate.relative_to(PROJECT_ROOT / "data" / "output")
            return "/output/" + str(rel).replace("\\", "/")

    return ""


def _detect_suspicious_ocr_text(text: str) -> bool:
    value = str(text or "")

    if len(value.strip()) < 80:
        return True

    weird = len(re.findall(r"[�□■◆◇<>~`^|_]{1,}", value))
    letters = len(re.findall(r"[A-Za-zĂÂÎȘȚăâîșț]", value))
    digits = len(re.findall(r"\d", value))

    if weird >= 5:
        return True

    if digits > letters and len(value) > 200:
        return True

    if re.search(r"\b(jj|ixii|v0|01g|lll|iiii|[Il1]{4,})\b", value.lower()):
        return True

    return False


@app.get("/review-ocr-text")
def review_ocr_text(pdf: str = "", page: int = 1):
    from fastapi.responses import HTMLResponse
    from urllib.parse import quote

    pdf_name = _safe_pdf_name(pdf)

    if not pdf_name:
        return HTMLResponse("<h1>" + _ut("error.missing_pdf_name", "Missing PDF name") + "</h1>", status_code=400)

    output_dir = _output_dir_for_pdf_name(pdf_name)
    pages = _load_ocr_review_pages(output_dir)

    if not pages:
        return HTMLResponse("<h1>" + _ut("error.no_ocr_pages_found", "No OCR pages found") + "</h1><p>" + _ut("message.run_ocr_first", "Run OCR first") + ".</p>", status_code=404)

    page_numbers = [int(item["page_number"]) for item in pages]
    min_page = min(page_numbers)
    max_page = max(page_numbers)

    if page < min_page:
        page = min_page

    if page > max_page:
        page = max_page

    current = next((item for item in pages if int(item["page_number"]) == page), pages[0])
    current_text = current.get("text") or ""

    suspicious_pages = [
        int(item["page_number"])
        for item in pages
        if _detect_suspicious_ocr_text(item.get("text") or "")
    ]

    previous_page = max(min_page, page - 1)
    next_page = min(max_page, page + 1)
    image_url = _ocr_page_image_url(output_dir, page)

    suspicious_nav = " ".join(
        f'<a href="/review-ocr-corrected?pdf={quote(pdf_name)}&page={p}">{p}</a>'
        for p in suspicious_pages[:80]
    )

    image_html = (
        f"""
        <div class="scan-shell">
          <div class="scan-toolbar">
            <button type="button" onclick="zoomScan(-0.15)">−</button>
            <button type="button" onclick="resetScanZoom()">100%</button>
            <button type="button" onclick="fitScanWidth()">{_ut("ui.fit_width", "Fit width")}</button>
            <button type="button" onclick="zoomScan(0.15)">+</button>
            <span class="zoom-pill" data-zoom-label>100%</span>
            <span class="scan-tip">Tip: Ctrl + mouse wheel = zoom · click + drag = move page</span>
          </div>

          <div class="scan-viewport" id="scanViewport">
            <img id="scanImage" class="scan-img" src="{_html_escape(image_url)}" alt="OCR source page {page}">
          </div>
</div>
        """
        if image_url
        else '<div class="no-img">No rendered page image found for this page.</div>'
    )

    html_doc = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{_ut("ui.review_ocr_text", "Review OCR Text")} · Voila!</title>
  <style>
    :root {{
      --bg: #101819;
      --panel: #202d31;
      --panel2: #26363b;
      --text: #f6ead7;
      --muted: #c7ad94;
      --line: #3b4b50;
      --accent: #e0ad68;
      --bad: #b45b46;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: system-ui, -apple-system, Segoe UI, sans-serif;
      padding: 24px;
    }}

    .wrap {{
      max-width: 1700px;
      margin: 0 auto;
    }}

    .top {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      margin-bottom: 18px;
    }}

    h1 {{
      margin: 0;
      font-size: clamp(30px, 5vw, 52px);
      line-height: 1.05;
    }}

    a, button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 11px 16px;
      background: var(--panel2);
      color: var(--text);
      text-decoration: none;
      font-weight: 850;
      cursor: pointer;
      font-size: 15px;
    }}

    button {{
      background: var(--accent);
      border-color: transparent;
      color: white;
    }}

    .grid {{
      display: grid;
      grid-template-columns: minmax(420px, 0.95fr) minmax(520px, 1.05fr);
      gap: 20px;
      align-items: start;
    }}

    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 20px;
      box-shadow: 0 18px 48px rgba(0,0,0,0.22);
    }}

    .scan-shell {{
      position: relative;
    }}

    .scan-toolbar {{
      position: sticky;
      top: 10px;
      z-index: 20;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
      margin-bottom: 12px;
      padding: 10px;
      background: rgba(32, 45, 49, 0.96);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: 0 10px 28px rgba(0,0,0,0.22);
    }}

    .scan-toolbar button,
    .scan-floating-zoom button {{
      padding: 9px 13px;
      min-width: 44px;
      border-radius: 999px;
      font-size: 15px;
      line-height: 1;
    }}

    .zoom-pill {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 8px 12px;
      border-radius: 999px;
      background: #142022;
      border: 1px solid var(--line);
      color: var(--muted);
      font-weight: 900;
      min-width: 68px;
    }}

    .scan-tip {{
      color: var(--muted);
      font-weight: 800;
      font-size: 14px;
      padding: 8px 10px;
    }}

    .scan-viewport {{
      width: 100%;
      height: 78vh;
      overflow: auto;
      background: #f2ead8;
      border-radius: 18px;
      border: 1px solid var(--line);
      overscroll-behavior: contain;
      cursor: grab;
      touch-action: none;
    }}

    .scan-viewport.dragging {{
      cursor: grabbing;
    }}

    .scan-img {{
      display: block;
      width: auto;
      max-width: none;
      height: auto;
      max-height: none;
      background: #f2ead8;
      border: 0;
      border-radius: 0;
      transform-origin: top left;
      user-select: none;
      -webkit-user-drag: none;
      pointer-events: none;
    }}
    .scan-floating-zoom {{
      display: none !important;
      visibility: hidden !important;
      pointer-events: none !important;
    }}
.no-img {{
      padding: 40px;
      border: 1px dashed var(--line);
      border-radius: 18px;
      color: var(--muted);
    }}

    textarea {{
      width: 100%;
      min-height: 68vh;
      resize: vertical;
      background: #121f22;
      color: var(--text);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      font-size: 18px;
      line-height: 1.55;
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
    }}

    .ocr-suggestions {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
      padding: 10px;
      background: #142022;
      border: 1px solid var(--line);
      border-radius: 16px;
    }}

    .ocr-suggestions[hidden] {{
      display: none;
    }}

    .ocr-suggestion {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 8px 12px;
      background: var(--panel2);
      color: var(--text);
      font-weight: 850;
      cursor: pointer;
    }}

    .ocr-suggestion.primary {{
      background: var(--accent);
      color: white;
      border-color: transparent;
    }}

    .small-tip {{
      font-size: 14px;
      margin-top: 8px;
    }}

    .actions {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin: 14px 0;
    }}

    .meta {{
      color: var(--muted);
      font-size: 17px;
      line-height: 1.5;
    }}

    .suspects {{
      margin-top: 18px;
      padding-top: 16px;
      border-top: 1px solid var(--line);
    }}

    .suspects a {{
      padding: 7px 11px;
      margin: 4px;
      background: rgba(180,91,70,0.20);
      border-color: rgba(180,91,70,0.55);
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

    @media (max-width: 980px) {{
      body {{ padding: 14px; }}
      .top {{ display: block; }}
      .grid {{ grid-template-columns: 1fr; }}
      textarea {{ min-height: 58vh; }}
      .floating-nav {{
        width: calc(100% - 24px);
        overflow-x: auto;
        justify-content: flex-start;
      }}
    }}
  

    /* VS Code style OCR autocomplete */
    .ocr-suggestions {{
      position: fixed !important;
      z-index: 3000 !important;
      display: block !important;
      min-width: 280px;
      max-width: min(520px, calc(100vw - 24px));
      max-height: 280px;
      overflow-y: auto;
      padding: 6px;
      background: #1b2529;
      border: 1px solid var(--line);
      border-radius: 12px;
      box-shadow: 0 18px 48px rgba(0,0,0,0.45);
    }}

    .ocr-suggestions[hidden] {{
      display: none !important;
    }}

    .ocr-suggestion {{
      display: block !important;
      width: 100%;
      border: 0;
      border-radius: 8px;
      padding: 9px 12px;
      background: transparent;
      color: var(--text);
      text-align: left;
      font-weight: 800;
      font-size: 15px;
      cursor: pointer;
      font-family: system-ui, -apple-system, Segoe UI, sans-serif;
    }}

    .ocr-suggestion:hover,
    .ocr-suggestion.active,
    .ocr-suggestion.primary {{
      background: var(--accent);
      color: white;
    }}

    .ocr-suggestion small {{
      display: block;
      color: rgba(255,255,255,0.70);
      font-weight: 700;
      margin-top: 2px;
    }}

  </style>
</head>
<body data-pdf-name="{_html_escape(pdf_name)}">
  <div class="wrap">
    <div class="top">
      <div>
        <h1>{_ut("ui.review_ocr_text", "Review OCR Text")}</h1>
        <div class="meta">PDF: <b>{_html_escape(pdf_name)}</b> · Page <b>{page}</b> / {max_page}</div>
      </div>
      <div class="actions">
        <a href="/course-tools?pdf={quote(pdf_name)}">{_ut("ui.link.course_tools", "Course tools")}</a>
        <a href="/">{_ut("library", "Library")}</a>
        <a href="/review-concepts?pdf={quote(pdf_name)}">{_ut("ui.review_concepts", "Review concepts")}</a>
        <a href="/view-course?pdf={quote(pdf_name)}">{_ut("ui.open_course", _ut("open_course", "Open course"))}</a>
        <a href="/study?pdf={quote(pdf_name)}">{_ut("ui.link.study", "Study")}</a>
      </div>
    </div>

    <div class="actions">
      <a href="/review-ocr-corrected?pdf={quote(pdf_name)}&page={previous_page}">← {_ut("ui.link.previous", "Previous")}</a>
      <a href="/review-ocr-corrected?pdf={quote(pdf_name)}&page={next_page}">{_ut("ui.link.next", "Next")} →</a>
    </div>

    <div class="grid">
      <section class="panel">
        <h2>{_ut("ui.heading.source_page", "Source page")}</h2>
        {image_html}
      </section>

      <section class="panel">
        <h2>{_ut("ui.heading.editable_ocr_text", "Editable OCR text")}</h2>
        <form method="post" action="/review-ocr-text/save">
          <input type="hidden" name="pdf" value="{_html_escape(pdf_name)}">
          <input type="hidden" name="page" value="{page}">
          <textarea id="ocrTextArea" name="text" autocomplete="off" spellcheck="false">{_html_escape(current_text)}</textarea>
          <div id="ocrSuggestions" class="ocr-suggestions" hidden></div>
          <p class="meta small-tip">Tip: sugestiile apar lângă cursor. ↑/↓ navighează · Enter/Tab acceptă · Esc închide · Ctrl+Space afișează sugestii.</p>
          <div class="actions">
            <button type="submit">{_ut("ui.button.save_page_correction", "Save page correction")}</button>
            <a href="/review-ocr-corrected?pdf={quote(pdf_name)}&page={page}">{_ut("ui.link.reload", "Reload")}</a>
          </div>
        </form>

        <div class="suspects">
          <h3>{_ut("ui.heading.suspicious_pages", "Suspicious pages")}</h3>
          <p class="meta">Primele pagini unde OCR-ul pare suspect.</p>
          {suspicious_nav if suspicious_nav else '<p class="meta">' + _ut("status.no_suspicious_pages_detected", "No suspicious pages detected.") + '</p>'}
        </div>
      </section>
    </div>
  </div>

  <nav class="floating-nav">
    <a href="/review-ocr-corrected?pdf={quote(pdf_name)}&page={previous_page}">← {_ut("ui.link.prev", "Prev")}</a>
    <a href="/review-ocr-corrected?pdf={quote(pdf_name)}&page={next_page}">{_ut("ui.link.next", "Next")} →</a>
    <a href="/review-concepts?pdf={quote(pdf_name)}">{_ut("ui.link.concepts", "Concepts")}</a>
    <a href="/study?pdf={quote(pdf_name)}">{_ut("ui.link.study", "Study")}</a>
  </nav>

  <script>
    let scanZoom = 1.0;

    function getScanElements() {{
      return {{
        img: document.getElementById("scanImage"),
        viewport: document.getElementById("scanViewport")
      }};
    }}

    function updateZoomLabels() {{
      const label = Math.round(scanZoom * 100) + "%";
      document.querySelectorAll("[data-zoom-label]").forEach((el) => {{
        el.textContent = label;
      }});
    }}

    function applyScanZoom() {{
      const {{ img }} = getScanElements();

      if (!img) {{
        return;
      }}

      const naturalWidth = img.naturalWidth || img.width || 1000;
      img.style.width = Math.max(120, naturalWidth * scanZoom) + "px";
      updateZoomLabels();
    }}

    function zoomScan(delta) {{
      scanZoom = Math.min(4.0, Math.max(0.25, scanZoom + delta));
      applyScanZoom();
    }}

    function resetScanZoom() {{
      scanZoom = 1.0;
      applyScanZoom();
    }}

    function fitScanWidth() {{
      const {{ img, viewport }} = getScanElements();

      if (!img || !viewport) {{
        return;
      }}

      const naturalWidth = img.naturalWidth || img.width || 1000;
      const availableWidth = Math.max(240, viewport.clientWidth - 24);

      scanZoom = Math.min(4.0, Math.max(0.25, availableWidth / naturalWidth));
      applyScanZoom();
      viewport.scrollLeft = 0;
    }}

    window.addEventListener("load", () => {{
      document.querySelectorAll(".scan-floating-zoom").forEach((el) => el.remove());
      applyScanZoom();
      enableScanPan();
      enableOcrAutocomplete();
    }});


    function enableScanPan() {{
      const viewport = document.getElementById("scanViewport");

      if (!viewport || viewport.dataset.panEnabled === "1") {{
        return;
      }}

      viewport.dataset.panEnabled = "1";

      let isDragging = false;
      let startX = 0;
      let startY = 0;
      let startScrollLeft = 0;
      let startScrollTop = 0;

      viewport.addEventListener("pointerdown", (event) => {{
        isDragging = true;
        startX = event.clientX;
        startY = event.clientY;
        startScrollLeft = viewport.scrollLeft;
        startScrollTop = viewport.scrollTop;
        viewport.classList.add("dragging");
        viewport.setPointerCapture(event.pointerId);
        event.preventDefault();
      }});

      viewport.addEventListener("pointermove", (event) => {{
        if (!isDragging) {{
          return;
        }}

        const dx = event.clientX - startX;
        const dy = event.clientY - startY;

        viewport.scrollLeft = startScrollLeft - dx;
        viewport.scrollTop = startScrollTop - dy;
        event.preventDefault();
      }});

      function stopDragging(event) {{
        if (!isDragging) {{
          return;
        }}

        isDragging = false;
        viewport.classList.remove("dragging");

        try {{
          viewport.releasePointerCapture(event.pointerId);
        }} catch (_) {{}}
      }}

      viewport.addEventListener("pointerup", stopDragging);
      viewport.addEventListener("pointercancel", stopDragging);
      viewport.addEventListener("pointerleave", stopDragging);
    }}

    document.addEventListener("wheel", (event) => {{
      const viewport = document.getElementById("scanViewport");

      if (!viewport || !event.ctrlKey) {{
        return;
      }}

      if (!viewport.contains(event.target)) {{
        return;
      }}

      event.preventDefault();
      zoomScan(event.deltaY < 0 ? 0.12 : -0.12);
    }}, {{ passive: false }});

    // OCR autocomplete start
    function getCurrentOcrWord(textarea) {{
      const cursor = textarea.selectionStart || 0;
      const before = textarea.value.slice(0, cursor);
      const match = before.match(/[A-Za-zĂÂÎȘȚăâîșț0-9-]+$/);

      if (!match) {{
        return null;
      }}

      const word = match[0];

      return {{
        word: word,
        start: cursor - word.length,
        end: cursor
      }};
    }}

    function getTextareaCaretViewportPosition(textarea) {{
      const position = textarea.selectionStart || 0;
      const style = window.getComputedStyle(textarea);
      const rect = textarea.getBoundingClientRect();

      const mirror = document.createElement("div");
      mirror.style.position = "absolute";
      mirror.style.visibility = "hidden";
      mirror.style.whiteSpace = "pre-wrap";
      mirror.style.overflowWrap = "break-word";
      mirror.style.wordWrap = "break-word";
      mirror.style.top = "0";
      mirror.style.left = "-9999px";
      mirror.style.width = textarea.clientWidth + "px";
      mirror.style.fontFamily = style.fontFamily;
      mirror.style.fontSize = style.fontSize;
      mirror.style.fontWeight = style.fontWeight;
      mirror.style.letterSpacing = style.letterSpacing;
      mirror.style.lineHeight = style.lineHeight;
      mirror.style.paddingTop = style.paddingTop;
      mirror.style.paddingRight = style.paddingRight;
      mirror.style.paddingBottom = style.paddingBottom;
      mirror.style.paddingLeft = style.paddingLeft;
      mirror.style.borderTopWidth = style.borderTopWidth;
      mirror.style.borderRightWidth = style.borderRightWidth;
      mirror.style.borderBottomWidth = style.borderBottomWidth;
      mirror.style.borderLeftWidth = style.borderLeftWidth;

      const before = textarea.value.slice(0, position);
      const after = textarea.value.slice(position);

      mirror.textContent = before;

      const marker = document.createElement("span");
      marker.textContent = after.length ? after[0] : ".";
      mirror.appendChild(marker);

      document.body.appendChild(mirror);

      const markerRect = marker.getBoundingClientRect();
      const mirrorRect = mirror.getBoundingClientRect();

      const lineHeight = parseFloat(style.lineHeight) || 24;

      const left = rect.left + (markerRect.left - mirrorRect.left) - textarea.scrollLeft;
      const top = rect.top + (markerRect.top - mirrorRect.top) - textarea.scrollTop + lineHeight + 4;

      document.body.removeChild(mirror);

      return {{
        left: left,
        top: top
      }};
    }}

    let ocrSuggestionTimer = null;
    let ocrLastSuggestions = [];
    let ocrActiveSuggestionIndex = 0;

    function getOcrSuggestionBox() {{
      return document.getElementById("ocrSuggestions");
    }}

    function ocrSuggestionBoxVisible() {{
      const box = getOcrSuggestionBox();
      return !!box && !box.hidden && ocrLastSuggestions.length > 0;
    }}

    function hideOcrSuggestions() {{
      const box = getOcrSuggestionBox();

      if (!box) {{
        return;
      }}

      box.hidden = true;
      box.innerHTML = "";
      ocrLastSuggestions = [];
      ocrActiveSuggestionIndex = 0;
    }}

    function positionOcrSuggestions() {{
      const textarea = document.getElementById("ocrTextArea");
      const box = getOcrSuggestionBox();

      if (!textarea || !box || box.hidden) {{
        return;
      }}

      const pos = getTextareaCaretViewportPosition(textarea);

      const boxWidth = Math.min(520, Math.max(280, box.offsetWidth || 320));
      const boxHeight = Math.min(280, box.offsetHeight || 220);

      let left = pos.left;
      let top = pos.top;

      if (left + boxWidth > window.innerWidth - 12) {{
        left = window.innerWidth - boxWidth - 12;
      }}

      if (left < 12) {{
        left = 12;
      }}

      if (top + boxHeight > window.innerHeight - 12) {{
        top = pos.top - boxHeight - 30;
      }}

      if (top < 12) {{
        top = 12;
      }}

      box.style.left = left + "px";
      box.style.top = top + "px";
    }}

    function renderOcrSuggestions(suggestions) {{
      const box = getOcrSuggestionBox();

      if (!box) {{
        return;
      }}

      ocrLastSuggestions = suggestions || [];
      ocrActiveSuggestionIndex = 0;

      if (!ocrLastSuggestions.length) {{
        hideOcrSuggestions();
        return;
      }}

      box.innerHTML = "";

      ocrLastSuggestions.forEach(function(word, index) {{
        const button = document.createElement("button");
        button.type = "button";
        button.className = index === ocrActiveSuggestionIndex ? "ocr-suggestion active" : "ocr-suggestion";
        button.textContent = word;
        button.dataset.index = String(index);
        button.dataset.word = word;

        button.addEventListener("mousedown", function(event) {{
          event.preventDefault();
        }});

        button.addEventListener("mouseenter", function() {{
          setActiveOcrSuggestion(index);
        }});

        button.addEventListener("click", function() {{
          insertOcrSuggestion(word);
        }});

        box.appendChild(button);
      }});

      box.hidden = false;
      positionOcrSuggestions();
    }}

    function setActiveOcrSuggestion(index) {{
      if (!ocrLastSuggestions.length) {{
        return;
      }}

      if (index < 0) {{
        index = ocrLastSuggestions.length - 1;
      }}

      if (index >= ocrLastSuggestions.length) {{
        index = 0;
      }}

      ocrActiveSuggestionIndex = index;

      const box = getOcrSuggestionBox();

      if (!box) {{
        return;
      }}

      box.querySelectorAll(".ocr-suggestion").forEach(function(button, i) {{
        button.classList.toggle("active", i === ocrActiveSuggestionIndex);

        if (i === ocrActiveSuggestionIndex) {{
          button.scrollIntoView({{ block: "nearest" }});
        }}
      }});
    }}

    function insertOcrSuggestion(value) {{
      const textarea = document.getElementById("ocrTextArea");

      if (!textarea) {{
        return;
      }}

      const info = getCurrentOcrWord(textarea);

      if (!info) {{
        return;
      }}

      const before = textarea.value.slice(0, info.start);
      const after = textarea.value.slice(info.end);

      textarea.value = before + value + after;

      const nextCursor = before.length + value.length;
      textarea.focus();
      textarea.setSelectionRange(nextCursor, nextCursor);

      hideOcrSuggestions();

      textarea.dispatchEvent(new Event("input", {{ bubbles: true }}));
    }}

    function refreshOcrSuggestions(force) {{
      const textarea = document.getElementById("ocrTextArea");

      if (!textarea) {{
        return;
      }}

      const info = getCurrentOcrWord(textarea);

      if (!info || (!force && info.word.length < 2)) {{
        hideOcrSuggestions();
        return;
      }}

      const pdfName = document.body.dataset.pdfName || "";
      const query = info ? info.word : "";
      const url = "/review-ocr-text/suggestions?pdf=" + encodeURIComponent(pdfName) + "&q=" + encodeURIComponent(query) + "&limit=12";

      fetch(url)
        .then(function(response) {{
          return response.json();
        }})
        .then(function(data) {{
          renderOcrSuggestions(data.suggestions || []);
        }})
        .catch(function() {{
          hideOcrSuggestions();
        }});
    }}

    function scheduleOcrSuggestions() {{
      clearTimeout(ocrSuggestionTimer);
      ocrSuggestionTimer = setTimeout(function() {{
        refreshOcrSuggestions(false);
      }}, 90);
    }}

    function enableOcrAutocomplete() {{
      const textarea = document.getElementById("ocrTextArea");

      if (!textarea || textarea.dataset.autocompleteEnabled === "1") {{
        return;
      }}

      textarea.dataset.autocompleteEnabled = "1";

      textarea.addEventListener("input", scheduleOcrSuggestions);
      textarea.addEventListener("click", scheduleOcrSuggestions);
      textarea.addEventListener("scroll", positionOcrSuggestions);

      textarea.addEventListener("keydown", function(event) {{
        if (event.ctrlKey && event.code === "Space") {{
          event.preventDefault();
          refreshOcrSuggestions(true);
          return;
        }}

        if (!ocrSuggestionBoxVisible()) {{
          return;
        }}

        if (event.key === "ArrowDown") {{
          event.preventDefault();
          setActiveOcrSuggestion(ocrActiveSuggestionIndex + 1);
          return;
        }}

        if (event.key === "ArrowUp") {{
          event.preventDefault();
          setActiveOcrSuggestion(ocrActiveSuggestionIndex - 1);
          return;
        }}

        if (event.key === "Tab" || event.key === "Enter") {{
          event.preventDefault();
          insertOcrSuggestion(ocrLastSuggestions[ocrActiveSuggestionIndex]);
          return;
        }}

        if (event.key === "Escape") {{
          event.preventDefault();
          hideOcrSuggestions();
          return;
        }}
      }});

      window.addEventListener("resize", positionOcrSuggestions);
      window.addEventListener("scroll", positionOcrSuggestions, true);
    }}

    document.addEventListener("DOMContentLoaded", function() {{
      enableOcrAutocomplete();
    }});
    // OCR autocomplete end


</script>

</body>
</html>
"""

    return HTMLResponse(html_doc)


@app.post("/review-ocr-text/save")
def save_ocr_text_page(
    pdf: str = Form(...),
    page: int = Form(...),
    text: str = Form(...),
):
    from datetime import datetime, timezone
    from fastapi.responses import HTMLResponse, RedirectResponse
    from urllib.parse import quote
    import traceback

    try:
        pdf_name = _safe_pdf_name(pdf)
        output_dir = _output_dir_for_pdf_name(pdf_name)
        pages = _load_ocr_review_pages(output_dir)

        if not pages:
            return HTMLResponse("<h1>" + _ut("error.no_ocr_pages_found", "No OCR pages found") + "</h1>", status_code=404)

        changed = False

        for item in pages:
            if int(item["page_number"]) == int(page):
                item["text"] = str(text or "").strip()
                changed = True
                break

        if not changed:
            return HTMLResponse(f"<h1>{_ut('error.page_not_found', 'Page not found')}: {_html_escape(str(page))}</h1>", status_code=404)

        overrides_path = output_dir / "ocr_page_text_overrides.json"
        overrides = _load_json_file(
            overrides_path,
            {
                "version": "1.0",
                "pages": {},
            },
        )

        overrides.setdefault("pages", {})[str(page)] = {
            "text": str(text or "").strip(),
            "source": "manual_ui",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        _save_json_file(overrides_path, overrides)
        _write_ocr_review_pages(output_dir, pages)

        return RedirectResponse(
            f"/review-ocr-corrected?pdf={quote(pdf_name)}&page={int(page)}",
            status_code=303,
        )

    except Exception:
        error = traceback.format_exc()
        return HTMLResponse(
            f"""
            <h1>{_ut("error.save_ocr_text_failed", "Save OCR text failed")}</h1>
            <pre style="white-space: pre-wrap; background:#111; color:#f6ead7; padding:16px; border-radius:12px;">{_html_escape(error)}</pre>
            <p><a href="/">{_ut("ui.link.back", "Back")}</a></p>
            """,
            status_code=500,
        )


@app.get("/review-ocr-text/rebuild")
def rebuild_after_ocr_text_review(pdf: str = ""):
    from fastapi.responses import HTMLResponse
    import subprocess
    import sys
    import traceback
    from urllib.parse import quote

    try:
        pdf_name = _safe_pdf_name(pdf)
        output_dir = _output_dir_for_pdf_name(pdf_name)
        pdf_path = PROJECT_ROOT / "data" / "input" / pdf_name
        course_html = output_dir / "course.cleaned.html"

        steps = [
            [
                sys.executable,
                str(PROJECT_ROOT / "services" / "api" / "ocr_course_builder.py"),
                str(output_dir),
                "--pdf-name",
                pdf_name,
                "--min-page",
                "15",
                "--pages-per-lesson",
                "2",
                "--max-lessons",
                "260",
            ],
            [
                sys.executable,
                str(PROJECT_ROOT / "services" / "api" / "html_exporter.py"),
                str(output_dir / "course.cleaned.md"),
            ],
            [
                sys.executable,
                str(PROJECT_ROOT / "services" / "api" / "course_nav_injector.py"),
                str(course_html),
                pdf_name,
            ],
            [
                sys.executable,
                str(PROJECT_ROOT / "services" / "api" / "study_quiz_builder.py"),
                str(output_dir),
                "--min-page",
                "15",
                "--max-per-lesson",
                "3",
                "--max-total",
                "500",
            ],
            [
                sys.executable,
                str(PROJECT_ROOT / "services" / "api" / "ocr_corrections_engine.py"),
                "apply-titles",
                str(output_dir),
            ],
        ]

        logs = []

        for step in steps:
            result = subprocess.run(
                step,
                cwd=str(PROJECT_ROOT),
                text=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
            )

            logs.append("$ " + " ".join(step))
            logs.append(result.stdout)

            if result.stderr:
                logs.append("STDERR:")
                logs.append(result.stderr)

            if result.returncode != 0:
                raise RuntimeError("\n".join(logs))

        state = output_dir / "study_state.json"

        if state.exists():
            state.unlink()

        log_text = "\n".join(logs)

        return HTMLResponse(
            f"""
            <h1>{_ut("status.rebuild_complete", "Rebuild complete")}</h1>
            <p>{_ut("ui.message.ocr_corrections_applied", "OCR text corrections were applied to course and study.")}</p>
            <p>
              <a href="/review-ocr-corrected?pdf={quote(pdf_name)}">{_ut("ui.link.back_to_ocr_review", "Back to OCR Review")}</a>
              · <a href="/review-concepts?pdf={quote(pdf_name)}">{_ut("ui.review_concepts", "Review Concepts")}</a>
              · <a href="/study?pdf={quote(pdf_name)}">{_ut("ui.link.study", "Study")}</a>
            </p>
            <pre style="white-space: pre-wrap; background:#111; color:#f6ead7; padding:16px; border-radius:12px;">{_html_escape(log_text)}</pre>
            """
        )

    except Exception:
        error = traceback.format_exc()
        return HTMLResponse(
            f"""
            <h1>{_ut("status.rebuild_failed", "Rebuild failed")}</h1>
            <pre style="white-space: pre-wrap; background:#111; color:#f6ead7; padding:16px; border-radius:12px;">{_html_escape(error)}</pre>
            """,
            status_code=500,
        )




@app.get("/review-ocr-text/suggestions")
def review_ocr_text_suggestions(pdf: str = "", q: str = "", limit: int = 12):
    from fastapi.responses import JSONResponse
    from collections import Counter
    import re

    pdf_name = _safe_pdf_name(pdf)

    if not pdf_name:
        return JSONResponse({"suggestions": []})

    output_dir = _output_dir_for_pdf_name(pdf_name)
    pages = _load_ocr_review_pages(output_dir)

    query = str(q or "").strip().lower()

    if len(query) < 2:
        return JSONResponse({"suggestions": []})

    technical_words = [
        "instalații", "electrice", "automatizare", "iluminat", "tensiune",
        "curent", "putere", "energie", "circuit", "circuite", "protecție",
        "alimentare", "distribuție", "comandă", "măsurare", "reglare",
        "control", "siguranță", "conductoare", "conductor", "echipamente",
        "tablouri", "aparate", "relee", "contactoare", "senzori",
        "rezistență", "impedanță", "frecvență", "factor", "defazaj",
        "luminos", "luminanță", "iluminare", "randament", "transformator",
        "motor", "monofazat", "trifazat", "împământare", "legare",
        "scurtcircuit", "suprasarcină", "declanșare", "automat",
        "automată", "sisteme", "scheme", "tehnologice", "principiu",
        "regulatoare", "traductoare", "ventilare", "climatizare",
        "temperatură", "presiune", "umiditate", "debit", "mărimi",
        "documentație", "obiective", "investiții", "publice", "tehnico",
        "economică", "proiectare", "execuție", "verificare",
    ]

    counter = Counter()

    for word in technical_words:
        normalized = word.lower()

        if normalized.startswith(query):
            counter[word] += 10000

    for page in pages:
        page_text = str(page.get("text") or "")

        for word in re.findall(r"[A-Za-zĂÂÎȘȚăâîșț0-9][A-Za-zĂÂÎȘȚăâîșț0-9\-]{2,}", page_text):
            clean = word.strip(".,:;()[]{}!?").lower()

            if len(clean) < 3:
                continue

            if clean.startswith(query):
                counter[clean] += 1

    suggestions = [
        word
        for word, _count in counter.most_common(max(1, min(limit, 30)))
    ]

    return JSONResponse({"suggestions": suggestions})




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




def _course_tools_button_html(pdf_name: str) -> str:
    from urllib.parse import quote
    safe = Path(str(pdf_name or "")).name
    q = quote(safe)
    return f'<a class="tool-link primary-tool" href="/course-tools?pdf={q}">{_ut("ui.course_tools", "Course Tools")}</a>'


def _voila_tools_bar(pdf_name: str, active: str = "") -> str:
    q = _nav_quote(pdf_name)

    links = [
        ("Tools", f"/course-tools?pdf={q}", "tools"),
        ("Course", f"/view-course?pdf={q}", "course"),
        ("Lessons", f"/lessons?pdf={q}", "lessons"),
        (_ut("ui.study", _ut("study", "Study")), f"/study?pdf={q}", "study"),
        (_ut("ui.review_ocr_text", "Review OCR Text"), f"/review-ocr-corrected?pdf={q}&page=1", "ocr"),
        (_ut("ui.review_concepts", "Review Concepts"), f"/review-concepts?pdf={q}", "concepts"),
        (_ut("ui.figures", "Figures"), f"/view-figures?pdf={q}", "figures"),
        (_ut("ui.edit_crops", "Edit crops"), f"/edit-crops?pdf={q}", "crops"),
        (_ut("ui.progress", _ut("progress", "Progress")), f"/progress?pdf={q}", "progress"),
        (_ut("ui.library", _ut("library", "Library")), "/", "library"),
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
        return HTMLResponse("<h1>" + _ut("error.missing_pdf_name", "Missing PDF name") + "</h1>", status_code=400)

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
        suffix = "" if enabled else f'<span>{_ut("status.not_generated_yet", "Not generated yet")}</span>'
        safe_href = href if enabled else "#"

        return f"""
        <a class="card {cls}" href="{safe_href}">
          <h2>{_nav_escape(title)}</h2>
          <p>{_nav_escape(description)}</p>
          {suffix}
        </a>
        """

    cards = [
        card(_ut("ui.open_course", _ut("open_course", "Open course")), _ut("message.open_course_description", "Read the generated course with navigation."), f"/view-course?pdf={q}", checks["course"]),
        card(_ut("ui.lessons", _ut("lessons", "Lessons")), _ut("message.lessons_description", "Choose a lesson, read it, then study only that lesson."), f"/lessons?pdf={q}", checks["study"]),
        card(_ut("ui.study_mode", "Study mode"), _ut("message.study_mode_description", "Practice questions generated from the course."), f"/study?pdf={q}", checks["study"]),
        card(_ut("ui.review_ocr_text", "Review OCR Text"), _ut("message.review_ocr_text_description", "Correct OCR text page by page."), f"/review-ocr-corrected?pdf={q}&page=1", checks["ocr"]),
        card(_ut("ui.review_study_concepts", "Review Study Concepts"), _ut("message.review_concepts_description", "Correct lesson and concept titles."), f"/review-concepts?pdf={q}", checks["concepts"]),
        card(_ut("ui.figures", "Figures"), _ut("message.figures_description", "View extracted figures."), f"/view-figures?pdf={q}", checks["figures"]),
        card(_ut("ui.edit_crops", "Edit crops"), _ut("message.edit_crops_description", "Manually edit figure crops."), f"/edit-crops?pdf={q}", checks["figures"]),
        card(_ut("ui.progress", _ut("progress", "Progress")), _ut("message.progress_description", "View study progress."), f"/progress?pdf={q}", checks["study"]),
        card(_ut("ui.exam_prep", "Exam Prep"), _ut("exam_prep.foundation_description", "Foundation dashboard for skill-based exam preparation. Progress is updated from Study Mode."), "/exam-prep", checks["study"]),
        card(_ut("ui.library", _ut("library", "Library")), _ut("message.return_to_library_description", "Return to the main course library."), "/", True),
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
  <title>{_ut("ui.course_tools", "Course Tools")} · Voila!</title>
  {css}
</head>
<body>
  <div class="wrap">
    <h1>{_ut("ui.course_tools", "Course Tools")}</h1>
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
        return HTMLResponse("<h1>" + _ut("error.missing_pdf_name", "Missing PDF name") + "</h1>", status_code=400)

    output_dir = _nav_output_dir(pdf_name)
    course_html = output_dir / "course.cleaned.html"

    if not course_html.exists():
        return HTMLResponse("<h1>" + _ut("error.course_html_not_found", "Course HTML not found") + "</h1>", status_code=404)

    html_doc = course_html.read_text(encoding="utf-8", errors="ignore")
    html_doc = _inject_voila_tools_bar(html_doc, pdf_name, "course")

    return HTMLResponse(html_doc)


@app.get("/view-figures")
def view_figures(pdf: str = ""):
    from fastapi.responses import HTMLResponse

    pdf_name = _nav_safe_pdf_name(pdf)

    if not pdf_name:
        return HTMLResponse("<h1>" + _ut("error.missing_pdf_name", "Missing PDF name") + "</h1>", status_code=400)

    output_dir = _nav_output_dir(pdf_name)
    figures_html = output_dir / "figures_hybrid" / "figures_hybrid.html"

    if not figures_html.exists():
        return HTMLResponse("<h1>" + _ut("error.figures_html_not_found", "Figures HTML not found") + "</h1>", status_code=404)

    html_doc = figures_html.read_text(encoding="utf-8", errors="ignore")

    base = "/output/" + _nav_quote(output_dir.name) + "/figures_hybrid/"
    html_doc = html_doc.replace('src="crops/', f'src="{base}crops/')
    html_doc = html_doc.replace("src='crops/", f"src='{base}crops/")

    html_doc = _inject_voila_tools_bar(html_doc, pdf_name, "figures")

    return HTMLResponse(html_doc)




@app.get("/quick-tools")
def quick_tools():
    from fastapi.responses import HTMLResponse
    from urllib.parse import quote
    import i18n

    ui_state = i18n.get_ui_language(PROJECT_ROOT)
    current_ui_language = str(ui_state.get("ui_language") or "ro")
    supported_ui_languages = ui_state.get("supported") or {}

    language_options = []
    for code, label in supported_ui_languages.items():
        selected = " selected" if str(code) == current_ui_language else ""
        language_options.append(
            f'<option value="{html.escape(str(code))}"{selected}>{html.escape(str(label))}</option>'
        )

    language_selector = f"""
      <form method="post" action="/ui-language-form" style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:0;">
        <label for="uiLanguageSelect" style="font-weight:800;color:var(--muted);">{_ut("ui_language", "Interface language")}</label>
        <select id="uiLanguageSelect" name="language" onchange="this.form.submit()" style="border:1px solid var(--line);border-radius:999px;padding:10px 14px;background:var(--panel2);color:var(--text);font-weight:800;">
          {''.join(language_options)}
        </select>
        <noscript><button type="submit">{_ut("save", "Save")}</button></noscript>
      </form>
    """

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
            status_label = _ut(f"ui.status.{key}", key)
            status.append(f"<span class='{key if ok else 'missing'}'>{html.escape(status_label)}: {'OK' if ok else '-'}</span>")

        cards.append(f"""
        <section class="card">
          <h2>{_nav_escape(pdf.name)}</h2>
          <p>{''.join(status)}</p>
          <div class="actions">
            <a class="primary" href="/course-tools?pdf={q}">{_ut("ui.course_tools", "Course Tools")}</a>
            <a href="/view-course?pdf={q}">{_ut("ui.link.course", "Course")}</a>
            <a href="/study?pdf={q}">{_ut("ui.link.study", "Study")}</a>
            <a href="/review-ocr-corrected?pdf={q}&page=1">{_ut("ui.link.review_ocr", "Review OCR")}</a>
            <a href="/review-concepts?pdf={q}">{_ut("ui.link.concepts", "Concepts")}</a>
          </div>
        </section>
        """)

    html_doc = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{_ut("ui.quick_tools", "Quick Tools")} · Voila!</title>
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
      <h1>{_ut("ui.quick_tools", "Quick Tools")}</h1>
      <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
        {language_selector}
        <a href="/">{_ut("library", "Library")}</a>
      </div>
    </div>
    {''.join(cards) if cards else '<p>' + _ut("ui.message.no_pdfs_found", "No PDFs found.") + '</p>'}
  </div>
</body>
</html>
"""

    return HTMLResponse(html_doc)



# VOILA_OCR_CORRECTION_ROUTES_V1

from fastapi import Request as _VoilaRequest
from fastapi.responses import HTMLResponse as _VoilaHTMLResponse
from fastapi.responses import RedirectResponse as _VoilaRedirectResponse
from fastapi.responses import Response as _VoilaResponse


def _voila_safe_pdf_name(pdf: str) -> str:
    return Path(str(pdf or "")).name


def _voila_ocr_out_dir(pdf: str) -> Path:
    return PROJECT_ROOT / "data" / "output" / Path(_voila_safe_pdf_name(pdf)).stem


def _voila_page_count_for_pdf(pdf: str) -> int:
    import fitz

    pdf_path = PROJECT_ROOT / "data" / "input" / _voila_safe_pdf_name(pdf)

    if not pdf_path.exists():
        return 1

    doc = fitz.open(pdf_path)

    try:
        return max(1, len(doc))
    finally:
        doc.close()


@app.get("/ocr-page-image")
def voila_ocr_page_image(pdf: str = "", page: int = 1, zoom: float = 2.2):
    import fitz

    safe_pdf = _voila_safe_pdf_name(pdf)
    pdf_path = PROJECT_ROOT / "data" / "input" / safe_pdf

    if not pdf_path.exists():
        return _VoilaResponse(_ut("error.pdf_not_found", "PDF not found"), status_code=404)

    page_index = max(0, int(page) - 1)

    doc = fitz.open(pdf_path)

    try:
        page_index = min(page_index, len(doc) - 1)
        pix = doc.load_page(page_index).get_pixmap(
            matrix=fitz.Matrix(float(zoom), float(zoom)),
            colorspace=fitz.csRGB,
            alpha=False,
        )
        png = pix.tobytes("png")
    finally:
        doc.close()

    return _VoilaResponse(content=png, media_type="image/png")


@app.get("/review-ocr-corrected")
def voila_review_ocr_corrected(pdf: str = "", page: int = 1, saved: int = 0, applied: int = 0):
    import html
    from urllib.parse import quote
    import ocr_page_corrections as oc

    safe_pdf = _voila_safe_pdf_name(pdf)
    out_dir = _voila_ocr_out_dir(safe_pdf)

    page_count = _voila_page_count_for_pdf(safe_pdf)
    page_number = max(1, min(int(page or 1), page_count))

    original_text = oc.get_page_text(out_dir, page_number)
    corrected_text = oc.get_corrected_text(out_dir, page_number)

    if not str(corrected_text or "").strip():
        try:
            import ocr_best_text as obt
            corrected_text = obt.get_best_page_text(out_dir, page_number)
        except Exception:
            pass

    corr_data = oc.load_corrections(out_dir)
    item = corr_data.get("page_corrections", {}).get(str(page_number), {})
    status = item.get("status") if isinstance(item, dict) else ""

    q_pdf = quote(safe_pdf)

    prev_page = max(1, page_number - 1)
    next_page = min(page_count, page_number + 1)

    saved_msg = ""
    if int(saved or 0):
        saved_msg = '<div class="notice ok">Saved correction.</div>'

    applied_msg = ""
    if int(applied or 0):
        applied_msg = '<div class="notice ok">Applied corrected OCR to pages.json / ocr_pages.json.</div>'

    css = """
    :root {
      --bg: #101819;
      --panel: #202d31;
      --panel2: #26363b;
      --text: #f6ead7;
      --muted: #c7ad94;
      --line: #3b4b50;
      --accent: #e0ad68;
      --danger: #b85757;
      --ok: #6fa878;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: system-ui, -apple-system, Segoe UI, sans-serif;
    }

    header {
      position: sticky;
      top: 0;
      z-index: 20;
      background: rgba(16, 24, 25, 0.96);
      border-bottom: 1px solid var(--line);
      padding: 14px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }

    h1 {
      margin: 0;
      font-size: 22px;
      line-height: 1.2;
    }

    .muted { color: var(--muted); }

    .actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }

    a, button {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 9px 13px;
      background: var(--panel2);
      color: var(--text);
      text-decoration: none;
      font-weight: 850;
      cursor: pointer;
    }

    button.primary, a.primary {
      background: var(--accent);
      color: white;
      border-color: transparent;
    }

    button.danger {
      background: var(--danger);
      color: white;
      border-color: transparent;
    }

    main {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 16px;
      padding: 16px;
      height: calc(100vh - 76px);
      overflow: hidden;
    }

    .pane {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 20px;
      overflow: hidden;
      min-height: 0;
      min-width: 0;
    }

    .pane-title {
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      color: var(--muted);
      font-weight: 800;
      display: flex;
      justify-content: space-between;
      gap: 10px;
    }

    .scan-wrap {
      width: 100%;
      height: calc(100% - 48px);
      overflow: auto;
      cursor: grab;
      background: #0b1112;
      padding: 16px;
    }

    .scan-wrap:active { cursor: grabbing; }

    .scan-wrap img {
      max-width: none;
      width: var(--scan-zoom, 100%);
      display: block;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0,0,0,.35);
      user-select: none;
      pointer-events: none;
    }

    form.editor {
      height: calc(100% - 48px);
      display: flex;
      flex-direction: column;
      gap: 10px;
      padding: 14px;
    }

    textarea {
      flex: 1;
      min-height: 0;
      width: 100%;
      resize: none;
      border-radius: 16px;
      border: 1px solid var(--line);
      background: #111b1e;
      color: var(--text);
      padding: 14px;
      font-family: Consolas, ui-monospace, monospace;
      font-size: 16px;
      line-height: 1.45;
      outline: none;
    }

    .notice {
      margin: 0 16px 12px;
      padding: 10px 12px;
      border-radius: 14px;
      font-weight: 800;
    }

    .notice.ok {
      background: rgba(111,168,120,.18);
      color: #bde7c3;
      border: 1px solid rgba(111,168,120,.35);
    }

    .hint {
      font-size: 13px;
      color: var(--muted);
      padding: 0 2px 4px;
    }

    @media (max-width: 980px) {
      main {
        grid-template-columns: 1fr;
        height: auto;
      }

      .pane {
        min-height: 70vh;
      }
    }
    """

    html_doc = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{_ut("ui.title.correct_ocr", "Correct OCR · Voila!")}</title>
  <style>{css}</style>
  <link rel="stylesheet" href="/voila-static/ocr_review_monaco.css?v=1778302140">
</head>
<body>
  <header>
    <div>
      <h1>{_ut("ui.correct_ocr_text", "Correct OCR Text")}</h1>
      <div class="muted">{html.escape(safe_pdf)} · page {page_number} / {page_count} · status: {html.escape(str(status or "not reviewed"))}</div>
    </div>

    <div class="actions">
      <a href="/course-tools?pdf={q_pdf}">{_ut("ui.course_tools", "Course Tools")}</a>
      <a href="/review-ocr-corrected?pdf={q_pdf}&page={prev_page}">← {_ut("ui.link.prev", "Prev")}</a>
      <a href="/review-ocr-corrected?pdf={q_pdf}&page={next_page}">{_ut("ui.link.next", "Next")} →</a>
    </div>
  </header>

  {saved_msg}
  {applied_msg}

  <main>
    <section class="pane">
      <div class="pane-title">
        <span>Scanned page</span>
        <span>Tip: Ctrl + mouse wheel = zoom doar pe imagine; click + drag = mută pagina</span>
      </div>
      <div class="scan-wrap" id="scanWrap">
        <img src="/ocr-page-image?pdf={q_pdf}&page={page_number}&zoom=2.4" alt="page scan">
      </div>
    </section>

    <section class="pane">
      <div class="pane-title">
        <span>Editable corrected OCR</span>
        <span>{len(corrected_text)} chars</span>
      </div>

      <form class="editor" method="post" action="/save-ocr-correction">
        <input type="hidden" name="pdf" value="{html.escape(safe_pdf)}">
        <input type="hidden" name="page" value="{page_number}">

        <div class="hint">
          Corectează textul aici. Save păstrează corecția în <code>ocr_corrections.json</code>.
        </div>

        <textarea name="text" spellcheck="false">{html.escape(corrected_text)}</textarea>

        <div class="actions">
          <button class="primary" type="submit" name="status" value="reviewed">{_ut("ui.button.save_reviewed_page", "Save reviewed page")}</button>
          <button type="submit" name="status" value="needs_review">{_ut("ui.button.save_as_needs_review", "Save as needs review")}</button>
        </div>
      </form>

      <form method="post" action="/apply-corrected-ocr" style="padding:0 14px 14px;">
        <input type="hidden" name="pdf" value="{html.escape(safe_pdf)}">
        <button class="danger" type="submit">{_ut("ui.button.apply_corrected_ocr", "Apply corrected OCR to pages.json")}</button>
      </form>
    </section>
  </main>

  <script>
    const box = document.getElementById('scanWrap');
    const img = box.querySelector('img');

    let isDown = false;
    let startX = 0;
    let startY = 0;
    let scrollLeft = 0;
    let scrollTop = 0;
    let scanZoom = 100;

    function setScanZoom(nextZoom) {{
      scanZoom = Math.max(45, Math.min(260, nextZoom));
      img.style.setProperty('--scan-zoom', scanZoom + '%');
    }}

    // Ctrl + mouse wheel zooms ONLY the scanned image.
    // It does not trigger browser zoom and does not resize the OCR editor pane.
    box.addEventListener('wheel', (e) => {{
      if (!e.ctrlKey) return;

      e.preventDefault();
      e.stopPropagation();

      const beforeX = box.scrollLeft + e.offsetX;
      const beforeY = box.scrollTop + e.offsetY;
      const oldZoom = scanZoom;

      const direction = e.deltaY < 0 ? 12 : -12;
      setScanZoom(scanZoom + direction);

      const ratio = scanZoom / oldZoom;
      box.scrollLeft = beforeX * ratio - e.offsetX;
      box.scrollTop = beforeY * ratio - e.offsetY;
    }}, {{ passive: false }});

    box.addEventListener('mousedown', (e) => {{
      isDown = true;
      startX = e.pageX - box.offsetLeft;
      startY = e.pageY - box.offsetTop;
      scrollLeft = box.scrollLeft;
      scrollTop = box.scrollTop;
    }});

    box.addEventListener('mouseleave', () => {{ isDown = false; }});
    box.addEventListener('mouseup', () => {{ isDown = false; }});

    box.addEventListener('mousemove', (e) => {{
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - box.offsetLeft;
      const y = e.pageY - box.offsetTop;
      box.scrollLeft = scrollLeft - (x - startX);
      box.scrollTop = scrollTop - (y - startY);
    }});
  </script>
  <script src="/voila-static/ocr_review_monaco.js?v=1778302140"></script>
</body>
</html>
"""

    return _VoilaHTMLResponse(html_doc)


@app.post("/save-ocr-correction")
async def voila_save_ocr_correction(request: _VoilaRequest):
    import ocr_page_corrections as oc
    from urllib.parse import quote

    form = await request.form()

    pdf = _voila_safe_pdf_name(str(form.get("pdf") or ""))
    page = int(form.get("page") or 1)
    text = str(form.get("text") or "")
    status = str(form.get("status") or "reviewed")

    out_dir = _voila_ocr_out_dir(pdf)

    oc.save_page_correction(
        out_dir=out_dir,
        page_number=page,
        text=text,
        status=status,
    )

    return _VoilaRedirectResponse(
        url=f"/review-ocr-corrected?pdf={quote(pdf)}&page={page}&saved=1",
        status_code=303,
    )


@app.post("/apply-corrected-ocr")
async def voila_apply_corrected_ocr(request: _VoilaRequest):
    import ocr_page_corrections as oc
    from urllib.parse import quote

    form = await request.form()

    pdf = _voila_safe_pdf_name(str(form.get("pdf") or ""))
    out_dir = _voila_ocr_out_dir(pdf)

    oc.apply_page_corrections(out_dir, pdf_name=pdf)

    return _VoilaRedirectResponse(
        url=f"/review-ocr-corrected?pdf={quote(pdf)}&page=1&applied=1",
        status_code=303,
    )



@app.get("/voila-static/{filename}")
def voila_static_file(filename: str):
    from fastapi.responses import Response

    safe_name = Path(str(filename or "")).name
    static_path = PROJECT_ROOT / "services" / "api" / "static" / safe_name

    if not static_path.exists() or not static_path.is_file():
        return Response(_ut("error.not_found", "Not found"), status_code=404)

    suffix = static_path.suffix.lower()

    if suffix == ".js":
        media_type = "text/javascript; charset=utf-8"
    elif suffix == ".css":
        media_type = "text/css; charset=utf-8"
    else:
        media_type = "text/plain; charset=utf-8"

    return Response(
        static_path.read_text(encoding="utf-8"),
        media_type=media_type,
    )





@app.post("/check-ocr-languagetool")
async def voila_check_ocr_languagetool(request: _VoilaRequest):
    from fastapi.responses import JSONResponse
    import ocr_languagetool as lt

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    try:
        result = lt.check_text(
            text=str(payload.get("text") or ""),
            language=str(payload.get("language") or "ro-RO"),
        )
    except Exception as exc:
        result = {
            "ok": False,
            "provider": "LanguageTool",
            "matches": [],
            "message": "Eroare internă la verificarea LanguageTool.",
            "error": str(exc),
        }

    return JSONResponse(result)



@app.get("/document-language")
def voila_get_document_language(pdf: str = ""):
    from fastapi.responses import JSONResponse
    import document_language as dl

    return JSONResponse(
        dl.get_document_language(PROJECT_ROOT, pdf)
    )


@app.post("/document-language")
async def voila_set_document_language(request: _VoilaRequest):
    from fastapi.responses import JSONResponse
    import document_language as dl

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    pdf = str(payload.get("pdf") or "")
    language = str(payload.get("language") or payload.get("document_language") or "auto")

    return JSONResponse(
        dl.set_document_language(PROJECT_ROOT, pdf, language)
    )



@app.post("/run-ocr-page")
async def voila_run_ocr_page(request: _VoilaRequest):
    from fastapi.responses import JSONResponse
    import subprocess
    import sys

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    pdf = str(payload.get("pdf") or "").strip()
    page = int(payload.get("page") or 1)
    psm = int(payload.get("psm") or 6)
    zoom = float(payload.get("zoom") or 3.0)
    columns = int(payload.get("columns") or 0)

    if not pdf:
        return JSONResponse(
            {
                "ok": False,
                "message": "PDF lipsă.",
            },
            status_code=400,
        )

    script = PROJECT_ROOT / "scripts" / "dev" / "run-ocr-page.py"

    if not script.exists():
        return JSONResponse(
            {
                "ok": False,
                "message": f"Nu găsesc scriptul OCR: {script}",
            },
            status_code=500,
        )

    cmd = [
        sys.executable,
        str(script),
        "--pdf",
        pdf,
        "--page",
        str(page),
        "--lang",
        "auto",
        "--psm",
        str(psm),
        "--zoom",
        str(zoom),
    ]

    if columns > 1:
        cmd.extend(["--columns", str(columns)])

    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=240,
        )
    except subprocess.TimeoutExpired:
        return JSONResponse(
            {
                "ok": False,
                "message": "OCR a durat prea mult și a fost oprit.",
            },
            status_code=504,
        )
    except Exception as exc:
        return JSONResponse(
            {
                "ok": False,
                "message": "Eroare la pornirea OCR.",
                "error": str(exc),
            },
            status_code=500,
        )

    ok = result.returncode == 0

    return JSONResponse(
        {
            "ok": ok,
            "message": "OCR pagină finalizat." if ok else "OCR pagină a eșuat.",
            "returncode": result.returncode,
            "stdout": (result.stdout or "")[-4000:],
            "stderr": (result.stderr or "")[-4000:],
        },
        status_code=200 if ok else 500,
    )



@app.post("/ui-language-form")
def voila_set_ui_language_form(
    language: str = Form(...),
) -> RedirectResponse:
    import i18n

    i18n.set_ui_language(PROJECT_ROOT, language)

    return RedirectResponse(url="/quick-tools", status_code=303)


@app.get("/ui-language")
def voila_get_ui_language():
    from fastapi.responses import JSONResponse
    import i18n

    return JSONResponse(
        i18n.get_ui_language(PROJECT_ROOT)
    )


@app.post("/ui-language")
async def voila_set_ui_language(request: _VoilaRequest):
    from fastapi.responses import JSONResponse
    import i18n

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    language = str(payload.get("language") or payload.get("ui_language") or "ro")

    return JSONResponse(
        i18n.set_ui_language(PROJECT_ROOT, language)
    )



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
          <div class="meta">#{index} · ID: <code>{html.escape(lesson_id)}</code> · {_ut("questions", "Questions")}: <strong>{questions_count}</strong> · {_ut("pages", "Pages")}: <strong>{html.escape(pages)}</strong></div>
          <h2>{html.escape(title)}</h2>
          <p>{html.escape(preview)}</p>
          <div class="actions">
            <a class="btn primary" href="/lesson?pdf={q_pdf}&lesson_id={quote(lesson_id)}">{_ut("open_lesson", "Open lesson")}</a>
            <a class="btn" href="/study-lesson?pdf={q_pdf}&lesson_id={quote(lesson_id)}">{_ut("study_lesson", "Study lesson")}</a>
          </div>
        </article>
        """)

    content = "\n".join(rows) if rows else """
    <article class="card">
      <h2>{_ut("no_lessons", "No lessons available")}</h2>
      <p>{_ut("generate_course_first_short", "Generate the course / quiz for this PDF first.")}</p>
    </article>
    """

    body = f"""
    <h1>{_ut("lessons", "Lessons")}</h1>

    <div class="notice">
      PDF: <strong>{html.escape(pdf_path.name)}</strong><br>
      {_ut("lessons_found", "Lessons found")}: <strong>{len(lessons)}</strong>
    </div>

    <div class="actions">
      <a class="btn" href="/course-tools?pdf={q_pdf}">{_ut("ui.course_tools", "Course Tools")}</a>
      <a class="btn" href="/view-course?pdf={q_pdf}">{_ut("ui.open_course", _ut("open_course", "Open course"))}</a>
      <a class="btn" href="/study?pdf={q_pdf}">{_ut("study", "Study")}</a>
      <a class="btn" href="/">{_ut("library", "Library")}</a>
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
        <h1>{_ut("lesson_not_found", "Lesson not found")}</h1>
        <p>Nu am găsit lecția <code>{html.escape(str(lesson_id))}</code>.</p>
        <p><a class="btn" href="/lessons?pdf={q_pdf}">{_ut("back_to_lessons", "Back to lessons")}</a></p>
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
        lesson_body = f"""<p>{_ut("no_source_text_for_lesson", "No source text is available for this lesson.")}</p>"""

    body = f"""
    <h1>{html.escape(title)}</h1>

    <div class="notice">
      PDF: <strong>{html.escape(pdf_path.name)}</strong><br>
      Lesson ID: <code>{html.escape(str(lesson_id))}</code><br>
      {_ut("pages", "Pages")}: <strong>{html.escape(pages)}</strong><br>
      {_ut("questions", "Questions")}: <strong>{int(lesson.get("questions_count") or 0)}</strong>
    </div>

    <div class="actions">
      <a class="btn" href="/lessons?pdf={q_pdf}">← {_ut("lessons", "Lessons")}</a>
      <a class="btn primary" href="/study-lesson?pdf={q_pdf}&lesson_id={q_lesson}">{_ut("study_lesson", "Study lesson")}</a>
      <a class="btn" href="/view-course?pdf={q_pdf}">{_ut("ui.open_course", _ut("open_course", "Open course"))}</a>
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
          <p>{_ut("no_questions_for_lesson", "No questions are available for the selected lesson.")}</p>
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
      <a class="btn" href="/lesson?pdf={q_pdf}&lesson_id={q_lesson}">{_ut("read_lesson", "Read lesson")}</a>
      <a class="btn" href="/lessons?pdf={q_pdf}">← {_ut("lessons", "Lessons")}</a>
      <a class="btn" href="/study?pdf={q_pdf}">{_ut("general_study", "General study")}</a>
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

# --- v0.4.6c safe Exam Prep dashboard skill links ---
try:
    from fastapi.responses import HTMLResponse as _V46CHTMLResponse
except Exception:
    _V46CHTMLResponse = None


def _v46c_fallback_skill_links_html() -> str:
    return (
        '<section class="exam-prep-skill-detail-links" style="margin-top:24px;background:#fff;'
        'border:1px solid #e5e7ef;border-radius:18px;padding:20px;">'
        '<h2>Detalii pe skill</h2>'
        '<p style="color:#667085;line-height:1.55;">'
        'Deschide un skill pentru descriere, progres și pașii de continuare în Study Mode.'
        '</p>'
        '<div class="skill-link-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin-top:14px;">'
        '<a style="display:block;border:1px solid #e5e7ef;border-radius:14px;padding:12px;text-decoration:none;color:#172033;background:#fff;font-weight:650;" href="/exam-prep/skill/derivate">Derivate</a>'
        '<a style="display:block;border:1px solid #e5e7ef;border-radius:14px;padding:12px;text-decoration:none;color:#172033;background:#fff;font-weight:650;" href="/exam-prep/skill/integrale">Integrale</a>'
        '<a style="display:block;border:1px solid #e5e7ef;border-radius:14px;padding:12px;text-decoration:none;color:#172033;background:#fff;font-weight:650;" href="/exam-prep/skill/functii">Funcții</a>'
        '<a style="display:block;border:1px solid #e5e7ef;border-radius:14px;padding:12px;text-decoration:none;color:#172033;background:#fff;font-weight:650;" href="/exam-prep/skill/geometrie">Geometrie</a>'
        '</div>'
        '</section>'
    )


def _v46c_skill_links_html() -> str:
    try:
        from services.api.exam_prep import render_exam_prep_skill_links_html
    except Exception:
        try:
            from exam_prep import render_exam_prep_skill_links_html
        except Exception:
            return _v46c_fallback_skill_links_html()

    try:
        html = render_exam_prep_skill_links_html()
    except Exception:
        html = ""

    if "/exam-prep/skill/" not in html:
        return _v46c_fallback_skill_links_html()

    return html


@app.middleware("http")
async def _v46c_exam_prep_dashboard_skill_links(request, call_next):
    response = await call_next(request)

    if request.url.path != "/exam-prep":
        return response

    content_type = response.headers.get("content-type", "")
    if response.status_code != 200 or "text/html" not in content_type:
        return response

    chunks = []
    async for chunk in response.body_iterator:
        if isinstance(chunk, str):
            chunk = chunk.encode("utf-8")
        chunks.append(chunk)

    text = b"".join(chunks).decode("utf-8", errors="replace")

    if "/exam-prep/skill/" not in text:
        links_html = _v46c_skill_links_html()

        if "</main>" in text:
            text = text.replace("</main>", links_html + "</main>", 1)
        elif "</body>" in text:
            text = text.replace("</body>", links_html + "</body>", 1)
        else:
            text = text + links_html

    headers = dict(response.headers)
    headers.pop("content-length", None)
    headers.pop("content-encoding", None)

    response_class = _V46CHTMLResponse
    if response_class is None:
        try:
            from fastapi.responses import HTMLResponse as response_class
        except Exception:
            return response

    return response_class(
        content=text,
        status_code=response.status_code,
        headers=headers,
    )
# --- end v0.4.6c safe Exam Prep dashboard skill links ---

# --- v0.4.6f clean safe Exam Prep skill detail route ---
from html import escape as _v46f_escape
from fastapi.responses import HTMLResponse as _V46FHTMLResponse


def _v46f_skill_label(skill_id: str) -> str:
    value = (skill_id or "").strip().lower()
    labels = {
        "derivate": "Derivate",
        "integrale": "Integrale",
        "functii": "Functii",
        "funcții": "Functii",
        "geometrie": "Geometrie",
    }
    return labels.get(value, (skill_id or "Skill").replace("_", " ").title())


def _v46f_fallback_skill_detail_page(skill_id: str) -> str:
    safe_id = _v46f_escape(skill_id or "")
    label = _v46f_escape(_v46f_skill_label(skill_id))

    return (
        '<!doctype html><html lang="ro"><head><meta charset="utf-8">'
        f'<title>Exam Prep - {label}</title>'
        '<style>'
        'body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0;background:#f7f7fb;color:#172033;}'
        'main{max-width:980px;margin:0 auto;padding:32px 20px 56px;}'
        '.card{background:#fff;border:1px solid #e5e7ef;border-radius:18px;padding:22px;box-shadow:0 10px 32px rgba(23,32,51,.06);}'
        '.muted{color:#667085;line-height:1.55;}'
        '.actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px;}'
        '.button{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;padding:10px 14px;text-decoration:none;border:1px solid #cfd6e6;color:#172033;background:#fff;font-weight:650;}'
        '.button.primary{background:#172033;color:#fff;border-color:#172033;}'
        '.metric-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:18px 0;}'
        '.metric{background:#f8fafc;border:1px solid #e5e7ef;border-radius:14px;padding:14px;}'
        '.metric strong{display:block;font-size:1.35rem;margin-top:4px;}'
        '</style></head><body><main><div class="card">'
        '<p class="muted">Pregatire examene - Bacalaureat - Matematica M1</p>'
        f'<h1>Detaliu skill: {label}</h1>'
        '<p>Skill din planul de pregatire Bacalaureat Matematica M1. '
        'Progresul se actualizeaza pe baza intrebarilor lucrate in Study Mode.</p>'
        '<div class="metric-grid">'
        '<div class="metric"><span>Stare consolidare</span><strong>Nepornit</strong>'
        '<small class="muted">Consolidat dupa lucru suficient in Study Mode</small></div>'
        '<div class="metric"><span>Scor progres</span><strong>-</strong>'
        '<small class="muted">read-only din Study Mode, unde exista</small></div>'
        '<div class="metric"><span>Intrebari Study legate</span><strong>0</strong>'
        '<small class="muted">din quiz.study.json</small></div>'
        '</div>'
        '<p class="muted">Pentru a lucra acest skill, deschide un PDF generat din biblioteca si foloseste actiunea Study. '
        'Progresul Exam Prep se actualizeaza gradual din Study Mode.</p>'
        '<div class="actions">'
        '<a class="button primary" href="/#library">Continua in Study Mode</a>'
        '<a class="button" href="/exam-prep">Inapoi la Exam Prep</a>'
        '<a class="button" href="/quick-tools">Quick Tools</a>'
        '</div>'
        f'<p class="muted">Skill ID: {safe_id}</p>'
        '</div></main></body></html>'
    )


@app.get("/exam-prep/skill/{skill_id}", response_class=_V46FHTMLResponse)
@app.get("/exam-prep/skill/{skill_id}/", response_class=_V46FHTMLResponse)
async def _v46f_exam_prep_skill_detail_page(skill_id: str):
    try:
        try:
            from services.api.exam_prep import render_exam_prep_skill_detail_page
        except Exception:
            from exam_prep import render_exam_prep_skill_detail_page

        html, status_code = render_exam_prep_skill_detail_page(skill_id)
        if status_code == 200 and html and "Detaliu skill" in html:
            return _V46FHTMLResponse(content=html, status_code=200)
    except Exception:
        pass

    return _V46FHTMLResponse(content=_v46f_fallback_skill_detail_page(skill_id), status_code=200)
# --- end v0.4.6f clean safe Exam Prep skill detail route ---

# --- v0.4.10 Exam Prep dashboard progress summary injection ---
from fastapi.responses import HTMLResponse as _V410HTMLResponse


def _v410_dashboard_summary_html() -> str:
    try:
        from services.api.exam_prep import render_exam_prep_dashboard_progress_summary_html
    except Exception:
        try:
            from exam_prep import render_exam_prep_dashboard_progress_summary_html
        except Exception:
            return ""

    try:
        return render_exam_prep_dashboard_progress_summary_html()
    except Exception:
        return ""


@app.middleware("http")
async def _v410_exam_prep_dashboard_progress_summary(request, call_next):
    response = await call_next(request)

    if request.url.path != "/exam-prep":
        return response

    content_type = response.headers.get("content-type", "")
    if response.status_code != 200 or "text/html" not in content_type:
        return response

    chunks = []
    async for chunk in response.body_iterator:
        if isinstance(chunk, str):
            chunk = chunk.encode("utf-8")
        chunks.append(chunk)

    text = b"".join(chunks).decode("utf-8", errors="replace")

    if "exam-prep-progress-summary-v0410" not in text:
        summary_html = _v410_dashboard_summary_html()

        if summary_html:
            import re

            match = re.search(r"<main[^>]*>", text, flags=re.IGNORECASE)
            if match:
                text = text[: match.end()] + summary_html + text[match.end() :]
            elif "<body>" in text:
                text = text.replace("<body>", "<body>" + summary_html, 1)
            elif "</body>" in text:
                text = text.replace("</body>", summary_html + "</body>", 1)
            else:
                text = summary_html + text

    headers = dict(response.headers)
    headers.pop("content-length", None)
    headers.pop("content-encoding", None)

    return _V410HTMLResponse(
        content=text,
        status_code=response.status_code,
        headers=headers,
    )
# --- end v0.4.10 Exam Prep dashboard progress summary injection ---
