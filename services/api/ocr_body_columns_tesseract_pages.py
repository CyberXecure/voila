from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path

import fitz
import numpy as np
from PIL import Image


RO_LETTERS = "A-Za-zĂÂÎȘȚăâîșț"


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

    return os.environ.get("TESSDATA_PREFIX")


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

    return (
        max(0, int(cols[0]) - padding),
        max(0, int(rows[0]) - padding),
        min(w, int(cols[-1]) + padding),
        min(h, int(rows[-1]) + padding),
    )


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


def run_tesseract_tsv(
    img: Image.Image,
    tesseract: str,
    lang: str,
    psm: int,
    tessdata_prefix: str | None,
) -> tuple[str, float, int]:
    env = os.environ.copy()

    if tessdata_prefix:
        env["TESSDATA_PREFIX"] = tessdata_prefix

    start = time.time()

    with tempfile.TemporaryDirectory() as tmp:
        image_path = Path(tmp) / "crop.png"
        img.save(image_path)

        cmd = [
            tesseract,
            str(image_path),
            "stdout",
            "-l",
            lang,
            "--psm",
            str(psm),
            "tsv",
        ]

        result = subprocess.run(
            cmd,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env=env,
        )

    return result.stdout or "", time.time() - start, result.returncode



def run_tesseract_text(
    img: Image.Image,
    tesseract: str,
    lang: str,
    psm: int,
    tessdata_prefix: str | None,
) -> tuple[str, float, int]:
    env = os.environ.copy()

    if tessdata_prefix:
        env["TESSDATA_PREFIX"] = tessdata_prefix

    start = time.time()

    with tempfile.TemporaryDirectory() as tmp:
        image_path = Path(tmp) / "crop.png"
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

    return (result.stdout or "").replace("\f", "").strip(), time.time() - start, result.returncode

def parse_tsv_lines(tsv: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(tsv), delimiter="\t")
    groups: dict[tuple[str, str, str], list[dict]] = {}

    for row in reader:
        if row.get("level") != "5":
            continue

        word = (row.get("text") or "").strip()
        if not word:
            continue

        try:
            conf = float(row.get("conf") or -1)
            left = int(float(row.get("left") or 0))
            top = int(float(row.get("top") or 0))
            width = int(float(row.get("width") or 0))
            height = int(float(row.get("height") or 0))
        except Exception:
            continue

        key = (
            row.get("block_num") or "0",
            row.get("par_num") or "0",
            row.get("line_num") or "0",
        )

        groups.setdefault(key, []).append(
            {
                "word": word,
                "conf": conf,
                "left": left,
                "top": top,
                "right": left + width,
                "bottom": top + height,
            }
        )

    lines = []

    for _key, words in groups.items():
        words = sorted(words, key=lambda item: item["left"])
        text = " ".join(item["word"] for item in words)
        text = normalize_line(text)

        confs = [item["conf"] for item in words if item["conf"] >= 0]
        avg_conf = sum(confs) / len(confs) if confs else -1

        lines.append(
            {
                "text": text,
                "conf": avg_conf,
                "left": min(item["left"] for item in words),
                "top": min(item["top"] for item in words),
                "right": max(item["right"] for item in words),
                "bottom": max(item["bottom"] for item in words),
                "words": len(words),
            }
        )

    return sorted(lines, key=lambda item: (item["top"], item["left"]))


def normalize_line(value: str) -> str:
    value = str(value or "")
    value = value.replace("ﬁ", "fi").replace("ﬂ", "fl")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def is_caption_start(line: str) -> bool:
    value = line.strip().lower()
    return bool(
        re.match(r"^(fig\.|figura|fig)\s*[0-9ivxl]+\.", value)
        or re.match(r"^fig\.\s*", value)
    )


def looks_like_body_line(line: str, conf: float) -> bool:
    value = normalize_line(line)

    if not value:
        return False

    lower = value.lower()

    if is_caption_start(value):
        return False

    if re.match(r"^[\|\-—–_.,;:()\[\]{}<>/\\0-9\s%°]+$", value):
        return False

    if re.search(r"[|]{2,}|[_]{2,}|[=]{2,}", value):
        return False

    letters = len(re.findall(rf"[{RO_LETTERS}]", value))
    digits = len(re.findall(r"\d", value))
    weird = len(re.findall(r"[|<>~`^_=◆◇□■]", value))
    chars = max(1, len(value))

    if letters < 5:
        return False

    if weird / chars > 0.12:
        return False

    if digits > letters and letters < 16:
        return False

    tokens = value.split()

    one_char_tokens = [token for token in tokens if len(token.strip(".,;:()[]{}")) <= 1]
    if len(tokens) >= 4 and len(one_char_tokens) / len(tokens) > 0.50:
        return False

    if conf >= 0 and conf < 25 and letters < 20:
        return False

    if re.search(r"\b(y[o0]|wey|fOr|isu|vv|sns|fires)\b", lower):
        return False

    return True


def lines_to_text(lines: list[dict]) -> str:
    kept = []
    caption_skip = 0

    for line in lines:
        text = normalize_line(line["text"])

        if is_caption_start(text):
            caption_skip = 6
            continue

        if caption_skip > 0:
            caption_skip -= 1
            continue

        if looks_like_body_line(text, float(line.get("conf", -1))):
            kept.append(line)

    if not kept:
        return ""

    heights = [max(1, item["bottom"] - item["top"]) for item in kept]
    median_h = float(np.median(heights)) if heights else 20

    out = []
    prev_bottom = None

    for item in kept:
        text = normalize_line(item["text"])

        if prev_bottom is not None:
            gap = item["top"] - prev_bottom
            if gap > median_h * 1.6:
                out.append("")

        out.append(text)
        prev_bottom = item["bottom"]

    return "\n".join(out).strip()



def looks_like_plain_body_line(line: str) -> bool:
    value = normalize_line(line)

    if not value:
        return False

    if is_caption_start(value):
        return False

    lower = value.lower()

    if re.match(r"^[\|\-—–_.,;:()\[\]{}<>/\\0-9\s%°]+$", value):
        return False

    letters = len(re.findall(rf"[{RO_LETTERS}]", value))
    digits = len(re.findall(r"\d", value))
    weird = len(re.findall(r"[|<>~`^_=◆◇□■]", value))
    chars = max(1, len(value))

    if letters < 4:
        return False

    if weird / chars > 0.22:
        return False

    if digits > letters * 2 and letters < 20:
        return False

    if re.search(r"\b(y[o0]|wey|fOr|isu|vv|sns|fires)\b", lower):
        return False

    return True


def plain_text_to_body_text(raw: str) -> str:
    lines = [normalize_line(line) for line in str(raw or "").splitlines()]
    lines = [line for line in lines if line]

    kept = []
    caption_skip = 0

    for line in lines:
        lower = line.lower()

        if is_caption_start(line):
            caption_skip = 5
            continue

        if caption_skip > 0:
            # Skip caption continuations: labels, numbered parts, short technical legend lines.
            if (
                len(line) < 95
                or re.match(r"^\s*[0-9a-z]\s*[-–]", lower)
                or re.match(r"^\s*[0-9]+\s*[-–]", lower)
                or re.search(r"\b(balonul|filamentul|electrodul|suportul|soclu|tubul|intrare curent|înveliș)\b", lower)
            ):
                caption_skip -= 1
                continue

            caption_skip = 0

        if looks_like_plain_body_line(line):
            kept.append(line)

    # Join paragraph-like lines, preserving visible paragraph gaps only lightly.
    out = []
    for line in kept:
        if out and out[-1].endswith("-"):
            out[-1] = out[-1][:-1] + line
        else:
            out.append(line)

    return "\n".join(out).strip()

def ocr_image_text(
    img: Image.Image,
    tesseract: str,
    lang: str,
    psm: int,
    tessdata_prefix: str | None,
) -> tuple[str, dict]:
    tsv, seconds, code = run_tesseract_tsv(
        img,
        tesseract=tesseract,
        lang=lang,
        psm=psm,
        tessdata_prefix=tessdata_prefix,
    )

    lines = parse_tsv_lines(tsv)
    text = lines_to_text(lines)

    report = {
        "seconds": round(seconds, 3),
        "returncode": code,
        "raw_lines": len(lines),
        "kept_chars": len(text),
        "fallback": False,
    }

    # If TSV filtering was too aggressive, fall back to plain OCR + gentler filtering.
    if len(text.strip()) >= 40:
        return text, report

    plain, seconds2, code2 = run_tesseract_text(
        img,
        tesseract=tesseract,
        lang=lang,
        psm=psm,
        tessdata_prefix=tessdata_prefix,
    )

    fallback_text = plain_text_to_body_text(plain)

    if fallback_text.strip():
        report.update(
            {
                "fallback": True,
                "fallback_seconds": round(seconds2, 3),
                "fallback_returncode": code2,
                "fallback_raw_chars": len(plain),
                "fallback_kept_chars": len(fallback_text),
            }
        )
        return fallback_text, report

    report.update(
        {
            "fallback": True,
            "fallback_seconds": round(seconds2, 3),
            "fallback_returncode": code2,
            "fallback_raw_chars": len(plain),
            "fallback_kept_chars": 0,
        }
    )

    return text, report

def save_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def save_md(path: Path, pdf_name: str, pages: list[dict]) -> None:
    lines = [
        f"# OCR body-column pages for {pdf_name}",
        "",
        "Generated by Voila! column-aware body-text OCR.",
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

    backup = path.with_name(path.name + ".before_body_columns_ocr")

    if backup.exists():
        return

    backup.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! body-text column OCR")

    parser.add_argument("pdf_path")
    parser.add_argument("output_dir")

    parser.add_argument("--lang", default="ron+eng")
    parser.add_argument("--columns", type=int, default=3)
    parser.add_argument("--zoom", type=float, default=2.8)
    parser.add_argument("--psm", type=int, default=6)
    parser.add_argument("--gutter-ratio", type=float, default=0.025)
    parser.add_argument("--header-ratio", type=float, default=0.065)

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

    print("Voila! body-column OCR started.")
    print(f"PDF: {pdf_path}")
    print(f"Pages: {min_page}-{max_page} / {total_pages}")
    print(f"Columns: {args.columns}")
    print(f"Lang: {args.lang}")
    print(f"PSM: {args.psm}")
    print(f"Zoom: {args.zoom}")

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

        texts = []
        crops_report = []

        header_img = image.crop(header_box)
        header_text, header_report = ocr_image_text(
            header_img,
            tesseract=tesseract,
            lang=args.lang,
            psm=args.psm,
            tessdata_prefix=tessdata_prefix,
        )

        if header_text:
            texts.append(header_text)

        crops_report.append(
            {
                "kind": "header",
                "box": header_box,
                **header_report,
            }
        )

        column_boxes = split_fixed_columns(
            body_box,
            columns=args.columns,
            gutter_ratio=args.gutter_ratio,
        )

        for col_index, col_box in enumerate(column_boxes, start=1):
            crop = image.crop(col_box)

            col_text, col_report = ocr_image_text(
                crop,
                tesseract=tesseract,
                lang=args.lang,
                psm=args.psm,
                tessdata_prefix=tessdata_prefix,
            )

            if col_text:
                texts.append(col_text)

            crops_report.append(
                {
                    "kind": f"column_{col_index}",
                    "box": col_box,
                    **col_report,
                }
            )

        final_text = "\n\n".join(texts).strip()

        pages.append(
            {
                "page_number": page_number,
                "text": final_text,
                "text_source": "tesseract_body_columns",
                "ocr_layout": {
                    "columns": args.columns,
                    "header_ratio": args.header_ratio,
                    "psm": args.psm,
                    "zoom": args.zoom,
                    "filter": "tsv_body_lines_no_fig_captions",
                },
            }
        )

        report_pages.append(
            {
                "page_number": page_number,
                "chars": len(final_text),
                "words": len(final_text.split()),
                "seconds": round(time.time() - page_start, 3),
                "crops": crops_report,
            }
        )

    payload = {
        "version": "voila_tesseract_body_columns_v1",
        "pdf": str(pdf_path),
        "text_source": "tesseract_body_columns",
        "pages": pages,
    }

    report = {
        "version": "voila_tesseract_body_columns_report_v1",
        "pdf": str(pdf_path),
        "page_range": [min_page, max_page],
        "total_chars": sum(len(page.get("text") or "") for page in pages),
        "total_words": sum(len((page.get("text") or "").split()) for page in pages),
        "columns": args.columns,
        "psm": args.psm,
        "zoom": args.zoom,
        "pages": report_pages,
    }

    json_path = output_dir / "ocr_body_columns_pages.json"
    md_path = output_dir / "ocr_body_columns_pages.md"
    report_path = output_dir / "ocr_body_columns_report.json"

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

    print("Voila! body-column OCR complete.")
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
