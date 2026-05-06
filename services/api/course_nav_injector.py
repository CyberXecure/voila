from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import quote


NAV_MARKER_START = "<!-- VOILA_FIXED_COURSE_NAV_START -->"
NAV_MARKER_END = "<!-- VOILA_FIXED_COURSE_NAV_END -->"


def remove_existing_nav(text: str) -> str:
    start = text.find(NAV_MARKER_START)
    end = text.find(NAV_MARKER_END)

    if start != -1 and end != -1 and end > start:
        end += len(NAV_MARKER_END)
        return text[:start] + text[end:]

    return text


def file_exists_near_course(html_path: Path, relative_path: str) -> bool:
    return (html_path.parent / relative_path).exists()


def build_nav(html_path: Path, pdf_name: str) -> str:
    encoded_pdf = quote(pdf_name)
    app_base = "http://127.0.0.1:8787"

    links = [
        f'<a href="{app_base}/">Back</a>',
    ]

    if file_exists_near_course(html_path, "quiz.study.json") or file_exists_near_course(html_path, "quiz.json"):
        links.append(f'<a class="secondary" href="{app_base}/study?pdf={encoded_pdf}">Study</a>')
        links.append(f'<a class="secondary" href="{app_base}/progress?pdf={encoded_pdf}">Progress</a>')

    if file_exists_near_course(html_path, "figures_hybrid/figures_hybrid.html"):
        links.append('<a class="secondary" href="figures_hybrid/figures_hybrid.html">Figures</a>')

    if file_exists_near_course(html_path, "figures_hybrid/figures_manifest.hybrid.json"):
        links.append(f'<a class="secondary" href="http://127.0.0.1:8790/?pdf={encoded_pdf}">Edit crops</a>')

    links.append('<button type="button" onclick="window.scrollTo({ top: 0, behavior: \'smooth\' })">↑ Top</button>')
    links.append('<button type="button" onclick="window.scrollTo({ top: document.documentElement.scrollHeight, behavior: \'smooth\' })">↓ Bottom</button>')

    links_html = "\n  ".join(links)

    return f"""
{NAV_MARKER_START}
<style>
  body {{
    padding-bottom: 112px !important;
  }}

  .voila-course-fixed-nav {{
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
    background: rgba(24, 33, 35, 0.90);
    border: 1px solid rgba(215, 197, 168, 0.45);
    border-radius: 999px;
    box-shadow: 0 18px 48px rgba(0,0,0,0.36);
    backdrop-filter: blur(10px);
  }}

  .voila-course-fixed-nav a,
  .voila-course-fixed-nav button {{
    border: 1px solid rgba(215, 197, 168, 0.55);
    background: #e0ae6b;
    color: #fffaf0;
    border-radius: 999px;
    padding: 9px 14px;
    font-weight: 800;
    cursor: pointer;
    text-decoration: none;
    font-size: 14px;
    white-space: nowrap;
    line-height: 1;
    font-family: inherit;
  }}

  .voila-course-fixed-nav a.secondary,
  .voila-course-fixed-nav button.secondary {{
    background: rgba(239, 227, 204, 0.12);
    color: #f5ecd9;
  }}

  .voila-course-fixed-nav a:hover,
  .voila-course-fixed-nav button:hover {{
    transform: translateY(-1px);
    filter: brightness(1.05);
  }}

  @media (max-width: 760px) {{
    body {{
      padding-bottom: 158px !important;
    }}

    .voila-course-fixed-nav {{
      left: 10px;
      right: 10px;
      bottom: calc(10px + env(safe-area-inset-bottom));
      transform: none;
      max-width: none;
      flex-wrap: wrap;
      border-radius: 22px;
      padding: 10px;
    }}

    .voila-course-fixed-nav a,
    .voila-course-fixed-nav button {{
      flex: 1 1 30%;
      min-width: 88px;
      padding: 10px 8px;
      font-size: 13px;
      text-align: center;
    }}
  }}
</style>

<nav class="voila-course-fixed-nav" aria-label="Voila course navigation">
  {links_html}
</nav>

<script>
  (function () {{
    document.addEventListener("click", function (event) {{
      const link = event.target.closest("a");
      if (!link) return;

      const href = link.getAttribute("href") || "";

      if (
        href.startsWith("/") ||
        href.startsWith("http://127.0.0.1") ||
        href.startsWith("http://localhost") ||
        href.startsWith("figures_hybrid/")
      ) {{
        link.removeAttribute("target");
      }}
    }});
  }})();
</script>
{NAV_MARKER_END}
"""


def inject_nav(html_path: Path, pdf_name: str) -> None:
    text = html_path.read_text(encoding="utf-8")
    text = remove_existing_nav(text)

    nav = build_nav(html_path, pdf_name)

    if "</body>" in text:
        text = text.replace("</body>", nav + "\n</body>", 1)
    else:
        text = text + "\n" + nav

    html_path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inject Voila navigation into course HTML")
    parser.add_argument("html_path", help="Path to course.cleaned.html")
    parser.add_argument("pdf_name", help="Original PDF file name, including .pdf")

    args = parser.parse_args()

    html_path = Path(args.html_path).resolve()

    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    inject_nav(html_path, args.pdf_name)

    print("Voila! course navigation injected successfully.")
    print(f"- {html_path}")
    print(f"PDF: {args.pdf_name}")


if __name__ == "__main__":
    main()
