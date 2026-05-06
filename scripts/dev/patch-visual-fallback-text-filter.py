from pathlib import Path

path = Path("services/api/figure_exporter_visual_fallback.py")
text = path.read_text(encoding="utf-8")

helper = r'''

def crop_text_word_count(page: fitz.Page, rect_points: list[float]) -> int:
    try:
        rect = fitz.Rect(rect_points)
        value = page.get_textbox(rect) or ""
    except Exception:
        return 0

    words = re.findall(r"[A-Za-zĂÂÎȘȚăâîșț0-9]{2,}", value)
    return len(words)


def crop_is_text_heavy(page: fitz.Page, rect_points: list[float], crop_area_ratio: float) -> bool:
    words = crop_text_word_count(page, rect_points)

    # Paragraphs, table-of-contents blocks, lists, and page text should not become figures.
    if words >= 25:
        return True

    # Smaller blocks with enough text are usually headings / lists, not figures.
    if crop_area_ratio < 0.28 and words >= 16:
        return True

    return False

'''

if "def crop_text_word_count" not in text:
    text = text.replace("def write_html(figures_dir: Path, pdf_path: Path, items: list[dict], page_from: int, page_to: int) -> None:", helper + "\n\ndef write_html(figures_dir: Path, pdf_path: Path, items: list[dict], page_from: int, page_to: int) -> None:")

old = '''            crop = image.crop((x0, y0, x1, y1))
            crop.save(out_path)

            # Convert pixel crop to PDF-point approximate crop.
            crop_rect = [
                x0 / args.zoom,
                y0 / args.zoom,
                x1 / args.zoom,
                y1 / args.zoom,
            ]

            items.append(
'''

new = '''            # Convert pixel crop to PDF-point approximate crop.
            crop_rect = [
                x0 / args.zoom,
                y0 / args.zoom,
                x1 / args.zoom,
                y1 / args.zoom,
            ]

            crop_area_ratio = ((x1 - x0) * (y1 - y0)) / max(1, image.width * image.height)

            if crop_is_text_heavy(page, crop_rect, crop_area_ratio):
                print(f"Skip text-heavy visual block: page {page_no}, words={crop_text_word_count(page, crop_rect)}")
                continue

            crop = image.crop((x0, y0, x1, y1))
            crop.save(out_path)

            items.append(
'''

if old not in text:
    raise SystemExit("Target crop-save block not found. Patch not applied.")

text = text.replace(old, new)

text = text.replace(
    '"version": "visual_fallback_v0.1"',
    '"version": "visual_fallback_v0.2_text_filtered"'
)

path.write_text(text, encoding="utf-8")

print("OK: visual fallback now skips text-heavy crops.")
