from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import fitz  # PyMuPDF
except Exception as exc:  # pragma: no cover
    raise SystemExit("FAILED_IMPORT_PYMUPDF=" + str(exc))


ALLOWED_BBOX_UNITS = {"page_pixels", "pdf_points"}


def _fail(message: str) -> None:
    raise SystemExit(message)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        _fail("FAILED_LOAD_VISUAL_ITEMS_JSON=" + str(exc))
    if not isinstance(data, dict):
        _fail("FAILED_VISUAL_ITEMS_PAYLOAD_NOT_OBJECT")
    return data


def _validate_bbox(raw: Any) -> tuple[int, int, int, int]:
    if not isinstance(raw, list) or len(raw) != 4:
        _fail("FAILED_BBOX_MUST_BE_FOUR_ITEM_LIST")
    if not all(isinstance(x, int) for x in raw):
        _fail("FAILED_BBOX_MUST_BE_INTEGERS")
    x1, y1, x2, y2 = raw
    if x2 <= x1 or y2 <= y1:
        _fail("FAILED_BBOX_MUST_BE_ORDERED")
    return x1, y1, x2, y2


def _safe_rel_path(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        _fail("FAILED_EMPTY_PATH_FIELD=" + label)
    rel = Path(value.replace("\\", "/"))
    if rel.is_absolute() or ".." in rel.parts:
        _fail("FAILED_UNSAFE_RELATIVE_PATH=" + label)
    return rel


def _page_to_png(page: fitz.Page, page_image_path: Path, zoom: float) -> fitz.Pixmap:
    page_image_path.parent.mkdir(parents=True, exist_ok=True)
    matrix = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    pix.save(str(page_image_path))
    return pix


def _clip_rect_for_item(page: fitz.Page, bbox: tuple[int, int, int, int], units: str, zoom: float) -> fitz.Rect:
    x1, y1, x2, y2 = bbox
    page_rect = page.rect

    if units == "pdf_points":
        rect = fitz.Rect(x1, y1, x2, y2)
    elif units == "page_pixels":
        rect = fitz.Rect(x1 / zoom, y1 / zoom, x2 / zoom, y2 / zoom)
    else:
        _fail("FAILED_UNSUPPORTED_BBOX_UNITS=" + str(units))

    rect = rect & page_rect
    if rect.is_empty or rect.width <= 0 or rect.height <= 0:
        _fail("FAILED_BBOX_OUTSIDE_PAGE_AFTER_CLIP")
    return rect


def build_crops(pdf_path: Path, visual_items_path: Path, output_root: Path, zoom: float = 2.0) -> dict[str, Any]:
    if zoom <= 0:
        _fail("FAILED_ZOOM_MUST_BE_POSITIVE")

    if not pdf_path.exists():
        _fail("FAILED_SOURCE_PDF_MISSING=" + str(pdf_path))

    payload = _load_json(visual_items_path)
    items = payload.get("items")
    if not isinstance(items, list):
        _fail("FAILED_ITEMS_MUST_BE_LIST")

    output_root.mkdir(parents=True, exist_ok=True)

    generated_items = []
    skipped_items = []

    document = fitz.open(str(pdf_path))
    try:
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                _fail(f"FAILED_ITEM_NOT_OBJECT={index}")

            page_number = item.get("page")
            if not isinstance(page_number, int) or page_number < 1:
                _fail(f"FAILED_ITEM_PAGE_INVALID={index}")

            if page_number > len(document):
                skipped_items.append({"index": index, "reason": "page_out_of_range", "page": page_number})
                continue

            bbox = _validate_bbox(item.get("bbox"))
            units = item.get("bbox_units")
            if units not in ALLOWED_BBOX_UNITS:
                _fail(f"FAILED_ITEM_BBOX_UNITS_INVALID={index}")

            page_image_rel = _safe_rel_path(item.get("page_image_path"), "page_image_path")
            crop_rel = _safe_rel_path(item.get("crop_path"), "crop_path")

            page = document[page_number - 1]

            page_image_path = output_root / page_image_rel
            crop_path = output_root / crop_rel
            crop_path.parent.mkdir(parents=True, exist_ok=True)

            _page_to_png(page, page_image_path, zoom)

            clip = _clip_rect_for_item(page, bbox, str(units), zoom)
            matrix = fitz.Matrix(zoom, zoom)
            crop_pix = page.get_pixmap(matrix=matrix, clip=clip, alpha=False)
            crop_pix.save(str(crop_path))

            item["crop_exists"] = crop_path.exists()
            item["page_image_path"] = str(page_image_rel).replace("\\", "/")
            item["crop_path"] = str(crop_rel).replace("\\", "/")

            generated_items.append(
                {
                    "item_id": item.get("item_id"),
                    "page": page_number,
                    "bbox": list(bbox),
                    "bbox_units": units,
                    "page_image_path": str(page_image_path),
                    "crop_path": str(crop_path),
                    "crop_size_bytes": crop_path.stat().st_size if crop_path.exists() else 0,
                }
            )
    finally:
        document.close()

    updated_path = output_root / "formula_visual_evidence" / "visual_items.bbox.with-crops.json"
    updated_path.parent.mkdir(parents=True, exist_ok=True)
    updated_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "source_pdf": str(pdf_path),
        "visual_items_path": str(visual_items_path),
        "output_root": str(output_root),
        "zoom": zoom,
        "item_count": len(items),
        "generated_crop_count": len(generated_items),
        "skipped_item_count": len(skipped_items),
        "generated_items": generated_items,
        "skipped_items": skipped_items,
        "updated_visual_items_path": str(updated_path),
    }

    summary_path = output_root / "formula_visual_evidence" / "visual_items.bbox.crop-summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Build real local crop PNG artifacts from a bbox visual_items file.")
    parser.add_argument("--pdf", required=True, help="Source PDF path")
    parser.add_argument("--visual-items", required=True, help="Path to visual_items.bbox.json")
    parser.add_argument("--output-root", required=True, help="Output root; relative paths from visual item fields are written under it")
    parser.add_argument("--zoom", type=float, default=2.0, help="Render zoom for PDF page/crop output")
    args = parser.parse_args()

    summary = build_crops(
        pdf_path=Path(args.pdf),
        visual_items_path=Path(args.visual_items),
        output_root=Path(args.output_root),
        zoom=args.zoom,
    )

    print("BBOX_VISUAL_CROPS_BUILD=PASS")
    print("source_pdf=" + summary["source_pdf"])
    print("visual_items_path=" + summary["visual_items_path"])
    print("output_root=" + summary["output_root"])
    print("generated_crop_count=" + str(summary["generated_crop_count"]))
    print("skipped_item_count=" + str(summary["skipped_item_count"]))
    print("updated_visual_items_path=" + summary["updated_visual_items_path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
