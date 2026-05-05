from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem


def safe_name(value: str) -> str:
    value = value.lower().strip()
    value = value.replace(".", "_").replace("-", "_")
    value = re.sub(r"[^a-z0-9_-]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_") or "item"


def get_caption(element, document) -> str:
    try:
        value = element.caption_text(doc=document)
        return str(value or "").strip()
    except Exception:
        return ""


def get_page_no(element) -> str:
    try:
        prov = getattr(element, "prov", None) or []
        if prov:
            return str(getattr(prov[0], "page_no", ""))
    except Exception:
        pass

    return ""


def get_bbox(element) -> list | None:
    try:
        prov = getattr(element, "prov", None) or []
        if not prov:
            return None

        bbox = getattr(prov[0], "bbox", None)
        if not bbox:
            return None

        return [
            float(getattr(bbox, "l", 0)),
            float(getattr(bbox, "t", 0)),
            float(getattr(bbox, "r", 0)),
            float(getattr(bbox, "b", 0)),
        ]
    except Exception:
        return None


def build_gallery_html(manifest: dict, output_path: Path) -> None:
    cards = []

    for item in manifest.get("items", []):
        rel = Path(item["relative_path"]).as_posix()
        kind = item.get("kind", "picture")
        number = item.get("index")
        title = f"{kind.title()} {number}"
        caption = item.get("caption") or ""
        page = item.get("pdf_page") or "?"

        cards.append(
            f"""
            <article class="card">
              <h2>{html.escape(title)}</h2>
              <p>{html.escape(caption)}</p>
              <p class="meta">PDF page {html.escape(str(page))}</p>
              <img src="{html.escape(rel)}" alt="{html.escape(title + ' ' + caption)}">
            </article>
            """
        )

    if not cards:
        cards.append(
            """
            <article class="card">
              <h2>No Docling pictures detected</h2>
              <p>Docling did not return picture/table image elements for this PDF.</p>
            </article>
            """
        )

    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Voila! Docling Figures</title>
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
    <h1>Voila! Docling Figure Extraction</h1>
    <p>Source: <code>{html.escape(manifest.get("source_file", ""))}</code></p>
    <p>Detected items: {len(manifest.get("items", []))}</p>
    <div class="grid">
      {''.join(cards)}
    </div>
  </main>
</body>
</html>
"""

    output_path.write_text(doc, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! Docling figure extractor")
    parser.add_argument("pdf", help="Path to source PDF")
    parser.add_argument("--scale", type=float, default=2.0)
    parser.add_argument("--max-items", type=int, default=120)

    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    output_root = Path("data/output").resolve() / pdf_path.stem
    figures_dir = output_root / "figures_docling"
    crops_dir = figures_dir / "crops"

    figures_dir.mkdir(parents=True, exist_ok=True)
    crops_dir.mkdir(parents=True, exist_ok=True)

    for old in crops_dir.glob("*.png"):
        old.unlink()

    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = args.scale
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    result = converter.convert(pdf_path)
    document = result.document

    manifest = {
        "source_file": str(pdf_path),
        "method": "docling_picture_table_export",
        "scale": args.scale,
        "items": [],
        "errors": [],
    }

    picture_count = 0
    table_count = 0
    total = 0

    for element, _level in document.iterate_items():
        if total >= args.max_items:
            break

        kind = None
        index = None

        if isinstance(element, PictureItem):
            picture_count += 1
            kind = "picture"
            index = picture_count

        elif isinstance(element, TableItem):
            table_count += 1
            kind = "table"
            index = table_count

        if kind is None:
            continue

        try:
            image = element.get_image(document)

            filename = f"{kind}_{index:03d}_page_{safe_name(get_page_no(element) or 'unknown')}.png"
            output_path = crops_dir / filename
            image.save(output_path, "PNG")

            manifest["items"].append(
                {
                    "kind": kind,
                    "index": index,
                    "caption": get_caption(element, document),
                    "pdf_page": get_page_no(element),
                    "bbox": get_bbox(element),
                    "path": str(output_path),
                    "relative_path": str(output_path.relative_to(figures_dir)),
                }
            )

            total += 1

        except Exception as exc:
            manifest["errors"].append(
                {
                    "kind": kind,
                    "index": index,
                    "pdf_page": get_page_no(element),
                    "caption": get_caption(element, document),
                    "error": str(exc),
                }
            )

    manifest_path = figures_dir / "figures_manifest.docling.json"
    gallery_path = figures_dir / "figures_docling.html"

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    build_gallery_html(manifest, gallery_path)

    try:
        document.save_as_markdown(
            figures_dir / "docling_with_image_refs.md",
            image_mode=ImageRefMode.REFERENCED,
        )
        document.save_as_html(
            figures_dir / "docling_with_image_refs.html",
            image_mode=ImageRefMode.REFERENCED,
        )
    except Exception as exc:
        manifest["errors"].append(
            {
                "kind": "export",
                "error": str(exc),
            }
        )

    print("Voila! Docling figures exported.")
    print(f"Output: {figures_dir}")
    print(f"Items: {len(manifest['items'])}")
    print(f"Errors: {len(manifest['errors'])}")
    print(f"- {manifest_path}")
    print(f"- {gallery_path}")


if __name__ == "__main__":
    main()
