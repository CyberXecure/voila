from __future__ import annotations

import argparse
import json
from pathlib import Path

import fitz


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! PDF image diagnostics")
    parser.add_argument("pdf", help="Path to PDF")

    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)

    report = {
        "source_file": str(pdf_path),
        "page_count": doc.page_count,
        "pages": [],
        "total_embedded_images": 0,
        "total_drawings": 0,
    }

    for page_index, page in enumerate(doc, start=1):
        images = page.get_images(full=True)
        drawings = page.get_drawings()

        image_items = []

        for image in images:
            xref = image[0]
            width = image[2]
            height = image[3]
            bpc = image[4]
            colorspace = image[5]

            image_items.append(
                {
                    "xref": xref,
                    "width": width,
                    "height": height,
                    "bpc": bpc,
                    "colorspace": colorspace,
                }
            )

        page_info = {
            "pdf_page": page_index,
            "embedded_images": len(images),
            "drawings": len(drawings),
            "image_items": image_items[:10],
        }

        report["pages"].append(page_info)
        report["total_embedded_images"] += len(images)
        report["total_drawings"] += len(drawings)

    output_dir = Path("data/output").resolve() / pdf_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "pdf_image_diagnostics.json"

    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Voila! PDF image diagnostics complete.")
    print(f"PDF pages: {report['page_count']}")
    print(f"Total embedded images: {report['total_embedded_images']}")
    print(f"Total vector drawings: {report['total_drawings']}")
    print(f"- {report_path}")

    print("")
    print("Pages with embedded images or drawings:")
    for page in report["pages"]:
        if page["embedded_images"] or page["drawings"]:
            print(
                f"Page {page['pdf_page']}: "
                f"images={page['embedded_images']}, "
                f"drawings={page['drawings']}"
            )


if __name__ == "__main__":
    main()
