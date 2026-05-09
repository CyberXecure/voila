from __future__ import annotations

from pathlib import Path
import json
import re
import sys
from datetime import datetime

PROJECT = Path(".").resolve()
INPUT_DIR = PROJECT / "data" / "input"
OUTPUT_DIR = PROJECT / "data" / "output"
REPORT_DIR = OUTPUT_DIR / "_reports"

OCR_CANDIDATES = [
    "ocr_corrections.json",
    "ocr_pages.post_clean.json",
    "ocr_tsv_columns_pages.post_clean.json",
    "ocr_body_columns_pages.post_clean.json",
    "ocr_pages.json",
    "ocr_tsv_columns_pages.json",
    "ocr_body_columns_pages.json",
    "course.json",
    "study_concepts.json",
]

PRIORITY_FOR_BEST = [
    "ocr_corrections.json",
    "ocr_pages.post_clean.json",
    "ocr_tsv_columns_pages.post_clean.json",
    "ocr_body_columns_pages.post_clean.json",
    "ocr_pages.json",
    "ocr_tsv_columns_pages.json",
    "ocr_body_columns_pages.json",
]


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def get_pdf_page_count(pdf_path: Path) -> int | None:
    try:
        import fitz
        doc = fitz.open(pdf_path)
        count = doc.page_count
        doc.close()
        return int(count)
    except Exception:
        return None


def normalize_page_number(value) -> int | None:
    try:
        return int(value)
    except Exception:
        return None


def extract_pages_from_json(data) -> dict[int, str]:
    pages: dict[int, str] = {}

    if data is None:
        return pages

    # Shape: {"pages": [{"page_number": 1, "text": "..."}]}
    if isinstance(data, dict) and isinstance(data.get("pages"), list):
        for item in data["pages"]:
            if not isinstance(item, dict):
                continue

            page = normalize_page_number(
                item.get("page_number")
                or item.get("page")
                or item.get("page_index")
            )

            if page is None:
                continue

            # page_index may be zero-based in some files
            if "page_index" in item and "page_number" not in item and page >= 0:
                page = page + 1

            text = (
                item.get("text")
                or item.get("corrected_text")
                or item.get("body")
                or item.get("content")
                or ""
            )

            pages[page] = str(text or "")

        return pages

    # Shape: {"3": {"text": "..."}}, {"page_3": "..."}
    if isinstance(data, dict):
        for key, value in data.items():
            page = None

            if isinstance(key, int):
                page = key
            else:
                m = re.search(r"\d+", str(key))
                if m:
                    page = int(m.group(0))

            if page is None:
                continue

            if isinstance(value, dict):
                text = (
                    value.get("text")
                    or value.get("corrected_text")
                    or value.get("body")
                    or value.get("content")
                    or ""
                )
            else:
                text = value

            pages[page] = str(text or "")

    return pages


def count_rendered_images(out_dir: Path) -> int:
    if not out_dir.exists():
        return 0

    image_exts = {".png", ".jpg", ".jpeg", ".webp"}
    count = 0

    for path in out_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in image_exts:
            count += 1

    return count


def page_has_text(text: str) -> bool:
    return bool(str(text or "").strip())


def summarize_pdf(pdf_path: Path) -> dict:
    pdf_name = pdf_path.name
    stem = pdf_path.stem
    out_dir = OUTPUT_DIR / stem
    page_count = get_pdf_page_count(pdf_path)

    files = {}
    best_by_page: dict[int, dict] = {}

    for candidate in OCR_CANDIDATES:
        path = out_dir / candidate
        pages = extract_pages_from_json(read_json(path)) if path.exists() else {}

        non_empty = {
            page: text
            for page, text in pages.items()
            if page_has_text(text)
        }

        files[candidate] = {
            "exists": path.exists(),
            "pages_total": len(pages),
            "pages_with_text": len(non_empty),
            "chars_total": sum(len(text or "") for text in non_empty.values()),
        }

    for source_name in PRIORITY_FOR_BEST:
        path = out_dir / source_name
        pages = extract_pages_from_json(read_json(path)) if path.exists() else {}

        for page, text in pages.items():
            if not page_has_text(text):
                continue

            if page not in best_by_page:
                best_by_page[page] = {
                    "source": source_name,
                    "chars": len(text),
                    "preview": text[:160].replace("\n", " "),
                }

    pages_with_best_ocr = len(best_by_page)

    if page_count:
        empty_pages = [
            page
            for page in range(1, page_count + 1)
            if page not in best_by_page
        ]
    else:
        empty_pages = []

    corrected_pages = files.get("ocr_corrections.json", {}).get("pages_with_text", 0)

    return {
        "pdf": pdf_name,
        "output_dir": str(out_dir.relative_to(PROJECT)) if out_dir.exists() else str(out_dir),
        "output_dir_exists": out_dir.exists(),
        "page_count": page_count,
        "rendered_images": count_rendered_images(out_dir),
        "pages_with_best_ocr": pages_with_best_ocr,
        "pages_corrected": corrected_pages,
        "empty_pages_count": len(empty_pages),
        "empty_pages_first_40": empty_pages[:40],
        "coverage_percent": round((pages_with_best_ocr / page_count) * 100, 2) if page_count else None,
        "files": files,
    }


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(INPUT_DIR.glob("*.pdf"))

    if not pdfs:
        print("Nu am găsit PDF-uri în data/input")
        return 1

    report = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "project": str(PROJECT),
        "pdf_count": len(pdfs),
        "manuals": [summarize_pdf(pdf) for pdf in pdfs],
    }

    json_path = REPORT_DIR / "ocr_coverage_report.json"
    md_path = REPORT_DIR / "ocr_coverage_report.md"

    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = []
    lines.append("# OCR Coverage Report")
    lines.append("")
    lines.append(f"Created: {report['created_at']}")
    lines.append("")
    lines.append("| PDF | Pages | Best OCR | Corrected | Empty | Coverage | Rendered images |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")

    for item in report["manuals"]:
        coverage = item["coverage_percent"]
        coverage_txt = "" if coverage is None else f"{coverage}%"

        lines.append(
            "| "
            + item["pdf"].replace("|", "\\|")
            + f" | {item['page_count'] or ''}"
            + f" | {item['pages_with_best_ocr']}"
            + f" | {item['pages_corrected']}"
            + f" | {item['empty_pages_count']}"
            + f" | {coverage_txt}"
            + f" | {item['rendered_images']}"
            + " |"
        )

    lines.append("")
    lines.append("## Empty pages sample")
    lines.append("")

    for item in report["manuals"]:
        lines.append(f"### {item['pdf']}")
        lines.append("")
        lines.append(f"- Output dir exists: `{item['output_dir_exists']}`")
        lines.append(f"- Output dir: `{item['output_dir']}`")
        lines.append(f"- First empty pages: `{item['empty_pages_first_40']}`")
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print("OCR coverage report created:")
    print("-", json_path)
    print("-", md_path)
    print("")

    print("Summary:")
    for item in report["manuals"]:
        print(
            f"- {item['pdf']}: "
            f"{item['pages_with_best_ocr']}/{item['page_count']} pages OCR, "
            f"corrected={item['pages_corrected']}, "
            f"empty={item['empty_pages_count']}, "
            f"coverage={item['coverage_percent']}%"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
