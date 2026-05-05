from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


OCR_FIXES = {
    "Arajses": "raises",
    "dosed": "closed",
    "Stearn": "Steam",
    "dick": "click",
    "deaning": "cleaning",
    "dean": "clean",
    "dosing": "closing",
    "Ftgure": "Figure",
    "Fig11re": "Figure",
    "\\lalves": "Valves",
    "Auto-Ktean": "Auto-Klean",
    "lhin": "thin",
    "am.1.rnber": "a number",
    "f alll o": "fall to",
    "steam1": "steam",
    "ifnecessary": "if necessary",
    "inthe": "in the",
    "onthe": "on the",
    "thetrap": "the trap",
    "level ofthe": "level of the",
    "tum": "turn",
    "Roy/es": "Royles",
    "projected .into": "projected into",
    "The float. falls": "The float falls",
}

VISUAL_NOISE_LINES = {
    "0",
    "8",
    "O",
    "C",
    "D",
    "--E",
    "B",
    "A",
    "J",
    "G",
    "Wire mesh cartridge",
    "filter",
    "Detail of",
    "cartridge",
    "Stout wire",
    "formers",
    "Fine",
    "gauze",
    "Fine gauze",
    "Air cock for venting",
    "not shown",
    "Twin",
    "cartridges",
    "Oil in",
    "Oil out",
    "Oil flow",
    "Ferrous matter",
    "trapped between",
    "gaps in segments",
    "Filter element",
    "dismantled for",
    "cleaning",
    "Permanent",
    "magnet",
    "Filter",
    "cage",
    "(iron)",
}


def apply_ocr_fixes(text: str) -> tuple[str, list[dict]]:
    corrections = []
    cleaned = text

    for wrong, right in OCR_FIXES.items():
        count = cleaned.count(wrong)
        if count:
            cleaned = cleaned.replace(wrong, right)
            corrections.append({"from": wrong, "to": right, "count": count})

    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip(), corrections


def is_page_header(line: str) -> bool:
    value = line.strip().lower()
    return (
        value == "valves and pipelines"
        or re.match(r"^\d{1,4}\s+valves and pipelines$", value) is not None
        or re.match(r"^valves and pipelines\s+\d{1,4}$", value) is not None
    )


def remove_noise_lines(text: str, lesson_title: str) -> str:
    title = lesson_title.strip().lower()
    output = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        lower = line.lower()

        if not line:
            output.append("")
            continue

        if is_page_header(line):
            continue

        if lower == title:
            continue

        output.append(raw_line)

    return "\n".join(output).strip()


def trim_automatic_trap_start(text: str) -> str:
    lines = text.splitlines()
    start_index = 0

    for index, line in enumerate(lines):
        lower = line.lower().strip()
        if lower.startswith("when the trap is empty"):
            start_index = index
            break
        if lower.startswith("a typical pumping trap is shown"):
            start_index = index
            break

    return "\n".join(lines[start_index:]).strip()


def remove_figure_423_block(text: str) -> str:
    lines = text.splitlines()
    output = []
    index = 0

    while index < len(lines):
        current = lines[index].strip()
        lookahead = "\n".join(lines[index:index + 28])

        starts_diagram_block = (
            current in {"C", "D", "--E", "B", "A", "J", "G"}
            and "Figure 4.23" in lookahead
        )

        starts_caption = current.startswith("Figure 4.23")

        if starts_diagram_block or starts_caption:
            while index < len(lines):
                if "J. Spindle" in lines[index]:
                    index += 1
                    break
                index += 1
            continue

        output.append(lines[index])
        index += 1

    return "\n".join(output).strip()


def is_visual_noise_line(line: str) -> bool:
    value = line.strip()

    if not value:
        return False

    if value in VISUAL_NOISE_LINES:
        return True

    if re.match(r"^[0O8\s]+$", value):
        return True

    if re.match(r"^Figure\s+\d+(?:\.\d+)?\b", value):
        return True

    return False


def is_caption_continuation(line: str) -> bool:
    value = line.strip()
    lower = value.lower()

    if not value:
        return False

    if lower.startswith(("service ", "and ", "or ", "separation ", "water ", "oil ")):
        return True

    if len(value) < 95 and not value.endswith((".", ";", ":")) and re.match(r"^[a-z]", value):
        return True

    return False


def remove_visual_noise(text: str) -> str:
    lines = text.splitlines()
    output = []
    skip_caption_continuation = 0

    for raw_line in lines:
        line = raw_line.strip()

        if skip_caption_continuation > 0 and is_caption_continuation(line):
            skip_caption_continuation -= 1
            continue

        if re.match(r"^Figure\s+\d+(?:\.\d+)?\b", line):
            skip_caption_continuation = 2
            continue

        if is_visual_noise_line(line):
            continue

        output.append(raw_line)

    cleaned = "\n".join(output)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def clean_lesson_text(lesson: dict) -> tuple[str, list[dict]]:
    title = str(lesson.get("title") or "")
    raw_text = str(lesson.get("source_text") or lesson.get("text_preview") or "").strip()

    fixed_text, corrections = apply_ocr_fixes(raw_text)
    fixed_text = remove_noise_lines(fixed_text, title)

    if "automatic pumping" in title.lower() or "vacuum trap" in title.lower():
        fixed_text = trim_automatic_trap_start(fixed_text)
    else:
        fixed_text = remove_figure_423_block(fixed_text)

    fixed_text = remove_visual_noise(fixed_text)
    fixed_text = re.sub(r"\n{3,}", "\n\n", fixed_text).strip()

    return fixed_text, corrections


def split_sentences(text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", text).strip()
    if not compact:
        return []
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", compact)
    return [part.strip() for part in parts if len(part.strip()) > 25]


def lesson_key(title: str) -> str:
    lower = title.lower()

    if "automatic pumping" in lower or "vacuum trap" in lower:
        return "automatic_pumping_trap"

    if "maintenance" in lower and "trap" in lower:
        return "maintenance_traps"

    if "strainer" in lower or "filter" in lower:
        return "strainers_filters"

    return "general"


def select_summary_points(lesson: dict, cleaned_text: str) -> list[str]:
    key = lesson_key(str(lesson.get("title") or ""))
    sentences = split_sentences(cleaned_text)

    if key == "automatic_pumping_trap":
        keywords = [
            "exhaust valve c is open",
            "non-return valve raises the float",
            "compresses the spring",
            "steam is therefore admitted",
            "drives out the water",
            "float falls",
            "cycle of operation",
            "float controlled",
        ]
    elif key == "maintenance_traps":
        keywords = [
            "defective trap wastes steam",
            "poor heater performance",
            "thermodynamic type",
            "strainer",
            "fine dirt",
            "pipe scale",
            "cleaning and reassembling",
            "mechanical traps",
            "thermostatic traps",
        ]
    elif key == "strainers_filters":
        keywords = [
            "strainer is sometimes used",
            "filters also describes",
            "simplest strainer",
            "strainer plates corrode",
            "basket strainers",
            "knife edge strainer",
            "cartridge filters",
            "magnetic filters",
        ]
    else:
        keywords = ["should", "must", "used", "installed", "consists", "checked"]

    selected = []

    for sentence in sentences:
        lower = sentence.lower()
        if any(keyword in lower for keyword in keywords):
            selected.append(sentence)
        if len(selected) >= 7:
            break

    return selected[:7] if selected else sentences[:5]


def select_maintenance_notes(lesson: dict, cleaned_text: str) -> list[str]:
    key = lesson_key(str(lesson.get("title") or ""))

    if key not in {"maintenance_traps", "strainers_filters"}:
        return []

    warning_words = [
        "defective",
        "wastes",
        "fails",
        "prevent",
        "damage",
        "blockage",
        "corrode",
        "erode",
        "renewed",
        "undue force",
        "clogging",
        "difficult",
        "waterlogging",
        "blow steam",
        "wire drawing",
    ]

    notes = []

    for sentence in split_sentences(cleaned_text):
        lower = sentence.lower()
        if any(word in lower for word in warning_words):
            notes.append(sentence)
        if len(notes) >= 6:
            break

    return notes


def make_review_questions(lesson: dict) -> list[str]:
    key = lesson_key(str(lesson.get("title") or ""))

    if key == "automatic_pumping_trap":
        return [
            "What is the position of the exhaust valve and steam valve when the trap is empty?",
            "What causes the float to rise inside the trap?",
            "What happens when steam is admitted to the trap?",
            "Why does the trap operate only when water is flowing into it?",
        ]

    if key == "maintenance_traps":
        return [
            "What can a defective steam trap cause?",
            "Why should the inlet strainer be checked before inspecting a trap?",
            "How can a thermodynamic trap be checked during operation?",
            "What should be checked on mechanical traps?",
            "What problems can incorrect adjustment of bimetallic steam traps cause?",
        ]

    if key == "strainers_filters":
        return [
            "How does the source distinguish between a strainer and a filter?",
            "Where are simple flat-plate strainers found according to the source?",
            "Why should strainer plates be inspected during cleaning?",
            "How does a knife edge strainer remove trapped particles?",
            "What extra protection do magnetic filters provide?",
        ]

    return [
        "What is the main topic of this lesson?",
        "Which source pages support this lesson?",
    ]


def write_clean_course(outline: dict, output_path: Path) -> list[dict]:
    lines = []
    all_corrections = []

    lines.append(f"# {outline.get('title')}")
    lines.append("")
    lines.append("Generated by Voila! v0.1.2")
    lines.append("")
    lines.append("Mode: source language, no translation, no AI generation")
    lines.append("Text status: OCR-cleaned reading text; original source preserved in pages.md/pages.json")
    lines.append(f"Source: `{outline.get('source_file')}`")
    lines.append("")

    for lesson in outline.get("lessons", []):
        lesson_id = lesson.get("lesson_id")
        title = lesson.get("title")
        pages = lesson.get("source_pdf_pages", [])

        cleaned_text, corrections = clean_lesson_text(lesson)

        for correction in corrections:
            correction["lesson_id"] = lesson_id
            correction["lesson_title"] = title
            correction["source_pdf_pages"] = pages
            all_corrections.append(correction)

        summary_points = select_summary_points(lesson, cleaned_text)
        maintenance_notes = select_maintenance_notes(lesson, cleaned_text)
        questions = make_review_questions(lesson)

        lines.append(f"## {lesson_id} — {title}")
        lines.append("")
        lines.append(f"Source PDF pages: {', '.join(map(str, pages))}")
        lines.append(f"Word count: {lesson.get('word_count')}")
        lines.append("")

        figures = lesson.get("figures") or []

        if figures:
            lines.append("### Figures")
            lines.append("")
            for figure in figures:
                lines.append(f"- Figure {figure.get('number')}: {figure.get('caption')}")
            lines.append("")

        lines.append("### Lesson summary")
        lines.append("")
        for point in summary_points:
            lines.append(f"- {point}")
        lines.append("")

        if maintenance_notes:
            lines.append("### Maintenance / safety notes")
            lines.append("")
            for note in maintenance_notes:
                lines.append(f"- {note}")
            lines.append("")

        lines.append("### Review questions")
        lines.append("")
        for index, question in enumerate(questions, start=1):
            lines.append(f"{index}. {question}")
        lines.append("")

        lines.append("### Cleaned source text")
        lines.append("")
        lines.append("```text")
        lines.append(cleaned_text)
        lines.append("```")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return all_corrections


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! course polisher")
    parser.add_argument("normalized_outline_json", help="Path to course_outline.normalized.json")

    args = parser.parse_args()
    outline_path = Path(args.normalized_outline_json).resolve()

    if not outline_path.exists():
        raise FileNotFoundError(f"Normalized outline not found: {outline_path}")

    outline = json.loads(outline_path.read_text(encoding="utf-8"))
    output_dir = outline_path.parent

    clean_course_path = output_dir / "course.cleaned.md"
    corrections_path = output_dir / "ocr_corrections.json"

    corrections = write_clean_course(outline, clean_course_path)

    corrections_path.write_text(
        json.dumps(corrections, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Voila! polished course generated successfully.")
    print(f"- {clean_course_path}")
    print(f"- {corrections_path}")
    print(f"OCR corrections applied: {len(corrections)}")


if __name__ == "__main__":
    main()
