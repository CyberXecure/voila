from __future__ import annotations

import argparse
import json
from pathlib import Path


PAGE_HEADER_TITLES = {
    "opening section",
    "valves and pipelines",
}


def get_lesson_text(lesson: dict) -> str:
    return str(lesson.get("text_preview", "") or "")


def infer_title_from_lesson(lesson: dict) -> str | None:
    text = get_lesson_text(lesson).lower()
    figures = lesson.get("figures") or []

    if "pumping trap" in text:
        return "Automatic Pumping or Vacuum Trap"

    if "non-return valve" in text and "float" in text and "steam valve" in text:
        return "Automatic Pumping or Vacuum Trap"

    for figure in figures:
        number = str(figure.get("number", "")).strip()
        caption = str(figure.get("caption", "")).strip()
        caption_lower = caption.lower()

        if number == "4.23":
            return "Automatic Pumping or Vacuum Trap"

        if "pumping" in caption_lower and "trap" in caption_lower:
            return "Automatic Pumping or Vacuum Trap"

        if caption and len(caption.split()) <= 8:
            return caption[:1].upper() + caption[1:]

    return None


def figure_key(figure: dict) -> str:
    return f"{figure.get('number')}::{figure.get('caption')}"


def move_figure_423_to_pumping_lesson(lessons: list[dict]) -> None:
    pumping_lesson = None
    maintenance_lesson = None

    for lesson in lessons:
        title = str(lesson.get("title", "")).lower()

        if "automatic pumping" in title or "vacuum trap" in title:
            pumping_lesson = lesson

        if "maintenance of traps" in title:
            maintenance_lesson = lesson

    if not pumping_lesson or not maintenance_lesson:
        return

    maintenance_figures = maintenance_lesson.get("figures") or []
    pumping_figures = pumping_lesson.get("figures") or []

    moved = []
    kept = []

    for figure in maintenance_figures:
        number = str(figure.get("number", "")).strip()
        caption = str(figure.get("caption", "")).lower()

        if number == "4.23" or ("pumping" in caption and "trap" in caption):
            moved.append(figure)
        else:
            kept.append(figure)

    existing = {figure_key(fig) for fig in pumping_figures}

    for figure in moved:
        if figure_key(figure) not in existing:
            pumping_figures.append(figure)

    pumping_lesson["figures"] = pumping_figures
    maintenance_lesson["figures"] = kept


def normalize_outline(outline: dict) -> dict:
    normalized_lessons = []

    for lesson in outline.get("lessons", []):
        title = str(lesson.get("title", "")).strip()
        title_key = title.lower()
        word_count = int(lesson.get("word_count") or 0)

        if word_count < 20:
            continue

        if title_key in PAGE_HEADER_TITLES:
            inferred_title = infer_title_from_lesson(lesson)

            if inferred_title:
                lesson["title"] = inferred_title
            else:
                continue

        normalized_lessons.append(lesson)

    move_figure_423_to_pumping_lesson(normalized_lessons)

    for index, lesson in enumerate(normalized_lessons, start=1):
        lesson["lesson_id"] = f"L{index:03d}"

    outline["lessons"] = normalized_lessons
    outline["outline_method"] = "heuristic_v0.1_normalized_keep_pumping_trap"
    outline["normalization"] = {
        "removed_low_word_count_sections": True,
        "removed_empty_page_header_titles": True,
        "kept_inferred_pumping_trap_section": True,
        "moved_figure_423_to_pumping_lesson": True,
        "renumbered_lessons": True,
        "ai_generation": False,
        "translation": False
    }

    return outline


def write_markdown(outline: dict, output_path: Path) -> None:
    lines = []

    lines.append(f"# {outline.get('title')}")
    lines.append("")
    lines.append("Mode: source language, no translation, no AI generation")
    lines.append(f"Source: `{outline.get('source_file')}`")
    lines.append("")

    for lesson in outline.get("lessons", []):
        lines.append(f"## {lesson['lesson_id']} — {lesson['title']}")
        lines.append("")
        lines.append(f"PDF pages: {', '.join(map(str, lesson.get('source_pdf_pages', [])))}")
        lines.append(f"Word count: {lesson.get('word_count')}")
        lines.append("")

        figures = lesson.get("figures") or []

        if figures:
            lines.append("Figures:")
            for figure in figures:
                lines.append(f"- Figure {figure.get('number')}: {figure.get('caption')}")
            lines.append("")

        lines.append("Preview:")
        lines.append("")
        preview = str(lesson.get("text_preview", "")).strip()
        lines.append("> " + preview.replace("\n", "\n> "))
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! outline normalizer")
    parser.add_argument("course_outline_json", help="Path to course_outline.json")

    args = parser.parse_args()

    input_path = Path(args.course_outline_json).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"course_outline.json not found: {input_path}")

    outline = json.loads(input_path.read_text(encoding="utf-8"))
    normalized = normalize_outline(outline)

    json_path = input_path.parent / "course_outline.normalized.json"
    md_path = input_path.parent / "course_outline.normalized.md"

    json_path.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    write_markdown(normalized, md_path)

    print("Voila! normalized outline generated successfully.")
    print(f"- {json_path}")
    print(f"- {md_path}")


if __name__ == "__main__":
    main()
