from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

import fitz


def normalize_text(text: str) -> str:
    text = text.replace("Ftgure", "Figure")
    text = text.replace("Fig11re", "Figure")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def safe_name(value: str) -> str:
    value = value.lower().strip().replace(".", "_")
    value = re.sub(r"[^a-z0-9_-]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_")


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

            lines.append(
                {
                    "text": text,
                    "bbox": bbox,
                    "y_pct": bbox.y0 / page.rect.height,
                }
            )

    return lines


def find_anchor(page: fitz.Page, anchor: str, prefer_y: float) -> dict:
    anchor_norm = normalize_text(anchor).lower()
    lines = get_text_lines(page)

    candidates = []

    for item in lines:
        text_norm = item["text"].lower()

        starts_with_anchor = text_norm.startswith(anchor_norm)
        contains_anchor = anchor_norm in text_norm

        if starts_with_anchor or contains_anchor:
            score = abs(float(item["y_pct"]) - float(prefer_y))

            if starts_with_anchor:
                score -= 0.15

            candidates.append((score, item))

    if not candidates:
        available = "\n".join(item["text"] for item in lines[:80])
        raise RuntimeError(f"Anchor not found: {anchor}\nAvailable lines:\n{available}")

    candidates.sort(key=lambda pair: pair[0])
    return candidates[0][1]


def crop_from_anchor(page: fitz.Page, config: dict) -> fitz.Rect:
    anchor_item = find_anchor(
        page=page,
        anchor=str(config["anchor"]),
        prefer_y=float(config.get("prefer_y", 0.5)),
    )

    rect = page.rect
    anchor_box = anchor_item["bbox"]

    x0 = rect.width * float(config["x0_pct"])
    x1 = rect.width * float(config["x1_pct"])

    y0 = anchor_box.y0 - rect.height * float(config["top_from_anchor_pct"])
    y1 = anchor_box.y1 + rect.height * float(config["bottom_from_anchor_pct"])

    y0 = max(0, y0)
    y1 = min(rect.height, y1)

    return fitz.Rect(x0, y0, x1, y1)


def render_crop(page: fitz.Page, clip: fitz.Rect, output_path: Path, zoom: float) -> None:
    pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False)
    pixmap.save(output_path)


def build_gallery_html(manifest: dict, output_path: Path) -> None:
    cards = []

    for item in manifest["figure_crops"]:
        rel = Path(item["relative_path"]).as_posix()
        title = f"Figure {item['number']}"
        caption = item["caption"]

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
  <title>Voila! Anchored Figures</title>
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
    <h1>Voila! Anchored Figure Crops</h1>
    <p>Source: <code>{html.escape(manifest["source_file"])}</code></p>
    <p>Figures: {len(manifest["figure_crops"])}</p>
    <div class="grid">
      {''.join(cards)}
    </div>
  </main>
</body>
</html>
"""

    output_path.write_text(doc, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! figure exporter using text anchors")
    parser.add_argument("pdf", help="Path to source PDF")
    parser.add_argument("--crop-config", default="data/figure_crops.anchor.json")
    parser.add_argument("--zoom", type=float, default=4.0)

    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()
    crop_config_path = Path(args.crop_config).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if not crop_config_path.exists():
        raise FileNotFoundError(f"Crop config not found: {crop_config_path}")

    crop_config = json.loads(crop_config_path.read_text(encoding="utf-8"))

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
        "crop_config": str(crop_config_path),
        "render_zoom": args.zoom,
        "method": "text_anchor_offsets_v1",
        "figure_crops": [],
    }

    for item in crop_config["figures"]:
        number = str(item["number"])
        caption = str(item["caption"])
        pdf_page = int(item["pdf_page"])

        page = doc[pdf_page - 1]
        clip = crop_from_anchor(page, item)

        filename = f"figure_{safe_name(number)}_page_{pdf_page:03d}.png"
        output_path = crops_dir / filename

        render_crop(page, clip, output_path, args.zoom)

        manifest["figure_crops"].append(
            {
                "number": number,
                "caption": caption,
                "pdf_page": pdf_page,
                "path": str(output_path),
                "relative_path": str(output_path.relative_to(figures_dir)),
                "crop_rect": [clip.x0, clip.y0, clip.x1, clip.y1],
                "anchor": item["anchor"],
                "prefer_y": item.get("prefer_y"),
            }
        )

    manifest_path = figures_dir / "figures_manifest.json"
    gallery_path = figures_dir / "figures.html"

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    build_gallery_html(manifest, gallery_path)

    print("Voila! anchored figures exported successfully.")
    print(f"Output: {figures_dir}")
    print(f"Figure crops: {len(manifest['figure_crops'])}")
    print(f"- {manifest_path}")
    print(f"- {gallery_path}")


if __name__ == "__main__":
    main()
