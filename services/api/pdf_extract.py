from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import fitz


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf(pdf_path: Path) -> dict:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)

    pages = []

    for index, page in enumerate(doc, start=1):
        raw_text = page.get_text("text")
        text = clean_text(raw_text)

        pages.append(
            {
                "page": index,
                "text": text,
                "char_count": len(text),
                "word_count": len(text.split()) if text else 0,
            }
        )

    title = doc.metadata.get("title") or pdf_path.stem

    return {
        "source_file": str(pdf_path),
        "title": title,
        "page_count": doc.page_count,
        "metadata": doc.metadata,
        "pages": pages,
    }


def write_markdown_preview(data: dict, output_path: Path) -> None:
    lines = []

    lines.append(f"# {data['title']}")
    lines.append("")
    lines.append(f"Source: `{data['source_file']}`")
    lines.append(f"Pages: {data['page_count']}")
    lines.append("")

    for page in data["pages"]:
        lines.append(f"## PDF Page {page['page']}")
        lines.append("")
        lines.append(page["text"] if page["text"] else "_No selectable text found on this page._")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! PDF extractor")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("--output-dir", default="data/output")

    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()
    output_root = Path(args.output_dir).resolve()
    output_dir = output_root / pdf_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    data = extract_pdf(pdf_path)

    json_path = output_dir / "pages.json"
    md_path = output_dir / "pages.md"

    json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    write_markdown_preview(data, md_path)

    print("Voila! PDF extracted successfully.")
    print(f"Input:  {pdf_path}")
    print(f"Output: {output_dir}")
    print(f"- {json_path}")
    print(f"- {md_path}")


if __name__ == "__main__":
    main()
