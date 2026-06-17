from __future__ import annotations

import argparse
import html
import json
import math
import re
from pathlib import Path
from urllib.parse import quote

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


def clean_caption(caption: str) -> str:
    caption = normalize_text(caption).strip(" .,-")

    # Some PDFs merge the real caption with the next paragraph.
    # These markers usually indicate that body text started after the caption.
    cut_markers = [
        " With a ",
        " With an ",
        " With the ",
        " This ",
        " These ",
        " In this ",
        " difficult to calculate ",
    ]

    for marker in cut_markers:
        if marker in caption and len(caption.split()) > 12:
            caption = caption.split(marker, 1)[0].strip(" .,-")
            break

    return caption


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

        if len(caption.split()) > 24:
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
                "caption": clean_caption(caption),
                "bbox": [bbox.x0, bbox.y0, bbox.x1, bbox.y1],
                "y_pct": bbox.y0 / page.rect.height if page.rect.height else 0,
            }
        )

    return captions


def rect_area(rect: fitz.Rect) -> float:
    return max(0.0, rect.width) * max(0.0, rect.height)


def expanded(rect: fitz.Rect, x: float, y: float) -> fitz.Rect:
    return fitz.Rect(rect.x0 - x, rect.y0 - y, rect.x1 + x, rect.y1 + y)


def valid_candidate_rect(page: fitz.Page, rect: fitz.Rect) -> bool:
    if rect.is_empty:
        return False

    page_area = page.rect.width * page.rect.height
    area = rect_area(rect)

    if area < page_area * 0.0012:
        return False

    if rect.width < page.rect.width * 0.06:
        return False

    if rect.height < page.rect.height * 0.025:
        return False

    if rect.width > page.rect.width * 0.98 and rect.height > page.rect.height * 0.98:
        return False

    return True


def cluster_rects(page: fitz.Page, rects: list[fitz.Rect]) -> list[fitz.Rect]:
    gap_x = page.rect.width * 0.025
    gap_y = page.rect.height * 0.025

    clusters: list[fitz.Rect] = []

    for rect in rects:
        if rect.is_empty:
            continue

        placed = False

        for idx, cluster in enumerate(clusters):
            if expanded(cluster, gap_x, gap_y).intersects(expanded(rect, gap_x, gap_y)):
                clusters[idx] = cluster | rect
                placed = True
                break

        if not placed:
            clusters.append(fitz.Rect(rect))

    changed = True

    while changed:
        changed = False
        merged: list[fitz.Rect] = []

        while clusters:
            base = clusters.pop(0)
            again = []

            for other in clusters:
                if expanded(base, gap_x, gap_y).intersects(expanded(other, gap_x, gap_y)):
                    base |= other
                    changed = True
                else:
                    again.append(other)

            clusters = again
            merged.append(base)

        clusters = merged

    return [rect for rect in clusters if valid_candidate_rect(page, rect)]


def get_embedded_image_candidates(page: fitz.Page) -> list[dict]:
    candidates = []

    for image_info in page.get_images(full=True):
        xref = image_info[0]

        try:
            rects = page.get_image_rects(xref)
        except Exception:
            continue

        for rect in rects:
            if valid_candidate_rect(page, rect):
                candidates.append(
                    {
                        "kind": "embedded_image",
                        "rect": rect,
                        "area": rect_area(rect),
                    }
                )

    return candidates


def get_vector_candidates(page: fitz.Page) -> list[dict]:
    rects = []

    for drawing in page.get_drawings():
        rect = drawing.get("rect")

        if not rect:
            continue

        rect = fitz.Rect(rect)

        if rect.is_empty:
            continue

        rects.append(rect)

    clusters = cluster_rects(page, rects)

    return [
        {
            "kind": "vector_drawing",
            "rect": rect,
            "area": rect_area(rect),
        }
        for rect in clusters
    ]


def get_all_candidates(page: fitz.Page) -> list[dict]:
    candidates = []
    candidates.extend(get_embedded_image_candidates(page))
    candidates.extend(get_vector_candidates(page))

    candidates.sort(key=lambda item: item["area"], reverse=True)

    return candidates


def center(rect: fitz.Rect) -> tuple[float, float]:
    return ((rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2)


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)



def horizontal_overlap_ratio(a: fitz.Rect, b: fitz.Rect) -> float:
    overlap = min(a.x1, b.x1) - max(a.x0, b.x0)

    if overlap <= 0:
        return 0.0

    return overlap / max(1.0, min(a.width, b.width))


def merge_related_vector_candidates(page: fitz.Page, caption: dict, chosen: dict, candidates: list[dict]) -> dict:
    if chosen["kind"] != "vector_drawing":
        return chosen

    cap = fitz.Rect(caption["bbox"])
    cap_y_pct = cap.y0 / page.rect.height if page.rect.height else 0

    merged = fitz.Rect(chosen["rect"])

    for candidate in candidates:
        if candidate is chosen:
            continue

        if candidate["kind"] != "vector_drawing":
            continue

        rect = fitz.Rect(candidate["rect"])

        # Caption usually below the drawing.
        if cap_y_pct > 0.25:
            if rect.y0 > cap.y1 + page.rect.height * 0.06:
                continue

            if rect.y1 < cap.y0 - page.rect.height * 0.62:
                continue

        # Caption near top: drawing likely below it.
        else:
            if rect.y1 < cap.y0 - page.rect.height * 0.06:
                continue

            if rect.y0 > cap.y1 + page.rect.height * 0.68:
                continue

        overlap_with_merged = horizontal_overlap_ratio(rect, merged)
        overlap_with_caption = horizontal_overlap_ratio(rect, cap)
        center_distance_x = abs(center(rect)[0] - center(cap)[0])

        close_enough_x = center_distance_x < page.rect.width * 0.48

        if overlap_with_merged > 0.08 or overlap_with_caption > 0.08 or close_enough_x:
            merged |= rect

    updated = dict(chosen)
    updated["rect"] = merged
    updated["kind"] = "vector_drawing_merged"

    return updated


def choose_candidate(page: fitz.Page, caption: dict, candidates: list[dict]) -> dict | None:
    if not candidates:
        return None

    cap = fitz.Rect(caption["bbox"])
    cap_center = center(cap)
    cap_y_pct = cap.y0 / page.rect.height if page.rect.height else 0

    scored = []

    for candidate in candidates:
        rect = candidate["rect"]

        above_caption = rect.y1 <= cap.y1 + page.rect.height * 0.04
        below_caption = rect.y0 >= cap.y0 - page.rect.height * 0.04

        overlap = horizontal_overlap_ratio(rect, cap)
        d = distance(center(rect), cap_center)

        direction_penalty = 0.0

        if cap_y_pct > 0.25 and not above_caption:
            direction_penalty += page.rect.height * 0.38

        if cap_y_pct <= 0.25 and not below_caption:
            direction_penalty += page.rect.height * 0.38

        overlap_bonus = page.rect.height * 0.12 if overlap > 0 else 0.0

        kind_bonus = 0.0
        if candidate["kind"] == "embedded_image":
            kind_bonus = page.rect.height * 0.07

        area_bonus = min(candidate["area"] / (page.rect.width * page.rect.height), 0.30) * page.rect.height * 0.13

        score = d + direction_penalty - overlap_bonus - kind_bonus - area_bonus

        scored.append((score, candidate))

    scored.sort(key=lambda pair: pair[0])

    chosen = scored[0][1]
    chosen = merge_related_vector_candidates(page, caption, chosen, candidates)

    return chosen



def fallback_rect(page: fitz.Page, caption: dict) -> fitz.Rect:
    cap = fitz.Rect(caption["bbox"])
    y_pct = cap.y0 / page.rect.height if page.rect.height else 0

    x0 = page.rect.width * 0.05
    x1 = page.rect.width * 0.95

    if y_pct < 0.25:
        y0 = cap.y0 - page.rect.height * 0.04
        y1 = cap.y1 + page.rect.height * 0.56
    else:
        y0 = cap.y0 - page.rect.height * 0.36
        y1 = cap.y1 + page.rect.height * 0.10

    return fitz.Rect(
        max(0, x0),
        max(0, y0),
        min(page.rect.width, x1),
        min(page.rect.height, y1),
    )


def make_crop_rect(page: fitz.Page, caption: dict, candidate: dict | None) -> tuple[fitz.Rect, str]:
    cap = fitz.Rect(caption["bbox"])

    # Wider horizontal margin helps embedded diagrams that are close to the page edge.
    margin_x = page.rect.width * 0.045

    # Asymmetric vertical margins:
    # - enough top margin for labels above the drawing
    # - small bottom margin to avoid pulling the paragraph after the caption
    cap_y_pct = cap.y0 / page.rect.height if page.rect.height else 0

    margin_top = page.rect.height * 0.030

    if cap_y_pct < 0.25:
        # Caption near top, figure likely below.
        margin_bottom = page.rect.height * 0.030
    else:
        # Caption below figure; avoid grabbing following paragraph.
        margin_bottom = page.rect.height * 0.010

    if candidate:
        rect = fitz.Rect(candidate["rect"])
        rect |= cap
        method = candidate["kind"]
    else:
        rect = fallback_rect(page, caption)
        method = "fallback_caption_window"

    rect = fitz.Rect(
        max(0, rect.x0 - margin_x),
        max(0, rect.y0 - margin_top),
        min(page.rect.width, rect.x1 + margin_x),
        min(page.rect.height, rect.y1 + margin_bottom),
    )

    if rect.is_empty:
        rect = fallback_rect(page, caption)
        method = "fallback_after_invalid_rect"

    return rect, method


def render_crop(page: fitz.Page, clip: fitz.Rect, output_path: Path, zoom: float) -> None:
    pixmap = page.get_pixmap(
        matrix=fitz.Matrix(zoom, zoom),
        clip=clip,
        alpha=False,
    )
    pixmap.save(output_path)


def build_gallery_html(manifest: dict, output_path: Path) -> None:
    cards = []
    all_items = manifest.get("figure_crops", [])
    visible_items = [
        item for item in all_items
        if str(item.get("status", "accepted")).strip().lower() != "rejected"
    ]
    rejected_count = len(all_items) - len(visible_items)

    for item in visible_items:
        rel = Path(item["relative_path"]).as_posix()
        title = f"Figure {item['number']}"
        caption = item.get("caption") or ""
        method = item.get("crop_method", "")

        cards.append(
            f"""
            <article class="card">
              <h2>{html.escape(title)}</h2>
              <p>{html.escape(caption)}</p>
              <p class="meta">PDF page {item['pdf_page']} · {html.escape(method)}</p>
              <img src="{html.escape(rel)}" alt="{html.escape(title + ' ' + caption)}">
            </article>
            """
        )

    if not cards:
        cards.append(
            """
            <article class="card">
              <h2>No accepted figures</h2>
              <p>No accepted figures are available. Rejected false figures are hidden from this gallery.</p>
            </article>
            """
        )

    rejected_note = (
        f"<p>Rejected false figures hidden: {rejected_count}</p>"
        if rejected_count
        else ""
    )

    pdf_name = Path(str(manifest.get("source_file", ""))).name
    pdf_query = quote(pdf_name)
    toolbar_style = "display:flex;flex-wrap:wrap;gap:12px;margin:22px 0 26px;"
    btn_style = "display:inline-flex;align-items:center;justify-content:center;border:1px solid #d7c5a8;border-radius:999px;padding:10px 16px;color:#2f2a24;text-decoration:none;background:rgba(255,255,255,0.34);font-weight:700;"
    primary_btn_style = btn_style + "background:#8a5a32;color:#fff7ea;border-color:#8a5a32;"
    toolbar = (
        f'<div class="toolbar" style="{toolbar_style}">'
        f'<a class="btn primary" style="{primary_btn_style}" href="http://127.0.0.1:8787/edit-crops?pdf={pdf_query}">Back to Crop Editor</a>'
        f'<a class="btn" style="{btn_style}" href="http://127.0.0.1:8787">Back to Voila!</a>'
        f'</div>'
        if pdf_name
        else f'<div class="toolbar" style="{toolbar_style}"><a class="btn" style="{btn_style}" href="http://127.0.0.1:8787">Back to Voila!</a></div>'
    )

    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Voila! Hybrid Figures</title>
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
    <h1>Voila! Hybrid Figure Extraction</h1>
    <p>Source: <code>{html.escape(manifest.get("source_file", ""))}</code></p>
    <p>Page range: {manifest.get("page_from")}–{manifest.get("page_to")}</p>
    <p>Detected figures: {len(visible_items)}</p>
    {rejected_note}
    {toolbar}
    <div class="grid">
      {''.join(cards)}
    </div>
  </main>
</body>
</html>
"""

    output_path.write_text(doc, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! hybrid PDF figure extractor")
    parser.add_argument("pdf", help="Path to source PDF")
    parser.add_argument("--page-from", type=int, default=1)
    parser.add_argument("--page-to", type=int, default=99999)
    parser.add_argument("--zoom", type=float, default=3.0)
    parser.add_argument("--max-figures", type=int, default=120)

    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    output_root = Path("data/output").resolve() / pdf_path.stem
    figures_dir = output_root / "figures_hybrid"
    crops_dir = figures_dir / "crops"

    figures_dir.mkdir(parents=True, exist_ok=True)
    crops_dir.mkdir(parents=True, exist_ok=True)

    # Keep existing crops.
    # Important: partial runs must not delete previously generated figures.
    # Missing/invalid images can be repaired with repair_hybrid_figures.py.

    doc = fitz.open(pdf_path)

    page_from = max(1, args.page_from)
    page_to = min(doc.page_count, args.page_to)

    manifest = {
        "source_file": str(pdf_path),
        "method": "hybrid_embedded_image_plus_vector_bbox_v1",
        "page_from": page_from,
        "page_to": page_to,
        "render_zoom": args.zoom,
        "max_figures": args.max_figures,
        "figure_crops": [],
        "errors": [],
    }

    total = 0

    for page_index in range(page_from, page_to + 1):
        if total >= args.max_figures:
            break

        page = doc[page_index - 1]
        captions = find_captions(page)

        if not captions:
            continue

        candidates = get_all_candidates(page)

        for caption in captions:
            if total >= args.max_figures:
                break

            try:
                chosen = choose_candidate(page, caption, candidates)
                clip, method = make_crop_rect(page, caption, chosen)

                filename = (
                    f"figure_{safe_name(caption['number'])}_"
                    f"page_{page_index:03d}_{total + 1:03d}.png"
                )
                output_path = crops_dir / filename

                render_crop(page, clip, output_path, args.zoom)

                manifest["figure_crops"].append(
                    {
                        "number": caption["number"],
                        "caption": caption.get("caption", ""),
                        "pdf_page": page_index,
                        "path": str(output_path),
                        "relative_path": str(output_path.relative_to(figures_dir)),
                        "caption_bbox": caption["bbox"],
                        "crop_rect": [clip.x0, clip.y0, clip.x1, clip.y1],
                        "crop_method": method,
                    }
                )

                total += 1

            except Exception as exc:
                manifest["errors"].append(
                    {
                        "number": caption.get("number"),
                        "caption": caption.get("caption"),
                        "pdf_page": page_index,
                        "error": str(exc),
                    }
                )

    manifest_path = figures_dir / "figures_manifest.hybrid.json"
    gallery_path = figures_dir / "figures_hybrid.html"

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    build_gallery_html(manifest, gallery_path)

    print("Voila! hybrid figures exported successfully.")
    print(f"Output: {figures_dir}")
    print(f"Figure crops: {len(manifest['figure_crops'])}")
    print(f"Errors: {len(manifest['errors'])}")
    print(f"- {manifest_path}")
    print(f"- {gallery_path}")


if __name__ == "__main__":
    main()
