from pathlib import Path
import re

path = Path("services/api/ocr_tsv_columns_tesseract_pages.py")
text = path.read_text(encoding="utf-8")

# 1. Strengthen has_fig_marker
text = re.sub(
    r'def has_fig_marker\(value: str\) -> bool:[\s\S]*?\n\n(?=def is_noise_line)',
    r'''def has_fig_marker(value: str) -> bool:
    value = clean_leading_noise(value).lower()

    return bool(
        re.search(r"\bfig[\.\s]*[0-9ivxl]+", value)
        or re.search(r"\bfigura\s*[0-9ivxl]+", value)
        or re.search(r"\bvariația procentuală\b", value)
        or re.search(r"\bvariatia procentuala\b", value)
        or re.search(r"\blampa cu lumin[ăa] mixt", value)
    )


''',
    text,
    count=1,
)

# 2. Strengthen is_noise_line
text = re.sub(
    r'def is_noise_line\(value: str\) -> bool:[\s\S]*?\n\n(?=def words_bbox)',
    r'''def is_noise_line(value: str) -> bool:
    value = clean_leading_noise(value)
    lower = value.lower()

    if not value:
        return True

    if has_fig_marker(value):
        return True

    # Remove leaked TSV-like numeric sequences.
    if re.search(r"(?:\s+\d+(?:\.\d+)?){6,}", value):
        value_without_numbers = re.sub(r"(?:\s+\d+(?:\.\d+)?){6,}\s*", " ", value)
        letters_after = len(re.findall(rf"[{RO_LETTERS}]", value_without_numbers))
        if letters_after < 12:
            return True

    # Mostly punctuation / axes / graph labels.
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
        "the ii",
        "pan al",
        "fey",
        "ioe",
        "deea",
        "ft",
        "tan",
    ]

    if any(token in lower for token in bad_tokens):
        return True

    legend_words = [
        "balonul",
        "filamentul",
        "electrodul",
        "suportul",
        "soclu",
        "tubul",
        "tubului",
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

    if any(word in lower for word in legend_words) and len(value) < 160:
        return True

    letters = len(re.findall(rf"[{RO_LETTERS}]", value))
    digits = len(re.findall(r"\d", value))
    weird = len(re.findall(r"[|<>~`^_=◆◇□■\\]", value))
    chars = max(1, len(value))

    if letters < 4:
        return True

    if weird / chars > 0.16:
        return True

    if digits > letters * 2 and letters < 30:
        return True

    tokens = re.findall(rf"[{RO_LETTERS}0-9]+", value)
    if tokens:
        short_tokens = [token for token in tokens if len(token) <= 2]
        if len(tokens) <= 6 and len(short_tokens) >= max(3, len(tokens) - 1):
            return True

    return False


''',
    text,
    count=1,
)

# 3. Clean numeric TSV leaks inside line_text
text = re.sub(
    r'def line_text\(line: list\[dict\]\) -> str:[\s\S]*?\n\n(?=def page_words_to_text)',
    r'''def line_text(line: list[dict]) -> str:
    text = " ".join(w["text"] for w in sorted(line, key=lambda w: w["left"]))
    text = clean_leading_noise(text)

    # Remove leaked TSV numeric fields if they appear as OCR words.
    text = re.sub(r"(?:\s+\d+(?:\.\d+)?){6,}\s*", " ", text)

    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    text = re.sub(r"\s{2,}", " ", text)

    return normalize_line(text)


''',
    text,
    count=1,
)

path.write_text(text, encoding="utf-8")
print("OK: TSV column OCR v5 cleanup filter applied.")
