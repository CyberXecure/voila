from pathlib import Path
import json
import re

path = Path("services/api/ocr_best_text.py")

path.write_text(r'''
from __future__ import annotations

from pathlib import Path
import json
import re


OCR_TEXT_SOURCES = [
    "ocr_corrections.json",
    "ocr_pages.manual.json",
    "ocr_pages.post_clean.json",
    "ocr_tsv_columns_pages.post_clean.json",
    "ocr_body_columns_pages.post_clean.json",
    "ocr_pages.json",
    "ocr_tsv_columns_pages.json",
    "ocr_body_columns_pages.json",
]


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _page_int(value):
    try:
        return int(value)
    except Exception:
        return None


def _extract_page_text(data, page_number: int) -> str:
    if data is None:
        return ""

    # Shape: {"pages": [{"page_number": 3, "text": "..."}]}
    if isinstance(data, dict) and isinstance(data.get("pages"), list):
        for item in data["pages"]:
            if not isinstance(item, dict):
                continue

            page = _page_int(
                item.get("page_number")
                or item.get("page")
                or item.get("page_index")
            )

            if page is None:
                continue

            # If a file stores zero-based page_index only.
            if "page_index" in item and "page_number" not in item and page >= 0:
                page += 1

            if page == page_number:
                return str(
                    item.get("text")
                    or item.get("corrected_text")
                    or item.get("body")
                    or item.get("content")
                    or ""
                )

    # Shape: {"3": {"text": "..."}}
    if isinstance(data, dict):
        for key, value in data.items():
            page = None

            if isinstance(key, int):
                page = key
            else:
                match = re.search(r"\d+", str(key))
                if match:
                    page = int(match.group(0))

            if page != page_number:
                continue

            if isinstance(value, dict):
                return str(
                    value.get("text")
                    or value.get("corrected_text")
                    or value.get("body")
                    or value.get("content")
                    or ""
                )

            return str(value or "")

    return ""


def get_best_page_text(out_dir: Path | str, page_number: int) -> str:
    out_dir = Path(out_dir)

    for source in OCR_TEXT_SOURCES:
        path = out_dir / source

        if not path.exists():
            continue

        text = _extract_page_text(_read_json(path), int(page_number))

        if str(text or "").strip():
            return str(text)

    return ""
''', encoding="utf-8")

print("OK: created services/api/ocr_best_text.py")
