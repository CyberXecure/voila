from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


RO_LETTERS = "A-Za-zĂÂÎȘȚăâîșț"


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


def is_caption_or_legend(value: str) -> bool:
    value = clean_leading_noise(value)
    lower = value.lower()

    if has_fig_marker(value):
        return True

    legend_words = [
        "balonul",
        "filamentul",
        "electrodul",
        "suportul",
        "soclu",
        "tubul",
        "tubului",
        "descărcare",
        "descarcare",
        "intrare curent",
        "înveliș",
        "invelis",
        "dispozitiv",
        "vidului",
        "intensitatea",
        "puterea",
        "fluxul luminos",
        "tensiunea",
    ]

    if any(word in lower for word in legend_words):
        # Nu eliminăm orice linie cu „descărcare”; eliminăm doar liniile scurte de legendă.
        if len(value) < 130 or re.match(r"^[0-9a-z]\s*[-–]", lower):
            return True

    if re.match(r"^[0-9a-z]\s*[-–]\s*", lower):
        return True

    return False


def is_graph_noise(value: str) -> bool:
    value = clean_leading_noise(value)
    lower = value.lower()

    if not value:
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
        "for",
        "pan al",
        "the ii",
    ]

    if any(token in lower for token in bad_tokens):
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

    tokens = re.findall(rf"[{RO_LETTERS}0-9]+", value)

    if tokens:
        short_tokens = [token for token in tokens if len(token) <= 2]
        if len(tokens) <= 5 and len(short_tokens) >= max(2, len(tokens) - 1):
            return True

    return False


def clean_text(text: str) -> str:
    raw_lines = [normalize_line(line) for line in str(text or "").splitlines()]
    raw_lines = [line for line in raw_lines if line]

    cleaned = []
    skip = 0

    for raw in raw_lines:
        line = clean_leading_noise(raw)

        if not line:
            continue

        if has_fig_marker(line):
            skip = 10
            continue

        if skip > 0:
            if is_caption_or_legend(line) or is_graph_noise(line) or len(line) < 120:
                skip -= 1
                continue
            skip = 0

        if is_caption_or_legend(line):
            continue

        if is_graph_noise(line):
            continue

        # Curățări ușoare, fără să inventăm text.
        line = re.sub(r"^\>\s*", "", line)
        line = re.sub(r"^_+", "", line)
        line = re.sub(r"\s+\|$", "", line)
        line = normalize_line(line)

        if line:
            cleaned.append(line)

    # Unește despărțiri cu cratimă la capăt de rând.
    merged = []

    for line in cleaned:
        if merged and merged[-1].endswith("-"):
            merged[-1] = merged[-1][:-1] + line
        else:
            merged.append(line)

    return "\n".join(merged).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila OCR post-cleaner")

    parser.add_argument("input_json")
    parser.add_argument("--output-json", default="")
    parser.add_argument("--output-md", default="")
    parser.add_argument("--replace", action="store_true")

    args = parser.parse_args()

    input_path = Path(args.input_json)

    payload = json.loads(input_path.read_text(encoding="utf-8"))

    pages = payload.get("pages", [])

    before_chars = 0
    after_chars = 0

    for page in pages:
        old = str(page.get("text") or "")
        new = clean_text(old)

        before_chars += len(old)
        after_chars += len(new)

        page["text_before_post_clean_chars"] = len(old)
        page["text"] = new
        page["text_source"] = str(page.get("text_source") or "") + "+post_clean_v1"

    if args.replace:
        backup = input_path.with_name(input_path.name + ".before_post_clean")
        if not backup.exists():
            backup.write_text(
                input_path.read_text(encoding="utf-8", errors="ignore"),
                encoding="utf-8",
            )

        output_json = input_path
    else:
        output_json = Path(args.output_json) if args.output_json else input_path.with_name(input_path.stem + ".post_clean.json")

    output_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    output_md = Path(args.output_md) if args.output_md else output_json.with_suffix(".md")

    lines = [
        "# OCR post-cleaned pages",
        "",
        f"Source: {input_path}",
        "",
    ]

    for page in pages:
        lines.append(f"## Page {page.get('page_number')}")
        lines.append("")
        lines.append(str(page.get("text") or "").strip())
        lines.append("")

    output_md.write_text("\n".join(lines), encoding="utf-8")

    print("Voila OCR post-clean complete.")
    print("Input:", input_path)
    print("Output JSON:", output_json)
    print("Output MD:", output_md)
    print("Chars before:", before_chars)
    print("Chars after:", after_chars)


if __name__ == "__main__":
    main()
