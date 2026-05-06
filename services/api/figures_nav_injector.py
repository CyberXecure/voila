from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import quote


START = "<!-- VOILA_FIGURES_NAV_START -->"
END = "<!-- VOILA_FIGURES_NAV_END -->"


def strip_existing(text: str) -> str:
    start = text.find(START)
    end = text.find(END)

    if start != -1 and end != -1 and end > start:
        end += len(END)
        return text[:start] + text[end:]

    return text


def inject(html_path: Path, pdf_name: str) -> None:
    encoded_pdf = quote(pdf_name)
    app_base = "http://127.0.0.1:8787"

    nav = f"""
{START}
<style>
  body {{
    padding-bottom: 132px !important;
  }}

  .voila-figures-fixed-nav {{
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

  .voila-figures-fixed-nav a,
  .voila-figures-fixed-nav button {{
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

  .voila-figures-fixed-nav a.secondary,
  .voila-figures-fixed-nav button.secondary {{
    background: rgba(239, 227, 204, 0.12);
    color: #f5ecd9;
  }}

  @media (max-width: 760px) {{
    body {{
      padding-bottom: 170px !important;
    }}

    .voila-figures-fixed-nav {{
      left: 10px;
      right: 10px;
      bottom: calc(10px + env(safe-area-inset-bottom));
      transform: none;
      max-width: none;
      flex-wrap: wrap;
      border-radius: 22px;
    }}

    .voila-figures-fixed-nav a,
    .voila-figures-fixed-nav button {{
      flex: 1 1 30%;
      min-width: 88px;
      padding: 10px 8px;
      font-size: 13px;
      text-align: center;
    }}
  }}
</style>

<nav class="voila-figures-fixed-nav" aria-label="Voila figures navigation">
  <a href="{app_base}/">Back</a>
  <a class="secondary" href="../course.cleaned.html">Course</a>
  <a class="secondary" href="{app_base}/study?pdf={encoded_pdf}">Study</a>
  <a class="secondary" href="{app_base}/progress?pdf={encoded_pdf}">Progress</a>
  <a class="secondary" href="http://127.0.0.1:8790/?pdf={encoded_pdf}">Edit crops</a>
  <button type="button" onclick="window.scrollTo({{ top: 0, behavior: 'smooth' }})">↑ Top</button>
  <button type="button" onclick="window.scrollTo({{ top: document.documentElement.scrollHeight, behavior: 'smooth' }})">↓ Bottom</button>
</nav>
{END}
"""

    text = html_path.read_text(encoding="utf-8")
    text = strip_existing(text)

    if "</body>" in text:
        text = text.replace("</body>", nav + "\n</body>", 1)
    else:
        text += "\n" + nav

    html_path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inject navigation into Voila figures HTML")
    parser.add_argument("html_path")
    parser.add_argument("pdf_name")

    args = parser.parse_args()

    html_path = Path(args.html_path).resolve()

    if not html_path.exists():
        raise FileNotFoundError(f"Figures HTML not found: {html_path}")

    inject(html_path, args.pdf_name)

    print("Voila! figures navigation injected successfully.")
    print(f"- {html_path}")


if __name__ == "__main__":
    main()
