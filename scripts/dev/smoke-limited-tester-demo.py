from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services" / "api"))

import fitz
from fastapi import HTTPException

import web_app


TMP_DIR = ROOT / "data" / "tmp-limited-demo-smoke"


def make_pdf(path: Path, pages: int) -> None:
    doc = fitz.open()
    try:
        for index in range(pages):
            page = doc.new_page()
            page.insert_text((72, 72), f"Voila limited tester demo smoke page {index + 1}")
        doc.save(path)
    finally:
        doc.close()


def main() -> None:
    shutil.rmtree(TMP_DIR, ignore_errors=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    allowed = TMP_DIR / "allowed_5_pages.pdf"
    blocked = TMP_DIR / "blocked_6_pages.pdf"

    make_pdf(allowed, web_app.VOILA_TESTER_DEMO_MAX_PAGES)
    make_pdf(blocked, web_app.VOILA_TESTER_DEMO_MAX_PAGES + 1)

    web_app.enforce_limited_tester_demo_pdf_limit(allowed)

    try:
        web_app.enforce_limited_tester_demo_pdf_limit(blocked)
    except HTTPException as exc:
        assert exc.status_code == 400
        assert "Limited Tester Demo" in str(exc.detail)
        assert "5 pages per PDF" in str(exc.detail)
    else:
        raise AssertionError("Expected 6-page PDF to be blocked.")

    shutil.rmtree(TMP_DIR, ignore_errors=True)
    print("OK: limited tester demo page limit smoke passed.")


if __name__ == "__main__":
    main()
