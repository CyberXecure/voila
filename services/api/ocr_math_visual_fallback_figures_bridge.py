"""Bridge OCR Math visual fallback candidates into a Figures/Crop sidecar manifest.

v0.7.43 diagnostic-only:
- reads visual_fallback_candidates.json from a course output folder;
- writes figures_hybrid/ocr_math_visual_fallback_manifest.json;
- preserves existing figures_manifest.hybrid.json and figures_hybrid.html;
- does not modify OCR text, Course, Study, Progress, Figures gallery, Crop Editor,
  ZIP, delivery, share, or distribution.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


MARKER = "VOILA_V0_7_43_OCR_MATH_VISUAL_FALLBACK_TO_FIGURES_CROP_SIDECAR"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _clean_text(value: Any, limit: int = 180) -> str:
    text = str(value or "").strip()
    text = " ".join(text.split())
    if len(text) > limit:
        return text[: limit - 1].rstrip() + "…"
    return text


def _candidate_number(candidate: dict[str, Any], index: int) -> str:
    page = candidate.get("page_number")
    if isinstance(page, int) and page > 0:
        return f"ocr-math-p{page:03d}-{index + 1:03d}"
    return f"ocr-math-unknown-{index + 1:03d}"


def _candidate_caption(candidate: dict[str, Any]) -> str:
    reason = _clean_text(candidate.get("reason"), 140)
    original = _clean_text(candidate.get("original"), 60)
    replacement = _clean_text(candidate.get("replacement"), 60)

    parts = []
    if reason:
        parts.append(reason)
    if original or replacement:
        parts.append(f"{original} -> {replacement}".strip())

    suffix = " · ".join(part for part in parts if part)
    if suffix:
        return "OCR Math visual fallback candidate: " + suffix

    return "OCR Math visual fallback candidate"


def _figures_relative_capture_path(candidate: dict[str, Any]) -> str:
    capture = str(candidate.get("capture_source") or "").replace("\\", "/").strip()
    if capture.startswith("ocr/page_images/"):
        return "../" + capture
    if capture:
        return capture
    page = candidate.get("page_number")
    if isinstance(page, int) and page > 0:
        return f"../ocr/page_images/page_{page:04d}.png"
    return ""


def build_sidecar(output_folder: Path, *, max_candidates: int = 80) -> dict[str, Any]:
    output_folder = Path(output_folder)
    source_path = output_folder / "visual_fallback_candidates.json"
    if not source_path.exists():
        raise FileNotFoundError(f"Missing source manifest: {source_path}")

    source = _read_json(source_path)
    raw_candidates = source.get("visual_fallback_candidates") or []
    if not isinstance(raw_candidates, list):
        raw_candidates = []

    figure_crops: list[dict[str, Any]] = []

    for index, candidate in enumerate(raw_candidates[:max_candidates]):
        if not isinstance(candidate, dict):
            continue
        if candidate.get("figure_candidate") is False:
            continue

        page_number = candidate.get("page_number")
        if not isinstance(page_number, int):
            page_number = None

        figure_crops.append(
            {
                "number": _candidate_number(candidate, len(figure_crops)),
                "caption": _candidate_caption(candidate),
                "pdf_page": page_number,
                "crop_method": "ocr_math_visual_fallback_sidecar",
                "relative_path": _figures_relative_capture_path(candidate),
                "crop_status": candidate.get("crop_status") or "needs_crop",
                "import_status": "sidecar_only_not_in_crop_editor_manifest",
                "source_candidate_id": candidate.get("candidate_id"),
                "source_line_number": candidate.get("line_number"),
                "source_file": candidate.get("source_file"),
                "risk_level": candidate.get("risk_level"),
                "severity": candidate.get("severity"),
                "rule_id": candidate.get("rule_id"),
                "reason": candidate.get("reason"),
                "original": candidate.get("original"),
                "replacement": candidate.get("replacement"),
                "capture_source": candidate.get("capture_source"),
                "capture_exists": bool(candidate.get("capture_exists")),
                "study_reference_allowed": bool(candidate.get("study_reference_allowed")),
            }
        )

    with_capture = sum(1 for item in figure_crops if item.get("capture_exists"))

    return {
        "marker": MARKER,
        "scope": (
            "diagnostic sidecar only; does not overwrite figures_manifest.hybrid.json; "
            "does not modify OCR/Course/Study/Progress/Figures gallery/Crop Editor; "
            "no build, no ZIP, no share, no delivery, no distribution"
        ),
        "source_manifest": "visual_fallback_candidates.json",
        "target_sidecar": "figures_hybrid/ocr_math_visual_fallback_manifest.json",
        "crop_editor_manifest_overwritten": False,
        "figures_gallery_overwritten": False,
        "candidate_count": len(figure_crops),
        "candidate_count_with_existing_capture": with_capture,
        "figure_crops": figure_crops,
    }


def write_sidecar(output_folder: Path, *, max_candidates: int = 80) -> dict[str, Any]:
    payload = build_sidecar(output_folder, max_candidates=max_candidates)
    out_path = Path(output_folder) / "figures_hybrid" / "ocr_math_visual_fallback_manifest.json"
    _write_json(out_path, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Build OCR Math visual fallback Figures/Crop sidecar manifest.")
    parser.add_argument("--output-folder", required=True)
    parser.add_argument("--max-candidates", type=int, default=80)
    args = parser.parse_args()

    payload = write_sidecar(Path(args.output_folder), max_candidates=args.max_candidates)
    print(
        f"{MARKER}=PASS "
        f"candidate_count={payload['candidate_count']} "
        f"candidate_count_with_existing_capture={payload['candidate_count_with_existing_capture']}"
    )


if __name__ == "__main__":
    main()
