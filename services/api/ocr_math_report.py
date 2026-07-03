from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ocr_math_normalizer import normalize_text


TEXT_CANDIDATES = (
    "pages.md",
    "course.cleaned.md",
    "course.md",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_markdown(report: dict) -> str:
    lines: list[str] = []

    lines.append("# Voila OCR Math Diagnostic Report")
    lines.append("")
    lines.append(f"- PDF: `{report['pdf']}`")
    lines.append(f"- Output folder: `{report['output_folder']}`")
    lines.append(f"- Total suggestions: **{report['total_suggestions']}**")
    lines.append(f"- Changed lines: **{report['changed_line_count']}**")
    lines.append("")
    lines.append("## Severity counts")
    for key, value in report["severity_counts"].items():
        lines.append(f"- `{key}`: {value}")

    lines.append("")
    lines.append("## Rule counts")
    for key, value in report["rule_counts"].items():
        lines.append(f"- `{key}`: {value}")

    lines.append("")
    lines.append("## Source summaries")
    for source in report["sources"]:
        lines.append("")
        lines.append(f"### {source['name']}")
        lines.append(f"- Suggestions: {source['suggestion_count']}")
        lines.append(f"- Changed lines: {source['changed_line_count']}")
        lines.append(f"- Math lines: {source['line_type_counts'].get('math', 0)}")
        lines.append(f"- Mixed lines: {source['line_type_counts'].get('mixed', 0)}")
        lines.append(f"- Text lines: {source['line_type_counts'].get('text', 0)}")

    lines.append("")
    lines.append("## Top suggestions")
    for index, item in enumerate(report["top_suggestions"], start=1):
        lines.append("")
        lines.append(f"### {index}. {item['source']} · line {item['line_number']} · {item['severity']}")
        lines.append(f"- Rule: `{item['rule_id']}`")
        lines.append(f"- Reason: {item['reason']}")
        lines.append("")
        lines.append("```text")
        lines.append(f"{item['original']} → {item['replacement']}")
        lines.append("```")

    lines.append("")
    lines.append("## Policy")
    lines.append("- Diagnostic only.")
    lines.append("- Does not modify OCR text, course files, Study, Progress, ZIP, delivery, or distribution.")
    lines.append("- Use this report to identify risky math lines before integrating Formula OCR or visual formula fallback.")

    return "\n".join(lines) + "\n"


def build_ocr_math_report(output_folder: Path, pdf_name: str) -> dict:
    output_folder = Path(output_folder)

    if not output_folder.exists():
        raise FileNotFoundError(f"Output folder not found: {output_folder}")

    sources = []
    all_suggestions = []

    for candidate in TEXT_CANDIDATES:
        path = output_folder / candidate
        if not path.exists():
            continue

        text = _read_text(path)
        result = normalize_text(text)

        rule_counts = Counter()
        severity_counts = Counter()
        line_type_counts = Counter()

        for line in result.line_results:
            line_type_counts[line.line_type] += 1

            for suggestion in line.suggestions:
                rule_counts[suggestion.rule_id] += 1
                severity_counts[suggestion.severity] += 1
                all_suggestions.append(
                    {
                        "source": candidate,
                        "line_number": suggestion.line_number,
                        "rule_id": suggestion.rule_id,
                        "severity": suggestion.severity,
                        "reason": suggestion.reason,
                        "original": suggestion.original,
                        "replacement": suggestion.replacement,
                    }
                )

        sources.append(
            {
                "name": candidate,
                "path": str(path),
                "suggestion_count": result.suggestion_count,
                "changed_line_count": result.changed_line_count,
                "line_type_counts": dict(line_type_counts),
                "rule_counts": dict(rule_counts),
                "severity_counts": dict(severity_counts),
            }
        )

    rule_counts_total = Counter(item["rule_id"] for item in all_suggestions)
    severity_counts_total = Counter(item["severity"] for item in all_suggestions)

    report = {
        "scope": "owner-local OCR math diagnostic report only; no build, no ZIP, no delivery, no distribution",
        "pdf": pdf_name,
        "output_folder": str(output_folder),
        "source_candidates": list(TEXT_CANDIDATES),
        "sources": sources,
        "total_suggestions": len(all_suggestions),
        "changed_line_count": sum(source["changed_line_count"] for source in sources),
        "rule_counts": dict(rule_counts_total),
        "severity_counts": dict(severity_counts_total),
        "top_suggestions": all_suggestions[:80],
    }

    return report


def write_report(output_folder: Path, pdf_name: str) -> dict:
    report = build_ocr_math_report(output_folder, pdf_name)

    json_path = output_folder / "ocr_math_report.json"
    md_path = output_folder / "ocr_math_report.md"

    _write_json(json_path, report)
    md_path.write_text(_build_markdown(report), encoding="utf-8")

    return {
        "report": report,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Build Voila OCR math diagnostic report")
    parser.add_argument("--output-folder", type=Path, required=True)
    parser.add_argument("--pdf-name", required=True)
    args = parser.parse_args()

    result = write_report(args.output_folder, args.pdf_name)
    report = result["report"]

    print(
        json.dumps(
            {
                "OCR_MATH_DIAGNOSTIC_REPORT": "PASS",
                "total_suggestions": report["total_suggestions"],
                "changed_line_count": report["changed_line_count"],
                "json_path": result["json_path"],
                "markdown_path": result["markdown_path"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
