from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def clean_line(line: str) -> str:
    line = line.replace("\x00", " ").strip()
    line = line.replace("Ftgure", "Figure")
    line = line.replace("Fig11re", "Figure")
    line = line.replace("\\lalves", "Valves")
    line = re.sub(r"[ \t]+", " ", line)
    return line.strip()


def is_page_header(line: str) -> bool:
    lower = line.lower()

    if "valves and pipelines" in lower and re.search(r"\d{1,4}", line):
        return True

    if re.match(r"^\d{1,4}\s+[A-Z][A-Za-z ,&-]{3,60}$", line):
        return True

    if re.match(r"^[A-Z][A-Za-z ,&-]{3,60}\s+\d{1,4}$", line):
        return True

    return False


def is_heading(line: str, next_line: str) -> bool:
    if not line:
        return False

    if is_page_header(line):
        return False

    lower = line.lower()

    if lower in {"further reading", "references", "bibliography"}:
        return False

    if "figure" in lower:
        return False

    if len(line) < 4 or len(line) > 80:
        return False

    if len(line.split()) > 8:
        return False

    if re.search(r"\d", line):
        return False

    if line.endswith((".", ",", ";", ":")):
        return False

    if not re.match(r"^[A-Z]", line):
        return False

    if len(next_line) < 40:
        return False

    return True


def extract_figures(text: str) -> list[dict]:
    figures = []

    for match in re.finditer(
        r"\bFigure\s+([0-9]+(?:\.[0-9]+)?)\s+(.+)",
        text,
        flags=re.IGNORECASE,
    ):
        caption = match.group(2).strip()
        caption = re.sub(r"\([^)]*\)", "", caption)
        caption = re.sub(r"\s+", " ", caption).strip(" .,-")

        figures.append(
            {
                "number": match.group(1),
                "caption": caption,
            }
        )

    return figures


def build_line_items(data: dict) -> list[dict]:
    items = []

    for page in data.get("pages", []):
        pdf_page = page.get("page")
        text = page.get("text", "") or ""

        for raw_line in text.splitlines():
            line = clean_line(raw_line)

            if line:
                items.append(
                    {
                        "line": line,
                        "pdf_page": pdf_page,
                    }
                )

    return items


def make_lesson(lesson_id: int, title: str, items: list[dict]) -> dict:
    clean_items = [
        item for item in items
        if item["line"] and not is_page_header(item["line"])
    ]

    text = "\n".join(item["line"] for item in clean_items).strip()

    return {
        "lesson_id": f"L{lesson_id:03d}",
        "title": title,
        "source_pdf_pages": sorted(set(item["pdf_page"] for item in clean_items)),
        "word_count": len(text.split()),
        "figures": extract_figures(text),
        "source_text": text,
        "text_preview": text[:800],
        "status": "outline_only_no_ai",
    }


def build_outline(data: dict) -> dict:
    items = build_line_items(data)

    lessons = []
    current_title = "Opening Section"
    buffer = []
    lesson_id = 1

    for index, item in enumerate(items):
        line = item["line"]
        next_line = items[index + 1]["line"] if index + 1 < len(items) else ""

        if is_heading(line, next_line):
            if buffer:
                lessons.append(make_lesson(lesson_id, current_title, buffer))
                lesson_id += 1

            current_title = line
            buffer = [item]
        else:
            buffer.append(item)

    if buffer:
        lessons.append(make_lesson(lesson_id, current_title, buffer))

    return {
        "title": data.get("title") or "Untitled course",
        "source_file": data.get("source_file"),
        "source_page_count": data.get("page_count"),
        "mode": {
            "course_language": "source",
            "translate": False,
            "ai_generation": False,
        },
        "outline_method": "heuristic_v0.1",
        "lessons": lessons,
    }


def write_markdown(outline: dict, output_path: Path) -> None:
    lines = []

    lines.append(f"# {outline['title']}")
    lines.append("")
    lines.append("Mode: source language, no translation, no AI generation")
    lines.append(f"Source: `{outline.get('source_file')}`")
    lines.append("")

    for lesson in outline["lessons"]:
        lines.append(f"## {lesson['lesson_id']} — {lesson['title']}")
        lines.append("")
        lines.append(f"PDF pages: {', '.join(map(str, lesson['source_pdf_pages']))}")
        lines.append(f"Word count: {lesson['word_count']}")
        lines.append("")

        if lesson["figures"]:
            lines.append("Figures:")

            for figure in lesson["figures"]:
                lines.append(f"- Figure {figure['number']}: {figure['caption']}")

            lines.append("")

        lines.append("Preview:")
        lines.append("")
        lines.append("> " + lesson["text_preview"].replace("\n", "\n> "))
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! outline builder")
    parser.add_argument("pages_json", help="Path to pages.json")

    args = parser.parse_args()

    pages_json = Path(args.pages_json).resolve()

    if not pages_json.exists():
        raise FileNotFoundError(f"pages.json not found: {pages_json}")

    data = json.loads(pages_json.read_text(encoding="utf-8"))
    outline = build_outline(data)

    json_path = pages_json.parent / "course_outline.json"
    md_path = pages_json.parent / "course_outline.md"

    json_path.write_text(
        json.dumps(outline, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    write_markdown(outline, md_path)

    print("Voila! course outline generated successfully.")
    print(f"- {json_path}")
    print(f"- {md_path}")


if __name__ == "__main__":
    main()

