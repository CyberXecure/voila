from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


def inline_markdown(text: str) -> str:
    safe = html.escape(text)
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    safe = re.sub(r"`(.+?)`", r"<code>\1</code>", safe)
    return safe


def load_figure_map(md_path: Path) -> dict[str, dict]:
    manifest_path = md_path.parent / "figures" / "figures_manifest.json"

    if not manifest_path.exists():
        return {}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    figure_map = {}

    for item in manifest.get("figure_crops", []):
        number = str(item.get("number", "")).strip()
        rel = Path("figures") / item.get("relative_path", "")
        figure_map[number] = {
            "number": number,
            "caption": item.get("caption", ""),
            "pdf_page": item.get("pdf_page", ""),
            "src": rel.as_posix(),
        }

    return figure_map


def figure_html(item: dict) -> str:
    title = f"Figure {html.escape(str(item['number']))}"
    caption = html.escape(str(item.get("caption", "")))
    src = html.escape(str(item.get("src", "")))
    page = html.escape(str(item.get("pdf_page", "")))

    return f"""
<figure class="figure-card">
  <img src="{src}" alt="{title} {caption}">
  <figcaption>
    <strong>{title}</strong> — {caption}
    <span>PDF page {page}</span>
  </figcaption>
</figure>
"""


def markdown_to_html(markdown: str, figure_map: dict[str, dict]) -> str:
    lines = markdown.splitlines()
    output = []
    in_code = False
    code_lines = []
    in_ul = False
    in_ol = False
    current_section = ""

    def close_lists() -> None:
        nonlocal in_ul, in_ol

        if in_ul:
            output.append("</ul>")
            in_ul = False

        if in_ol:
            output.append("</ol>")
            in_ol = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            if not in_code:
                close_lists()
                in_code = True
                code_lines = []
            else:
                output.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                in_code = False
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not stripped:
            close_lists()
            continue

        if stripped.startswith("# "):
            close_lists()
            current_section = ""
            output.append(f"<h1>{inline_markdown(stripped[2:])}</h1>")
            continue

        if stripped.startswith("## "):
            close_lists()
            current_section = ""
            output.append(f"<h2>{inline_markdown(stripped[3:])}</h2>")
            continue

        if stripped.startswith("### "):
            close_lists()
            current_section = stripped[4:].strip().lower()
            output.append(f"<h3>{inline_markdown(stripped[4:])}</h3>")
            continue

        if stripped.startswith("- "):
            figure_match = re.match(r"^- Figure\s+([0-9]+(?:\.[0-9]+)?)\s*:", stripped)

            if current_section == "figures" and figure_match:
                close_lists()
                number = figure_match.group(1)
                item = figure_map.get(number)

                if item:
                    output.append(figure_html(item))
                else:
                    output.append(f"<p>{inline_markdown(stripped[2:])}</p>")

                continue

            if not in_ul:
                close_lists()
                output.append("<ul>")
                in_ul = True

            output.append(f"<li>{inline_markdown(stripped[2:])}</li>")
            continue

        ordered = re.match(r"^(\d+)\.\s+(.+)$", stripped)

        if ordered:
            if not in_ol:
                close_lists()
                output.append("<ol>")
                in_ol = True

            output.append(f"<li>{inline_markdown(ordered.group(2))}</li>")
            continue

        close_lists()
        output.append(f"<p>{inline_markdown(stripped)}</p>")

    close_lists()

    return "\n".join(output)


def build_html(title: str, body: str) -> str:
    template = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <script>
    (function () {
      const saved = localStorage.getItem("voila-theme");
      const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
      const theme = saved || (prefersDark ? "dark" : "light");
      document.documentElement.setAttribute("data-theme", theme);
    })();
  </script>
  <style>
    :root {
      --bg: #e8dfd0;
      --paper: #f5ecd9;
      --paper-soft: #efe3cc;
      --text: #2f2a24;
      --muted: #75695c;
      --heading: #241e19;
      --accent: #8a5a32;
      --accent-soft: #ead7b8;
      --accent-strong: #65401f;
      --teal: #2f6f6d;
      --border: #d7c5a8;
      --source-bg: #efe4d0;
      --source-text: #2d2923;
      --source-border: #d2bea0;
      --shadow: rgba(62, 45, 28, 0.16);
      color-scheme: light;
    }

    html[data-theme="dark"] {
      --bg: #151a1d;
      --paper: #20272b;
      --paper-soft: #263035;
      --text: #d8d0c3;
      --muted: #a79d90;
      --heading: #f1e7d8;
      --accent: #d7a86e;
      --accent-soft: #3a3026;
      --accent-strong: #f0c98d;
      --teal: #72b8b2;
      --border: #3a444a;
      --source-bg: #192023;
      --source-text: #e2d8c9;
      --source-border: #3a444a;
      --shadow: rgba(0, 0, 0, 0.34);
      color-scheme: dark;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      background:
        radial-gradient(circle at top left, rgba(138, 90, 50, 0.14), transparent 34%),
        linear-gradient(180deg, var(--paper-soft) 0%, var(--bg) 100%);
      color: var(--text);
      font-family: "Segoe UI", Arial, sans-serif;
      line-height: 1.72;
      font-size: 17px;
    }

    html[data-theme="dark"] body {
      background:
        radial-gradient(circle at top left, rgba(215, 168, 110, 0.10), transparent 34%),
        linear-gradient(180deg, #1b2226 0%, var(--bg) 100%);
    }

    .theme-bar {
      position: sticky;
      top: 0;
      z-index: 10;
      display: flex;
      justify-content: flex-end;
      max-width: 1040px;
      margin: 0 auto;
      padding: 14px 20px 0;
    }

    .theme-toggle {
      border: 1px solid var(--border);
      background: var(--paper);
      color: var(--text);
      border-radius: 999px;
      padding: 9px 14px;
      font-size: 14px;
      font-weight: 650;
      cursor: pointer;
      box-shadow: 0 8px 24px var(--shadow);
    }

    main {
      max-width: 1040px;
      margin: 24px auto 42px;
      padding: 46px;
      background: var(--paper);
      border: 1px solid var(--border);
      border-radius: 26px;
      box-shadow: 0 22px 58px var(--shadow);
    }

    h1 {
      margin: 0 0 20px;
      padding-bottom: 22px;
      border-bottom: 1px solid var(--border);
      color: var(--heading);
      font-size: 36px;
      line-height: 1.2;
      letter-spacing: -0.03em;
    }

    h2 {
      margin-top: 52px;
      padding-top: 30px;
      border-top: 1px solid var(--border);
      color: var(--heading);
      font-size: 30px;
      line-height: 1.25;
      letter-spacing: -0.025em;
    }

    h2::before {
      content: "";
      display: block;
      width: 58px;
      height: 5px;
      margin-bottom: 16px;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--accent), var(--teal));
    }

    h3 {
      margin-top: 32px;
      margin-bottom: 14px;
      color: var(--accent-strong);
      font-size: 20px;
      line-height: 1.35;
    }

    ul,
    ol {
      margin: 10px 0 20px;
      padding-left: 28px;
    }

    li {
      margin: 9px 0;
    }

    li::marker {
      color: var(--accent);
      font-weight: 700;
    }

    h3 + ul,
    h3 + ol {
      background: var(--paper-soft);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 18px 24px 18px 38px;
    }

    code {
      background: var(--accent-soft);
      color: var(--accent-strong);
      padding: 2px 7px;
      border-radius: 7px;
      font-size: 0.94em;
    }

    pre {
      white-space: pre-wrap;
      background: var(--source-bg);
      color: var(--source-text);
      padding: 24px;
      border-radius: 18px;
      overflow-x: auto;
      border: 1px solid var(--source-border);
      font-size: 15.5px;
      line-height: 1.68;
    }

    pre code {
      background: transparent;
      color: inherit;
      padding: 0;
      border-radius: 0;
      font-size: inherit;
    }

    .figure-card {
      margin: 18px 0 26px;
      padding: 18px;
      background: var(--paper-soft);
      border: 1px solid var(--border);
      border-radius: 18px;
    }

    .figure-card img {
      display: block;
      width: 100%;
      max-width: 780px;
      height: auto;
      margin: 0 auto;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: #fff;
    }

    .figure-card figcaption {
      margin-top: 12px;
      color: var(--muted);
      font-size: 15px;
      text-align: center;
    }

    .figure-card figcaption span {
      display: block;
      margin-top: 4px;
      font-size: 13px;
    }

    strong {
      color: var(--heading);
    }

    @media (max-width: 760px) {
      .theme-bar {
        padding: 10px 10px 0;
      }

      main {
        margin: 12px 0 0;
        padding: 24px;
        border-radius: 0;
      }

      body {
        font-size: 16px;
      }

      h1 {
        font-size: 30px;
      }

      h2 {
        font-size: 25px;
      }
    }
  </style>
</head>
<body>
  <div class="theme-bar">
    <button class="theme-toggle" type="button" id="themeToggle">Toggle theme</button>
  </div>

  <main>
__BODY__
  </main>

  <script>
    (function () {
      const root = document.documentElement;
      const button = document.getElementById("themeToggle");

      function label(theme) {
        button.textContent = theme === "dark" ? "☀ Light mode" : "🌙 Dark mode";
      }

      function setTheme(theme) {
        root.setAttribute("data-theme", theme);
        localStorage.setItem("voila-theme", theme);
        label(theme);
      }

      const current = root.getAttribute("data-theme") || "light";
      label(current);

      button.addEventListener("click", function () {
        const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
        setTheme(next);
      });
    })();
  </script>
</body>
</html>
"""

    return (
        template
        .replace("__TITLE__", html.escape(title))
        .replace("__BODY__", body)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! Markdown to HTML exporter with figures")
    parser.add_argument("course_cleaned_md", help="Path to course.cleaned.md")

    args = parser.parse_args()

    md_path = Path(args.course_cleaned_md).resolve()

    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    markdown = md_path.read_text(encoding="utf-8")
    title = markdown.splitlines()[0].replace("#", "").strip() or "Voila! Course"

    figure_map = load_figure_map(md_path)
    body = markdown_to_html(markdown, figure_map)
    html_doc = build_html(title, body)

    html_path = md_path.parent / "course.cleaned.html"
    html_path.write_text(html_doc, encoding="utf-8")

    print("Voila! HTML course exported successfully.")
    print(f"Figures linked: {len(figure_map)}")
    print(f"- {html_path}")


if __name__ == "__main__":
    main()
