from pathlib import Path
import re

path = Path("services/api/figure_exporter_hybrid.py")
text = path.read_text(encoding="utf-8")

# 1. Add caption cleaner after normalize_text()
needle = '''def normalize_text(text: str) -> str:
    text = text.replace("Ftgure", "Figure")
    text = text.replace("Fig11re", "Figure")
    text = re.sub(r"\\s+", " ", text)
    return text.strip()
'''

insert = '''def normalize_text(text: str) -> str:
    text = text.replace("Ftgure", "Figure")
    text = text.replace("Fig11re", "Figure")
    text = re.sub(r"\\s+", " ", text)
    return text.strip()


def clean_caption(caption: str) -> str:
    caption = normalize_text(caption).strip(" .,-")

    # Some PDFs merge the real caption with the next paragraph.
    # These markers usually indicate that body text started after the caption.
    cut_markers = [
        " With a ",
        " With an ",
        " With the ",
        " This ",
        " These ",
        " In this ",
        " difficult to calculate ",
    ]

    for marker in cut_markers:
        if marker in caption and len(caption.split()) > 12:
            caption = caption.split(marker, 1)[0].strip(" .,-")
            break

    return caption
'''

if needle not in text:
    raise SystemExit("normalize_text block not found. Patch not applied.")

text = text.replace(needle, insert)

# 2. Clean caption before it is stored
text = text.replace(
    '''        captions.append(
            {
                "number": number,
                "caption": caption.strip(" .,-"),
                "bbox": [bbox.x0, bbox.y0, bbox.x1, bbox.y1],
                "y_pct": bbox.y0 / page.rect.height if page.rect.height else 0,
            }
        )
''',
    '''        captions.append(
            {
                "number": number,
                "caption": clean_caption(caption),
                "bbox": [bbox.x0, bbox.y0, bbox.x1, bbox.y1],
                "y_pct": bbox.y0 / page.rect.height if page.rect.height else 0,
            }
        )
'''
)

# 3. Replace make_crop_rect with asymmetric margins
pattern = r'''def make_crop_rect\(page: fitz\.Page, caption: dict, candidate: dict \| None\) -> tuple\[fitz\.Rect, str\]:
.*?
    return rect, method
'''

replacement = '''def make_crop_rect(page: fitz.Page, caption: dict, candidate: dict | None) -> tuple[fitz.Rect, str]:
    cap = fitz.Rect(caption["bbox"])

    # Wider horizontal margin helps embedded diagrams that are close to the page edge.
    margin_x = page.rect.width * 0.045

    # Asymmetric vertical margins:
    # - enough top margin for labels above the drawing
    # - small bottom margin to avoid pulling the paragraph after the caption
    cap_y_pct = cap.y0 / page.rect.height if page.rect.height else 0

    margin_top = page.rect.height * 0.030

    if cap_y_pct < 0.25:
        # Caption near top, figure likely below.
        margin_bottom = page.rect.height * 0.030
    else:
        # Caption below figure; avoid grabbing following paragraph.
        margin_bottom = page.rect.height * 0.010

    if candidate:
        rect = fitz.Rect(candidate["rect"])
        rect |= cap
        method = candidate["kind"]
    else:
        rect = fallback_rect(page, caption)
        method = "fallback_caption_window"

    rect = fitz.Rect(
        max(0, rect.x0 - margin_x),
        max(0, rect.y0 - margin_top),
        min(page.rect.width, rect.x1 + margin_x),
        min(page.rect.height, rect.y1 + margin_bottom),
    )

    if rect.is_empty:
        rect = fallback_rect(page, caption)
        method = "fallback_after_invalid_rect"

    return rect, method
'''

text2 = re.sub(pattern, replacement, text, flags=re.DOTALL)

if text2 == text:
    raise SystemExit("make_crop_rect block not found. Patch not applied.")

path.write_text(text2, encoding="utf-8")

print("OK: hybrid extractor patched to v2: cleaner captions + better crop margins.")
