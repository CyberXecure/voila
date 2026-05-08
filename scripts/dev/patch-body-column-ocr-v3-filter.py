from pathlib import Path
import re

path = Path("services/api/ocr_body_columns_tesseract_pages.py")
text = path.read_text(encoding="utf-8")

# Replace caption/noise helpers and plain body filtering with stricter v3 logic.

pattern = r'def is_caption_start\(line: str\) -> bool:[\s\S]*?\n\n(?=def looks_like_body_line)'
replacement = r'''def clean_leading_ocr_noise(value: str) -> str:
    value = normalize_line(value)
    value = re.sub(r"^[\s\|\]\[\(\)'\\"`´~:;.,_—–-]+", "", value)
    return value.strip()


def is_caption_start(line: str) -> bool:
    value = clean_leading_ocr_noise(line).lower()

    return bool(
        re.match(r"^(fig\.?|figura)\s*[0-9ivxl]+", value)
        or re.match(r"^(fig\.?|figura)\s*", value)
    )


def contains_caption_marker(line: str) -> bool:
    value = clean_leading_ocr_noise(line).lower()

    return bool(
        re.search(r"\bfig\.?\s*[0-9ivxl]+", value)
        or re.search(r"\bfigura\s*[0-9ivxl]+", value)
    )


def is_figure_legend_or_noise(line: str) -> bool:
    value = clean_leading_ocr_noise(line)
    lower = value.lower()

    if not value:
        return True

    if contains_caption_marker(value):
        return True

    if re.search(
        r"\b(balonul|filamentul|electrodul|suportul|soclu|tubul|tubului|"
        r"intrare curent|înveliș|invelis|dispozitiv|vidului|tensiunea|"
        r"puterea|fluxul luminos|intensitatea)\b",
        lower,
    ):
        return True

    # Common OCR garbage from graphs / axes / drawing labels.
    if re.search(r"\b(yo|wey|isu|sns|fires|wate|for|vv|pan)\b", lower):
        return True

    if re.match(r"^[\|\-—–_.,;:()\[\]{}<>/\\0-9\s%°]+$", value):
        return True

    if re.search(r"[|]{2,}|[_]{2,}|[=]{2,}", value):
        return True

    tokens = re.findall(rf"[{RO_LETTERS}0-9]+", value)
    if not tokens:
        return True

    short_tokens = [token for token in tokens if len(token) <= 2]
    if len(tokens) <= 5 and len(short_tokens) >= max(2, len(tokens) - 1):
        return True

    letters = len(re.findall(rf"[{RO_LETTERS}]", value))
    digits = len(re.findall(r"\d", value))
    weird = len(re.findall(r"[|<>~`^_=◆◇□■]", value))
    chars = max(1, len(value))

    if letters < 4:
        return True

    if weird / chars > 0.18:
        return True

    if digits > letters * 2 and letters < 20:
        return True

    return False


def clean_body_output_line(line: str) -> str:
    value = clean_leading_ocr_noise(line)

    # Remove leading orphan OCR characters before a real capitalized word.
    value = re.sub(r"^[a-z]\s+(?=[A-ZĂÂÎȘȚ])", "", value)

    # Remove repeated OCR fence marks.
    value = re.sub(r"^[\|\]\[]+\s*", "", value)
    value = re.sub(r"\s+[\|\]\[]+$", "", value)

    return normalize_line(value)

'''
text, count = re.subn(pattern, replacement, text)

if count != 1:
    raise SystemExit(f"Could not replace caption helper block. Replacements: {count}")


pattern = r'def looks_like_body_line\(line: str, conf: float\) -> bool:[\s\S]*?\n\n(?=def lines_to_text)'
replacement = r'''def looks_like_body_line(line: str, conf: float) -> bool:
    value = clean_body_output_line(line)

    if not value:
        return False

    if is_figure_legend_or_noise(value):
        return False

    letters = len(re.findall(rf"[{RO_LETTERS}]", value))
    digits = len(re.findall(r"\d", value))
    chars = max(1, len(value))

    if letters < 5:
        return False

    if digits > letters and letters < 16:
        return False

    if conf >= 0 and conf < 22 and letters < 22:
        return False

    return True

'''
text, count = re.subn(pattern, replacement, text)

if count != 1:
    raise SystemExit(f"Could not replace looks_like_body_line. Replacements: {count}")


pattern = r'def looks_like_plain_body_line\(line: str\) -> bool:[\s\S]*?\n\n(?=def plain_text_to_body_text)'
replacement = r'''def looks_like_plain_body_line(line: str) -> bool:
    value = clean_body_output_line(line)

    if not value:
        return False

    if is_figure_legend_or_noise(value):
        return False

    letters = len(re.findall(rf"[{RO_LETTERS}]", value))
    digits = len(re.findall(r"\d", value))
    chars = max(1, len(value))
    weird = len(re.findall(r"[|<>~`^_=◆◇□■]", value))

    if letters < 4:
        return False

    if weird / chars > 0.18:
        return False

    if digits > letters * 2 and letters < 20:
        return False

    return True

'''
text, count = re.subn(pattern, replacement, text)

if count != 1:
    raise SystemExit(f"Could not replace looks_like_plain_body_line. Replacements: {count}")


pattern = r'def plain_text_to_body_text\(raw: str\) -> str:[\s\S]*?\n\n(?=def ocr_image_text)'
replacement = r'''def plain_text_to_body_text(raw: str) -> str:
    lines = [clean_body_output_line(line) for line in str(raw or "").splitlines()]
    lines = [line for line in lines if line]

    kept = []
    caption_skip = 0

    for line in lines:
        lower = line.lower()

        if contains_caption_marker(line):
            caption_skip = 10
            continue

        if caption_skip > 0:
            # Skip caption continuations and legends after Fig.
            if (
                len(line) < 120
                or is_figure_legend_or_noise(line)
                or re.match(r"^\s*[0-9a-z]\s*[-–]", lower)
                or re.match(r"^\s*[0-9]+\s*[-–]", lower)
                or re.search(
                    r"\b(balonul|filamentul|electrodul|suportul|soclu|tubul|"
                    r"tubului|intrare curent|înveliș|invelis|dispozitiv|vidului)\b",
                    lower,
                )
            ):
                caption_skip -= 1
                continue

            caption_skip = 0

        if looks_like_plain_body_line(line):
            kept.append(line)

    out = []

    for line in kept:
        if out and out[-1].endswith("-"):
            out[-1] = out[-1][:-1] + line
        else:
            out.append(line)

    return "\n".join(out).strip()

'''
text, count = re.subn(pattern, replacement, text)

if count != 1:
    raise SystemExit(f"Could not replace plain_text_to_body_text. Replacements: {count}")


path.write_text(text, encoding="utf-8")
print("OK: body-column OCR v3 figure/caption filter applied.")
