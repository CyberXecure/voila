from __future__ import annotations

import json
import os
from pathlib import Path

from ocr_math_report import write_report


ENV_FLAG = "VOILA_ENABLE_OCR_MATH_REPORT_HOOK"


def _enabled_from_env() -> bool:
    value = os.environ.get(ENV_FLAG, "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


def build_ocr_math_report_if_enabled(
    output_folder: Path | str,
    pdf_name: str,
    *,
    enabled: bool | None = None,
    reason: str = "owner-local-hook",
) -> dict:
    """Build OCR math report only when explicitly enabled.

    Safe policy:
    - does not modify OCR text
    - does not modify course/study/progress files
    - does not build ZIP/package/release artifacts
    - writes only ocr_math_report.json and ocr_math_report.md in the output folder
    """

    output_path = Path(output_folder)

    if enabled is None:
        enabled = _enabled_from_env()

    if not enabled:
        return {
            "OCR_MATH_REPORT_HOOK": "SKIPPED",
            "enabled": False,
            "reason": "disabled",
            "output_folder": str(output_path),
            "pdf_name": pdf_name,
            "json_path": None,
            "markdown_path": None,
            "total_suggestions": 0,
            "changed_line_count": 0,
        }

    if not output_path.exists():
        return {
            "OCR_MATH_REPORT_HOOK": "SKIPPED",
            "enabled": True,
            "reason": "missing_output_folder",
            "output_folder": str(output_path),
            "pdf_name": pdf_name,
            "json_path": None,
            "markdown_path": None,
            "total_suggestions": 0,
            "changed_line_count": 0,
        }

    result = write_report(output_path, pdf_name)
    report = result["report"]

    return {
        "OCR_MATH_REPORT_HOOK": "PASS",
        "enabled": True,
        "reason": reason,
        "output_folder": str(output_path),
        "pdf_name": pdf_name,
        "json_path": result["json_path"],
        "markdown_path": result["markdown_path"],
        "total_suggestions": report["total_suggestions"],
        "changed_line_count": report["changed_line_count"],
        "scope": "owner-local diagnostic only; no build, no ZIP, no delivery, no distribution",
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Owner-local OCR math report hook")
    parser.add_argument("--output-folder", type=Path, required=True)
    parser.add_argument("--pdf-name", required=True)
    parser.add_argument("--enable", action="store_true")
    parser.add_argument("--reason", default="manual-owner-local-check")
    args = parser.parse_args()

    payload = build_ocr_math_report_if_enabled(
        args.output_folder,
        args.pdf_name,
        enabled=args.enable,
        reason=args.reason,
    )

    print(json.dumps(payload, ensure_ascii=False, indent=2))

    return 0 if payload["OCR_MATH_REPORT_HOOK"] in {"PASS", "SKIPPED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
