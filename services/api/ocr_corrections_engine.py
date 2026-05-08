from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default):
    if not path.exists():
        return default

    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_pages(payload) -> list[dict]:
    if isinstance(payload, dict):
        pages = payload.get("pages") or payload.get("items") or []
        return pages if isinstance(pages, list) else []

    if isinstance(payload, list):
        return payload

    return []


def replace_pages_shape(original, pages: list[dict]):
    if isinstance(original, dict):
        if "pages" in original:
            original["pages"] = pages
            original["text_source"] = "ocr_corrected"
            return original

        if "items" in original:
            original["items"] = pages
            original["text_source"] = "ocr_corrected"
            return original

    if isinstance(original, list):
        return pages

    return {
        "version": "voila_ocr_corrected_v1",
        "text_source": "ocr_corrected",
        "pages": pages,
    }


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def add_correction(
    output_dir: Path,
    original: str,
    corrected: str,
    page_number: int | None,
    lesson_id: str,
    correction_type: str,
    scope: str,
    source: str,
) -> Path:
    path = output_dir / "ocr_corrections.manual.json"

    payload = load_json(
        path,
        {
            "version": "1.0",
            "corrections": [],
        },
    )

    correction = {
        "id": str(uuid4()),
        "page_number": page_number,
        "lesson_id": lesson_id,
        "original": original,
        "corrected": corrected,
        "type": correction_type,
        "scope": scope,
        "source": source,
        "created_at": now_iso(),
    }

    payload.setdefault("corrections", []).append(correction)

    save_json(path, payload)
    return path


def add_title_override(
    output_dir: Path,
    lesson_id: str,
    title: str,
    source: str,
) -> Path:
    path = output_dir / "study_concept_overrides.json"

    payload = load_json(
        path,
        {
            "version": "1.0",
            "overrides": {},
        },
    )

    payload.setdefault("overrides", {})[lesson_id] = {
        "concept_title": title,
        "lesson_title": title,
        "source": source,
        "updated_at": now_iso(),
    }

    save_json(path, payload)
    return path


def apply_text_corrections_to_pages(output_dir: Path, replace_pages: bool, replace_ocr: bool) -> dict:
    corrections_path = output_dir / "ocr_corrections.manual.json"
    corrections_payload = load_json(corrections_path, {"corrections": []})
    corrections = corrections_payload.get("corrections") or []

    source_path = output_dir / "ocr_pages.json"

    if not source_path.exists():
        source_path = output_dir / "pages.json"

    if not source_path.exists():
        raise FileNotFoundError(f"No pages source found in {output_dir}")

    source_payload = load_json(source_path, {})
    pages = get_pages(source_payload)

    new_pages = []
    applied = []

    for index, page in enumerate(pages, start=1):
        if not isinstance(page, dict):
            continue

        page_number = int(page.get("page_number") or page.get("pdf_page") or index)
        text = str(page.get("text") or page.get("content") or "")

        for correction in corrections:
            original = str(correction.get("original") or "")
            corrected = str(correction.get("corrected") or "")
            scope = correction.get("scope") or "page_exact"
            correction_page = correction.get("page_number")

            if not original or not corrected:
                continue

            should_apply = False

            if scope == "global_exact":
                should_apply = True
            elif scope == "page_exact":
                should_apply = correction_page is not None and int(correction_page) == page_number
            elif scope == "all_exact":
                should_apply = True

            if not should_apply:
                continue

            before = text
            text = text.replace(original, corrected)

            if text != before:
                applied.append(
                    {
                        "correction_id": correction.get("id"),
                        "page_number": page_number,
                        "original": original,
                        "corrected": corrected,
                        "scope": scope,
                    }
                )

        new_page = dict(page)
        new_page["page_number"] = page_number
        new_page["text"] = text
        new_page["text_source"] = "ocr_corrected"
        new_pages.append(new_page)

    corrected_payload = {
        "version": "voila_ocr_corrected_v1",
        "source": str(source_path),
        "corrections_file": str(corrections_path),
        "applied_count": len(applied),
        "pages": new_pages,
    }

    corrected_path = output_dir / "ocr_pages.corrected.json"
    corrected_md = output_dir / "ocr_pages.corrected.md"

    save_json(corrected_path, corrected_payload)

    md_lines = [
        f"# Corrected OCR pages for {output_dir.name}",
        "",
        "Generated by Voila! OCR corrections engine.",
        "",
    ]

    for page in new_pages:
        md_lines.extend(
            [
                f"## Page {page['page_number']}",
                "",
                str(page.get("text") or "").strip(),
                "",
            ]
        )

    corrected_md.write_text("\n".join(md_lines), encoding="utf-8")

    if replace_ocr:
        backup = output_dir / "ocr_pages.before_manual_corrections.json"

        ocr_path = output_dir / "ocr_pages.json"

        if ocr_path.exists() and not backup.exists():
            backup.write_text(ocr_path.read_text(encoding="utf-8"), encoding="utf-8")

        save_json(
            ocr_path,
            {
                "version": "voila_ocr_corrected_v1",
                "pages": new_pages,
            },
        )

        (output_dir / "ocr_pages.md").write_text("\n".join(md_lines), encoding="utf-8")

    if replace_pages:
        pages_path = output_dir / "pages.json"
        pages_md = output_dir / "pages.md"

        if pages_path.exists():
            backup = output_dir / "pages.before_manual_corrections.json"

            if not backup.exists():
                backup.write_text(pages_path.read_text(encoding="utf-8"), encoding="utf-8")

            original_payload = load_json(pages_path, {})
        else:
            original_payload = {}

        save_json(pages_path, replace_pages_shape(original_payload, new_pages))
        pages_md.write_text("\n".join(md_lines), encoding="utf-8")

    report = {
        "version": "voila_ocr_corrections_report_v1",
        "applied_count": len(applied),
        "applied": applied,
        "corrected_json": str(corrected_path),
        "corrected_md": str(corrected_md),
    }

    report_path = output_dir / "ocr_corrections_report.json"
    save_json(report_path, report)

    return report


def apply_title_overrides(output_dir: Path) -> dict:
    overrides_path = output_dir / "study_concept_overrides.json"
    overrides_payload = load_json(overrides_path, {"overrides": {}})
    overrides = overrides_payload.get("overrides") or {}

    if not overrides:
        return {"updated": 0, "message": "No title overrides found."}

    updated = 0

    for name in ["course.cleaned.md", "course.md"]:
        path = output_dir / name

        if not path.exists():
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")

        for lesson_id, value in overrides.items():
            new_title = normalize_space(value.get("lesson_title") or value.get("concept_title") or "")

            if not new_title:
                continue

            pattern = rf"^(##\s+{re.escape(lesson_id)}\s+—\s+).*$"
            replacement = rf"\1{new_title}"

            text, count = re.subn(pattern, replacement, text, flags=re.MULTILINE)

            if count:
                updated += count

        path.write_text(text, encoding="utf-8")

    quiz_path = output_dir / "quiz.study.json"

    if quiz_path.exists():
        quiz = load_json(quiz_path, {})

        for question in quiz.get("questions", []):
            lesson_id = question.get("lesson_id")

            if lesson_id not in overrides:
                continue

            new_title = normalize_space(
                overrides[lesson_id].get("concept_title")
                or overrides[lesson_id].get("lesson_title")
                or ""
            )

            if not new_title:
                continue

            question["lesson_title"] = new_title
            question["concept_title"] = new_title
            question["concept_id"] = f"{lesson_id} — {new_title}"
            updated += 1

        save_json(quiz_path, quiz)

    return {
        "updated": updated,
        "overrides": overrides,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! OCR corrections engine")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add text correction")
    p_add.add_argument("output_dir")
    p_add.add_argument("--original", required=True)
    p_add.add_argument("--corrected", required=True)
    p_add.add_argument("--page", type=int, default=0)
    p_add.add_argument("--lesson-id", default="")
    p_add.add_argument("--type", default="text")
    p_add.add_argument("--scope", default="page_exact", choices=["page_exact", "global_exact", "all_exact"])
    p_add.add_argument("--source", default="manual")

    p_title = sub.add_parser("title", help="Add lesson/concept title override")
    p_title.add_argument("output_dir")
    p_title.add_argument("--lesson-id", required=True)
    p_title.add_argument("--title", required=True)
    p_title.add_argument("--source", default="manual")

    p_apply = sub.add_parser("apply", help="Apply text corrections")
    p_apply.add_argument("output_dir")
    p_apply.add_argument("--replace-pages", action="store_true")
    p_apply.add_argument("--replace-ocr", action="store_true")

    p_apply_titles = sub.add_parser("apply-titles", help="Apply title overrides to course/quiz")
    p_apply_titles.add_argument("output_dir")

    args = parser.parse_args()
    output_dir = Path(args.output_dir).resolve()

    if args.cmd == "add":
        path = add_correction(
            output_dir=output_dir,
            original=args.original,
            corrected=args.corrected,
            page_number=args.page if args.page > 0 else None,
            lesson_id=args.lesson_id,
            correction_type=args.type,
            scope=args.scope,
            source=args.source,
        )

        print("Correction saved.")
        print(f"- {path}")

    elif args.cmd == "title":
        path = add_title_override(
            output_dir=output_dir,
            lesson_id=args.lesson_id,
            title=args.title,
            source=args.source,
        )

        print("Title override saved.")
        print(f"- {path}")

    elif args.cmd == "apply":
        report = apply_text_corrections_to_pages(
            output_dir=output_dir,
            replace_pages=args.replace_pages,
            replace_ocr=args.replace_ocr,
        )

        print("Corrections applied.")
        print(f"Applied: {report['applied_count']}")
        print(f"- {report['corrected_json']}")

    elif args.cmd == "apply-titles":
        report = apply_title_overrides(output_dir)
        print("Title overrides applied.")
        print(f"Updated: {report.get('updated')}")


if __name__ == "__main__":
    main()
