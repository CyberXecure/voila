from __future__ import annotations

import shutil
import datetime as dt
import re
import subprocess
import sys
from datetime import datetime

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from study_engine import get_study_view, record_answer, reset_study_state
import exam_prep
import html
import json
import os
from pathlib import Path
from starlette.requests import Request
from urllib.parse import quote, unquote
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response
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

# VOILA_V0_7_1_OWNER_LOCAL_OCR_MATH_REPORT_UI_LINK_START
# Owner-local UI link/viewer only for OCR Math diagnostic reports.
# Policy: read-only diagnostics; no auto-correction, no Formula OCR, no build, no ZIP, no delivery, no distribution.

def _voila_ocr_math_report_candidate_roots() -> list[Path]:
    roots: list[Path] = []

    for env_name in (
        "VOILA_DATA_DIR",
        "VOILA_LIBRARY_DIR",
        "VOILA_OWNER_LIBRARY_DIR",
        "VOILA_STORAGE_DIR",
    ):
        env_value = os.environ.get(env_name)
        if env_value:
            roots.append(Path(env_value))

    here = Path(__file__).resolve()
    repo_candidates = [Path.cwd()]
    for parent in here.parents:
        repo_candidates.append(parent)

    for base in repo_candidates:
        roots.extend(
            [
                base,
                base / "data",
                base / "library",
                base / "uploads",
                base / "courses",
                base / "services" / "api" / "data",
                base / "services" / "api" / "library",
            ]
        )

    unique: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        try:
            resolved = root.resolve()
        except Exception:
            resolved = root
        key = str(resolved).lower()
        if key not in seen:
            seen.add(key)
            unique.append(resolved)
    return unique


def _voila_ocr_math_report_is_excluded(path: Path) -> bool:
    excluded = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".release-cache",
        "release-assets",
        "dist",
        "build",
    }
    return any(part in excluded for part in path.parts)


def _voila_ocr_math_report_paths(course_id: str) -> tuple[Path | None, Path | None]:
    safe_id = unquote(str(course_id or "")).strip().strip("/")
    if not safe_id:
        return None, None
    if ".." in safe_id or "\\" in safe_id or ":" in safe_id:
        return None, None

    lowered = safe_id.lower()
    matches: list[Path] = []

    for root in _voila_ocr_math_report_candidate_roots():
        if not root.exists() or _voila_ocr_math_report_is_excluded(root):
            continue

        direct_dirs = [
            root / safe_id,
            root / "output" / safe_id,
            root / "data" / "output" / safe_id,
            root / "library" / safe_id,
            root / "uploads" / safe_id,
            root / "courses" / safe_id,
            root / "data" / safe_id,
        ]
        for directory in direct_dirs:
            md = directory / "ocr_math_report.md"
            if md.is_file():
                return md, directory / "ocr_math_report.json"

        # v0.7.56: bounded owner-local lookup only.
        # Do not fall back to recursive scans across repo parents or drive roots.
        # Missing OCR Math reports must return quickly as unavailable.

    if not matches:
        return None, None

    md = sorted(matches, key=lambda p: len(str(p)))[0]
    return md, md.parent / "ocr_math_report.json"


def _voila_ocr_math_report_nested_value(data: dict, keys: tuple[str, ...]):
    for key in keys:
        if key in data:
            return data.get(key)

    for container_key in ("summary", "stats", "diagnostics", "report"):
        nested = data.get(container_key)
        if isinstance(nested, dict):
            for key in keys:
                if key in nested:
                    return nested.get(key)

    return None


def _voila_ocr_math_report_summary(md_path: Path, json_path: Path | None) -> dict:
    data = {}
    if json_path and json_path.is_file():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    total_suggestions = None
    changed_line_count = None

    if isinstance(data, dict):
        total_suggestions = _voila_ocr_math_report_nested_value(
            data,
            ("total_suggestions", "suggestion_count", "suggestions_count"),
        )
        changed_line_count = _voila_ocr_math_report_nested_value(
            data,
            ("changed_line_count", "changed_lines_count"),
        )

        suggestions = data.get("suggestions")
        if total_suggestions is None and isinstance(suggestions, list):
            total_suggestions = len(suggestions)

        changed_lines = data.get("changed_lines")
        if changed_line_count is None and isinstance(changed_lines, list):
            changed_line_count = len(changed_lines)

    return {
        "exists": True,
        "report_md": "ocr_math_report.md",
        "total_suggestions": total_suggestions,
        "changed_line_count": changed_line_count,
        "report_size_bytes": md_path.stat().st_size,
    }


def _voila_ocr_math_report_display_value(value) -> str:
    if value is None or value == "":
        return "n/a"
    return str(value)


@app.get("/owner/ocr-math-report/{course_id}/summary.json", include_in_schema=False)
async def _voila_owner_ocr_math_report_summary(course_id: str):
    md_path, json_path = _voila_ocr_math_report_paths(course_id)
    if not md_path or not md_path.is_file():
        return JSONResponse(
            {
                "exists": False,
                "report_md": "ocr_math_report.md",
                "total_suggestions": None,
                "changed_line_count": None,
            },
            status_code=404,
        )

    return JSONResponse(_voila_ocr_math_report_summary(md_path, json_path))


@app.get("/owner/ocr-math-report/{course_id}/ocr_math_report.md", include_in_schema=False)
async def _voila_owner_ocr_math_report_markdown(course_id: str):
    md_path, _json_path = _voila_ocr_math_report_paths(course_id)
    if not md_path or not md_path.is_file():
        return PlainTextResponse(
            "ocr_math_report.md was not found for this local course/document.",
            status_code=404,
        )

    return PlainTextResponse(
        md_path.read_text(encoding="utf-8", errors="replace"),
        media_type="text/markdown; charset=utf-8",
    )


def _voila_ocr_math_report_markdown_to_html(markdown_text: str) -> str:
    """Render a small, safe, dependency-free subset of Markdown for owner-local reports."""
    parts: list[str] = []
    in_list = False
    in_code = False
    code_lines: list[str] = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            parts.append("</ul>")
            in_list = False

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code:
                parts.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
                in_code = False
            else:
                close_list()
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not stripped:
            close_list()
            parts.append("<br>")
            continue

        if stripped.startswith("#"):
            close_list()
            level = min(len(stripped) - len(stripped.lstrip("#")), 4)
            content = stripped[level:].strip() or stripped
            parts.append(f"<h{level}>{html.escape(content)}</h{level}>")
            continue

        if stripped.startswith(("- ", "* ")):
            if not in_list:
                parts.append("<ul>")
                in_list = True
            parts.append("<li>" + html.escape(stripped[2:].strip()) + "</li>")
            continue

        close_list()
        parts.append("<p>" + html.escape(line) + "</p>")

    if in_code:
        parts.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")

    close_list()
    return "\n".join(parts)


@app.get("/owner/ocr-math-report/{course_id}/view", include_in_schema=False)
async def _voila_owner_ocr_math_report_viewer(course_id: str):
    md_path, json_path = _voila_ocr_math_report_paths(course_id)
    if not md_path or not md_path.is_file():
        return HTMLResponse(
            """
<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <title>Raport diagnostic OCR Math indisponibil</title>
  <style>
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; line-height: 1.5; }
    .card { max-width: 920px; border: 1px solid rgba(31,78,121,0.3); border-radius: 16px; padding: 20px; }
    .muted { opacity: 0.76; }
  </style>
</head>
<body>
  <main class="card">
    <h1>Raport diagnostic OCR Math indisponibil</h1>
    <p class="muted">Nu există încă un <code>ocr_math_report.md</code> pentru acest document local.</p>
    <p class="muted">Această pagină este read-only și nu modifică OCR-ul, cursul, Study sau Progress.</p>
  </main>
</body>
</html>
""",
            status_code=404,
        )

    summary = _voila_ocr_math_report_summary(md_path, json_path)
    markdown_text = md_path.read_text(encoding="utf-8", errors="replace")
    rendered_report = _voila_ocr_math_report_markdown_to_html(markdown_text)

    safe_course_id = html.escape(str(course_id), quote=True)
    safe_raw_href = "/owner/ocr-math-report/" + quote(str(course_id), safe="") + "/ocr_math_report.md"
    # VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_OCR_MATH_LINK_START
    safe_formula_visual_href = "/owner/formula-visual-evidence/" + quote(str(course_id), safe="") + "/view"
    # VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_OCR_MATH_LINK_END
    total_suggestions = html.escape(_voila_ocr_math_report_display_value(summary.get("total_suggestions")))
    changed_line_count = html.escape(_voila_ocr_math_report_display_value(summary.get("changed_line_count")))
    size_bytes = html.escape(_voila_ocr_math_report_display_value(summary.get("report_size_bytes")))

    page = f"""
<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <title>Raport diagnostic OCR Math</title>
  <style>
    :root {{
      color-scheme: light dark;
      --voila-blue: #1F4E79;
      --voila-border: rgba(31,78,121,0.32);
      --voila-soft: rgba(31,78,121,0.07);
    }}
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
      line-height: 1.55;
    }}
    main {{
      max-width: 1040px;
      margin: 0 auto;
      padding: 28px 20px 44px;
    }}
    .topbar {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-start;
      flex-wrap: wrap;
      border: 1px solid var(--voila-border);
      border-radius: 18px;
      padding: 18px;
      background: var(--voila-soft);
      margin-bottom: 20px;
    }}
    h1 {{
      margin: 0 0 6px;
      font-size: clamp(1.6rem, 3vw, 2.25rem);
    }}
    .muted {{ opacity: 0.76; }}
    .badge {{
      display: inline-flex;
      border: 1px solid var(--voila-border);
      border-radius: 999px;
      padding: 5px 9px;
      font-size: 0.82rem;
      margin-top: 4px;
    }}
    .metrics {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 14px;
    }}
    .metric {{
      border: 1px solid var(--voila-border);
      border-radius: 14px;
      padding: 10px 12px;
      min-width: 150px;
      background: rgba(255,255,255,0.05);
    }}
    .metric span {{
      display: block;
      font-size: 0.82rem;
      opacity: 0.75;
    }}
    .metric strong {{
      display: block;
      font-size: 1.35rem;
      margin-top: 2px;
    }}
    .actions {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
    }}
    a.button {{
      display: inline-flex;
      border: 1px solid currentColor;
      border-radius: 12px;
      padding: 9px 12px;
      text-decoration: none;
      font-weight: 650;
    }}
    .report {{
      border: 1px solid var(--voila-border);
      border-radius: 18px;
      padding: 22px;
      overflow-wrap: anywhere;
    }}
    .report h1, .report h2, .report h3, .report h4 {{
      color: var(--voila-blue);
      margin-top: 1.3em;
    }}
    .report h1:first-child, .report h2:first-child, .report h3:first-child {{ margin-top: 0; }}
    .report p {{ margin: 0.55em 0; }}
    .report pre {{
      overflow: auto;
      padding: 14px;
      border-radius: 12px;
      border: 1px solid var(--voila-border);
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      font-size: 0.95em;
    }}
  </style>
</head>
<body>
  <main>
    <section class="topbar" aria-label="Sumar raport diagnostic OCR Math">
      <div>
        <h1>Raport diagnostic OCR Math</h1>
        <div class="badge">Diagnostic local · read-only</div>
        <p class="muted">Document local: <code>{safe_course_id}</code></p>
        <p class="muted">Această pagină este doar pentru citire. Nu modifică OCR-ul, cursul, Study sau Progress.</p>
        <div class="metrics">
          <div class="metric"><span>Sugestii detectate</span><strong>{total_suggestions}</strong></div>
          <div class="metric"><span>Linii posibil afectate</span><strong>{changed_line_count}</strong></div>
          <div class="metric"><span>Mărime raport</span><strong>{size_bytes}</strong></div>
        </div>
      </div>
      <div class="actions">
        <a class="button" href="{safe_raw_href}">Deschide raw .md</a>
        <a class="button" href="{safe_formula_visual_href}">Formula visual evidence</a>
      </div>
    </section>

    <article class="report" aria-label="Conținut raport OCR Math">
      {rendered_report}
    </article>
  </main>
</body>
</html>
"""
    return HTMLResponse(content=page)


def _voila_ocr_math_report_ui_script_html() -> str:
    return r"""
<script id="voila-ocr-math-report-ui-link-v072">
(function () {
  var rootMarker = "data-voila-ocr-math-report-ui-link-v072";
  if (document.documentElement.hasAttribute(rootMarker)) return;
  document.documentElement.setAttribute(rootMarker, "1");

  function unique(values) {
    var seen = {};
    var out = [];
    values.forEach(function (value) {
      if (!value) return;
      value = String(value).trim();
      if (!value || seen[value]) return;
      seen[value] = true;
      out.push(value);
    });
    return out;
  }

  function idsFromUrl(href) {
    var ids = [];
    try {
      var url = new URL(href, window.location.origin);
      [
        /\/(?:course|courses|library|document|documents|ocr-review|review-ocr|study|progress)\/([^\/?#]+)/i,
        /\/owner\/(?:course|courses|library|document|documents|ocr-review|review-ocr)\/([^\/?#]+)/i
      ].forEach(function (pattern) {
        var match = url.pathname.match(pattern);
        if (match && match[1]) ids.push(decodeURIComponent(match[1]));
      });

      ["course_id", "course", "doc_id", "document_id", "item_id", "id"].forEach(function (key) {
        var value = url.searchParams.get(key);
        if (value) ids.push(value);
      });
    } catch (error) {}
    return unique(ids);
  }

  function formatCount(value) {
    if (value === null || value === undefined || value === "") return "n/a";
    return String(value);
  }

  function reportHref(id) {
    return "/owner/ocr-math-report/" + encodeURIComponent(id) + "/view";
  }

  function hasReportBox(container, id) {
    return Array.prototype.some.call(
      container.querySelectorAll("[data-voila-ocr-math-report-id]"),
      function (node) {
        return node.getAttribute("data-voila-ocr-math-report-id") === id;
      }
    );
  }

  function createMetric(label, value) {
    var item = document.createElement("span");
    item.style.cssText = "display:inline-flex;gap:4px;align-items:baseline;margin:4px 10px 0 0;white-space:nowrap;";
    var name = document.createElement("span");
    name.textContent = label + ":";
    name.style.cssText = "opacity:0.78;";
    var count = document.createElement("strong");
    count.textContent = formatCount(value);
    item.appendChild(name);
    item.appendChild(count);
    return item;
  }

  function renderReportBox(container, id, summary, compact) {
    if (!container || hasReportBox(container, id)) return;

    var box = document.createElement("section");
    box.setAttribute("data-voila-ocr-math-report-id", id);
    box.setAttribute("aria-label", "Raport diagnostic OCR Math disponibil");
    box.style.cssText = [
      "margin:12px 0",
      "padding:14px",
      "border:1px solid rgba(31,78,121,0.35)",
      "border-radius:14px",
      "background:rgba(31,78,121,0.06)",
      "display:flex",
      "gap:12px",
      "align-items:flex-start",
      "justify-content:space-between",
      "flex-wrap:wrap"
    ].join(";");

    var content = document.createElement("div");
    content.style.cssText = "min-width:220px;flex:1 1 260px;";

    var topRow = document.createElement("div");
    topRow.style.cssText = "display:flex;gap:8px;align-items:center;flex-wrap:wrap;";

    var title = document.createElement("strong");
    title.textContent = "Raport diagnostic OCR Math disponibil";

    var badge = document.createElement("span");
    badge.textContent = "Diagnostic local";
    badge.style.cssText = [
      "font-size:0.78em",
      "line-height:1",
      "padding:4px 7px",
      "border:1px solid rgba(31,78,121,0.35)",
      "border-radius:999px",
      "opacity:0.86"
    ].join(";");

    topRow.appendChild(title);
    topRow.appendChild(badge);
    content.appendChild(topRow);

    var helper = document.createElement("div");
    helper.textContent = "Raportul este doar informativ. Nu modifică OCR-ul, cursul, Study sau Progress.";
    helper.style.cssText = "font-size:0.9em;opacity:0.78;margin-top:5px;";
    content.appendChild(helper);

    var metrics = document.createElement("div");
    metrics.style.cssText = "font-size:0.92em;margin-top:7px;";
    metrics.appendChild(createMetric("Sugestii detectate", summary.total_suggestions));
    metrics.appendChild(createMetric("Linii posibil afectate", summary.changed_line_count));
    content.appendChild(metrics);

    var link = document.createElement("a");
    link.href = reportHref(id);
    link.textContent = compact ? "Deschide raportul" : "Deschide raportul OCR Math";
    link.style.cssText = [
      "align-self:center",
      "padding:8px 11px",
      "border:1px solid currentColor",
      "border-radius:10px",
      "text-decoration:none",
      "font-weight:600",
      "white-space:nowrap"
    ].join(";");

    box.appendChild(content);
    box.appendChild(link);
    container.appendChild(box);
  }

  async function fetchSummary(id) {
    try {
      var response = await fetch(
        "/owner/ocr-math-report/" + encodeURIComponent(id) + "/summary.json",
        { headers: { "Accept": "application/json" } }
      );
      if (!response.ok) return null;
      var summary = await response.json();
      return summary && summary.exists ? summary : null;
    } catch (error) {
      return null;
    }
  }

  async function addForCurrentPage() {
    var ids = idsFromUrl(window.location.href).slice(0, 3);
    if (!ids.length) return;
    var target =
      document.querySelector(".course-tools, [data-testid='course-tools'], .ocr-review, [data-testid='ocr-review']") ||
      document.querySelector("main") ||
      document.body;

    for (var i = 0; i < ids.length; i++) {
      var summary = await fetchSummary(ids[i]);
      if (summary) renderReportBox(target, ids[i], summary, false);
    }
  }

  async function addForCards() {
    var pairs = [];
    Array.prototype.forEach.call(document.querySelectorAll("[data-course-id], [data-document-id], [data-doc-id]"), function (node) {
      var id = node.getAttribute("data-course-id") || node.getAttribute("data-document-id") || node.getAttribute("data-doc-id");
      if (id) pairs.push({ id: id, host: node });
    });

    Array.prototype.forEach.call(document.querySelectorAll("a[href]"), function (link) {
      idsFromUrl(link.href).forEach(function (id) {
        var host = link.closest("article, .card, .course-card, .library-card, li, section") || link.parentElement;
        pairs.push({ id: id, host: host });
      });
    });

    var seen = {};
    pairs = pairs.filter(function (pair) {
      var key = pair.id + "::" + (pair.host ? Array.prototype.indexOf.call(document.querySelectorAll("*"), pair.host) : "none");
      if (seen[key]) return false;
      seen[key] = true;
      return true;
    }).slice(0, 20);

    for (var i = 0; i < pairs.length; i++) {
      var summary = await fetchSummary(pairs[i].id);
      if (summary) renderReportBox(pairs[i].host, pairs[i].id, summary, true);
    }
  }

  function run() {
    addForCurrentPage();
    addForCards();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
</script>
"""



def _voila_tester_flow_bottom_nav_html() -> str:
    return r"""
<style id="voila-tester-flow-bottom-nav-v0724-style">
  .voila-tester-flow-bottom-nav {
    position: fixed;
    left: 50%;
    right: auto;
    bottom: calc(14px + env(safe-area-inset-bottom));
    transform: translateX(-50%);
    z-index: 99999;
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    max-width: min(980px, calc(100vw - 24px));
    padding: 10px 12px;
    border-radius: 22px;
    border: 1px solid rgba(31, 78, 121, 0.35);
    background: rgba(245, 236, 217, 0.94);
    box-shadow: 0 16px 44px rgba(0, 0, 0, 0.22);
    backdrop-filter: blur(12px);
    font-family: "Segoe UI", Arial, sans-serif;
  }
  .voila-tester-flow-bottom-nav a,
  .voila-tester-flow-bottom-nav button {
    border: 1px solid rgba(31, 78, 121, 0.42);
    background: rgba(255, 255, 255, 0.64);
    color: #1F4E79;
    border-radius: 999px;
    padding: 8px 11px;
    text-decoration: none;
    font-size: 13px;
    font-weight: 750;
    cursor: pointer;
  }
  .voila-tester-flow-bottom-nav a.primary {
    background: #1F4E79;
    color: #fff;
  }
  body.voila-has-tester-flow-bottom-nav {
    padding-bottom: 168px !important;
  }
  @media (prefers-color-scheme: dark) {
    .voila-tester-flow-bottom-nav {
      background: rgba(24, 32, 36, 0.94);
      border-color: rgba(215, 168, 110, 0.34);
    }
    .voila-tester-flow-bottom-nav a,
    .voila-tester-flow-bottom-nav button {
      background: rgba(255, 255, 255, 0.08);
      color: #f0c98d;
      border-color: rgba(240, 201, 141, 0.32);
    }
    .voila-tester-flow-bottom-nav a.primary {
      background: #d7a86e;
      color: #141414;
    }
  }
</style>
<script id="voila-tester-flow-bottom-nav-v0724">
(function () {
  if (document.getElementById("voilaTesterFlowBottomNav")) return;

  var params = new URLSearchParams(window.location.search);
  var pdf = params.get("pdf") || "";
  var outputMatch = window.location.pathname.match(/\/output\/([^\/]+)\/course\.cleaned\.html/i);

  if (!pdf && outputMatch && outputMatch[1]) {
    try {
      pdf = decodeURIComponent(outputMatch[1]) + ".pdf";
    } catch (_) {
      pdf = outputMatch[1] + ".pdf";
    }
  }

  function enc(value) {
    return encodeURIComponent(value || "");
  }

  function addLink(nav, label, href, primary) {
    if (!href) return;
    var a = document.createElement("a");
    a.textContent = label;
    a.href = href;
    if (primary) a.className = "primary";
    nav.appendChild(a);
  }

  var nav = document.createElement("nav");
  nav.id = "voilaTesterFlowBottomNav";
  nav.className = "voila-tester-flow-bottom-nav";
  nav.setAttribute("aria-label", "Voila tester flow bottom navigation");

  addLink(nav, "Bibliotecă", "/", true);

  if (pdf) {
    var q = enc(pdf);
    addLink(nav, "Instrumente curs", "/course-tools?pdf=" + q, false);
    addLink(nav, "Deschide cursul", "/course-open?pdf=" + q, false);
    addLink(nav, "Studiu", "/study?pdf=" + q, false);
    addLink(nav, "Progres", "/progress?pdf=" + q, false);
    addLink(nav, "OCR Review", "/review-ocr-corrected?pdf=" + q + "&page=1", false);

    var courseId = pdf.replace(/\.pdf$/i, "");
    addLink(nav, "OCR Math", "/owner/ocr-math-report/" + enc(courseId) + "/view", false);
  }

  addLink(nav, "Exam Prep", "/exam-prep", false);

  var topButton = document.createElement("button");
  topButton.type = "button";
  topButton.textContent = "↑ Sus";
  topButton.addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
  nav.appendChild(topButton);

  document.body.appendChild(nav);
  document.body.classList.add("voila-has-tester-flow-bottom-nav");
})();
</script>
"""


@app.middleware("http")
async def _voila_ocr_math_report_ui_link_middleware(request, call_next):
    response = await call_next(request)
    content_type = response.headers.get("content-type", "").lower()
    if "text/html" not in content_type:
        return response

    body_chunks = []
    async for chunk in response.body_iterator:
        body_chunks.append(chunk)
    body = b"".join(body_chunks)

    try:
        html_text = body.decode("utf-8")
    except UnicodeDecodeError:
        headers = dict(response.headers)
        headers.pop("content-length", None)
        return Response(content=body, status_code=response.status_code, headers=headers, media_type=response.media_type)

    marker = "voila-ocr-math-report-ui-link-v072"
    if marker not in html_text:
        script = _voila_ocr_math_report_ui_script_html()
        if "</body>" in html_text:
            html_text = html_text.replace("</body>", script + "\n</body>", 1)
        else:
            html_text = html_text + script

    path_lower = str(getattr(request.url, "path", "") or "").lower()
    skip_tester_flow_bottom_nav = path_lower in {
        "/review-ocr-corrected",
        "/review-ocr-text",
    }
    bottom_nav_marker = "voila-tester-flow-bottom-nav-v0724"
    if (
        not skip_tester_flow_bottom_nav
        and bottom_nav_marker not in html_text
        and "appFixedNav" not in html_text
    ):
        bottom_nav = _voila_tester_flow_bottom_nav_html()
        if "</body>" in html_text:
            html_text = html_text.replace("</body>", bottom_nav + "\n</body>", 1)
        else:
            html_text = html_text + bottom_nav

    headers = dict(response.headers)
    headers.pop("content-length", None)
    headers.pop("content-encoding", None)
    return HTMLResponse(content=html_text, status_code=response.status_code, headers=headers)

# VOILA_V0_7_1_OWNER_LOCAL_OCR_MATH_REPORT_UI_LINK_END
# VOILA_V0_7_2_OWNER_LOCAL_OCR_MATH_REPORT_UX_POLISH_APPLIED
# VOILA_V0_7_3_OWNER_LOCAL_OCR_MATH_REPORT_VIEWER_PAGE_APPLIED
# VOILA_V0_7_5_OWNER_LOCAL_OCR_MATH_REPORT_SYNTAX_AND_SMOKE_IMPORT_MOVE_APPLIED


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
    # VOILA_V0_7_84_STUDY_ITEMS_PREVIEW_DISPLAY_GUARD_START
    if isinstance(question, dict) and question.get("source_artifact") == "study_items.preview.json":
        return _study_question_display(str(question.get("question") or ""))
    # VOILA_V0_7_84_STUDY_ITEMS_PREVIEW_DISPLAY_GUARD_END

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
      <a class="primary" href="/">{_ut("ui.library", _ut("library", "Library"))}</a>
      <a id="fixedCourseToolsLink" href="/" hidden>{_ut("ui.course_tools", "Course Tools")}</a>
      <a id="fixedCourseOpenLink" href="/" hidden>{_ut("ui.open_course", _ut("open_course", "Open course"))}</a>
      <a id="fixedStudyLink" href="/" hidden>{_ut("ui.study", _ut("study", "Study"))}</a>
      <a id="fixedReviewLink" href="/" hidden>{_ut("ui.review_weak", "Review due")}</a>
      <a id="fixedOcrReviewLink" href="/" hidden>{_ut("ui.review_ocr_text", "OCR Review")}</a>
      <a id="fixedProgressLink" href="/" hidden>{_ut("ui.progress", _ut("progress", "Progress"))}</a>
      <a id="fixedExamPrepLink" href="/exam-prep">{_ut("ui.exam_prep", "Exam Prep")}</a>
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
        const courseToolsLink = document.getElementById("fixedCourseToolsLink");
        const courseOpenLink = document.getElementById("fixedCourseOpenLink");
        const ocrReviewLink = document.getElementById("fixedOcrReviewLink");
        const resetButton = document.getElementById("fixedResetButton");

        if (pdf) {{
          const encodedPdf = encodeURIComponent(pdf);

          if (courseToolsLink && path !== "/course-tools") {{
            courseToolsLink.href = "/course-tools?pdf=" + encodedPdf;
            courseToolsLink.hidden = false;
          }}

          if (courseOpenLink && path !== "/course-open") {{
            courseOpenLink.href = "/course-open?pdf=" + encodedPdf;
            courseOpenLink.hidden = false;
          }}

          if (ocrReviewLink && path !== "/review-ocr-corrected") {{
            ocrReviewLink.href = "/review-ocr-corrected?pdf=" + encodedPdf + "&page=1";
            ocrReviewLink.hidden = false;
          }}


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


# VOILA_V0_7_31_SAFE_UPLOAD_NAME_ONLY_START
def safe_upload_name(name: str) -> str:
    # Return a stable local PDF filename without fragile regex ranges.
    import re as _voila_v0731_re
    import unicodedata as _voila_v0731_unicodedata
    from pathlib import Path as _VoilaV0731Path

    raw = str(name or "document.pdf").replace("\\", "/").rsplit("/", 1)[-1]
    parsed = _VoilaV0731Path(raw)
    stem = parsed.stem or "document"
    suffix = parsed.suffix.lower()

    if suffix != ".pdf":
        suffix = ".pdf"

    folded = _voila_v0731_unicodedata.normalize("NFKD", stem)
    folded = folded.encode("ascii", "ignore").decode("ascii")
    folded = _voila_v0731_re.sub(r"[^A-Za-z0-9._ -]+", "_", folded)
    folded = _voila_v0731_re.sub(r"\s+", " ", folded).strip(" ._")
    folded = _voila_v0731_re.sub(r"_+", "_", folded)

    if not folded:
        folded = "document"

    return folded[:120] + suffix
# VOILA_V0_7_31_SAFE_UPLOAD_NAME_ONLY_END
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
    <style id="voila-v0735-exam-prep-contrast-only">.exam-prep-contrast-v0735 .card{{background:rgba(255,255,255,.96)!important;color:#172033!important;border-color:rgba(23,32,51,.18)!important;box-shadow:0 12px 34px rgba(23,32,51,.10)!important}}.exam-prep-contrast-v0735 .card h2,.exam-prep-contrast-v0735 .card p,.exam-prep-contrast-v0735 .card .meta,.exam-prep-contrast-v0735 .card strong{{color:#172033!important}}.exam-prep-contrast-v0735 .notice{{background:rgba(255,255,255,.94)!important;color:#172033!important;border-color:rgba(23,32,51,.16)!important}}</style>
    <section class="exam-prep-contrast-v0735"><h1>{_ut("ui.exam_prep_title", "Voila! Exam Prep")}</h1>

    <div class="notice">
      <strong>{_ut("exam_prep.bac_matematica_m1", "Baccalaureate → Mathematics M1")}</strong><br>
      {_ut("exam_prep.foundation_description", "Foundation dashboard for skill-based exam preparation. Progress is updated from Study Mode.")}
    </div>

    <section class="grid">
      {''.join(rows)}
    </section>

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
        course_md = out_dir / "course.cleaned.md"
        course_generated = course_html.exists() or course_md.exists()
        course_html_pending = course_md.exists() and not course_html.exists()
        figures_html = out_dir / "figures" / "figures.html"
        hybrid_figures_html = out_dir / "figures_hybrid" / "figures_hybrid.html"
        hybrid_manifest = out_dir / "figures_hybrid" / "figures_manifest.hybrid.json"
        log_file = out_dir / "last_run.log"
        quiz_file = out_dir / "quiz.json"

        size_mb = pdf.stat().st_size / (1024 * 1024)

        if course_html.exists():
            status = f'<span class="status">{_ut("ui.generated", "Generated")}</span>'
        elif course_md.exists():
            status = f'<span class="status">{_ut("ui.generated_markdown_html_pending", "Generated · HTML pending")}</span>'
        else:
            status = f'<span class="status missing">{_ut("status.not_generated_yet", "Not generated yet")}</span>'

        generate_label = (
            _ut("ui.regenerate_course", "Regenerate course")
            if course_generated
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

        if course_generated:
            actions.append(
                f'<a class="btn" href="/course-open?pdf={quote(pdf.name)}">{_ut("ui.open_course", _ut("open_course", "Open course"))}</a>'
            )
            actions.append(
                f'<a class="btn" href="/course-tools?pdf={quote(pdf.name)}">{_ut("ui.course_tools", "Course Tools")}</a>'
            )
            if course_html_pending:
                actions.append(
                    f'<span class="meta">{_ut("ui.html_will_be_rebuilt_on_open", "HTML will be rebuilt automatically when opened.")}</span>'
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





# VOILA_V0_7_77_OWNER_LOCAL_GENERATE_INTEGRATION_FROM_READINESS_GATED_LEARNING_PACK_START
# Owner-local /generate integration from readiness-gated document learning pack.
# Policy: use local document_learning_pack.json only when generate_readiness_gate.json is PASS.
# No build, no ZIP, no share, no delivery, no distribution.

def _voila_v0777_load_json(path: Path) -> dict:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _voila_v0777_ready_learning_pack_for_generate(output_dir: Path) -> Path | None:
    pack_path = Path(output_dir) / "document_learning_pack.json"
    gate_path = Path(output_dir) / "generate_readiness_gate.json"

    if not pack_path.is_file() or not gate_path.is_file():
        return None

    pack = _voila_v0777_load_json(pack_path)
    gate = _voila_v0777_load_json(gate_path)

    pack_gate = pack.get("quality_gate") if isinstance(pack.get("quality_gate"), dict) else {}
    gate_quality = gate.get("quality_gate") if isinstance(gate.get("quality_gate"), dict) else {}
    gate_policy = gate.get("policy") if isinstance(gate.get("policy"), dict) else {}

    if gate.get("artifact") != "owner_local_generate_readiness_gate":
        return None
    if gate.get("artifact_version") != "v0.7.76":
        return None
    if gate.get("generate_readiness_status") != "PASS":
        return None
    if gate.get("ready_for_separate_generate_integration_milestone") is not True:
        return None
    if pack.get("artifact") != "document_learning_pack":
        return None
    if pack.get("rebuild_artifact_version") != "v0.7.75":
        return None
    if pack.get("document_learning_pack_rebuilt_from_applied_ocr_review") is not True:
        return None
    if pack_gate.get("document_learning_status") != "PASS":
        return None
    if pack_gate.get("generation_allowed") is not True:
        return None
    if int(pack_gate.get("verified_user_evidence_count") or 0) <= 0:
        return None
    if gate_quality.get("generate_integration_changed") is not False:
        return None
    if gate_quality.get("course_regeneration_performed") is not False:
        return None
    if gate_policy.get("build_performed") is not False:
        return None
    if gate_policy.get("zip_created") is not False:
        return None
    if gate_policy.get("delivery_performed") is not False:
        return None

    return pack_path


def _voila_v0777_write_generate_integration_report(output_dir: Path, learning_pack_path: Path | None) -> None:
    report = {
        "artifact": "owner_local_generate_integration_from_readiness_gated_learning_pack",
        "artifact_version": "v0.7.77",
        "learning_pack_used": learning_pack_path is not None,
        "learning_pack_path": str(learning_pack_path or ""),
        "generate_readiness_gate_required": True,
        "generate_integration_changed": True,
        "generator_route_changed": True,
        "course_regeneration_performed": True,
        "build_performed": False,
        "zip_created": False,
        "share_created": False,
        "delivery_performed": False,
        "distribution_performed": False,
        "tester_readiness": "BROWSER_SMOKE_REQUIRED",
    }
    target = Path(output_dir) / "generate_integration_report.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# VOILA_V0_7_77_OWNER_LOCAL_GENERATE_INTEGRATION_FROM_READINESS_GATED_LEARNING_PACK_END


# VOILA_V0_7_17C_GENERATE_FOR_PDF_ENTRYPOINT
def generate_for_pdf(pdf_path: Path) -> Path:
    """Run the existing local PDF-to-course pipeline used by /generate.

    This restores the entrypoint that the existing /generate route already calls.
    It intentionally runs the concrete local scripts that are already present in
    services/api instead of using a generic dynamic shim.
    """

    import subprocess
    import sys
    from pathlib import Path as _VoilaPath

    source_pdf = _VoilaPath(pdf_path)
    if not source_pdf.is_absolute():
        source_pdf = (_VoilaPath(PROJECT_ROOT) / source_pdf).resolve()
    if not source_pdf.exists():
        raise FileNotFoundError(f"PDF not found: {source_pdf}")

    api_dir = _VoilaPath(__file__).resolve().parent
    output_root = OUTPUT_DIR
    output_dir = output_root / source_pdf.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    learning_pack_path = _voila_v0777_ready_learning_pack_for_generate(output_dir)
    _voila_v0777_write_generate_integration_report(output_dir, learning_pack_path)

    steps = [
        (
            "extract pages",
            [
                sys.executable,
                str(api_dir / "pdf_extract.py"),
                str(source_pdf),
                "--output-dir",
                str(output_root),
            ],
        ),
        (
            "build OCR Math report if enabled",
            [
                sys.executable,
                str(api_dir / "ocr_math_report_hook.py"),
                "--output-folder",
                str(output_dir),
                "--pdf-name",
                source_pdf.name,
            ] + (
                ["--enable"]
                if __import__("os").environ.get("VOILA_ENABLE_OCR_MATH_REPORT_HOOK", "").strip().lower()
                in {"1", "true", "yes", "on"}
                else []
            ) + [
                "--reason",
                "v0.7.78-generate-for-pdf",
            ],
        ),
        (
            "build outline",
            [
                sys.executable,
                str(api_dir / "outline_builder.py"),
                str(output_dir / "pages.json"),
            ],
        ),
        (
            "normalize outline",
            [
                sys.executable,
                str(api_dir / "normalize_outline.py"),
                str(output_dir / "course_outline.json"),
            ],
        ),
        (
            "generate course assets",
            [
                sys.executable,
                str(api_dir / "course_generator.py"),
                str(output_dir / "course_outline.normalized.json"),
            ] + (
                ["--learning-pack-json", str(learning_pack_path)]
                if learning_pack_path is not None
                else []
            ),
        ),
        (
            "polish course",
            [
                sys.executable,
                str(api_dir / "course_polisher.py"),
                str(output_dir / "course_outline.normalized.json"),
            ] + (
                ["--learning-pack-json", str(learning_pack_path)]
                if learning_pack_path is not None
                else []
            ),
        ),
    ]

    for label, command in steps:
        completed = subprocess.run(
            command,
            cwd=str(api_dir),
            text=True,
            capture_output=True,
        )

        if completed.returncode != 0:
            stdout = (completed.stdout or "").strip()
            stderr = (completed.stderr or "").strip()
            detail = "\n".join(
                part
                for part in [
                    f"Voila generate step failed: {label}",
                    f"Command: {' '.join(command)}",
                    f"Exit code: {completed.returncode}",
                    f"stdout:\n{stdout}" if stdout else "",
                    f"stderr:\n{stderr}" if stderr else "",
                ]
                if part
            )
            raise RuntimeError(detail)

    if learning_pack_path is not None:
        stale_course_html = output_dir / "course.cleaned.html"
        if stale_course_html.exists():
            stale_course_html.unlink()

    ensure_course_html_for_pdf(source_pdf)

    return output_dir


def ensure_course_html_for_pdf(pdf_path: Path) -> Path:
    """Ensure a generated course has course.cleaned.html.

    v0.7.24 tester UI reality fix:
    - /generate must not stop at course.cleaned.md only.
    - Existing extracted-package courses with course.cleaned.md can be opened safely.
    - HTML export/navigation failures are surfaced instead of hidden.
    """

    source_pdf = Path(pdf_path)
    output_dir = OUTPUT_DIR / source_pdf.stem
    course_md = output_dir / "course.cleaned.md"
    course_html = output_dir / "course.cleaned.html"

    if course_html.exists():
        return course_html

    if not course_md.exists():
        raise FileNotFoundError(f"course.cleaned.md not found: {course_md}")

    api_dir = Path(__file__).resolve().parent
    steps = [
        (
            "export course html",
            [
                sys.executable,
                str(api_dir / "html_exporter.py"),
                str(course_md),
            ],
        ),
        (
            "inject course navigation",
            [
                sys.executable,
                str(api_dir / "course_nav_injector.py"),
                str(course_html),
                source_pdf.name,
            ],
        ),
    ]

    for label, command in steps:
        completed = subprocess.run(
            command,
            cwd=str(api_dir),
            text=True,
            capture_output=True,
        )

        if completed.returncode != 0:
            stdout = (completed.stdout or "").strip()
            stderr = (completed.stderr or "").strip()
            detail = "\n".join(
                part
                for part in [
                    f"Voila course HTML step failed: {label}",
                    f"Command: {' '.join(command)}",
                    f"Exit code: {completed.returncode}",
                    f"stdout:\n{stdout}" if stdout else "",
                    f"stderr:\n{stderr}" if stderr else "",
                ]
                if part
            )
            raise RuntimeError(detail)

    if not course_html.exists():
        raise RuntimeError(f"course.cleaned.html was not created: {course_html}")

    return course_html

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


@app.get("/course-open")
def course_open(pdf: str = Query(...)):
    pdf_path = validate_pdf_name(pdf)

    try:
        ensure_course_html_for_pdf(pdf_path)
    except Exception as exc:
        body = f"""
        <h1>{_ut("ui.course_unavailable", "Course unavailable")}</h1>
        <div class="notice">
          {_ut("ui.course_html_rebuild_failed", "The course Markdown exists, but Voila could not rebuild/open the HTML course.")}
        </div>
        <p>PDF: <strong>{html.escape(pdf_path.name)}</strong></p>
        <p>Error: <code>{html.escape(str(exc))}</code></p>
        <div class="actions">
          <a class="btn" href="/">{_ut("ui.library", _ut("library", "Library"))}</a>
          <a class="btn" href="/course-tools?pdf={quote(pdf_path.name)}">{_ut("ui.course_tools", "Course Tools")}</a>
        </div>
        """
        return page("Voila! Course unavailable", body)

    return RedirectResponse(
        url=output_url(pdf_path.stem, "course.cleaned.html"),
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
          {_ut("study.concept_mastery_changed", "Nivelul conceptului s-a schimbat de la")} <strong>{before}%</strong> {_ut("to", "to")} <strong>{after}%</strong>.
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
        recommendation_reason = html.escape(_voila_v080_study_recommendation_reason_label(str(current.get("recommendation_reason") or "")))

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



# VOILA_V0_7_80_STUDY_UX_REASON_LABEL_START
# Display-only Study UX labels.
# Policy: no question generation, no BKT, no Study state, no Progress logic changes.
def _voila_v080_study_recommendation_reason_label(raw: str) -> str:
    label = _study_recommendation_reason_label(str(raw or ""))
    replacements = {
        "concept nou": "Concept nou",
        "new concept": "Concept nou",
        "legacy short answer": "răspuns scurt",
        "legacy_short_answer": "răspuns scurt",
        "concept_understanding": "înțelegere concept",
        "concept understanding": "înțelegere concept",
        "conditions_check": "verificare condiții",
        "conditions check": "verificare condiții",
        "distinction": "diferențiere",
        "true_false": "adevărat/fals",
        "true false": "adevărat/fals",
        "why_it_matters": "de ce contează",
        "why it matters": "de ce contează",
        "apply_or_check": "aplicare/verificare",
        "apply or check": "aplicare/verificare",
    }
    for old, new in replacements.items():
        label = label.replace(old, new)
    return label
# VOILA_V0_7_80_STUDY_UX_REASON_LABEL_END



# VOILA_V0_7_82_STUDY_ITEMS_PREVIEW_VIEWER_START

def _voila_v082_study_items_preview_path(course_id: str):
    from pathlib import Path as _Path
    return _Path(__file__).resolve().parents[2] / "data" / "output" / course_id / "study_items.preview.json"


def _voila_v082_escape(value) -> str:
    import html as _html
    return _html.escape(str(value or ""))


# VOILA_V0_7_85_STUDY_ITEMS_PREVIEW_LABEL_POLISH_START
def _voila_v085_study_item_question_type_label(value) -> str:
    labels = {
        "concept_understanding": "înțelegere concept",
        "concept understanding": "înțelegere concept",
        "conditions_check": "verificare condiții",
        "conditions check": "verificare condiții",
        "distinction": "diferențiere",
        "true_false": "adevărat/fals",
        "true false": "adevărat/fals",
        "why_it_matters": "de ce contează",
        "why it matters": "de ce contează",
        "apply_or_check": "aplicare/verificare",
        "apply or check": "aplicare/verificare",
        "learning_pack_preview": "întrebare pedagogică",
        "learning pack preview": "întrebare pedagogică",
        "technical_fact": "fapt tehnic",
        "technical fact": "fapt tehnic",
        "legacy_short_answer": "răspuns scurt",
        "legacy short answer": "răspuns scurt",
    }
    raw = str(value or "").strip()
    return labels.get(raw, raw.replace("_", " "))
# VOILA_V0_7_85_STUDY_ITEMS_PREVIEW_LABEL_POLISH_END


@app.get("/owner/study-items-preview/{course_id}/view", response_class=HTMLResponse)
def owner_study_items_preview_view(course_id: str):
    import json as _json
    import re as _re

    if not _re.fullmatch(r"[A-Za-z0-9_.-]+", str(course_id or "")):
        body = "<main class=\"card\"><h1>Previzualizare Study items</h1><p>Course id invalid.</p></main>"
        return HTMLResponse(content=page("Voila! Study items preview", body), status_code=400)

    preview_path = _voila_v082_study_items_preview_path(course_id)

    if not preview_path.exists():
        body = f"""
        <main class="card">
          <h1>Previzualizare Study items</h1>
          <p>Nu există <code>study_items.preview.json</code> pentru cursul <strong>{_voila_v082_escape(course_id)}</strong>.</p>
          <p>Rulează generatorul preview înainte de vizualizare.</p>
        </main>
        """
        return HTMLResponse(content=page("Voila! Study items preview", body), status_code=404)

    preview = _json.loads(preview_path.read_text(encoding="utf-8"))
    items = preview.get("items") if isinstance(preview.get("items"), list) else []
    gate = preview.get("quality_gate") if isinstance(preview.get("quality_gate"), dict) else {}
    policy = preview.get("policy") if isinstance(preview.get("policy"), dict) else {}

    cards = []
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict):
            continue

        pages = item.get("source_pdf_pages") or []
        if isinstance(pages, list):
            pages_label = ", ".join(str(x) for x in pages) or "—"
        else:
            pages_label = _voila_v082_escape(pages) or "—"

        cards.append(f"""
        <article class="card v0782-study-item-card">
          <div class="meta">
            #{index} · {_voila_v082_escape(item.get("concept_id"))}
            · {_voila_v082_escape(item.get("term"))}
            · {_voila_v082_escape(_voila_v085_study_item_question_type_label(item.get("question_type")))}
            · pagini sursă: {_voila_v082_escape(pages_label)}
          </div>
          <h2>{_voila_v082_escape(item.get("question"))}</h2>
          <p><strong>Răspuns așteptat:</strong> {_voila_v082_escape(item.get("expected_answer"))}</p>
          <p><strong>Indiciu:</strong> {_voila_v082_escape(item.get("hint"))}</p>
          <p><strong>Explicație:</strong> {_voila_v082_escape(item.get("explanation"))}</p>
        </article>
        """)

    item_count = preview.get("item_count", len(items))
    concept_count = preview.get("concept_count", "—")
    quality_status = gate.get("preview_quality_status", "—")
    # VOILA_V0_7_86_STUDY_ITEMS_PREVIEW_STATUS_COPY_POLISH_START
    quality_status_normalized = str(quality_status or "").strip().upper()
    if quality_status_normalized == "PASS":
        study_status_copy = "Owner-local · read-only · integrat în Study când Quality gate este PASS"
        study_integration_badge = "activă"
    else:
        study_status_copy = "Owner-local · read-only · neintegrat în Study: Quality gate nu este PASS"
        study_integration_badge = "inactivă"
    # VOILA_V0_7_86_STUDY_ITEMS_PREVIEW_STATUS_COPY_POLISH_END

    body = f"""
    <style id="voila-v0782-study-items-preview-viewer-style">
      .v0782-study-preview-summary {{
        display: grid;
        gap: 12px;
      }}
      .v0782-study-preview-badges {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
      }}
      .v0782-study-preview-badges span {{
        border: 1px solid rgba(148, 163, 184, 0.35);
        border-radius: 999px;
        padding: 6px 10px;
        background: rgba(15, 23, 42, 0.35);
      }}
      .v0782-study-preview-grid {{
        display: grid;
        gap: 14px;
        margin-top: 16px;
      }}
      .v0782-study-item-card h2 {{
        margin-top: 8px;
      }}
      .v0782-study-item-card p {{
        margin: 8px 0;
      }}
    </style>

    <main>
      <section class="card v0782-study-preview-summary">
        <h1>Previzualizare Study items</h1>
        <p class="meta">{_voila_v082_escape(study_status_copy)}</p>
        <p><code>study_items.preview.json</code></p>

        <div class="v0782-study-preview-badges">
          <span>Itemuri: <strong>{_voila_v082_escape(item_count)}</strong></span>
          <span>Concepte: <strong>{_voila_v082_escape(concept_count)}</strong></span>
          <span>Quality gate: <strong>{_voila_v082_escape(quality_status)}</strong></span>
          <span>LLM: <strong>{_voila_v082_escape(uses_llm_label)}</strong></span>
          <span>Cloud: <strong>{_voila_v082_escape(uses_cloud_label)}</strong></span>
          <span>Study integration: <strong>{_voila_v082_escape(study_integration_badge)}</strong></span>
        </div>
      </section>

      <section class="v0782-study-preview-grid">
        {''.join(cards)}
      </section>
    </main>
    """

    return page("Voila! Study items preview", body)


# VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_VIEWER_START

def _voila_v090_formula_visual_manifest_path(course_id: str):
    from pathlib import Path as _Path
    return _Path(__file__).resolve().parents[2] / "data" / "output" / course_id / "formula_visual_evidence.manifest.json"


def _voila_v090_formula_visual_evidence_dir(course_id: str):
    from pathlib import Path as _Path
    return _Path(__file__).resolve().parents[2] / "data" / "output" / course_id / "formula_visual_evidence"


def _voila_v090_validate_course_id(course_id: str) -> str:
    import re as _re
    safe_course_id = str(course_id or "").strip()
    if not _re.fullmatch(r"[A-Za-z0-9_.-]+", safe_course_id):
        raise ValueError("invalid course id")
    return safe_course_id


@app.get("/owner/formula-visual-evidence/{course_id}/asset", include_in_schema=False)
def owner_formula_visual_evidence_asset(course_id: str, candidate_id: str):
    # VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_SAFE_ASSET_START
    # Security policy: do not build a filesystem path directly from a user-provided path.
    # The request provides only a strict candidate id. The crop path is resolved from the
    # owner-local manifest and then constrained to the formula_visual_evidence directory.
    import json as _json
    import re as _re
    from fastapi.responses import FileResponse as _FileResponse

    try:
        safe_course_id = _voila_v090_validate_course_id(course_id)
    except ValueError:
        return HTMLResponse(content="Invalid course id.", status_code=400)

    safe_candidate_id = str(candidate_id or "").strip()
    if not _re.fullmatch(r"p[0-9]{3}-c[0-9]{3}", safe_candidate_id):
        return HTMLResponse(content="Invalid candidate id.", status_code=400)

    manifest_path = _voila_v090_formula_visual_manifest_path(safe_course_id)
    if not manifest_path.exists():
        return HTMLResponse(content="Manifest not found.", status_code=404)

    manifest = _json.loads(manifest_path.read_text(encoding="utf-8"))
    candidates = manifest.get("candidates") if isinstance(manifest.get("candidates"), list) else []

    crop_path = ""
    for item in candidates:
        if isinstance(item, dict) and str(item.get("id") or "") == safe_candidate_id:
            crop_path = str(item.get("crop_path") or "")
            break

    if not crop_path:
        return HTMLResponse(content="Candidate not found.", status_code=404)

    if not crop_path.startswith("formula_visual_evidence/crops/"):
        return HTMLResponse(content="Invalid manifest crop scope.", status_code=400)

    filename = crop_path.rsplit("/", 1)[-1]
    if not _re.fullmatch(r"page-[0-9]{3}-candidate-[0-9]{3}\.png", filename):
        return HTMLResponse(content="Invalid manifest crop filename.", status_code=400)

    base = _voila_v090_formula_visual_evidence_dir(safe_course_id).resolve()
    target = (base / "crops" / filename).resolve()

    try:
        target.relative_to(base / "crops")
    except ValueError:
        return HTMLResponse(content="Invalid asset scope.", status_code=400)

    if not target.exists() or not target.is_file():
        return HTMLResponse(content="Asset not found.", status_code=404)

    return _FileResponse(str(target))
    # VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_SAFE_ASSET_END


@app.get("/owner/formula-visual-evidence/{course_id}/view", response_class=HTMLResponse)
def owner_formula_visual_evidence_view(course_id: str):
    import json as _json
    from urllib.parse import quote as _quote

    try:
        safe_course_id = _voila_v090_validate_course_id(course_id)
    except ValueError:
        body = "<main class=\"card\"><h1>Formula visual evidence</h1><p>Course id invalid.</p></main>"
        return HTMLResponse(content=page("Voila! Formula visual evidence", body), status_code=400)

    manifest_path = _voila_v090_formula_visual_manifest_path(safe_course_id)
    if not manifest_path.exists():
        body = f"""
        <main class="card">
          <h1>Formula visual evidence</h1>
          <p>Nu există <code>formula_visual_evidence.manifest.json</code> pentru cursul <strong>{_voila_v082_escape(safe_course_id)}</strong>.</p>
          <p>Rulează <code>scripts/dev/build-formula-visual-evidence-manifest.py</code> pentru acest curs.</p>
        </main>
        """
        return HTMLResponse(content=page("Voila! Formula visual evidence", body), status_code=404)

    manifest = _json.loads(manifest_path.read_text(encoding="utf-8"))
    candidates = manifest.get("candidates") if isinstance(manifest.get("candidates"), list) else []
    # VOILA_V0_7_92_FORMULA_VISUAL_EVIDENCE_VIEWER_SORT_START
    def _v0792_quality_rank(item):
        tier = str((item or {}).get("quality_tier") or "low")
        tier_rank = {"high": 0, "medium": 1, "low": 2}.get(tier, 2)
        score = int((item or {}).get("quality_score") or 0)
        return (tier_rank, -score, str((item or {}).get("id") or ""))

    display_candidates = sorted(candidates, key=_v0792_quality_rank)
    quality_counts = manifest.get("quality_counts") if isinstance(manifest.get("quality_counts"), dict) else {}
    high_count = int(quality_counts.get("high") or 0)
    medium_count = int(quality_counts.get("medium") or 0)
    low_count = int(quality_counts.get("low") or 0)
    # VOILA_V0_7_92_FORMULA_VISUAL_EVIDENCE_VIEWER_SORT_END
    page_images = manifest.get("page_images") if isinstance(manifest.get("page_images"), list) else []
    policy = manifest.get("policy") if isinstance(manifest.get("policy"), dict) else {}

    cards = []
    for index, item in enumerate(display_candidates, 1):
        if not isinstance(item, dict):
            continue

        crop_path = str(item.get("crop_path") or "")
        candidate_id = str(item.get("id") or "")
        crop_src = (
            f"/owner/formula-visual-evidence/{_quote(safe_course_id, safe='')}/asset?candidate_id={_quote(candidate_id, safe='')}"
            if crop_path and candidate_id
            else ""
        )
        reasons = item.get("reasons") if isinstance(item.get("reasons"), list) else []
        reasons_label = ", ".join(str(x) for x in reasons) or "—"
        quality_tier = str(item.get("quality_tier") or "low")
        quality_score = str(item.get("quality_score") or 0)
        noise_reasons = item.get("noise_reasons") if isinstance(item.get("noise_reasons"), list) else []
        noise_label = ", ".join(str(x) for x in noise_reasons) or "—"
        bbox = item.get("bbox") if isinstance(item.get("bbox"), list) else []
        bbox_label = ", ".join(str(x) for x in bbox) or "—"

        image_html = (
            f'<img class="v0790-formula-crop" src="{_voila_v082_escape(crop_src)}" alt="Formula candidate crop {_voila_v082_escape(item.get("id"))}">'
            if crop_src
            else '<p class="missing-note">Crop lipsă.</p>'
        )

        cards.append(f"""
        <article class="card v0790-formula-card">
          <div class="meta">
            #{index} · {_voila_v082_escape(item.get("id"))}
            · pagina {_voila_v082_escape(item.get("page"))}
            · status: {_voila_v082_escape(item.get("review_status"))}
            · calitate: {_voila_v082_escape(quality_tier)} ({_voila_v082_escape(quality_score)})
          </div>
          {image_html}
          <p><strong>Text OCR:</strong> {_voila_v082_escape(item.get("text"))}</p>
          <p><strong>Calitate:</strong> {_voila_v082_escape(quality_tier)} · score {_voila_v082_escape(quality_score)}</p>
          <p><strong>Motiv detectare:</strong> {_voila_v082_escape(reasons_label)}</p>
          <p><strong>Zgomot:</strong> {_voila_v082_escape(noise_label)}</p>
          <p><strong>BBox:</strong> <code>{_voila_v082_escape(bbox_label)}</code></p>
          <p><strong>Crop:</strong> <code>{_voila_v082_escape(crop_path)}</code></p>
        </article>
        """)

    # VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_BOOL_DISPLAY_START
    uses_pymupdf_label = str(policy.get("uses_pymupdf", False))
    uses_llm_label = str(policy.get("uses_llm", False))
    uses_cloud_label = str(policy.get("uses_cloud", False))
    formula_ocr_label = str(policy.get("formula_ocr_performed", False))
    # VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_BOOL_DISPLAY_END

    body = f"""
    <style id="voila-v0790-formula-visual-evidence-viewer-style">
      .v0790-formula-summary {{
        display: grid;
        gap: 12px;
      }}
      .v0790-formula-badges {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
      }}
      .v0790-formula-badges span {{
        border: 1px solid rgba(148, 163, 184, 0.35);
        border-radius: 999px;
        padding: 6px 10px;
        background: rgba(15, 23, 42, 0.35);
      }}
      .v0790-formula-grid {{
        display: grid;
        gap: 14px;
        margin-top: 16px;
      }}
      .v0790-formula-crop {{
        display: block;
        max-width: 100%;
        height: auto;
        margin: 10px 0;
        border: 1px solid rgba(148, 163, 184, 0.35);
        border-radius: 12px;
        background: white;
      }}
      .v0790-formula-card p {{
        margin: 8px 0;
      }}
    </style>

    <main>
      <section class="card v0790-formula-summary">
        <h1>Formula visual evidence</h1>
        <p class="meta">Owner-local · read-only · crop-uri vizuale pentru candidați formulă/simbol</p>
        <p><code>formula_visual_evidence.manifest.json</code></p>

        <div class="v0790-formula-badges">
          <span>Pagini: <strong>{_voila_v082_escape(manifest.get("page_count"))}</strong></span>
          <span>Imagini pagină: <strong>{_voila_v082_escape(len(page_images))}</strong></span>
          <span>Candidați: <strong>{_voila_v082_escape(manifest.get("candidate_count", len(candidates)))}</strong></span>
          <span>High: <strong>{_voila_v082_escape(high_count)}</strong></span>
          <span>Medium: <strong>{_voila_v082_escape(medium_count)}</strong></span>
          <span>Low/noisy: <strong>{_voila_v082_escape(low_count)}</strong></span>
          <span>PyMuPDF: <strong>{_voila_v082_escape(uses_pymupdf_label)}</strong></span>
          <span>LLM: <strong>{_voila_v082_escape(uses_llm_label)}</strong></span>
          <span>Cloud: <strong>{_voila_v082_escape(uses_cloud_label)}</strong></span>
          <span>Formula OCR: <strong>{_voila_v082_escape(formula_ocr_label)}</strong></span>
        </div>
      </section>

      <section class="v0790-formula-grid">
        {''.join(cards)}
      </section>
    </main>
    """

    return page("Voila! Formula visual evidence", body)

# VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_VIEWER_END





# VOILA_V0_7_96_MANUAL_LEARNING_EVIDENCE_UI_SKELETON_START
def _voila_v0796_safe_course_id(course_id: str) -> str:
    raw = Path(str(course_id or "").replace("\\", "/")).name
    cleaned = "".join(ch for ch in raw if ch.isalnum() or ch in "._-")
    if cleaned in {"", ".", ".."}:
        return "_invalid_course"
    return cleaned


def _voila_v0796_manual_learning_evidence_dir(course_id: str) -> Path:
    return OUTPUT_DIR / _voila_v0796_safe_course_id(course_id)


def _voila_v0796_page_image_path(course_id: str, page: int) -> Path:
    safe_course_id = _voila_v0796_safe_course_id(course_id)
    return OUTPUT_DIR / safe_course_id / "formula_visual_evidence" / "pages" / f"page-{int(page):03d}.png"



# VOILA_V0_8_8_MANUAL_LEARNING_PACK_EXPORT_DRAFT_START
def _voila_v088_manual_learning_pack_required_fields():
    return ["title", "kind", "verified_text", "explanation_ro", "page", "bbox"]


def _voila_v088_manual_learning_pack_eligible_items(items):
    if not isinstance(items, list):
        items = []

    required_fields = _voila_v088_manual_learning_pack_required_fields()
    eligible_items = []

    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("status") != "accepted_owner_verified" or item.get("owner_verified") is not True:
            continue

        missing = []
        for field in required_fields:
            value = item.get(field)
            if field == "bbox":
                if not isinstance(value, list) or len(value) != 4:
                    missing.append(field)
            elif value is None or str(value).strip() == "":
                missing.append(field)

        if missing:
            continue

        eligible_items.append(item)

    return eligible_items


def _voila_v088_manual_learning_pack_payload(course_id, items):
    eligible_items = _voila_v088_manual_learning_pack_eligible_items(items)
    pack_items = []

    for item in eligible_items:
        pack_items.append({
            "source_evidence_id": str(item.get("id") or ""),
            "title": str(item.get("title") or ""),
            "kind": str(item.get("kind") or ""),
            "verified_text": str(item.get("verified_text") or ""),
            "explanation_ro": str(item.get("explanation_ro") or ""),
            "page": item.get("page"),
            "bbox": item.get("bbox"),
            "source_status": str(item.get("source_status") or ""),
            "owner_verified": True,
            "status": "accepted_owner_verified",
        })

    return {
        "schema": "voila.manual_learning_pack.preview.v1",
        "course_id": str(course_id or ""),
        "source": "manual_learning_evidence.json",
        "artifact": "manual_learning_pack.preview.json",
        "mode": "owner_local_preview_draft",
        "generated_by": "v0.8.8_manual_learning_evidence_export_draft_json",
        "quality_gate": {
            "required_fields": _voila_v088_manual_learning_pack_required_fields(),
            "uses_only_accepted_owner_verified": True,
            "uses_only_owner_verified_true": True,
            "uses_only_quality_gate_eligible": True,
        },
        "items_count": len(pack_items),
        "items": pack_items,
        "policy": {
            "learning_pack_preview_only": True,
            "course_generation_changed": False,
            "study_changed": False,
            "progress_changed": False,
            "ocr_rewrite_performed": False,
            "formula_ocr_performed": False,
            "build_performed": False,
            "zip_created": False,
            "share_created": False,
            "delivery_performed": False,
            "distribution_performed": False,
        },
    }


def _voila_v088_manual_learning_pack_export_form_html(course_id, eligible_count):
    safe_course_id = _voila_v090_validate_course_id(str(course_id or ""))
    action_path = f"/owner/manual-learning-evidence/{safe_course_id}/export-learning-pack-draft"

    disabled = "" if eligible_count > 0 else " disabled"
    button_label = "Exportă draft Learning Pack JSON" if eligible_count > 0 else "Export blocat: nu există itemuri eligibile"

    return f"""
    <div class="v088-export-draft" data-testid="manual-learning-pack-export-draft">
      <strong>Learning Pack preview export</strong>
      <p class="meta">
        Scrie doar artifact separat <code>manual_learning_pack.preview.json</code>
        din itemuri accepted + owner verified + quality gate eligible.
      </p>
      <form method="post" action="{action_path}">
        <button class="v088-export-button" type="submit"{disabled} data-testid="manual-learning-pack-export-draft-button">{html.escape(button_label, quote=True)}</button>
      </form>
      <p class="meta v088-export-note">
        eligible dry-run items: <code>{eligible_count}</code>.
        No Course/Study/Progress/OCR rewrite. No build/ZIP/share/delivery.
        Viewer route: <code>/owner/manual-learning-pack-preview/{safe_course_id}</code>
      </p>
    </div>
    """
# VOILA_V0_8_8_MANUAL_LEARNING_PACK_EXPORT_DRAFT_END


# VOILA_V0_8_7_MANUAL_LEARNING_EVIDENCE_LEARNING_PACK_DRY_RUN_START
def _voila_v087_manual_learning_evidence_learning_pack_dry_run_html(course_id, items):
    if not isinstance(items, list):
        items = []

    required_fields = ["title", "kind", "verified_text", "explanation_ro", "page", "bbox"]
    eligible_items = []
    accepted_incomplete_count = 0

    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("status") != "accepted_owner_verified" or item.get("owner_verified") is not True:
            continue

        missing = []
        for field in required_fields:
            value = item.get(field)
            if field == "bbox":
                if not isinstance(value, list) or len(value) != 4:
                    missing.append(field)
            elif value is None or str(value).strip() == "":
                missing.append(field)

        if missing:
            accepted_incomplete_count += 1
        else:
            eligible_items.append(item)

    if not eligible_items:
        return f"""
        <section class="v087-learning-pack-dry-run" data-testid="manual-evidence-learning-pack-dry-run">
          <strong>Learning Pack dry-run preview</strong>
          <p class="meta">
            No quality-gate eligible accepted evidence items yet.
            accepted incomplete/blocked: <code>{accepted_incomplete_count}</code>.
          </p>
          <span class="v087-dry-run-badge">Dry-run only · no Learning Pack artifact written</span>
          {_voila_v088_manual_learning_pack_export_form_html(course_id, 0)}
        </section>
        """

    cards = []
    for item in eligible_items[-25:]:
        draft_id = html.escape(str(item.get("id") or "(missing-id)"), quote=True)
        title = html.escape(str(item.get("title") or "(fără titlu)"), quote=True)
        kind = html.escape(str(item.get("kind") or ""), quote=True)
        page_value = html.escape(str(item.get("page") or ""), quote=True)
        source_status = html.escape(str(item.get("source_status") or ""), quote=True)
        verified_text = html.escape(str(item.get("verified_text") or ""), quote=True)
        explanation_ro = html.escape(str(item.get("explanation_ro") or ""), quote=True)
        bbox = item.get("bbox")
        bbox_text = "[" + ", ".join(html.escape(str(part), quote=True) for part in bbox) + "]"

        cards.append(
            f"""
            <article class="v087-learning-pack-card" data-testid="manual-evidence-learning-pack-dry-run-card">
              <h3>{title}</h3>
              <p class="meta">
                dry_run_source_id: <code>{draft_id}</code><br>
                page: <code>{page_value}</code> · kind: <code>{kind}</code> · source_status: <code>{source_status}</code>
              </p>
              <p><strong>Learning objective source:</strong><br>{verified_text}</p>
              <p><strong>Romanian explanation:</strong><br>{explanation_ro}</p>
              <p>source bbox: <code>{bbox_text}</code></p>
              <span class="v087-dry-run-badge">Would enter future Learning Pack</span>
            </article>
            """
        )

    return f"""
    <section class="v087-learning-pack-dry-run" data-testid="manual-evidence-learning-pack-dry-run">
      <strong>Learning Pack dry-run preview</strong> · eligible items: <code>{len(eligible_items)}</code>
      <p class="meta">
        Read-only dry-run using only <code>accepted_owner_verified</code> items that pass the quality gate.
        v0.8.7 does not write or modify any Learning Pack artifact.
      </p>
      {_voila_v088_manual_learning_pack_export_form_html(course_id, len(eligible_items))}
      <div class="v087-learning-pack-grid">
        {''.join(cards)}
      </div>
    </section>
    """
# VOILA_V0_8_7_MANUAL_LEARNING_EVIDENCE_LEARNING_PACK_DRY_RUN_END


# VOILA_V0_8_6_MANUAL_LEARNING_EVIDENCE_QUALITY_GATE_START
def _voila_v086_manual_learning_evidence_quality_gate_html(items):
    if not isinstance(items, list):
        items = []

    required_fields = ["title", "kind", "verified_text", "explanation_ro", "page", "bbox"]
    accepted_items = [
        item for item in items
        if isinstance(item, dict)
        and item.get("status") == "accepted_owner_verified"
        and item.get("owner_verified") is True
    ]

    eligible = 0
    incomplete = 0
    blocked = 0
    rows = []

    for item in accepted_items[-25:]:
        missing = []

        for field in required_fields:
            value = item.get(field)
            if field == "bbox":
                if not isinstance(value, list) or len(value) != 4:
                    missing.append(field)
            elif value is None or str(value).strip() == "":
                missing.append(field)

        draft_id = html.escape(str(item.get("id") or "(missing-id)"), quote=True)
        title = html.escape(str(item.get("title") or "(fără titlu)"), quote=True)

        if missing:
            incomplete += 1
            gate_status = "incomplete"
            missing_text = ", ".join(html.escape(field, quote=True) for field in missing)
        else:
            eligible += 1
            gate_status = "eligible"
            missing_text = "none"

        rows.append(
            f"""
            <div class="v086-quality-item" data-testid="manual-evidence-quality-item">
              <span class="v086-gate-badge">{gate_status}</span>
              <strong>{title}</strong>
              <p class="meta">
                id: <code>{draft_id}</code><br>
                required fields: <code>{html.escape(', '.join(required_fields), quote=True)}</code><br>
                missing: <code>{missing_text}</code>
              </p>
            </div>
            """
        )

    if not accepted_items:
        blocked = 1
        gate_state = "blocked"
    elif incomplete:
        gate_state = "incomplete"
    else:
        gate_state = "eligible"

    return f"""
    <section class="v086-quality-gate" data-testid="manual-evidence-quality-gate">
      <strong>Accepted evidence quality gate</strong>
      <p class="meta">
        Read-only validation for future Learning Pack eligibility.
        Required fields: <code>{html.escape(', '.join(required_fields), quote=True)}</code>.
        No Learning Pack is generated in v0.8.6.
      </p>
      <div class="v086-quality-grid">
        <div class="v086-quality-stat" data-testid="manual-evidence-quality-eligible">
          <strong>{eligible}</strong>
          eligible
        </div>
        <div class="v086-quality-stat" data-testid="manual-evidence-quality-incomplete">
          <strong>{incomplete}</strong>
          incomplete
        </div>
        <div class="v086-quality-stat" data-testid="manual-evidence-quality-blocked">
          <strong>{blocked}</strong>
          blocked
        </div>
        <div class="v086-quality-stat" data-testid="manual-evidence-quality-state">
          <strong>{gate_state}</strong>
          gate state
        </div>
      </div>
      <div class="v086-quality-list">
        {''.join(rows)}
      </div>
    </section>
    """
# VOILA_V0_8_6_MANUAL_LEARNING_EVIDENCE_QUALITY_GATE_END


# VOILA_V0_8_5_MANUAL_LEARNING_EVIDENCE_ACCEPTED_PREVIEW_START
def _voila_v085_manual_learning_evidence_accepted_preview_html(items):
    if not isinstance(items, list):
        items = []

    accepted_items = [
        item for item in items
        if isinstance(item, dict)
        and item.get("status") == "accepted_owner_verified"
        and item.get("owner_verified") is True
    ]

    if not accepted_items:
        return """
        <section class="v085-accepted-preview" data-testid="manual-evidence-accepted-preview">
          <strong>Accepted evidence preview</strong>
          <p class="meta">
            No <code>accepted_owner_verified</code> items yet.
            Future Learning Pack input preview is empty.
          </p>
          <span class="v085-learning-pack-ghost">Learning Pack not generated in v0.8.5</span>
        </section>
        """

    cards = []
    for item in accepted_items[-25:]:
        draft_id = html.escape(str(item.get("id") or "(missing-id)"), quote=True)
        title = html.escape(str(item.get("title") or "(fără titlu)"), quote=True)
        kind = html.escape(str(item.get("kind") or ""), quote=True)
        page_value = html.escape(str(item.get("page") or ""), quote=True)
        source_status = html.escape(str(item.get("source_status") or ""), quote=True)
        verified_text = html.escape(str(item.get("verified_text") or ""), quote=True)
        explanation_ro = html.escape(str(item.get("explanation_ro") or ""), quote=True)

        bbox = item.get("bbox")
        if isinstance(bbox, list):
            bbox_text = "[" + ", ".join(html.escape(str(part), quote=True) for part in bbox) + "]"
        else:
            bbox_text = "[]"

        cards.append(
            f"""
            <article class="v085-accepted-card" data-testid="manual-evidence-accepted-card">
              <h3>{title}</h3>
              <p class="meta">
                id: <code>{draft_id}</code><br>
                page: <code>{page_value}</code> · kind: <code>{kind}</code> · source_status: <code>{source_status}</code>
              </p>
              <p><strong>Verified text:</strong><br>{verified_text}</p>
              <p><strong>Explanation RO:</strong><br>{explanation_ro}</p>
              <p>bbox: <code>{bbox_text}</code></p>
              <span class="v085-learning-pack-ghost">Would be eligible for future Learning Pack</span>
            </article>
            """
        )

    return f"""
    <section class="v085-accepted-preview" data-testid="manual-evidence-accepted-preview">
      <strong>Accepted evidence preview</strong> · accepted items: <code>{len(accepted_items)}</code>
      <p class="meta">
        Read-only preview of <code>accepted_owner_verified</code> items.
        This shows what could feed a future Learning Pack, but v0.8.5 does not generate or modify Learning Pack artifacts.
      </p>
      <div class="v085-accepted-grid">
        {''.join(cards)}
      </div>
    </section>
    """
# VOILA_V0_8_5_MANUAL_LEARNING_EVIDENCE_ACCEPTED_PREVIEW_END


# VOILA_V0_8_4_MANUAL_LEARNING_EVIDENCE_REVIEW_SUMMARY_START
def _voila_v084_manual_learning_evidence_review_summary_html(items):
    if not isinstance(items, list):
        items = []

    counts = {
        "pending_owner_review": 0,
        "accepted_owner_verified": 0,
        "rejected_noise": 0,
        "other": 0,
    }

    for item in items:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "")
        if status in counts:
            counts[status] += 1
        else:
            counts["other"] += 1

    total = sum(counts.values())

    return f"""
    <section class="v084-review-summary" data-testid="manual-evidence-review-summary">
      <strong>Review summary</strong>
      <div class="v084-review-grid">
        <div class="v084-review-stat" data-testid="manual-evidence-count-total">
          <strong>{total}</strong>
          total evidence items
        </div>
        <div class="v084-review-stat" data-testid="manual-evidence-count-pending">
          <strong>{counts["pending_owner_review"]}</strong>
          pending_owner_review
        </div>
        <div class="v084-review-stat" data-testid="manual-evidence-count-accepted">
          <strong>{counts["accepted_owner_verified"]}</strong>
          accepted_owner_verified
        </div>
        <div class="v084-review-stat" data-testid="manual-evidence-count-rejected">
          <strong>{counts["rejected_noise"]}</strong>
          rejected_noise
        </div>
      </div>
      <div class="v084-filter-row" data-testid="manual-evidence-status-filters">
        <a href="#manual-evidence-status-pending_owner_review">Pending</a>
        <a href="#manual-evidence-status-accepted_owner_verified">Accepted</a>
        <a href="#manual-evidence-status-rejected_noise">Rejected</a>
      </div>
      <p class="meta">Read-only review summary. No new write endpoint in v0.8.4. No Learning Pack.</p>
    </section>
    """
# VOILA_V0_8_4_MANUAL_LEARNING_EVIDENCE_REVIEW_SUMMARY_END


# VOILA_V0_8_1_MANUAL_LEARNING_EVIDENCE_LIST_DRAFTS_START
def _voila_v081_manual_learning_evidence_list_html(course_id: str):
    import json as _json

    safe_course_id = _voila_v0796_safe_course_id(course_id)
    target = _voila_v0796_manual_learning_evidence_dir(safe_course_id) / "manual_learning_evidence.json"

    if not target.exists():
        return (
            """
            <div class="notice" data-testid="manual-evidence-draft-list">
              <strong>Draft evidence list</strong><br>
              No <code>manual_learning_evidence.json</code> exists yet.
            </div>
            """,
            0,
            False,
        )

    try:
        data = _json.loads(target.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return (
            f"""
            <div class="notice warn" data-testid="manual-evidence-draft-list">
              <strong>Draft evidence list unavailable</strong><br>
              Could not read <code>manual_learning_evidence.json</code>:
              <code>{html.escape(str(exc), quote=True)}</code>
            </div>
            """,
            0,
            True,
        )

    if isinstance(data, dict):
        raw_items = data.get("items", [])
    elif isinstance(data, list):
        raw_items = data
    else:
        raw_items = []

    if not isinstance(raw_items, list):
        raw_items = []

    items = [item for item in raw_items if isinstance(item, dict)]

    if not items:
        return (
            """
            <div class="notice" data-testid="manual-evidence-draft-list">
              <strong>Draft evidence list</strong><br>
              <code>manual_learning_evidence.json</code> exists, but it has no draft items yet.
            </div>
            """,
            0,
            True,
        )

    # VOILA_V0_8_4_MANUAL_LEARNING_EVIDENCE_REVIEW_SUMMARY_COUNTS_START
    review_summary_html = _voila_v084_manual_learning_evidence_review_summary_html(items)
    accepted_preview_html = _voila_v085_manual_learning_evidence_accepted_preview_html(items)
    quality_gate_html = _voila_v086_manual_learning_evidence_quality_gate_html(items)
    learning_pack_dry_run_html = _voila_v087_manual_learning_evidence_learning_pack_dry_run_html(course_id, items)
    # VOILA_V0_8_4_MANUAL_LEARNING_EVIDENCE_REVIEW_SUMMARY_COUNTS_END

    cards = []
    last_status_heading = None
    for item in sorted(items[-25:], key=lambda candidate: str(candidate.get("status") or "") if isinstance(candidate, dict) else ""):
        draft_id = html.escape(str(item.get("id") or "(missing-id)"), quote=True)
        title = html.escape(str(item.get("title") or "(fără titlu)"), quote=True)
        kind = html.escape(str(item.get("kind") or ""), quote=True)
        status = html.escape(str(item.get("status") or ""), quote=True)
        page_value = html.escape(str(item.get("page") or ""), quote=True)
        owner_verified = "true" if item.get("owner_verified") is True else "false"
        save_state = html.escape(str(item.get("save_state") or ""), quote=True)
        source_status = html.escape(str(item.get("source_status") or ""), quote=True)

        status_raw = str(item.get("status") or "other")
        status_anchor = status_raw if status_raw in {"pending_owner_review", "accepted_owner_verified", "rejected_noise"} else "other"
        section_html = ""
        if status_anchor != last_status_heading:
            last_status_heading = status_anchor
            section_html = (
                f'<div class="v084-status-section" '
                f'id="manual-evidence-status-{html.escape(status_anchor, quote=True)}">'
                f'<h3>{html.escape(status_anchor, quote=True)}</h3>'
                f'</div>'
            )

        bbox = item.get("bbox")
        if isinstance(bbox, list):
            bbox_text = "[" + ", ".join(html.escape(str(part), quote=True) for part in bbox) + "]"
        else:
            bbox_text = "[]"

        # VOILA_V0_8_3_MANUAL_LEARNING_EVIDENCE_REJECT_DRAFT_CARD_START
        if item.get("status") == "accepted_owner_verified" and item.get("owner_verified") is True:
            verify_action_html = '<span class="v082-verified-badge">accepted_owner_verified</span>'
        elif item.get("status") == "rejected_noise":
            verify_action_html = '<span class="v083-rejected-badge">rejected_noise</span>'
        else:
            verify_action = html.escape(
                "/owner/manual-learning-evidence/" + quote(safe_course_id, safe="") + "/verify-draft",
                quote=True,
            )
            reject_action = html.escape(
                "/owner/manual-learning-evidence/" + quote(safe_course_id, safe="") + "/reject-draft",
                quote=True,
            )
            verify_action_html = (
                f'<div class="v083-action-row">'
                f'<form class="v082-verify-form" method="post" action="{verify_action}">'
                f'<input type="hidden" name="draft_id" value="{draft_id}">'
                f'<button type="submit">Verify / Accept draft</button>'
                f'<p class="meta">Writes only <code>manual_learning_evidence.json</code>. No Learning Pack.</p>'
                f'</form>'
                f'<form class="v083-reject-form" method="post" action="{reject_action}">'
                f'<input type="hidden" name="draft_id" value="{draft_id}">'
                f'<input type="hidden" name="rejection_reason" value="owner_rejected_noise">'
                f'<button type="submit">Reject / Noise draft</button>'
                f'<p class="meta">Marks this draft as <code>rejected_noise</code>. No Learning Pack.</p>'
                f'</form>'
                f'</div>'
            )
        # VOILA_V0_8_3_MANUAL_LEARNING_EVIDENCE_REJECT_DRAFT_CARD_END

        cards.append(
            f"""
            {section_html}
            <article class="v081-draft-card" data-testid="manual-evidence-draft-card" data-status="{status_anchor}">
              <h3>{title}</h3>
              <p class="meta">
                id: <code>{draft_id}</code><br>
                page: <code>{page_value}</code> · kind: <code>{kind}</code> · source_status: <code>{source_status}</code>
              </p>
              <p>
                status: <code>{status}</code> · owner_verified: <code>{owner_verified}</code> · save_state: <code>{save_state}</code>
              </p>
              <p>bbox: <code>{bbox_text}</code></p>
              {verify_action_html}
            </article>
            """
        )

    return (
        f"""
        {review_summary_html}
        {accepted_preview_html}
        {quality_gate_html}
        {learning_pack_dry_run_html}
        <div class="v081-draft-summary" data-testid="manual-evidence-draft-list">
          <strong>Draft evidence list</strong> · items: <code>{len(items)}</code> · source:
          <code>manual_learning_evidence.json</code>
        </div>
        <div class="v081-draft-list">
          {''.join(cards)}
        </div>
        """,
        len(items),
        True,
    )
# VOILA_V0_8_1_MANUAL_LEARNING_EVIDENCE_LIST_DRAFTS_END


@app.get("/owner/manual-learning-evidence/{course_id}", response_class=HTMLResponse, include_in_schema=False)
def owner_manual_learning_evidence_skeleton(course_id: str, page_number: int = Query(default=1, alias="page")) -> HTMLResponse:
    safe_course_id = _voila_v0796_safe_course_id(course_id)
    safe_page = max(1, int(page_number or 1))
    output_dir = _voila_v0796_manual_learning_evidence_dir(safe_course_id)
    page_image = _voila_v0796_page_image_path(safe_course_id, safe_page)
    pdf_name = safe_course_id + ".pdf"

    safe_course_id_url = quote(safe_course_id, safe="")
    pdf_name_url = quote(pdf_name, safe="")
    back_url = html.escape(f"/course-tools?pdf={pdf_name_url}", quote=True)
    formula_viewer_url = html.escape(f"/owner/formula-visual-evidence/{safe_course_id_url}/view", quote=True)
    prev_url = html.escape(f"/owner/manual-learning-evidence/{safe_course_id_url}?page={max(1, safe_page - 1)}", quote=True)
    next_url = html.escape(f"/owner/manual-learning-evidence/{safe_course_id_url}?page={safe_page + 1}", quote=True)
    safe_course_id_html = html.escape(safe_course_id, quote=True)
    output_dir_html = html.escape(str(output_dir), quote=True)

    if page_image.exists():
        page_image_src = html.escape(
            output_url(safe_course_id, "formula_visual_evidence", "pages", f"page-{safe_page:03d}.png"),
            quote=True,
        )
        page_image_html = f"""
        <figure class="v0796-page-frame">
          <div class="v0798-crop-shell" id="v0798CropShell" aria-label="Manual crop selection preview">
            <img id="v0798SourceImage" src="{page_image_src}" alt="Source page {safe_page}" draggable="false">
            <div class="v0798-selection-box" id="v0798SelectionBox" hidden></div>
          </div>
          <figcaption>source page {safe_page} · crop preview only · no save</figcaption>
        </figure>
        """
        source_state = "source_page_image_found"
    else:
        page_image_expected_html = html.escape(str(page_image), quote=True)
        page_image_html = f"""
        <div class="notice warn">
          <strong>Source page image missing.</strong><br>
          Expected: <code>{page_image_expected_html}</code>
        </div>
        """
        source_state = "source_page_image_missing"

    # VOILA_V0_8_1_MANUAL_LEARNING_EVIDENCE_LIST_DRAFTS_READ_START
    manual_evidence_list_html, manual_evidence_item_count, manual_evidence_json_exists = _voila_v081_manual_learning_evidence_list_html(safe_course_id)
    # VOILA_V0_8_1_MANUAL_LEARNING_EVIDENCE_LIST_DRAFTS_READ_END

    body = f"""
    <style>
      .v0796-grid {{
        display: grid;
        grid-template-columns: minmax(320px, 1.2fr) minmax(320px, 0.8fr);
        gap: 20px;
        align-items: start;
      }}
      .v0796-page-frame {{
        margin: 0;
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 12px;
        background: rgba(255,255,255,0.32);
      }}
      .v0796-page-frame img {{
        width: 100%;
        height: auto;
        border-radius: 12px;
        border: 1px solid var(--border);
        background: white;
      }}
      .v0796-form {{
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 16px;
        background: rgba(255,255,255,0.32);
      }}
      .v0796-form label {{
        display: block;
        font-weight: 700;
        margin-top: 12px;
      }}
      .v0796-form input,
      .v0796-form select,
      .v0796-form textarea {{
        width: 100%;
        margin-top: 4px;
        padding: 8px;
        border-radius: 10px;
        border: 1px solid var(--border);
        background: #fffaf0;
      }}
      .v0796-disabled-note {{
        margin-top: 14px;
        color: var(--muted);
        font-size: 14px;
      }}
      /* VOILA_V0_7_97_MANUAL_LEARNING_EVIDENCE_VISUAL_POLISH_START */
      .v0797-readonly-banner {{
        border: 1px solid rgba(31,78,121,0.28);
        border-radius: 18px;
        padding: 14px 16px;
        margin: 16px 0;
        background: rgba(31,78,121,0.08);
      }}
      .v0797-status-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 12px 0 16px;
      }}
      .v0797-chip {{
        display: inline-flex;
        align-items: center;
        border: 1px solid rgba(31,78,121,0.22);
        border-radius: 999px;
        padding: 6px 10px;
        background: rgba(255,255,255,0.42);
        font-size: 13px;
        font-weight: 700;
      }}
      .v0797-next-steps {{
        margin-top: 12px;
        padding-left: 18px;
      }}
      .v0797-next-steps li {{
        margin: 4px 0;
      }}
      /* VOILA_V0_7_97_MANUAL_LEARNING_EVIDENCE_VISUAL_POLISH_END */
      /* VOILA_V0_7_98_MANUAL_LEARNING_EVIDENCE_CROP_SELECTION_PREVIEW_START */
      .v0798-crop-shell {{
        position: relative;
        cursor: crosshair;
        touch-action: none;
        user-select: none;
      }}
      .v0798-crop-shell img {{
        display: block;
      }}
      .v0798-selection-box {{
        position: absolute;
        border: 2px solid rgba(31,78,121,0.95);
        background: rgba(31,78,121,0.16);
        pointer-events: none;
        border-radius: 4px;
      }}
      .v0798-preview-panel {{
        border: 1px solid rgba(31,78,121,0.28);
        border-radius: 18px;
        padding: 16px;
        background: rgba(255,255,255,0.32);
      }}
      .v0798-preview-canvas {{
        width: 100%;
        max-height: 360px;
        border: 1px solid rgba(31,78,121,0.28);
        border-radius: 12px;
        background: white;
        display: block;
      }}
      .v0798-bbox {{
        display: block;
        white-space: normal;
        overflow-wrap: anywhere;
        margin: 8px 0;
      }}
      /* VOILA_V0_7_99_MANUAL_LEARNING_EVIDENCE_METADATA_PREVIEW_BINDING_START */
      .v0799-pending-preview {{
        margin-top: 14px;
        border: 1px solid rgba(31,78,121,0.28);
        border-radius: 16px;
        padding: 12px;
        background: rgba(31,78,121,0.06);
      }}
      .v0799-pending-preview textarea {{
        width: 100%;
        min-height: 190px;
        margin-top: 8px;
        padding: 10px;
        border: 1px solid rgba(31,78,121,0.28);
        border-radius: 12px;
        background: #fffaf0;
        font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
        font-size: 13px;
      }}
      .v0799-readonly-field {{
        margin-top: 8px;
      }}
      /* VOILA_V0_7_99_MANUAL_LEARNING_EVIDENCE_METADATA_PREVIEW_BINDING_END */
      /* VOILA_V0_8_0_MANUAL_LEARNING_EVIDENCE_SAVE_DRAFT_JSON_START */
      .v080-save-draft-form {{
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid rgba(31,78,121,0.18);
      }}
      .v080-save-draft-form button {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border: 0;
        border-radius: 12px;
        padding: 10px 14px;
        background: var(--voila-blue, #1F4E79);
        color: white;
        font-weight: 800;
        cursor: pointer;
      }}
      .v080-save-draft-form button:disabled {{
        opacity: 0.55;
        cursor: not-allowed;
      }}
      /* VOILA_V0_8_0_MANUAL_LEARNING_EVIDENCE_SAVE_DRAFT_JSON_END */
      /* VOILA_V0_8_1_MANUAL_LEARNING_EVIDENCE_LIST_DRAFTS_CSS_START */
      .v081-draft-summary {{
        margin: 12px 0;
        border: 1px solid rgba(31,78,121,0.28);
        border-radius: 16px;
        padding: 12px;
        background: rgba(31,78,121,0.06);
      }}
      .v081-draft-list {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 12px;
        margin-top: 12px;
      }}
      .v081-draft-card {{
        border: 1px solid rgba(31,78,121,0.24);
        border-radius: 16px;
        padding: 12px;
        background: rgba(255,255,255,0.38);
      }}
      .v081-draft-card h3 {{
        margin: 0 0 8px;
      }}
      /* VOILA_V0_8_1_MANUAL_LEARNING_EVIDENCE_LIST_DRAFTS_CSS_END */
      /* VOILA_V0_8_2_MANUAL_LEARNING_EVIDENCE_VERIFY_DRAFT_CSS_START */
      .v082-verify-form {{
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid rgba(31,78,121,0.16);
      }}
      .v082-verify-form button {{
        border: 0;
        border-radius: 12px;
        padding: 9px 12px;
        background: var(--voila-blue, #1F4E79);
        color: white;
        font-weight: 800;
        cursor: pointer;
      }}
      .v082-verified-badge {{
        display: inline-flex;
        border: 1px solid rgba(31,78,121,0.24);
        border-radius: 999px;
        padding: 5px 9px;
        background: rgba(31,78,121,0.08);
        font-size: 13px;
        font-weight: 800;
      }}
      /* VOILA_V0_8_2_MANUAL_LEARNING_EVIDENCE_VERIFY_DRAFT_CSS_END */
      /* VOILA_V0_8_3_MANUAL_LEARNING_EVIDENCE_REJECT_DRAFT_CSS_START */
      .v083-action-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: flex-start;
      }}
      .v083-reject-form {{
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid rgba(121,31,31,0.16);
      }}
      .v083-reject-form button {{
        border: 1px solid rgba(121,31,31,0.28);
        border-radius: 12px;
        padding: 9px 12px;
        background: rgba(121,31,31,0.08);
        color: #5f1f1f;
        font-weight: 800;
        cursor: pointer;
      }}
      .v083-rejected-badge {{
        display: inline-flex;
        border: 1px solid rgba(121,31,31,0.24);
        border-radius: 999px;
        padding: 5px 9px;
        background: rgba(121,31,31,0.08);
        color: #5f1f1f;
        font-size: 13px;
        font-weight: 800;
      }}
      /* VOILA_V0_8_3_MANUAL_LEARNING_EVIDENCE_REJECT_DRAFT_CSS_END */
      /* VOILA_V0_8_4_MANUAL_LEARNING_EVIDENCE_REVIEW_SUMMARY_CSS_START */
      .v084-review-summary {{
        margin: 12px 0;
        border: 1px solid rgba(31,78,121,0.24);
        border-radius: 18px;
        padding: 14px;
        background: rgba(31,78,121,0.055);
      }}
      .v084-review-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 10px;
        margin-top: 10px;
      }}
      .v084-review-stat {{
        border: 1px solid rgba(31,78,121,0.18);
        border-radius: 14px;
        padding: 10px;
        background: rgba(255,255,255,0.42);
      }}
      .v084-review-stat strong {{
        display: block;
        font-size: 20px;
        margin-bottom: 3px;
      }}
      .v084-filter-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
      }}
      .v084-filter-row a {{
        border: 1px solid rgba(31,78,121,0.22);
        border-radius: 999px;
        padding: 6px 10px;
        text-decoration: none;
        font-weight: 800;
        background: rgba(255,255,255,0.50);
      }}
      .v084-status-section {{
        margin-top: 16px;
      }}
      .v084-status-section h3 {{
        margin: 0 0 8px;
      }}
      /* VOILA_V0_8_4_MANUAL_LEARNING_EVIDENCE_REVIEW_SUMMARY_CSS_END */
      /* VOILA_V0_8_5_MANUAL_LEARNING_EVIDENCE_ACCEPTED_PREVIEW_CSS_START */
      .v085-accepted-preview {{
        margin: 14px 0;
        border: 1px solid rgba(31,78,121,0.28);
        border-radius: 18px;
        padding: 14px;
        background: rgba(31,78,121,0.075);
      }}
      .v085-accepted-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 12px;
        margin-top: 12px;
      }}
      .v085-accepted-card {{
        border: 1px solid rgba(31,78,121,0.22);
        border-radius: 16px;
        padding: 12px;
        background: rgba(255,255,255,0.48);
      }}
      .v085-accepted-card h3 {{
        margin: 0 0 8px;
      }}
      .v085-learning-pack-ghost {{
        display: inline-flex;
        margin-top: 8px;
        border: 1px dashed rgba(31,78,121,0.35);
        border-radius: 999px;
        padding: 5px 9px;
        font-size: 13px;
        font-weight: 800;
      }}
      /* VOILA_V0_8_5_MANUAL_LEARNING_EVIDENCE_ACCEPTED_PREVIEW_CSS_END */
      /* VOILA_V0_8_6_MANUAL_LEARNING_EVIDENCE_QUALITY_GATE_CSS_START */
      .v086-quality-gate {{
        margin: 14px 0;
        border: 1px solid rgba(31,78,121,0.28);
        border-radius: 18px;
        padding: 14px;
        background: rgba(31,78,121,0.06);
      }}
      .v086-quality-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 10px;
        margin-top: 10px;
      }}
      .v086-quality-stat {{
        border: 1px solid rgba(31,78,121,0.18);
        border-radius: 14px;
        padding: 10px;
        background: rgba(255,255,255,0.46);
      }}
      .v086-quality-stat strong {{
        display: block;
        font-size: 20px;
        margin-bottom: 3px;
      }}
      .v086-quality-list {{
        margin-top: 12px;
        display: grid;
        gap: 8px;
      }}
      .v086-quality-item {{
        border: 1px solid rgba(31,78,121,0.16);
        border-radius: 14px;
        padding: 10px;
        background: rgba(255,255,255,0.42);
      }}
      .v086-gate-badge {{
        display: inline-flex;
        border-radius: 999px;
        padding: 4px 8px;
        font-size: 13px;
        font-weight: 800;
        border: 1px solid rgba(31,78,121,0.24);
        background: rgba(31,78,121,0.08);
      }}
      /* VOILA_V0_8_6_MANUAL_LEARNING_EVIDENCE_QUALITY_GATE_CSS_END */
      /* VOILA_V0_8_7_MANUAL_LEARNING_EVIDENCE_LEARNING_PACK_DRY_RUN_CSS_START */
      .v087-learning-pack-dry-run {{
        margin: 14px 0;
        border: 1px dashed rgba(31,78,121,0.38);
        border-radius: 18px;
        padding: 14px;
        background: rgba(31,78,121,0.045);
      }}
      .v087-learning-pack-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 12px;
        margin-top: 12px;
      }}
      .v087-learning-pack-card {{
        border: 1px solid rgba(31,78,121,0.20);
        border-radius: 16px;
        padding: 12px;
        background: rgba(255,255,255,0.50);
      }}
      .v087-learning-pack-card h3 {{
        margin: 0 0 8px;
      }}
      .v087-dry-run-badge {{
        display: inline-flex;
        border: 1px dashed rgba(31,78,121,0.35);
        border-radius: 999px;
        padding: 5px 9px;
        font-size: 13px;
        font-weight: 800;
        background: rgba(255,255,255,0.42);
      }}
      /* VOILA_V0_8_7_MANUAL_LEARNING_EVIDENCE_LEARNING_PACK_DRY_RUN_CSS_END */
      /* VOILA_V0_8_8_MANUAL_LEARNING_PACK_EXPORT_DRAFT_CSS_START */
      .v088-export-draft {{
        margin-top: 12px;
        border: 1px solid rgba(31,78,121,0.22);
        border-radius: 16px;
        padding: 12px;
        background: rgba(255,255,255,0.46);
      }}
      .v088-export-button {{
        border: 0;
        border-radius: 999px;
        padding: 10px 14px;
        font-weight: 900;
        cursor: pointer;
        background: #1F4E79;
        color: white;
      }}
      .v088-export-note {{
        margin-top: 8px;
      }}
      /* VOILA_V0_8_8_MANUAL_LEARNING_PACK_EXPORT_DRAFT_CSS_END */
      /* VOILA_V0_8_9_MANUAL_LEARNING_PACK_PREVIEW_VIEWER_CSS_START */
      .v089-pack-viewer {{
        margin: 14px 0;
        border: 1px solid rgba(31,78,121,0.24);
        border-radius: 18px;
        padding: 14px;
        background: rgba(31,78,121,0.045);
      }}
      .v089-pack-meta-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 10px;
        margin: 12px 0;
      }}
      .v089-pack-meta-card {{
        border: 1px solid rgba(31,78,121,0.18);
        border-radius: 14px;
        padding: 10px;
        background: rgba(255,255,255,0.50);
      }}
      .v089-pack-item-grid {{
        display: grid;
        gap: 12px;
        margin-top: 12px;
      }}
      .v089-pack-item {{
        border: 1px solid rgba(31,78,121,0.20);
        border-radius: 16px;
        padding: 12px;
        background: rgba(255,255,255,0.54);
      }}
      .v089-policy-ok {{
        display: inline-flex;
        border-radius: 999px;
        padding: 4px 8px;
        font-size: 13px;
        font-weight: 800;
        border: 1px solid rgba(31,78,121,0.24);
        background: rgba(31,78,121,0.08);
        margin: 2px 4px 2px 0;
      }}
      /* VOILA_V0_8_9_MANUAL_LEARNING_PACK_PREVIEW_VIEWER_CSS_END */
      /* VOILA_V0_8_10_MANUAL_LEARNING_PACK_STUDY_ADAPTER_DRY_RUN_CSS_START */
      .v0810-study-adapter {{
        margin: 14px 0;
        border: 1px dashed rgba(31,78,121,0.34);
        border-radius: 18px;
        padding: 14px;
        background: rgba(31,78,121,0.045);
      }}
      .v0810-study-grid {{
        display: grid;
        gap: 12px;
        margin-top: 12px;
      }}
      .v0810-study-card {{
        border: 1px solid rgba(31,78,121,0.20);
        border-radius: 16px;
        padding: 12px;
        background: rgba(255,255,255,0.54);
      }}
      .v0810-study-type {{
        display: inline-flex;
        border-radius: 999px;
        padding: 4px 8px;
        font-size: 13px;
        font-weight: 900;
        border: 1px solid rgba(31,78,121,0.24);
        background: rgba(31,78,121,0.08);
        margin-bottom: 8px;
      }}
      .v0810-study-meta-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 10px;
        margin: 12px 0;
      }}
      .v0810-study-meta-card {{
        border: 1px solid rgba(31,78,121,0.18);
        border-radius: 14px;
        padding: 10px;
        background: rgba(255,255,255,0.50);
      }}
      /* VOILA_V0_8_10_MANUAL_LEARNING_PACK_STUDY_ADAPTER_DRY_RUN_CSS_END */
      /* VOILA_V0_8_11_MANUAL_STUDY_ITEMS_PREVIEW_EXPORT_CSS_START */
      .v0811-study-export {{
        margin-top: 12px;
        border: 1px solid rgba(31,78,121,0.22);
        border-radius: 16px;
        padding: 12px;
        background: rgba(255,255,255,0.48);
      }}
      .v0811-study-export-button {{
        border: 0;
        border-radius: 999px;
        padding: 10px 14px;
        font-weight: 900;
        cursor: pointer;
        background: #1F4E79;
        color: white;
      }}
      .v0811-study-export-note {{
        margin-top: 8px;
      }}
      /* VOILA_V0_8_11_MANUAL_STUDY_ITEMS_PREVIEW_EXPORT_CSS_END */
      /* VOILA_V0_8_12_MANUAL_STUDY_ITEMS_PREVIEW_VIEWER_CSS_START */
      .v0812-manual-study-viewer {{
        margin: 14px 0;
        border: 1px solid rgba(31,78,121,0.24);
        border-radius: 18px;
        padding: 14px;
        background: rgba(31,78,121,0.045);
      }}
      .v0812-manual-study-meta-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 10px;
        margin: 12px 0;
      }}
      .v0812-manual-study-meta-card {{
        border: 1px solid rgba(31,78,121,0.18);
        border-radius: 14px;
        padding: 10px;
        background: rgba(255,255,255,0.50);
      }}
      .v0812-manual-study-items {{
        display: grid;
        gap: 12px;
        margin-top: 12px;
      }}
      .v0812-manual-study-item {{
        border: 1px solid rgba(31,78,121,0.20);
        border-radius: 16px;
        padding: 12px;
        background: rgba(255,255,255,0.54);
      }}
      .v0812-manual-study-type {{
        display: inline-flex;
        border-radius: 999px;
        padding: 4px 8px;
        font-size: 13px;
        font-weight: 900;
        border: 1px solid rgba(31,78,121,0.24);
        background: rgba(31,78,121,0.08);
        margin-bottom: 8px;
      }}
      .v0812-policy-flag {{
        display: inline-flex;
        border-radius: 999px;
        padding: 4px 8px;
        font-size: 13px;
        font-weight: 800;
        border: 1px solid rgba(31,78,121,0.24);
        background: rgba(31,78,121,0.08);
        margin: 2px 4px 2px 0;
      }}
      /* VOILA_V0_8_12_MANUAL_STUDY_ITEMS_PREVIEW_VIEWER_CSS_END */
      /* VOILA_V0_8_13_MANUAL_STUDY_ROUTE_READ_ONLY_PREVIEW_CSS_START */
      .v0813-manual-study {{
        margin: 14px 0;
        border: 1px solid rgba(31,78,121,0.24);
        border-radius: 18px;
        padding: 14px;
        background: rgba(31,78,121,0.045);
      }}
      .v0813-study-shell {{
        display: grid;
        gap: 14px;
        margin-top: 14px;
      }}
      .v0813-study-card {{
        border: 1px solid rgba(31,78,121,0.22);
        border-radius: 18px;
        padding: 14px;
        background: rgba(255,255,255,0.58);
      }}
      .v0813-study-card h3 {{
        margin: 4px 0 10px;
      }}
      .v0813-study-chip {{
        display: inline-flex;
        border-radius: 999px;
        padding: 4px 8px;
        font-size: 13px;
        font-weight: 900;
        border: 1px solid rgba(31,78,121,0.24);
        background: rgba(31,78,121,0.08);
        margin: 2px 4px 8px 0;
      }}
      .v0813-study-prompt {{
        border-left: 4px solid rgba(31,78,121,0.55);
        padding: 8px 10px;
        background: rgba(31,78,121,0.055);
        border-radius: 10px;
      }}
      .v0813-study-answer {{
        margin-top: 10px;
        border: 1px solid rgba(31,78,121,0.18);
        border-radius: 14px;
        padding: 10px;
        background: rgba(255,255,255,0.55);
      }}
      .v0813-study-meta {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 10px;
        margin: 12px 0;
      }}
      .v0813-study-meta-card {{
        border: 1px solid rgba(31,78,121,0.18);
        border-radius: 14px;
        padding: 10px;
        background: rgba(255,255,255,0.50);
      }}
      /* VOILA_V0_8_13_MANUAL_STUDY_ROUTE_READ_ONLY_PREVIEW_CSS_END */
      /* VOILA_V0_8_14_MANUAL_STUDY_PREVIEW_COURSE_TOOLS_LINK_CSS_START */
      .v0814-manual-study-tools-link {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border-radius: 999px;
        padding: 8px 11px;
        margin: 4px 6px 4px 0;
        font-weight: 900;
        text-decoration: none;
        border: 1px solid rgba(31,78,121,0.26);
        background: rgba(31,78,121,0.08);
      }}
      .v0814-manual-study-tools-status {{
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 5px 9px;
        margin: 4px 6px 4px 0;
        font-size: 13px;
        font-weight: 900;
        border: 1px solid rgba(31,78,121,0.22);
        background: rgba(255,255,255,0.52);
      }}
      .v0814-manual-study-tools-status.ready {{
        background: rgba(38,128,91,0.10);
      }}
      .v0814-manual-study-tools-status.missing {{
        background: rgba(190,128,36,0.10);
      }}
      /* VOILA_V0_8_14_MANUAL_STUDY_PREVIEW_COURSE_TOOLS_LINK_CSS_END */
      /* VOILA_V0_8_15_MANUAL_STUDY_PREVIEW_NAVIGATION_POLISH_CSS_START */
      .v0815-study-top-nav {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
        margin: 12px 0 16px;
      }}
      .v0815-study-top-nav a,
      .v0815-study-card-nav a {{
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 7px 10px;
        font-size: 13px;
        font-weight: 900;
        text-decoration: none;
        border: 1px solid rgba(31,78,121,0.26);
        background: rgba(31,78,121,0.08);
      }}
      .v0815-study-card-nav {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 12px 0 4px;
      }}
      .v0815-study-position {{
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 5px 9px;
        font-size: 13px;
        font-weight: 900;
        border: 1px solid rgba(31,78,121,0.18);
        background: rgba(255,255,255,0.55);
      }}
      .v0815-study-focus-hint {{
        margin-top: 8px;
        font-size: 13px;
        opacity: 0.82;
      }}
      .v0813-study-card:target {{
        outline: 3px solid rgba(31,78,121,0.45);
        scroll-margin-top: 18px;
      }}
      /* VOILA_V0_8_15_MANUAL_STUDY_PREVIEW_NAVIGATION_POLISH_CSS_END */
      /* VOILA_V0_7_98_MANUAL_LEARNING_EVIDENCE_CROP_SELECTION_PREVIEW_END */
      @media (max-width: 860px) {{
        .v0796-grid {{
          grid-template-columns: 1fr;
        }}
      }}
    </style>

    <h1>Manual Learning Evidence · skeleton</h1>
    <p class="meta">
      Owner-local · read-only · follows v0.7.94 Direction Charter and v0.7.95 UI design.
    </p>

    <div class="toolbar">
      <a class="btn" href="{back_url}">Back to Course Tools</a>
      <a class="btn" href="{formula_viewer_url}">Formula Visual Evidence viewer</a>
      <a class="btn" href="{prev_url}">Previous page</a>
      <a class="btn" href="{next_url}">Next page</a>
    </div>

    <div class="v0797-readonly-banner">
      <strong>Skeleton only · read-only.</strong>
      This page supports browser-only crop selection preview and can save a draft evidence JSON item.
      Future evidence will be saved to <code>manual_learning_evidence.json</code>.
      <div class="v0797-status-row">
        <span class="v0797-chip">crop preview only</span>
        <span class="v0797-chip">draft save enabled</span>
        <span class="v0797-chip">draft list read-only</span>
        <span class="v0797-chip">verify draft enabled</span>
        <span class="v0797-chip">reject draft enabled</span>
        <span class="v0797-chip">review summary read-only</span>
        <span class="v0797-chip">accepted preview read-only</span>
        <span class="v0797-chip">quality gate read-only</span>
        <span class="v0797-chip">learning pack dry-run read-only</span>
        <span class="v0797-chip">learning pack draft export</span>
        <span class="v0797-chip">learning pack preview viewer</span>
        <span class="v0797-chip">study adapter dry-run</span>
        <span class="v0797-chip">manual study preview export</span>
        <span class="v0797-chip">manual study preview viewer</span>
        <span class="v0797-chip">manual study route preview</span>
        <span class="v0797-chip">manual study Course Tools link</span>
        <span class="v0797-chip">manual study navigation polish</span>
        <span class="v0797-chip">Learning Pack disabled</span>
        <span class="v0797-chip">owner-local only</span>
      </div>
      <ul class="v0797-next-steps">
        <li>Selectează un dreptunghi pe pagina sursă pentru preview local în browser.</li>
        <li>Save draft scrie doar în <code>manual_learning_evidence.json</code>.</li>
        <li>Learning Pack nu consumă încă acest ecran.</li>
      </ul>
    </div>

    <p class="meta">
      course_id: <code>{safe_course_id_html}</code><br>
      page: <code>{safe_page}</code><br>
      source_state: <code>{source_state}</code><br>
      output_dir: <code>{output_dir_html}</code><br>
      manual_evidence_json_exists: <code>{manual_evidence_json_exists}</code><br>
      manual_evidence_item_count: <code>{manual_evidence_item_count}</code>
    </p>

    <div class="v0796-grid">
      <section>
        <h2>1. Source page</h2>
        {page_image_html}
      </section>

      <section class="v0798-preview-panel">
        <h2>2. Crop selection preview</h2>
        <p class="meta" id="v0798CropHelp">Drag on the source page to preview a crop. Preview only; no file is written.</p>
        <code class="v0798-bbox" id="v0798BboxText">bbox_px=[]</code>
        <input id="v0799BoundBboxPreview" class="v0799-readonly-field" value="bbox_px=[]" readonly disabled>
        <canvas class="v0798-preview-canvas" id="v0798PreviewCanvas" width="640" height="220" aria-label="Crop preview canvas"></canvas>
        <div class="v0796-disabled-note">
          Draft save enabled. Writes manual_learning_evidence.json only. No crop file write.
        </div>
      </section>

      <section class="v0796-form">
        <h2>3. Evidence metadata form</h2>
        <p class="meta">Read-only placeholder. Save endpoint is intentionally absent in v0.7.98.</p>

        <label>title</label>
        <input id="v0799TitlePreview" value="" placeholder="Example: Modulul vectorului AB" disabled>

        <label>kind</label>
        <select id="v0799KindPreview" disabled>
          <option>formula</option>
          <option>definition</option>
          <option>example</option>
          <option>theorem</option>
          <option>diagram</option>
          <option>drawing</option>
          <option>note</option>
        </select>

        <label>verified_text</label>
        <textarea id="v0799VerifiedTextPreview" rows="4" placeholder="Owner-verified text/formula goes here" disabled></textarea>

        <label>explanation_ro</label>
        <textarea id="v0799ExplanationPreview" rows="4" placeholder="Explicație scurtă verificată de owner" disabled></textarea>

        <label>source_status</label>
        <select id="v0799SourceStatusPreview" disabled>
          <option>verified</option>
          <option>uncertain</option>
          <option>possible_source_error</option>
        </select>

        <label>source_note</label>
        <textarea id="v0799SourceNotePreview" rows="3" placeholder="Observații despre sursă / posibile greșeli" disabled></textarea>

        <label>status</label>
        <select id="v0799StatusPreview" disabled>
          <option>pending_owner_review</option>
          <option>accepted_owner_verified</option>
          <option>rejected_noise</option>
        </select>

        <div class="v0799-pending-preview">
          <strong>Pending evidence preview</strong>
          <p class="meta">Browser-only preview. Nothing is saved in v0.7.99.</p>
          <textarea id="v0799PendingEvidencePreview" readonly disabled>{{
  "status": "pending_owner_review",
  "bbox": [],
  "save_enabled": false
}}</textarea>

          <form class="v080-save-draft-form" method="post" action="/owner/manual-learning-evidence/{safe_course_id_url}/save-draft">
            <input type="hidden" name="draft_id" value="ui-draft-{safe_course_id_html}-p{safe_page}">
            <input type="hidden" name="page" value="{safe_page}">
            <input type="hidden" id="v080SaveDraftBbox" name="bbox" value="">
            <input type="hidden" name="kind" value="formula">
            <input type="hidden" name="title" value="">
            <input type="hidden" name="verified_text" value="">
            <input type="hidden" name="explanation_ro" value="">
            <input type="hidden" name="source_status" value="uncertain">
            <input type="hidden" name="source_note" value="">
            <button id="v080SaveDraftButton" type="submit">Save draft evidence</button>
            <p class="meta">Owner-local POST. Writes only <code>manual_learning_evidence.json</code>. No crop file. No Learning Pack.</p>
          </form>
        </div>

        <div class="v0796-disabled-note">
          Draft save enabled. Crop file write disabled. Learning Pack integration disabled.
        </div>
      </section>
    </div>

    <h2>4. Draft evidence list</h2>
    <p class="meta">Read-only list from <code>manual_learning_evidence.json</code>. No accept/verify action in v0.8.1.</p>
    {manual_evidence_list_html}

    <script>
      // VOILA_V0_7_98_MANUAL_LEARNING_EVIDENCE_CROP_SELECTION_PREVIEW_JS_START
      (function () {{
        const shell = document.getElementById("v0798CropShell");
        const image = document.getElementById("v0798SourceImage");
        const box = document.getElementById("v0798SelectionBox");
        const bboxText = document.getElementById("v0798BboxText");
        const canvas = document.getElementById("v0798PreviewCanvas");
        const help = document.getElementById("v0798CropHelp");
        // VOILA_V0_7_99_MANUAL_LEARNING_EVIDENCE_METADATA_PREVIEW_BINDING_JS_START
        const boundBboxPreview = document.getElementById("v0799BoundBboxPreview");
        const pendingEvidencePreview = document.getElementById("v0799PendingEvidencePreview");
        const titlePreview = document.getElementById("v0799TitlePreview");
        const kindPreview = document.getElementById("v0799KindPreview");
        const verifiedTextPreview = document.getElementById("v0799VerifiedTextPreview");
        const explanationPreview = document.getElementById("v0799ExplanationPreview");
        const sourceStatusPreview = document.getElementById("v0799SourceStatusPreview");
        const sourceNotePreview = document.getElementById("v0799SourceNotePreview");
        const statusPreview = document.getElementById("v0799StatusPreview");
        // VOILA_V0_8_0_MANUAL_LEARNING_EVIDENCE_SAVE_DRAFT_JSON_JS_START
        const saveDraftBboxInput = document.getElementById("v080SaveDraftBbox");
        // VOILA_V0_8_0_MANUAL_LEARNING_EVIDENCE_SAVE_DRAFT_JSON_JS_END
        // VOILA_V0_7_99_MANUAL_LEARNING_EVIDENCE_METADATA_PREVIEW_BINDING_JS_END

        if (!shell || !image || !box || !bboxText || !canvas || !help || !boundBboxPreview || !pendingEvidencePreview) {{
          return;
        }}

        const ctx = canvas.getContext("2d");
        let active = false;
        let startPoint = null;

        function clamp(value, min, max) {{
          return Math.min(Math.max(value, min), max);
        }}

        function pointFromEvent(event) {{
          const rect = image.getBoundingClientRect();
          const cssX = clamp(event.clientX - rect.left, 0, rect.width);
          const cssY = clamp(event.clientY - rect.top, 0, rect.height);
          const scaleX = image.naturalWidth && rect.width ? image.naturalWidth / rect.width : 1;
          const scaleY = image.naturalHeight && rect.height ? image.naturalHeight / rect.height : 1;
          return {{
            cssX: cssX,
            cssY: cssY,
            imgX: Math.round(cssX * scaleX),
            imgY: Math.round(cssY * scaleY),
          }};
        }}

        function clearPreview() {{
          ctx.clearRect(0, 0, canvas.width, canvas.height);
        }}

        // VOILA_V0_7_99_MANUAL_LEARNING_EVIDENCE_PENDING_PREVIEW_START
        function fieldValue(element, fallback) {{
          if (!element) {{
            return fallback;
          }}
          return element.value || fallback;
        }}

        function updatePendingEvidencePreview(bbox, cropW, cropH) {{
          const bboxTextValue = "bbox_px=[" + bbox.join(", ") + "]";
          boundBboxPreview.value = bboxTextValue;
          if (saveDraftBboxInput) {{
            saveDraftBboxInput.value = JSON.stringify(bbox);
          }}

          const pending = {{
            artifact: "manual_learning_evidence.preview",
            course_id: "{safe_course_id_html}",
            page: {safe_page},
            bbox: bbox,
            crop_size: [cropW, cropH],
            kind: fieldValue(kindPreview, "formula"),
            title: fieldValue(titlePreview, ""),
            verified_text: fieldValue(verifiedTextPreview, ""),
            explanation_ro: fieldValue(explanationPreview, ""),
            source_status: fieldValue(sourceStatusPreview, "verified"),
            source_note: fieldValue(sourceNotePreview, ""),
            status: fieldValue(statusPreview, "pending_owner_review"),
            save_enabled: false,
            manual_learning_evidence_written: false,
            crop_file_written: false,
            learning_pack_changed: false
          }};

          pendingEvidencePreview.value = JSON.stringify(pending, null, 2);
        }}
        // VOILA_V0_7_99_MANUAL_LEARNING_EVIDENCE_PENDING_PREVIEW_END

        function updateSelection(point) {{
          if (!startPoint) {{
            return;
          }}

          const left = Math.min(startPoint.cssX, point.cssX);
          const top = Math.min(startPoint.cssY, point.cssY);
          const width = Math.abs(point.cssX - startPoint.cssX);
          const height = Math.abs(point.cssY - startPoint.cssY);

          box.hidden = width < 2 || height < 2;
          box.style.left = left + "px";
          box.style.top = top + "px";
          box.style.width = width + "px";
          box.style.height = height + "px";

          const x1 = Math.min(startPoint.imgX, point.imgX);
          const y1 = Math.min(startPoint.imgY, point.imgY);
          const x2 = Math.max(startPoint.imgX, point.imgX);
          const y2 = Math.max(startPoint.imgY, point.imgY);
          const cropW = Math.max(0, x2 - x1);
          const cropH = Math.max(0, y2 - y1);

          const bbox = [x1, y1, x2, y2];
          bboxText.textContent = "bbox_px=[" + bbox.join(", ") + "] · size=" + cropW + "x" + cropH;
          updatePendingEvidencePreview(bbox, cropW, cropH);

          if (cropW < 2 || cropH < 2 || !image.complete) {{
            clearPreview();
            return;
          }}

          const maxWidth = 640;
          const previewScale = Math.min(1, maxWidth / cropW);
          canvas.width = Math.max(1, Math.round(cropW * previewScale));
          canvas.height = Math.max(1, Math.round(cropH * previewScale));
          ctx.drawImage(image, x1, y1, cropW, cropH, 0, 0, canvas.width, canvas.height);
        }}

        shell.addEventListener("pointerdown", function (event) {{
          event.preventDefault();
          active = true;
          startPoint = pointFromEvent(event);
          shell.setPointerCapture(event.pointerId);
          help.textContent = "Selecting crop preview… release pointer to keep the preview.";
          updateSelection(startPoint);
        }});

        shell.addEventListener("pointermove", function (event) {{
          if (!active) {{
            return;
          }}
          event.preventDefault();
          updateSelection(pointFromEvent(event));
        }});

        shell.addEventListener("pointerup", function (event) {{
          if (!active) {{
            return;
          }}
          event.preventDefault();
          active = false;
          updateSelection(pointFromEvent(event));
          help.textContent = "Crop preview ready. Save is disabled in v0.7.98.";
        }});

        shell.addEventListener("pointercancel", function () {{
          active = false;
          help.textContent = "Crop selection cancelled. Save is disabled in v0.7.98.";
        }});
      }})();
      // VOILA_V0_7_98_MANUAL_LEARNING_EVIDENCE_CROP_SELECTION_PREVIEW_JS_END
    </script>
    """

    return page("Manual Learning Evidence · skeleton", body)

# VOILA_V0_8_0_MANUAL_LEARNING_EVIDENCE_SAVE_DRAFT_ENDPOINT_START
def _voila_v080_clean_text(value, max_len: int = 4000) -> str:
    cleaned = str(value or "").replace("\x00", "").strip()
    return cleaned[:max_len]


def _voila_v080_normalize_bbox(value):
    import json as _json

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            value = _json.loads(raw)
        except Exception:
            parts = [part.strip() for part in raw.replace("[", "").replace("]", "").split(",")]
            value = parts

    if not isinstance(value, (list, tuple)) or len(value) != 4:
        return None

    try:
        bbox = [int(round(float(part))) for part in value]
    except Exception:
        return None

    x1, y1, x2, y2 = bbox
    if x2 <= x1 or y2 <= y1:
        return None
    if min(bbox) < 0:
        return None
    return bbox


async def _voila_v080_request_payload(request: Request) -> dict:
    import json as _json
    from urllib.parse import parse_qs as _parse_qs

    content_type = str(request.headers.get("content-type") or "").lower()

    if "application/json" in content_type:
        try:
            data = await request.json()
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    raw = await request.body()
    decoded = raw.decode("utf-8", errors="replace")
    parsed = _parse_qs(decoded, keep_blank_values=True)
    return {str(key): (values[-1] if values else "") for key, values in parsed.items()}


@app.post("/owner/manual-learning-evidence/{course_id}/save-draft", include_in_schema=False)
async def owner_manual_learning_evidence_save_draft(course_id: str, request: Request):
    import json as _json
    import re as _re
    from datetime import datetime as _datetime, timezone as _timezone
    from fastapi.responses import JSONResponse as _JSONResponse

    safe_course_id = _voila_v0796_safe_course_id(course_id)
    output_dir = _voila_v0796_manual_learning_evidence_dir(safe_course_id)

    if not output_dir.exists() or not output_dir.is_dir():
        return _JSONResponse(
            {
                "ok": False,
                "error": "course_output_dir_missing",
                "manual_learning_evidence_written": False,
                "crop_file_written": False,
                "learning_pack_changed": False,
            },
            status_code=404,
        )

    payload = await _voila_v080_request_payload(request)
    bbox = _voila_v080_normalize_bbox(payload.get("bbox"))

    if bbox is None:
        return _JSONResponse(
            {
                "ok": False,
                "error": "valid_bbox_required",
                "manual_learning_evidence_written": False,
                "crop_file_written": False,
                "learning_pack_changed": False,
            },
            status_code=400,
        )

    try:
        page_value = max(1, int(str(payload.get("page") or "1").strip()))
    except Exception:
        page_value = 1

    kind_allowed = {"formula", "definition", "example", "theorem", "diagram", "drawing", "note"}
    source_status_allowed = {"verified", "uncertain", "possible_source_error"}

    kind = _voila_v080_clean_text(payload.get("kind"), 80) or "note"
    if kind not in kind_allowed:
        kind = "note"

    source_status = _voila_v080_clean_text(payload.get("source_status"), 80) or "uncertain"
    if source_status not in source_status_allowed:
        source_status = "uncertain"

    requested_draft_id = _voila_v080_clean_text(payload.get("draft_id"), 120)
    draft_id = _re.sub(r"[^A-Za-z0-9_.-]+", "-", requested_draft_id).strip("-._")

    created_at_utc = _datetime.now(_timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if not draft_id:
        draft_id = "draft-" + created_at_utc.replace(":", "").replace("-", "").replace("Z", "")

    crop_size = [bbox[2] - bbox[0], bbox[3] - bbox[1]]
    target = output_dir / "manual_learning_evidence.json"

    if target.exists():
        try:
            existing = _json.loads(target.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            return _JSONResponse(
                {
                    "ok": False,
                    "error": "manual_learning_evidence_json_invalid",
                    "manual_learning_evidence_written": False,
                    "crop_file_written": False,
                    "learning_pack_changed": False,
                },
                status_code=409,
            )
    else:
        existing = {}

    if isinstance(existing, list):
        data = {
            "schema": "voila.manual_learning_evidence.v0",
            "course_id": safe_course_id,
            "items": existing,
        }
    elif isinstance(existing, dict):
        data = existing
        data.setdefault("schema", "voila.manual_learning_evidence.v0")
        data.setdefault("course_id", safe_course_id)
        data.setdefault("items", [])
    else:
        return _JSONResponse(
            {
                "ok": False,
                "error": "manual_learning_evidence_json_shape_invalid",
                "manual_learning_evidence_written": False,
                "crop_file_written": False,
                "learning_pack_changed": False,
            },
            status_code=409,
        )

    if not isinstance(data.get("items"), list):
        return _JSONResponse(
            {
                "ok": False,
                "error": "manual_learning_evidence_items_invalid",
                "manual_learning_evidence_written": False,
                "crop_file_written": False,
                "learning_pack_changed": False,
            },
            status_code=409,
        )

    item = {
        "id": draft_id,
        "course_id": safe_course_id,
        "page": page_value,
        "bbox": bbox,
        "crop_size": crop_size,
        "kind": kind,
        "title": _voila_v080_clean_text(payload.get("title"), 300),
        "verified_text": _voila_v080_clean_text(payload.get("verified_text"), 4000),
        "explanation_ro": _voila_v080_clean_text(payload.get("explanation_ro"), 4000),
        "source_status": source_status,
        "source_note": _voila_v080_clean_text(payload.get("source_note"), 2000),
        "status": "pending_owner_review",
        "owner_verified": False,
        "save_state": "draft",
        "created_at_utc": created_at_utc,
        "source": "manual_learning_evidence_ui_v0.8.0",
        "crop_file_written": False,
        "learning_pack_changed": False,
        "course_generation_changed": False,
        "study_changed": False,
        "progress_changed": False,
    }

    data["items"] = [
        existing_item
        for existing_item in data.get("items", [])
        if not (isinstance(existing_item, dict) and existing_item.get("id") == draft_id)
    ]
    data["items"].append(item)

    data["updated_at_utc"] = created_at_utc
    data["manual_learning_evidence_written"] = True
    data["crop_file_written"] = False
    data["learning_pack_changed"] = False

    target.write_text(_json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return _JSONResponse(
        {
            "ok": True,
            "draft_id": draft_id,
            "manual_learning_evidence_written": True,
            "manual_learning_evidence_path": str(target),
            "crop_file_written": False,
            "learning_pack_changed": False,
            "course_generation_changed": False,
            "study_changed": False,
            "progress_changed": False,
            "item_count": len(data["items"]),
        }
    )
# VOILA_V0_8_0_MANUAL_LEARNING_EVIDENCE_SAVE_DRAFT_ENDPOINT_END

# VOILA_V0_8_2_MANUAL_LEARNING_EVIDENCE_VERIFY_DRAFT_ENDPOINT_START
@app.post("/owner/manual-learning-evidence/{course_id}/verify-draft", include_in_schema=False)
async def owner_manual_learning_evidence_verify_draft(course_id: str, request: Request):
    import json as _json
    from datetime import datetime as _datetime, timezone as _timezone
    from fastapi.responses import JSONResponse as _JSONResponse

    safe_course_id = _voila_v0796_safe_course_id(course_id)
    output_dir = _voila_v0796_manual_learning_evidence_dir(safe_course_id)
    target = output_dir / "manual_learning_evidence.json"

    if not output_dir.exists() or not output_dir.is_dir():
        return _JSONResponse(
            {
                "ok": False,
                "error": "course_output_dir_missing",
                "manual_learning_evidence_written": False,
                "crop_file_written": False,
                "learning_pack_changed": False,
            },
            status_code=404,
        )

    if not target.exists() or not target.is_file():
        return _JSONResponse(
            {
                "ok": False,
                "error": "manual_learning_evidence_json_missing",
                "manual_learning_evidence_written": False,
                "crop_file_written": False,
                "learning_pack_changed": False,
            },
            status_code=404,
        )

    payload = await _voila_v080_request_payload(request)
    draft_id = _voila_v080_clean_text(payload.get("draft_id"), 160)

    if not draft_id:
        return _JSONResponse(
            {
                "ok": False,
                "error": "draft_id_required",
                "manual_learning_evidence_written": False,
                "crop_file_written": False,
                "learning_pack_changed": False,
            },
            status_code=400,
        )

    try:
        data = _json.loads(target.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return _JSONResponse(
            {
                "ok": False,
                "error": "manual_learning_evidence_json_invalid",
                "manual_learning_evidence_written": False,
                "crop_file_written": False,
                "learning_pack_changed": False,
            },
            status_code=409,
        )

    if isinstance(data, list):
        data = {
            "schema": "voila.manual_learning_evidence.v0",
            "course_id": safe_course_id,
            "items": data,
        }

    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        return _JSONResponse(
            {
                "ok": False,
                "error": "manual_learning_evidence_items_invalid",
                "manual_learning_evidence_written": False,
                "crop_file_written": False,
                "learning_pack_changed": False,
            },
            status_code=409,
        )

    target_item = None
    for item in data["items"]:
        if isinstance(item, dict) and str(item.get("id") or "") == draft_id:
            target_item = item
            break

    if target_item is None:
        return _JSONResponse(
            {
                "ok": False,
                "error": "draft_not_found",
                "draft_id": draft_id,
                "manual_learning_evidence_written": False,
                "crop_file_written": False,
                "learning_pack_changed": False,
            },
            status_code=404,
        )

    verified_at_utc = _datetime.now(_timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    target_item["status"] = "accepted_owner_verified"
    target_item["owner_verified"] = True
    target_item["save_state"] = "verified"
    target_item["verified_at_utc"] = verified_at_utc
    target_item["verified_by"] = "owner"
    target_item["crop_file_written"] = False
    target_item["learning_pack_changed"] = False
    target_item["course_generation_changed"] = False
    target_item["study_changed"] = False
    target_item["progress_changed"] = False

    data["updated_at_utc"] = verified_at_utc
    data["manual_learning_evidence_written"] = True
    data["crop_file_written"] = False
    data["learning_pack_changed"] = False

    target.write_text(_json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return _JSONResponse(
        {
            "ok": True,
            "draft_id": draft_id,
            "status": "accepted_owner_verified",
            "owner_verified": True,
            "manual_learning_evidence_written": True,
            "manual_learning_evidence_path": str(target),
            "crop_file_written": False,
            "learning_pack_changed": False,
            "course_generation_changed": False,
            "study_changed": False,
            "progress_changed": False,
        }
    )
# VOILA_V0_8_2_MANUAL_LEARNING_EVIDENCE_VERIFY_DRAFT_ENDPOINT_END

# VOILA_V0_8_3_MANUAL_LEARNING_EVIDENCE_REJECT_DRAFT_ENDPOINT_START
@app.post("/owner/manual-learning-evidence/{course_id}/reject-draft", include_in_schema=False)
async def owner_manual_learning_evidence_reject_draft(course_id: str, request: Request):
    import json as _json
    from datetime import datetime as _datetime, timezone as _timezone
    from fastapi.responses import JSONResponse as _JSONResponse

    safe_course_id = _voila_v0796_safe_course_id(course_id)
    output_dir = _voila_v0796_manual_learning_evidence_dir(safe_course_id)
    target = output_dir / "manual_learning_evidence.json"

    if not output_dir.exists() or not output_dir.is_dir():
        return _JSONResponse(
            {
                "ok": False,
                "error": "course_output_dir_missing",
                "manual_learning_evidence_written": False,
                "crop_file_written": False,
                "learning_pack_changed": False,
            },
            status_code=404,
        )

    if not target.exists() or not target.is_file():
        return _JSONResponse(
            {
                "ok": False,
                "error": "manual_learning_evidence_json_missing",
                "manual_learning_evidence_written": False,
                "crop_file_written": False,
                "learning_pack_changed": False,
            },
            status_code=404,
        )

    payload = await _voila_v080_request_payload(request)
    draft_id = _voila_v080_clean_text(payload.get("draft_id"), 160)
    rejection_reason = _voila_v080_clean_text(payload.get("rejection_reason"), 240) or "owner_rejected_noise"

    if not draft_id:
        return _JSONResponse(
            {
                "ok": False,
                "error": "draft_id_required",
                "manual_learning_evidence_written": False,
                "crop_file_written": False,
                "learning_pack_changed": False,
            },
            status_code=400,
        )

    try:
        data = _json.loads(target.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return _JSONResponse(
            {
                "ok": False,
                "error": "manual_learning_evidence_json_invalid",
                "manual_learning_evidence_written": False,
                "crop_file_written": False,
                "learning_pack_changed": False,
            },
            status_code=409,
        )

    if isinstance(data, list):
        data = {
            "schema": "voila.manual_learning_evidence.v0",
            "course_id": safe_course_id,
            "items": data,
        }

    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        return _JSONResponse(
            {
                "ok": False,
                "error": "manual_learning_evidence_items_invalid",
                "manual_learning_evidence_written": False,
                "crop_file_written": False,
                "learning_pack_changed": False,
            },
            status_code=409,
        )

    target_item = None
    for item in data["items"]:
        if isinstance(item, dict) and str(item.get("id") or "") == draft_id:
            target_item = item
            break

    if target_item is None:
        return _JSONResponse(
            {
                "ok": False,
                "error": "draft_not_found",
                "draft_id": draft_id,
                "manual_learning_evidence_written": False,
                "crop_file_written": False,
                "learning_pack_changed": False,
            },
            status_code=404,
        )

    rejected_at_utc = _datetime.now(_timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    target_item["status"] = "rejected_noise"
    target_item["owner_verified"] = False
    target_item["save_state"] = "rejected"
    target_item["rejected_at_utc"] = rejected_at_utc
    target_item["rejected_by"] = "owner"
    target_item["rejection_reason"] = rejection_reason
    target_item["crop_file_written"] = False
    target_item["learning_pack_changed"] = False
    target_item["course_generation_changed"] = False
    target_item["study_changed"] = False
    target_item["progress_changed"] = False

    data["updated_at_utc"] = rejected_at_utc
    data["manual_learning_evidence_written"] = True
    data["crop_file_written"] = False
    data["learning_pack_changed"] = False

    target.write_text(_json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return _JSONResponse(
        {
            "ok": True,
            "draft_id": draft_id,
            "status": "rejected_noise",
            "owner_verified": False,
            "save_state": "rejected",
            "manual_learning_evidence_written": True,
            "manual_learning_evidence_path": str(target),
            "crop_file_written": False,
            "learning_pack_changed": False,
            "course_generation_changed": False,
            "study_changed": False,
            "progress_changed": False,
        }
    )
# VOILA_V0_8_3_MANUAL_LEARNING_EVIDENCE_REJECT_DRAFT_ENDPOINT_END

# VOILA_V0_8_8_MANUAL_LEARNING_PACK_EXPORT_DRAFT_ENDPOINT_START
@app.post("/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft")
def owner_manual_learning_evidence_export_learning_pack_draft(course_id: str):
    safe_course_id = _voila_v090_validate_course_id(course_id)

    output_root = Path("data") / "output"
    output_dir = None
    if output_root.exists():
        for candidate_dir in output_root.iterdir():
            if candidate_dir.is_dir() and candidate_dir.name == safe_course_id:
                output_dir = candidate_dir
                break

    if output_dir is None:
        raise HTTPException(status_code=404, detail="Course output folder not found")

    evidence_path = output_dir / "manual_learning_evidence.json"
    preview_path = output_dir / "manual_learning_pack.preview.json"

    items = []
    if evidence_path.exists():
        try:
            payload = json.loads(evidence_path.read_text(encoding="utf-8", errors="replace"))
            if isinstance(payload, dict) and isinstance(payload.get("items"), list):
                items = payload.get("items") or []
        except Exception:
            items = []

    preview_payload = _voila_v088_manual_learning_pack_payload(safe_course_id, items)
    preview_path.write_text(json.dumps(preview_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return RedirectResponse(
        url="/?learning_pack_preview_exported=1",
        status_code=303,
    )
# VOILA_V0_8_8_MANUAL_LEARNING_PACK_EXPORT_DRAFT_ENDPOINT_END

# VOILA_V0_8_9_MANUAL_LEARNING_PACK_PREVIEW_VIEWER_START
def _voila_v089_find_existing_course_output_dir(course_id: str):
    safe_course_id = _voila_v090_validate_course_id(course_id)
    output_root = Path("data") / "output"
    if not output_root.exists():
        return None, safe_course_id

    for candidate_dir in output_root.iterdir():
        if candidate_dir.is_dir() and candidate_dir.name == safe_course_id:
            return candidate_dir, safe_course_id

    return None, safe_course_id


def _voila_v089_pack_preview_policy_html(policy):
    if not isinstance(policy, dict):
        policy = {}

    keys = [
        "learning_pack_preview_only",
        "course_generation_changed",
        "study_changed",
        "progress_changed",
        "ocr_rewrite_performed",
        "formula_ocr_performed",
        "build_performed",
        "zip_created",
        "share_created",
        "delivery_performed",
        "distribution_performed",
    ]

    badges = []
    for key in keys:
        value = policy.get(key)
        badges.append(
            f'<span class="v089-policy-ok">{html.escape(str(key), quote=True)}=<code>{html.escape(str(value), quote=True)}</code></span>'
        )

    return "".join(badges)


def _voila_v089_pack_preview_items_html(items):
    if not isinstance(items, list):
        items = []

    if not items:
        return '<p class="meta" data-testid="manual-learning-pack-preview-empty">Nu există itemuri exportate în preview.</p>'

    cards = []
    for item in items[:100]:
        if not isinstance(item, dict):
            continue

        source_evidence_id = html.escape(str(item.get("source_evidence_id") or ""), quote=True)
        title = html.escape(str(item.get("title") or "(fără titlu)"), quote=True)
        kind = html.escape(str(item.get("kind") or ""), quote=True)
        verified_text = html.escape(str(item.get("verified_text") or ""), quote=True)
        explanation_ro = html.escape(str(item.get("explanation_ro") or ""), quote=True)
        page_value = html.escape(str(item.get("page") or ""), quote=True)
        source_status = html.escape(str(item.get("source_status") or ""), quote=True)
        bbox = item.get("bbox")
        if isinstance(bbox, list):
            bbox_text = "[" + ", ".join(html.escape(str(part), quote=True) for part in bbox) + "]"
        else:
            bbox_text = html.escape(str(bbox or ""), quote=True)

        cards.append(
            f"""
            <article class="v089-pack-item" data-testid="manual-learning-pack-preview-item">
              <h3>{title}</h3>
              <p class="meta">
                source_evidence_id: <code>{source_evidence_id}</code><br>
                kind: <code>{kind}</code> · page: <code>{page_value}</code> · source_status: <code>{source_status}</code>
              </p>
              <p><strong>Verified text</strong><br>{verified_text}</p>
              <p><strong>Explicație RO</strong><br>{explanation_ro}</p>
              <p>bbox: <code>{bbox_text}</code></p>
            </article>
            """
        )

    return "".join(cards)


@app.get("/owner/manual-learning-pack-preview/{course_id}")
def owner_manual_learning_pack_preview_viewer(course_id: str):
    output_dir, safe_course_id = _voila_v089_find_existing_course_output_dir(course_id)
    if output_dir is None:
        raise HTTPException(status_code=404, detail="Course output folder not found")

    preview_path = output_dir / "manual_learning_pack.preview.json"
    if not preview_path.exists():
        raise HTTPException(status_code=404, detail="manual_learning_pack.preview.json not found")

    try:
        pack = json.loads(preview_path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        raise HTTPException(status_code=500, detail="manual_learning_pack.preview.json could not be read")

    if not isinstance(pack, dict):
        raise HTTPException(status_code=500, detail="manual_learning_pack.preview.json is invalid")

    schema = html.escape(str(pack.get("schema") or ""), quote=True)
    artifact = html.escape(str(pack.get("artifact") or ""), quote=True)
    mode = html.escape(str(pack.get("mode") or ""), quote=True)
    generated_by = html.escape(str(pack.get("generated_by") or ""), quote=True)
    source = html.escape(str(pack.get("source") or ""), quote=True)
    course_label = html.escape(str(safe_course_id), quote=True)

    items = pack.get("items") if isinstance(pack.get("items"), list) else []
    items_count = len(items)

    policy_html = _voila_v089_pack_preview_policy_html(pack.get("policy"))
    items_html = _voila_v089_pack_preview_items_html(items)

    body = f"""
    <section class="v089-pack-viewer" data-testid="manual-learning-pack-preview-viewer">
      <h1>Manual Learning Pack Preview</h1>
      <p class="meta">
        Read-only viewer pentru <code>manual_learning_pack.preview.json</code>.
        Nu conectează Study/Course/Progress și nu rescrie OCR/course.
        Study adapter dry-run: <code>/owner/manual-learning-pack-study-adapter-dry-run/{course_label}</code>.
      </p>

      <div class="v089-pack-meta-grid">
        <div class="v089-pack-meta-card" data-testid="manual-learning-pack-preview-schema">
          <strong>schema</strong><br><code>{schema}</code>
        </div>
        <div class="v089-pack-meta-card" data-testid="manual-learning-pack-preview-course">
          <strong>course_id</strong><br><code>{course_label}</code>
        </div>
        <div class="v089-pack-meta-card" data-testid="manual-learning-pack-preview-items-count">
          <strong>items_count</strong><br><code>{items_count}</code>
        </div>
        <div class="v089-pack-meta-card">
          <strong>artifact</strong><br><code>{artifact}</code>
        </div>
        <div class="v089-pack-meta-card">
          <strong>source</strong><br><code>{source}</code>
        </div>
        <div class="v089-pack-meta-card">
          <strong>mode</strong><br><code>{mode}</code>
        </div>
        <div class="v089-pack-meta-card">
          <strong>generated_by</strong><br><code>{generated_by}</code>
        </div>
      </div>

      <h2>Policy flags</h2>
      <div data-testid="manual-learning-pack-preview-policy">
        {policy_html}
      </div>

      <h2>Preview items</h2>
      <div class="v089-pack-item-grid" data-testid="manual-learning-pack-preview-items">
        {items_html}
      </div>
    </section>
    """

    return page("Manual Learning Pack Preview", body)
# VOILA_V0_8_9_MANUAL_LEARNING_PACK_PREVIEW_VIEWER_END

# VOILA_V0_8_11_MANUAL_STUDY_ITEMS_PREVIEW_EXPORT_START
def _voila_v0811_manual_study_items_preview_payload(course_id, dry_run_items):
    if not isinstance(dry_run_items, list):
        dry_run_items = []

    items = []
    for item in dry_run_items:
        if not isinstance(item, dict):
            continue

        items.append({
            "source_evidence_id": str(item.get("source_evidence_id") or ""),
            "manual_study_item_id": str(item.get("dry_run_id") or ""),
            "study_item_type": str(item.get("study_item_type") or ""),
            "title": str(item.get("title") or ""),
            "prompt": str(item.get("prompt") or ""),
            "answer": str(item.get("answer") or ""),
            "source_page": item.get("source_page"),
            "source_bbox": item.get("source_bbox"),
            "source_kind": str(item.get("source_kind") or ""),
            "source_status": str(item.get("source_status") or ""),
            "owner_verified_source": True,
            "write_target": "manual_study_items.preview.json",
        })

    return {
        "schema": "voila.manual_study_items.preview.v1",
        "course_id": str(course_id or ""),
        "source": "manual_learning_pack.preview.json",
        "artifact": "manual_study_items.preview.json",
        "mode": "owner_local_manual_study_items_preview",
        "generated_by": "v0.8.11_manual_study_items_preview_export_json",
        "items_count": len(items),
        "items": items,
        "policy": {
            "manual_study_preview_only": True,
            "legacy_study_items_preview_untouched": True,
            "study_integration": False,
            "course_generation_changed": False,
            "study_changed": False,
            "progress_changed": False,
            "ocr_rewrite_performed": False,
            "formula_ocr_performed": False,
            "build_performed": False,
            "zip_created": False,
            "share_created": False,
            "delivery_performed": False,
            "distribution_performed": False,
        },
    }


def _voila_v0811_manual_study_items_export_form_html(course_id, dry_run_count):
    safe_course_id = _voila_v090_validate_course_id(str(course_id or ""))
    action_path = f"/owner/manual-learning-pack-study-adapter-dry-run/{safe_course_id}/export-manual-study-items-preview"

    disabled = "" if dry_run_count > 0 else " disabled"
    label = "Exportă manual_study_items.preview.json" if dry_run_count > 0 else "Export blocat: nu există candidate Study items"

    return f"""
    <div class="v0811-study-export" data-testid="manual-study-items-preview-export">
      <strong>Manual Study Items preview export</strong>
      <p class="meta">
        Scrie doar artifact separat <code>manual_study_items.preview.json</code>.
        Nu atinge vechiul <code>study_items.preview.json</code> și nu conectează Study real.
      </p>
      <form method="post" action="{action_path}">
        <button class="v0811-study-export-button" type="submit"{disabled} data-testid="manual-study-items-preview-export-button">{html.escape(label, quote=True)}</button>
      </form>
      <p class="meta v0811-study-export-note">
        candidate Study items: <code>{dry_run_count}</code>.
        Viewer route: <code>/owner/manual-study-items-preview/{safe_course_id}</code>.
        No Course/Progress/OCR rewrite. No build/ZIP/share/delivery.
      </p>
    </div>
    """
# VOILA_V0_8_11_MANUAL_STUDY_ITEMS_PREVIEW_EXPORT_END


# VOILA_V0_8_10_MANUAL_LEARNING_PACK_STUDY_ADAPTER_DRY_RUN_START
def _voila_v0810_study_adapter_type(kind):
    kind_value = str(kind or "").strip().lower()
    if kind_value == "formula":
        return "formula_card"
    if kind_value == "definition":
        return "concept_card"
    if kind_value == "definiție":
        return "concept_card"
    if kind_value == "example":
        return "worked_example_card"
    if kind_value == "exemplu":
        return "worked_example_card"
    if kind_value == "theorem":
        return "theorem_card"
    if kind_value == "teoremă":
        return "theorem_card"
    return "concept_card"


def _voila_v0810_build_study_adapter_dry_run_items(pack_items):
    if not isinstance(pack_items, list):
        pack_items = []

    dry_run_items = []
    for index, item in enumerate(pack_items, start=1):
        if not isinstance(item, dict):
            continue

        title = str(item.get("title") or "").strip()
        verified_text = str(item.get("verified_text") or "").strip()
        explanation_ro = str(item.get("explanation_ro") or "").strip()
        kind = str(item.get("kind") or "").strip()

        if not title or not verified_text or not explanation_ro:
            continue

        adapter_type = _voila_v0810_study_adapter_type(kind)
        source_evidence_id = str(item.get("source_evidence_id") or "").strip()

        dry_run_items.append({
            "dry_run_id": f"study-dry-run-{index}",
            "source_evidence_id": source_evidence_id,
            "study_item_type": adapter_type,
            "title": title,
            "prompt": verified_text,
            "answer": explanation_ro,
            "source_page": item.get("page"),
            "source_bbox": item.get("bbox"),
            "source_kind": kind,
            "source_status": str(item.get("source_status") or ""),
            "write_target": "none",
        })

    return dry_run_items


def _voila_v0810_study_adapter_items_html(items):
    if not isinstance(items, list):
        items = []

    if not items:
        return '<p class="meta" data-testid="manual-learning-pack-study-adapter-empty">Nu există candidate Study items pentru dry-run.</p>'

    cards = []
    for item in items[:100]:
        dry_run_id = html.escape(str(item.get("dry_run_id") or ""), quote=True)
        source_evidence_id = html.escape(str(item.get("source_evidence_id") or ""), quote=True)
        study_item_type = html.escape(str(item.get("study_item_type") or ""), quote=True)
        title = html.escape(str(item.get("title") or "(fără titlu)"), quote=True)
        prompt = html.escape(str(item.get("prompt") or ""), quote=True)
        answer = html.escape(str(item.get("answer") or ""), quote=True)
        source_page = html.escape(str(item.get("source_page") or ""), quote=True)
        source_kind = html.escape(str(item.get("source_kind") or ""), quote=True)
        source_status = html.escape(str(item.get("source_status") or ""), quote=True)
        bbox = item.get("source_bbox")
        if isinstance(bbox, list):
            bbox_text = "[" + ", ".join(html.escape(str(part), quote=True) for part in bbox) + "]"
        else:
            bbox_text = html.escape(str(bbox or ""), quote=True)

        cards.append(
            f"""
            <article class="v0810-study-card" data-testid="manual-learning-pack-study-adapter-item">
              <span class="v0810-study-type">{study_item_type}</span>
              <h3>{title}</h3>
              <p class="meta">
                dry_run_id: <code>{dry_run_id}</code><br>
                source_evidence_id: <code>{source_evidence_id}</code><br>
                source_kind: <code>{source_kind}</code> · source_status: <code>{source_status}</code> · page: <code>{source_page}</code>
              </p>
              <p><strong>Study prompt</strong><br>{prompt}</p>
              <p><strong>Study answer</strong><br>{answer}</p>
              <p>source bbox: <code>{bbox_text}</code></p>
              <p class="meta">write_target: <code>none</code> · dry-run only</p>
            </article>
            """
        )

    return "".join(cards)


@app.get("/owner/manual-learning-pack-study-adapter-dry-run/{course_id}")
def owner_manual_learning_pack_study_adapter_dry_run(course_id: str):
    output_dir, safe_course_id = _voila_v089_find_existing_course_output_dir(course_id)
    if output_dir is None:
        raise HTTPException(status_code=404, detail="Course output folder not found")

    preview_path = output_dir / "manual_learning_pack.preview.json"
    if not preview_path.exists():
        raise HTTPException(status_code=404, detail="manual_learning_pack.preview.json not found")

    try:
        pack = json.loads(preview_path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        raise HTTPException(status_code=500, detail="manual_learning_pack.preview.json could not be read")

    if not isinstance(pack, dict):
        raise HTTPException(status_code=500, detail="manual_learning_pack.preview.json is invalid")

    pack_items = pack.get("items") if isinstance(pack.get("items"), list) else []
    dry_run_items = _voila_v0810_build_study_adapter_dry_run_items(pack_items)
    items_html = _voila_v0810_study_adapter_items_html(dry_run_items)

    schema = html.escape(str(pack.get("schema") or ""), quote=True)
    course_label = html.escape(str(safe_course_id), quote=True)
    pack_count = len(pack_items)
    dry_run_count = len(dry_run_items)

    body = f"""
    <section class="v0810-study-adapter" data-testid="manual-learning-pack-study-adapter-dry-run">
      <h1>Manual Learning Pack → Study Adapter Dry-run</h1>
      <p class="meta">
        Read-only adapter preview. Transformă în memorie <code>manual_learning_pack.preview.json</code>
        în candidate Study items. Nu scrie niciun Study artifact și nu conectează Study real.
      </p>

      <div class="v0810-study-meta-grid">
        <div class="v0810-study-meta-card" data-testid="manual-learning-pack-study-adapter-schema">
          <strong>source schema</strong><br><code>{schema}</code>
        </div>
        <div class="v0810-study-meta-card" data-testid="manual-learning-pack-study-adapter-course">
          <strong>course_id</strong><br><code>{course_label}</code>
        </div>
        <div class="v0810-study-meta-card" data-testid="manual-learning-pack-study-adapter-source-count">
          <strong>source preview items</strong><br><code>{pack_count}</code>
        </div>
        <div class="v0810-study-meta-card" data-testid="manual-learning-pack-study-adapter-dry-run-count">
          <strong>candidate Study items</strong><br><code>{dry_run_count}</code>
        </div>
      </div>

      <p class="meta" data-testid="manual-learning-pack-study-adapter-policy">
        write_target=<code>none</code>;
        study_integration=<code>false</code>;
        course_generation_changed=<code>false</code>;
        progress_changed=<code>false</code>;
        build_performed=<code>false</code>;
        zip_created=<code>false</code>;
        delivery_performed=<code>false</code>.
      </p>

      {_voila_v0811_manual_study_items_export_form_html(safe_course_id, dry_run_count)}

      <div class="v0810-study-grid" data-testid="manual-learning-pack-study-adapter-items">
        {items_html}
      </div>
    </section>
    """

    return page("Manual Learning Pack Study Adapter Dry-run", body)
# VOILA_V0_8_10_MANUAL_LEARNING_PACK_STUDY_ADAPTER_DRY_RUN_END

# VOILA_V0_8_11_MANUAL_STUDY_ITEMS_PREVIEW_EXPORT_ENDPOINT_START
@app.post("/owner/manual-learning-pack-study-adapter-dry-run/{course_id}/export-manual-study-items-preview")
def owner_manual_study_items_preview_export(course_id: str):
    output_dir, safe_course_id = _voila_v089_find_existing_course_output_dir(course_id)
    if output_dir is None:
        raise HTTPException(status_code=404, detail="Course output folder not found")

    learning_pack_preview_path = output_dir / "manual_learning_pack.preview.json"
    manual_study_preview_path = output_dir / "manual_study_items.preview.json"

    if not learning_pack_preview_path.exists():
        raise HTTPException(status_code=404, detail="manual_learning_pack.preview.json not found")

    try:
        pack = json.loads(learning_pack_preview_path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        raise HTTPException(status_code=500, detail="manual_learning_pack.preview.json could not be read")

    if not isinstance(pack, dict):
        raise HTTPException(status_code=500, detail="manual_learning_pack.preview.json is invalid")

    pack_items = pack.get("items") if isinstance(pack.get("items"), list) else []
    dry_run_items = _voila_v0810_build_study_adapter_dry_run_items(pack_items)
    preview_payload = _voila_v0811_manual_study_items_preview_payload(safe_course_id, dry_run_items)

    manual_study_preview_path.write_text(json.dumps(preview_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return RedirectResponse(
        url="/?manual_study_items_preview_exported=1",
        status_code=303,
    )
# VOILA_V0_8_11_MANUAL_STUDY_ITEMS_PREVIEW_EXPORT_ENDPOINT_END

# VOILA_V0_8_12_MANUAL_STUDY_ITEMS_PREVIEW_VIEWER_START
def _voila_v0812_manual_study_policy_html(policy):
    if not isinstance(policy, dict):
        policy = {}

    keys = [
        "manual_study_preview_only",
        "legacy_study_items_preview_untouched",
        "study_integration",
        "course_generation_changed",
        "study_changed",
        "progress_changed",
        "ocr_rewrite_performed",
        "formula_ocr_performed",
        "build_performed",
        "zip_created",
        "share_created",
        "delivery_performed",
        "distribution_performed",
    ]

    flags = []
    for key in keys:
        value = policy.get(key)
        flags.append(
            f'<span class="v0812-policy-flag">{html.escape(str(key), quote=True)}=<code>{html.escape(str(value), quote=True)}</code></span>'
        )

    return "".join(flags)


def _voila_v0812_manual_study_items_html(items):
    if not isinstance(items, list):
        items = []

    if not items:
        return '<p class="meta" data-testid="manual-study-items-preview-empty">Nu există candidate Study items exportate.</p>'

    cards = []
    for item in items[:100]:
        if not isinstance(item, dict):
            continue

        manual_study_item_id = html.escape(str(item.get("manual_study_item_id") or ""), quote=True)
        source_evidence_id = html.escape(str(item.get("source_evidence_id") or ""), quote=True)
        study_item_type = html.escape(str(item.get("study_item_type") or ""), quote=True)
        title = html.escape(str(item.get("title") or "(fără titlu)"), quote=True)
        prompt = html.escape(str(item.get("prompt") or ""), quote=True)
        answer = html.escape(str(item.get("answer") or ""), quote=True)
        source_page = html.escape(str(item.get("source_page") or ""), quote=True)
        source_kind = html.escape(str(item.get("source_kind") or ""), quote=True)
        source_status = html.escape(str(item.get("source_status") or ""), quote=True)
        write_target = html.escape(str(item.get("write_target") or ""), quote=True)

        bbox = item.get("source_bbox")
        if isinstance(bbox, list):
            bbox_text = "[" + ", ".join(html.escape(str(part), quote=True) for part in bbox) + "]"
        else:
            bbox_text = html.escape(str(bbox or ""), quote=True)

        cards.append(
            f"""
            <article class="v0812-manual-study-item" data-testid="manual-study-items-preview-item">
              <span class="v0812-manual-study-type">{study_item_type}</span>
              <h3>{title}</h3>
              <p class="meta">
                manual_study_item_id: <code>{manual_study_item_id}</code><br>
                source_evidence_id: <code>{source_evidence_id}</code><br>
                source_kind: <code>{source_kind}</code> · source_status: <code>{source_status}</code> · source_page: <code>{source_page}</code>
              </p>
              <p><strong>Prompt</strong><br>{prompt}</p>
              <p><strong>Answer</strong><br>{answer}</p>
              <p>source_bbox: <code>{bbox_text}</code></p>
              <p class="meta">write_target: <code>{write_target}</code></p>
            </article>
            """
        )

    return "".join(cards)


@app.get("/owner/manual-study-items-preview/{course_id}")
def owner_manual_study_items_preview_viewer(course_id: str):
    output_dir, safe_course_id = _voila_v089_find_existing_course_output_dir(course_id)
    if output_dir is None:
        raise HTTPException(status_code=404, detail="Course output folder not found")

    preview_path = output_dir / "manual_study_items.preview.json"
    if not preview_path.exists():
        raise HTTPException(status_code=404, detail="manual_study_items.preview.json not found")

    try:
        payload = json.loads(preview_path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        raise HTTPException(status_code=500, detail="manual_study_items.preview.json could not be read")

    if not isinstance(payload, dict):
        raise HTTPException(status_code=500, detail="manual_study_items.preview.json is invalid")

    schema = html.escape(str(payload.get("schema") or ""), quote=True)
    artifact = html.escape(str(payload.get("artifact") or ""), quote=True)
    source = html.escape(str(payload.get("source") or ""), quote=True)
    mode = html.escape(str(payload.get("mode") or ""), quote=True)
    generated_by = html.escape(str(payload.get("generated_by") or ""), quote=True)
    course_label = html.escape(str(safe_course_id), quote=True)

    items = payload.get("items") if isinstance(payload.get("items"), list) else []
    items_count = len(items)

    policy_html = _voila_v0812_manual_study_policy_html(payload.get("policy"))
    items_html = _voila_v0812_manual_study_items_html(items)

    body = f"""
    <section class="v0812-manual-study-viewer" data-testid="manual-study-items-preview-viewer">
      <h1>Manual Study Items Preview</h1>
      <p class="meta">
        Read-only viewer pentru <code>manual_study_items.preview.json</code>.
        Nu conectează Study real, nu atinge legacy <code>study_items.preview.json</code>,
        nu schimbă Course/Progress/OCR și nu face build/ZIP/delivery.
        Manual Study Preview: <code>/owner/manual-study-preview/{course_label}</code>.
      </p>

      <div class="v0812-manual-study-meta-grid">
        <div class="v0812-manual-study-meta-card" data-testid="manual-study-items-preview-schema">
          <strong>schema</strong><br><code>{schema}</code>
        </div>
        <div class="v0812-manual-study-meta-card" data-testid="manual-study-items-preview-course">
          <strong>course_id</strong><br><code>{course_label}</code>
        </div>
        <div class="v0812-manual-study-meta-card" data-testid="manual-study-items-preview-items-count">
          <strong>items_count</strong><br><code>{items_count}</code>
        </div>
        <div class="v0812-manual-study-meta-card">
          <strong>artifact</strong><br><code>{artifact}</code>
        </div>
        <div class="v0812-manual-study-meta-card">
          <strong>source</strong><br><code>{source}</code>
        </div>
        <div class="v0812-manual-study-meta-card">
          <strong>mode</strong><br><code>{mode}</code>
        </div>
        <div class="v0812-manual-study-meta-card">
          <strong>generated_by</strong><br><code>{generated_by}</code>
        </div>
      </div>

      <h2>Policy flags</h2>
      <div data-testid="manual-study-items-preview-policy">
        {policy_html}
      </div>

      <h2>Candidate Study items</h2>
      <div class="v0812-manual-study-items" data-testid="manual-study-items-preview-items">
        {items_html}
      </div>
    </section>
    """

    return page("Manual Study Items Preview", body)
# VOILA_V0_8_12_MANUAL_STUDY_ITEMS_PREVIEW_VIEWER_END

# VOILA_V0_8_13_MANUAL_STUDY_ROUTE_READ_ONLY_PREVIEW_START
def _voila_v0813_manual_study_preview_cards_html(items):
    if not isinstance(items, list):
        items = []

    valid_items = [item for item in items if isinstance(item, dict)]

    if not valid_items:
        return '<p class="meta" data-testid="manual-study-preview-empty">Nu există carduri manual Study disponibile.</p>'

    total = len(valid_items)
    quick_links = []
    cards = []

    for index, item in enumerate(valid_items[:100], start=1):
        card_id = f"manual-study-card-{index}"
        title = html.escape(str(item.get("title") or f"Card {index}"), quote=True)
        quick_links.append(
            f'<a href="#{html.escape(card_id, quote=True)}" data-testid="manual-study-preview-nav-jump">Card {index}</a>'
        )

    quick_nav_html = (
        '<nav class="v0815-study-top-nav" data-testid="manual-study-preview-top-navigation">'
        '<span class="v0815-study-position">Navigare carduri</span>'
        + "".join(quick_links[:40])
        + '</nav>'
    )

    for index, item in enumerate(valid_items[:100], start=1):
        card_id = f"manual-study-card-{index}"
        prev_id = f"manual-study-card-{index - 1}" if index > 1 else ""
        next_id = f"manual-study-card-{index + 1}" if index < min(total, 100) else ""

        manual_study_item_id = html.escape(str(item.get("manual_study_item_id") or f"manual-study-{index}"), quote=True)
        source_evidence_id = html.escape(str(item.get("source_evidence_id") or ""), quote=True)
        study_item_type = html.escape(str(item.get("study_item_type") or ""), quote=True)
        title = html.escape(str(item.get("title") or "(fără titlu)"), quote=True)
        prompt = html.escape(str(item.get("prompt") or ""), quote=True)
        answer = html.escape(str(item.get("answer") or ""), quote=True)
        source_page = html.escape(str(item.get("source_page") or ""), quote=True)
        source_kind = html.escape(str(item.get("source_kind") or ""), quote=True)
        source_status = html.escape(str(item.get("source_status") or ""), quote=True)

        bbox = item.get("source_bbox")
        if isinstance(bbox, list):
            bbox_text = "[" + ", ".join(html.escape(str(part), quote=True) for part in bbox) + "]"
        else:
            bbox_text = html.escape(str(bbox or ""), quote=True)

        previous_link = (
            f'<a href="#{html.escape(prev_id, quote=True)}" data-testid="manual-study-preview-prev">← Previous</a>'
            if prev_id
            else '<span class="v0815-study-position" data-testid="manual-study-preview-prev-disabled">Start</span>'
        )
        next_link = (
            f'<a href="#{html.escape(next_id, quote=True)}" data-testid="manual-study-preview-next">Next →</a>'
            if next_id
            else '<span class="v0815-study-position" data-testid="manual-study-preview-next-disabled">Final</span>'
        )

        cards.append(
            f"""
            <article id="{html.escape(card_id, quote=True)}" class="v0813-study-card" data-testid="manual-study-preview-card">
              <span class="v0813-study-chip">manual Study preview</span>
              <span class="v0813-study-chip">{study_item_type}</span>
              <span class="v0815-study-position" data-testid="manual-study-preview-position">Card {index} / {total}</span>
              <h3>{index}. {title}</h3>

              <div class="v0813-study-prompt" data-testid="manual-study-preview-prompt">
                <strong>Întrebare / prompt</strong><br>{prompt}
              </div>

              <details class="v0813-study-answer" data-testid="manual-study-preview-answer">
                <summary><strong>Arată răspunsul</strong></summary>
                <p>{answer}</p>
              </details>

              <nav class="v0815-study-card-nav" data-testid="manual-study-preview-card-navigation">
                {previous_link}
                <a href="#manual-study-preview-top" data-testid="manual-study-preview-back-to-top">Sus ↑</a>
                {next_link}
              </nav>

              <p class="meta v0815-study-focus-hint">
                Navigarea este doar cu ancore locale. Nu se scrie progres și nu se marchează răspunsuri.
              </p>

              <p class="meta" data-testid="manual-study-preview-source">
                manual_study_item_id: <code>{manual_study_item_id}</code><br>
                source_evidence_id: <code>{source_evidence_id}</code><br>
                source_kind: <code>{source_kind}</code> · source_status: <code>{source_status}</code><br>
                source_page: <code>{source_page}</code> · source_bbox: <code>{bbox_text}</code>
              </p>
            </article>
            """
        )

    return quick_nav_html + "".join(cards)


@app.get("/owner/manual-study-preview/{course_id}")
def owner_manual_study_route_read_only_preview(course_id: str):
    output_dir, safe_course_id = _voila_v089_find_existing_course_output_dir(course_id)
    if output_dir is None:
        raise HTTPException(status_code=404, detail="Course output folder not found")

    preview_path = output_dir / "manual_study_items.preview.json"
    if not preview_path.exists():
        raise HTTPException(status_code=404, detail="manual_study_items.preview.json not found")

    try:
        payload = json.loads(preview_path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        raise HTTPException(status_code=500, detail="manual_study_items.preview.json could not be read")

    if not isinstance(payload, dict):
        raise HTTPException(status_code=500, detail="manual_study_items.preview.json is invalid")

    items = payload.get("items") if isinstance(payload.get("items"), list) else []
    cards_html = _voila_v0813_manual_study_preview_cards_html(items)

    schema = html.escape(str(payload.get("schema") or ""), quote=True)
    course_label = html.escape(str(safe_course_id), quote=True)
    items_count = len(items)

    body = f"""
    <section id="manual-study-preview-top" class="v0813-manual-study" data-testid="manual-study-preview-route">
      <h1>Manual Study Preview</h1>
      <p class="meta">
        Read-only Study-like preview bazat pe <code>manual_study_items.preview.json</code>.
        Nu înlocuiește <code>/study</code>, nu scrie progres, nu marchează răspunsuri
        și nu atinge legacy <code>study_items.preview.json</code>.
      </p>

      <div class="v0813-study-meta">
        <div class="v0813-study-meta-card" data-testid="manual-study-preview-schema">
          <strong>schema</strong><br><code>{schema}</code>
        </div>
        <div class="v0813-study-meta-card" data-testid="manual-study-preview-course">
          <strong>course_id</strong><br><code>{course_label}</code>
        </div>
        <div class="v0813-study-meta-card" data-testid="manual-study-preview-items-count">
          <strong>items_count</strong><br><code>{items_count}</code>
        </div>
        <div class="v0813-study-meta-card" data-testid="manual-study-preview-policy">
          <strong>policy</strong><br>
          progress_write=<code>false</code><br>
          answer_marking=<code>false</code><br>
          local_anchor_navigation=<code>true</code><br>
          replaces_study_route=<code>false</code><br>
          build_performed=<code>false</code><br>
          delivery_performed=<code>false</code>
        </div>
      </div>

      <div class="v0813-study-shell" data-testid="manual-study-preview-cards">
        {cards_html}
      </div>
    </section>
    """

    return page("Manual Study Preview", body)
# VOILA_V0_8_13_MANUAL_STUDY_ROUTE_READ_ONLY_PREVIEW_END









# VOILA_V0_7_96_MANUAL_LEARNING_EVIDENCE_UI_SKELETON_END




@app.get("/study", response_class=HTMLResponse)
def study(pdf: str = Query(...)) -> HTMLResponse:
    pdf_path = validate_pdf_name(pdf)
    output_dir = OUTPUT_DIR / pdf_path.stem

    try:
        view = get_study_view(output_dir)
    except Exception as exc:
        body = f"""
        <h1>{_ut("ui.study_mode", "Modul Studiu")}</h1>
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
          {_ut("study.concept_mastery_changed", "Nivelul conceptului s-a schimbat de la")} <strong>{before}%</strong> {_ut("to", "to")} <strong>{after}%</strong>.
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

        recommendation_reason = html.escape(_voila_v080_study_recommendation_reason_label(str(current.get("recommendation_reason") or "")))
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
      {_ut("study.current_overall_mastery", "Nivel general curent")}: <strong>{view.get("overall_mastery_percent")}%</strong> ·
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
    return Path(str(value or "")).name


def _nav_output_dir(pdf_name: str) -> Path:
    return PROJECT_ROOT / "data" / "output" / Path(pdf_name).stem


def _nav_quote(value: str) -> str:
    return quote(str(value or ""))


def _nav_escape(value: str) -> str:
    return html.escape(str(value or ""), quote=True)


def _course_tools_button_html(pdf_name: str) -> str:
    safe = Path(str(pdf_name or "")).name
    q = quote(safe)
    return f'<a class="tool-link primary-tool" href="/course-tools?pdf={q}">{_ut("ui.course_tools", "Course Tools")}</a>'


def _voila_tools_bar(pdf_name: str, active: str = "") -> str:
    q = _nav_quote(pdf_name)

    course_id = str(pdf_name or "").replace(".pdf", "")
    links = [
        (_ut("ui.course_tools", "Course Tools"), f"/course-tools?pdf={q}", "tools"),
        (_ut("ui.open_course", _ut("open_course", "Open course")), f"/course-open?pdf={q}", "course"),
        ("Lessons", f"/lessons?pdf={q}", "lessons"),
        (_ut("ui.study", _ut("study", "Study")), f"/study?pdf={q}", "study"),
        (_ut("ui.progress", _ut("progress", "Progress")), f"/progress?pdf={q}", "progress"),
        (_ut("ui.review_ocr_text", "Review OCR Text"), f"/review-ocr-corrected?pdf={q}&page=1", "ocr"),
        (_ut("ui.review_concepts", "Review Concepts"), f"/review-concepts?pdf={q}", "concepts"),
        (_ut("ui.figures", "Figures"), f"/view-figures?pdf={q}", "figures"),
        (_ut("ui.edit_crops", "Edit crops"), f"/edit-crops?pdf={q}", "crops"),
        ("OCR Math", f"/owner/ocr-math-report/{_nav_quote(course_id)}/view", "ocr_math"),
        (_ut("ui.exam_prep", "Exam Prep"), "/exam-prep", "exam_prep"),
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



# VOILA_V0_8_14_MANUAL_STUDY_PREVIEW_COURSE_TOOLS_LINK_START
def _voila_v0814_manual_study_preview_course_tools_link_html(course_id):
    try:
        safe_course_id = _voila_v090_validate_course_id(str(course_id or ""))
    except Exception:
        return ""

    output_dir, _safe_course_id = _voila_v089_find_existing_course_output_dir(safe_course_id)
    ready = bool(output_dir is not None and (output_dir / "manual_study_items.preview.json").exists())

    status_text = "Manual Study preview: OK" if ready else "Manual Study preview: lipsește manual_study_items.preview.json"
    status_class = "ready" if ready else "missing"
    href = "/owner/manual-study-preview/" + safe_course_id

    return (
        '<a class="v0814-manual-study-tools-link" '
        'data-testid="manual-study-preview-course-tools-link" '
        f'href="{html.escape(href, quote=True)}">Manual Study Preview</a>'
        f'<span class="v0814-manual-study-tools-status {html.escape(status_class, quote=True)}" '
        'data-testid="manual-study-preview-course-tools-status">'
        f'{html.escape(status_text, quote=True)}</span>'
    )


def _voila_v0814_manual_study_preview_course_tools_fallback_html():
    output_root = Path("data") / "output"
    if not output_root.exists():
        return ""

    links = []
    for candidate_dir in sorted(output_root.iterdir(), key=lambda item: item.name):
        if not candidate_dir.is_dir():
            continue
        if not (candidate_dir / "manual_study_items.preview.json").exists():
            continue

        link_html = _voila_v0814_manual_study_preview_course_tools_link_html(candidate_dir.name)
        if link_html:
            links.append(
                '<div class="v0814-manual-study-tools-status ready" '
                'data-testid="manual-study-preview-course-tools-fallback-item">'
                f'{link_html}</div>'
            )

    if not links:
        return (
            '<section class="card" data-testid="manual-study-preview-course-tools-fallback">'
            '<h2>Manual Study Preview</h2>'
            '<span class="v0814-manual-study-tools-status missing" '
            'data-testid="manual-study-preview-course-tools-status">'
            'Manual Study preview: lipsește manual_study_items.preview.json</span>'
            '</section>'
        )

    return (
        '<section class="card" data-testid="manual-study-preview-course-tools-fallback">'
        '<h2>Manual Study Preview</h2>'
        '<p class="meta">Preview read-only din manual_study_items.preview.json. '
        'Nu scrie progres și nu înlocuiește /study.</p>'
        + "".join(links)
        + '</section>'
    )


def _voila_v0814_inject_manual_study_preview_course_tools_link(body):
    if not isinstance(body, str):
        return body

    marker = 'href="/owner/manual-learning-evidence/'
    search_from = 0
    changed = False

    while True:
        marker_pos = body.find(marker, search_from)
        if marker_pos < 0:
            break

        course_start = marker_pos + len(marker)
        course_end = body.find("?page=1", course_start)
        if course_end < 0:
            search_from = marker_pos + len(marker)
            continue

        anchor_end = body.find("</a>", course_end)
        if anchor_end < 0:
            search_from = course_end
            continue
        anchor_end += len("</a>")

        course_id = body[course_start:course_end]
        if "manual-study-preview-course-tools-link" in body[anchor_end:anchor_end + 700]:
            search_from = anchor_end
            continue

        injected = _voila_v0814_manual_study_preview_course_tools_link_html(course_id)
        body = body[:anchor_end] + injected + body[anchor_end:]
        search_from = anchor_end + len(injected)
        changed = True

    if changed:
        return body

    if "manual-study-preview-course-tools-fallback" in body:
        return body

    fallback = _voila_v0814_manual_study_preview_course_tools_fallback_html()
    if not fallback:
        return body

    body_close = body.rfind("</main>")
    if body_close >= 0:
        return body[:body_close] + fallback + body[body_close:]

    return body + fallback
# VOILA_V0_8_14_MANUAL_STUDY_PREVIEW_COURSE_TOOLS_LINK_END

# VOILA_V0_8_14_MANUAL_STUDY_PREVIEW_COURSE_TOOLS_LINK_MIDDLEWARE_START
@app.middleware("http")
async def voila_v0814_manual_study_preview_course_tools_link_middleware(request, call_next):
    response = await call_next(request)

    if str(getattr(request, "method", "")).upper() != "GET":
        return response

    if str(getattr(getattr(request, "url", None), "path", "")) != "/course-tools":
        return response

    try:
        status_code = int(getattr(response, "status_code", 0) or 0)
    except Exception:
        status_code = 0

    if status_code != 200:
        return response

    media_type = str(getattr(response, "media_type", "") or "")
    content_type = ""
    try:
        content_type = str(response.headers.get("content-type", "") or "")
    except Exception:
        content_type = ""

    if "html" not in media_type.lower() and "html" not in content_type.lower():
        return response

    try:
        chunks = []
        async for chunk in response.body_iterator:
            chunks.append(chunk)
        body_bytes = b"".join(chunks)
        body_text = body_bytes.decode("utf-8", errors="replace")
    except Exception:
        return response

    if "manual-study-preview-course-tools-link" not in body_text:
        fallback = _voila_v0814_manual_study_preview_course_tools_fallback_html()
        if fallback:
            close_main = body_text.rfind("</main>")
            if close_main >= 0:
                body_text = body_text[:close_main] + fallback + body_text[close_main:]
            else:
                close_body = body_text.rfind("</body>")
                if close_body >= 0:
                    body_text = body_text[:close_body] + fallback + body_text[close_body:]
                else:
                    body_text = body_text + fallback

    from fastapi.responses import HTMLResponse
    return HTMLResponse(
        content=body_text,
        status_code=status_code,
        headers=dict(response.headers),
    )
# VOILA_V0_8_14_MANUAL_STUDY_PREVIEW_COURSE_TOOLS_LINK_MIDDLEWARE_END




@app.get("/course-tools")
def course_tools(pdf: str = Query("")):
    pdf_name = str(pdf or "").strip()

    if not pdf_name:
        return HTMLResponse("<h1>" + _ut("error.missing_pdf_name", "Missing PDF name") + "</h1>", status_code=400)

    try:
        pdf_path = validate_pdf_name(pdf_name)
    except Exception as exc:
        return HTMLResponse(
            "<h1>" + _ut("error.missing_pdf_name", "Missing PDF name") + "</h1>"
            + f"<p><code>{html.escape(str(exc))}</code></p>",
            status_code=400,
        )

    output_dir = OUTPUT_DIR / pdf_path.stem
    q = quote(pdf_path.name)

    course_md = output_dir / "course.cleaned.md"
    course_html = output_dir / "course.cleaned.html"
    quiz_json = output_dir / "quiz.json"
    quiz_study_json = output_dir / "quiz.study.json"
    # VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_START
    study_items_preview_json = output_dir / "study_items.preview.json"
    # VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_END
    flashcards_json = output_dir / "flashcards.json"
    glossary_json = output_dir / "glossary.json"
    pages_json = output_dir / "pages.json"
    ocr_pages_json = output_dir / "ocr_pages.json"
    figures_hybrid_html = output_dir / "figures_hybrid" / "figures_hybrid.html"
    figures_html = output_dir / "figures" / "figures.html"
    hybrid_manifest = output_dir / "figures_hybrid" / "figures_manifest.hybrid.json"
    # VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_COURSE_TOOLS_LINK_START
    formula_visual_manifest = output_dir / "formula_visual_evidence.manifest.json"
    # VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_COURSE_TOOLS_LINK_END

    course_available = course_html.exists() or course_md.exists()
    # VOILA_V0_7_87_STUDY_STATUS_COPY_CONSISTENCY_START
    def _voila_v087_preview_quality_pass(path) -> bool:
        try:
            import json as _json
            data = _json.loads(path.read_text(encoding="utf-8"))
            gate = data.get("quality_gate") if isinstance(data, dict) else {}
            return str((gate or {}).get("preview_quality_status") or "").strip().upper() == "PASS"
        except Exception:
            return False

    preview_quality_pass = study_items_preview_json.exists() and _voila_v087_preview_quality_pass(study_items_preview_json)
    study_available = quiz_json.exists() or quiz_study_json.exists() or preview_quality_pass
    # VOILA_V0_7_87_STUDY_STATUS_COPY_CONSISTENCY_END
    # VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_AVAILABLE_START
    study_items_preview_available = study_items_preview_json.exists()
    # VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_AVAILABLE_END
    ocr_available = pages_json.exists() or ocr_pages_json.exists()
    figures_available = figures_hybrid_html.exists() or figures_html.exists()
    crops_available = hybrid_manifest.exists()
    # VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_COURSE_TOOLS_AVAILABLE_START
    formula_visual_available = formula_visual_manifest.exists()
    formula_visual_candidate_count = None
    if formula_visual_available:
        try:
            import json as _json
            _formula_visual_data = _json.loads(formula_visual_manifest.read_text(encoding="utf-8"))
            formula_visual_candidate_count = _formula_visual_data.get("candidate_count")
        except Exception:
            formula_visual_candidate_count = None
    formula_visual_description = (
        "Viewer owner-local read-only pentru crop-uri vizuale formulă/simbol: imagine, pagină, bbox, text OCR, motiv detectare și status review."
    )
    if formula_visual_candidate_count is not None:
        formula_visual_description += " Candidați vizuali: " + html.escape(str(formula_visual_candidate_count)) + "."

    # VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_COURSE_TOOLS_AVAILABLE_END
    ocr_math_md, ocr_math_json = _voila_ocr_math_report_paths(pdf_path.stem)
    # VOILA_V0_7_34_OCR_MATH_CARD_AVAILABILITY_ONLY_START
    ocr_math_available = bool(ocr_math_md and ocr_math_md.is_file())
    ocr_math_summary_available = bool(ocr_math_json and ocr_math_json.is_file())
    ocr_math_description = (
        "Raport diagnostic local OCR Math disponibil. Read-only: nu modifică OCR-ul, cursul, Study sau Progress."
        if ocr_math_available
        else "Raportul OCR Math nu există încă. Lipsește ocr_math_report.md; raportul se creează doar când hook-ul local OCR Math este activ."
    )
    if ocr_math_available and not ocr_math_summary_available:
        ocr_math_description += " Sumarul JSON este opțional și lipsește momentan."
    # VOILA_V0_7_34_OCR_MATH_CARD_AVAILABILITY_ONLY_END

    if ocr_math_available:
        try:
            ocr_math_summary = _voila_ocr_math_report_summary(ocr_math_md, ocr_math_json)
            ocr_math_description += (
                " Sugestii detectate: "
                + html.escape(_voila_ocr_math_report_display_value(ocr_math_summary.get("total_suggestions")))
                + "."
            )
        except Exception:
            pass

    def card(title: str, description: str, href: str, available: bool, missing: str = "") -> str:
        title_html = html.escape(str(title))
        description_html = html.escape(str(description))
        status_label = _ut("ui.available", "Available") if available else _ut("ui.unavailable", "Unavailable")
        status_class = "ok" if available else "missing"

        if available:
            action = f'<a class="btn primary" href="{href}">{_ut("ui.open", "Open")}</a>'
        else:
            action = f'<span class="btn disabled">{_ut("ui.unavailable", "Unavailable")}</span>'

        missing_html = ""
        if missing and not available:
            missing_html = f'<p class="missing-note">{html.escape(missing)}</p>'

        return f"""
        <article class="tool-card {status_class}">
          <div class="tool-card-head">
            <h2>{title_html}</h2>
            <span class="tool-status {status_class}">{html.escape(status_label)}</span>
          </div>
          <p>{description_html}</p>
          {missing_html}
          <div class="actions">{action}</div>
        </article>
        """

    cards = [
        card(
            _ut("ui.open_course", _ut("open_course", "Open course")),
            "Deschide cursul generat. Dacă există doar course.cleaned.md, Voila reconstruiește automat course.cleaned.html.",
            f"/course-open?pdf={q}",
            course_available,
            "Lipsește course.cleaned.md. Rulează Generate pentru acest PDF.",
        ),
        card(
            _ut("ui.study", _ut("study", "Study")),
            "Întrebări de studiu din study_items.preview.json când Quality gate este PASS, cu fallback la quiz.json / quiz.study.json.",
            f"/study?pdf={q}",
            study_available,
            "Lipsește study_items.preview.json PASS sau quiz.json / quiz.study.json. Rulează Generate pentru acest PDF.",
        ),
        card(
            "Study Items Preview",
            "Previzualizare owner-local read-only pentru întrebările pedagogice generate din learning pack. Study folosește artifactul când Quality gate este PASS; nu modifică BKT sau Progress.",
            f"/owner/study-items-preview/{quote(pdf_path.stem, safe='')}/view",
            study_items_preview_available,
            "Lipsește study_items.preview.json. Rulează generatorul preview pentru acest curs.",
        ),
        card(
            _ut("ui.progress", _ut("progress", "Progress")),
            "Dashboard de progres pentru întrebările de studiu disponibile în Study.",
            f"/progress?pdf={q}",
            study_available,
            "Progress are nevoie de study_items.preview.json PASS sau quiz.json / quiz.study.json.",
        ),
        card(
            _ut("ui.review_ocr_text", "OCR Review"),
            "Revizuiește textul OCR extras din pages.json / ocr_pages.json.",
            f"/review-ocr-corrected?pdf={q}&page=1",
            ocr_available,
            "Lipsește pages.json sau ocr_pages.json. Rulează Generate/OCR pentru acest PDF.",
        ),
        card(
            _ut("ui.exam_prep", "Exam Prep"),
            "Dashboard pentru pregătire examen; disponibil ca flux separat.",
            "/exam-prep",
            True,
        ),
        card(
            "OCR Math Diagnostic",
            ocr_math_description,
            f"/owner/ocr-math-report/{quote(pdf_path.stem, safe='')}/view",
            ocr_math_available,
            "Lipsește ocr_math_report.md. Activează hook-ul local OCR Math și regenerează dacă vrei diagnostic.",
        ),
        card(
            "Formula Visual Evidence",
            formula_visual_description,
            f"/owner/formula-visual-evidence/{quote(pdf_path.stem, safe='')}/view",
            formula_visual_available,
            "Lipsește formula_visual_evidence.manifest.json. Rulează manifest builder local pentru crop-uri formulă/simbol.",
        ),
        card(
            _ut("ui.figures", "Figures"),
            "Galerie figuri extrase din document.",
            f"/view-figures?pdf={q}",
            figures_available,
            "Lipsește figures_hybrid.html sau figures.html.",
        ),
        card(
            _ut("ui.edit_crops", "Edit crops"),
            "Editor local pentru crop-uri de figuri.",
            f"/edit-crops?pdf={q}",
            crops_available,
            "Lipsește figures_manifest.hybrid.json.",
        ),
        card(
            "Quiz JSON",
            "Deschide quiz.json ca artefact local.",
            output_url(pdf_path.stem, "quiz.json"),
            quiz_json.exists(),
            "Lipsește quiz.json.",
        ),
        card(
            "Flashcards JSON",
            "Deschide flashcards.json ca artefact local.",
            output_url(pdf_path.stem, "flashcards.json"),
            flashcards_json.exists(),
            "Lipsește flashcards.json.",
        ),
        card(
            "Glossary JSON",
            "Deschide glossary.json ca artefact local.",
            output_url(pdf_path.stem, "glossary.json"),
            glossary_json.exists(),
            "Lipsește glossary.json.",
        ),
        card(
            _ut("ui.library", _ut("library", "Library")),
            "Înapoi la biblioteca principală.",
            "/",
            True,
        ),
    ]

    css = """
<style>
  :root {
    color-scheme: light dark;
    --bg: #efe3cc;
    --panel: #f8eedc;
    --text: #2f2a24;
    --muted: #75695c;
    --accent: #1F4E79;
    --border: rgba(31, 78, 121, 0.24);
    --ok: #2f6f6d;
    --missing: #9a5a2f;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #12191d;
      --panel: #20272b;
      --text: #f1e7d8;
      --muted: #b8afa3;
      --accent: #d7a86e;
      --border: rgba(215, 168, 110, 0.28);
      --ok: #72b8b2;
      --missing: #f0c98d;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 28px 18px 118px;
    background: var(--bg);
    color: var(--text);
    font-family: "Segoe UI", Arial, sans-serif;
    line-height: 1.55;
  }
  .wrap { max-width: 1120px; margin: 0 auto; }
  .topbar, .bottom-actions {
    display: flex;
    gap: 10px;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    margin: 0 0 18px;
  }
  .tools-nav, .bottom-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  .tools-nav a, .bottom-actions a, .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 9px 12px;
    text-decoration: none;
    color: var(--accent);
    background: rgba(255,255,255,0.38);
    font-weight: 750;
  }
  .btn.primary, .tools-nav a.active, .bottom-actions a.primary {
    background: var(--accent);
    color: white;
  }
  .btn.disabled {
    opacity: 0.62;
    cursor: not-allowed;
  }
  .muted { color: var(--muted); }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(245px, 1fr));
    gap: 14px;
    margin-top: 18px;
  }
  .tool-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
  }
  .tool-card.missing { opacity: 0.88; }
  .tool-card h2 { margin: 0; font-size: 18px; }
  .tool-card-head {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: start;
  }
  .tool-status {
    border-radius: 999px;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: 800;
  }
  .tool-status.ok { background: rgba(47, 111, 109, 0.16); color: var(--ok); }
  .tool-status.missing { background: rgba(154, 90, 47, 0.16); color: var(--missing); }
  .missing-note {
    border-left: 3px solid var(--missing);
    padding-left: 10px;
    color: var(--muted);
  }
  .actions { margin-top: 12px; }
</style>
"""

    bottom_nav = f"""
    <nav class="bottom-actions" aria-label="Voila tester bottom navigation">
      <a class="primary" href="/">Bibliotecă</a>
      <a href="/course-tools?pdf={q}">Instrumente curs</a>
      <a href="/course-open?pdf={q}">Deschide cursul</a>
      <a href="/study?pdf={q}">Studiu</a>
      <a href="/progress?pdf={q}">Progres</a>
      <a href="/review-ocr-corrected?pdf={q}&page=1">OCR Review</a>
      <a href="/exam-prep">Exam Prep</a>
      <a href="/owner/ocr-math-report/{quote(pdf_path.stem, safe='')}/view">OCR Math</a>
      <a href="/owner/formula-visual-evidence/{quote(pdf_path.stem, safe='')}/view">Formula evidence</a>
    </nav>
    """

    # VOILA_V0_7_97_MANUAL_LEARNING_EVIDENCE_COURSE_TOOLS_LINK_START
    manual_learning_evidence_href = html.escape(
        "/owner/manual-learning-evidence/" + quote(pdf_path.stem, safe="") + "?page=1",
        quote=True,
    )
    # VOILA_V0_7_97_MANUAL_LEARNING_EVIDENCE_COURSE_TOOLS_LINK_END

    page_html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_ut("ui.course_tools", "Course Tools")} · Voila!</title>
  {css}
</head>
<body>
  <main class="wrap course-tools" data-testid="course-tools">
    <section class="topbar">
      <div>
        <h1>{_ut("ui.course_tools", "Course Tools")}</h1>
        <div class="muted">PDF: <b>{html.escape(pdf_path.name)}</b></div>
        <div class="muted">Status curs: <b>{html.escape("HTML + Markdown" if course_html.exists() else "Markdown generated · HTML pending" if course_md.exists() else "Negenerat")}</b></div>
      </div>
      <nav class="tools-nav" aria-label="Voila tester top navigation">
        <a class="active" href="/course-tools?pdf={q}">Instrumente curs</a>
        <a href="/course-open?pdf={q}">Deschide cursul</a>
        <a href="/study?pdf={q}">Studiu</a>
        <a href="/progress?pdf={q}">Progres</a>
        <a href="/review-ocr-corrected?pdf={q}&page=1">OCR Review</a>
        <a href="/owner/formula-visual-evidence/{quote(pdf_path.stem, safe='')}/view">Formula evidence</a>
        <a href="{manual_learning_evidence_href}">Manual evidence</a>
        <a href="/exam-prep">Exam Prep</a>
        <a href="/">Bibliotecă</a>
      </nav>
    </section>

    <section class="grid">
      {''.join(cards)}
    </section>

    {bottom_nav}
  </main>
</body>
</html>"""

    return HTMLResponse(page_html)


@app.get("/view-course")
def view_course(pdf: str = ""):
    from fastapi.responses import HTMLResponse

    pdf_name = _nav_safe_pdf_name(pdf)

    if not pdf_name:
        return HTMLResponse("<h1>" + _ut("error.missing_pdf_name", "Missing PDF name") + "</h1>", status_code=400)

    output_dir = _nav_output_dir(pdf_name)
    course_html = output_dir / "course.cleaned.html"

    if not course_html.exists() and (output_dir / "course.cleaned.md").exists():
        try:
            course_html = ensure_course_html_for_pdf(PROJECT_ROOT / "data" / "input" / pdf_name)
        except Exception as exc:
            return HTMLResponse(
                "<h1>" + _ut("error.course_html_not_found", "Course HTML not found") + "</h1>"
                + f"<p>{_ut('ui.course_html_rebuild_failed', 'The course Markdown exists, but Voila could not rebuild/open the HTML course.')}</p>"
                + f"<p><code>{html.escape(str(exc))}</code></p>"
                + f'<p><a href="/course-tools?pdf={quote(pdf_name)}">{_ut("ui.course_tools", "Course Tools")}</a></p>',
                status_code=500,
            )

    if not course_html.exists():
        return HTMLResponse(
            "<h1>" + _ut("error.course_html_not_found", "Course HTML not found") + "</h1>"
            + f'<p><a href="/course-tools?pdf={quote(pdf_name)}">{_ut("ui.course_tools", "Course Tools")}</a></p>',
            status_code=404,
        )

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

        # VOILA_V0_7_87_QUICK_TOOLS_STUDY_STATUS_CONSISTENCY_START
        study_preview_path = out / "study_items.preview.json"
        study_preview_pass = False
        if study_preview_path.exists():
            try:
                import json as _json
                preview_data = _json.loads(study_preview_path.read_text(encoding="utf-8"))
                preview_gate = preview_data.get("quality_gate") if isinstance(preview_data, dict) else {}
                study_preview_pass = str((preview_gate or {}).get("preview_quality_status") or "").strip().upper() == "PASS"
            except Exception:
                study_preview_pass = False

        exists = {
            "course": (out / "course.cleaned.html").exists(),
            "study": (out / "quiz.study.json").exists() or (out / "quiz.json").exists() or study_preview_pass,
            "figures": (out / "figures_hybrid" / "figures_hybrid.html").exists(),
            "ocr": (out / "ocr_pages.json").exists() or (out / "pages.json").exists(),
        }
        # VOILA_V0_7_87_QUICK_TOOLS_STUDY_STATUS_CONSISTENCY_END

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
  <script src="/voila-static/ocr_review_monaco.js?v=1783592400"></script>
</body>
</html>
"""

    return _VoilaHTMLResponse(html_doc)


@app.post("/save-ocr-correction")
async def voila_save_ocr_correction(request: _VoilaRequest):
    import ocr_page_corrections as oc

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
        'Progresul se actualizează pe baza întrebărilor lucrate în Modul Studiu.</p>'
        '<div class="metric-grid">'
        '<div class="metric"><span>Stare consolidare</span><strong>Nepornit</strong>'
        '<small class="muted">Consolidat după lucru suficient în Modul Studiu</small></div>'
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
from urllib.parse import quote, unquote as _v415_unquote


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
from urllib.parse import quote, unquote as _v416_unquote


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
from urllib.parse import quote, unquote as _v423_unquote


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
        ("Întrebări", "Întrebări"),
        ("Continua", "Continuă"),
        ("Inapoi", "Înapoi"),
        ("Întrebări Study legate", "Întrebări asociate din Modul Studiu"),
        ("Continuă în Modul Studiu", "Continuă în Modul Studiu"),
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

# v0.7.27 generated Romanian diacritics / responsiveness display guard.
#
# This is intentionally display-layer only. It does not rewrite OCR source files,
# course markdown, or user data. It repairs common OCR/encoding artifacts in
# generated HTML responses and prevents the tester-flow bottom navigation from
# becoming visually heavy or duplicated.
def _voila_v0727_normalize_romanian_ocr_display_text(value: str) -> str:
    if not isinstance(value, str) or not value:
        return value

    replacements = (
        ("ǎ", "ă"),
        ("Ǎ", "Ă"),
        ("˘a", "ă"),
        ("a˘", "ă"),
        ("˘A", "Ă"),
        ("A˘", "Ă"),
        ("s¸", "ș"),
        ("S¸", "Ș"),
        ("t¸", "ț"),
        ("T¸", "Ț"),
        ("¸s", "ș"),
        ("¸S", "Ș"),
        ("¸t", "ț"),
        ("¸T", "Ț"),
        ("ş", "ș"),
        ("Ş", "Ș"),
        ("ţ", "ț"),
        ("Ţ", "Ț"),
        ("ş", "ș"),
        ("Ş", "Ș"),
        ("ţ", "ț"),
        ("Ţ", "Ț"),
    )

    for bad, good in replacements:
        value = value.replace(bad, good)

    return value


def _voila_v0727_inject_bottom_nav_css_once(value: str) -> str:
    if not isinstance(value, str) or not value:
        return value

    css_id = "voila-v0727-bottom-nav-polish"
    if css_id in value:
        return value

    css = "\n".join([
        '<style id="voila-v0727-bottom-nav-polish">',
        # v0.7.57: target the injected nav element, not the script tag marker.
        '.voila-tester-flow-bottom-nav,',
        '#voilaTesterFlowBottomNav {',
        '  position: static !important;',
        '  left: auto !important;',
        '  right: auto !important;',
        '  bottom: auto !important;',
        '  z-index: auto !important;',
        '  display: flex !important;',
        '  flex-wrap: wrap !important;',
        '  gap: 0.5rem !important;',
        '  align-items: center !important;',
        '  justify-content: flex-start !important;',
        '  max-width: 100% !important;',
        '  margin: 2rem 0 0 !important;',
        '  padding: 0.75rem 0 !important;',
        '  background: transparent !important;',
        '  box-shadow: none !important;',
        '}',
        '.voila-tester-flow-bottom-nav a,',
        '#voilaTesterFlowBottomNav a {',
        '  white-space: normal !important;',
        '  line-height: 1.25 !important;',
        '}',
        '</style>',
    ])

    if "</head>" in value:
        return value.replace("</head>", css + "\n</head>", 1)

    return css + value


def _voila_v0727_remove_duplicate_bottom_nav_blocks(value: str) -> str:
    if not isinstance(value, str) or not value:
        return value

    marker = "voila-tester-flow-bottom-nav-v0724"
    if value.count(marker) <= 1:
        return value

    # Keep the last bottom navigation block. The visible problem observed in
    # v0.7.26 was navigation becoming heavy/overlapping in generated course view.
    import re as _voila_v0727_re

    pattern = _voila_v0727_re.compile(
        r"<(?P<tag>nav|div|section)(?P<attrs>[^>]*?(?:id|class)=[\"'][^\"']*"
        + _voila_v0727_re.escape(marker)
        + r"[^\"']*[\"'][^>]*)>.*?</(?P=tag)>",
        _voila_v0727_re.IGNORECASE | _voila_v0727_re.DOTALL,
    )
    matches = list(pattern.finditer(value))
    if len(matches) <= 1:
        return value

    keep_start, keep_end = matches[-1].span()
    chunks = []
    cursor = 0
    for match in matches:
        start, end = match.span()
        if start == keep_start and end == keep_end:
            chunks.append(value[cursor:end])
            cursor = end
        else:
            chunks.append(value[cursor:start])
            cursor = end
    chunks.append(value[cursor:])
    return "".join(chunks)


def _voila_v0727_polish_html_response_text(value: str) -> str:
    value = _voila_v0727_normalize_romanian_ocr_display_text(value)
    value = _voila_v0727_remove_duplicate_bottom_nav_blocks(value)
    value = _voila_v0727_inject_bottom_nav_css_once(value)
    return value


@app.middleware("http")
async def _voila_v0727_html_response_polish_middleware(request, call_next):
    response = await call_next(request)
    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type.lower():
        return response

    if not hasattr(response, "body_iterator"):
        return response

    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        text = body.decode("utf-8", errors="replace")

    polished = _voila_v0727_polish_html_response_text(text)

    headers = dict(response.headers)
    for header in ("content-length", "content-type", "content-encoding", "transfer-encoding"):
        headers.pop(header, None)

    from fastapi.responses import HTMLResponse as _VoilaV0727HTMLResponse

    return _VoilaV0727HTMLResponse(
        content=polished,
        status_code=response.status_code,
        headers=headers,
    )


# VOILA_V0_7_71_OWNER_LOCAL_OCR_REVIEW_READ_ONLY_PAGE_SHELL_START
# Owner-local guided OCR Review read-only shell.
# Policy: read-only display only; no decision write, no apply patch, no learning pack rebuild,
# no /generate integration, no build, no ZIP, no delivery, no distribution.

def _voila_ocr_review_safe_course_id(course_id: str) -> str:
    safe_id = unquote(str(course_id or "")).strip().strip("/")
    if not safe_id:
        raise ValueError("Missing OCR Review course id")
    if ".." in safe_id or "\\" in safe_id or "/" in safe_id or ":" in safe_id:
        raise ValueError("Unsafe OCR Review course id")
    return safe_id


def _voila_ocr_review_json_load(path: Path) -> tuple[dict, str]:
    if not path.is_file():
        return {}, f"missing {path.name}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}, f"invalid {path.name}"
    if not isinstance(data, dict):
        return {}, f"invalid {path.name}: expected JSON object"
    return data, ""


def _voila_ocr_review_list(value) -> list:
    return value if isinstance(value, list) else []


def _voila_ocr_review_bool_label(value) -> str:
    if value is True:
        return "True"
    if value is False:
        return "False"
    return "n/a"


def _voila_ocr_review_text(value, max_len: int = 260) -> str:
    clean = " ".join(str(value or "").split()).strip()
    if len(clean) > max_len:
        return clean[: max_len - 1] + "…"
    return clean


def _voila_ocr_review_decision_counts(decisions_data: dict) -> dict:
    decisions = _voila_ocr_review_list(decisions_data.get("decisions"))
    decision_count = int(decisions_data.get("decision_count") or len(decisions))
    pending_count = int(
        decisions_data.get("pending_decision_count")
        if decisions_data.get("pending_decision_count") is not None
        else sum(1 for item in decisions if item.get("decision") == "pending" and item.get("requires_user_decision", True))
    )
    resolved_count = int(
        decisions_data.get("resolved_decision_count")
        if decisions_data.get("resolved_decision_count") is not None
        else max(0, decision_count - pending_count)
    )
    return {
        "decision_count": decision_count,
        "pending_decision_count": pending_count,
        "resolved_decision_count": resolved_count,
    }


def _voila_ocr_review_gate(queue_data: dict, decisions_data: dict) -> dict:
    review_items = _voila_ocr_review_list(queue_data.get("review_items"))
    counts = _voila_ocr_review_decision_counts(decisions_data)
    quality_gate = decisions_data.get("quality_gate") if isinstance(decisions_data.get("quality_gate"), dict) else {}

    generation_should_wait = quality_gate.get("generation_should_wait_for_review")
    if generation_should_wait is None:
        generation_should_wait = counts["pending_decision_count"] > 0 or (len(review_items) > 0 and counts["decision_count"] == 0)

    all_resolved = quality_gate.get("all_required_decisions_resolved")
    if all_resolved is None:
        all_resolved = counts["pending_decision_count"] == 0 and counts["decision_count"] == len(review_items)

    return {
        "review_item_count": len(review_items),
        "decision_count": counts["decision_count"],
        "pending_decision_count": counts["pending_decision_count"],
        "resolved_decision_count": counts["resolved_decision_count"],
        "generation_should_wait_for_review": bool(generation_should_wait),
        "all_required_decisions_resolved": bool(all_resolved),
    }


# VOILA_V0_7_72_OWNER_LOCAL_OCR_REVIEW_GUIDED_DECISION_BUTTONS_START
# Owner-local guided OCR Review decision buttons.
# Policy: write decisions only to ocr_review_decisions.json.
# No apply patch, no ocr_review_decisions.applied.json, no document learning pack rebuild,
# no /generate integration, no build, no ZIP, no delivery, no distribution.
VOILA_V0_7_72_OCR_REVIEW_GUIDED_DECISIONS = {
    "accepted": "Acceptă sugestia",
    "edited": "Editează textul",
    "ignored": "Ignoră",
    "marked_definition": "Este definiție",
    "marked_formula": "Este formulă",
    "marked_notation": "Este notație",
    "marked_theorem": "Este teoremă",
    "marked_example": "Este exemplu",
    "marked_glossary_term": "Este termen de glosar",
    "marked_not_relevant": "Nu este relevant",
}


def _voila_ocr_review_card_html(item: dict, decision_by_id: dict, course_id: str) -> str:
    review_item_id = str(item.get("review_item_id") or "")
    decision = decision_by_id.get(review_item_id) or {}
    current_decision = str(decision.get("decision") or "pending")

    linked_terms = ", ".join(str(term) for term in _voila_ocr_review_list(item.get("linked_concept_terms"))) or "n/a"
    form_action = "/owner/ocr-review/" + quote(str(course_id), safe="") + "/decision"
    corrected_text = str(decision.get("corrected_text") or "")
    user_note = str(decision.get("user_note") or "")

    buttons = []
    for value, label in VOILA_V0_7_72_OCR_REVIEW_GUIDED_DECISIONS.items():
        css = "primary" if value == current_decision else ""
        buttons.append(
            f'<button class="{html.escape(css, quote=True)}" type="submit" name="decision" value="{html.escape(value, quote=True)}">'
            f'{html.escape(label)}</button>'
        )

    return f"""
    <article class="card" data-voila-ocr-review-item="{html.escape(review_item_id, quote=True)}">
      <h2>{html.escape(review_item_id or "Review item")}</h2>
      <div class="meta">
        Pagină PDF: <strong>{html.escape(str(item.get("source_pdf_page") or "n/a"))}</strong> ·
        Tip problemă: <strong>{html.escape(str(item.get("issue_type") or "n/a"))}</strong> ·
        Rol sugerat: <strong>{html.escape(str(item.get("suggested_learning_role") or "n/a"))}</strong>
      </div>
      <p><strong>Concepte legate:</strong> {html.escape(linked_terms)}</p>
      <p><strong>Text OCR suspect:</strong><br>{html.escape(_voila_ocr_review_text(item.get("source_text")))}</p>
      <p><strong>Sugestie:</strong><br>{html.escape(_voila_ocr_review_text(item.get("suggested_text")))}</p>
      <p><strong>Decizie curentă:</strong> <code>{html.escape(current_decision)}</code></p>

      <form method="post" action="{html.escape(form_action, quote=True)}" class="ocr-review-decision-form">
        <input type="hidden" name="review_item_id" value="{html.escape(review_item_id, quote=True)}">
        <label>
          Text corectat, doar pentru „Editează textul”
          <textarea name="corrected_text" rows="3" maxlength="4000">{html.escape(corrected_text)}</textarea>
        </label>
        <label>
          Notă opțională
          <input name="user_note" maxlength="1000" value="{html.escape(user_note, quote=True)}">
        </label>
        <div class="actions">
          {''.join(buttons)}
        </div>
      </form>

      <p class="muted">v0.7.72: salvează doar decizia în <code>ocr_review_decisions.json</code>. Nu aplică patch, nu reconstruiește learning pack și nu cheamă /generate.</p>
    </article>
    """


@app.get("/owner/ocr-review/{course_id}", response_class=HTMLResponse, include_in_schema=False)
def _voila_owner_ocr_review_read_only_shell(course_id: str) -> HTMLResponse:
    try:
        safe_id = _voila_ocr_review_safe_course_id(course_id)
    except ValueError:
        return PlainTextResponse(
            "OCR Review unavailable: invalid local course id.",
            status_code=400,
        )

    output_dir = OUTPUT_DIR / safe_id
    queue_path = output_dir / "ocr_review_queue.json"
    decisions_path = output_dir / "ocr_review_decisions.json"

    queue_data, queue_error = _voila_ocr_review_json_load(queue_path)
    decisions_data, decisions_error = _voila_ocr_review_json_load(decisions_path)

    review_items = _voila_ocr_review_list(queue_data.get("review_items"))
    decisions = _voila_ocr_review_list(decisions_data.get("decisions"))
    decision_by_id = {
        str(item.get("review_item_id") or ""): item
        for item in decisions
        if isinstance(item, dict)
    }

    gate = _voila_ocr_review_gate(queue_data, decisions_data)

    missing = []
    if queue_error:
        missing.append(queue_error)
    if decisions_error:
        missing.append(decisions_error)

    owner_review_confirmed = bool(decisions_data.get("owner_review_confirmed") is True)
    pending_count_for_confirm = int(gate.get("pending_decision_count") or 0)
    confirm_action = "/owner/ocr-review/" + quote(safe_id, safe="") + "/confirm"

    if gate["generation_should_wait_for_review"]:
        gate_label = "Blocat — OCR Review trebuie rezolvat înainte de generare."
        gate_class = "notice"
    else:
        gate_label = "OK — nu există decizii pending în artifactele citite."
        gate_class = "notice success"

    if owner_review_confirmed:
        confirm_html = """
        <div class="notice success">
          <strong>OCR Review confirmat final.</strong><br>
          v0.7.73 păstrează generarea blocată până la un milestone separat de integrare.
        </div>
        """
    elif pending_count_for_confirm == 0 and int(gate.get("decision_count") or 0) > 0:
        confirm_html = f"""
        <form method="post" action="{html.escape(confirm_action, quote=True)}" class="ocr-review-final-confirm-form">
          <div class="notice success">
            <strong>Toate deciziile OCR Review sunt rezolvate.</strong><br>
            Apasă doar dacă ai verificat manual toate cardurile.
            <div class="actions">
              <button class="primary" type="submit">Confirmă OCR Review</button>
            </div>
            <p class="muted">v0.7.73: confirmarea scrie doar în <code>ocr_review_decisions.json</code>. Nu aplică patch, nu reconstruiește learning pack și nu cheamă /generate.</p>
          </div>
        </form>
        """
    else:
        confirm_html = f"""
        <div class="notice">
          <strong>Confirmarea finală este blocată.</strong><br>
          Mai există <strong>{pending_count_for_confirm}</strong> decizii pending.
          <p class="muted">Rezolvă toate deciziile înainte de „Confirmă OCR Review”.</p>
        </div>
        """

    missing_html = ""
    if missing:
        missing_html = """
        <div class="notice warning">
          <strong>Diagnostic local:</strong><br>
          """ + "<br>".join(html.escape(item) for item in missing) + """
          <br>Pagina este read-only și nu creează artifacte lipsă.
        </div>
        """

    cards_html = "".join(_voila_ocr_review_card_html(item, decision_by_id, safe_id) for item in review_items[:50])
    if not cards_html:
        cards_html = """
        <article class="card">
          <h2>Niciun item OCR Review de afișat</h2>
          <p class="muted">Lipsește queue-ul sau nu există itemi care cer review.</p>
        </article>
        """

    q_pdf = html.escape(quote(safe_id + ".pdf", safe=""), quote=True)
    # VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_OCR_REVIEW_LINK_START
    safe_formula_visual_href = html.escape(
        "/owner/formula-visual-evidence/" + quote(safe_id, safe="") + "/view",
        quote=True,
    )
    # VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_OCR_REVIEW_LINK_END
    body = f"""
    <style>
      .ocr-review-summary {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 12px;
        margin: 16px 0;
      }}
      .ocr-review-metric {{
        border: 1px solid rgba(80, 64, 40, 0.18);
        border-radius: 14px;
        padding: 12px;
        background: rgba(255,255,255,0.28);
      }}
      .ocr-review-metric strong {{
        display: block;
        font-size: 24px;
        margin-top: 4px;
      }}
      .notice.warning {{
        border-color: #b7791f;
      }}
      .notice.success {{
        border-color: #2f855a;
      }}
    </style>

    <section data-testid="owner-ocr-review-read-only-shell">
      <h1>OCR Review · decizii ghidate</h1>
      <div class="meta">Course ID: <strong>{html.escape(safe_id)}</strong></div>

      <div class="{gate_class}">
        <strong>Status generare:</strong> {html.escape(gate_label)}<br>
        generation_should_wait_for_review=<code>{html.escape(_voila_ocr_review_bool_label(gate["generation_should_wait_for_review"]))}</code> ·
        all_required_decisions_resolved=<code>{html.escape(_voila_ocr_review_bool_label(gate["all_required_decisions_resolved"]))}</code>
      </div>

      {missing_html}

      {confirm_html}

      <div class="ocr-review-summary">
        <div class="ocr-review-metric">Review items<strong>{gate["review_item_count"]}</strong></div>
        <div class="ocr-review-metric">Decizii total<strong>{gate["decision_count"]}</strong></div>
        <div class="ocr-review-metric">Pending<strong>{gate["pending_decision_count"]}</strong></div>
        <div class="ocr-review-metric">Rezolvate<strong>{gate["resolved_decision_count"]}</strong></div>
      </div>

      <div class="notice">
        v0.7.72: poți salva decizii ghidate în ocr_review_decisions.json. Nu aplică patch, nu reconstruiește learning pack și nu cheamă /generate.
      </div>

      <div class="actions">
        <a class="btn" href="/course-tools?pdf={q_pdf}">Course Tools</a>
        <a class="btn" href="{safe_formula_visual_href}">Formula visual evidence</a>
        <a class="btn" href="/">Library</a>
      </div>

      <h2>Itemi OCR Review</h2>
      <div class="grid">
        {cards_html}
      </div>
    </section>
    """

    doc = f"""<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Voila! OCR Review decisions</title>
  <style>
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #e8dfd0;
      color: #1f2933;
    }}
    .wrap {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 28px;
    }}
    .card, .notice {{
      background: #f5ecd9;
      border: 1px solid rgba(80, 64, 40, 0.16);
      border-radius: 18px;
      padding: 18px;
      margin: 14px 0;
      box-shadow: 0 10px 28px rgba(80, 64, 40, 0.08);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 14px;
    }}
    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 16px 0;
    }}
    .btn {{
      display: inline-block;
      padding: 10px 14px;
      border-radius: 999px;
      background: #1f2933;
      color: #fff;
      text-decoration: none;
      font-weight: 700;
    }}
    .meta, .muted {{
      color: #6b5b45;
    }}
    code {{
      background: rgba(31, 41, 51, 0.08);
      padding: 2px 6px;
      border-radius: 6px;
    }}
  </style>
</head>
<body>
  <main class="wrap">
    {body}
  </main>
</body>
</html>"""
    return HTMLResponse(content=doc)


def _voila_ocr_review_confirmed_role_for_decision(decision: str) -> str:
    return {
        "marked_definition": "definition",
        "marked_formula": "formula",
        "marked_notation": "notation",
        "marked_theorem": "theorem",
        "marked_example": "example",
        "marked_glossary_term": "glossary_term",
        "marked_not_relevant": "not_relevant",
    }.get(str(decision or ""), "")


def _voila_ocr_review_save_guided_decision(
    course_id: str,
    review_item_id: str,
    decision: str,
    corrected_text: str = "",
    user_note: str = "",
) -> tuple[bool, str]:
    try:
        safe_id = _voila_ocr_review_safe_course_id(course_id)
    except ValueError:
        return False, "invalid_course_id"

    clean_review_item_id = str(review_item_id or "").strip()
    clean_decision = str(decision or "").strip()
    clean_corrected_text = str(corrected_text or "").strip()
    clean_user_note = str(user_note or "").strip()

    if not clean_review_item_id or len(clean_review_item_id) > 100:
        return False, "invalid_review_item_id"
    if clean_decision not in VOILA_V0_7_72_OCR_REVIEW_GUIDED_DECISIONS:
        return False, "invalid_decision"
    if clean_decision == "edited" and not clean_corrected_text:
        return False, "edited_requires_corrected_text"
    if len(clean_corrected_text) > 4000 or len(clean_user_note) > 1000:
        return False, "input_too_long"

    decisions_path = OUTPUT_DIR / safe_id / "ocr_review_decisions.json"
    if not decisions_path.is_file():
        return False, "missing_decisions_file"

    try:
        decisions_data = json.loads(decisions_path.read_text(encoding="utf-8"))
    except Exception:
        return False, "invalid_decisions_file"

    if not isinstance(decisions_data, dict):
        return False, "invalid_decisions_file"

    decisions = decisions_data.get("decisions")
    if not isinstance(decisions, list):
        return False, "invalid_decisions_file"

    target = None
    for item in decisions:
        if isinstance(item, dict) and str(item.get("review_item_id") or "") == clean_review_item_id:
            target = item
            break

    if target is None:
        return False, "unknown_review_item_id"

    now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    target["decision"] = clean_decision
    target["corrected_text"] = clean_corrected_text if clean_decision == "edited" else ""
    target["user_note"] = clean_user_note
    target["requires_user_decision"] = False
    target["real_user_decision"] = True
    target["decision_source"] = "owner_local_guided_ui_v0.7.72"
    target["applied_to_learning_pack"] = False
    target["updated_at"] = now

    confirmed_role = _voila_ocr_review_confirmed_role_for_decision(clean_decision)
    if confirmed_role:
        target["confirmed_learning_role"] = confirmed_role

    pending_count = sum(
        1
        for item in decisions
        if isinstance(item, dict)
        and item.get("requires_user_decision", True)
        and str(item.get("decision") or "pending") == "pending"
    )
    decision_count = len([item for item in decisions if isinstance(item, dict)])
    resolved_count = max(0, decision_count - pending_count)

    decisions_data["decision_count"] = decision_count
    decisions_data["pending_decision_count"] = pending_count
    decisions_data["resolved_decision_count"] = resolved_count
    decisions_data["real_user_decisions_performed"] = True
    decisions_data["owner_review_confirmed"] = False
    decisions_data["applied_to_learning_pack"] = False
    decisions_data["updated_at"] = now
    decisions_data["decision_source"] = "owner_local_guided_ui_v0.7.72"

    quality_gate = decisions_data.get("quality_gate")
    if not isinstance(quality_gate, dict):
        quality_gate = {}
    quality_gate["pending_decision_count"] = pending_count
    quality_gate["resolved_decision_count"] = resolved_count
    quality_gate["all_required_decisions_resolved"] = pending_count == 0
    quality_gate["owner_review_confirmed"] = False
    quality_gate["generation_should_wait_for_review"] = True
    quality_gate["generation_block_reason"] = "owner_review_not_final_confirmed"
    decisions_data["quality_gate"] = quality_gate

    decisions_path.write_text(
        json.dumps(decisions_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return True, "saved"


@app.post("/owner/ocr-review/{course_id}/decision", include_in_schema=False)
def _voila_owner_ocr_review_guided_decision(
    course_id: str,
    review_item_id: str = Form(...),
    decision: str = Form(...),
    corrected_text: str = Form(default=""),
    user_note: str = Form(default=""),
):
    ok, _message = _voila_ocr_review_save_guided_decision(
        course_id=course_id,
        review_item_id=review_item_id,
        decision=decision,
        corrected_text=corrected_text,
        user_note=user_note,
    )
    if not ok:
        return PlainTextResponse(
            "OCR Review decision was not saved.",
            status_code=400,
        )

    try:
        safe_id = _voila_ocr_review_safe_course_id(course_id)
    except ValueError:
        return PlainTextResponse(
            "OCR Review decision was not saved.",
            status_code=400,
        )

    return RedirectResponse(
        url="/owner/ocr-review/" + quote(safe_id, safe=""),
        status_code=303,
    )

# VOILA_V0_7_72_OWNER_LOCAL_OCR_REVIEW_GUIDED_DECISION_BUTTONS_END


# VOILA_V0_7_73_OWNER_LOCAL_OCR_REVIEW_FINAL_CONFIRM_BUTTON_START
# Owner-local OCR Review final confirmation.
# Policy: write final confirmation only to ocr_review_decisions.json.
# No apply patch, no ocr_review_decisions.applied.json, no document_learning_pack rebuild,
# no /generate integration, no build, no ZIP, no delivery, no distribution.

def _voila_ocr_review_save_final_confirmation(course_id: str) -> tuple[bool, str]:
    try:
        safe_id = _voila_ocr_review_safe_course_id(course_id)
    except ValueError:
        return False, "invalid_course_id"

    decisions_path = OUTPUT_DIR / safe_id / "ocr_review_decisions.json"
    if not decisions_path.is_file():
        return False, "missing_decisions_file"

    try:
        decisions_data = json.loads(decisions_path.read_text(encoding="utf-8"))
    except Exception:
        return False, "invalid_decisions_file"

    if not isinstance(decisions_data, dict):
        return False, "invalid_decisions_file"

    decisions = decisions_data.get("decisions")
    if not isinstance(decisions, list):
        return False, "invalid_decisions_file"

    decision_count = len([item for item in decisions if isinstance(item, dict)])
    pending_count = sum(
        1
        for item in decisions
        if isinstance(item, dict)
        and item.get("requires_user_decision", True)
        and str(item.get("decision") or "pending") == "pending"
    )
    if decision_count <= 0:
        return False, "no_decisions_to_confirm"
    if pending_count != 0:
        return False, "pending_decisions_remain"

    now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    resolved_count = decision_count

    decisions_data["decision_count"] = decision_count
    decisions_data["pending_decision_count"] = 0
    decisions_data["resolved_decision_count"] = resolved_count
    decisions_data["owner_review_confirmed"] = True
    decisions_data["owner_review_confirmed_at"] = now
    decisions_data["real_user_decisions_performed"] = True
    decisions_data["applied_to_learning_pack"] = False
    decisions_data["updated_at"] = now
    decisions_data["final_confirmation_source"] = "owner_local_guided_ui_v0.7.73"

    quality_gate = decisions_data.get("quality_gate")
    if not isinstance(quality_gate, dict):
        quality_gate = {}
    quality_gate["pending_decision_count"] = 0
    quality_gate["resolved_decision_count"] = resolved_count
    quality_gate["all_required_decisions_resolved"] = True
    quality_gate["owner_review_confirmed"] = True
    quality_gate["owner_review_confirmed_at"] = now
    quality_gate["generation_should_wait_for_review"] = True
    quality_gate["generation_block_reason"] = "generate_integration_not_enabled_v0.7.73"
    decisions_data["quality_gate"] = quality_gate

    decisions_path.write_text(
        json.dumps(decisions_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return True, "confirmed"


@app.post("/owner/ocr-review/{course_id}/confirm", include_in_schema=False)
def _voila_owner_ocr_review_final_confirm(course_id: str):
    ok, _message = _voila_ocr_review_save_final_confirmation(course_id)
    if not ok:
        return PlainTextResponse(
            "OCR Review final confirmation was not saved.",
            status_code=400,
        )

    try:
        safe_id = _voila_ocr_review_safe_course_id(course_id)
    except ValueError:
        return PlainTextResponse(
            "OCR Review final confirmation was not saved.",
            status_code=400,
        )

    return RedirectResponse(
        url="/owner/ocr-review/" + quote(safe_id, safe=""),
        status_code=303,
    )

# VOILA_V0_7_73_OWNER_LOCAL_OCR_REVIEW_FINAL_CONFIRM_BUTTON_END

# VOILA_V0_7_71_OWNER_LOCAL_OCR_REVIEW_READ_ONLY_PAGE_SHELL_END\n


# VOILA_V0_8_18_MANUAL_STUDY_INTEGRATION_DRY_RUN_TOGGLE_START
def _voila_v0818_manual_study_dry_run_toggle_enabled(value):
    value_text = str(value or "").strip().lower()
    return value_text in {"1", "true", "yes", "on"}


def _voila_v0818_load_manual_study_items_preview(course_id):
    safe_course_id = _voila_v090_validate_course_id(course_id)

    output_root = Path("data") / "output"
    output_dir = None

    if output_root.exists():
        try:
            for candidate_dir in output_root.iterdir():
                if candidate_dir.is_dir() and candidate_dir.name == safe_course_id:
                    output_dir = candidate_dir
                    break
        except Exception:
            output_dir = None

    if output_dir is None:
        return safe_course_id, None, [], "course_output_not_found"

    preview_path = output_dir / "manual_study_items.preview.json"
    if not preview_path.exists():
        return safe_course_id, None, [], "manual_study_items_preview_missing"

    try:
        preview_data = json.loads(preview_path.read_text(encoding="utf-8"))
    except Exception:
        return safe_course_id, None, [], "manual_study_items_preview_unreadable"

    preview_items = preview_data.get("items")
    if not isinstance(preview_items, list):
        preview_items = []

    return safe_course_id, preview_data, preview_items, "ok"


@app.get("/owner/manual-study-integration-dry-run/{course_id}")
def owner_manual_study_integration_dry_run(course_id: str, enabled: str = "0"):
    safe_course_id, preview_data, preview_items, load_status = _voila_v0818_load_manual_study_items_preview(course_id)

    enabled_flag = _voila_v0818_manual_study_dry_run_toggle_enabled(enabled)
    safe_course_id_html = html.escape(safe_course_id, quote=True)
    safe_course_id_url = quote(safe_course_id, safe="")
    item_count = len(preview_items)

    off_href = "/owner/manual-study-integration-dry-run/" + safe_course_id_url + "?enabled=0"
    on_href = "/owner/manual-study-integration-dry-run/" + safe_course_id_url + "?enabled=1"
    preview_href = "/owner/manual-study-preview/" + safe_course_id_url

    if preview_data is None:
        cards_html = (
            '<p class="meta" data-testid="manual-study-integration-dry-run-missing-preview">'
            + html.escape("manual_study_items.preview.json lipsește sau nu poate fi citit. Status: " + load_status, quote=True)
            + "</p>"
        )
        preview_available = "false"
    elif enabled_flag:
        cards_html = _voila_v0813_manual_study_preview_cards_html(preview_items)
        preview_available = "true"
    else:
        cards_html = """
        <p class="meta" data-testid="manual-study-integration-dry-run-toggle-off">
          Toggle OFF. Nu randăm cardurile până nu activezi dry-run-ul explicit.
        </p>
        """
        preview_available = "true"

    enabled_text = "true" if enabled_flag else "false"

    return page(
        "Manual Study Integration Dry Run",
        f"""
        <section class="v0813-manual-study" data-testid="manual-study-integration-dry-run-route">
          <h1>Manual Study Integration Dry Run</h1>

          <p class="meta">
            Route owner-local pentru verificarea explicită a integrării Manual Study înainte de orice atingere a route-ului real <code>/study</code>.
          </p>

          <div class="v0815-study-top-nav" data-testid="manual-study-integration-dry-run-toggle">
            <span class="v0815-study-position">dry_run_toggle_enabled=<code>{enabled_text}</code></span>
            <a href="{html.escape(off_href, quote=True)}" data-testid="manual-study-integration-dry-run-off">Toggle OFF</a>
            <a href="{html.escape(on_href, quote=True)}" data-testid="manual-study-integration-dry-run-on">Toggle ON</a>
            <a href="{html.escape(preview_href, quote=True)}" data-testid="manual-study-integration-dry-run-preview-link">Înapoi la Manual Study Preview</a>
          </div>

          <p class="meta" data-testid="manual-study-integration-dry-run-source">
            course_id=<code>{safe_course_id_html}</code><br>
            source_artifact=<code>manual_study_items.preview.json</code><br>
            load_status=<code>{html.escape(load_status, quote=True)}</code><br>
            preview_available=<code>{preview_available}</code><br>
            item_count=<code>{item_count}</code><br>
            target_route=<code>/study</code><br>
            integration_mode=<code>dry_run_only</code>
          </p>

          <p class="meta" data-testid="manual-study-integration-dry-run-policy">
            manual_study_connected_to_real_study=<code>false</code><br>
            replaces_existing_study_route=<code>false</code><br>
            progress_write=<code>false</code><br>
            answer_marking=<code>false</code><br>
            writes_legacy_study_items_preview=<code>false</code><br>
            build_performed=<code>false</code><br>
            zip_created=<code>false</code><br>
            share_created=<code>false</code><br>
            delivery_performed=<code>false</code>
          </p>

          <div id="manual-study-preview-top" data-testid="manual-study-integration-dry-run-cards">
            {cards_html}
          </div>
        </section>
        """,
    )
# VOILA_V0_8_18_MANUAL_STUDY_INTEGRATION_DRY_RUN_TOGGLE_END

# VOILA_V0_8_19_MANUAL_STUDY_DRY_RUN_COURSE_TOOLS_LINK_START
def _voila_v0819_inject_manual_study_dry_run_course_tools_link(html_text):
    if not isinstance(html_text, str):
        return html_text

    if 'data-testid="manual-study-dry-run-course-tools-link"' in html_text:
        return html_text

    import re as _voila_v0819_re
    from urllib.parse import quote as _voila_v0819_quote

    match = _voila_v0819_re.search(
        r'href="(/owner/manual-study-preview/([A-Za-z0-9_.-]+))"',
        html_text,
    )
    if not match:
        return html_text

    safe_course_id = match.group(2)
    if not _voila_v0819_re.fullmatch(r"[A-Za-z0-9_.-]+", safe_course_id):
        return html_text

    safe_course_id_url = _voila_v0819_quote(safe_course_id, safe="")
    dry_run_href = "/owner/manual-study-integration-dry-run/" + safe_course_id_url + "?enabled=0"
    dry_run_href_html = html.escape(dry_run_href, quote=True)
    # VOILA_V0_8_24_MANUAL_STUDY_SHADOW_COURSE_TOOLS_LINK_START
    shadow_href = "/study?manual_study_shadow=1&course_id=" + safe_course_id_url
    shadow_href_html = html.escape(shadow_href, quote=True)
    # VOILA_V0_8_24_MANUAL_STUDY_SHADOW_COURSE_TOOLS_LINK_END
    safe_course_id_html = html.escape(safe_course_id, quote=True)

    dry_run_block = f"""
    <section class="v0813-manual-study" data-testid="manual-study-dry-run-course-tools-section">
      <h2>Manual Study dry-run</h2>
      <p class="meta">
        Link owner-local către dry-run toggle înainte de orice integrare reală în <code>/study</code>.
      </p>
      <p>
        <a href="{dry_run_href_html}" data-testid="manual-study-dry-run-course-tools-link">
          Deschide Manual Study Integration Dry Run
        </a>
      </p>
      <p>
        <a href="{shadow_href_html}" data-testid="manual-study-shadow-course-tools-link">
          Deschide Study Manual Shadow
        </a>
      </p>
      <p class="meta" data-testid="manual-study-dry-run-course-tools-status">
        course_id=<code>{safe_course_id_html}</code><br>
        source_artifact=<code>manual_study_items.preview.json</code><br>
        dry_run_toggle_default=<code>off</code><br>
        integration_mode=<code>dry_run_only</code><br>
        shadow_route=<code>/study?manual_study_shadow=1&amp;course_id={safe_course_id_html}</code><br>
        shadow_integration_mode=<code>read_only_shadow_toggle</code><br>
        manual_study_default_enabled=<code>false</code><br>
        manual_study_connected_to_real_study=<code>shadow_only_explicit_link</code><br>
        progress_write=<code>false</code><br>
        answer_marking=<code>false</code><br>
        writes_legacy_study_items_preview=<code>false</code>
      </p>
    </section>
    """

    anchor = 'data-testid="manual-study-preview-course-tools-status"'
    anchor_index = html_text.find(anchor)
    if anchor_index >= 0:
        paragraph_end = html_text.find("</p>", anchor_index)
        if paragraph_end >= 0:
            insert_at = paragraph_end + len("</p>")
            return html_text[:insert_at] + dry_run_block + html_text[insert_at:]

    body_end = html_text.lower().rfind("</body>")
    if body_end >= 0:
        return html_text[:body_end] + dry_run_block + html_text[body_end:]

    return html_text + dry_run_block


@app.middleware("http")
async def _voila_v0819_manual_study_dry_run_course_tools_link_middleware(request, call_next):
    response = await call_next(request)

    if getattr(request.url, "path", "") != "/course-tools":
        return response

    if getattr(response, "status_code", 200) != 200:
        return response

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type.lower():
        return response

    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    html_text = body.decode("utf-8", errors="replace")
    injected = _voila_v0819_inject_manual_study_dry_run_course_tools_link(html_text)

    from starlette.responses import Response as _VoilaV0819Response

    headers = {
        key: value
        for key, value in response.headers.items()
        if key.lower() not in {"content-length", "content-type"}
    }

    return _VoilaV0819Response(
        content=injected,
        status_code=response.status_code,
        headers=headers,
        media_type="text/html",
    )
# VOILA_V0_8_19_MANUAL_STUDY_DRY_RUN_COURSE_TOOLS_LINK_END

# VOILA_V0_8_22_MANUAL_STUDY_REAL_STUDY_READ_ONLY_SHADOW_TOGGLE_START
def _voila_v0822_manual_study_shadow_toggle_enabled(value):
    value_text = str(value or "").strip().lower()
    return value_text in {"1", "true", "yes", "on"}


def _voila_v0822_manual_study_shadow_page(course_id):
    safe_course_id, preview_data, preview_items, load_status = _voila_v0818_load_manual_study_items_preview(course_id)

    safe_course_id_html = html.escape(safe_course_id, quote=True)
    preview_href = "/owner/manual-study-preview/" + quote(safe_course_id, safe="")
    dry_run_href = "/owner/manual-study-integration-dry-run/" + quote(safe_course_id, safe="") + "?enabled=1"

    if preview_data is None:
        cards_html = (
            '<p class="meta" data-testid="manual-study-shadow-missing-preview">'
            + html.escape("manual_study_items.preview.json lipsește sau nu poate fi citit. Status: " + load_status, quote=True)
            + "</p>"
        )
        preview_available = "false"
        item_count = 0
    else:
        cards_html = _voila_v0813_manual_study_preview_cards_html(preview_items)
        preview_available = "true"
        item_count = len(preview_items)

    return page(
        "Study · Manual Shadow",
        f"""
        <section class="v0813-manual-study" data-testid="manual-study-shadow-route">
          <h1>Study · Manual Shadow</h1>

          <p class="meta">
            Shadow mode owner-local pentru <code>/study</code>. Activ doar cu query explicit:
            <code>manual_study_shadow=1</code> și <code>course_id</code>.
          </p>

          <div class="v0815-study-top-nav" data-testid="manual-study-shadow-navigation">
            <span class="v0815-study-position">manual_study_shadow=<code>true</code></span>
            <a href="{html.escape(preview_href, quote=True)}" data-testid="manual-study-shadow-preview-link">Manual Study Preview</a>
            <a href="{html.escape(dry_run_href, quote=True)}" data-testid="manual-study-shadow-dry-run-link">Dry-run ON</a>
          </div>

          <p class="meta" data-testid="manual-study-shadow-source">
            course_id=<code>{safe_course_id_html}</code><br>
            source_artifact=<code>manual_study_items.preview.json</code><br>
            load_status=<code>{html.escape(load_status, quote=True)}</code><br>
            preview_available=<code>{preview_available}</code><br>
            item_count=<code>{item_count}</code><br>
            route=<code>/study</code><br>
            integration_mode=<code>read_only_shadow_toggle</code>
          </p>

          <p class="meta" data-testid="manual-study-shadow-policy">
            fallback_existing_study_available=<code>true</code><br>
            manual_study_connected_to_real_study=<code>shadow_only</code><br>
            replaces_existing_study_route=<code>false</code><br>
            progress_write=<code>false</code><br>
            answer_marking=<code>false</code><br>
            writes_legacy_study_items_preview=<code>false</code><br>
            study_artifact_written=<code>false</code><br>
            build_performed=<code>false</code><br>
            zip_created=<code>false</code><br>
            share_created=<code>false</code><br>
            delivery_performed=<code>false</code>
          </p>

          <div id="manual-study-preview-top" data-testid="manual-study-shadow-cards">
            {cards_html}
          </div>
        </section>
        """,
    )


@app.middleware("http")
async def _voila_v0822_manual_study_real_study_read_only_shadow_toggle_middleware(request, call_next):
    if getattr(request.url, "path", "") != "/study":
        return await call_next(request)

    shadow_enabled = _voila_v0822_manual_study_shadow_toggle_enabled(request.query_params.get("manual_study_shadow"))
    if not shadow_enabled:
        return await call_next(request)

    course_id = request.query_params.get("course_id")
    if not course_id:
        return page(
            "Study · Manual Shadow",
            """
            <section class="v0813-manual-study" data-testid="manual-study-shadow-missing-course">
              <h1>Study · Manual Shadow</h1>
              <p class="meta">Lipsește <code>course_id</code>. Fallback-ul /study existent rămâne disponibil când shadow toggle-ul lipsește.</p>
            </section>
            """,
        )

    return _voila_v0822_manual_study_shadow_page(course_id)
# VOILA_V0_8_22_MANUAL_STUDY_REAL_STUDY_READ_ONLY_SHADOW_TOGGLE_END

# VOILA_V0_8_27_MANUAL_STUDY_DEFAULT_STUDY_READ_ONLY_FALLBACK_START
def _voila_v0827_manual_study_default_page(pdf_name, course_id):
    safe_course_id, preview_data, preview_items, load_status = _voila_v0818_load_manual_study_items_preview(course_id)

    if preview_data is None or not preview_items:
        return None

    safe_course_id_html = html.escape(safe_course_id, quote=True)
    safe_pdf_html = html.escape(str(pdf_name or ""), quote=True)
    shadow_href = "/study?manual_study_shadow=1&course_id=" + quote(safe_course_id, safe="")
    preview_href = "/owner/manual-study-preview/" + quote(safe_course_id, safe="")
    dry_run_href = "/owner/manual-study-integration-dry-run/" + quote(safe_course_id, safe="") + "?enabled=1"

    cards_html = _voila_v0813_manual_study_preview_cards_html(preview_items)

    return page(
        "Voila! Study",
        f"""
        <section class="v0813-manual-study" data-testid="manual-study-default-route">
          <h1>Voila! Study · Manual Study</h1>

          <p class="meta">
            Manual Study este activ implicit pentru acest curs deoarece
            <code>manual_study_items.preview.json</code> există și este valid.
            Fallback-ul legacy rămâne disponibil automat când preview-ul lipsește sau nu este valid.
          </p>

          <div class="v0815-study-top-nav" data-testid="manual-study-default-navigation">
            <span class="v0815-study-position">default_study=<code>manual_study_read_only</code></span>
            <a href="{html.escape(shadow_href, quote=True)}" data-testid="manual-study-default-shadow-link">Study Manual Shadow</a>
            <a href="{html.escape(preview_href, quote=True)}" data-testid="manual-study-default-preview-link">Manual Study Preview</a>
            <a href="{html.escape(dry_run_href, quote=True)}" data-testid="manual-study-default-dry-run-link">Dry-run ON</a>
          </div>

          <p class="meta" data-testid="manual-study-default-source">
            pdf=<code>{safe_pdf_html}</code><br>
            course_id=<code>{safe_course_id_html}</code><br>
            source_artifact=<code>manual_study_items.preview.json</code><br>
            load_status=<code>{html.escape(load_status, quote=True)}</code><br>
            preview_available=<code>true</code><br>
            item_count=<code>{len(preview_items)}</code><br>
            route=<code>/study</code><br>
            integration_mode=<code>manual_study_default_read_only_fallback</code>
          </p>

          <p class="meta" data-testid="manual-study-default-policy">
            manual_study_default_enabled=<code>true</code><br>
            fallback_legacy_study_available=<code>true</code><br>
            manual_study_connected_to_real_study=<code>default_read_only_with_legacy_fallback</code><br>
            replaces_existing_study_route=<code>false</code><br>
            progress_write=<code>false</code><br>
            answer_marking=<code>false</code><br>
            writes_legacy_study_items_preview=<code>false</code><br>
            study_artifact_written=<code>false</code><br>
            build_performed=<code>false</code><br>
            zip_created=<code>false</code><br>
            share_created=<code>false</code><br>
            delivery_performed=<code>false</code>
          </p>

          <div id="manual-study-preview-top" data-testid="manual-study-default-cards">
            {cards_html}
          </div>
        </section>
        """,
    )


@app.middleware("http")
async def _voila_v0827_manual_study_default_study_read_only_fallback_middleware(request, call_next):
    if getattr(request.url, "path", "") != "/study":
        return await call_next(request)

    if _voila_v0822_manual_study_shadow_toggle_enabled(request.query_params.get("manual_study_shadow")):
        return await call_next(request)

    pdf_name = request.query_params.get("pdf")
    if not pdf_name:
        return await call_next(request)

    try:
        pdf_path = validate_pdf_name(pdf_name)
    except Exception:
        return await call_next(request)

    manual_default_page = _voila_v0827_manual_study_default_page(pdf_path.name, pdf_path.stem)
    if manual_default_page is None:
        return await call_next(request)

    return manual_default_page
# VOILA_V0_8_27_MANUAL_STUDY_DEFAULT_STUDY_READ_ONLY_FALLBACK_END

# VOILA_V0_8_42_EXAM_DOCUMENT_WORKFLOW_UX_POLISH_START
from starlette.responses import HTMLResponse as _VoilaV0842HTMLResponse
import html as _voila_v0842_html
import re as _voila_v0842_re
import urllib.parse as _voila_v0842_urllib_parse


def _voila_v0842_exam_workflow_card(pdf_name: str) -> str:
    safe_pdf = ""
    course_id = ""

    if isinstance(pdf_name, str):
        candidate = pdf_name.strip()
        if _voila_v0842_re.fullmatch(r"[A-Za-z0-9_.-]+\.pdf", candidate):
            safe_pdf = candidate
            course_id = candidate[:-4]

    safe_pdf_q = _voila_v0842_urllib_parse.quote(safe_pdf) if safe_pdf else ""
    safe_course_q = _voila_v0842_urllib_parse.quote(course_id) if course_id else ""

    review_href = f"/owner/manual-learning-evidence/{safe_course_q}?page=1" if safe_course_q else "#"
    preview_href = f"/owner/manual-study-preview/{safe_course_q}" if safe_course_q else "#"
    study_href = f"/study?pdf={safe_pdf_q}" if safe_pdf_q else "#"
    shadow_href = f"/study?manual_study_shadow=1&course_id={safe_course_q}" if safe_course_q else "#"
    dry_run_href = f"/owner/manual-study-integration-dry-run/{safe_course_q}?enabled=0" if safe_course_q else "#"

    safe_pdf_html = _voila_v0842_html.escape(safe_pdf or "documentul selectat")

    return f"""
<section class="voila-v0842-exam-workflow" data-testid="exam-document-workflow-ux-polish" aria-label="Învață pentru examen din acest document">
  <style>
    .voila-v0842-exam-workflow {{
      margin: 18px 0 22px;
      padding: 20px;
      border: 1px solid rgba(148, 163, 184, .35);
      border-radius: 18px;
      background: linear-gradient(135deg, rgba(15, 23, 42, .96), rgba(30, 64, 175, .18));
      box-shadow: 0 12px 30px rgba(15, 23, 42, .18);
    }}
    .voila-v0842-exam-workflow h2 {{
      margin: 0 0 6px;
      font-size: 1.35rem;
      line-height: 1.2;
    }}
    .voila-v0842-exam-workflow .voila-v0842-subtitle {{
      margin: 0 0 16px;
      color: #cbd5e1;
      max-width: 850px;
    }}
    .voila-v0842-exam-workflow .voila-v0842-document {{
      display: inline-flex;
      gap: 8px;
      align-items: center;
      margin: 0 0 14px;
      padding: 7px 10px;
      border-radius: 999px;
      background: rgba(15, 23, 42, .45);
      color: #e2e8f0;
      font-size: .92rem;
    }}
    .voila-v0842-exam-workflow ol {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 10px;
      padding: 0;
      margin: 0 0 16px;
      list-style: none;
      counter-reset: examWorkflow;
    }}
    .voila-v0842-exam-workflow li {{
      counter-increment: examWorkflow;
      padding: 13px;
      border-radius: 14px;
      background: rgba(15, 23, 42, .52);
      border: 1px solid rgba(148, 163, 184, .22);
      min-height: 94px;
    }}
    .voila-v0842-exam-workflow li::before {{
      content: counter(examWorkflow);
      display: inline-grid;
      place-items: center;
      width: 26px;
      height: 26px;
      margin-bottom: 8px;
      border-radius: 999px;
      background: #e0f2fe;
      color: #0f172a;
      font-weight: 800;
    }}
    .voila-v0842-exam-workflow strong {{
      display: block;
      color: #f8fafc;
      margin-bottom: 4px;
    }}
    .voila-v0842-exam-workflow span {{
      color: #cbd5e1;
      font-size: .92rem;
    }}
    .voila-v0842-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }}
    .voila-v0842-actions a {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 10px 13px;
      border-radius: 12px;
      text-decoration: none;
      background: #e0f2fe;
      color: #0f172a;
      font-weight: 700;
    }}
    .voila-v0842-actions a.secondary {{
      background: rgba(226, 232, 240, .12);
      color: #e2e8f0;
      border: 1px solid rgba(226, 232, 240, .22);
    }}
    .voila-v0842-diagnostic {{
      margin-top: 14px;
      color: #cbd5e1;
      font-size: .9rem;
    }}
    .voila-v0842-diagnostic summary {{
      cursor: pointer;
      color: #e2e8f0;
    }}
    .voila-v0842-diagnostic code {{
      color: #bfdbfe;
    }}
  </style>

  <h2>Învață pentru examen din acest document</h2>
  <p class="voila-v0842-subtitle">Transformă documentul în pași clari de învățare, cu text, formule și noțiuni verificate înainte să ajungă în Study.</p>
  <p class="voila-v0842-document">Document: <strong>{safe_pdf_html}</strong></p>

  <ol>
    <li><strong>Revizuiește documentul</strong><span>Corectează textul, formulele și zonele importante din pagină.</span></li>
    <li><strong>Alege noțiuni importante</strong><span>Marchează definiții, formule, exemple și teoreme utile.</span></li>
    <li><strong>Creează material de învățare</strong><span>Pregătește cardurile care vor intra în lecția de studiu.</span></li>
    <li><strong>Învață acum</strong><span>Deschide Study și parcurge cardurile verificate.</span></li>
    <li><strong>Exersează pentru examen</strong><span>Folosește noțiunile clare ca bază pentru întrebări și recapitulare.</span></li>
  </ol>

  <div class="voila-v0842-actions">
    <a href="{review_href}" data-testid="exam-workflow-review-document">Revizuiește documentul</a>
    <a href="{preview_href}" data-testid="exam-workflow-important-concepts">Alege noțiuni importante</a>
    <a href="{study_href}" data-testid="exam-workflow-study-now">Învață acum</a>
    <a class="secondary" href="{shadow_href}" data-testid="exam-workflow-study-shadow">Study verificat</a>
  </div>

  <details class="voila-v0842-diagnostic" data-testid="exam-workflow-technical-diagnostic">
    <summary>Diagnostic tehnic</summary>
    <p>Flux intern: <code>Manual Learning Evidence</code> → <code>Learning Pack preview</code> → <code>Manual Study Items preview</code> → <code>Study</code>.</p>
    <p>Dry-run tehnic: <a href="{dry_run_href}">deschide verificarea owner-local</a>.</p>
  </details>
</section>
"""


@app.middleware("http")
async def _voila_v0842_exam_document_workflow_ux_polish_middleware(request, call_next):
    response = await call_next(request)

    if getattr(request.url, "path", "") != "/course-tools":
        return response

    if response.status_code != 200:
        return response

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type.lower():
        return response

    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    html_text = body.decode("utf-8", errors="replace")
    if "data-testid=\"exam-document-workflow-ux-polish\"" in html_text:
        return _VoilaV0842HTMLResponse(content=html_text, status_code=response.status_code)

    pdf_name = request.query_params.get("pdf", "")
    card = _voila_v0842_exam_workflow_card(pdf_name)

    if "</main>" in html_text:
        html_text = html_text.replace("<main", "<main", 1)
        html_text = html_text.replace(">", ">" + card, 1) if "<main" in html_text else card + html_text
    elif "<body" in html_text:
        html_text = _voila_v0842_re.sub(r"(<body[^>]*>)", r"\1" + card, html_text, count=1, flags=_voila_v0842_re.IGNORECASE)
    else:
        html_text = card + html_text

    headers = dict(response.headers)
    for key in list(headers.keys()):
        if key.lower() == "content-length":
            headers.pop(key, None)

    return _VoilaV0842HTMLResponse(content=html_text, status_code=response.status_code, headers=headers)
# VOILA_V0_8_42_EXAM_DOCUMENT_WORKFLOW_UX_POLISH_END

# VOILA_V0_8_50_REVIEW_DOCUMENT_SHELL_READ_ONLY_FIRST_SLICE_START
from starlette.responses import HTMLResponse as _VoilaV0850HTMLResponse
import html as _voila_v0850_html
import urllib.parse as _voila_v0850_urllib_parse


def _voila_v0850_ascii_name_is_safe(value: str, *, require_pdf: bool) -> bool:
    if not isinstance(value, str):
        return False

    candidate = value.strip()
    if not candidate or len(candidate) > 180:
        return False

    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-")

    if any(ch not in allowed for ch in candidate):
        return False

    if "/" in candidate or "\\" in candidate:
        return False

    if candidate in {".", ".."} or candidate.startswith(".") or ".." in candidate:
        return False

    if require_pdf:
        if not candidate.lower().endswith(".pdf"):
            return False
        stem = candidate[:-4]
        return bool(stem) and stem not in {".", ".."}

    return True


def _voila_v0850_valid_pdf_name(value: str) -> bool:
    return _voila_v0850_ascii_name_is_safe(value, require_pdf=True)


def _voila_v0850_valid_course_id(value: str) -> bool:
    return _voila_v0850_ascii_name_is_safe(value, require_pdf=False)


def _voila_v0850_review_document_shell_html(*, pdf_name: str = "", course_id: str = "", lang: str = "ro") -> str:
    safe_pdf = pdf_name.strip() if _voila_v0850_valid_pdf_name(pdf_name) else ""
    safe_course = course_id.strip() if _voila_v0850_valid_course_id(course_id) else ""

    if safe_pdf and not safe_course:
        safe_course = safe_pdf[:-4]

    if safe_course and not safe_pdf:
        safe_pdf = safe_course + ".pdf"

    selected_lang = "en" if str(lang).strip().lower() == "en" else "ro"

    display_document = safe_pdf or safe_course or "documentul selectat"
    display_document_html = _voila_v0850_html.escape(display_document)

    safe_pdf_q = _voila_v0850_urllib_parse.quote(safe_pdf) if safe_pdf else ""
    course_tools_href = f"/course-tools?pdf={safe_pdf_q}" if safe_pdf_q else "/"

    language_badge_ro = "selectată" if selected_lang == "ro" else "disponibilă"
    language_badge_en = "selected" if selected_lang == "en" else "available"

    return f"""<!doctype html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <title>Revizuire document · Voila</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0f172a;
      --panel: rgba(15, 23, 42, .86);
      --panel-soft: rgba(30, 41, 59, .78);
      --border: rgba(148, 163, 184, .28);
      --text: #f8fafc;
      --muted: #cbd5e1;
      --accent: #e0f2fe;
      --accent-text: #0f172a;
    }}
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(59, 130, 246, .24), transparent 30rem),
        radial-gradient(circle at bottom right, rgba(14, 165, 233, .16), transparent 26rem),
        var(--bg);
      color: var(--text);
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px 18px 42px;
    }}
    .hero {{
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 24px;
      background: linear-gradient(135deg, rgba(15, 23, 42, .96), rgba(30, 64, 175, .22));
      box-shadow: 0 18px 42px rgba(0, 0, 0, .28);
    }}
    .eyebrow {{
      color: var(--muted);
      margin: 0 0 8px;
      font-size: .95rem;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: clamp(2rem, 5vw, 3.2rem);
      letter-spacing: -.04em;
    }}
    .subtitle {{
      color: var(--muted);
      max-width: 820px;
      line-height: 1.6;
      margin: 0;
    }}
    .meta-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 18px;
    }}
    .pill {{
      border: 1px solid var(--border);
      background: rgba(15, 23, 42, .52);
      color: var(--muted);
      border-radius: 999px;
      padding: 8px 12px;
      font-size: .95rem;
    }}
    .pill strong {{
      color: var(--text);
    }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(0, 1.6fr) minmax(280px, .8fr);
      gap: 16px;
      margin-top: 18px;
    }}
    @media (max-width: 860px) {{
      .layout {{
        grid-template-columns: 1fr;
      }}
    }}
    .card {{
      border: 1px solid var(--border);
      border-radius: 20px;
      background: var(--panel);
      padding: 18px;
    }}
    .steps {{
      display: grid;
      gap: 10px;
      counter-reset: reviewSteps;
      list-style: none;
      margin: 0;
      padding: 0;
    }}
    .step {{
      counter-increment: reviewSteps;
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 12px;
      align-items: start;
      padding: 14px;
      border-radius: 16px;
      background: var(--panel-soft);
      border: 1px solid rgba(148, 163, 184, .18);
    }}
    .step::before {{
      content: counter(reviewSteps);
      display: inline-grid;
      place-items: center;
      width: 32px;
      height: 32px;
      border-radius: 999px;
      background: var(--accent);
      color: var(--accent-text);
      font-weight: 800;
    }}
    .step strong {{
      display: block;
      margin-bottom: 4px;
    }}
    .step span {{
      color: var(--muted);
      line-height: 1.45;
    }}
    .guidance h2,
    .card h2 {{
      margin-top: 0;
      letter-spacing: -.02em;
    }}
    .guidance p,
    .guidance li {{
      color: var(--muted);
      line-height: 1.55;
    }}
    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 18px;
    }}
    .button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 12px;
      padding: 10px 14px;
      text-decoration: none;
      font-weight: 750;
      background: var(--accent);
      color: var(--accent-text);
    }}
    .button.secondary {{
      background: rgba(226, 232, 240, .10);
      color: var(--text);
      border: 1px solid var(--border);
    }}
    details {{
      margin-top: 16px;
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 12px 14px;
      background: rgba(15, 23, 42, .56);
    }}
    summary {{
      cursor: pointer;
      font-weight: 750;
    }}
    code {{
      color: #bfdbfe;
    }}
  </style>
</head>
<body>
<main data-testid="review-document-shell-read-only" data-voila-version="v0.8.50">
  <section class="hero" aria-label="Revizuire document">
    <p class="eyebrow">Voila! — Documentele tale, lecții clare</p>
    <h1>Revizuire document</h1>
    <p class="subtitle">Verifică textul, formulele și imaginile înainte să creezi lecția. Acest prim slice este read-only: arată noul flux ghidat, fără să scrie date și fără să pornească motoare.</p>
    <div class="meta-row">
      <span class="pill">Document: <strong>{display_document_html}</strong></span>
      <span class="pill">Limba lecției: <strong>Română</strong> · {language_badge_ro}</span>
      <span class="pill">English · {language_badge_en}</span>
      <span class="pill">Mod: <strong>read-only</strong></span>
    </div>
  </section>

  <section class="layout">
    <article class="card" aria-label="Pași de revizuire">
      <h2>Pașii pentru pregătirea lecției</h2>
      <ol class="steps">
        <li class="step" data-testid="review-step-text-detected"><div><strong>Text detectat</strong><span>Verifici textul extras din document, pe pagini și fragmente clare.</span></div></li>
        <li class="step" data-testid="review-step-corrections"><div><strong>Corecturi sugerate</strong><span>Primești sugestii prietenoase pentru corectarea textului.</span></div></li>
        <li class="step" data-testid="review-step-visuals"><div><strong>Formule și imagini</strong><span>Selectezi formule, diagrame, desene, tabele sau grafice importante.</span></div></li>
        <li class="step" data-testid="review-step-important-concepts"><div><strong>Noțiuni importante</strong><span>Alegi ce merită să intre în lecție și adaugi explicații pe înțeles.</span></div></li>
        <li class="step" data-testid="review-step-ready-study"><div><strong>Gata pentru studiu</strong><span>Confirmi ce este pregătit pentru Study curat.</span></div></li>
      </ol>
      <div class="actions">
        <a class="button" href="{course_tools_href}" data-testid="review-document-back-course-tools">Înapoi la Course Tools</a>
        <a class="button secondary" href="/" data-testid="review-document-back-home">Acasă</a>
      </div>
    </article>

    <aside class="card guidance" aria-label="Ghid pentru student">
      <h2>Ce faci aici?</h2>
      <p>Voila te va ghida pas cu pas. Motoarele tehnice rulează în fundal; tu trebuie doar să confirmi ce este corect și ce merită învățat.</p>
      <ul>
        <li>Nu trebuie să știi ce înseamnă OCR, bbox sau JSON.</li>
        <li>Nu editezi metadata.</li>
        <li>Pregătești explicații clare pentru lecție.</li>
      </ul>
      <p><strong>Următorul pas:</strong> legăm acest shell din Course Tools, apoi adăugăm coada pentru Text detectat.</p>

      <details data-testid="review-document-technical-diagnostic">
        <summary>Diagnostic tehnic</summary>
        <p>Slice: <code>v0.8.50 read-only learner shell</code></p>
        <p>Rută primară: <code>/review-document?pdf={{pdf_name}}</code></p>
        <p>Alias: <code>/review-document/{{course_id}}</code></p>
        <p>Nu scrie date, nu rulează OCR, nu rulează LanguageTool, nu rulează crop, nu schimbă Study.</p>
      </details>
    </aside>
  </section>
</main>
</body>
</html>"""


@app.get("/review-document", response_class=_VoilaV0850HTMLResponse)
async def _voila_v0850_review_document_shell_query(pdf: str = "", lang: str = "ro"):
    safe_pdf = pdf.strip() if _voila_v0850_valid_pdf_name(pdf) else ""
    return _VoilaV0850HTMLResponse(
        content=_voila_v0850_review_document_shell_html(pdf_name=safe_pdf, lang=lang),
        status_code=200,
    )


@app.get("/review-document/{course_id}", response_class=_VoilaV0850HTMLResponse)
async def _voila_v0850_review_document_shell_course(course_id: str, lang: str = "ro"):
    safe_course = course_id.strip() if _voila_v0850_valid_course_id(course_id) else ""
    return _VoilaV0850HTMLResponse(
        content=_voila_v0850_review_document_shell_html(course_id=safe_course, lang=lang),
        status_code=200,
    )
# VOILA_V0_8_50_REVIEW_DOCUMENT_SHELL_READ_ONLY_FIRST_SLICE_END

# VOILA_V0_8_51_COURSE_TOOLS_LINK_TO_REVIEW_DOCUMENT_SHELL_START
from starlette.requests import Request as _VoilaV0851Request
from starlette.responses import HTMLResponse as _VoilaV0851HTMLResponse
import urllib.parse as _voila_v0851_urllib_parse


def _voila_v0851_review_document_course_tools_card(pdf_name: str) -> str:
    safe_pdf = pdf_name.strip() if _voila_v0850_valid_pdf_name(pdf_name) else ""
    if not safe_pdf:
        return ""

    safe_pdf_q = _voila_v0851_urllib_parse.quote(safe_pdf)
    href = "/review-document?pdf=" + safe_pdf_q

    return f"""
<section class="voila-v0851-review-document-entry" data-testid="course-tools-review-document-entry" style="margin:18px 0;padding:18px;border:1px solid rgba(148,163,184,.28);border-radius:18px;background:rgba(15,23,42,.76);">
  <p style="margin:0 0 6px;color:#cbd5e1;">Voila! — Documentele tale, lecții clare</p>
  <h2 style="margin:0 0 8px;color:#f8fafc;">Revizuire document</h2>
  <p style="margin:0 0 14px;color:#cbd5e1;line-height:1.55;">Înainte de Study curat, verifică textul, corecturile, formulele și imaginile într-un flux ghidat.</p>
  <a data-testid="course-tools-review-document-link" href="{href}" style="display:inline-flex;align-items:center;justify-content:center;border-radius:12px;padding:10px 14px;text-decoration:none;font-weight:750;background:#e0f2fe;color:#0f172a;">Deschide Revizuire document</a>
</section>
"""


def _voila_v0851_inject_review_document_entry(html_text: str, pdf_name: str) -> str:
    if not isinstance(html_text, str) or "course-tools-review-document-entry" in html_text:
        return html_text

    card = _voila_v0851_review_document_course_tools_card(pdf_name)
    if not card:
        return html_text

    if "</main>" in html_text:
        return html_text.replace("</main>", card + "\n</main>", 1)

    if "</body>" in html_text:
        return html_text.replace("</body>", card + "\n</body>", 1)

    return html_text + card


@app.middleware("http")
async def _voila_v0851_course_tools_review_document_link_middleware(request: _VoilaV0851Request, call_next):
    response = await call_next(request)

    if request.url.path != "/course-tools":
        return response

    pdf_name = request.query_params.get("pdf", "")
    if not _voila_v0850_valid_pdf_name(pdf_name):
        return response

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        return response

    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    html_text = body.decode("utf-8", errors="replace")
    updated = _voila_v0851_inject_review_document_entry(html_text, pdf_name)

    headers = dict(response.headers)
    headers.pop("content-length", None)

    return _VoilaV0851HTMLResponse(
        content=updated,
        status_code=response.status_code,
        headers=headers,
    )
# VOILA_V0_8_51_COURSE_TOOLS_LINK_TO_REVIEW_DOCUMENT_SHELL_END

# VOILA_V0_8_52_TEXT_DETECTED_READ_ONLY_QUEUE_START
from pathlib import Path as _VoilaV0852Path
import json as _voila_v0852_json
from starlette.requests import Request as _VoilaV0852Request
from starlette.responses import HTMLResponse as _VoilaV0852HTMLResponse


def _voila_v0852_repo_root() -> _VoilaV0852Path:
    return _VoilaV0852Path(__file__).resolve().parents[2]


def _voila_v0852_course_id_from_pdf(pdf_name: str) -> str:
    safe_pdf = pdf_name.strip() if _voila_v0850_valid_pdf_name(pdf_name) else ""
    if not safe_pdf:
        return ""
    return safe_pdf[:-4]


def _voila_v0852_find_course_output_dir(course_id: str):
    safe_course = course_id.strip() if _voila_v0850_valid_course_id(course_id) else ""
    if not safe_course:
        return None

    output_root = _voila_v0852_repo_root() / "data" / "output"
    if not output_root.exists() or not output_root.is_dir():
        return None

    for child in output_root.iterdir():
        try:
            if child.is_dir() and child.name == safe_course:
                return child
        except OSError:
            continue

    return None


def _voila_v0852_clean_text_fragment(value: str, limit: int = 900) -> str:
    if not isinstance(value, str):
        return ""

    lines = []
    for raw_line in value.splitlines():
        line = " ".join(raw_line.strip().split())
        if line:
            lines.append(line)

    cleaned = "\n".join(lines).strip()
    if len(cleaned) > limit:
        cleaned = cleaned[:limit].rstrip() + "…"

    return cleaned


def _voila_v0852_text_from_page_item(item) -> str:
    if not isinstance(item, dict):
        if isinstance(item, str):
            return item
        return ""

    for key in [
        "text",
        "ocr_text",
        "page_text",
        "content",
        "markdown",
        "body",
        "raw_text",
    ]:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value

    blocks = item.get("blocks")
    if isinstance(blocks, list):
        parts = []
        for block in blocks:
            if isinstance(block, dict):
                for key in ["text", "ocr_text", "content", "value"]:
                    value = block.get(key)
                    if isinstance(value, str) and value.strip():
                        parts.append(value)
                        break
            elif isinstance(block, str) and block.strip():
                parts.append(block)
        return "\n".join(parts)

    return ""


def _voila_v0852_page_number_from_item(item, fallback: int) -> int:
    if not isinstance(item, dict):
        return fallback

    for key in ["page", "page_number", "page_index", "index"]:
        value = item.get(key)
        if isinstance(value, int):
            if key in {"page_index", "index"} and value >= 0:
                return value + 1
            if value > 0:
                return value

    return fallback


def _voila_v0852_load_pages_json(course_dir: _VoilaV0852Path):
    source = course_dir / "pages.json"
    if not source.exists() or not source.is_file():
        return [], ""

    try:
        payload = _voila_v0852_json.loads(source.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return [], "pages.json"

    if isinstance(payload, dict):
        raw_pages = payload.get("pages")
        if not isinstance(raw_pages, list):
            raw_pages = payload.get("items")
        if not isinstance(raw_pages, list):
            raw_pages = []
    elif isinstance(payload, list):
        raw_pages = payload
    else:
        raw_pages = []

    blocks = []
    for index, item in enumerate(raw_pages, start=1):
        fragment = _voila_v0852_clean_text_fragment(_voila_v0852_text_from_page_item(item))
        if not fragment:
            continue
        blocks.append(
            {
                "page": _voila_v0852_page_number_from_item(item, index),
                "text": fragment,
            }
        )
        if len(blocks) >= 8:
            break

    return blocks, "pages.json"


def _voila_v0852_load_pages_md(course_dir: _VoilaV0852Path):
    source = course_dir / "pages.md"
    if not source.exists() or not source.is_file():
        return [], ""

    try:
        content = source.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return [], "pages.md"

    current_page = 1
    current_lines = []
    blocks = []

    def flush():
        nonlocal current_lines, current_page, blocks
        fragment = _voila_v0852_clean_text_fragment("\n".join(current_lines))
        if fragment:
            blocks.append({"page": current_page, "text": fragment})
        current_lines = []

    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        lowered = stripped.lower()

        if stripped.startswith("#") and "pagina" in lowered:
            flush()
            digits = "".join(ch for ch in stripped if ch.isdigit())
            if digits:
                try:
                    current_page = max(1, int(digits))
                except ValueError:
                    current_page = len(blocks) + 1
            else:
                current_page = len(blocks) + 1
            continue

        if stripped:
            current_lines.append(stripped)

        if len(blocks) >= 8:
            break

    if len(blocks) < 8:
        flush()

    return blocks[:8], "pages.md"


def _voila_v0852_load_existing_ocr_blocks(pdf_name: str = "", course_id: str = ""):
    safe_course = course_id.strip() if _voila_v0850_valid_course_id(course_id) else ""
    if not safe_course:
        safe_course = _voila_v0852_course_id_from_pdf(pdf_name)

    if not safe_course:
        return {
            "course_id": "",
            "source": "",
            "blocks": [],
            "status": "missing_course",
        }

    course_dir = _voila_v0852_find_course_output_dir(safe_course)
    if course_dir is None:
        return {
            "course_id": safe_course,
            "source": "",
            "blocks": [],
            "status": "missing_output_dir",
        }

    for loader in [_voila_v0852_load_pages_json, _voila_v0852_load_pages_md]:
        blocks, source_name = loader(course_dir)
        if blocks:
            return {
                "course_id": safe_course,
                "source": source_name,
                "blocks": blocks,
                "status": "loaded",
            }

    return {
        "course_id": safe_course,
        "source": "",
        "blocks": [],
        "status": "missing_text_artifact",
    }


def _voila_v0852_text_detected_section(pdf_name: str = "", course_id: str = "") -> str:
    data = _voila_v0852_load_existing_ocr_blocks(pdf_name=pdf_name, course_id=course_id)
    blocks = data.get("blocks", [])
    status = data.get("status", "")
    source = data.get("source", "")

    cards = []

    if blocks:
        for block in blocks:
            page = block.get("page", "?")
            text_fragment = _voila_v0850_html.escape(str(block.get("text", "")).strip())
            cards.append(
                f"""
<article data-testid="text-detected-block-card" style="padding:14px;border:1px solid rgba(148,163,184,.22);border-radius:16px;background:rgba(30,41,59,.74);">
  <p style="margin:0 0 8px;color:#cbd5e1;font-weight:750;">Pagina {page} · Doar citire</p>
  <p style="white-space:pre-wrap;margin:0;color:#f8fafc;line-height:1.55;">{text_fragment}</p>
</article>
"""
            )
    else:
        cards.append(
            """
<div data-testid="text-detected-empty-state" style="padding:14px;border:1px solid rgba(148,163,184,.22);border-radius:16px;background:rgba(30,41,59,.74);">
  <p style="margin:0;color:#f8fafc;font-weight:750;">Nu găsesc încă fragmente detectate pentru acest document.</p>
  <p style="margin:8px 0 0;color:#cbd5e1;line-height:1.55;">Această secțiune nu pornește OCR. Va afișa textul doar după ce există artefacte locale deja generate.</p>
</div>
"""
        )

    visible_count = len(blocks)

    return f"""
<section data-testid="review-document-text-detected-queue" style="margin-top:18px;padding:18px;border:1px solid rgba(148,163,184,.28);border-radius:18px;background:rgba(15,23,42,.72);">
  <p style="margin:0 0 6px;color:#cbd5e1;">Pasul 1</p>
  <h2 style="margin:0 0 8px;color:#f8fafc;">Text detectat</h2>
  <p style="margin:0 0 14px;color:#cbd5e1;line-height:1.55;">Fragmente detectate din document, afișate pentru verificare. Acum este doar citire: nu salvăm, nu corectăm și nu rescriem textul.</p>
  <p data-testid="text-detected-read-only-status" style="margin:0 0 14px;color:#e0f2fe;font-weight:750;">Fragmente detectate: {visible_count} · Doar citire</p>
  <div style="display:grid;gap:10px;">{''.join(cards)}</div>
  <details data-testid="text-detected-diagnostic" style="margin-top:14px;">
    <summary>Diagnostic tehnic pentru Text detectat</summary>
    <p>Status-top:14px;">
    <summary>Diagnostic tehnic pentru Text detectat</summary>
    <p>Status: <code>{_voila_v0850_html.escape(status)}</code></p>
    <p>Sursă locală citită: <code>{_voila_v0850_html.escape(source or "niciuna")}</code></p>
    <p>Nu s-a rulat OCR. Nu s-a scris niciun artefact.</p>
  </details>
</section>
"""


def _voila_v0852_extract_review_target(request: _VoilaV0852Request):
    path = request.url.path

    if path == "/review-document":
        pdf_name = request.query_params.get("pdf", "")
        safe_pdf = pdf_name.strip() if _voila_v0850_valid_pdf_name(pdf_name) else ""
        return safe_pdf, ""

    prefix = "/review-document/"
    if path.startswith(prefix):
        candidate = path[len(prefix):].strip()
        safe_course = candidate if _voila_v0850_valid_course_id(candidate) else ""
        return "", safe_course

    return "", ""


def _voila_v0852_inject_text_detected_queue(html_text: str, pdf_name: str = "", course_id: str = "") -> str:
    if not isinstance(html_text, str) or "review-document-text-detected-queue" in html_text:
        return html_text

    section = _voila_v0852_text_detected_section(pdf_name=pdf_name, course_id=course_id)

    marker = "</ol>"
    if marker in html_text:
        return html_text.replace(marker, marker + "\n" + section, 1)

    fallback = "</article>"
    if fallback in html_text:
        return html_text.replace(fallback, section + "\n" + fallback, 1)

    return html_text + section


@app.middleware("http")
async def _voila_v0852_text_detected_read_only_queue_middleware(request: _VoilaV0852Request, call_next):
    response = await call_next(request)

    if not (request.url.path == "/review-document" or request.url.path.startswith("/review-document/")):
        return response

    pdf_name, course_id = _voila_v0852_extract_review_target(request)
    if not pdf_name and not course_id:
        return response

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        return response

    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    html_text = body.decode("utf-8", errors="replace")
    updated = _voila_v0852_inject_text_detected_queue(html_text, pdf_name=pdf_name, course_id=course_id)

    headers = dict(response.headers)
    headers.pop("content-length", None)

    return _VoilaV0852HTMLResponse(
        content=updated,
        status_code=response.status_code,
        headers=headers,
    )
# VOILA_V0_8_52_TEXT_DETECTED_READ_ONLY_QUEUE_END
