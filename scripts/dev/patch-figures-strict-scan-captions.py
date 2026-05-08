from pathlib import Path

path = Path("services/api/figure_exporter_visual_fallback.py")
text = path.read_text(encoding="utf-8")

# Make page_has_figure_caption strict.
start = text.find("def page_has_figure_caption(")
end = text.find("\n\ndef ", start + 1)

if start == -1:
    raise SystemExit("page_has_figure_caption function not found")

if end == -1:
    end = text.find("\n\n", start + 1)

replacement = r'''def page_has_figure_caption(page_text: str) -> bool:
    text = page_text or ""
    lower = text.lower()

    # Never treat table of contents / index pages as figure pages.
    if "cuprins" in lower:
        return False

    if "bibliografie" in lower:
        return False

    if "index" in lower and len(text) > 500:
        return False

    # For scanned PDFs, accept only explicit figure captions.
    patterns = [
        r"(?im)^\s*(?:fig\.|figura)\s*[IVXLCDM0-9]+(?:[.\-]\d+)*",
        r"(?im)\b(?:fig\.|figura)\s*[IVXLCDM0-9]+(?:[.\-]\d+)*",
    ]

    return any(re.search(pattern, text) for pattern in patterns)
'''

text = text[:start] + replacement + text[end:]

# Make extract_possible_caption strict too.
start = text.find("def extract_possible_caption(")
end = text.find("\n\ndef ", start + 1)

if start == -1:
    raise SystemExit("extract_possible_caption function not found")

replacement = r'''def extract_possible_caption(page_text: str, page_no: int, index: int) -> tuple[str, str]:
    patterns = [
        r"(?im)^\s*(?:fig\.|figura|figure)\s*([IVXLCDM0-9]+(?:[.\-][0-9]+)*)\.?\s+(.{3,180})$",
        r"(?im)\b(?:fig\.|figura|figure)\s*([IVXLCDM0-9]+(?:[.\-][0-9]+)*)\.?\s+(.{3,180})",
    ]

    matches = []

    for pattern in patterns:
        matches.extend(re.findall(pattern, page_text or ""))

    if matches:
        number, caption = matches[min(index, len(matches) - 1)]
        caption = re.sub(r"\s+", " ", caption).strip(" .:-")
        return number.strip(), caption[:180]

    number = f"p{page_no}.{index + 1}"
    caption = f"Visual figure candidate from PDF page {page_no}"
    return number, caption
'''

text = text[:start] + replacement + text[end:]

path.write_text(text, encoding="utf-8")

print("OK: visual fallback now rejects cuprins/index pages and requires Fig./Figura captions.")
