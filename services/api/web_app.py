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
        "in_progress": _ut("in_progress", "În progress"),
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

    # VOILA_OCR_MATH_REPORT_HOOK_GENERATE_V1
    # Owner-local diagnostic hook only. It never rewrites OCR text, course files,
    # Study state, Progress state, build artifacts, ZIPs, releases, or delivery assets.
    try:
        from ocr_math_report_hook import build_ocr_math_report_if_enabled

        build_ocr_math_report_if_enabled(
            output_dir,
            pdf_path.name,
            reason="generate_for_pdf",
        )
    except Exception:
        # Diagnostic hook must never break Generate/Regenerează.
        pass

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
            return _ut("exam_prep.status.in_progress", "În progress")
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
          {_ut("in_progress", "În progress")}: <strong>{len(review)}</strong><br>
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
    {concept_list(_ut("in_progress", "În progress"), review, _ut("no_concepts_in_this_range_yet", "No concepts in this range yet."))}
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
            <summary>Întrebarea sample</summary>
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
  

    /* OCR suggestions panel: static, non-overlapping, below the editor. */
    .ocr-suggestions {{
      position: static !important;
      z-index: auto !important;
      display: block !important;
      width: 100%;
      max-width: none;
      max-height: 260px;
      overflow: auto;
      margin-top: 12px;
      background: #0f1a20;
      border: 1px solid rgba(255,255,255,0.16);
      border-radius: 12px;
      padding: 8px;
      box-shadow: none;
    }}

    .ocr-suggestions::before {{
      content: "Sugestii OCR / corectură";
      display: block;
      margin: 0 0 8px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 900;
      letter-spacing: .08em;
      text-transform: uppercase;
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
      font-weight: 850;
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
          <p class="meta small-tip">Tip: sugestiile apar în panoul de sub editor, fără suprapunere peste text. ↑/↓ navighează · Enter/Tab acceptă · Esc închide · Ctrl+Space afișează sugestii.</p>
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
      const box = getOcrSuggestionBox();

      if (!box || box.hidden) {{
        return;
      }}

      // Suggestions are intentionally kept in document flow below the editor.
      // Do not position them over the textarea/editor.
      box.style.left = "";
      box.style.top = "";
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
        'Deschide un skill pentru descriere, progres și pașii de continuare în Modul Studiu.'
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
        "functii": "Funcții",
        "funcții": "Funcții",
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
        '<p class="muted">Pregătire examene - Bacalaureat - Matematică M1</p>'
        f'<h1>Detaliu skill: {label}</h1>'
        '<p>Skill din planul de pregătire Bacalaureat Matematică M1. '
        'Progresul se actualizeaza pe baza întrebărilor lucrate în Study Mode.</p>'
        '<div class="metric-grid">'
        '<div class="metric"><span>Stare consolidare</span><strong>Nepornit</strong>'
        '<small class="muted">Consolidat după lucru suficient în Study Mode</small></div>'
        '<div class="metric"><span>Scor progres</span><strong>-</strong>'
        '<small class="muted">read-only din Modul Studiu, unde există</small></div>'
        '<div class="metric"><span>Întrebări asociate din Modul Studiu</span><strong>0</strong>'
        '<small class="muted">din quiz.study.json</small></div>'
        '</div>'
        '<p class="muted">Răspunde la întrebări în Modul Studiu, iar progresul se va actualiza aici. '
        '</p>'
        '<div class="actions">'
        '<a class="button primary" href="/#library">Continuă în Modul Studiu</a>'
        '<a class="button" href="/exam-prep">Înapoi la Pregătire examene</a>'
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

# --- v0.4.11 Exam Prep dashboard skill cards injection ---
from fastapi.responses import HTMLResponse as _V411HTMLResponse


def _v411_dashboard_skill_cards_html() -> str:
    try:
        from services.api.exam_prep import render_exam_prep_dashboard_skill_cards_html
    except Exception:
        try:
            from exam_prep import render_exam_prep_dashboard_skill_cards_html
        except Exception:
            return ""

    try:
        return render_exam_prep_dashboard_skill_cards_html()
    except Exception:
        return ""


@app.middleware("http")
async def _v411_exam_prep_dashboard_skill_cards(request, call_next):
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

    if "exam-prep-skill-cards-v0411" not in text:
        cards_html = _v411_dashboard_skill_cards_html()

        if cards_html:
            if "exam-prep-progress-summary-v0410" in text:
                marker = "</section>"
                start = text.find("exam-prep-progress-summary-v0410")
                end = text.find(marker, start)
                if end != -1:
                    end = end + len(marker)
                    text = text[:end] + cards_html + text[end:]
                else:
                    text = cards_html + text
            else:
                import re

                match = re.search(r"<main[^>]*>", text, flags=re.IGNORECASE)
                if match:
                    text = text[: match.end()] + cards_html + text[match.end() :]
                elif "<body>" in text:
                    text = text.replace("<body>", "<body>" + cards_html, 1)
                elif "</body>" in text:
                    text = text.replace("</body>", cards_html + "</body>", 1)
                else:
                    text = cards_html + text

    headers = dict(response.headers)
    headers.pop("content-length", None)
    headers.pop("content-encoding", None)

    return _V411HTMLResponse(
        content=text,
        status_code=response.status_code,
        headers=headers,
    )
# --- end v0.4.11 Exam Prep dashboard skill cards injection ---

# --- v0.4.15 related Modul Studiu questions response guard ---
from fastapi.responses import HTMLResponse as _V415HTMLResponse
from urllib.parse import unquote as _v415_unquote


def _v415_related_questions_html_for_path(path: str) -> str:
    try:
        from services.api.exam_prep import render_exam_prep_related_study_questions_html
    except Exception:
        try:
            from exam_prep import render_exam_prep_related_study_questions_html
        except Exception:
            return ""

    try:
        skill_id = _v415_unquote(path.rstrip("/").rsplit("/", 1)[-1])
        return render_exam_prep_related_study_questions_html(skill_id)
    except Exception:
        return ""


@app.middleware("http")
async def _v415_exam_prep_related_questions_response_guard(request, call_next):
    response = await call_next(request)

    if not request.url.path.startswith("/exam-prep/skill/"):
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

    if "exam-prep-related-study-questions-v0415" not in text:
        section = _v415_related_questions_html_for_path(request.url.path)
        if section:
            if '<div class="actions">' in text:
                text = text.replace('<div class="actions">', section + '<div class="actions">', 1)
            elif "</main>" in text:
                text = text.replace("</main>", section + "</main>", 1)
            elif "</body>" in text:
                text = text.replace("</body>", section + "</body>", 1)
            else:
                text = text + section

    headers = dict(response.headers)
    headers.pop("content-length", None)
    headers.pop("content-encoding", None)

    return _V415HTMLResponse(
        content=text,
        status_code=response.status_code,
        headers=headers,
    )
# --- end v0.4.15 related Modul Studiu questions response guard ---

# --- v0.4.16 next recommended action response guard ---
from fastapi.responses import HTMLResponse as _V416HTMLResponse
from urllib.parse import unquote as _v416_unquote


def _v416_next_action_html_for_path(path: str) -> str:
    try:
        from services.api.exam_prep import render_exam_prep_next_action_html
    except Exception:
        try:
            from exam_prep import render_exam_prep_next_action_html
        except Exception:
            return ""

    try:
        skill_id = _v416_unquote(path.rstrip("/").rsplit("/", 1)[-1])
        return render_exam_prep_next_action_html(skill_id)
    except Exception:
        return ""


@app.middleware("http")
async def _v416_exam_prep_next_action_response_guard(request, call_next):
    response = await call_next(request)

    if not request.url.path.startswith("/exam-prep/skill/"):
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

    if "exam-prep-next-action-v0416" not in text:
        section = _v416_next_action_html_for_path(request.url.path)

        if section:
            if "exam-prep-related-study-questions-v0415" in text:
                marker = "</section>"
                start = text.find("exam-prep-related-study-questions-v0415")
                end = text.find(marker, start)
                if end != -1:
                    end = end + len(marker)
                    text = text[:end] + section + text[end:]
                else:
                    text = text + section
            elif '<div class="actions">' in text:
                text = text.replace('<div class="actions">', section + '<div class="actions">', 1)
            elif "</main>" in text:
                text = text.replace("</main>", section + "</main>", 1)
            elif "</body>" in text:
                text = text.replace("</body>", section + "</body>", 1)
            else:
                text = text + section

    headers = dict(response.headers)
    headers.pop("content-length", None)
    headers.pop("content-encoding", None)

    return _V416HTMLResponse(
        content=text,
        status_code=response.status_code,
        headers=headers,
    )
# --- end v0.4.16 next recommended action response guard ---

# --- v0.4.17 dashboard next action summary injection ---
from fastapi.responses import HTMLResponse as _V417HTMLResponse


def _v417_dashboard_next_action_html() -> str:
    try:
        from services.api.exam_prep import render_exam_prep_dashboard_next_action_html
    except Exception:
        try:
            from exam_prep import render_exam_prep_dashboard_next_action_html
        except Exception:
            return ""

    try:
        return render_exam_prep_dashboard_next_action_html()
    except Exception:
        return ""


@app.middleware("http")
async def _v417_exam_prep_dashboard_next_action(request, call_next):
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

    if "exam-prep-dashboard-next-action-v0417" not in text:
        next_action_html = _v417_dashboard_next_action_html()

        if next_action_html:
            if "exam-prep-progress-summary-v0410" in text:
                text = text.replace(
                    '<section class="exam-prep-progress-summary-v0410"',
                    next_action_html + '<section class="exam-prep-progress-summary-v0410"',
                    1,
                )
            else:
                import re
                match = re.search(r"<main[^>]*>", text, flags=re.IGNORECASE)
                if match:
                    text = text[: match.end()] + next_action_html + text[match.end() :]
                elif "<body>" in text:
                    text = text.replace("<body>", "<body>" + next_action_html, 1)
                else:
                    text = next_action_html + text

    headers = dict(response.headers)
    headers.pop("content-length", None)
    headers.pop("content-encoding", None)

    return _V417HTMLResponse(
        content=text,
        status_code=response.status_code,
        headers=headers,
    )
# --- end v0.4.17 dashboard next action summary injection ---

# --- v0.4.18 Exam Prep dashboard section ordering cleanup ---
from fastapi.responses import HTMLResponse as _V418HTMLResponse


def _v418_extract_section(text: str, marker: str) -> tuple[str, str]:
    marker_index = text.find(marker)
    if marker_index == -1:
        return text, ""

    section_start = text.rfind("<section", 0, marker_index)
    if section_start == -1:
        return text, ""

    section_end = text.find("</section>", marker_index)
    if section_end == -1:
        return text, ""

    section_end += len("</section>")
    section = text[section_start:section_end]
    text = text[:section_start] + text[section_end:]
    return text, section


def _v418_insert_after_main(text: str, html: str) -> str:
    import re

    match = re.search(r"<main[^>]*>", text, flags=re.IGNORECASE)
    if match:
        return text[: match.end()] + html + text[match.end() :]

    if "<body>" in text:
        return text.replace("<body>", "<body>" + html, 1)

    return html + text


def _v418_order_exam_prep_dashboard_sections(text: str) -> str:
    if "exam-prep-dashboard-order-v0418" in text:
        return text

    ordered_markers = [
        "exam-prep-dashboard-next-action-v0417",
        "exam-prep-progress-summary-v0410",
        "exam-prep-skill-cards-v0411",
    ]

    sections = []
    for marker in ordered_markers:
        text, section = _v418_extract_section(text, marker)
        if section:
            sections.append(section)

    if not sections:
        return text

    wrapper = (
        '<div class="exam-prep-dashboard-order-v0418" '
        'style="display:block;margin:0 0 24px;">'
        + "".join(sections)
        + "</div>"
    )

    return _v418_insert_after_main(text, wrapper)


@app.middleware("http")
async def _v418_exam_prep_dashboard_section_ordering(request, call_next):
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
    text = _v418_order_exam_prep_dashboard_sections(text)

    headers = dict(response.headers)
    headers.pop("content-length", None)
    headers.pop("content-encoding", None)

    return _V418HTMLResponse(
        content=text,
        status_code=response.status_code,
        headers=headers,
    )
# --- end v0.4.18 Exam Prep dashboard section ordering cleanup ---

# --- v0.4.19 Exam Prep dashboard visual consistency polish ---
from fastapi.responses import HTMLResponse as _V419HTMLResponse


def _v419_dashboard_visual_css() -> str:
    return (
        '<style id="exam-prep-dashboard-visual-v0419">'
        '.exam-prep-dashboard-order-v0418{display:grid!important;gap:18px!important;margin:0 0 24px!important;}'
        '.exam-prep-dashboard-order-v0418 section{margin:0!important;}'
        '.exam-prep-dashboard-order-v0418 h2{letter-spacing:-0.01em;}'
        '.exam-prep-dashboard-order-v0418 a[href^="/exam-prep/skill/"],'
        '.exam-prep-dashboard-order-v0418 a[href="/exam-prep"],'
        '.exam-prep-dashboard-order-v0418 a[href="/#library"]{text-decoration:none;}'
        '.exam-prep-dashboard-order-v0418 strong{font-weight:750;}'
        '</style>'
    )


def _v419_apply_dashboard_visual_polish(text: str) -> str:
    if "exam-prep-dashboard-visual-v0419" in text:
        return text

    css = _v419_dashboard_visual_css()

    if "</head>" in text:
        return text.replace("</head>", css + "</head>", 1)

    if "<body>" in text:
        return text.replace("<body>", "<body>" + css, 1)

    return css + text


@app.middleware("http")
async def _v419_exam_prep_dashboard_visual_consistency(request, call_next):
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
    text = _v419_apply_dashboard_visual_polish(text)

    headers = dict(response.headers)
    headers.pop("content-length", None)
    headers.pop("content-encoding", None)

    return _V419HTMLResponse(
        content=text,
        status_code=response.status_code,
        headers=headers,
    )
# --- end v0.4.19 Exam Prep dashboard visual consistency polish ---

# --- v0.4.22 consolidated Exam Prep dashboard rendering middleware ---
from fastapi.responses import HTMLResponse as _V422HTMLResponse


def _v422_consolidated_dashboard_sections_html() -> str:
    try:
        from services.api.exam_prep import render_exam_prep_dashboard_sections_html
    except Exception:
        try:
            from exam_prep import render_exam_prep_dashboard_sections_html
        except Exception:
            return ""

    try:
        return render_exam_prep_dashboard_sections_html()
    except Exception:
        return ""


def _v422_extract_existing_section(text: str, marker: str) -> tuple[str, str]:
    marker_index = text.find(marker)
    if marker_index == -1:
        return text, ""

    section_start = text.rfind("<section", 0, marker_index)
    if section_start == -1:
        return text, ""

    section_end = text.find("</section>", marker_index)
    if section_end == -1:
        return text, ""

    section_end += len("</section>")
    section = text[section_start:section_end]
    text = text[:section_start] + text[section_end:]
    return text, section


def _v422_remove_empty_order_wrappers(text: str) -> str:
    # Keep this intentionally conservative. It only removes the exact empty wrapper
    # left after extracting the three legacy sections.
    text = text.replace(
        '<div class="exam-prep-dashboard-order-v0418" style="display:block;margin:0 0 24px;"></div>',
        "",
    )
    text = text.replace(
        '<div class="exam-prep-dashboard-order-v0418" style="display:block;margin:0 0 24px;">\n</div>',
        "",
    )
    return text


def _v422_insert_after_main(text: str, html: str) -> str:
    import re

    match = re.search(r"<main[^>]*>", text, flags=re.IGNORECASE)
    if match:
        return text[: match.end()] + html + text[match.end() :]

    if "<body>" in text:
        return text.replace("<body>", "<body>" + html, 1)

    return html + text


def _v422_apply_dashboard_consolidation(text: str) -> str:
    if "exam-prep-dashboard-consolidated-v0422" in text:
        return text

    consolidated = _v422_consolidated_dashboard_sections_html()
    if not consolidated:
        return text

    for marker in (
        "exam-prep-dashboard-next-action-v0417",
        "exam-prep-progress-summary-v0410",
        "exam-prep-skill-cards-v0411",
    ):
        text, _section = _v422_extract_existing_section(text, marker)

    text = _v422_remove_empty_order_wrappers(text)
    text = _v422_insert_after_main(text, consolidated)

    return text


@app.middleware("http")
async def _v422_exam_prep_dashboard_rendering_consolidation(request, call_next):
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
    text = _v422_apply_dashboard_consolidation(text)
    text = text.replace("Functii", "Funcții").replace("In progres", "În progres")
    text = text.replace("reprezentari", "reprezentări").replace("proprietati", "proprietăți").replace("interpretari", "interpretări")

    headers = dict(response.headers)
    headers.pop("content-length", None)
    headers.pop("content-encoding", None)

    return _V422HTMLResponse(
        content=text,
        status_code=response.status_code,
        headers=headers,
    )
# --- end v0.4.22 consolidated Exam Prep dashboard rendering middleware ---

# --- v0.4.23 consolidated Exam Prep skill detail rendering middleware ---
from fastapi.responses import HTMLResponse as _V423HTMLResponse
from urllib.parse import unquote as _v423_unquote


def _v423_consolidated_skill_detail_sections_html(path: str) -> str:
    try:
        from services.api.exam_prep import render_exam_prep_skill_detail_sections_html
    except Exception:
        try:
            from exam_prep import render_exam_prep_skill_detail_sections_html
        except Exception:
            return ""

    try:
        skill_id = _v423_unquote(path.rstrip("/").rsplit("/", 1)[-1])
        return render_exam_prep_skill_detail_sections_html(skill_id)
    except Exception:
        return ""


def _v423_extract_existing_section(text: str, marker: str) -> tuple[str, str]:
    marker_index = text.find(marker)
    if marker_index == -1:
        return text, ""

    section_start = text.rfind("<section", 0, marker_index)
    if section_start == -1:
        return text, ""

    section_end = text.find("</section>", marker_index)
    if section_end == -1:
        return text, ""

    section_end += len("</section>")
    section = text[section_start:section_end]
    text = text[:section_start] + text[section_end:]
    return text, section


def _v423_insert_before_actions_or_end(text: str, html: str) -> str:
    if '<div class="actions">' in text:
        return text.replace('<div class="actions">', html + '<div class="actions">', 1)

    if "</main>" in text:
        return text.replace("</main>", html + "</main>", 1)

    if "</body>" in text:
        return text.replace("</body>", html + "</body>", 1)

    return text + html


def _v423_polish_skill_detail_response(text: str) -> str:
    replacements = [
        ("Functii", "Funcții"),
        ("In progres", "În progres"),
        ("Pregatire examene", "Pregătire examene"),
        ("Matematica M1", "Matematică M1"),
        ("Intrebari", "Întrebări"),
        ("Continua", "Continuă"),
        ("Inapoi", "Înapoi"),
        ("Întrebări Study legate", "Întrebări asociate din Modul Studiu"),
        ("Continuă în Study Mode", "Continuă în Modul Studiu"),
        ("Înapoi la Exam Prep", "Înapoi la Pregătire examene"),
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    return text


def _v423_apply_skill_detail_consolidation(path: str, text: str) -> str:
    if "exam-prep-skill-detail-consolidated-v0423" in text:
        return _v423_polish_skill_detail_response(text)

    consolidated = _v423_consolidated_skill_detail_sections_html(path)
    if not consolidated:
        return _v423_polish_skill_detail_response(text)

    for marker in (
        "exam-prep-related-study-questions-v0415",
        "exam-prep-next-action-v0416",
    ):
        text, _section = _v423_extract_existing_section(text, marker)

    text = _v423_insert_before_actions_or_end(text, consolidated)
    text = _v423_polish_skill_detail_response(text)

    return text


@app.middleware("http")
async def _v423_exam_prep_skill_detail_rendering_consolidation(request, call_next):
    response = await call_next(request)

    if not request.url.path.startswith("/exam-prep/skill/"):
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
    text = _v423_apply_skill_detail_consolidation(request.url.path, text)

    headers = dict(response.headers)
    headers.pop("content-length", None)
    headers.pop("content-encoding", None)

    return _V423HTMLResponse(
        content=text,
        status_code=response.status_code,
        headers=headers,
    )
# --- end v0.4.23 consolidated Exam Prep skill detail rendering middleware ---

# v0.4.50-local-bank-protected-preview-route
@app.get("/exam-prep/local-bank-study-preview")
def exam_prep_local_bank_study_preview_route(
    root: str = "",
    course_id: str = "",
    skill_id: str = "",
    limit: int = 5,
) -> dict:
    """Internal read-only local bank study preview route.

    Disabled by default. Enable only for local diagnostics with:
    VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_PREVIEW_ROUTE=1

    This route does not save attempts, score answers, update progress,
    replace live study sessions, or change weak review behavior.
    """

    import os

    enabled = os.environ.get(
        "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_PREVIEW_ROUTE",
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}

    if not enabled:
        return {
            "status": "disabled",
            "route_version": "v0.4.50",
            "mode": "protected_read_only_route",
            "message": "Local bank study preview route is disabled by default.",
            "enable_with": "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_PREVIEW_ROUTE=1",
            "will_save_attempt": False,
            "will_update_progress": False,
            "will_score_answer": False,
            "will_replace_live_study_session": False,
            "requires_cloud_or_api": False,
        }

    if not root:
        return {
            "status": "error",
            "route_version": "v0.4.50",
            "error": "Missing required root query parameter.",
            "will_save_attempt": False,
            "will_update_progress": False,
            "will_score_answer": False,
        }

    from exam_prep_local_bank_study_preview import (
        build_local_bank_read_only_study_preview,
    )

    preview = build_local_bank_read_only_study_preview(
        root,
        course_id=course_id or None,
        skill_id=skill_id or None,
        limit=limit or None,
    )

    return {
        "status": "ok",
        "route_version": "v0.4.50",
        "mode": "protected_read_only_route",
        "preview": preview,
        "will_save_attempt": False,
        "will_update_progress": False,
        "will_score_answer": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
    }

# v0.4.51-local-bank-preview-internal-panel
@app.get("/exam-prep/local-bank-study-preview/panel")
def exam_prep_local_bank_study_preview_internal_panel(
    course_id: str = "v051-panel",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
) -> dict:
    """Internal JSON-only read-only panel model for local bank study preview.

    Disabled by default. Enable only for local diagnostics with:
    VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_PREVIEW_ROUTE=1

    This route intentionally does not accept a filesystem root from the user.
    It generates a temporary local sample internally, then previews that sample.
    It does not render HTML, save attempts, score answers, update progress,
    replace live study sessions, or change weak review behavior.
    """

    import os
    import tempfile

    enabled = os.environ.get(
        "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_PREVIEW_ROUTE",
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}

    base = {
        "route_version": "v0.4.51",
        "mode": "protected_json_panel",
        "panel_kind": "internal_diagnostics_json",
        "path_policy": "no_user_provided_filesystem_root",
        "has_public_ui_link": False,
        "will_save_attempt": False,
        "will_update_progress": False,
        "will_score_answer": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
    }

    if not enabled:
        return {
            **base,
            "status": "disabled",
            "message": "Local bank study preview panel is disabled by default.",
            "enable_with": "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_PREVIEW_ROUTE=1",
            "preview": None,
        }

    sample_text = (
        "Funcțiile sunt relații matematice între două mulțimi. "
        "O funcție este definită prin domeniu, codomeniu și lege de corespondență. "
        "Derivata descrie variația locală a unei funcții. "
        "Apoi se poate studia monotonia și se pot identifica punctele critice. "
        "Formula f'(x)=lim h->0 (f(x+h)-f(x))/h este folosită pentru calculul derivatei."
    )

    safe_course_id = course_id or "v051-panel"
    safe_skill_id = skill_id or "local_concept_001_functiile"

    from exam_prep_local_bank_study_preview import (
        build_local_bank_read_only_study_preview,
    )
    from local_pedagogy_engine import generate_local_pedagogy_bundle

    with tempfile.TemporaryDirectory(prefix="voila-local-bank-panel-") as tmp_root:
        generate_local_pedagogy_bundle(
            sample_text,
            tmp_root,
            course_id=safe_course_id,
            source_path="internal_v051_sample",
            language="ro",
        )

        preview = build_local_bank_read_only_study_preview(
            tmp_root,
            course_id=safe_course_id,
            skill_id=safe_skill_id,
            limit=limit or None,
        )

    return {
        **base,
        "status": "ok",
        "preview": preview,
    }

# v0.4.64-guarded-live-trial-route-smoke
@app.get("/exam-prep/local-bank/guarded-trial-smoke")
def exam_prep_local_bank_guarded_trial_smoke(
    course_id: str = "v064-route",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
) -> dict:
    """Internal JSON-only smoke route for the guarded local-bank trial hook.

    Disabled by default. Enable locally with:
    VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_SMOKE_ROUTE=1

    This route intentionally does not accept a filesystem root. It does not
    consume local-bank questions live, persist attempts/sessions/progress,
    score live sessions, or modify the Exam Prep UI.
    """

    import os

    smoke_enabled = os.environ.get(
        "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_SMOKE_ROUTE",
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}

    base = {
        "schema_version": "1",
        "route_version": "v0.4.64",
        "mode": "guarded_trial_smoke_route",
        "route_path": "/exam-prep/local-bank/guarded-trial-smoke",
        "route_enabled": smoke_enabled,
        "route_kind": "internal_json_only",
        "has_public_ui_link": False,
        "path_policy": "no_user_provided_filesystem_root",
        "will_consume_local_bank_live": False,
        "will_start_live_session": False,
        "will_replace_effective_source": False,
        "will_persist_progress": False,
        "will_persist_session": False,
        "will_persist_attempts": False,
        "will_update_progress": False,
        "will_score_live_session": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
    }

    if not smoke_enabled:
        return {
            **base,
            "status": "disabled",
            "message": "Guarded local-bank trial smoke route is disabled by default.",
            "enable_with": "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_SMOKE_ROUTE=1",
            "hook": None,
        }

    from exam_prep_local_bank_noop_study_session_hook import (
        build_noop_study_session_hook,
    )

    safe_limit = max(1, min(int(limit or 5), 20))
    hook = build_noop_study_session_hook(
        course_id=course_id or "v064-route",
        skill_id=skill_id or "local_concept_001_functiile",
        limit=safe_limit,
    )

    return {
        **base,
        "status": "ok",
        "hook_status": hook.get("hook_status"),
        "effective_source": hook.get("effective_source"),
        "reported_candidate_available": hook.get("reported_candidate_available"),
        "hook": hook,
    }

# v0.4.65-guarded-trial-route-diagnostics-report
@app.get("/exam-prep/local-bank/guarded-trial-diagnostics")
def exam_prep_local_bank_guarded_trial_diagnostics(
    course_id: str = "v065-route",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
) -> dict:
    """Internal JSON-only diagnostics report for guarded local-bank trial.

    Disabled by default. Enable locally with:
    VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE=1

    This route intentionally does not accept a filesystem root. It does not
    consume local-bank questions live, persist attempts/sessions/progress,
    score live sessions, or modify the Exam Prep UI.
    """

    import os

    diagnostics_enabled = os.environ.get(
        "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE",
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}

    base = {
        "schema_version": "1",
        "diagnostics_route_version": "v0.4.65",
        "mode": "guarded_trial_diagnostics_report",
        "route_path": "/exam-prep/local-bank/guarded-trial-diagnostics",
        "route_enabled": diagnostics_enabled,
        "route_kind": "internal_json_only",
        "has_public_ui_link": False,
        "path_policy": "no_user_provided_filesystem_root",
        "will_consume_local_bank_live": False,
        "will_start_live_session": False,
        "will_replace_effective_source": False,
        "will_persist_progress": False,
        "will_persist_session": False,
        "will_persist_attempts": False,
        "will_update_progress": False,
        "will_score_live_session": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
    }

    if not diagnostics_enabled:
        return {
            **base,
            "status": "disabled",
            "diagnostics_status": "disabled",
            "message": "Guarded local-bank trial diagnostics route is disabled by default.",
            "enable_with": "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE=1",
            "summary": None,
        }

    from exam_prep_local_bank_noop_study_session_hook import (
        build_noop_study_session_hook,
    )

    safe_limit = max(1, min(int(limit or 5), 20))
    hook = build_noop_study_session_hook(
        course_id=course_id or "v065-route",
        skill_id=skill_id or "local_concept_001_functiile",
        limit=safe_limit,
    )

    boundary = hook.get("adapter_boundary") or {}
    trial = boundary.get("guarded_live_trial") or {}
    readiness = trial.get("readiness_report") or {}

    safety_flags = {
        "will_consume_local_bank_live": False,
        "will_start_live_session": False,
        "will_replace_effective_source": False,
        "will_persist_progress": False,
        "will_persist_session": False,
        "will_persist_attempts": False,
        "will_update_progress": False,
        "will_score_live_session": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
    }

    safety_ok = all(value is False for value in safety_flags.values())

    summary = {
        "diagnostics_status": "ok" if safety_ok else "needs_review",
        "hook_status": hook.get("hook_status"),
        "boundary_status": boundary.get("boundary_status"),
        "readiness_status": readiness.get("readiness_status"),
        "candidate_available": hook.get("reported_candidate_available"),
        "effective_source": hook.get("effective_source"),
        "fallback_source": boundary.get("fallback_source", "legacy_fallback"),
        "safety_ok": safety_ok,
        "safety_flags": safety_flags,
        "versions": {
            "noop_hook_version": hook.get("noop_hook_version"),
            "adapter_boundary_version": boundary.get("adapter_boundary_version"),
            "guarded_trial_version": trial.get("guarded_trial_version"),
            "readiness_report_version": readiness.get("readiness_report_version"),
        },
    }

    return {
        **base,
        "status": "ok",
        "diagnostics_status": summary["diagnostics_status"],
        "summary": summary,
        "hook": hook,
    }

# v0.4.66-guarded-trial-candidate-question-preview-route
@app.get("/exam-prep/local-bank/guarded-trial-candidates")
def exam_prep_local_bank_guarded_trial_candidates(
    course_id: str = "v066-route",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
) -> dict:
    """Internal JSON-only candidate question preview for guarded local-bank trial.

    Disabled by default. Enable locally with:
    VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE=1

    For candidate availability, this route also expects the diagnostics route flag
    and guarded live-trial flag to be enabled. It intentionally does not accept a
    filesystem root and does not expose answer previews.
    """

    import os

    candidates_enabled = os.environ.get(
        "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE",
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}
    diagnostics_enabled = os.environ.get(
        "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE",
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}

    base = {
        "schema_version": "1",
        "candidate_route_version": "v0.4.66",
        "mode": "guarded_trial_candidate_question_preview",
        "route_path": "/exam-prep/local-bank/guarded-trial-candidates",
        "route_enabled": candidates_enabled,
        "diagnostics_route_flag_enabled": diagnostics_enabled,
        "route_kind": "internal_json_only",
        "has_public_ui_link": False,
        "answers_exposed": False,
        "explanations_exposed": False,
        "path_policy": "no_user_provided_filesystem_root",
        "will_consume_local_bank_live": False,
        "will_start_live_session": False,
        "will_replace_effective_source": False,
        "will_persist_progress": False,
        "will_persist_session": False,
        "will_persist_attempts": False,
        "will_update_progress": False,
        "will_score_live_session": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
    }

    if not candidates_enabled:
        return {
            **base,
            "status": "disabled",
            "candidate_status": "disabled",
            "message": "Guarded local-bank trial candidate route is disabled by default.",
            "enable_with": "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE=1",
            "candidate_questions": [],
        }

    if not diagnostics_enabled:
        return {
            **base,
            "status": "blocked",
            "candidate_status": "diagnostics_route_flag_required",
            "message": "Candidate preview requires diagnostics route flag for the guarded trial chain.",
            "enable_with": "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE=1",
            "candidate_questions": [],
        }

    from exam_prep_local_bank_noop_study_session_hook import (
        build_noop_study_session_hook,
    )

    safe_limit = max(1, min(int(limit or 5), 20))
    hook = build_noop_study_session_hook(
        course_id=course_id or "v066-route",
        skill_id=skill_id or "local_concept_001_functiile",
        limit=safe_limit,
    )

    boundary = hook.get("adapter_boundary") or {}
    trial = boundary.get("guarded_live_trial") or {}
    readiness = trial.get("readiness_report") or {}
    snapshots = readiness.get("snapshots") or {}
    source_selection = snapshots.get("source_selection") or {}
    dry_run_items = source_selection.get("dry_run_items") or []

    candidate_questions = []
    for index, item in enumerate(dry_run_items[:safe_limit], start=1):
        if not isinstance(item, dict):
            continue
        candidate_questions.append(
            {
                "candidate_index": index,
                "dry_run_item_id": item.get("dry_run_item_id", ""),
                "question_id": item.get("question_id", ""),
                "course_id": item.get("course_id", course_id),
                "skill_id": item.get("skill_id", skill_id),
                "question_type": item.get("question_type", ""),
                "difficulty": item.get("difficulty", ""),
                "question": item.get("question", ""),
                "choices": item.get("choices", []),
                "source": item.get("source", "local_exercise_bank_adapter"),
                "answer_preview_hidden": True,
                "explanation_preview_hidden": True,
                "dry_run_only": True,
                "will_save_attempt": False,
                "will_update_progress": False,
                "will_score_answer": False,
            }
        )

    safety_flags = {
        "will_consume_local_bank_live": False,
        "will_start_live_session": False,
        "will_replace_effective_source": False,
        "will_persist_progress": False,
        "will_persist_session": False,
        "will_persist_attempts": False,
        "will_update_progress": False,
        "will_score_live_session": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
    }

    safety_ok = all(value is False for value in safety_flags.values())

    return {
        **base,
        "status": "ok",
        "candidate_status": "candidate_questions_preview_ready",
        "hook_status": hook.get("hook_status"),
        "boundary_status": boundary.get("boundary_status"),
        "readiness_status": readiness.get("readiness_status"),
        "effective_source": hook.get("effective_source"),
        "reported_candidate_available": hook.get("reported_candidate_available"),
        "candidate_question_count": len(candidate_questions),
        "candidate_questions": candidate_questions,
        "safety_ok": safety_ok,
        "safety_flags": safety_flags,
        "versions": {
            "noop_hook_version": hook.get("noop_hook_version"),
            "adapter_boundary_version": boundary.get("adapter_boundary_version"),
            "guarded_trial_version": trial.get("guarded_trial_version"),
            "readiness_report_version": readiness.get("readiness_report_version"),
        },
    }

# v0.4.67-guarded-trial-candidate-preview-internal-panel
@app.get("/exam-prep/local-bank/guarded-trial-candidates-panel")
def exam_prep_local_bank_guarded_trial_candidates_panel(
    course_id: str = "v067-panel",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 5,
):
    """Hidden/internal preview panel for guarded local-bank candidate questions.

    Disabled by default. Enable locally with:
    VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL=1

    The panel reads the v0.4.66 JSON candidate route from the browser. It does
    not expose answers, consume local-bank questions live, persist data, score
    sessions, or modify the Exam Prep UI navigation.
    """

    import html
    import os
    from fastapi.responses import HTMLResponse

    panel_enabled = os.environ.get(
        "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL",
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}

    safe_course = html.escape(course_id or "v067-panel", quote=True)
    safe_skill = html.escape(skill_id or "local_concept_001_functiile", quote=True)
    safe_limit = max(1, min(int(limit or 5), 20))

    if not panel_enabled:
        disabled_html = f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex,nofollow">
  <title>Local-bank candidate preview disabled</title>
</head>
<body data-panel-version="v0.4.67" data-panel-status="disabled">
  <main>
    <h1>Guarded local-bank candidate preview</h1>
    <p id="candidate-panel-status">disabled</p>
    <p>This hidden/internal panel is disabled by default.</p>
    <p>Enable locally with <code>VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL=1</code>.</p>
    <ul>
      <li>Effective source remains legacy_fallback.</li>
      <li>No live local-bank consumption.</li>
      <li>No attempts, progress, session persistence, or live scoring.</li>
      <li>No answers or explanations are exposed by this panel.</li>
    </ul>
  </main>
</body>
</html>
"""
        return HTMLResponse(content=disabled_html)

    candidates_url = (
        "/exam-prep/local-bank/guarded-trial-candidates"
        f"?course_id={safe_course}&skill_id={safe_skill}&limit={safe_limit}"
    )

    panel_html = f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex,nofollow">
  <title>Guarded local-bank candidate preview</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, sans-serif; margin: 2rem; line-height: 1.45; }}
    main {{ max-width: 960px; margin: 0 auto; }}
    .badge {{ display: inline-block; padding: .2rem .5rem; border: 1px solid #999; border-radius: 999px; margin-right: .4rem; font-size: .85rem; }}
    .question-card {{ border: 1px solid #ddd; border-radius: .75rem; padding: 1rem; margin: 1rem 0; }}
    .muted {{ color: #555; }}
    code {{ background: #f5f5f5; padding: .1rem .25rem; border-radius: .25rem; }}
  </style>
</head>
<body
  data-panel-version="v0.4.67"
  data-panel-status="enabled"
  data-route-kind="internal_hidden_panel"
  data-has-public-ui-link="false"
  data-effective-source="legacy_fallback"
  data-will-consume-local-bank-live="false"
  data-will-persist-attempts="false"
  data-will-update-progress="false"
>
  <main>
    <h1>Guarded local-bank candidate preview</h1>
    <p id="candidate-panel-status">loading</p>
    <p class="muted">
      Internal hidden panel. Preview-only. Effective source remains <code>legacy_fallback</code>.
      Correct answers and explanations are intentionally not rendered.
    </p>

    <section aria-labelledby="safety-title">
      <h2 id="safety-title">Safety guardrails</h2>
      <ul>
        <li>No live local-bank consumption.</li>
        <li>No live session start.</li>
        <li>No effective source replacement.</li>
        <li>No attempt, progress, or session persistence.</li>
        <li>No live scoring and no Exam Prep UI navigation change.</li>
      </ul>
    </section>

    <section aria-labelledby="candidate-title">
      <h2 id="candidate-title">Candidate questions</h2>
      <div id="candidate-summary" class="muted"></div>
      <div id="candidate-list"></div>
    </section>
  </main>

  <script>
    const candidateUrl = "{candidates_url}";
    const statusEl = document.getElementById("candidate-panel-status");
    const summaryEl = document.getElementById("candidate-summary");
    const listEl = document.getElementById("candidate-list");

    function text(value) {{
      return value === undefined || value === null ? "" : String(value);
    }}

    function renderChoiceList(choices) {{
      if (!Array.isArray(choices) || choices.length === 0) return "";
      const items = choices.map((choice) => `<li>${{text(choice)}}</li>`).join("");
      return `<ol>${{items}}</ol>`;
    }}

    function renderQuestion(item) {{
      const type = text(item.question_type);
      const difficulty = text(item.difficulty);
      const skill = text(item.skill_id);
      const question = text(item.question);
      const choices = renderChoiceList(item.choices);
      return `
        <article class="question-card">
          <div>
            <span class="badge">${{type}}</span>
            <span class="badge">${{difficulty}}</span>
            <span class="badge">${{skill}}</span>
          </div>
          <h3>Întrebarea ${{text(item.candidate_index)}}</h3>
          <p>${{question}}</p>
          ${{choices}}
          <p class="muted">Answers hidden: ${{text(item.answer_preview_hidden)}} · Explanations hidden: ${{text(item.explanation_preview_hidden)}}</p>
        </article>
      `;
    }}

    fetch(candidateUrl, {{ headers: {{ "accept": "application/json" }} }})
      .then((response) => response.json())
      .then((data) => {{
        statusEl.textContent = data.status || "unknown";
        summaryEl.textContent = `candidate_status=${{data.candidate_status || "unknown"}}; effective_source=${{data.effective_source || "legacy_fallback"}}; count=${{data.candidate_question_count || 0}}`;
        const questions = Array.isArray(data.candidate_questions) ? data.candidate_questions : [];
        listEl.innerHTML = questions.map(renderQuestion).join("") || "<p>No candidate questions available.</p>";
      }})
      .catch((error) => {{
        statusEl.textContent = "error";
        summaryEl.textContent = text(error);
      }});
  </script>
</body>
</html>
"""
    return HTMLResponse(content=panel_html)

# v0.4.68-guarded-trial-candidate-panel-polish-owner-smoke
@app.get("/exam-prep/local-bank/guarded-trial-candidates-panel-polish")
def exam_prep_local_bank_guarded_trial_candidates_panel_polish():
    """Hidden/internal polished owner-smoke panel for guarded local-bank candidates."""

    import os
    from fastapi.responses import HTMLResponse

    panel_enabled = os.environ.get(
        "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL_POLISH",
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}


    if not panel_enabled:
        disabled_html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex,nofollow">
  <title>Guarded candidate panel polish disabled</title>
</head>
<body
  data-panel-polish-version="v0.4.68"
  data-panel-polish-status="disabled"
  data-route-kind="internal_hidden_owner_smoke_panel"
  data-has-public-ui-link="false"
  data-effective-source="legacy_fallback"
  data-will-consume-local-bank-live="false"
  data-will-persist-attempts="false"
  data-will-update-progress="false"
>
  <main>
    <h1>Guarded candidate preview panel polish</h1>
    <p id="candidate-panel-polish-status">disabled</p>
    <p>This hidden/internal owner-smoke panel is disabled by default.</p>
    <p>Enable locally with <code>VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL_POLISH=1</code>.</p>
    <ul>
      <li>Effective source remains legacy_fallback.</li>
      <li>No live local-bank consumption.</li>
      <li>No attempts, progress, session persistence, or live scoring.</li>
      <li>No answers or explanations are exposed by this panel.</li>
    </ul>
  </main>
</body>
</html>
"""
        return HTMLResponse(content=disabled_html)

    candidates_url_json = '"/exam-prep/local-bank/guarded-trial-candidates?course_id=v068-panel&skill_id=local_concept_001_functiile&limit=5"'

    panel_html = f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex,nofollow">
  <title>Guarded candidate preview owner smoke</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, sans-serif; margin: 0; line-height: 1.45; }}
    main {{ max-width: 1080px; margin: 0 auto; padding: 2rem; }}
    header {{ border-bottom: 1px solid #ddd; margin-bottom: 1.25rem; padding-bottom: 1rem; }}
    .muted {{ opacity: .72; }}
    .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: .75rem; margin: 1rem 0; }}
    .summary-card {{ border: 1px solid #ddd; border-radius: .9rem; padding: .85rem; }}
    .summary-card strong {{ display: block; font-size: .8rem; text-transform: uppercase; letter-spacing: .05em; opacity: .7; }}
    .summary-card span {{ display: block; font-size: 1.05rem; margin-top: .25rem; }}
    .badge-row {{ display: flex; flex-wrap: wrap; gap: .4rem; margin: .65rem 0; }}
    .badge {{ display: inline-flex; align-items: center; border: 1px solid #bbb; border-radius: 999px; padding: .2rem .55rem; font-size: .82rem; }}
    .question-card {{ border: 1px solid #ddd; border-radius: 1rem; padding: 1rem; margin: 1rem 0; }}
    .safety {{ border-left: .25rem solid #999; padding-left: .85rem; margin: 1rem 0; }}
    code {{ background: #f5f5f5; padding: .1rem .25rem; border-radius: .25rem; }}
  </style>
</head>
<body
  data-panel-polish-version="v0.4.68"
  data-panel-polish-status="enabled"
  data-route-kind="internal_hidden_owner_smoke_panel"
  data-has-public-ui-link="false"
  data-effective-source="legacy_fallback"
  data-will-consume-local-bank-live="false"
  data-will-start-live-session="false"
  data-will-replace-effective-source="false"
  data-will-persist-attempts="false"
  data-will-update-progress="false"
  data-will-score-live-session="false"
>
  <main>
    <header>
      <h1>Guarded candidate preview owner smoke</h1>
      <p class="muted">Hidden/internal panel. Preview-only. Effective source remains <code>legacy_fallback</code>.</p>
      <p id="candidate-panel-polish-status">loading</p>
    </header>

    <section aria-labelledby="summary-title">
      <h2 id="summary-title">Compact summary</h2>
      <div class="summary-grid">
        <div class="summary-card"><strong>Status</strong><span id="summary-status">loading</span></div>
        <div class="summary-card"><strong>Count</strong><span id="summary-count">0</span></div>
        <div class="summary-card"><strong>Source</strong><span id="summary-source">legacy_fallback</span></div>
        <div class="summary-card"><strong>Safety</strong><span id="summary-safety">pending</span></div>
      </div>
    </section>

    <section class="safety" aria-labelledby="safety-title">
      <h2 id="safety-title">Safety guardrails</h2>
      <ul>
        <li>No live local-bank consumption.</li>
        <li>No live session start.</li>
        <li>No effective source replacement.</li>
        <li>No attempt, progress, or session persistence.</li>
        <li>No live scoring and no public Exam Prep navigation change.</li>
      </ul>
    </section>

    <section aria-labelledby="candidate-title">
      <h2 id="candidate-title">Candidate questions</h2>
      <p class="muted" id="candidate-subtitle">Waiting for candidate route...</p>
      <div id="candidate-list"></div>
    </section>
  </main>

  <script>
    const candidateUrl = {candidates_url_json};
    const statusEl = document.getElementById("candidate-panel-polish-status");
    const summaryStatusEl = document.getElementById("summary-status");
    const summaryCountEl = document.getElementById("summary-count");
    const summarySourceEl = document.getElementById("summary-source");
    const summarySafetyEl = document.getElementById("summary-safety");
    const subtitleEl = document.getElementById("candidate-subtitle");
    const listEl = document.getElementById("candidate-list");

    function text(value) {{
      return value === undefined || value === null ? "" : String(value);
    }}

    function appendText(parent, tagName, value, className) {{
      const el = document.createElement(tagName);
      if (className) el.className = className;
      el.textContent = text(value);
      parent.appendChild(el);
      return el;
    }}

    function appendBadge(parent, value) {{
      appendText(parent, "span", value, "badge");
    }}

    function renderQuestion(item) {{
      const article = document.createElement("article");
      article.className = "question-card";

      const badges = document.createElement("div");
      badges.className = "badge-row";
      appendBadge(badges, text(item.question_type) || "unknown_type");
      appendBadge(badges, text(item.difficulty) || "unknown_difficulty");
      appendBadge(badges, text(item.skill_id) || "unknown_skill");
      appendBadge(badges, "answers hidden");
      appendBadge(badges, "explanations hidden");
      article.appendChild(badges);

      appendText(article, "h3", "Întrebarea " + text(item.candidate_index));
      appendText(article, "p", item.question || "");

      const choices = Array.isArray(item.choices) ? item.choices : [];
      if (choices.length > 0) {{
        const ol = document.createElement("ol");
        choices.forEach((choice) => appendText(ol, "li", choice));
        article.appendChild(ol);
      }}

      appendText(article, "p", "Preview-safe payload rendered without solution fields.", "muted");
      return article;
    }}

    fetch(candidateUrl, {{ headers: {{ "accept": "application/json" }} }})
      .then((response) => response.json())
      .then((data) => {{
        const questions = Array.isArray(data.candidate_questions) ? data.candidate_questions : [];
        statusEl.textContent = data.status || "unknown";
        summaryStatusEl.textContent = data.candidate_status || data.status || "unknown";
        summaryCountEl.textContent = String(data.candidate_question_count || questions.length || 0);
        summarySourceEl.textContent = data.effective_source || "legacy_fallback";
        summarySafetyEl.textContent = data.safety_ok === true ? "safety_ok" : "needs_review";
        subtitleEl.textContent = "Rendered from preview-safe candidate route.";

        listEl.replaceChildren();
        if (questions.length === 0) {{
          appendText(listEl, "p", "No candidate questions available.", "muted");
          return;
        }}
        questions.forEach((item) => listEl.appendChild(renderQuestion(item)));
      }})
      .catch((error) => {{
        statusEl.textContent = "error";
        summaryStatusEl.textContent = "error";
        subtitleEl.textContent = text(error);
      }});
  </script>
</body>
</html>
"""
    return HTMLResponse(content=panel_html)

# v0.4.73-guarded-live-consumption-shadow-route-report
@app.get("/exam-prep/local-bank/live-consumption-shadow-report")
def exam_prep_local_bank_live_consumption_shadow_report() -> dict:
    """Internal JSON-only sanitized report for guarded local-bank shadow selector.

    Disabled by default. Enable locally with:
    VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_ROUTE=1

    The route intentionally uses fixed owner-smoke inputs and does not accept
    user-provided filesystem roots or query parameters. It returns a compact
    sanitized report and does not include raw snapshots, answers, explanations,
    correct_answer_preview, or explanation_preview fields.
    """

    import os

    route_enabled = os.environ.get(
        "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_ROUTE",
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}

    base = {
        "schema_version": "1",
        "shadow_report_route_version": "v0.4.73",
        "mode": "guarded_live_consumption_shadow_route_report",
        "route_path": "/exam-prep/local-bank/live-consumption-shadow-report",
        "route_enabled": route_enabled,
        "route_kind": "internal_json_only",
        "has_public_ui_link": False,
        "report_sanitized": True,
        "raw_snapshots_included": False,
        "answers_exposed": False,
        "explanations_exposed": False,
        "path_policy": "no_user_provided_filesystem_root",
        "will_consume_local_bank_live": False,
        "will_deliver_shadow_questions_live": False,
        "will_start_live_session": False,
        "will_replace_effective_source": False,
        "will_persist_progress": False,
        "will_persist_session": False,
        "will_persist_attempts": False,
        "will_update_progress": False,
        "will_score_live_session": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
    }

    if not route_enabled:
        return {
            **base,
            "status": "disabled",
            "selector_status": "disabled",
            "message": "Guarded local-bank shadow report route is disabled by default.",
            "enable_with": "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_ROUTE=1",
            "effective_source": "legacy_fallback",
            "shadow_source": "",
            "coverage_comparison": {},
            "selected_shadow_questions": [],
        }

    from exam_prep_local_bank_live_consumption_shadow_selector import (
        build_shadow_source_selector,
    )

    selector = build_shadow_source_selector(
        course_id="v073-route",
        skill_id="local_concept_001_functiile",
        limit=5,
    )
    shadow_report = selector.get("shadow_selection_report") or {}
    coverage = shadow_report.get("coverage_comparison") or {}
    local_profile = shadow_report.get("local_candidate_profile") or {}
    selected = shadow_report.get("selected_shadow_questions") or []

    safe_questions = []
    for item in selected:
        if not isinstance(item, dict):
            continue
        safe_questions.append(
            {
                "shadow_index": item.get("shadow_index"),
                "question_id": item.get("question_id", ""),
                "skill_id": item.get("skill_id", ""),
                "question_type": item.get("question_type", ""),
                "difficulty": item.get("difficulty", ""),
                "source": item.get("source", "local_exercise_bank_adapter"),
                "dry_run_only": True,
                "will_deliver_live": False,
                "will_save_attempt": False,
                "will_update_progress": False,
                "will_score_answer": False,
            }
        )

    return {
        **base,
        "status": "ok",
        "selector_status": selector.get("selector_status"),
        "adapter_boundary_status": selector.get("adapter_boundary_status"),
        "effective_source": "legacy_fallback",
        "shadow_source": selector.get("shadow_source", ""),
        "shadow_candidate_count": shadow_report.get("shadow_candidate_count", 0),
        "coverage_comparison": {
            "compared_against_legacy_live_output": False,
            "local_question_type_diversity": coverage.get("local_question_type_diversity", 0),
            "local_difficulty_diversity": coverage.get("local_difficulty_diversity", 0),
            "local_skill_diversity": coverage.get("local_skill_diversity", 0),
        },
        "local_candidate_profile": {
            "source": "local_exercise_bank_adapter",
            "available": local_profile.get("available", False),
            "question_count": local_profile.get("question_count", 0),
            "question_type_counts": local_profile.get("question_type_counts", {}),
            "difficulty_counts": local_profile.get("difficulty_counts", {}),
            "skill_counts": local_profile.get("skill_counts", {}),
        },
        "selected_shadow_questions": safe_questions,
        "explicit_not_live_yet": [
            "shadow report route does not change effective_source",
            "local-bank questions are not delivered live",
            "live study sessions are not started",
            "effective_source remains legacy_fallback",
            "attempts are not persisted",
            "progress is not updated",
            "sessions are not persisted",
            "live scoring is not enabled",
            "public Exam Prep navigation is not changed",
        ],
    }

# v0.4.74-guarded-live-consumption-shadow-route-owner-panel
@app.get("/exam-prep/local-bank/live-consumption-shadow-panel")
def exam_prep_local_bank_live_consumption_shadow_panel():
    """Hidden/internal owner panel for the guarded local-bank shadow report.

    Disabled by default. Enable locally with:
    VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_OWNER_PANEL=1

    The panel reads the v0.4.73 sanitized JSON report route from the browser. It
    uses safe DOM rendering, does not accept query parameters, does not expose
    answers/explanations/raw snapshots, and does not consume local-bank questions
    live.
    """

    import os
    from fastapi.responses import HTMLResponse

    panel_enabled = os.environ.get(
        "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_OWNER_PANEL",
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}

    if not panel_enabled:
        disabled_html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex,nofollow">
  <title>Shadow owner panel disabled</title>
</head>
<body
  data-shadow-owner-panel-version="v0.4.74"
  data-shadow-owner-panel-status="disabled"
  data-route-kind="internal_hidden_owner_panel"
  data-has-public-ui-link="false"
  data-effective-source="legacy_fallback"
  data-will-consume-local-bank-live="false"
  data-will-deliver-shadow-questions-live="false"
  data-will-persist-attempts="false"
  data-will-update-progress="false"
>
  <main>
    <h1>Guarded live-consumption shadow owner panel</h1>
    <p id="shadow-owner-panel-status">disabled</p>
    <p>This hidden/internal owner panel is disabled by default.</p>
    <p>Enable locally with <code>VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_OWNER_PANEL=1</code>.</p>
    <ul>
      <li>Effective source remains legacy_fallback.</li>
      <li>No local-bank questions are delivered live.</li>
      <li>No attempts, progress, session persistence, or live scoring.</li>
      <li>No answers, explanations, or raw snapshots are exposed by this panel.</li>
    </ul>
  </main>
</body>
</html>
"""
        return HTMLResponse(content=disabled_html)

    panel_html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex,nofollow">
  <title>Guarded shadow owner panel</title>
  <style>
    :root { color-scheme: light dark; }
    body {
      font-family: system-ui, -apple-system, Segoe UI, sans-serif;
      margin: 0;
      line-height: 1.45;
      background: Canvas;
      color: CanvasText;
    }
    main { max-width: 1080px; margin: 0 auto; padding: 2rem; }
    header { border-bottom: 1px solid color-mix(in srgb, CanvasText 20%, transparent); margin-bottom: 1.25rem; padding-bottom: 1rem; }
    .muted { opacity: .72; }
    .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: .75rem; margin: 1rem 0; }
    .summary-card { border: 1px solid color-mix(in srgb, CanvasText 18%, transparent); border-radius: .9rem; padding: .85rem; }
    .summary-card strong { display: block; font-size: .8rem; text-transform: uppercase; letter-spacing: .05em; opacity: .7; }
    .summary-card span { display: block; font-size: 1.05rem; margin-top: .25rem; }
    .badge-row { display: flex; flex-wrap: wrap; gap: .4rem; margin: .65rem 0; }
    .badge { display: inline-flex; align-items: center; border: 1px solid color-mix(in srgb, CanvasText 22%, transparent); border-radius: 999px; padding: .2rem .55rem; font-size: .82rem; }
    .shadow-card { border: 1px solid color-mix(in srgb, CanvasText 16%, transparent); border-radius: 1rem; padding: 1rem; margin: 1rem 0; }
    .safety { border-left: .25rem solid color-mix(in srgb, CanvasText 35%, transparent); padding-left: .85rem; margin: 1rem 0; }
    code { background: color-mix(in srgb, CanvasText 8%, transparent); padding: .1rem .25rem; border-radius: .25rem; }
  </style>
</head>
<body
  data-shadow-owner-panel-version="v0.4.74"
  data-shadow-owner-panel-status="enabled"
  data-route-kind="internal_hidden_owner_panel"
  data-has-public-ui-link="false"
  data-effective-source="legacy_fallback"
  data-report-route="/exam-prep/local-bank/live-consumption-shadow-report"
  data-will-consume-local-bank-live="false"
  data-will-deliver-shadow-questions-live="false"
  data-will-start-live-session="false"
  data-will-replace-effective-source="false"
  data-will-persist-attempts="false"
  data-will-update-progress="false"
  data-will-score-live-session="false"
>
  <main>
    <header>
      <h1>Guarded live-consumption shadow owner panel</h1>
      <p class="muted">
        Hidden/internal owner panel. Reads the sanitized v0.4.73 JSON report.
        Effective source remains <code>legacy_fallback</code>. Shadow questions are metadata-only.
      </p>
      <p id="shadow-owner-panel-status">loading</p>
    </header>

    <section aria-labelledby="summary-title">
      <h2 id="summary-title">Shadow summary</h2>
      <div class="summary-grid">
        <div class="summary-card"><strong>Selector</strong><span id="summary-selector">loading</span></div>
        <div class="summary-card"><strong>Effective source</strong><span id="summary-effective">legacy_fallback</span></div>
        <div class="summary-card"><strong>Shadow source</strong><span id="summary-shadow">pending</span></div>
        <div class="summary-card"><strong>Count</strong><span id="summary-count">0</span></div>
      </div>
    </section>

    <section aria-labelledby="coverage-title">
      <h2 id="coverage-title">Coverage comparison</h2>
      <div class="summary-grid">
        <div class="summary-card"><strong>Types</strong><span id="coverage-types">0</span></div>
        <div class="summary-card"><strong>Difficulty</strong><span id="coverage-difficulty">0</span></div>
        <div class="summary-card"><strong>Skills</strong><span id="coverage-skills">0</span></div>
      </div>
    </section>

    <section class="safety" aria-labelledby="safety-title">
      <h2 id="safety-title">Safety guardrails</h2>
      <ul>
        <li>No local-bank questions are delivered live.</li>
        <li>No live session start.</li>
        <li>No effective source replacement.</li>
        <li>No attempt, progress, or session persistence.</li>
        <li>No live scoring and no public Exam Prep navigation change.</li>
      </ul>
    </section>

    <section aria-labelledby="questions-title">
      <h2 id="questions-title">Selected shadow question metadata</h2>
      <p class="muted" id="questions-subtitle">Waiting for sanitized shadow report...</p>
      <div id="shadow-question-list"></div>
    </section>
  </main>

  <script>
    const reportUrl = "/exam-prep/local-bank/live-consumption-shadow-report";
    const statusEl = document.getElementById("shadow-owner-panel-status");
    const summarySelectorEl = document.getElementById("summary-selector");
    const summaryEffectiveEl = document.getElementById("summary-effective");
    const summaryShadowEl = document.getElementById("summary-shadow");
    const summaryCountEl = document.getElementById("summary-count");
    const coverageTypesEl = document.getElementById("coverage-types");
    const coverageDifficultyEl = document.getElementById("coverage-difficulty");
    const coverageSkillsEl = document.getElementById("coverage-skills");
    const subtitleEl = document.getElementById("questions-subtitle");
    const listEl = document.getElementById("shadow-question-list");

    function text(value) {
      return value === undefined || value === null ? "" : String(value);
    }

    function appendText(parent, tagName, value, className) {
      const el = document.createElement(tagName);
      if (className) el.className = className;
      el.textContent = text(value);
      parent.appendChild(el);
      return el;
    }

    function appendBadge(parent, value) {
      appendText(parent, "span", value, "badge");
    }

    function renderShadowQuestion(item) {
      const article = document.createElement("article");
      article.className = "shadow-card";

      const badges = document.createElement("div");
      badges.className = "badge-row";
      appendBadge(badges, text(item.question_type) || "unknown_type");
      appendBadge(badges, text(item.difficulty) || "unknown_difficulty");
      appendBadge(badges, text(item.skill_id) || "unknown_skill");
      appendBadge(badges, text(item.source) || "unknown_source");
      appendBadge(badges, "metadata only");
      article.appendChild(badges);

      appendText(article, "h3", "Shadow item " + text(item.shadow_index));
      appendText(article, "p", "Întrebarea ID: " + text(item.question_id), "muted");
      appendText(article, "p", "Dry run only: " + text(item.dry_run_only) + " · Delivered live: " + text(item.will_deliver_live), "muted");
      return article;
    }

    fetch(reportUrl, { headers: { "accept": "application/json" } })
      .then((response) => response.json())
      .then((data) => {
        const coverage = data.coverage_comparison || {};
        const questions = Array.isArray(data.selected_shadow_questions) ? data.selected_shadow_questions : [];

        statusEl.textContent = data.status || "unknown";
        summarySelectorEl.textContent = data.selector_status || "unknown";
        summaryEffectiveEl.textContent = data.effective_source || "legacy_fallback";
        summaryShadowEl.textContent = data.shadow_source || "";
        summaryCountEl.textContent = String(data.shadow_candidate_count || questions.length || 0);
        coverageTypesEl.textContent = String(coverage.local_question_type_diversity || 0);
        coverageDifficultyEl.textContent = String(coverage.local_difficulty_diversity || 0);
        coverageSkillsEl.textContent = String(coverage.local_skill_diversity || 0);
        subtitleEl.textContent = "Rendered from sanitized metadata-only shadow report.";

        listEl.replaceChildren();
        if (questions.length === 0) {
          appendText(listEl, "p", "No selected shadow questions available.", "muted");
          return;
        }
        questions.forEach((item) => listEl.appendChild(renderShadowQuestion(item)));
      })
      .catch((error) => {
        statusEl.textContent = "error";
        summarySelectorEl.textContent = "error";
        subtitleEl.textContent = text(error);
      });
  </script>
</body>
</html>
"""
    return HTMLResponse(content=panel_html)

# v0.4.78-guarded-first-live-trial-contract-report-route
@app.get("/exam-prep/local-bank/first-live-trial-contract-report")
def exam_prep_local_bank_first_live_trial_contract_report() -> dict:
    """Internal JSON-only sanitized report for the guarded first live-trial contract.

    Disabled by default. Enable locally with:
    VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT_REPORT_ROUTE=1

    This route intentionally uses fixed owner-smoke inputs and does not accept
    user-provided filesystem roots or query parameters. It does not enable live
    consumption, persistence, progress updates, scoring, or public UI changes.
    """

    import os

    route_enabled = os.environ.get(
        "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT_REPORT_ROUTE",
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}

    base = {
        "schema_version": "1",
        "contract_report_route_version": "v0.4.78",
        "mode": "guarded_first_live_trial_contract_report_route",
        "route_path": "/exam-prep/local-bank/first-live-trial-contract-report",
        "route_enabled": route_enabled,
        "route_kind": "internal_json_only",
        "has_public_ui_link": False,
        "report_sanitized": True,
        "raw_contract_included": False,
        "raw_snapshots_included": False,
        "answers_exposed": False,
        "explanations_exposed": False,
        "path_policy": "no_user_provided_filesystem_root",
        "will_consume_local_bank_live": False,
        "will_deliver_local_bank_questions_live": False,
        "will_start_live_session": False,
        "will_replace_effective_source": False,
        "will_persist_progress": False,
        "will_persist_session": False,
        "will_persist_attempts": False,
        "will_update_progress": False,
        "will_score_live_session": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
    }

    if not route_enabled:
        return {
            **base,
            "status": "disabled",
            "contract_status": "disabled",
            "message": "Guarded first live-trial contract report route is disabled by default.",
            "enable_with": "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT_REPORT_ROUTE=1",
            "effective_source": "legacy_fallback",
            "candidate_source": "",
            "fallback_source": "legacy_fallback",
            "contract_sections_available": [],
        }

    from exam_prep_local_bank_first_live_trial_contract import (
        build_first_live_trial_contract,
    )

    contract = build_first_live_trial_contract(
        course_id="v078-route",
        skill_id="local_concept_001_functiile",
        limit=5,
    )
    sections = contract.get("contract_sections") or {}
    implementation = contract.get("implementation_scope") or {}

    return {
        **base,
        "status": "ok",
        "contract_status": contract.get("contract_status"),
        "blocking_reasons": contract.get("blocking_reasons", []),
        "contract_flag_name": contract.get("contract_flag_name"),
        "contract_flag_enabled": contract.get("contract_flag_enabled", False),
        "shadow_consolidation_status": contract.get("shadow_consolidation_status"),
        "shadow_consolidation_ready": contract.get("shadow_consolidation_ready", False),
        "effective_source": "legacy_fallback",
        "candidate_source": contract.get("candidate_source", "local_exercise_bank_adapter"),
        "fallback_source": "legacy_fallback",
        "contract_sections_available": sorted(sections.keys()),
        "source_selection_summary": {
            "current_effective_source": "legacy_fallback",
            "candidate_source": "local_exercise_bank_adapter",
            "fallback_source": "legacy_fallback",
            "may_select_candidate_live_now": False,
            "selection_mode": "contract_skeleton_only",
        },
        "contract_guardrails": {
            "session_boundary_defined": "session_boundary" in sections,
            "attempt_persistence_requires_separate_milestone": True,
            "progress_updates_require_separate_milestone": True,
            "live_scoring_requires_separate_milestone": True,
            "answers_exposed_before_submission": False,
            "explanations_exposed_before_submission": False,
            "raw_snapshots_exposed": False,
            "source_excerpts_exposed": False,
            "requires_safe_dom_rendering": True,
        },
        "implementation_scope": {
            "json_only_contract_object": bool(implementation.get("json_only_contract_object", True)),
            "adds_web_route": True,
            "adds_public_ui": False,
            "starts_live_session": False,
            "replaces_live_study_session": False,
            "persists_attempts": False,
            "updates_progress": False,
            "scores_live_session": False,
            "requires_cloud_or_api": False,
        },
        "next_allowed_milestone_options": contract.get("next_allowed_milestone_options", []),
        "explicit_not_live_yet": [
            "contract report route does not change effective_source",
            "local-bank questions are not delivered live",
            "local-bank questions are not consumed live",
            "live study sessions are not started",
            "effective_source remains legacy_fallback",
            "attempts are not persisted",
            "progress is not updated",
            "sessions are not persisted",
            "live scoring is not enabled",
            "public Exam Prep navigation is not changed",
        ],
    }

# v0.4.79-guarded-first-live-trial-contract-owner-panel
@app.get("/exam-prep/local-bank/first-live-trial-contract-panel")
def exam_prep_local_bank_first_live_trial_contract_panel():
    """Hidden/internal owner panel for the guarded first live-trial contract report.

    Disabled by default. Enable locally with:
    VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT_OWNER_PANEL=1

    The panel reads the v0.4.78 sanitized JSON report route from the browser.
    It uses safe DOM rendering, does not accept query parameters, and does not
    enable live consumption, persistence, progress updates, scoring, or public UI.
    """

    import os
    from fastapi.responses import HTMLResponse

    panel_enabled = os.environ.get(
        "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT_OWNER_PANEL",
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}

    if not panel_enabled:
        disabled_html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex,nofollow">
  <title>First live-trial contract owner panel disabled</title>
</head>
<body
  data-first-live-trial-contract-owner-panel-version="v0.4.79"
  data-first-live-trial-contract-owner-panel-status="disabled"
  data-route-kind="internal_hidden_owner_panel"
  data-has-public-ui-link="false"
  data-effective-source="legacy_fallback"
  data-will-consume-local-bank-live="false"
  data-will-deliver-local-bank-questions-live="false"
  data-will-persist-attempts="false"
  data-will-update-progress="false"
>
  <main>
    <h1>Guarded first live-trial contract owner panel</h1>
    <p id="contract-owner-panel-status">disabled</p>
    <p>This hidden/internal owner panel is disabled by default.</p>
    <p>Enable locally with <code>VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT_OWNER_PANEL=1</code>.</p>
    <ul>
      <li>Effective source remains legacy_fallback.</li>
      <li>No local-bank questions are delivered live.</li>
      <li>No attempts, progress, session persistence, or live scoring.</li>
      <li>No answers, explanations, raw snapshots, or raw contract payloads are exposed by this panel.</li>
    </ul>
  </main>
</body>
</html>
"""
        return HTMLResponse(content=disabled_html)

    panel_html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex,nofollow">
  <title>Guarded first live-trial contract owner panel</title>
  <style>
    :root { color-scheme: light dark; }
    body {
      font-family: system-ui, -apple-system, Segoe UI, sans-serif;
      margin: 0;
      line-height: 1.45;
      background: Canvas;
      color: CanvasText;
    }
    main { max-width: 1120px; margin: 0 auto; padding: 2rem; }
    header { border-bottom: 1px solid color-mix(in srgb, CanvasText 20%, transparent); margin-bottom: 1.25rem; padding-bottom: 1rem; }
    .muted { opacity: .72; }
    .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: .75rem; margin: 1rem 0; }
    .summary-card { border: 1px solid color-mix(in srgb, CanvasText 18%, transparent); border-radius: .9rem; padding: .85rem; }
    .summary-card strong { display: block; font-size: .8rem; text-transform: uppercase; letter-spacing: .05em; opacity: .7; }
    .summary-card span { display: block; font-size: 1.05rem; margin-top: .25rem; }
    .badge-row { display: flex; flex-wrap: wrap; gap: .4rem; margin: .65rem 0; }
    .badge { display: inline-flex; align-items: center; border: 1px solid color-mix(in srgb, CanvasText 22%, transparent); border-radius: 999px; padding: .2rem .55rem; font-size: .82rem; }
    .panel-card { border: 1px solid color-mix(in srgb, CanvasText 16%, transparent); border-radius: 1rem; padding: 1rem; margin: 1rem 0; }
    .safety { border-left: .25rem solid color-mix(in srgb, CanvasText 35%, transparent); padding-left: .85rem; margin: 1rem 0; }
    code { background: color-mix(in srgb, CanvasText 8%, transparent); padding: .1rem .25rem; border-radius: .25rem; }
  </style>
</head>
<body
  data-first-live-trial-contract-owner-panel-version="v0.4.79"
  data-first-live-trial-contract-owner-panel-status="enabled"
  data-route-kind="internal_hidden_owner_panel"
  data-has-public-ui-link="false"
  data-effective-source="legacy_fallback"
  data-report-route="/exam-prep/local-bank/first-live-trial-contract-report"
  data-will-consume-local-bank-live="false"
  data-will-deliver-local-bank-questions-live="false"
  data-will-start-live-session="false"
  data-will-replace-effective-source="false"
  data-will-persist-attempts="false"
  data-will-update-progress="false"
  data-will-score-live-session="false"
>
  <main>
    <header>
      <h1>Guarded first live-trial contract owner panel</h1>
      <p class="muted">
        Hidden/internal owner panel. Reads the sanitized v0.4.78 JSON report.
        Effective source remains <code>legacy_fallback</code>. This is visual review only.
      </p>
      <p id="contract-owner-panel-status">loading</p>
    </header>

    <section aria-labelledby="summary-title">
      <h2 id="summary-title">Contract summary</h2>
      <div class="summary-grid">
        <div class="summary-card"><strong>Status</strong><span id="summary-contract-status">loading</span></div>
        <div class="summary-card"><strong>Effective source</strong><span id="summary-effective">legacy_fallback</span></div>
        <div class="summary-card"><strong>Candidate source</strong><span id="summary-candidate">pending</span></div>
        <div class="summary-card"><strong>Fallback source</strong><span id="summary-fallback">legacy_fallback</span></div>
      </div>
    </section>

    <section aria-labelledby="sections-title">
      <h2 id="sections-title">Contract sections</h2>
      <div id="section-badges" class="badge-row"></div>
    </section>

    <section aria-labelledby="guardrails-title">
      <h2 id="guardrails-title">Guardrails</h2>
      <div id="guardrails-list" class="panel-card"></div>
    </section>

    <section aria-labelledby="implementation-title">
      <h2 id="implementation-title">Implementation scope</h2>
      <div id="implementation-list" class="panel-card"></div>
    </section>

    <section class="safety" aria-labelledby="safety-title">
      <h2 id="safety-title">Explicitly not live yet</h2>
      <ul id="not-live-list"></ul>
    </section>
  </main>

  <script>
    const reportUrl = "/exam-prep/local-bank/first-live-trial-contract-report";
    const statusEl = document.getElementById("contract-owner-panel-status");
    const contractStatusEl = document.getElementById("summary-contract-status");
    const effectiveEl = document.getElementById("summary-effective");
    const candidateEl = document.getElementById("summary-candidate");
    const fallbackEl = document.getElementById("summary-fallback");
    const sectionBadgesEl = document.getElementById("section-badges");
    const guardrailsListEl = document.getElementById("guardrails-list");
    const implementationListEl = document.getElementById("implementation-list");
    const notLiveListEl = document.getElementById("not-live-list");

    function text(value) {
      return value === undefined || value === null ? "" : String(value);
    }

    function appendText(parent, tagName, value, className) {
      const el = document.createElement(tagName);
      if (className) el.className = className;
      el.textContent = text(value);
      parent.appendChild(el);
      return el;
    }

    function appendBadge(parent, value) {
      appendText(parent, "span", value, "badge");
    }

    function renderKeyValues(parent, obj) {
      parent.replaceChildren();
      const list = document.createElement("ul");
      Object.keys(obj || {}).sort().forEach((key) => {
        const item = document.createElement("li");
        item.textContent = key + ": " + text(obj[key]);
        list.appendChild(item);
      });
      parent.appendChild(list);
    }

    function renderList(parent, values) {
      parent.replaceChildren();
      (Array.isArray(values) ? values : []).forEach((value) => {
        appendText(parent, "li", value);
      });
    }

    fetch(reportUrl, { headers: { "accept": "application/json" } })
      .then((response) => response.json())
      .then((data) => {
        statusEl.textContent = data.status || "unknown";
        contractStatusEl.textContent = data.contract_status || "unknown";
        effectiveEl.textContent = data.effective_source || "legacy_fallback";
        candidateEl.textContent = data.candidate_source || "";
        fallbackEl.textContent = data.fallback_source || "legacy_fallback";

        sectionBadgesEl.replaceChildren();
        const sections = Array.isArray(data.contract_sections_available) ? data.contract_sections_available : [];
        sections.forEach((name) => appendBadge(sectionBadgesEl, name));

        renderKeyValues(guardrailsListEl, data.contract_guardrails || {});
        renderKeyValues(implementationListEl, data.implementation_scope || {});
        renderList(notLiveListEl, data.explicit_not_live_yet || []);
      })
      .catch((error) => {
        statusEl.textContent = "error";
        contractStatusEl.textContent = text(error);
      });
  </script>
</body>
</html>
"""
    return HTMLResponse(content=panel_html)

# v0.4.84-guarded-first-live-trial-delivery-route-scaffold
@app.get("/exam-prep/local-bank/first-live-trial-delivery-noop")
def exam_prep_local_bank_first_live_trial_delivery_noop() -> dict:
    """Internal JSON-only first-live-trial delivery route scaffold.

    Disabled by default. Enable locally with:
    VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DELIVERY_ROUTE=1

    This route calls the v0.4.83 no-op delivery adapter. It does not deliver
    questions live, does not start a live session, and does not persist attempts,
    sessions, progress, or scoring.
    """

    import os

    route_enabled = os.environ.get(
        "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DELIVERY_ROUTE",
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}

    base = {
        "schema_version": "1",
        "delivery_route_scaffold_version": "v0.4.84",
        "mode": "guarded_first_live_trial_delivery_route_scaffold",
        "route_path": "/exam-prep/local-bank/first-live-trial-delivery-noop",
        "route_enabled": route_enabled,
        "route_kind": "internal_json_only",
        "has_public_ui_link": False,
        "report_sanitized": True,
        "raw_adapter_result_included": False,
        "raw_contract_included": False,
        "raw_session_envelope_included": False,
        "raw_question_envelopes_included": False,
        "answers_exposed": False,
        "explanations_exposed": False,
        "path_policy": "no_user_provided_filesystem_root",
        "effective_source": "legacy_fallback",
        "fallback_source": "legacy_fallback",
        "will_consume_local_bank_live": False,
        "will_deliver_local_bank_questions_live": False,
        "will_start_live_session": False,
        "will_replace_effective_source": False,
        "will_persist_progress": False,
        "will_persist_session": False,
        "will_persist_attempts": False,
        "will_update_progress": False,
        "will_score_live_session": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
    }

    if not route_enabled:
        return {
            **base,
            "status": "disabled",
            "adapter_status": "disabled",
            "message": "Guarded first live-trial delivery route scaffold is disabled by default.",
            "enable_with": "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DELIVERY_ROUTE=1",
            "candidate_source": "",
            "delivery_attempted": False,
            "delivery_performed": False,
            "delivered_question_count": 0,
            "delivered_question_ids": [],
        }

    from exam_prep_local_bank_first_live_trial_delivery_adapter import (
        build_noop_delivery_adapter_result,
    )

    adapter = build_noop_delivery_adapter_result(
        course_id="v084-route",
        skill_id="local_concept_001_functiile",
        limit=5,
    )
    adapter_summary = adapter.get("adapter_summary") or {}
    adapter_boundary = adapter.get("adapter_contract_boundary") or {}

    return {
        **base,
        "status": "ok",
        "adapter_status": adapter.get("status"),
        "adapter_ready_for_owner_review": adapter.get("ready_for_owner_review", False),
        "adapter_flag_name": adapter.get("adapter_flag_name"),
        "adapter_flag_enabled": adapter.get("adapter_flag_enabled", False),
        "no_persistence_delivery_contract_status": adapter.get("no_persistence_delivery_contract_status"),
        "no_persistence_delivery_contract_ready": adapter.get("no_persistence_delivery_contract_ready", False),
        "candidate_source": adapter.get("candidate_source", "local_exercise_bank_adapter"),
        "candidate_question_count": adapter_summary.get("candidate_question_count", 0),
        "delivery_attempted": False,
        "delivery_performed": False,
        "delivered_question_count": 0,
        "delivered_question_ids": [],
        "adapter_summary": {
            "delivery_attempted": False,
            "delivery_performed": False,
            "delivered_question_count": 0,
            "candidate_question_count": adapter_summary.get("candidate_question_count", 0),
            "noop_only": True,
            "legacy_fallback_available": True,
        },
        "adapter_contract_boundary": {
            "accepts_delivery_contract": bool(adapter_boundary.get("accepts_delivery_contract", True)),
            "requires_no_persistence_policy": True,
            "requires_abort_policy": True,
            "requires_legacy_fallback": True,
            "requires_owner_only_scope": True,
            "requires_candidate_questions": True,
            "blocks_delivery_now": True,
            "returns_noop_result": True,
        },
        "implementation_scope": {
            "json_only_route_scaffold": True,
            "calls_noop_adapter": True,
            "adds_public_ui": False,
            "starts_live_session": False,
            "replaces_live_study_session": False,
            "delivers_local_bank_questions_live": False,
            "persists_sessions": False,
            "persists_attempts": False,
            "updates_progress": False,
            "scores_live_session": False,
            "requires_cloud_or_api": False,
        },
        "explicit_not_live_yet": [
            "delivery route scaffold does not change effective_source",
            "delivery route scaffold calls a no-op adapter",
            "delivery_performed remains false",
            "delivered_question_count remains zero",
            "local-bank questions are not delivered live",
            "local-bank questions are not consumed live",
            "live study sessions are not started",
            "effective_source remains legacy_fallback",
            "attempts are not persisted",
            "progress is not updated",
            "sessions are not persisted",
            "live scoring is not enabled",
            "public Exam Prep navigation is not changed",
        ],
    }

# v0.4.85-guarded-first-live-trial-owner-smoke-route
@app.get("/exam-prep/local-bank/first-live-trial-owner-smoke")
def exam_prep_local_bank_first_live_trial_owner_smoke() -> dict:
    """Internal JSON-only owner smoke route for the first live-trial chain.

    Disabled by default. Enable locally with:
    VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_SMOKE_ROUTE=1

    This route verifies the guarded chain end-to-end up to the no-op delivery
    boundary. It does not deliver questions live, does not start a session, and
    does not persist attempts, sessions, progress, or scoring.
    """

    import os

    route_enabled = os.environ.get(
        "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_SMOKE_ROUTE",
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}

    base = {
        "schema_version": "1",
        "owner_smoke_route_version": "v0.4.85",
        "mode": "guarded_first_live_trial_owner_smoke_route",
        "route_path": "/exam-prep/local-bank/first-live-trial-owner-smoke",
        "route_enabled": route_enabled,
        "route_kind": "internal_json_only",
        "has_public_ui_link": False,
        "report_sanitized": True,
        "raw_adapter_result_included": False,
        "raw_contract_included": False,
        "raw_session_envelope_included": False,
        "raw_question_envelopes_included": False,
        "answers_exposed": False,
        "explanations_exposed": False,
        "path_policy": "no_user_provided_filesystem_root",
        "effective_source": "legacy_fallback",
        "fallback_source": "legacy_fallback",
        "delivery_attempted": False,
        "delivery_performed": False,
        "delivered_question_count": 0,
        "delivered_question_ids": [],
        "will_consume_local_bank_live": False,
        "will_deliver_local_bank_questions_live": False,
        "will_start_live_session": False,
        "will_replace_effective_source": False,
        "will_persist_progress": False,
        "will_persist_session": False,
        "will_persist_attempts": False,
        "will_update_progress": False,
        "will_score_live_session": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
    }

    if not route_enabled:
        return {
            **base,
            "status": "disabled",
            "smoke_status": "disabled",
            "message": "Guarded first live-trial owner smoke route is disabled by default.",
            "enable_with": "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_SMOKE_ROUTE=1",
            "candidate_source": "",
            "owner_smoke_ready_for_next_decision": False,
        }

    from exam_prep_local_bank_first_live_trial_delivery_adapter import (
        build_noop_delivery_adapter_result,
    )

    adapter = build_noop_delivery_adapter_result(
        course_id="v085-owner-smoke",
        skill_id="local_concept_001_functiile",
        limit=5,
    )
    adapter_summary = adapter.get("adapter_summary") or {}
    adapter_boundary = adapter.get("adapter_contract_boundary") or {}
    adapter_ready = bool(adapter.get("ready_for_owner_review", False))
    noop_ok = (
        adapter_summary.get("delivery_attempted") is False
        and adapter_summary.get("delivery_performed") is False
        and int(adapter_summary.get("delivered_question_count") or 0) == 0
    )

    smoke_checks = {
        "adapter_ready": adapter_ready,
        "noop_adapter_status": adapter.get("status"),
        "delivery_attempted_false": adapter_summary.get("delivery_attempted") is False,
        "delivery_performed_false": adapter_summary.get("delivery_performed") is False,
        "delivered_question_count_zero": int(adapter_summary.get("delivered_question_count") or 0) == 0,
        "candidate_question_count_positive": int(adapter_summary.get("candidate_question_count") or 0) > 0,
        "legacy_fallback_available": adapter_summary.get("legacy_fallback_available") is True,
        "blocks_delivery_now": adapter_boundary.get("blocks_delivery_now") is True,
        "returns_noop_result": adapter_boundary.get("returns_noop_result") is True,
        "no_persistence_contract_ready": adapter.get("no_persistence_delivery_contract_ready") is True,
    }
    smoke_ready = all(smoke_checks.values()) and noop_ok

    return {
        **base,
        "status": "ok",
        "smoke_status": "owner_smoke_ready_for_next_decision" if smoke_ready else "blocked",
        "owner_smoke_ready_for_next_decision": smoke_ready,
        "adapter_status": adapter.get("status"),
        "adapter_ready_for_owner_review": adapter_ready,
        "adapter_flag_name": adapter.get("adapter_flag_name"),
        "adapter_flag_enabled": adapter.get("adapter_flag_enabled", False),
        "no_persistence_delivery_contract_status": adapter.get("no_persistence_delivery_contract_status"),
        "no_persistence_delivery_contract_ready": adapter.get("no_persistence_delivery_contract_ready", False),
        "candidate_source": adapter.get("candidate_source", "local_exercise_bank_adapter"),
        "candidate_question_count": int(adapter_summary.get("candidate_question_count") or 0),
        "smoke_checks": smoke_checks,
        "adapter_summary": {
            "delivery_attempted": False,
            "delivery_performed": False,
            "delivered_question_count": 0,
            "candidate_question_count": int(adapter_summary.get("candidate_question_count") or 0),
            "noop_only": True,
            "legacy_fallback_available": True,
        },
        "adapter_contract_boundary": {
            "accepts_delivery_contract": bool(adapter_boundary.get("accepts_delivery_contract", True)),
            "requires_no_persistence_policy": True,
            "requires_abort_policy": True,
            "requires_legacy_fallback": True,
            "requires_owner_only_scope": True,
            "requires_candidate_questions": True,
            "blocks_delivery_now": True,
            "returns_noop_result": True,
        },
        "next_decision_options": [
            "stop_here_keep_noop_route",
            "add_owner_smoke_panel_disabled_by_default",
            "add_explicit_no_persistence_delivery_decision_gate",
        ],
        "implementation_scope": {
            "json_only_owner_smoke_route": True,
            "calls_noop_adapter": True,
            "adds_public_ui": False,
            "starts_live_session": False,
            "replaces_live_study_session": False,
            "delivers_local_bank_questions_live": False,
            "persists_sessions": False,
            "persists_attempts": False,
            "updates_progress": False,
            "scores_live_session": False,
            "requires_cloud_or_api": False,
        },
        "explicit_not_live_yet": [
            "owner smoke route does not change effective_source",
            "owner smoke route calls a no-op adapter",
            "delivery_performed remains false",
            "delivered_question_count remains zero",
            "local-bank questions are not delivered live",
            "local-bank questions are not consumed live",
            "live study sessions are not started",
            "effective_source remains legacy_fallback",
            "attempts are not persisted",
            "progress is not updated",
            "sessions are not persisted",
            "live scoring is not enabled",
            "public Exam Prep navigation is not changed",
        ],
    }

# v0.4.87-guarded-first-live-trial-owner-decision-report-route
@app.get("/exam-prep/local-bank/first-live-trial-owner-decision-report")
def exam_prep_local_bank_first_live_trial_owner_decision_report() -> dict:
    """Internal JSON-only owner decision report over the v0.4.86 decision gate.

    Disabled by default. Enable locally with:
    VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_DECISION_REPORT_ROUTE=1

    This route reports the decision-gate state only. It does not deliver
    questions live, does not start a session, and does not persist attempts,
    sessions, progress, or scoring.
    """

    import os

    route_enabled = os.environ.get(
        "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_DECISION_REPORT_ROUTE",
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}

    base = {
        "schema_version": "1",
        "owner_decision_report_route_version": "v0.4.87",
        "mode": "guarded_first_live_trial_owner_decision_report_route",
        "route_path": "/exam-prep/local-bank/first-live-trial-owner-decision-report",
        "route_enabled": route_enabled,
        "route_kind": "internal_json_only",
        "has_public_ui_link": False,
        "report_sanitized": True,
        "raw_decision_gate_included": False,
        "raw_adapter_result_included": False,
        "raw_contract_included": False,
        "raw_session_envelope_included": False,
        "raw_question_envelopes_included": False,
        "answers_exposed": False,
        "explanations_exposed": False,
        "path_policy": "no_user_provided_filesystem_root",
        "effective_source": "legacy_fallback",
        "fallback_source": "legacy_fallback",
        "real_delivery_allowed_now": False,
        "delivery_attempted": False,
        "delivery_performed": False,
        "delivered_question_count": 0,
        "delivered_question_ids": [],
        "will_consume_local_bank_live": False,
        "will_deliver_local_bank_questions_live": False,
        "will_start_live_session": False,
        "will_replace_effective_source": False,
        "will_persist_progress": False,
        "will_persist_session": False,
        "will_persist_attempts": False,
        "will_update_progress": False,
        "will_score_live_session": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
    }

    if not route_enabled:
        return {
            **base,
            "status": "disabled",
            "decision_gate_status": "disabled",
            "message": "Guarded first live-trial owner decision report route is disabled by default.",
            "enable_with": "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_DECISION_REPORT_ROUTE=1",
            "candidate_source": "",
            "ready_for_next_decision": False,
            "accepted_decision": "",
            "next_allowed_action": "",
        }

    from exam_prep_local_bank_first_live_trial_decision_gate import (
        build_first_live_trial_decision_gate,
    )

    decision = build_first_live_trial_decision_gate(
        course_id="v087-decision-report",
        skill_id="local_concept_001_functiile",
        limit=5,
        requested_decision="keep_noop_only",
    )
    readiness = decision.get("readiness_checks") or {}
    policy = decision.get("decision_gate_policy") or {}
    owner_result = decision.get("owner_decision_result") or {}
    summary = decision.get("decision_summary") or {}
    ready_for_next_decision = bool(decision.get("ready_for_next_decision", False))

    return {
        **base,
        "status": "ok",
        "decision_gate_status": decision.get("status"),
        "decision_gate_ready_for_owner_review": ready_for_next_decision,
        "decision_gate_flag_name": decision.get("decision_gate_flag_name"),
        "decision_gate_flag_enabled": decision.get("decision_gate_flag_enabled", False),
        "noop_delivery_adapter_status": decision.get("noop_delivery_adapter_status"),
        "noop_delivery_adapter_ready": decision.get("noop_delivery_adapter_ready", False),
        "candidate_source": decision.get("candidate_source", "local_exercise_bank_adapter"),
        "requested_decision": decision.get("requested_decision", "keep_noop_only"),
        "accepted_decision": owner_result.get("accepted_decision", ""),
        "ready_for_next_decision": ready_for_next_decision,
        "next_allowed_action": owner_result.get("next_allowed_action", ""),
        "allowed_decision_values": decision.get("allowed_decision_values", []),
        "real_delivery_allowed_now": False,
        "delivery_attempted": False,
        "delivery_performed": False,
        "delivered_question_count": 0,
        "delivered_question_ids": [],
        "decision_summary": {
            "ready_for_next_decision": ready_for_next_decision,
            "real_delivery_allowed_now": False,
            "delivery_attempted": False,
            "delivery_performed": False,
            "delivered_question_count": 0,
            "candidate_question_count": int(summary.get("candidate_question_count") or 0),
            "effective_source_after_decision": "legacy_fallback",
        },
        "readiness_checks": {
            "decision_gate_flag_enabled": bool(readiness.get("decision_gate_flag_enabled", False)),
            "all_required_owner_flags_enabled": bool(readiness.get("all_required_owner_flags_enabled", False)),
            "noop_adapter_ready": bool(readiness.get("noop_adapter_ready", False)),
            "candidate_question_count_positive": bool(readiness.get("candidate_question_count_positive", False)),
            "delivery_attempted_false": bool(readiness.get("delivery_attempted_false", False)),
            "delivery_performed_false": bool(readiness.get("delivery_performed_false", False)),
            "delivered_question_count_zero": bool(readiness.get("delivered_question_count_zero", False)),
            "legacy_fallback_available": bool(readiness.get("legacy_fallback_available", False)),
            "requested_decision_supported": bool(readiness.get("requested_decision_supported", False)),
        },
        "decision_gate_policy": {
            "real_delivery_allowed_now": False,
            "may_flip_effective_source_now": False,
            "may_start_live_session_now": False,
            "may_persist_session_now": False,
            "may_persist_attempts_now": False,
            "may_update_progress_now": False,
            "may_score_live_session_now": False,
            "requires_separate_real_delivery_milestone": True,
            "requires_owner_reconfirmation_before_real_delivery": bool(policy.get("requires_owner_reconfirmation_before_real_delivery", True)),
            "requires_rollback_to_legacy_fallback": bool(policy.get("requires_rollback_to_legacy_fallback", True)),
        },
        "next_decision_options": [
            "keep_noop_only",
            "prepare_owner_panel_review",
            "prepare_future_real_delivery_milestone",
        ],
        "implementation_scope": {
            "json_only_owner_decision_report_route": True,
            "calls_decision_gate": True,
            "adds_public_ui": False,
            "starts_live_session": False,
            "replaces_live_study_session": False,
            "delivers_local_bank_questions_live": False,
            "persists_sessions": False,
            "persists_attempts": False,
            "updates_progress": False,
            "scores_live_session": False,
            "requires_cloud_or_api": False,
        },
        "explicit_not_live_yet": [
            "owner decision report route does not change effective_source",
            "owner decision report route calls a decision gate that blocks real delivery",
            "real_delivery_allowed_now remains false",
            "delivery_performed remains false",
            "delivered_question_count remains zero",
            "local-bank questions are not delivered live",
            "local-bank questions are not consumed live",
            "live study sessions are not started",
            "effective_source remains legacy_fallback",
            "attempts are not persisted",
            "progress is not updated",
            "sessions are not persisted",
            "live scoring is not enabled",
            "public Exam Prep navigation is not changed",
        ],
    }

# v0.4.88-guarded-first-live-trial-owner-decision-panel
@app.get("/exam-prep/local-bank/first-live-trial-owner-decision-panel")
def exam_prep_local_bank_first_live_trial_owner_decision_panel():
    """Hidden/internal owner decision panel over the v0.4.87 decision report.

    Disabled by default. Enable locally with:
    VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_DECISION_PANEL=1

    The panel reads the v0.4.87 sanitized JSON report route from the browser.
    It uses safe DOM rendering, does not accept query parameters, and does not
    enable live delivery, persistence, progress updates, scoring, or public UI.
    """

    import os
    from fastapi.responses import HTMLResponse

    panel_enabled = os.environ.get(
        "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_DECISION_PANEL",
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}

    if not panel_enabled:
        disabled_html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex,nofollow">
  <title>First live-trial owner decision panel disabled</title>
</head>
<body
  data-owner-decision-panel-version="v0.4.88"
  data-owner-decision-panel-status="disabled"
  data-route-kind="internal_hidden_owner_panel"
  data-has-public-ui-link="false"
  data-effective-source="legacy_fallback"
  data-real-delivery-allowed-now="false"
  data-delivery-performed="false"
  data-delivered-question-count="0"
  data-will-consume-local-bank-live="false"
  data-will-deliver-local-bank-questions-live="false"
  data-will-persist-attempts="false"
  data-will-update-progress="false"
  data-will-score-live-session="false"
>
  <main>
    <h1>Guarded first live-trial owner decision panel</h1>
    <p id="owner-decision-panel-status">disabled</p>
    <p>This hidden/internal owner panel is disabled by default.</p>
    <p>Enable locally with <code>VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_DECISION_PANEL=1</code>.</p>
    <ul>
      <li>Effective source remains legacy_fallback.</li>
      <li>Real delivery is not allowed now.</li>
      <li>No local-bank questions are delivered live.</li>
      <li>No attempts, progress, session persistence, or live scoring.</li>
      <li>No answers, explanations, raw envelopes, or raw contracts are exposed by this panel.</li>
    </ul>
  </main>
</body>
</html>
"""
        return HTMLResponse(content=disabled_html)

    panel_html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex,nofollow">
  <title>Guarded first live-trial owner decision panel</title>
  <style>
    :root { color-scheme: light dark; }
    body {
      font-family: system-ui, -apple-system, Segoe UI, sans-serif;
      margin: 0;
      line-height: 1.45;
      background: Canvas;
      color: CanvasText;
    }
    main { max-width: 1120px; margin: 0 auto; padding: 2rem; }
    header { border-bottom: 1px solid color-mix(in srgb, CanvasText 20%, transparent); margin-bottom: 1.25rem; padding-bottom: 1rem; }
    .muted { opacity: .72; }
    .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: .75rem; margin: 1rem 0; }
    .summary-card { border: 1px solid color-mix(in srgb, CanvasText 18%, transparent); border-radius: .9rem; padding: .85rem; }
    .summary-card strong { display: block; font-size: .8rem; text-transform: uppercase; letter-spacing: .05em; opacity: .7; }
    .summary-card span { display: block; font-size: 1.05rem; margin-top: .25rem; }
    .badge-row { display: flex; flex-wrap: wrap; gap: .4rem; margin: .65rem 0; }
    .badge { display: inline-flex; align-items: center; border: 1px solid color-mix(in srgb, CanvasText 22%, transparent); border-radius: 999px; padding: .2rem .55rem; font-size: .82rem; }
    .panel-card { border: 1px solid color-mix(in srgb, CanvasText 16%, transparent); border-radius: 1rem; padding: 1rem; margin: 1rem 0; }
    .safety { border-left: .25rem solid color-mix(in srgb, CanvasText 35%, transparent); padding-left: .85rem; margin: 1rem 0; }
    code { background: color-mix(in srgb, CanvasText 8%, transparent); padding: .1rem .25rem; border-radius: .25rem; }
  </style>
</head>
<body
  data-owner-decision-panel-version="v0.4.88"
  data-owner-decision-panel-status="enabled"
  data-route-kind="internal_hidden_owner_panel"
  data-has-public-ui-link="false"
  data-effective-source="legacy_fallback"
  data-report-route="/exam-prep/local-bank/first-live-trial-owner-decision-report"
  data-real-delivery-allowed-now="false"
  data-delivery-performed="false"
  data-delivered-question-count="0"
  data-will-consume-local-bank-live="false"
  data-will-deliver-local-bank-questions-live="false"
  data-will-start-live-session="false"
  data-will-replace-effective-source="false"
  data-will-persist-attempts="false"
  data-will-update-progress="false"
  data-will-score-live-session="false"
>
  <main>
    <header>
      <h1>Guarded first live-trial owner decision panel</h1>
      <p class="muted">
        Hidden/internal owner panel. Reads the sanitized v0.4.87 JSON decision report.
        Effective source remains <code>legacy_fallback</code>. Real delivery is still blocked.
      </p>
      <p id="owner-decision-panel-status">loading</p>
    </header>

    <section aria-labelledby="summary-title">
      <h2 id="summary-title">Decision summary</h2>
      <div class="summary-grid">
        <div class="summary-card"><strong>Accepted decision</strong><span id="summary-accepted">loading</span></div>
        <div class="summary-card"><strong>Ready for next decision</strong><span id="summary-ready">loading</span></div>
        <div class="summary-card"><strong>Real delivery allowed</strong><span id="summary-real-delivery">false</span></div>
        <div class="summary-card"><strong>Delivery performed</strong><span id="summary-delivery-performed">false</span></div>
        <div class="summary-card"><strong>Delivered questions</strong><span id="summary-delivered-count">0</span></div>
        <div class="summary-card"><strong>Effective source</strong><span id="summary-effective">legacy_fallback</span></div>
      </div>
    </section>

    <section aria-labelledby="options-title">
      <h2 id="options-title">Next decision options</h2>
      <div id="decision-options" class="badge-row"></div>
    </section>

    <section aria-labelledby="readiness-title">
      <h2 id="readiness-title">Readiness checks</h2>
      <div id="readiness-list" class="panel-card"></div>
    </section>

    <section aria-labelledby="policy-title">
      <h2 id="policy-title">Decision gate policy</h2>
      <div id="policy-list" class="panel-card"></div>
    </section>

    <section class="safety" aria-labelledby="safety-title">
      <h2 id="safety-title">Explicitly not live yet</h2>
      <ul id="not-live-list"></ul>
    </section>
  </main>

  <script>
    const reportUrl = "/exam-prep/local-bank/first-live-trial-owner-decision-report";
    const statusEl = document.getElementById("owner-decision-panel-status");
    const acceptedEl = document.getElementById("summary-accepted");
    const readyEl = document.getElementById("summary-ready");
    const realDeliveryEl = document.getElementById("summary-real-delivery");
    const deliveryPerformedEl = document.getElementById("summary-delivery-performed");
    const deliveredCountEl = document.getElementById("summary-delivered-count");
    const effectiveEl = document.getElementById("summary-effective");
    const decisionOptionsEl = document.getElementById("decision-options");
    const readinessListEl = document.getElementById("readiness-list");
    const policyListEl = document.getElementById("policy-list");
    const notLiveListEl = document.getElementById("not-live-list");

    function text(value) {
      return value === undefined || value === null ? "" : String(value);
    }

    function appendText(parent, tagName, value, className) {
      const el = document.createElement(tagName);
      if (className) el.className = className;
      el.textContent = text(value);
      parent.appendChild(el);
      return el;
    }

    function appendBadge(parent, value) {
      appendText(parent, "span", value, "badge");
    }

    function renderKeyValues(parent, obj) {
      parent.replaceChildren();
      const list = document.createElement("ul");
      Object.keys(obj || {}).sort().forEach((key) => {
        const item = document.createElement("li");
        item.textContent = key + ": " + text(obj[key]);
        list.appendChild(item);
      });
      parent.appendChild(list);
    }

    function renderList(parent, values) {
      parent.replaceChildren();
      (Array.isArray(values) ? values : []).forEach((value) => {
        appendText(parent, "li", value);
      });
    }

    fetch(reportUrl, { headers: { "accept": "application/json" } })
      .then((response) => response.json())
      .then((data) => {
        statusEl.textContent = data.status || "unknown";
        acceptedEl.textContent = data.accepted_decision || "";
        readyEl.textContent = text(data.ready_for_next_decision);
        realDeliveryEl.textContent = text(data.real_delivery_allowed_now);
        deliveryPerformedEl.textContent = text(data.delivery_performed);
        deliveredCountEl.textContent = text(data.delivered_question_count);
        effectiveEl.textContent = data.effective_source || "legacy_fallback";

        decisionOptionsEl.replaceChildren();
        const options = Array.isArray(data.next_decision_options) ? data.next_decision_options : [];
        options.forEach((name) => appendBadge(decisionOptionsEl, name));

        renderKeyValues(readinessListEl, data.readiness_checks || {});
        renderKeyValues(policyListEl, data.decision_gate_policy || {});
        renderList(notLiveListEl, data.explicit_not_live_yet || []);
      })
      .catch((error) => {
        statusEl.textContent = "error";
        acceptedEl.textContent = text(error);
      });
  </script>
</body>
</html>
"""
    return HTMLResponse(content=panel_html)

# --- v0.5.5 owner-only hidden session preview route ---
from fastapi import Request as _VoilaOwnerSessionPreviewRequest
from fastapi.responses import JSONResponse as _VoilaOwnerSessionPreviewJSONResponse

_VOILA_OWNER_SESSION_PREVIEW_ROUTE_VERSION = "v0.5.5"
_VOILA_OWNER_SESSION_PREVIEW_ROUTE_FLAG = "VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_ROUTE"
_VOILA_OWNER_SESSION_PREVIEW_ROUTE_PATH = "/owner/exam-prep/session-preview.json"


def _voila_owner_session_preview_route_flag_enabled() -> bool:
    import os

    return str(os.environ.get(_VOILA_OWNER_SESSION_PREVIEW_ROUTE_FLAG, "")).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _voila_owner_session_preview_is_local_request(
    request: _VoilaOwnerSessionPreviewRequest,
) -> bool:
    client = getattr(request, "client", None)
    host = str(getattr(client, "host", "") or "").strip().lower()
    return host in {"127.0.0.1", "::1", "localhost"} or host.startswith("127.")


def _voila_owner_session_preview_not_found() -> _VoilaOwnerSessionPreviewJSONResponse:
    return _VoilaOwnerSessionPreviewJSONResponse(
        status_code=404,
        content={
            "schema_version": "1",
            "route_version": _VOILA_OWNER_SESSION_PREVIEW_ROUTE_VERSION,
            "status": "not_found",
            "route_enabled": False,
            "owner_only": True,
            "hidden_route": True,
            "effective_source": "legacy_fallback",
            "delivery_performed": False,
            "adds_public_ui": False,
            "persists_sessions": False,
            "persists_attempts": False,
            "updates_progress": False,
            "scores_live_session": False,
        },
    )


@app.get(_VOILA_OWNER_SESSION_PREVIEW_ROUTE_PATH, include_in_schema=False)
async def voila_owner_only_session_preview_json(
    request: _VoilaOwnerSessionPreviewRequest,
) -> _VoilaOwnerSessionPreviewJSONResponse:
    if not _voila_owner_session_preview_route_flag_enabled():
        return _voila_owner_session_preview_not_found()

    if not _voila_owner_session_preview_is_local_request(request):
        return _voila_owner_session_preview_not_found()

    import importlib.util
    import shutil
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    work_root = root / ".tmp" / "v055-owner-only-session-preview-route"
    output = work_root / "owner_only_session_preview_route.json"
    helper_path = root / "scripts" / "dev" / "build-local-bank-owner-only-session-preview.py"

    try:
        spec = importlib.util.spec_from_file_location(
            "voila_v055_owner_only_session_preview_helper",
            helper_path,
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("Could not load owner-only session preview helper")

        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)

        preview = helper.build_preview(root=root, work_root=work_root, output=output)
        preview["route_version"] = _VOILA_OWNER_SESSION_PREVIEW_ROUTE_VERSION
        preview["route_path"] = _VOILA_OWNER_SESSION_PREVIEW_ROUTE_PATH
        preview["route_flag_name"] = _VOILA_OWNER_SESSION_PREVIEW_ROUTE_FLAG
        preview["route_enabled"] = True
        preview["owner_only_route"] = True
        preview["hidden_route"] = True
        preview["adds_public_ui"] = False
        preview["persists_sessions"] = False
        preview["persists_attempts"] = False
        preview["updates_progress"] = False
        preview["scores_live_session"] = False
        preview["requires_cloud_or_api"] = False

        return _VoilaOwnerSessionPreviewJSONResponse(content=preview)
    except Exception as exc:
        return _VoilaOwnerSessionPreviewJSONResponse(
            status_code=500,
            content={
                "schema_version": "1",
                "route_version": _VOILA_OWNER_SESSION_PREVIEW_ROUTE_VERSION,
                "status": "error",
                "owner_only_route": True,
                "hidden_route": True,
                "error_code": "owner_session_preview_unavailable",
                "error_message": "Owner-only session preview is unavailable.",
                "adds_public_ui": False,
                "persists_sessions": False,
                "persists_attempts": False,
                "updates_progress": False,
                "scores_live_session": False,
            },
        )
    finally:
        if work_root.exists():
            shutil.rmtree(work_root)
# --- end v0.5.5 owner-only hidden session preview route ---

# --- v0.5.6 owner-only hidden session preview page ---
from fastapi import Request as _VoilaOwnerSessionPreviewPageRequest
from fastapi.responses import HTMLResponse as _VoilaOwnerSessionPreviewHTMLResponse

_VOILA_OWNER_SESSION_PREVIEW_PAGE_VERSION = "v0.5.6"
_VOILA_OWNER_SESSION_PREVIEW_PAGE_FLAG = "VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_PAGE"
_VOILA_OWNER_SESSION_PREVIEW_PAGE_PATH = "/owner/exam-prep/session-preview"


def _voila_owner_session_preview_page_flag_enabled() -> bool:
    import os

    return str(os.environ.get(_VOILA_OWNER_SESSION_PREVIEW_PAGE_FLAG, "")).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _voila_owner_session_preview_page_is_local_request(
    request: _VoilaOwnerSessionPreviewPageRequest,
) -> bool:
    client = getattr(request, "client", None)
    host = str(getattr(client, "host", "") or "").strip().lower()
    return host in {"127.0.0.1", "::1", "localhost"} or host.startswith("127.")


def _voila_owner_session_preview_page_not_found() -> _VoilaOwnerSessionPreviewHTMLResponse:
    return _VoilaOwnerSessionPreviewHTMLResponse(
        status_code=404,
        content="Not found",
    )


def _voila_owner_session_preview_page_escape(value: object) -> str:
    import html

    return html.escape(str(value or ""), quote=True)


def _voila_owner_session_preview_page_polish_display_copy(value: object) -> str:
    text = str(value or "")
    replacements = {
        "Mentioneaza": "Menționează",
        "sustinuta": "susținută",
        "Daca exista": "Dacă există",
        "LHopital": "L'Hôpital",
        "Ce idee importanta": "Ce idee importantă",
        "aplicatie": "aplicație",
        "notiunii": "noțiunii",
        "limita": "limită",
        "existentei": "existenței",
        "functii": "funcții",
        "functiei": "funcției",
        "urmatoarea": "următoarea",
        "definitie": "definiție",
        "incercari": "încercări",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def _voila_owner_session_preview_page_question_type_label(value: object) -> str:
    labels = {
        "short_answer": "răspuns scurt",
        "multiple_choice": "alegere multiplă",
    }
    raw = str(value or "")
    return labels.get(raw, raw)


def _voila_owner_session_preview_page_difficulty_label(value: object) -> str:
    labels = {
        "easy": "ușor",
        "medium": "mediu",
        "hard": "dificil",
    }
    raw = str(value or "")
    return labels.get(raw, raw)


def _voila_owner_session_preview_page_html(preview: dict) -> str:
    prompts = []
    session = preview.get("session_preview") or {}
    questions = session.get("questions") or []

    for question in questions:
        display_index = _voila_owner_session_preview_page_escape(question.get("display_index"))
        prompt = _voila_owner_session_preview_page_escape(
            _voila_owner_session_preview_page_polish_display_copy(question.get("prompt"))
        )
        question_id = _voila_owner_session_preview_page_escape(question.get("question_id"))
        question_type = _voila_owner_session_preview_page_escape(
            _voila_owner_session_preview_page_question_type_label(question.get("question_type"))
        )
        difficulty = _voila_owner_session_preview_page_escape(
            _voila_owner_session_preview_page_difficulty_label(question.get("difficulty"))
        )

        prompts.append(
            "<article class=\"question-card\" data-question-id=\""
            + question_id
            + "\">"
            + "<p class=\"question-meta\">Întrebarea "
            + display_index
            + " · "
            + question_type
            + " · "
            + difficulty
            + "</p>"
            + "<h2>"
            + prompt
            + "</h2>"
            + "<p class=\"question-policy\">Răspunsul și explicația sunt ascunse. Această previzualizare nu trimite răspunsuri, nu salvează încercări, nu actualizează progresul și nu calculează scoruri.</p>"
            + "</article>"
        )

    selected_course = _voila_owner_session_preview_page_escape(
        preview.get("selected_real_course_path")
    )
    question_count = _voila_owner_session_preview_page_escape(
        session.get("question_count")
    )
    route_version = _voila_owner_session_preview_page_escape(
        _VOILA_OWNER_SESSION_PREVIEW_PAGE_VERSION
    )
    effective_source = _voila_owner_session_preview_page_escape(
        (preview.get("delivery_result") or {}).get("effective_source")
    )
    rollback_source = _voila_owner_session_preview_page_escape(
        (preview.get("rollback_result") or {}).get("effective_source")
    )

    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex,nofollow">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Previzualizare sesiune Pregătire examene</title>
  <style>
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; background: #0f172a; color: #e5e7eb; }
    main { max-width: 920px; margin: 0 auto; padding: 32px 20px 56px; }
    .badge { display: inline-block; padding: 4px 10px; border: 1px solid #334155; border-radius: 999px; color: #cbd5e1; font-size: 13px; }
    .summary, .question-card { background: #111827; border: 1px solid #334155; border-radius: 18px; padding: 18px; margin-top: 16px; }
    .question-meta, .question-policy, .muted { color: #94a3b8; font-size: 14px; }
    h1 { font-size: 30px; margin-bottom: 8px; }
    h2 { font-size: 18px; line-height: 1.45; }
    code { color: #bae6fd; }
  </style>
</head>
<body data-route-version=\"""" + route_version + """\" data-owner-only=\"true\" data-hidden-route=\"true\">
  <main>
    <span class="badge">Owner-only hidden preview · """ + route_version + """</span>
    <h1>Previzualizare sesiune Pregătire examene</h1>
    <p class="muted">Această previzualizare locală owner-only afișează cinci întrebări sanitizate. Nu are trimitere răspunsuri, nu salvează încercări, nu actualizează progresul și nu calculează scoruri.</p>

    <section class="summary">
      <p><strong>Curs selectat:</strong> <code>""" + selected_course + """</code></p>
      <p><strong>Întrebări:</strong> """ + question_count + """</p>
      <p><strong>Sursă activă:</strong> """ + effective_source + """</p>
      <p><strong>Sursă rollback:</strong> """ + rollback_source + """</p>
    </section>

    <section aria-label="Session questions">
      """ + "\n      ".join(prompts) + """
    </section>
  </main>
</body>
</html>"""


@app.get(_VOILA_OWNER_SESSION_PREVIEW_PAGE_PATH, include_in_schema=False)
async def voila_owner_only_session_preview_page(
    request: _VoilaOwnerSessionPreviewPageRequest,
) -> _VoilaOwnerSessionPreviewHTMLResponse:
    if not _voila_owner_session_preview_page_flag_enabled():
        return _voila_owner_session_preview_page_not_found()

    if not _voila_owner_session_preview_page_is_local_request(request):
        return _voila_owner_session_preview_page_not_found()

    import importlib.util
    import shutil
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    work_root = root / ".tmp" / "v056-owner-only-session-preview-page"
    output = work_root / "owner_only_session_preview_page.json"
    helper_path = root / "scripts" / "dev" / "build-local-bank-owner-only-session-preview.py"

    try:
        spec = importlib.util.spec_from_file_location(
            "voila_v056_owner_only_session_preview_helper",
            helper_path,
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("owner_preview_helper_unavailable")

        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)

        preview = helper.build_preview(root=root, work_root=work_root, output=output)
        preview["page_version"] = _VOILA_OWNER_SESSION_PREVIEW_PAGE_VERSION
        preview["page_path"] = _VOILA_OWNER_SESSION_PREVIEW_PAGE_PATH
        preview["page_flag_name"] = _VOILA_OWNER_SESSION_PREVIEW_PAGE_FLAG
        preview["page_enabled"] = True
        preview["owner_only_page"] = True
        preview["hidden_page"] = True
        preview["adds_public_ui"] = False
        preview["persists_sessions"] = False
        preview["persists_attempts"] = False
        preview["updates_progress"] = False
        preview["scores_live_session"] = False
        preview["requires_cloud_or_api"] = False

        return _VoilaOwnerSessionPreviewHTMLResponse(
            content=_voila_owner_session_preview_page_html(preview)
        )
    except Exception:
        return _VoilaOwnerSessionPreviewHTMLResponse(
            status_code=500,
            content="Owner-only session preview is unavailable.",
        )
    finally:
        if work_root.exists():
            shutil.rmtree(work_root)
# --- end v0.5.6 owner-only hidden session preview page ---
