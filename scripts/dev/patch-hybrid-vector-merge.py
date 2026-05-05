from pathlib import Path
import re

path = Path("services/api/figure_exporter_hybrid.py")
text = path.read_text(encoding="utf-8")

new_block = r'''
def horizontal_overlap_ratio(a: fitz.Rect, b: fitz.Rect) -> float:
    overlap = min(a.x1, b.x1) - max(a.x0, b.x0)

    if overlap <= 0:
        return 0.0

    return overlap / max(1.0, min(a.width, b.width))


def merge_related_vector_candidates(page: fitz.Page, caption: dict, chosen: dict, candidates: list[dict]) -> dict:
    if chosen["kind"] != "vector_drawing":
        return chosen

    cap = fitz.Rect(caption["bbox"])
    cap_y_pct = cap.y0 / page.rect.height if page.rect.height else 0

    merged = fitz.Rect(chosen["rect"])

    for candidate in candidates:
        if candidate is chosen:
            continue

        if candidate["kind"] != "vector_drawing":
            continue

        rect = fitz.Rect(candidate["rect"])

        # Caption usually below the drawing.
        if cap_y_pct > 0.25:
            if rect.y0 > cap.y1 + page.rect.height * 0.06:
                continue

            if rect.y1 < cap.y0 - page.rect.height * 0.62:
                continue

        # Caption near top: drawing likely below it.
        else:
            if rect.y1 < cap.y0 - page.rect.height * 0.06:
                continue

            if rect.y0 > cap.y1 + page.rect.height * 0.68:
                continue

        overlap_with_merged = horizontal_overlap_ratio(rect, merged)
        overlap_with_caption = horizontal_overlap_ratio(rect, cap)
        center_distance_x = abs(center(rect)[0] - center(cap)[0])

        close_enough_x = center_distance_x < page.rect.width * 0.48

        if overlap_with_merged > 0.08 or overlap_with_caption > 0.08 or close_enough_x:
            merged |= rect

    updated = dict(chosen)
    updated["rect"] = merged
    updated["kind"] = "vector_drawing_merged"

    return updated


def choose_candidate(page: fitz.Page, caption: dict, candidates: list[dict]) -> dict | None:
    if not candidates:
        return None

    cap = fitz.Rect(caption["bbox"])
    cap_center = center(cap)
    cap_y_pct = cap.y0 / page.rect.height if page.rect.height else 0

    scored = []

    for candidate in candidates:
        rect = candidate["rect"]

        above_caption = rect.y1 <= cap.y1 + page.rect.height * 0.04
        below_caption = rect.y0 >= cap.y0 - page.rect.height * 0.04

        overlap = horizontal_overlap_ratio(rect, cap)
        d = distance(center(rect), cap_center)

        direction_penalty = 0.0

        if cap_y_pct > 0.25 and not above_caption:
            direction_penalty += page.rect.height * 0.38

        if cap_y_pct <= 0.25 and not below_caption:
            direction_penalty += page.rect.height * 0.38

        overlap_bonus = page.rect.height * 0.12 if overlap > 0 else 0.0

        kind_bonus = 0.0
        if candidate["kind"] == "embedded_image":
            kind_bonus = page.rect.height * 0.07

        area_bonus = min(candidate["area"] / (page.rect.width * page.rect.height), 0.30) * page.rect.height * 0.13

        score = d + direction_penalty - overlap_bonus - kind_bonus - area_bonus

        scored.append((score, candidate))

    scored.sort(key=lambda pair: pair[0])

    chosen = scored[0][1]
    chosen = merge_related_vector_candidates(page, caption, chosen, candidates)

    return chosen


'''

pattern = r"def choose_candidate\(page: fitz\.Page, caption: dict, candidates: list\[dict\]\) -> dict \| None:.*?\ndef fallback_rect"

updated = re.sub(
    pattern,
    new_block + "\ndef fallback_rect",
    text,
    flags=re.DOTALL,
)

if updated == text:
    raise SystemExit("Patch failed: choose_candidate block not found.")

updated = updated.replace(
    "margin_y = page.rect.height * 0.025",
    "margin_y = page.rect.height * 0.035",
)

path.write_text(updated, encoding="utf-8")
print("OK: hybrid extractor patched with vector cluster merge.")
