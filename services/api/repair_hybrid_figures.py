from __future__ import annotations

import argparse
import json
from pathlib import Path

import fitz


def rerender_missing(pdf_path: Path, manifest_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    figures_dir = manifest_path.parent
    zoom = float(manifest.get("render_zoom") or 3.0)

    doc = fitz.open(pdf_path)

    repaired = 0
    skipped = 0
    already_ok = 0

    for item in manifest.get("figure_crops", []):
        rel = item.get("relative_path")
        rect = item.get("crop_rect")
        page_no = int(item.get("pdf_page") or 0)

        if not rel or not rect or page_no < 1:
            skipped += 1
            continue

        out_path = figures_dir / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if out_path.exists() and out_path.stat().st_size >= 1000:
            already_ok += 1
            continue

        page = doc[page_no - 1]
        clip = fitz.Rect(rect)

        clip = fitz.Rect(
            max(0, clip.x0),
            max(0, clip.y0),
            min(page.rect.width, clip.x1),
            min(page.rect.height, clip.y1),
        )

        if clip.is_empty:
            skipped += 1
            continue

        pixmap = page.get_pixmap(
            matrix=fitz.Matrix(zoom, zoom),
            clip=clip,
            alpha=False,
        )

        pixmap.save(out_path)
        repaired += 1

    doc.close()

    print("Voila! hybrid figure repair complete.")
    print(f"Already OK: {already_ok}")
    print(f"Repaired: {repaired}")
    print(f"Skipped: {skipped}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair missing Voila hybrid figure PNG files")
    parser.add_argument("pdf")
    parser.add_argument("manifest")

    args = parser.parse_args()

    rerender_missing(
        pdf_path=Path(args.pdf).resolve(),
        manifest_path=Path(args.manifest).resolve(),
    )


if __name__ == "__main__":
    main()
