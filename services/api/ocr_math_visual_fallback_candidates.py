"""Build OCR Math visual fallback candidates.

Diagnostic-only:
- reads ocr_math_report.json and source markdown files;
- maps risky math lines to pages using "## Page N" headings;
- references ocr/page_images/page_XXXX.png;
- writes only visual_fallback_candidates.json;
- does not modify OCR text, Course, Study, Progress, Figures, Crop, ZIP, delivery, or distribution.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


MARKER = "VOILA_V0_7_42_OCR_MATH_VISUAL_FALLBACK_CANDIDATES_MANIFEST"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _line_to_page_index(path: Path) -> dict[int, int]:
    mapping: dict[int, int] = {}
    current_page: int | None = None

    if not path.exists():
        return mapping

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    for line_number, line in enumerate(lines, start=1):
        match = re.match(
            r"^\s*##\s+Page\s+(\d+)\s*$",
            line.strip(),
            flags=re.IGNORECASE,
        )

        if match:
            current_page = int(match.group(1))

        if current_page is not None:
            mapping[line_number] = current_page

    return mapping


def _image_path_for_page(output_folder: Path, page_number: int | None) -> tuple[str | None, bool]:
    if page_number is None:
        return None, False

    relative = Path("ocr") / "page_images" / f"page_{page_number:04d}.png"
    absolute = output_folder / relative

    return relative.as_posix(), absolute.is_file()


def _risk_level(item: dict[str, Any]) -> str:
    severity = str(item.get("severity") or "").strip().lower()
    rule_id = str(item.get("rule_id") or "").strip().lower()
    reason = str(item.get("reason") or "").strip().lower()

    if severity in {"critical", "high"}:
        return "high"

    if "lim" in rule_id or "integral" in rule_id or "formula" in reason:
        return "high"

    return "medium"


def _candidate_reason(item: dict[str, Any]) -> str:
    rule_id = str(item.get("rule_id") or "").strip()
    reason = str(item.get("reason") or "").strip()

    if rule_id and reason:
        return f"{rule_id}: {reason}"

    if reason:
        return reason

    if rule_id:
        return rule_id

    return "math_or_symbol_dense_line"


def build_candidates(
    output_folder: Path,
    pdf_name: str = "",
    *,
    max_candidates: int = 80,
) -> dict[str, Any]:
    output_folder = Path(output_folder)
    report_path = output_folder / "ocr_math_report.json"

    if not report_path.exists():
        raise FileNotFoundError(f"Missing OCR Math report: {report_path}")

    report = _read_json(report_path)
    suggestions = report.get("top_suggestions") or []

    if not isinstance(suggestions, list):
        suggestions = []

    source_indexes: dict[str, dict[int, int]] = {}
    candidates: list[dict[str, Any]] = []
    per_page_counts: dict[int, int] = {}

    for item in suggestions[:max_candidates]:
        if not isinstance(item, dict):
            continue

        source_file = str(item.get("source") or "")
        line_number = int(item.get("line_number") or 0)

        if source_file not in source_indexes:
            source_indexes[source_file] = _line_to_page_index(output_folder / source_file)

        page_number = source_indexes[source_file].get(line_number)
        capture_source, capture_exists = _image_path_for_page(output_folder, page_number)

        if page_number is None:
            candidate_id = f"math-unknown-{len(candidates) + 1:03d}"
        else:
            per_page_counts[page_number] = per_page_counts.get(page_number, 0) + 1
            candidate_id = f"math-p{page_number:03d}-{per_page_counts[page_number]:03d}"

        candidates.append(
            {
                "candidate_id": candidate_id,
                "page_number": page_number,
                "source": "ocr_math_report",
                "source_file": source_file,
                "line_number": line_number,
                "rule_id": item.get("rule_id"),
                "severity": item.get("severity"),
                "risk_level": _risk_level(item),
                "reason": _candidate_reason(item),
                "original": item.get("original"),
                "replacement": item.get("replacement"),
                "capture_source": capture_source,
                "capture_exists": capture_exists,
                "crop_status": "needs_crop",
                "figure_candidate": True,
                "study_reference_allowed": True,
            }
        )

    with_capture = sum(1 for item in candidates if item.get("capture_exists"))

    return {
        "marker": MARKER,
        "scope": "diagnostic manifest only; no OCR/Course/Study/Progress/Figures/Crop rewrite; no build, no ZIP, no delivery, no distribution",
        "pdf": pdf_name or str(report.get("pdf") or output_folder.name),
        "output_folder": str(output_folder),
        "source_report": "ocr_math_report.json",
        "source_page_images": "ocr/page_images/page_XXXX.png",
        "candidate_count": len(candidates),
        "candidate_count_with_existing_capture": with_capture,
        "visual_fallback_candidates": candidates,
    }


def write_candidates(
    output_folder: Path,
    pdf_name: str = "",
    *,
    max_candidates: int = 80,
) -> dict[str, Any]:
    payload = build_candidates(output_folder, pdf_name, max_candidates=max_candidates)
    out_path = Path(output_folder) / "visual_fallback_candidates.json"
    _write_json(out_path, payload)

    return {
        "OCR_MATH_VISUAL_FALLBACK_CANDIDATES": "PASS",
        "json_path": str(out_path),
        "candidate_count": payload["candidate_count"],
        "candidate_count_with_existing_capture": payload["candidate_count_with_existing_capture"],
        "scope": payload["scope"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build OCR Math visual fallback candidates manifest"
    )
    parser.add_argument("--output-folder", type=Path, required=True)
    parser.add_argument("--pdf-name", default="")
    parser.add_argument("--max-candidates", type=int, default=80)
    args = parser.parse_args()

    result = write_candidates(
        args.output_folder,
        args.pdf_name,
        max_candidates=args.max_candidates,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
