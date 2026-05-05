from __future__ import annotations

import argparse
import html
import json
import math
import re
from pathlib import Path

import cv2
import fitz
import numpy as np
from PIL import Image


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

            if not text or bbox.is_empty:
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

        if caption_lower.startswith(BAD_CAPTION_STARTS):
            continue

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

    # Dedupe by figure number on same page.
    best: dict[str, dict] = {}

    for item in captions:
        number = item["number"]
        existing = best.get(number)

        if not existing:
            best[number] = item
            continue

        existing_caption = existing.get("caption", "")
        new_caption = item.get("caption", "")

        if len(new_caption) > len(existing_caption):
            best[number] = item

    return list(best.values())


def page_to_image(page: fitz.Page, zoom: float) -> Image.Image:
    pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    return Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)


def scale_rect(rect: fitz.Rect, zoom: float) -> tuple[int, int, int, int]:
    return (
        int(rect.x0 * zoom),
        int(rect.y0 * zoom),
        int(rect.x1 * zoom),
        int(rect.y1 * zoom),
    )


def build_text_mask(page: fitz.Page, image_shape: tuple[int, int], zoom: float, caption_rects: list[fitz.Rect]) -> np.ndarray:
    height, width = image_shape
    mask = np.zeros((height, width), dtype=np.uint8)

    # Important:
    # Caption text is also masked here, so OpenCV does not mistake the caption
    # itself for a graphic region. The caption is added back later in make_crop().
    for item in get_text_lines(page):
        bbox = fitz.Rect(item["bbox"])

        x0, y0, x1, y1 = scale_rect(bbox, zoom)

        pad_x = int(4 * zoom)
        pad_y = int(3 * zoom)

        x0 = max(0, x0 - pad_x)
        y0 = max(0, y0 - pad_y)
        x1 = min(width, x1 + pad_x)
        y1 = min(height, y1 + pad_y)

        cv2.rectangle(mask, (x0, y0), (x1, y1), 255, thickness=-1)

    return mask


def detect_graphic_candidates(page: fitz.Page, image: Image.Image, captions: list[dict], zoom: float) -> list[dict]:
    rgb = np.array(image)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    height, width = gray.shape
    page_area = width * height

    caption_rects = [fitz.Rect(caption["bbox"]) for caption in captions]
    text_mask = build_text_mask(page, gray.shape, zoom, caption_rects)

    # Ink mask: dark content on the page.
    _, ink = cv2.threshold(gray, 235, 255, cv2.THRESH_BINARY_INV)

    # Remove most OCR/text areas so text paragraphs do not become figure candidates.
    ink_without_text = cv2.bitwise_and(ink, cv2.bitwise_not(text_mask))

    # Join drawing strokes into larger regions.
    k = max(11, int(min(width, height) * 0.018))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    joined = cv2.dilate(ink_without_text, kernel, iterations=2)

    contours, _ = cv2.findContours(joined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h

        if area < page_area * 0.004:
            continue

        if w < width * 0.10:
            continue

        if h < height * 0.045:
            continue

        if w > width * 0.98 and h > height * 0.98:
            continue

        crop_text_mask = text_mask[y:y + h, x:x + w]
        text_overlap = float(np.count_nonzero(crop_text_mask)) / float(max(1, area))

        # Large text-only blocks have high OCR/text overlap.
        if text_overlap > 0.30:
            continue

        candidates.append(
            {
                "bbox": (x, y, x + w, y + h),
                "area": area,
                "text_overlap": text_overlap,
                "center": (x + w / 2, y + h / 2),
            }
        )

    candidates.sort(key=lambda item: item["area"], reverse=True)
    return candidates


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def choose_candidate_for_caption(caption: dict, candidates: list[dict], page: fitz.Page, zoom: float, image_size: tuple[int, int]) -> dict | None:
    if not candidates:
        return None

    width, height = image_size
    cap = fitz.Rect(caption["bbox"])

    cap_x0, cap_y0, cap_x1, cap_y1 = scale_rect(cap, zoom)
    cap_center = ((cap_x0 + cap_x1) / 2, (cap_y0 + cap_y1) / 2)
    cap_y_pct = cap_y0 / max(1, height)

    scored = []

    for candidate in candidates:
        x0, y0, x1, y1 = candidate["bbox"]
        cx, cy = candidate["center"]

        is_above = y1 <= cap_y1 + height * 0.03
        is_below = y0 >= cap_y0 - height * 0.03

        d = distance((cx, cy), cap_center)

        direction_penalty = 0

        # Most captions are below figures.
        if cap_y_pct > 0.25 and not is_above:
            direction_penalty += height * 0.35

        # If caption is at top of page, figure is likely below.
        if cap_y_pct <= 0.25 and not is_below:
            direction_penalty += height * 0.35

        area_bonus = min(candidate["area"] / (width * height), 0.25) * height * 0.15

        score = d + direction_penalty - area_bonus

        scored.append((score, candidate))

    scored.sort(key=lambda pair: pair[0])
    return scored[0][1]


def fallback_crop_rect(page: fitz.Page, caption: dict, zoom: float, image_size: tuple[int, int]) -> tuple[int, int, int, int]:
    width, height = image_size
    bbox = fitz.Rect(caption["bbox"])

    cap_x0, cap_y0, cap_x1, cap_y1 = scale_rect(bbox, zoom)
    cap_y_pct = cap_y0 / max(1, height)

    x0 = int(width * 0.05)
    x1 = int(width * 0.95)

    if cap_y_pct < 0.25:
        y0 = max(0, cap_y0 - int(height * 0.04))
        y1 = min(height, cap_y1 + int(height * 0.58))
    else:
        y0 = max(0, cap_y0 - int(height * 0.36))
        y1 = min(height, cap_y1 + int(height * 0.09))

    return x0, y0, x1, y1


def make_crop(image: Image.Image, page: fitz.Page, caption: dict, candidate: dict | None, zoom: float) -> tuple[Image.Image, tuple[int, int, int, int], str]:
    width, height = image.size
    cap = fitz.Rect(caption["bbox"])
    cap_x0, cap_y0, cap_x1, cap_y1 = scale_rect(cap, zoom)

    margin = int(24 * zoom)

    if candidate:
        x0, y0, x1, y1 = candidate["bbox"]
        method = "vision_candidate"

        # Include caption too.
        x0 = min(x0, cap_x0)
        y0 = min(y0, cap_y0)
        x1 = max(x1, cap_x1)
        y1 = max(y1, cap_y1)
    else:
        x0, y0, x1, y1 = fallback_crop_rect(page, caption, zoom, image.size)
        method = "fallback_caption_window"

    x0 = max(0, x0 - margin)
    y0 = max(0, y0 - margin)
    x1 = min(width, x1 + margin)
    y1 = min(height, y1 + margin)

    if x1 <= x0 or y1 <= y0:
        x0, y0, x1, y1 = fallback_crop_rect(page, caption, zoom, image.size)
        method = "fallback_after_invalid_rect"

    crop = image.crop((x0, y0, x1, y1))
    return crop, (x0, y0, x1, y1), method


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
              <p class="meta">PDF page {item['pdf_page']} · {html.escape(item.get('crop_method', ''))}</p>
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

    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Voila! Vision Figures</title>
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
    <h1>Voila! Vision Figure Crops</h1>
    <p>Source: <code>{html.escape(manifest.get("source_file", ""))}</code></p>
    <p>Detected figures: {len(manifest.get("figure_crops", []))}</p>
    <div class="grid">
      {''.join(cards)}
    </div>
  </main>
</body>
</html>
"""

    output_path.write_text(doc, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! advanced vision-based figure detector")
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
        "method": "vision_graphic_region_association_v1",
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

        if not captions:
            continue

        image = page_to_image(page, args.zoom)
        candidates = detect_graphic_candidates(page, image, captions, args.zoom)

        for caption in captions:
            if total >= args.max_figures:
                break

            number = caption["number"]

            try:
                candidate = choose_candidate_for_caption(
                    caption=caption,
                    candidates=candidates,
                    page=page,
                    zoom=args.zoom,
                    image_size=image.size,
                )

                crop, crop_rect, method = make_crop(
                    image=image,
                    page=page,
                    caption=caption,
                    candidate=candidate,
                    zoom=args.zoom,
                )

                filename = f"figure_{safe_name(number)}_page_{page_index:03d}_{total + 1:03d}.png"
                crop_path = crops_dir / filename
                crop.save(crop_path)

                manifest["figure_crops"].append(
                    {
                        "number": number,
                        "caption": caption.get("caption", ""),
                        "pdf_page": page_index,
                        "path": str(crop_path),
                        "relative_path": str(crop_path.relative_to(figures_dir)),
                        "caption_bbox": caption["bbox"],
                        "crop_rect_px": list(crop_rect),
                        "crop_method": method,
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

    print("Voila! vision figures exported successfully.")
    print(f"Output: {figures_dir}")
    print(f"Figure crops: {len(manifest['figure_crops'])}")
    print(f"Errors: {len(manifest['errors'])}")
    print(f"- {manifest_path}")
    print(f"- {html_path}")


if __name__ == "__main__":
    main()
