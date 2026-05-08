from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import fitz
from PIL import Image, ImageFilter, ImageOps


def find_tesseract() -> str:
    found = shutil.which("tesseract")

    if found:
        return found

    candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]

    for candidate in candidates:
        if Path(candidate).exists():
            return candidate

    raise FileNotFoundError("Tesseract not found.")


def load_existing_ocr(output_dir: Path) -> dict[int, str]:
    candidates = [
        output_dir / "ocr_pages.cleaned.json",
        output_dir / "ocr_pages.json",
        output_dir / "pages.json",
    ]

    for path in candidates:
        if not path.exists():
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        if isinstance(data, dict):
            pages = data.get("pages") or data.get("items") or []
        elif isinstance(data, list):
            pages = data
        else:
            pages = []

        result = {}

        for idx, page in enumerate(pages, start=1):
            if not isinstance(page, dict):
                continue

            page_number = int(page.get("page_number") or page.get("pdf_page") or idx)
            text = str(page.get("text") or page.get("content") or "").strip()

            result[page_number] = text

        if result:
            return result

    return {}


def render_base(page: fitz.Page, zoom: float) -> Image.Image:
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return image


def preprocess(image: Image.Image, mode: str) -> Image.Image:
    gray = ImageOps.grayscale(image)

    if mode == "gray":
        return ImageOps.autocontrast(gray)

    if mode == "sharp":
        img = ImageOps.autocontrast(gray)
        img = img.filter(ImageFilter.SHARPEN)
        return img

    if mode == "binary":
        img = ImageOps.autocontrast(gray)
        return img.point(lambda p: 255 if p > 185 else 0)

    if mode == "denoise":
        img = ImageOps.autocontrast(gray)
        img = img.filter(ImageFilter.MedianFilter(size=3))
        img = img.filter(ImageFilter.SHARPEN)
        return img

    return ImageOps.autocontrast(gray)


def run_tesseract(
    tesseract: str,
    image_path: Path,
    lang: str,
    psm: int,
    tessdata_prefix: str | None,
) -> tuple[str, float]:
    env = os.environ.copy()

    if tessdata_prefix:
        env["TESSDATA_PREFIX"] = tessdata_prefix

    cmd = [
        tesseract,
        str(image_path),
        "stdout",
        "-l",
        lang,
        "--oem",
        "1",
        "--psm",
        str(psm),
    ]

    start = time.time()

    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )

    elapsed = time.time() - start

    if result.returncode != 0:
        return "", elapsed

    return (result.stdout or "").replace("\f", "").strip(), elapsed


def quality_score(text: str) -> float:
    compact = re.sub(r"\s+", " ", text or "").strip()

    if not compact:
        return -100000.0

    chars = len(compact)
    words = re.findall(r"[A-Za-zĂÂÎȘȚăâîșț0-9]{2,}", compact)
    word_count = len(words)

    letters = re.findall(r"[A-Za-zĂÂÎȘȚăâîșț]", compact)
    letter_ratio = len(letters) / max(1, chars)

    romanian_hits = sum(
        compact.lower().count(token)
        for token in [
            " și ",
            " în ",
            " este ",
            " sunt ",
            " pentru ",
            " instala",
            " electric",
            " curent",
            " tensiune",
            " iluminat",
            " protec",
            " comand",
        ]
    )

    weird_chars = len(re.findall(r"[�□■●◆◇<>~`^\\]", compact))
    broken_words = len(re.findall(r"\b[A-Za-zĂÂÎȘȚăâîșț]{1}\b", compact))
    repeated_noise = len(re.findall(r"([|Il1._-]\s*){5,}", compact))

    score = 0.0
    score += min(chars, 8000) * 0.08
    score += word_count * 1.6
    score += letter_ratio * 250
    score += romanian_hits * 12
    score -= weird_chars * 25
    score -= broken_words * 2.2
    score -= repeated_noise * 35

    # Prefer useful technical pages, not pure cover/front matter.
    if word_count < 40:
        score -= 400

    if "cuprins" in compact.lower() and len(re.findall(r"\.{3,}\s*\d+", compact)) > 10:
        score -= 250

    return score


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("˚", "°").replace("º", "°")
    text = text.replace("“", '"').replace("”", '"').replace("„", '"')
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"-\n(?=[a-zăâîșț])", "", text, flags=re.IGNORECASE)

    lines = []

    for line in text.splitlines():
        value = line.strip()

        if not value:
            lines.append("")
            continue

        if re.fullmatch(r"[|Il1\s._-]{1,10}", value):
            continue

        lines.append(value)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def write_pages_json(path: Path, pdf_path: Path, pages: list[dict]) -> None:
    payload = {
        "version": "voila_advanced_ocr_v0.4.1",
        "source_file": str(pdf_path),
        "page_count": len(pages),
        "pages": pages,
    }

    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_pages_md(path: Path, pdf_name: str, pages: list[dict]) -> None:
    chunks = [
        f"# Advanced OCR pages for {pdf_name}",
        "",
        "Generated by Voila! Advanced OCR.",
        "",
    ]

    for page in pages:
        chunks.extend(
            [
                f"## Page {page['page_number']}",
                "",
                page.get("text") or "",
                "",
            ]
        )

    path.write_text("\n".join(chunks), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! Advanced OCR ensemble")
    parser.add_argument("pdf")
    parser.add_argument("output_dir")
    parser.add_argument("--lang", default="ron+eng")
    parser.add_argument("--zoom", type=float, default=2.2)
    parser.add_argument("--page-from", type=int, default=1)
    parser.add_argument("--page-to", type=int, default=0)
    parser.add_argument("--repair-only", action="store_true")
    parser.add_argument("--replace-pages", action="store_true")
    parser.add_argument("--replace-ocr", action="store_true")
    parser.add_argument("--tessdata-prefix", default="")

    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    tesseract = find_tesseract()
    tessdata_prefix = args.tessdata_prefix.strip() or os.environ.get("TESSDATA_PREFIX")

    existing = load_existing_ocr(output_dir)

    doc = fitz.open(pdf_path)

    page_from = max(1, args.page_from)
    page_to = min(len(doc), args.page_to if args.page_to > 0 else len(doc))

    work_dir = output_dir / "ocr" / "advanced_work"
    work_dir.mkdir(parents=True, exist_ok=True)

    pages = []
    report_pages = []

    variants = [
        ("gray", 1),
        ("gray", 4),
        ("sharp", 4),
        ("denoise", 4),
        ("binary", 6),
        ("gray", 11),
    ]

    print("Voila! Advanced OCR started.")
    print(f"PDF: {pdf_path}")
    print(f"Pages: {len(doc)}")
    print(f"Page range: {page_from}-{page_to}")
    print(f"Lang: {args.lang}")
    print(f"Zoom: {args.zoom}")
    print(f"Tesseract: {tesseract}")

    if tessdata_prefix:
        print(f"TESSDATA_PREFIX: {tessdata_prefix}")

    for page_number in range(page_from, page_to + 1):
        page = doc[page_number - 1]
        old_text = existing.get(page_number, "")
        old_score = quality_score(old_text)

        if args.repair_only and old_score >= 650 and len(old_text.split()) >= 120:
            best_text = clean_text(old_text)
            best_variant = "existing"
            best_score = old_score
            best_seconds = 0.0
        else:
            base = render_base(page, args.zoom)

            candidates = []

            if old_text:
                candidates.append(
                    {
                        "variant": "existing",
                        "text": old_text,
                        "score": old_score,
                        "seconds": 0.0,
                    }
                )

            for mode, psm in variants:
                image_path = work_dir / f"page_{page_number:04d}_{mode}_psm{psm}.png"
                processed = preprocess(base, mode)
                processed.save(image_path)

                print(f"OCR page {page_number}/{len(doc)} · {mode} · psm {psm}")

                text, seconds = run_tesseract(
                    tesseract=tesseract,
                    image_path=image_path,
                    lang=args.lang,
                    psm=psm,
                    tessdata_prefix=tessdata_prefix,
                )

                cleaned = clean_text(text)
                score = quality_score(cleaned)

                candidates.append(
                    {
                        "variant": f"{mode}_psm{psm}",
                        "text": cleaned,
                        "score": score,
                        "seconds": seconds,
                    }
                )

            best = sorted(candidates, key=lambda item: item["score"], reverse=True)[0]

            best_text = clean_text(best["text"])
            best_variant = best["variant"]
            best_score = float(best["score"])
            best_seconds = float(best["seconds"])

        pages.append(
            {
                "page_number": page_number,
                "text": best_text,
                "text_source": "advanced_tesseract_ensemble",
                "ocr_lang": args.lang,
                "variant": best_variant,
                "score": round(best_score, 2),
            }
        )

        report_pages.append(
            {
                "page_number": page_number,
                "chars": len(best_text),
                "words": len(best_text.split()),
                "variant": best_variant,
                "score": round(best_score, 2),
                "seconds": round(best_seconds, 2),
            }
        )

    doc.close()

    out_json = output_dir / "ocr_pages.advanced.json"
    out_md = output_dir / "ocr_pages.advanced.md"
    report = output_dir / "ocr_report.advanced.json"

    write_pages_json(out_json, pdf_path, pages)
    write_pages_md(out_md, pdf_path.name, pages)

    report.write_text(
        json.dumps(
            {
                "version": "voila_advanced_ocr_v0.4.1",
                "source_file": str(pdf_path),
                "page_from": page_from,
                "page_to": page_to,
                "page_count": len(pages),
                "total_chars": sum(item["chars"] for item in report_pages),
                "total_words": sum(item["words"] for item in report_pages),
                "pages": report_pages,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    if args.replace_ocr:
        backup = output_dir / "ocr_pages.before_advanced.json"

        src = output_dir / "ocr_pages.json"

        if src.exists() and not backup.exists():
            backup.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

        write_pages_json(src, pdf_path, pages)
        write_pages_md(output_dir / "ocr_pages.md", pdf_path.name, pages)

    if args.replace_pages:
        pages_json = output_dir / "pages.json"
        pages_md = output_dir / "pages.md"

        backup = output_dir / "pages.before_advanced_ocr.json"

        if pages_json.exists() and not backup.exists():
            backup.write_text(pages_json.read_text(encoding="utf-8"), encoding="utf-8")

        write_pages_json(pages_json, pdf_path, pages)
        write_pages_md(pages_md, pdf_path.name, pages)

    print("")
    print("Voila! Advanced OCR complete.")
    print(f"Total chars: {sum(item['chars'] for item in report_pages)}")
    print(f"Total words: {sum(item['words'] for item in report_pages)}")
    print(f"- {out_json}")
    print(f"- {out_md}")
    print(f"- {report}")


if __name__ == "__main__":
    main()
