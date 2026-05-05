from pathlib import Path

path = Path("services/api/figure_exporter_auto.py")
text = path.read_text(encoding="utf-8")

text = text.replace(
'''CAPTION_RE = re.compile(
    r"^\\s*(?:Figure|Fig\\.?|FIGURE|FIG\\.?)\\s+([0-9]+(?:[.\\-][0-9A-Za-z]+)*)\\s*[:.\\-]?\\s*(.*)$",
    re.IGNORECASE,
)
''',
'''CAPTION_RE = re.compile(
    r"^\\s*(?:Figure|Fig\\.?|FIGURE|FIG\\.?)\\s+([0-9]+(?:[.\\-][0-9A-Za-z]+)*)\\s*[:.\\-]?\\s*(.*)$",
    re.IGNORECASE,
)

BAD_CAPTION_STARTS = (
    "shows ",
    "show ",
    "illustrates ",
    "illustrate ",
    "is ",
    "are ",
    "was ",
    "were ",
    "gives ",
    "give ",
    "describes ",
    "describe ",
    "contains ",
    "contain ",
    "indicates ",
    "indicate ",
    "represents ",
    "represent ",
)
'''
)

text = text.replace(
'''        number = match.group(1)
        caption = normalize_text(match.group(2))
        bbox = fitz.Rect(item["bbox"])
''',
'''        number = match.group(1)
        caption = normalize_text(match.group(2))
        caption_lower = caption.lower()

        # Ignore inline references such as:
        # "Figure 1.6 shows the sequence..."
        if caption_lower.startswith(BAD_CAPTION_STARTS):
            continue

        # Long prose after "Figure X.Y" is usually an inline reference, not a real caption.
        if len(caption.split()) > 18:
            continue

        bbox = fitz.Rect(item["bbox"])
'''
)

text = text.replace(
'''    if y_pct < 0.28:
        y0 = bbox.y0 - height * 0.035
        y1 = bbox.y1 + height * 0.34
''',
'''    if y_pct < 0.28:
        y0 = bbox.y0 - height * 0.035
        y1 = bbox.y1 + height * 0.58
'''
)

text = text.replace(
'''    if y1 <= y0:
        y0 = clamp(bbox.y0 - height * 0.25, 0, height)
        y1 = clamp(bbox.y1 + height * 0.08, 0, height)
''',
'''    min_height = height * 0.22

    if y1 <= y0:
        y0 = clamp(bbox.y0 - height * 0.25, 0, height)
        y1 = clamp(bbox.y1 + height * 0.08, 0, height)

    if (y1 - y0) < min_height:
        center = (y0 + y1) / 2
        y0 = clamp(center - min_height / 2, 0, height)
        y1 = clamp(center + min_height / 2, 0, height)
'''
)

path.write_text(text, encoding="utf-8")
print("OK: figure_exporter_auto.py patched to v2.")
