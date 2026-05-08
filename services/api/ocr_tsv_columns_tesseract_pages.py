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


def tessdata_prefix(project_root: Path) -> str | None:
    local = project_root / ".tessdata"
    if local.exists():
        return str(local)
    return os.environ.get("TESSDATA_PREFIX")


def render_page(doc: fitz.Document, page_index: int, zoom: float) -> Image.Image:
    page = doc.load_page(page_index)
    pix = page.get_pixmap(
        matrix=fitz.Matrix(zoom, zoom),
        colorspace=fitz.csRGB,
        alpha=False,
    )
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


def run_tesseract_tsv(
    img: Image.Image,
    tesseract: str,
    lang: str,
    psm: int,
    tessdata: str | None,
) -> tuple[str, float, int]:
    env = os.environ.copy()

    if tessdata:
        env["TESSDATA_PREFIX"] = tessdata

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        image_path = tmp_dir / "page.png"
        output_base = tmp_dir / "ocr_out"
        tsv_path = tmp_dir / "ocr_out.tsv"

        img.save(image_path)

        cmd = [
            tesseract,
            str(image_path),
            str(output_base),
            "-l",
            lang,
            "--psm",
            str(psm),
            "-c",
            "tessedit_create_tsv=1",
        ]

        start = time.time()

        result = subprocess.run(
            cmd,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env=env,
        )

        elapsed = time.time() - start

        if tsv_path.exists():
            tsv = tsv_path.read_text(encoding="utf-8", errors="replace")
        else:
            tsv = result.stdout or ""

    return tsv, elapsed, result.returncode


def parse_words(tsv: str, min_conf: float = -1.0) -> list[dict]:
    raw = str(tsv or "").lstrip("\ufeff")

    if not raw.strip():
        return []

    reader = csv.DictReader(io.StringIO(raw), delimiter="\t")
    words = []

    for row in reader:
        clean_row = {
            str(k or "").lstrip("\ufeff").strip(): v
            for k, v in row.items()
        }

        level = str(clean_row.get("level") or "").strip()

        if level != "5":
            continue

        word_text = str(clean_row.get("text") or "").strip()

        if not word_text:
            continue

        try:
            conf = float(str(clean_row.get("conf") or "-1").replace(",", "."))
            left = int(float(str(clean_row.get("left") or "0").replace(",", ".")))
            top = int(float(str(clean_row.get("top") or "0").replace(",", ".")))
            width = int(float(str(clean_row.get("width") or "0").replace(",", ".")))
            height = int(float(str(clean_row.get("height") or "0").replace(",", ".")))
        except Exception:
            continue

        if min_conf >= 0 and conf >= 0 and conf < min_conf:
            continue

        if width <= 0 or height <= 0:
            continue

        words.append(
            {
                "text": word_text,
                "conf": conf,
                "left": left,
                "top": top,
                "right": left + width,
                "bottom": top + height,
                "cx": left + width / 2,
                "cy": top + height / 2,
                "height": height,
            }
        )

    return words


def normalize_line(value: str) -> str:
    value = str(value or "")
    value = value.replace("ﬁ", "fi").replace("ﬂ", "fl")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_leading_noise(value: str) -> str:
    value = normalize_line(value)
    value = re.sub(r"^[\s\|\]\[\(\)'\"`´~:;.,_—–\\/-]+", "", value)
    value = re.sub(r"^[a-z]\s+(?=[A-ZĂÂÎȘȚ])", "", value)
    return value.strip()


def has_fig_marker(value: str) -> bool:
    value = clean_leading_noise(value).lower()
    return bool(
        re.search(r"\bfig\.?\s*[0-9ivxl]+", value)
        or re.search(r"\bfigura\s*[0-9ivxl]+", value)
    )


def is_noise_line(value: str) -> bool:
    value = clean_leading_noise(value)
    lower = value.lower()

    if not value:
        return True

    if has_fig_marker(value):
        return True

    if re.match(r"^[\|\-—–_.,;:()\[\]{}<>/\\0-9\s%°]+$", value):
        return True

    bad_tokens = [
        "wey",
        "wate",
        "sires",
        "fires",
        "sns",
        "isu",
        "f0r",
        "the ii",
        "pan al",
    ]

    if any(token in lower for token in bad_tokens):
        return True

    legend_words = [
        "balonul",
        "filamentul",
        "electrodul",
        "suportul",
        "soclu",
        "tubul",
        "tubului",
        "intrare curent",
        "înveliș",
        "invelis",
        "dispozitiv",
        "vidului",
    ]

    if any(word in lower for word in legend_words) and len(value) < 140:
        return True

    letters = len(re.findall(rf"[{RO_LETTERS}]", value))
    digits = len(re.findall(r"\d", value))
    weird = len(re.findall(r"[|<>~`^_=◆◇□■]", value))
    chars = max(1, len(value))

    if letters < 4:
        return True

    if weird / chars > 0.20:
        return True

    if digits > letters * 2 and letters < 20:
        return True

    return False


def words_bbox(words: list[dict], img: Image.Image) -> tuple[int, int, int, int]:
    if not words:
        return (0, 0, img.width, img.height)

    return (
        max(0, int(min(w["left"] for w in words)) - 8),
        max(0, int(min(w["top"] for w in words)) - 8),
        min(img.width, int(max(w["right"] for w in words)) + 8),
        min(img.height, int(max(w["bottom"] for w in words)) + 8),
    )


def column_index(cx: float, left: int, right: int, columns: int) -> int:
    if columns <= 1:
        return 0

    width = max(1, right - left)
    idx = int((cx - left) / width * columns)

    if idx < 0:
        return 0

    if idx >= columns:
        return columns - 1

    return idx


def group_words_into_lines(words: list[dict]) -> list[list[dict]]:
    if not words:
        return []

    heights = [w["height"] for w in words if w["height"] > 0]
    median_h = float(np.median(heights)) if heights else 18
    tolerance = max(8, median_h * 0.65)

    words_sorted = sorted(words, key=lambda w: (w["cy"], w["left"]))

    lines: list[list[dict]] = []

    for word in words_sorted:
        placed = False

        for line in lines:
            line_cy = sum(w["cy"] for w in line) / len(line)

            if abs(word["cy"] - line_cy) <= tolerance:
                line.append(word)
                placed = True
                break

        if not placed:
            lines.append([word])

    for line in lines:
        line.sort(key=lambda w: w["left"])

    lines.sort(key=lambda line: min(w["top"] for w in line))

    return lines


def line_text(line: list[dict]) -> str:
    text = " ".join(w["text"] for w in sorted(line, key=lambda w: w["left"]))
    text = clean_leading_noise(text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    return normalize_line(text)


def page_words_to_text(
    words: list[dict],
    img: Image.Image,
    columns: int,
    header_ratio: float,
) -> tuple[str, dict]:
    if not words:
        return "", {"words": 0, "kept_lines": 0}

    left, top, right, bottom = words_bbox(words, img)
    height = bottom - top
    header_bottom = top + int(height * header_ratio)

    header_words = [w for w in words if w["cy"] < header_bottom]
    body_words = [w for w in words if w["cy"] >= header_bottom]

    output_lines = []

    # Header first, left-to-right.
    header_lines = group_words_into_lines(header_words)

    for line in header_lines:
        text = line_text(line)
        if text and not is_noise_line(text):
            output_lines.append(text)

    if output_lines:
        output_lines.append("")

    # Body: column 1 top-bottom, then column 2, then column 3.
    col_words = [[] for _ in range(columns)]

    for word in body_words:
        idx = column_index(word["cx"], left, right, columns)
        col_words[idx].append(word)

    kept_lines = 0

    for idx, words_in_col in enumerate(col_words):
        lines = group_words_into_lines(words_in_col)
        skip_after_fig = 0

        for line in lines:
            text = line_text(line)

            if not text:
                continue

            if has_fig_marker(text):
                skip_after_fig = 8
                continue

            if skip_after_fig > 0:
                if is_noise_line(text) or len(text) < 120:
                    skip_after_fig -= 1
                    continue

                skip_after_fig = 0

            if is_noise_line(text):
                continue

            output_lines.append(text)
            kept_lines += 1

        if idx < len(col_words) - 1:
            output_lines.append("")

    # Merge hyphenated lines.
    merged = []

    for line in output_lines:
        if not line:
            if merged and merged[-1]:
                merged.append("")
            continue

        if merged and merged[-1].endswith("-"):
            merged[-1] = merged[-1][:-1] + line
        else:
            merged.append(line)

    # Collapse excessive blanks.
    final_lines = []
    previous_blank = False

    for line in merged:
        blank = not line.strip()

        if blank and previous_blank:
            continue

        final_lines.append(line)
        previous_blank = blank

    return "\n".join(final_lines).strip(), {
        "words": len(words),
        "kept_lines": kept_lines,
        "bbox": [left, top, right, bottom],
    }


def save_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def save_md(path: Path, pdf_name: str, pages: list[dict]) -> None:
    lines = [
        f"# OCR TSV column-order pages for {pdf_name}",
        "",
        "Generated by Voila! full-page TSV OCR with column reading order.",
        "",
    ]

    for page in pages:
        lines.append(f"## Page {page['page_number']}")
        lines.append("")
        lines.append(str(page.get("text") or "").strip())
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def backup_once(path: Path) -> None:
    if not path.exists():
        return

    backup = path.with_name(path.name + ".before_tsv_columns_ocr")

    if backup.exists():
        return

    backup.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila TSV column-order OCR")

    parser.add_argument("pdf_path")
    parser.add_argument("output_dir")

    parser.add_argument("--lang", default="ron+eng")
    parser.add_argument("--columns", type=int, default=3)
    parser.add_argument("--zoom", type=float, default=2.8)
    parser.add_argument("--psm", type=int, default=11)
    parser.add_argument("--header-ratio", type=float, default=0.065)
    parser.add_argument("--min-page", type=int, default=1)
    parser.add_argument("--max-page", type=int, default=0)
    parser.add_argument("--replace-pages", action="store_true")
    parser.add_argument("--min-conf", type=float, default=-1.0)

    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    pdf_path = Path(args.pdf_path).resolve()
    output_dir = Path(args.output_dir).resolve()

    tesseract = find_tesseract()
    tessdata = tessdata_prefix(project_root)

    doc = fitz.open(pdf_path)

    total_pages = len(doc)
    min_page = max(1, args.min_page)
    max_page = args.max_page if args.max_page > 0 else total_pages
    max_page = min(total_pages, max_page)

    pages = []
    report_pages = []

    print("Voila TSV column OCR started.")
    print("PDF:", pdf_path)
    print(f"Pages: {min_page}-{max_page} / {total_pages}")
    print("Columns:", args.columns)
    print("PSM:", args.psm)
    print("Zoom:", args.zoom)

    for page_number in range(min_page, max_page + 1):
        print(f"OCR page {page_number}/{max_page}...")

        started = time.time()

        img = render_page(doc, page_number - 1, args.zoom)
        img = trim_dark_edges(img)

        tsv, ocr_seconds, code = run_tesseract_tsv(
            img,
            tesseract=tesseract,
            lang=args.lang,
            psm=args.psm,
            tessdata=tessdata,
        )

        tsv_preview = "\\n".join(str(tsv or "").splitlines()[:8])
        words = parse_words(tsv, min_conf=args.min_conf)

        text, layout_report = page_words_to_text(
            words,
            img,
            columns=args.columns,
            header_ratio=args.header_ratio,
        )

        pages.append(
            {
                "page_number": page_number,
                "text": text,
                "text_source": "tesseract_tsv_columns_v1",
                "ocr_layout": {
                    "columns": args.columns,
                    "psm": args.psm,
                    "zoom": args.zoom,
                    "header_ratio": args.header_ratio,
                    "method": "full_page_tsv_words_reordered_by_columns",
                },
            }
        )

        report_pages.append(
            {
                "page_number": page_number,
                "chars": len(text),
                "words": len(text.split()),
                "seconds": round(time.time() - started, 3),
                "ocr_seconds": round(ocr_seconds, 3),
                "returncode": code,
                "tsv_chars": len(tsv or ""),
                "tsv_preview": tsv_preview,
                "parsed_words": len(words),
                **layout_report,
            }
        )

    payload = {
        "version": "voila_tesseract_tsv_columns_v1",
        "pdf": str(pdf_path),
        "text_source": "tesseract_tsv_columns_v1",
        "pages": pages,
    }

    report = {
        "version": "voila_tesseract_tsv_columns_report_v1",
        "pdf": str(pdf_path),
        "page_range": [min_page, max_page],
        "columns": args.columns,
        "psm": args.psm,
        "zoom": args.zoom,
        "total_chars": sum(len(page.get("text") or "") for page in pages),
        "total_words": sum(len((page.get("text") or "").split()) for page in pages),
        "pages": report_pages,
    }

    json_path = output_dir / "ocr_tsv_columns_pages.json"
    md_path = output_dir / "ocr_tsv_columns_pages.md"
    report_path = output_dir / "ocr_tsv_columns_report.json"

    save_json(json_path, payload)
    save_md(md_path, pdf_path.name, pages)
    save_json(report_path, report)

    if args.replace_pages:
        for name in ["pages.json", "ocr_pages.json"]:
            target = output_dir / name
            backup_once(target)
            save_json(target, payload)

        for name in ["pages.md", "ocr_pages.md"]:
            target = output_dir / name
            backup_once(target)
            save_md(target, pdf_path.name, pages)

    print("Voila TSV column OCR complete.")
    print("Pages OCRed:", len(pages))
    print("Total chars:", report["total_chars"])
    print("Total words:", report["total_words"])
    print("-", json_path)
    print("-", md_path)
    print("-", report_path)

    if args.replace_pages:
        print("Replaced pages.json / pages.md / ocr_pages.json / ocr_pages.md")


if __name__ == "__main__":
    main()
