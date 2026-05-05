from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

import fitz


CAPTION_RE = re.compile(
    r"^\s*(?:Figure|Fig\.?|FIGURE|FIG\.?)\s+([0-9]+(?:[.\-][0-9A-Za-z]+)*)\s*[:.\-]?\s*(.*)$",
    re.IGNORECASE,
)

BAD_CAPTION_STARTS = (
    "shows ",
    "show ",
    "illustrates ",
    "illustrate ",
    "is ",
    "are ",
    "was ",
    "were ",
    "gives ",
    "give ",
    "describes ",
    "describe ",
    "contains ",
    "contain ",
    "indicates ",
    "indicate ",
    "represents ",
    "represent ",
)


def normalize_text(text: str) -> str:
    text = text.replace("Ftgure", "Figure")
    text = text.replace("Fig11re", "Figure")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def safe_name(value: str) -> str:
    value = value.lower().strip()
    value = value.replace(".", "_").replace("-", "_")
    value = re.sub(r"[^a-z0-9_-]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_") or "figure"


def line_text(line: dict) -> str:
    return normalize_text("".join(span.get("text", "") for span in line.get("spans", [])))


def line_bbox(line: dict) -> fitz.Rect:
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


def get_text_lines(page: fitz.Page) -> list[dict]:
    data = page.get_text("dict")
    lines = []

    for block in data.get("blocks", []):
        if block.get("type") != 0:
            continue

        for line in block.get("lines", []):
            text = line_text(line)
            bbox = line_bbox(line)

            if not text:
                continue

            if bbox.is_empty:
                continue

            lines.append(
                {
                    "text": text,
                    "bbox": bbox,
                    "y_pct": bbox.y0 / page.rect.height if page.rect.height else 0,
                }
            )

    lines.sort(key=lambda item: (item["bbox"].y0, item["bbox"].x0))
    return lines


def is_caption_continuation(text: str) -> bool:
    value = text.strip()

    if not value:
        return False

    if CAPTION_RE.match(value):
        return False

    lower = value.lower()

    if lower.startswith(("and ", "or ", "for ", "showing ", "continued ", "with ", "of ")):
        return True

    if len(value) <= 115 and not value.endswith(".") and re.match(r"^[a-z]", value):
        return True

    return False


def find_captions(page: fitz.Page) -> list[dict]:
    lines = get_text_lines(page)
    captions = []

    for index, item in enumerate(lines):
        text = item["text"]
        match = CAPTION_RE.match(text)

        if not match:
            continue

        number = match.group(1)
        caption = normalize_text(match.group(2))
        caption_lower = caption.lower()

        # Ignore inline references such as:
        # "Figure 1.6 shows the sequence..."
        if caption_lower.startswith(BAD_CAPTION_STARTS):
            continue

        # Long prose after "Figure X.Y" is usually an inline reference, not a real caption.
        if len(caption.split()) > 18:
            continue

        bbox = fitz.Rect(item["bbox"])

        for next_item in lines[index + 1:index + 3]:
            gap = next_item["bbox"].y0 - bbox.y1

            if gap < -3 or gap > 30:
                continue

            if is_caption_continuation(next_item["text"]):
                caption = normalize_text((caption + " " + next_item["text"]).strip())
                bbox |= next_item["bbox"]

        captions.append(
            {
                "number": number,
                "caption": caption.strip(" .,-"),
                "bbox": [bbox.x0, bbox.y0, bbox.x1, bbox.y1],
                "y_pct": bbox.y0 / page.rect.height if page.rect.height else 0,
            }
        )

    best: dict[str, dict] = {}

    for item in captions:
        number = item["number"]
        existing = best.get(number)

        if not existing:
            best[number] = item
            continue

        if len(item.get("caption", "")) > len(existing.get("caption", "")):
            best[number] = item

    return list(best.values())


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def crop_rect_from_caption(page: fitz.Page, caption: dict) -> fitz.Rect:
    page_rect = page.rect
    bbox = fitz.Rect(caption["bbox"])

    width = page_rect.width
    height = page_rect.height
    y_pct = float(caption.get("y_pct") or 0)

    x0 = width * 0.05
    x1 = width * 0.95

    # Most technical books place figure captions below drawings.
    # If caption is very high on page, assume caption may be above the drawing.
    if y_pct < 0.28:
        y0 = bbox.y0 - height * 0.035
        y1 = bbox.y1 + height * 0.58
    else:
        y0 = bbox.y0 - height * 0.34
        y1 = bbox.y1 + height * 0.075

    x0 = clamp(x0, 0, width)
    x1 = clamp(x1, 0, width)
    y0 = clamp(y0, 0, height)
    y1 = clamp(y1, 0, height)

    min_height = height * 0.22

    if y1 <= y0:
        y0 = clamp(bbox.y0 - height * 0.25, 0, height)
        y1 = clamp(bbox.y1 + height * 0.08, 0, height)

    if (y1 - y0) < min_height:
        center = (y0 + y1) / 2
        y0 = clamp(center - min_height / 2, 0, height)
        y1 = clamp(center + min_height / 2, 0, height)

    if x1 <= x0:
        x0 = 0
        x1 = width

    return fitz.Rect(x0, y0, x1, y1)


def render_crop(page: fitz.Page, clip: fitz.Rect, output_path: Path, zoom: float) -> None:
    pixmap = page.get_pixmap(
        matrix=fitz.Matrix(zoom, zoom),
        clip=clip,
        alpha=False,
    )
    pixmap.save(output_path)


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

    if not cards:
        cards.append(
            """
            <article class="card">
              <h2>No figures detected</h2>
              <p>No caption lines like Figure 1.1 or Fig. 2.3 were detected in this PDF.</p>
            </article>
            """
        )

    errors_html = ""

    if manifest.get("errors"):
        error_items = []

        for error in manifest["errors"][:30]:
            error_items.append(
                f"<li>Page {html.escape(str(error.get('pdf_page')))} / "
                f"{html.escape(str(error.get('number')))}: "
                f"{html.escape(str(error.get('error')))}</li>"
            )

        errors_html = f"""
        <section class="errors">
          <h2>Skipped crops</h2>
          <ul>{''.join(error_items)}</ul>
        </section>
        """

    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Voila! Auto Figures</title>
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
      --danger: #9f3a2f;
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

    .card,
    .errors {{
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

    .errors {{
      margin-top: 24px;
      color: var(--danger);
    }}
  </style>
</head>
<body>
  <main>
    <h1>Voila! Auto Figure Crops</h1>
    <p>Source: <code>{html.escape(manifest.get("source_file", ""))}</code></p>
    <p>Detected figures: {len(manifest.get("figure_crops", []))}</p>
    <div class="grid">
      {''.join(cards)}
    </div>
    {errors_html}
  </main>
</body>
</html>
"""

    output_path.write_text(doc, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! automatic figure detector and cropper")
    parser.add_argument("pdf", help="Path to source PDF")
    parser.add_argument("--zoom", type=float, default=3.0)
    parser.add_argument("--max-figures", type=int, default=80)
    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    output_root = Path("data/output").resolve() / pdf_path.stem
    figures_dir = output_root / "figures"
    crops_dir = figures_dir / "crops"

    figures_dir.mkdir(parents=True, exist_ok=True)
    crops_dir.mkdir(parents=True, exist_ok=True)

    for old_png in crops_dir.glob("figure_*.png"):
        old_png.unlink()

    doc = fitz.open(pdf_path)

    manifest = {
        "source_file": str(pdf_path),
        "method": "auto_caption_crop_safe_v1",
        "render_zoom": args.zoom,
        "max_figures": args.max_figures,
        "figure_crops": [],
        "errors": [],
    }

    total = 0

    for page_index, page in enumerate(doc, start=1):
        if total >= args.max_figures:
            break

        captions = find_captions(page)

        for caption in captions:
            if total >= args.max_figures:
                break

            number = caption["number"]

            try:
                clip = crop_rect_from_caption(page, caption)

                filename = f"figure_{safe_name(number)}_page_{page_index:03d}.png"
                crop_path = crops_dir / filename

                render_crop(page, clip, crop_path, args.zoom)

                manifest["figure_crops"].append(
                    {
                        "number": number,
                        "caption": caption.get("caption", ""),
                        "pdf_page": page_index,
                        "path": str(crop_path),
                        "relative_path": str(crop_path.relative_to(figures_dir)),
                        "caption_bbox": caption["bbox"],
                        "crop_rect": [clip.x0, clip.y0, clip.x1, clip.y1],
                    }
                )

                total += 1

            except Exception as exc:
                manifest["errors"].append(
                    {
                        "number": number,
                        "pdf_page": page_index,
                        "caption": caption.get("caption", ""),
                        "error": str(exc),
                    }
                )

    manifest_path = figures_dir / "figures_manifest.json"
    html_path = figures_dir / "figures.html"

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    build_gallery_html(manifest, html_path)

    print("Voila! automatic figures exported successfully.")
    print(f"Output: {figures_dir}")
    print(f"Figure crops: {len(manifest['figure_crops'])}")
    print(f"Errors: {len(manifest['errors'])}")
    print(f"- {manifest_path}")
    print(f"- {html_path}")


if __name__ == "__main__":
    main()
