from pathlib import Path

path = Path("services/api/figure_exporter_vision.py")
text = path.read_text(encoding="utf-8")

old = '''def build_text_mask(page: fitz.Page, image_shape: tuple[int, int], zoom: float, caption_rects: list[fitz.Rect]) -> np.ndarray:
    height, width = image_shape
    mask = np.zeros((height, width), dtype=np.uint8)

    caption_boxes = [fitz.Rect(box) for box in caption_rects]

    for item in get_text_lines(page):
        bbox = fitz.Rect(item["bbox"])

        is_caption = False
        for cap in caption_boxes:
            if bbox.intersects(cap):
                is_caption = True
                break

        if is_caption:
            continue

        x0, y0, x1, y1 = scale_rect(bbox, zoom)

        pad_x = int(3 * zoom)
        pad_y = int(2 * zoom)

        x0 = max(0, x0 - pad_x)
        y0 = max(0, y0 - pad_y)
        x1 = min(width, x1 + pad_x)
        y1 = min(height, y1 + pad_y)

        cv2.rectangle(mask, (x0, y0), (x1, y1), 255, thickness=-1)

    return mask
'''

new = '''def build_text_mask(page: fitz.Page, image_shape: tuple[int, int], zoom: float, caption_rects: list[fitz.Rect]) -> np.ndarray:
    height, width = image_shape
    mask = np.zeros((height, width), dtype=np.uint8)

    # Important:
    # Caption text is also masked here, so OpenCV does not mistake the caption
    # itself for a graphic region. The caption is added back later in make_crop().
    for item in get_text_lines(page):
        bbox = fitz.Rect(item["bbox"])

        x0, y0, x1, y1 = scale_rect(bbox, zoom)

        pad_x = int(4 * zoom)
        pad_y = int(3 * zoom)

        x0 = max(0, x0 - pad_x)
        y0 = max(0, y0 - pad_y)
        x1 = min(width, x1 + pad_x)
        y1 = min(height, y1 + pad_y)

        cv2.rectangle(mask, (x0, y0), (x1, y1), 255, thickness=-1)

    return mask
'''

if old not in text:
    raise SystemExit("Target function not found. Patch not applied.")

text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
print("OK: figure_exporter_vision.py patched. Captions are no longer detected as graphic regions.")
