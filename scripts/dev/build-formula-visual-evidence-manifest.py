from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


MATH_PATTERNS = [
    (re.compile(r"\\b(vector|vectori|segment orientat|segmente orientate|direc[tț]ie|sens|modul|lungime)\\b", re.I), "math_vocabulary"),
    (re.compile(r"\\b[A-Z]\\s*[A-Z]\\b"), "point_pair_or_segment"),
    (re.compile(r"[→↔⇒⇔∈⊂⊆∪∩∞±×÷≤≥≠≈=<>]"), "math_symbol"),
    (re.compile(r"\\b(R|N|Z|Q|C)\\b"), "set_symbol_candidate"),
    (re.compile(r"\\b[a-zA-Z]\\s*=\\s*[-+]?\\d"), "assignment_or_equation"),
    (re.compile(r"\\b(fig\\.|figura|figură|desen|diagram[ăa])\\b", re.I), "figure_reference"),
]


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _candidate_reasons(text: str) -> list[str]:
    normalized = " ".join(_safe_text(text).split())
    reasons: list[str] = []
    if len(normalized) < 2:
        return reasons

    for pattern, reason in MATH_PATTERNS:
        if pattern.search(normalized):
            reasons.append(reason)

    letters = sum(ch.isalpha() for ch in normalized)
    symbols = sum(ch in "+-=<>/\\|()[]{}^_.,;:→↔⇒⇔∈⊂⊆∪∩∞±×÷≤≥≠≈" for ch in normalized)
    digits = sum(ch.isdigit() for ch in normalized)

    if symbols >= 2 and letters <= 20:
        reasons.append("symbol_dense_short_line")
    if digits and symbols:
        reasons.append("numeric_formula_candidate")

    # Deduplicate while preserving order.
    result: list[str] = []
    for item in reasons:
        if item not in result:
            result.append(item)
    return result


def _clip_bbox(bbox: tuple[float, float, float, float], rect, pad: float) -> tuple[float, float, float, float]:
    x0, y0, x1, y1 = bbox
    return (
        max(float(rect.x0), x0 - pad),
        max(float(rect.y0), y0 - pad),
        min(float(rect.x1), x1 + pad),
        min(float(rect.y1), y1 + pad),
    )


def build_manifest(course_id: str, max_candidates_per_page: int = 24, dpi: int = 180) -> dict[str, Any]:
    root = _repo_root()
    input_pdf = root / "data" / "input" / f"{course_id}.pdf"
    output_dir = root / "data" / "output" / course_id
    evidence_dir = output_dir / "formula_visual_evidence"
    crops_dir = evidence_dir / "crops"
    pages_dir = evidence_dir / "pages"
    manifest_path = output_dir / "formula_visual_evidence.manifest.json"

    if not input_pdf.exists():
        raise FileNotFoundError(f"Missing input PDF: {input_pdf}")

    evidence_dir.mkdir(parents=True, exist_ok=True)
    crops_dir.mkdir(parents=True, exist_ok=True)
    pages_dir.mkdir(parents=True, exist_ok=True)

    import fitz

    doc = fitz.open(str(input_pdf))
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    candidates: list[dict[str, Any]] = []
    page_images: list[dict[str, Any]] = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        page_number = page_index + 1
        page_rect = page.rect

        page_image_rel = Path("formula_visual_evidence") / "pages" / f"page-{page_number:03d}.png"
        page_image_abs = output_dir / page_image_rel
        page_pix = page.get_pixmap(matrix=matrix, alpha=False)
        page_pix.save(str(page_image_abs))

        page_images.append(
            {
                "page": page_number,
                "image_path": str(page_image_rel).replace("\\", "/"),
                "width_px": page_pix.width,
                "height_px": page_pix.height,
                "page_rect": [page_rect.x0, page_rect.y0, page_rect.x1, page_rect.y1],
                "dpi": dpi,
            }
        )

        page_dict = page.get_text("dict")
        page_candidates: list[dict[str, Any]] = []

        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                line_text = " ".join(_safe_text(span.get("text")) for span in spans).strip()
                reasons = _candidate_reasons(line_text)
                if not reasons:
                    continue

                raw_bbox = tuple(float(x) for x in line.get("bbox", [0, 0, 0, 0]))
                x0, y0, x1, y1 = _clip_bbox(raw_bbox, page_rect, pad=10.0)
                if x1 <= x0 or y1 <= y0:
                    continue

                page_candidates.append(
                    {
                        "page": page_number,
                        "text": line_text,
                        "bbox": [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)],
                        "raw_bbox": [round(x, 2) for x in raw_bbox],
                        "reasons": reasons,
                    }
                )

        page_candidates = page_candidates[:max_candidates_per_page]

        for page_item_index, item in enumerate(page_candidates, 1):
            crop_rel = Path("formula_visual_evidence") / "crops" / f"page-{page_number:03d}-candidate-{page_item_index:03d}.png"
            crop_abs = output_dir / crop_rel
            clip = fitz.Rect(item["bbox"])
            crop_pix = page.get_pixmap(matrix=matrix, clip=clip, alpha=False)
            crop_pix.save(str(crop_abs))

            item_id = f"p{page_number:03d}-c{page_item_index:03d}"
            item.update(
                {
                    "id": item_id,
                    "crop_path": str(crop_rel).replace("\\", "/"),
                    "crop_width_px": crop_pix.width,
                    "crop_height_px": crop_pix.height,
                    "source": "pymupdf_text_line_bbox",
                    "review_status": "pending_owner_review",
                }
            )
            candidates.append(item)

    doc.close()

    manifest = {
        "artifact": "formula_visual_evidence_manifest",
        "version": "v0.7.89",
        "course_id": course_id,
        "input_pdf": str(input_pdf),
        "output_dir": str(output_dir),
        "page_count": len(page_images),
        "candidate_count": len(candidates),
        "page_images": page_images,
        "candidates": candidates,
        "policy": {
            "owner_local": True,
            "uses_pymupdf": True,
            "uses_llm": False,
            "uses_cloud": False,
            "ocr_rewrite_performed": False,
            "formula_ocr_performed": False,
            "build_performed": False,
            "zip_created": False,
            "share_created": False,
            "delivery_performed": False,
        },
    }

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--course-id", required=True)
    parser.add_argument("--max-candidates-per-page", type=int, default=24)
    parser.add_argument("--dpi", type=int, default=180)
    args = parser.parse_args()

    manifest = build_manifest(
        course_id=args.course_id,
        max_candidates_per_page=args.max_candidates_per_page,
        dpi=args.dpi,
    )

    print("VOILA_V0_7_89_FORMULA_VISUAL_EVIDENCE_MANIFEST_BUILD=PASS")
    print("course_id=" + str(manifest["course_id"]))
    print("page_count=" + str(manifest["page_count"]))
    print("candidate_count=" + str(manifest["candidate_count"]))
    print("uses_pymupdf=" + str(manifest["policy"]["uses_pymupdf"]))
    print("uses_llm=" + str(manifest["policy"]["uses_llm"]))
    print("uses_cloud=" + str(manifest["policy"]["uses_cloud"]))
    print("ocr_rewrite_performed=" + str(manifest["policy"]["ocr_rewrite_performed"]))
    print("formula_ocr_performed=" + str(manifest["policy"]["formula_ocr_performed"]))
    print("BUILD_PERFORMED=" + str(manifest["policy"]["build_performed"]))
    print("ZIP_CREATED=" + str(manifest["policy"]["zip_created"]))
    print("SHARE_CREATED=" + str(manifest["policy"]["share_created"]))
    print("DELIVERY_PERFORMED=" + str(manifest["policy"]["delivery_performed"]))
    print("MANIFEST=" + str(Path(manifest["output_dir"]) / "formula_visual_evidence.manifest.json"))


if __name__ == "__main__":
    main()
