from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

import fitz
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"


def load_pages_text_length(output_dir: Path) -> int:
    pages_path = output_dir / "pages.json"

    if not pages_path.exists():
        return 0

    try:
        data = json.loads(pages_path.read_text(encoding="utf-8"))
    except Exception:
        return 0

    if isinstance(data, dict):
        pages = data.get("pages") or data.get("items") or []
    elif isinstance(data, list):
        pages = data
    else:
        pages = []

    total = 0

    for page in pages:
        if isinstance(page, dict):
            value = page.get("text") or page.get("content") or ""
            total += len(str(value).strip())

    return total


def should_apply_fallback(output_dir: Path, min_text_chars: int) -> bool:
    text_length = load_pages_text_length(output_dir)

    if text_length < min_text_chars:
        return True

    course_md = output_dir / "course.cleaned.md"

    if course_md.exists() and len(course_md.read_text(encoding="utf-8", errors="ignore").strip()) < 700:
        return True

    return False


def render_pages(pdf_path: Path, output_dir: Path, zoom: float) -> list[dict]:
    pages_dir = output_dir / "scanned_pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    pages = []

    for index, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)

        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        filename = f"page_{index:04d}.jpg"
        out_path = pages_dir / filename

        image.save(out_path, quality=88, optimize=True)

        pages.append(
            {
                "page_number": index,
                "relative_path": f"scanned_pages/{filename}",
                "width": image.width,
                "height": image.height,
            }
        )

    doc.close()
    return pages


def write_html(pdf_path: Path, output_dir: Path, pages: list[dict], zoom: float) -> Path:
    title = pdf_path.stem
    course_html = output_dir / "course.cleaned.html"

    page_cards = []

    for page in pages:
        page_number = page["page_number"]
        rel_path = html.escape(page["relative_path"])

        page_cards.append(
            f"""
            <article class="scan-page" id="page-{page_number}">
              <div class="page-head">
                <h2>Page {page_number}</h2>
                <a href="#top">Top</a>
              </div>
              <img src="{rel_path}" alt="Scanned PDF page {page_number}" loading="lazy">
            </article>
            """
        )

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)} — Voila! scanned reading mode</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg: #111819;
      --panel: #1d292c;
      --panel-soft: #243235;
      --text: #f4ead9;
      --muted: #c8b79d;
      --border: #3b4a4e;
      --accent: #e0ae6b;
      --paper: #f5efe2;
    }}

    html {{
      scroll-behavior: smooth;
    }}

    body {{
      margin: 0;
      background:
        radial-gradient(circle at top, rgba(224, 174, 107, 0.10), transparent 38%),
        var(--bg);
      color: var(--text);
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
      padding: 34px;
    }}

    .wrap {{
      max-width: 1180px;
      margin: 0 auto;
    }}

    .hero {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 28px;
      padding: 34px;
      box-shadow: 0 22px 70px rgba(0,0,0,0.30);
      margin-bottom: 28px;
    }}

    h1 {{
      font-size: clamp(34px, 5vw, 58px);
      line-height: 1.08;
      margin: 0 0 18px;
    }}

    .meta {{
      color: var(--muted);
      font-size: 18px;
    }}

    .notice {{
      margin-top: 22px;
      background: var(--panel-soft);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 18px 20px;
      color: var(--muted);
    }}

    .toc {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 22px;
    }}

    .toc a {{
      color: var(--text);
      text-decoration: none;
      background: var(--panel-soft);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 8px 12px;
      font-weight: 700;
    }}

    .scan-page {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 28px;
      padding: 24px;
      margin: 26px 0;
      box-shadow: 0 18px 52px rgba(0,0,0,0.24);
    }}

    .page-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 16px;
    }}

    .page-head h2 {{
      margin: 0;
      font-size: 28px;
    }}

    .page-head a {{
      color: var(--accent);
      text-decoration: none;
      font-weight: 800;
    }}

    .scan-page img {{
      display: block;
      width: 100%;
      max-width: 960px;
      height: auto;
      margin: 0 auto;
      background: var(--paper);
      border-radius: 18px;
      border: 1px solid rgba(224, 174, 107, 0.45);
      box-shadow: 0 16px 44px rgba(0,0,0,0.28);
    }}

    @media (max-width: 760px) {{
      body {{
        padding: 14px;
      }}

      .hero,
      .scan-page {{
        border-radius: 20px;
        padding: 18px;
      }}

      .page-head h2 {{
        font-size: 22px;
      }}
    }}
  </style>
</head>
<body id="top">
  <main class="wrap">
    <section class="hero">
      <h1>{html.escape(title)}</h1>

      <div class="meta">
        Generated by Voila! scanned reading fallback<br>
        Source: <code>{html.escape(str(pdf_path))}</code><br>
        Pages: <strong>{len(pages)}</strong> · Render zoom: <strong>{zoom}</strong>
      </div>

      <div class="notice">
        This PDF appears to be scan/image-based. Normal text extraction returned too little text,
        so Voila! generated a visual reading course from rendered page images.
      </div>

      <nav class="toc" aria-label="Page navigation">
        {''.join(f'<a href="#page-{page["page_number"]}">Page {page["page_number"]}</a>' for page in pages[:80])}
      </nav>
    </section>

    {''.join(page_cards)}
  </main>
</body>
</html>
"""

    course_html.write_text(html_text, encoding="utf-8")
    return course_html


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! scanned PDF course fallback")
    parser.add_argument("pdf", help="Source PDF path")
    parser.add_argument("output_dir", help="Voila output directory")
    parser.add_argument("--zoom", type=float, default=1.45)
    parser.add_argument("--min-text-chars", type=int, default=800)
    parser.add_argument("--force", action="store_true")

    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if not args.force and not should_apply_fallback(output_dir, args.min_text_chars):
        print("Voila! scanned fallback skipped: enough text was extracted.")
        return

    pages = render_pages(pdf_path, output_dir, args.zoom)
    course_html = write_html(pdf_path, output_dir, pages, args.zoom)

    manifest = {
        "version": "scanned_course_fallback_v0.1",
        "source_file": str(pdf_path),
        "render_zoom": args.zoom,
        "page_count": len(pages),
        "pages": pages,
    }

    (output_dir / "scanned_course_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Voila! scanned PDF course fallback generated successfully.")
    print(f"Pages rendered: {len(pages)}")
    print(f"- {course_html}")
    print(f"- {output_dir / 'scanned_course_manifest.json'}")


if __name__ == "__main__":
    main()
