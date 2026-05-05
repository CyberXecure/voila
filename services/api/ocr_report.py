from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


OCR_SIGNALS = [
    r"\bFtgure\b",
    r"\bFig11re\b",
    r"\\lalves",
    r"\bArajses\b",
    r"\bdosed\b",
    r"\bStearn\b",
    r"\bdeaning\b",
    r"\blhin\b",
    r"\bam\.1\.rnber\b",
    r"\bf\s*alll\s*o\b",
]


def count_ocr_signals(text: str) -> int:
    total = 0

    for pattern in OCR_SIGNALS:
        total += len(re.findall(pattern, text, flags=re.IGNORECASE))

    return total


def infer_quality(word_count: int, signal_count: int) -> str:
    if word_count < 20:
        return "low_or_image_only"

    if signal_count >= 3:
        return "medium_review_recommended"

    if signal_count > 0:
        return "good_with_minor_ocr_signals"

    return "good"


def build_report(data: dict) -> dict:
    pages = []

    for page in data.get("pages", []):
        text = page.get("text", "") or ""
        word_count = len(text.split())
        signal_count = count_ocr_signals(text)

        pages.append(
            {
                "pdf_page": page.get("page"),
                "word_count": word_count,
                "ocr_signal_count": signal_count,
                "quality": infer_quality(word_count, signal_count),
            }
        )

    return {
        "source_file": data.get("source_file"),
        "source_page_count": data.get("page_count"),
        "method": "basic_ocr_signal_scan_v0.1",
        "pages": pages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! OCR report")
    parser.add_argument("pages_json", help="Path to pages.json")

    args = parser.parse_args()

    pages_json = Path(args.pages_json).resolve()

    if not pages_json.exists():
        raise FileNotFoundError(f"pages.json not found: {pages_json}")

    data = json.loads(pages_json.read_text(encoding="utf-8"))
    report = build_report(data)

    output_path = pages_json.parent / "ocr_report.json"

    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Voila! OCR report generated successfully.")
    print(f"- {output_path}")


if __name__ == "__main__":
    main()
