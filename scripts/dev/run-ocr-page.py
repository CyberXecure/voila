from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import fitz


PROJECT = Path(".").resolve()
INPUT_DIR = PROJECT / "data" / "input"
OUTPUT_DIR = PROJECT / "data" / "output"

sys.path.insert(0, str(PROJECT / "services" / "api"))
import document_language as dl


def find_tesseract() -> str:
    candidates = [
        os.environ.get("TESSERACT_CMD"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        "tesseract",
    ]

    for item in candidates:
        if not item:
            continue

        if item == "tesseract":
            return item

        if Path(item).exists():
            return item

    raise SystemExit("Nu găsesc tesseract.exe. Verifică instalarea Tesseract OCR.")


def find_pdf(name_or_part: str) -> Path:
    raw = Path(name_or_part)

    if raw.exists():
        return raw.resolve()

    matches = [
        p for p in INPUT_DIR.glob("*.pdf")
        if name_or_part.lower() in p.name.lower()
    ]

    if not matches:
        raise SystemExit(f"Nu găsesc PDF în data/input pentru: {name_or_part}")

    if len(matches) > 1:
        print("Mai multe PDF-uri potrivite:")
        for p in matches:
            print("-", p.name)
        raise SystemExit("Folosește un nume mai specific.")

    return matches[0]


def render_page(pdf_path: Path, page_number: int, zoom: float, image_path: Path) -> None:
    doc = fitz.open(pdf_path)

    if page_number < 1 or page_number > doc.page_count:
        raise SystemExit(f"Pagina {page_number} este în afara intervalului 1..{doc.page_count}")

    page = doc.load_page(page_number - 1)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    pix.save(str(image_path))
    doc.close()




def render_page_columns(pdf_path: Path, page_number: int, zoom: float, tmp_dir: Path, columns: int) -> list[Path]:
    doc = fitz.open(pdf_path)

    if page_number < 1 or page_number > doc.page_count:
        raise SystemExit(f"Pagina {page_number} este în afara intervalului 1..{doc.page_count}")

    page = doc.load_page(page_number - 1)
    rect = page.rect

    image_paths: list[Path] = []

    for index in range(columns):
        x0 = rect.x0 + (rect.width * index / columns)
        x1 = rect.x0 + (rect.width * (index + 1) / columns)

        # Small overlap helps avoid cutting words close to column boundaries.
        overlap = rect.width * 0.01

        if index > 0:
            x0 -= overlap

        if index < columns - 1:
            x1 += overlap

        clip = fitz.Rect(x0, rect.y0, x1, rect.y1)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False)

        image_path = tmp_dir / f"page_{page_number:04d}_col_{index + 1}.png"
        pix.save(str(image_path))
        image_paths.append(image_path)

    doc.close()
    return image_paths


def run_tesseract(image_path: Path, lang: str, psm: int) -> str:
    tesseract = find_tesseract()

    env = os.environ.copy()
    tessdata = PROJECT / ".tessdata"

    if tessdata.exists():
        env["TESSDATA_PREFIX"] = str(tessdata)

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

    if result.returncode != 0:
        print("STDERR:")
        print(result.stderr)
        raise SystemExit(f"Tesseract failed with code {result.returncode}")

    return str(result.stdout or "").strip()


def load_manual_pages(path: Path) -> dict:
    if not path.exists():
        return {
            "source": "manual_page_ocr",
            "pages": [],
        }

    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        data = {
            "source": "manual_page_ocr",
            "pages": [],
        }

    if not isinstance(data, dict):
        data = {
            "source": "manual_page_ocr",
            "pages": [],
        }

    if not isinstance(data.get("pages"), list):
        data["pages"] = []

    return data


def save_page_text(out_dir: Path, page_number: int, text: str, lang: str, psm: int, zoom: float) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / "ocr_pages.manual.json"
    data = load_manual_pages(path)

    pages = [
        item for item in data["pages"]
        if int(item.get("page_number", -1)) != int(page_number)
    ]

    pages.append(
        {
            "page_number": int(page_number),
            "text": text,
            "chars": len(text),
            "lang": lang,
            "psm": psm,
            "zoom": zoom,
            "source": "manual_single_page_tesseract",
        }
    )

    pages.sort(key=lambda item: int(item.get("page_number", 0)))

    data["pages"] = pages

    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    md_path = out_dir / "ocr_pages.manual.md"
    md_lines = []

    for item in pages:
        md_lines.append(f"## Page {item.get('page_number')}")
        md_lines.append("")
        md_lines.append(str(item.get("text") or ""))
        md_lines.append("")

    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, help="PDF filename or unique substring from data/input")
    parser.add_argument("--page", type=int, required=True)
    parser.add_argument("--lang", default="auto")
    parser.add_argument("--psm", type=int, default=6)
    parser.add_argument("--zoom", type=float, default=3.0)
    parser.add_argument("--columns", type=int, default=0, help="0/1 = normal OCR, 2/3 = OCR left-to-right by columns")

    args = parser.parse_args()

    pdf_path = find_pdf(args.pdf)

    if str(args.lang or "").lower() == "auto":
        args.lang = dl.get_ocr_lang(PROJECT, pdf_path.name)

    out_dir = OUTPUT_DIR / pdf_path.stem

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        image_path = tmp_dir / f"page_{args.page:04d}.png"

        print("PDF:", pdf_path)
        print("Page:", args.page)
        print("Lang:", args.lang)
        print("PSM:", args.psm)
        print("Zoom:", args.zoom)
        print("Columns:", args.columns)
        print("")

        if int(args.columns or 0) > 1:
            image_paths = render_page_columns(
                pdf_path=pdf_path,
                page_number=args.page,
                zoom=args.zoom,
                tmp_dir=tmp_dir,
                columns=int(args.columns),
            )

            chunks = []

            for col_index, col_image in enumerate(image_paths, start=1):
                print(f"OCR column {col_index}/{len(image_paths)}...")
                chunk = run_tesseract(col_image, args.lang, args.psm).strip()

                if chunk:
                    chunks.append(chunk)

            text = "\n\n".join(chunks).strip()
        else:
            render_page(pdf_path, args.page, args.zoom, image_path)
            text = run_tesseract(image_path, args.lang, args.psm)

    saved = save_page_text(out_dir, args.page, text, args.lang, args.psm, args.zoom)

    print("OCR complete.")
    print("Chars:", len(text))
    print("Words:", len(text.split()))
    print("Saved:", saved)
    print("")
    preview = text[:1200]
    try:
        print(preview)
    except UnicodeEncodeError:
        print(preview.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
