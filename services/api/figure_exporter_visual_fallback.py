from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

import fitz
import numpy as np
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"




def load_ocr_text_by_page(output_dir: Path) -> dict[int, str]:
    candidates = [
        output_dir / "ocr_pages.cleaned.json",
        output_dir / "ocr_pages.json",
        output_dir / "pages.json",
    ]

    for path in candidates:
        if not path.exists():
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        if isinstance(data, dict):
            pages = data.get("pages") or data.get("items") or []
        elif isinstance(data, list):
            pages = data
        else:
            pages = []

        result = {}

        for idx, page in enumerate(pages, start=1):
            if not isinstance(page, dict):
                continue

            page_number = int(page.get("page_number") or page.get("pdf_page") or idx)
            page_text = str(page.get("text") or page.get("content") or "").strip()

            if page_text:
                result[page_number] = page_text

        if result:
            return result

    return {}


def page_has_figure_caption(page_text: str) -> bool:
    text = page_text or ""
    lower = text.lower()

    # Never treat table of contents / index pages as figure pages.
    if "cuprins" in lower:
        return False

    if "bibliografie" in lower:
        return False

    if "index" in lower and len(text) > 500:
        return False

    # For scanned PDFs, accept only explicit figure captions.
    patterns = [
        r"(?im)^\s*(?:fig\.|figura)\s*[IVXLCDM0-9]+(?:[.\-]\d+)*",
        r"(?im)\b(?:fig\.|figura)\s*[IVXLCDM0-9]+(?:[.\-]\d+)*",
    ]

    return any(re.search(pattern, text) for pattern in patterns)


def safe_number(value: str) -> str:
    value = re.sub(r"[^0-9A-Za-z._-]+", "_", value)
    return value.strip("_") or "visual"


def find_runs(active: np.ndarray, gap: int, min_size: int) -> list[tuple[int, int]]:
    runs = []
    start = None
    last = None

    for idx, flag in enumerate(active):
        if flag:
            if start is None:
                start = idx
            last = idx
        elif start is not None and last is not None and idx - last > gap:
            if last - start + 1 >= min_size:
                runs.append((start, last + 1))
            start = None
            last = None

    if start is not None and last is not None:
        if last - start + 1 >= min_size:
            runs.append((start, last + 1))

    return runs


def page_to_image(page: fitz.Page, zoom: float) -> Image.Image:
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


def detect_visual_blocks(image: Image.Image, max_per_page: int) -> list[tuple[int, int, int, int]]:
    gray = image.convert("L")
    arr = np.array(gray)

    height, width = arr.shape

    # Ignore page edges.
    margin_x = int(width * 0.04)
    margin_y = int(height * 0.04)

    mask = arr < 220
    mask[:margin_y, :] = False
    mask[height - margin_y:, :] = False
    mask[:, :margin_x] = False
    mask[:, width - margin_x:] = False

    row_counts = mask.sum(axis=1)
    row_threshold = max(8, int(width * 0.006))
    active_rows = row_counts > row_threshold

    row_runs = find_runs(
        active_rows,
        gap=max(10, int(height * 0.012)),
        min_size=max(80, int(height * 0.075)),
    )

    candidates = []

    for y0, y1 in row_runs:
        block = mask[y0:y1, :]
        col_counts = block.sum(axis=0)
        col_threshold = max(5, int((y1 - y0) * 0.006))
        active_cols = col_counts > col_threshold

        col_runs = find_runs(
            active_cols,
            gap=max(10, int(width * 0.015)),
            min_size=max(120, int(width * 0.18)),
        )

        if not col_runs:
            continue

        x0 = min(run[0] for run in col_runs)
        x1 = max(run[1] for run in col_runs)

        pad_x = int(width * 0.018)
        pad_y = int(height * 0.018)

        x0 = max(0, x0 - pad_x)
        y0 = max(0, y0 - pad_y)
        x1 = min(width, x1 + pad_x)
        y1 = min(height, y1 + pad_y)

        w = x1 - x0
        h = y1 - y0

        if w < width * 0.28:
            continue

        if h < height * 0.08:
            continue

        density = mask[y0:y1, x0:x1].mean()

        # Text-only blocks tend to be too narrow or too dense/regular.
        if density < 0.003 or density > 0.28:
            continue

        # Avoid full-page captures unless page really appears mostly visual.
        if w > width * 0.94 and h > height * 0.88 and density < 0.015:
            continue

        area = (w * h) / (width * height)

        candidates.append(
            {
                "rect": (x0, y0, x1, y1),
                "area": area,
                "density": float(density),
            }
        )

    # Prefer larger visual regions.
    candidates.sort(key=lambda item: item["area"], reverse=True)

    # Remove near-duplicates / nested crops.
    selected = []

    for candidate in candidates:
        x0, y0, x1, y1 = candidate["rect"]

        duplicate = False

        for existing in selected:
            ex0, ey0, ex1, ey1 = existing
            ix0 = max(x0, ex0)
            iy0 = max(y0, ey0)
            ix1 = min(x1, ex1)
            iy1 = min(y1, ey1)

            if ix1 <= ix0 or iy1 <= iy0:
                continue

            intersection = (ix1 - ix0) * (iy1 - iy0)
            area = (x1 - x0) * (y1 - y0)

            if intersection / max(1, area) > 0.70:
                duplicate = True
                break

        if not duplicate:
            selected.append(candidate["rect"])

        if len(selected) >= max_per_page:
            break

    return selected


def extract_possible_caption(page_text: str, page_no: int, index: int) -> tuple[str, str]:
    patterns = [
        r"(?im)^\s*(?:fig\.|figura|figure)\s*([IVXLCDM0-9]+(?:[.\-][0-9]+)*)\.?\s+(.{3,180})$",
        r"(?im)\b(?:fig\.|figura|figure)\s*([IVXLCDM0-9]+(?:[.\-][0-9]+)*)\.?\s+(.{3,180})",
    ]

    matches = []

    for pattern in patterns:
        matches.extend(re.findall(pattern, page_text or ""))

    if matches:
        number, caption = matches[min(index, len(matches) - 1)]
        caption = re.sub(r"\s+", " ", caption).strip(" .:-")
        return number.strip(), caption[:180]

    number = f"p{page_no}.{index + 1}"
    caption = f"Visual figure candidate from PDF page {page_no}"
    return number, caption


def crop_text_word_count(page: fitz.Page, rect_points: list[float]) -> int:
    try:
        rect = fitz.Rect(rect_points)
        value = page.get_textbox(rect) or ""
    except Exception:
        return 0

    words = re.findall(r"[A-Za-zĂÂÎȘȚăâîșț0-9]{2,}", value)
    return len(words)


def crop_is_text_heavy(page: fitz.Page, rect_points: list[float], crop_area_ratio: float) -> bool:
    words = crop_text_word_count(page, rect_points)

    # Paragraphs, table-of-contents blocks, lists, and page text should not become figures.
    if words >= 25:
        return True

    # Smaller blocks with enough text are usually headings / lists, not figures.
    if crop_area_ratio < 0.28 and words >= 16:
        return True

    return False



def write_html(figures_dir: Path, pdf_path: Path, items: list[dict], page_from: int, page_to: int) -> None:
    cards = []

    for item in items:
        image_path = html.escape(item["relative_path"].replace("\\", "/"))
        number = html.escape(str(item["number"]))
        caption = html.escape(str(item["caption"]))
        page = html.escape(str(item["pdf_page"]))

        cards.append(
            f"""
            <article class="card">
              <h2>Figure {number}</h2>
              <p>{caption}</p>
              <p class="meta">PDF page {page} · visual_fallback</p>
              <img src="{image_path}" alt="Figure {number} {caption}">
            </article>
            """
        )

    if not cards:
        cards.append(
            """
            <article class="card">
              <h2>No figures detected</h2>
              <p>No visual figure candidates were detected in this range.</p>
            </article>
            """
        )

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Voila! Visual Figure Extraction</title>
  <style>
    body {{
      margin: 0;
      background: #efe5d2;
      color: #111827;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      padding: 36px;
    }}

    .wrap {{
      background: #f7efdf;
      border: 1px solid #d8bd92;
      border-radius: 24px;
      padding: 36px;
      box-shadow: 0 16px 48px rgba(0,0,0,0.12);
    }}

    h1 {{
      font-size: 42px;
      margin-top: 0;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 24px;
      margin-top: 24px;
    }}

    .card {{
      background: #fbf5e8;
      border: 1px solid #d8bd92;
      border-radius: 22px;
      padding: 24px;
      overflow: hidden;
    }}

    .card h2 {{
      font-size: 30px;
      margin: 0 0 12px;
    }}

    .meta {{
      color: #7a644a;
    }}

    img {{
      max-width: 100%;
      height: auto;
      display: block;
      border-radius: 16px;
      border: 1px solid #d8bd92;
      background: white;
      margin-top: 18px;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Voila! Visual Figure Extraction</h1>
    <p>Source: <code>{html.escape(str(pdf_path))}</code></p>
    <p>Page range: {page_from}–{page_to}</p>
    <p>Detected figures: {len(items)}</p>

    <div class="grid">
      {''.join(cards)}
    </div>
  </div>
</body>
</html>
"""

    (figures_dir / "figures_hybrid.html").write_text(html_text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! visual fallback figure extractor")
    parser.add_argument("pdf")
    parser.add_argument("--page-from", type=int, default=1)
    parser.add_argument("--page-to", type=int, default=0)
    parser.add_argument("--zoom", type=float, default=1.8)
    parser.add_argument("--max-items", type=int, default=180)
    parser.add_argument("--max-per-page", type=int, default=3)

    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()
    out_dir = OUTPUT_DIR / pdf_path.stem
    figures_dir = out_dir / "figures_hybrid"
    crops_dir = figures_dir / "crops"

    figures_dir.mkdir(parents=True, exist_ok=True)
    crops_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    ocr_text_by_page = load_ocr_text_by_page(out_dir)
    page_to = args.page_to if args.page_to > 0 else len(doc)
    page_to = min(page_to, len(doc))
    page_from = max(1, args.page_from)

    items = []

    for page_no in range(page_from, page_to + 1):
        if len(items) >= args.max_items:
            break

        page = doc[page_no - 1]
        embedded_text = page.get_text("text") or ""
        page_text = embedded_text.strip() or ocr_text_by_page.get(page_no, "")

        # For scanned/image PDFs, do not extract random text blocks as figures.
        # Require an OCR-visible figure caption on the page.
        if ocr_text_by_page and not page_has_figure_caption(page_text):
            print(f"Skip page without figure caption: {page_no}")
            continue

        image = page_to_image(page, args.zoom)

        blocks = detect_visual_blocks(image, max_per_page=args.max_per_page)

        for block_index, (x0, y0, x1, y1) in enumerate(blocks):
            if len(items) >= args.max_items:
                break

            number, caption = extract_possible_caption(page_text, page_no, block_index)
            safe = safe_number(number)

            filename = f"visual_figure_{safe}_page_{page_no:03d}_{len(items) + 1:03d}.png"
            rel_path = Path("crops") / filename
            out_path = figures_dir / rel_path

            # Convert pixel crop to PDF-point approximate crop.
            crop_rect = [
                x0 / args.zoom,
                y0 / args.zoom,
                x1 / args.zoom,
                y1 / args.zoom,
            ]

            crop_area_ratio = ((x1 - x0) * (y1 - y0)) / max(1, image.width * image.height)

            if crop_is_text_heavy(page, crop_rect, crop_area_ratio):
                print(f"Skip text-heavy visual block: page {page_no}, words={crop_text_word_count(page, crop_rect)}")
                continue

            crop = image.crop((x0, y0, x1, y1))
            crop.save(out_path)

            items.append(
                {
                    "number": number,
                    "caption": caption,
                    "pdf_page": page_no,
                    "crop_method": "visual_fallback",
                    "relative_path": str(rel_path),
                    "crop_rect": crop_rect,
                }
            )

    doc.close()

    manifest = {
        "version": "visual_fallback_v0.2_text_filtered",
        "source_file": str(pdf_path),
        "render_zoom": args.zoom,
        "page_from": page_from,
        "page_to": page_to,
        "figure_crops": items,
    }

    (figures_dir / "figures_manifest.hybrid.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    write_html(figures_dir, pdf_path, items, page_from, page_to)

    print("Voila! visual fallback figure extraction complete.")
    print(f"Detected figures: {len(items)}")
    print(f"- {figures_dir / 'figures_hybrid.html'}")
    print(f"- {figures_dir / 'figures_manifest.hybrid.json'}")


if __name__ == "__main__":
    main()
