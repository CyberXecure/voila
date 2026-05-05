from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

import fitz
from PIL import Image


FIGURE_START_RE = re.compile(
    r"^\s*(?:Figure|Ftgure|Fig11re)\s+([0-9]+(?:\.[0-9]+)?)\s*(.*)$",
    re.IGNORECASE,
)


def normalize_text(text: str) -> str:
    text = text.replace("Ftgure", "Figure")
    text = text.replace("Fig11re", "Figure")
    text = text.replace("Auto-Ktean", "Auto-Klean")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def safe_name(value: str) -> str:
    value = value.lower().strip()
    value = value.replace(".", "_")
    value = re.sub(r"[^a-z0-9_-]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_")


def get_line_text(line: dict) -> str:
    return normalize_text("".join(span.get("text", "") for span in line.get("spans", [])))


def get_line_bbox(line: dict) -> fitz.Rect:
    boxes = []

    for span in line.get("spans", []):
        bbox = span.get("bbox")
        if bbox:
            boxes.append(fitz.Rect(bbox))

    if not boxes:
        return fitz.Rect(0, 0, 0, 0)

    rect = boxes[0]

    for box in boxes[1:]:
        rect |= box

    return rect


def extract_text_lines(page: fitz.Page) -> list[dict]:
    data = page.get_text("dict")
    lines = []

    for block in data.get("blocks", []):
        if block.get("type") != 0:
            continue

        for line in block.get("lines", []):
            text = get_line_text(line)
            bbox = get_line_bbox(line)

            if not text:
                continue

            lines.append(
                {
                    "text": text,
                    "bbox": bbox,
                }
            )

    lines.sort(key=lambda item: (item["bbox"].y0, item["bbox"].x0))
    return lines


def is_caption_continuation(text: str) -> bool:
    lower = text.lower().strip()

    if not lower:
        return False

    if re.match(r"^[a-z]", lower):
        return True

    if lower.startswith(("service ", "and ", "or ", "separation ", "water ", "oil ")):
        return True

    return False


def find_figure_captions(page: fitz.Page) -> list[dict]:
    lines = extract_text_lines(page)
    captions = []

    for index, item in enumerate(lines):
        text = item["text"]
        match = FIGURE_START_RE.match(text)

        if not match:
            continue

        number = match.group(1)
        caption = normalize_text(match.group(2))
        bbox = fitz.Rect(item["bbox"])

        # Capture captions split across the next line.
        for next_item in lines[index + 1:index + 3]:
            next_text = next_item["text"]
            next_bbox = next_item["bbox"]
            vertical_gap = next_bbox.y0 - bbox.y1

            if vertical_gap < -2 or vertical_gap > 24:
                continue

            if not caption or caption in {".", "-"} or is_caption_continuation(next_text):
                caption = normalize_text((caption + " " + next_text).strip())
                bbox |= next_bbox

        caption = caption.strip(" .,-")

        captions.append(
            {
                "number": number,
                "caption": caption,
                "bbox": [bbox.x0, bbox.y0, bbox.x1, bbox.y1],
            }
        )

    # De-duplicate same figure on same page.
    grouped = {}

    for caption in captions:
        key = caption["number"]
        existing = grouped.get(key)

        if not existing:
            grouped[key] = caption
            continue

        existing_text = existing.get("caption", "")
        new_text = caption.get("caption", "")

        if len(new_text) > len(existing_text):
            old_box = fitz.Rect(existing["bbox"])
            new_box = fitz.Rect(caption["bbox"])
            combined = old_box | new_box
            caption["bbox"] = [combined.x0, combined.y0, combined.x1, combined.y1]
            grouped[key] = caption

    return list(grouped.values())


def page_to_image(page: fitz.Page, zoom: float) -> Image.Image:
    matrix = fitz.Matrix(zoom, zoom)
    pixmap = page.get_pixmap(matrix=matrix, alpha=False)
    return Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)


def save_page_image(page: fitz.Page, output_path: Path, zoom: float) -> None:
    image = page_to_image(page, zoom)
    image.save(output_path)


def row_has_ink(gray: Image.Image, y: int, x0: int, x1: int, threshold: int = 225) -> bool:
    width = max(1, x1 - x0)
    step = max(1, width // 420)
    dark = 0
    samples = 0

    pixels = gray.load()

    for x in range(x0, x1, step):
        samples += 1

        if pixels[x, y] < threshold:
            dark += 1

    return samples > 0 and (dark / samples) > 0.006


def col_has_ink(gray: Image.Image, x: int, y0: int, y1: int, threshold: int = 225) -> bool:
    height = max(1, y1 - y0)
    step = max(1, height // 420)
    dark = 0
    samples = 0

    pixels = gray.load()

    for y in range(y0, y1, step):
        samples += 1

        if pixels[x, y] < threshold:
            dark += 1

    return samples > 0 and (dark / samples) > 0.006


def find_blank_band_up(gray: Image.Image, start_y: int, x0: int, x1: int, min_blank: int) -> int:
    blank_count = 0

    for y in range(start_y, 0, -1):
        has_ink = row_has_ink(gray, y, x0, x1)

        if has_ink:
            blank_count = 0
            continue

        blank_count += 1

        if blank_count >= min_blank:
            return y + min_blank

    return 0


def find_blank_band_down(gray: Image.Image, start_y: int, x0: int, x1: int, min_blank: int) -> int:
    blank_count = 0
    height = gray.height

    for y in range(start_y, height):
        has_ink = row_has_ink(gray, y, x0, x1)

        if has_ink:
            blank_count = 0
            continue

        blank_count += 1

        if blank_count >= min_blank:
            return y - min_blank

    return height


def tighten_x(gray: Image.Image, y0: int, y1: int, margin: int) -> tuple[int, int]:
    width = gray.width
    xs = []

    for x in range(0, width, 2):
        if col_has_ink(gray, x, y0, y1):
            xs.append(x)

    if not xs:
        return 0, width

    return max(0, min(xs) - margin), min(width, max(xs) + margin)


def crop_figure_from_caption(page: fitz.Page, caption_bbox: list[float], zoom: float) -> Image.Image:
    image = page_to_image(page, zoom)
    gray = image.convert("L")

    cap = fitz.Rect(caption_bbox)

    cap_x0 = int(cap.x0 * zoom)
    cap_y0 = int(cap.y0 * zoom)
    cap_x1 = int(cap.x1 * zoom)
    cap_y1 = int(cap.y1 * zoom)

    width = image.width
    height = image.height

    scan_x0 = int(width * 0.04)
    scan_x1 = int(width * 0.96)

    margin = int(26 * zoom)
    min_blank = int(34 * zoom)

    # Search for the large blank band above the drawing, not the small gap near the caption.
    y0 = find_blank_band_up(gray, max(0, cap_y0 - int(12 * zoom)), scan_x0, scan_x1, min_blank)
    y1 = find_blank_band_down(gray, min(height - 1, cap_y1 + int(8 * zoom)), scan_x0, scan_x1, min_blank)

    y0 = max(0, y0 - margin)
    y1 = min(height, y1 + margin)

    x0, x1 = tighten_x(gray, y0, y1, margin)

    # Avoid extremely tiny crops.
    if (y1 - y0) < int(110 * zoom):
        y0 = max(0, cap_y0 - int(260 * zoom))
        y1 = min(height, cap_y1 + int(80 * zoom))
        x0, x1 = tighten_x(gray, y0, y1, margin)

    return image.crop((x0, y0, x1, y1))


def build_gallery_html(manifest: dict, output_path: Path) -> None:
    cards = []

    for item in manifest.get("figure_crops", []):
        rel = Path(item["relative_path"]).as_posix()
        title = f"Figure {item['number']}"
        caption = item.get("caption") or ""

        cards.append(
            f"""
            <article class="card">
              <h2>{html.escape(title)}</h2>
              <p>{html.escape(caption)}</p>
              <p class="meta">PDF page {item['pdf_page']}</p>
              <img src="{html.escape(rel)}" alt="{html.escape(title + ' ' + caption)}">
            </article>
            """
        )

    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Voila! Figures</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg: #e8dfd0;
      --paper: #f5ecd9;
      --paper-soft: #efe3cc;
      --text: #2f2a24;
      --heading: #241e19;
      --muted: #75695c;
      --border: #d7c5a8;
      --accent: #8a5a32;
    }}

    body {{
      margin: 0;
      background: linear-gradient(180deg, #eee4d2 0%, var(--bg) 100%);
      color: var(--text);
      font-family: "Segoe UI", Arial, sans-serif;
      line-height: 1.6;
    }}

    main {{
      max-width: 1180px;
      margin: 40px auto;
      padding: 34px;
      background: var(--paper);
      border: 1px solid var(--border);
      border-radius: 24px;
      box-shadow: 0 22px 58px rgba(62, 45, 28, 0.16);
    }}

    h1 {{
      margin-top: 0;
      color: var(--heading);
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 24px;
    }}

    .card {{
      background: rgba(255,255,255,0.34);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 18px;
    }}

    .card h2 {{
      margin: 0 0 6px;
      color: var(--heading);
      font-size: 22px;
    }}

    .card p {{
      margin: 6px 0;
    }}

    .meta {{
      color: var(--muted);
      font-size: 14px;
    }}

    img {{
      width: 100%;
      height: auto;
      display: block;
      margin-top: 14px;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: white;
    }}
  </style>
</head>
<body>
  <main>
    <h1>Voila! Extracted Figures</h1>
    <p>Source: <code>{html.escape(manifest.get("source_file", ""))}</code></p>
    <p>Detected figure crops: {len(manifest.get("figure_crops", []))}</p>
    <div class="grid">
      {''.join(cards)}
    </div>
  </main>
</body>
</html>
"""

    output_path.write_text(doc, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! figure and drawing exporter v2")
    parser.add_argument("pdf", help="Path to source PDF")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--zoom", type=float, default=3.4)

    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if args.output_dir:
        figures_dir = Path(args.output_dir).resolve()
    else:
        figures_dir = Path("data/output").resolve() / pdf_path.stem / "figures"

    pages_dir = figures_dir / "pages"
    crops_dir = figures_dir / "crops"

    pages_dir.mkdir(parents=True, exist_ok=True)
    crops_dir.mkdir(parents=True, exist_ok=True)

    for old_png in crops_dir.glob("*.png"):
        old_png.unlink()

    doc = fitz.open(pdf_path)

    manifest = {
        "source_file": str(pdf_path),
        "page_count": doc.page_count,
        "render_zoom": args.zoom,
        "page_images": [],
        "figure_crops": [],
    }

    for page_index, page in enumerate(doc, start=1):
        page_image_name = f"page_{page_index:03d}.png"
        page_image_path = pages_dir / page_image_name

        save_page_image(page, page_image_path, args.zoom)

        manifest["page_images"].append(
            {
                "pdf_page": page_index,
                "path": str(page_image_path),
                "relative_path": str(page_image_path.relative_to(figures_dir)),
            }
        )

        captions = find_figure_captions(page)

        for caption in captions:
            number = caption["number"]
            caption_text = caption["caption"]

            crop_image = crop_figure_from_caption(page, caption["bbox"], args.zoom)

            crop_name = f"figure_{safe_name(number)}_page_{page_index:03d}.png"
            crop_path = crops_dir / crop_name
            crop_image.save(crop_path)

            manifest["figure_crops"].append(
                {
                    "number": number,
                    "caption": caption_text,
                    "pdf_page": page_index,
                    "path": str(crop_path),
                    "relative_path": str(crop_path.relative_to(figures_dir)),
                    "caption_bbox": caption["bbox"],
                }
            )

    manifest_path = figures_dir / "figures_manifest.json"
    html_path = figures_dir / "figures.html"

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    build_gallery_html(manifest, html_path)

    print("Voila! figures exported successfully.")
    print(f"Source: {pdf_path}")
    print(f"Output: {figures_dir}")
    print(f"Page images: {len(manifest['page_images'])}")
    print(f"Figure crops: {len(manifest['figure_crops'])}")
    print(f"- {manifest_path}")
    print(f"- {html_path}")


if __name__ == "__main__":
    main()
