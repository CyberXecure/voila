from __future__ import annotations

import argparse
import re
from pathlib import Path


VISUAL_LINES = {
    "0",
    "8",
    "O",
    "Figure 4.25",
    "Figure 4.26",
    "Figure 4.27",
    "Cartridge filters",
    "Magnetic filter",
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
    "Permanent",
    "magnet",
    "Filter",
    "cage",
    "(iron)",
}


def is_visual_noise(line: str) -> bool:
    value = line.strip()

    if not value:
        return False

    if value in VISUAL_LINES:
        return True

    if re.match(r"^[0O8\s]+$", value):
        return True

    if value.startswith("~") and "cage" in value:
        return True

    if value.startswith("The Auto-Klean strainer showing"):
        return True

    if value.startswith("separation washers and spider"):
        return True

    if value.startswith("Ferrous matter"):
        return True

    if value.startswith("trapped between"):
        return True

    if value.startswith("gaps in segments"):
        return True

    if value.startswith("Filter element"):
        return True

    if value.startswith("dismantled for"):
        return True

    return False


def clean_code_block(text: str) -> str:
    lines = text.splitlines()
    output = []
    stop = False

    for raw_line in lines:
        line = raw_line.strip()

        if line == "Further reading":
            stop = True
            continue

        if stop:
            continue

        if is_visual_noise(line):
            continue

        line = line.replace("sizes others are made up", "Cartridges can be of gauze layers with different mesh sizes; others are made up")

        output.append(line)

    cleaned = "\n".join(output)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()


def finalize_markdown(markdown: str) -> str:
    parts = markdown.split("```text")

    if len(parts) == 1:
        return markdown

    final = [parts[0]]

    for part in parts[1:]:
        if "```" not in part:
            final.append("```text" + part)
            continue

        code, rest = part.split("```", 1)
        cleaned_code = clean_code_block(code.strip())

        final.append("```text\n")
        final.append(cleaned_code)
        final.append("\n```")
        final.append(rest)

    return "".join(final)


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! final cleanup for cleaned course Markdown")
    parser.add_argument("course_cleaned_md", help="Path to course.cleaned.md")

    args = parser.parse_args()

    path = Path(args.course_cleaned_md).resolve()

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    original = path.read_text(encoding="utf-8")
    finalized = finalize_markdown(original)

    backup_path = path.with_suffix(".md.bak")
    backup_path.write_text(original, encoding="utf-8")
    path.write_text(finalized, encoding="utf-8")

    print("Voila! final cleaned text applied.")
    print(f"- Updated: {path}")
    print(f"- Backup:  {backup_path}")


if __name__ == "__main__":
    main()
