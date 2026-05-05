from __future__ import annotations

import argparse
import html
import json
import re
import tempfile
from pathlib import Path

import fitz
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import PictureItem, TableItem


def safe_name(value: str) -> str:
    value = value.lower().strip()
    value = value.replace(".", "_").replace("-", "_")
    value = re.sub(r"[^a-z0-9_-]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_") or "item"


def safe_set_option(obj, name: str, value) -> None:
    try:
        setattr(obj, name, value)
    except Exception:
        pass


def make_pdf_slice(source_pdf: Path, page_from: int, page_to: int, output_pdf: Path) -> int:
    source = fitz.open(source_pdf)

    total_pages = source.page_count
    page_from = max(1, page_from)
    page_to = min(total_pages, page_to)

    if page_from > page_to:
        raise ValueError(f"Invalid page range: {page_from}-{page_to}")

    sliced = fitz.open()
    sliced.insert_pdf(source, from_page=page_from - 1, to_page=page_to - 1)
    sliced.save(output_pdf)

    source.close()
    sliced.close()

    return page_from - 1


def get_caption(element, document) -> str:
    try:
        value = element.caption_text(doc=document)
        return str(value or "").strip()
    except Exception:
        return ""


def get_page_no(element, page_offset: int = 0) -> str:
    try:
        prov = getattr(element, "prov", None) or []

        if prov:
            page_no = getattr(prov[0], "page_no", "")

            if page_no:
                return str(int(page_no) + page_offset)
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
        index = item.get("index")
        title = f"{kind.title()} {index}"
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
              <h2>No items extracted</h2>
              <p>Docling Lite did not extract picture/table image elements for this page range.</p>
            </article>
            """
        )

    error_html = ""

    if manifest.get("errors"):
        rows = []

        for error in manifest["errors"][:40]:
            rows.append(
                f"<li>{html.escape(str(error.get('kind')))} "
                f"{html.escape(str(error.get('index')))} / page "
                f"{html.escape(str(error.get('pdf_page')))}: "
                f"{html.escape(str(error.get('error')))}</li>"
            )

        error_html = f"""
        <section class="errors">
          <h2>Errors / skipped items</h2>
          <ul>{''.join(rows)}</ul>
        </section>
        """

    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Voila! Docling Lite Figures</title>
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
    <h1>Voila! Docling Lite Figure Extraction</h1>
    <p>Source: <code>{html.escape(manifest.get("source_file", ""))}</code></p>
    <p>Page range: {html.escape(str(manifest.get("page_from")))}–{html.escape(str(manifest.get("page_to")))}</p>
    <p>Detected items: {len(manifest.get("items", []))}</p>
    <div class="grid">
      {''.join(cards)}
    </div>
    {error_html}
  </main>
</body>
</html>
"""

    output_path.write_text(doc, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! Docling Lite figure extractor")
    parser.add_argument("pdf", help="Path to source PDF")
    parser.add_argument("--page-from", type=int, default=1)
    parser.add_argument("--page-to", type=int, default=80)
    parser.add_argument("--scale", type=float, default=1.2)
    parser.add_argument("--max-items", type=int, default=120)

    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    output_root = Path("data/output").resolve() / pdf_path.stem
    figures_dir = output_root / "figures_docling_lite"
    crops_dir = figures_dir / "crops"

    figures_dir.mkdir(parents=True, exist_ok=True)
    crops_dir.mkdir(parents=True, exist_ok=True)

    for old in crops_dir.glob("*.png"):
        old.unlink()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_pdf = Path(tmp) / "slice.pdf"
        page_offset = make_pdf_slice(
            source_pdf=pdf_path,
            page_from=args.page_from,
            page_to=args.page_to,
            output_pdf=tmp_pdf,
        )

        pipeline_options = PdfPipelineOptions()

        safe_set_option(pipeline_options, "do_ocr", False)
        safe_set_option(pipeline_options, "do_table_structure", False)
        safe_set_option(pipeline_options, "images_scale", args.scale)
        safe_set_option(pipeline_options, "generate_page_images", False)
        safe_set_option(pipeline_options, "generate_picture_images", True)

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

        result = converter.convert(tmp_pdf)
        document = result.document

        manifest = {
            "source_file": str(pdf_path),
            "method": "docling_lite_no_ocr_page_slice",
            "page_from": args.page_from,
            "page_to": args.page_to,
            "scale": args.scale,
            "max_items": args.max_items,
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

                if image is None:
                    raise RuntimeError("No image returned by Docling for this item.")

                pdf_page = get_page_no(element, page_offset)

                filename = f"{kind}_{index:03d}_page_{safe_name(pdf_page or 'unknown')}.png"
                output_path = crops_dir / filename
                image.save(output_path, "PNG")

                manifest["items"].append(
                    {
                        "kind": kind,
                        "index": index,
                        "caption": get_caption(element, document),
                        "pdf_page": pdf_page,
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
                        "pdf_page": get_page_no(element, page_offset),
                        "caption": get_caption(element, document),
                        "error": str(exc),
                    }
                )

    manifest_path = figures_dir / "figures_manifest.docling_lite.json"
    gallery_path = figures_dir / "figures_docling_lite.html"

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    build_gallery_html(manifest, gallery_path)

    print("Voila! Docling Lite figures exported.")
    print(f"Output: {figures_dir}")
    print(f"Items: {len(manifest['items'])}")
    print(f"Errors: {len(manifest['errors'])}")
    print(f"- {manifest_path}")
    print(f"- {gallery_path}")


if __name__ == "__main__":
    main()
