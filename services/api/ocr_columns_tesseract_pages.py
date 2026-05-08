from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

import fitz
import numpy as np
from PIL import Image


def find_tesseract() -> str:
    candidates = [
        os.environ.get("TESSERACT_EXE"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        "tesseract",
    ]

    for candidate in candidates:
        if not candidate:
            continue

        if candidate == "tesseract" or Path(candidate).exists():
            return candidate

    raise FileNotFoundError("Tesseract executable not found.")


def resolve_tessdata_prefix(project_root: Path) -> str | None:
    local = project_root / ".tessdata"

    if local.exists():
        return str(local)

    existing = os.environ.get("TESSDATA_PREFIX")

    if existing:
        return existing

    return None


def render_page(doc: fitz.Document, page_index: int, zoom: float) -> Image.Image:
    page = doc.load_page(page_index)
    matrix = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=False)

    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


def trim_dark_edges(img: Image.Image) -> Image.Image:
    gray = np.array(img.convert("L"))
    h, w = gray.shape

    dark = gray < 45

    col_dark_ratio = dark.mean(axis=0)
    row_dark_ratio = dark.mean(axis=1)

    left = 0
    right = w
    top = 0
    bottom = h

    while left < w - 1 and col_dark_ratio[left] > 0.35:
        left += 1

    while right > left + 1 and col_dark_ratio[right - 1] > 0.35:
        right -= 1

    while top < h - 1 and row_dark_ratio[top] > 0.80:
        top += 1

    while bottom > top + 1 and row_dark_ratio[bottom - 1] > 0.80:
        bottom -= 1

    return img.crop((left, top, right, bottom))


def content_bbox(img: Image.Image, padding: int = 12) -> tuple[int, int, int, int]:
    gray = np.array(img.convert("L"))
    h, w = gray.shape

    ink = gray < 245

    row_ratio = ink.mean(axis=1)
    col_ratio = ink.mean(axis=0)

    rows = np.where(row_ratio > 0.002)[0]
    cols = np.where(col_ratio > 0.002)[0]

    if len(rows) == 0 or len(cols) == 0:
        return (0, 0, w, h)

    left = max(0, int(cols[0]) - padding)
    right = min(w, int(cols[-1]) + padding)
    top = max(0, int(rows[0]) - padding)
    bottom = min(h, int(rows[-1]) + padding)

    return (left, top, right, bottom)


def split_fixed_columns(
    bbox: tuple[int, int, int, int],
    columns: int,
    gutter_ratio: float,
) -> list[tuple[int, int, int, int]]:
    left, top, right, bottom = bbox
    width = right - left

    if columns <= 1:
        return [bbox]

    col_width = width / columns
    gutter = int(width * gutter_ratio)

    boxes = []

    for i in range(columns):
        x1 = int(left + i * col_width)
        x2 = int(left + (i + 1) * col_width)

        if i > 0:
            x1 += gutter // 2

        if i < columns - 1:
            x2 -= gutter // 2

        boxes.append((x1, top, x2, bottom))

    return boxes


def detect_auto_columns(
    img: Image.Image,
    bbox: tuple[int, int, int, int],
    max_columns: int = 3,
) -> int:
    left, top, right, bottom = bbox
    crop = img.crop((left, top, right, bottom))
    gray = np.array(crop.convert("L"))

    h, w = gray.shape

    if w < 500:
        return 1

    ink = gray < 210
    density = ink.mean(axis=0)

    window = max(15, int(w * 0.015))
    kernel = np.ones(window) / window
    smooth = np.convolve(density, kernel, mode="same")

    threshold = max(0.004, np.percentile(smooth, 20) * 1.15)
    low = smooth < threshold

    min_gutter = max(18, int(w * 0.025))
    runs = []
    start = None

    for idx, value in enumerate(low):
        if value and start is None:
            start = idx

        if (not value or idx == len(low) - 1) and start is not None:
            end = idx if not value else idx + 1
            length = end - start

            center = (start + end) // 2

            if length >= min_gutter and int(w * 0.15) < center < int(w * 0.85):
                runs.append((start, end, length, center))

            start = None

    if len(runs) >= 2 and max_columns >= 3:
        return 3

    if len(runs) >= 1:
        return 2

    return 1


def run_tesseract(
    img: Image.Image,
    tesseract: str,
    lang: str,
    psm: int,
    tessdata_prefix: str | None,
) -> tuple[str, float, int]:
    start = time.time()

    env = os.environ.copy()

    if tessdata_prefix:
        env["TESSDATA_PREFIX"] = tessdata_prefix

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        image_path = tmp_dir / "crop.png"

        img.save(image_path)

        cmd = [
            tesseract,
            str(image_path),
            "stdout",
            "-l",
            lang,
            "--psm",
            str(psm),
        ]

        result = subprocess.run(
            cmd,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env=env,
        )

    elapsed = time.time() - start

    text = (result.stdout or "").replace("\f", "").strip()

    return text, elapsed, result.returncode


def normalize_text(text: str) -> str:
    lines = []

    for line in str(text or "").splitlines():
        clean = " ".join(line.strip().split())

        if clean:
            lines.append(clean)

    return "\n".join(lines).strip()


def save_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_md(path: Path, pdf_name: str, pages: list[dict]) -> None:
    lines = [
        f"# OCR column pages for {pdf_name}",
        "",
        "Generated by Voila! column-aware Tesseract OCR.",
        "",
    ]

    for page in pages:
        lines.extend(
            [
                f"## Page {page['page_number']}",
                "",
                str(page.get("text") or "").strip(),
                "",
            ]
        )

    path.write_text("\n".join(lines), encoding="utf-8")


def backup_once(path: Path) -> None:
    if not path.exists():
        return

    backup = path.with_suffix(path.suffix + ".before_columns_ocr")

    if backup.exists():
        return

    backup.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! column-aware Tesseract OCR")

    parser.add_argument("pdf_path")
    parser.add_argument("output_dir")

    parser.add_argument("--lang", default="ron+eng")
    parser.add_argument("--columns", default="auto", help="auto, 1, 2, or 3")
    parser.add_argument("--zoom", type=float, default=2.5)
    parser.add_argument("--psm", type=int, default=6)
    parser.add_argument("--gutter-ratio", type=float, default=0.025)
    parser.add_argument("--header-ratio", type=float, default=0.075)

    parser.add_argument("--min-page", type=int, default=1)
    parser.add_argument("--max-page", type=int, default=0)

    parser.add_argument("--replace-pages", action="store_true")

    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    pdf_path = Path(args.pdf_path).resolve()
    output_dir = Path(args.output_dir).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    tesseract = find_tesseract()
    tessdata_prefix = resolve_tessdata_prefix(project_root)

    doc = fitz.open(pdf_path)

    total_pages = len(doc)
    min_page = max(1, args.min_page)
    max_page = args.max_page if args.max_page > 0 else total_pages
    max_page = min(total_pages, max_page)

    pages = []
    report_pages = []

    print("Voila! column OCR started.")
    print(f"PDF: {pdf_path}")
    print(f"Pages: {min_page}-{max_page} / {total_pages}")
    print(f"Columns: {args.columns}")
    print(f"Lang: {args.lang}")
    print(f"PSM: {args.psm}")
    print(f"Zoom: {args.zoom}")
    print(f"Tesseract: {tesseract}")

    if tessdata_prefix:
        print(f"TESSDATA_PREFIX: {tessdata_prefix}")

    for page_number in range(min_page, max_page + 1):
        print(f"OCR page {page_number}/{max_page}...")

        page_start = time.time()
        image = render_page(doc, page_number - 1, args.zoom)
        image = trim_dark_edges(image)

        bbox = content_bbox(image)

        left, top, right, bottom = bbox
        height = bottom - top
        header_h = int(height * args.header_ratio)

        header_box = (left, top, right, min(bottom, top + header_h))
        body_box = (left, min(bottom, top + header_h), right, bottom)

        if args.columns == "auto":
            detected_columns = detect_auto_columns(image, body_box, max_columns=3)
        else:
            detected_columns = max(1, int(args.columns))

        texts = []
        crop_reports = []

        if args.header_ratio > 0:
            header_img = image.crop(header_box)
            header_text, header_seconds, header_code = run_tesseract(
                header_img,
                tesseract=tesseract,
                lang=args.lang,
                psm=args.psm,
                tessdata_prefix=tessdata_prefix,
            )

            header_text = normalize_text(header_text)

            if header_text:
                texts.append(header_text)

            crop_reports.append(
                {
                    "kind": "header",
                    "box": header_box,
                    "chars": len(header_text),
                    "seconds": round(header_seconds, 3),
                    "returncode": header_code,
                }
            )

        column_boxes = split_fixed_columns(
            body_box,
            columns=detected_columns,
            gutter_ratio=args.gutter_ratio,
        )

        for col_index, col_box in enumerate(column_boxes, start=1):
            crop = image.crop(col_box)

            col_text, col_seconds, col_code = run_tesseract(
                crop,
                tesseract=tesseract,
                lang=args.lang,
                psm=args.psm,
                tessdata_prefix=tessdata_prefix,
            )

            col_text = normalize_text(col_text)

            if col_text:
                texts.append(col_text)

            crop_reports.append(
                {
                    "kind": f"column_{col_index}",
                    "box": col_box,
                    "chars": len(col_text),
                    "seconds": round(col_seconds, 3),
                    "returncode": col_code,
                }
            )

        final_text = "\n\n".join(texts).strip()
        elapsed = time.time() - page_start

        pages.append(
            {
                "page_number": page_number,
                "text": final_text,
                "text_source": "tesseract_columns",
                "ocr_layout": {
                    "columns": detected_columns,
                    "header_ratio": args.header_ratio,
                    "psm": args.psm,
                    "zoom": args.zoom,
                },
            }
        )

        report_pages.append(
            {
                "page_number": page_number,
                "columns": detected_columns,
                "chars": len(final_text),
                "words": len(final_text.split()),
                "seconds": round(elapsed, 3),
                "crops": crop_reports,
            }
        )

    payload = {
        "version": "voila_tesseract_columns_v1",
        "pdf": str(pdf_path),
        "text_source": "tesseract_columns",
        "pages": pages,
    }

    report = {
        "version": "voila_tesseract_columns_report_v1",
        "pdf": str(pdf_path),
        "page_range": [min_page, max_page],
        "total_chars": sum(len(page.get("text") or "") for page in pages),
        "total_words": sum(len((page.get("text") or "").split()) for page in pages),
        "columns": args.columns,
        "psm": args.psm,
        "zoom": args.zoom,
        "pages": report_pages,
    }

    json_path = output_dir / "ocr_columns_pages.json"
    md_path = output_dir / "ocr_columns_pages.md"
    report_path = output_dir / "ocr_columns_report.json"

    save_json(json_path, payload)
    save_md(md_path, pdf_path.name, pages)
    save_json(report_path, report)

    if args.replace_pages:
        for target_name in ["ocr_pages.json", "pages.json"]:
            target = output_dir / target_name
            backup_once(target)
            save_json(target, payload)

        for target_name in ["ocr_pages.md", "pages.md"]:
            target = output_dir / target_name
            backup_once(target)
            save_md(target, pdf_path.name, pages)

    print("Voila! column OCR complete.")
    print(f"Pages OCRed: {len(pages)}")
    print(f"Total chars: {report['total_chars']}")
    print(f"Total words: {report['total_words']}")
    print(f"- {json_path}")
    print(f"- {md_path}")
    print(f"- {report_path}")

    if args.replace_pages:
        print("Replaced pages.json / pages.md / ocr_pages.json / ocr_pages.md")


if __name__ == "__main__":
    main()
