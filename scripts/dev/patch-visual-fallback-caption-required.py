from pathlib import Path

path = Path("services/api/figure_exporter_visual_fallback.py")
text = path.read_text(encoding="utf-8")

helper = r'''

def load_ocr_text_by_page(output_dir: Path) -> dict[int, str]:
    candidates = [
        output_dir / "ocr_pages.cleaned.json",
        output_dir / "ocr_pages.json",
        output_dir / "pages.json",
    ]

    for path in candidates:
        if not path.exists():
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        if isinstance(data, dict):
            pages = data.get("pages") or data.get("items") or []
        elif isinstance(data, list):
            pages = data
        else:
            pages = []

        result = {}

        for idx, page in enumerate(pages, start=1):
            if not isinstance(page, dict):
                continue

            page_number = int(page.get("page_number") or page.get("pdf_page") or idx)
            page_text = str(page.get("text") or page.get("content") or "").strip()

            if page_text:
                result[page_number] = page_text

        if result:
            return result

    return {}


def page_has_figure_caption(page_text: str) -> bool:
    text = page_text or ""

    patterns = [
        r"(?im)^\s*(?:fig\.|figura)\s*[IVXLCDM0-9]+(?:[.\-]\d+)*",
        r"(?im)^\s*\d{1,2}\.\d{1,2}\.\s+[A-ZĂÂÎȘȚ]",
    ]

    return any(re.search(pattern, text) for pattern in patterns)

'''

if "def load_ocr_text_by_page" not in text:
    text = text.replace("def safe_number(value: str) -> str:", helper + "\n\ndef safe_number(value: str) -> str:")

text = text.replace(
'''    patterns = [
        r"(?m)^\\s*(?:figura|figure|fig\\.?)\\s*([0-9]+(?:\\.[0-9]+)+)\\.?\\s+(.{3,160})$",
        r"(?m)^\\s*([0-9]+(?:\\.[0-9]+)+)\\.\\s+(.{3,160})$",
    ]
''',
'''    patterns = [
        r"(?m)^\\s*(?:figura|figure|fig\\.?)\\s*([IVXLCDM0-9]+(?:[.\\-][0-9]+)+)\\.?\\s+(.{3,180})$",
        r"(?m)^\\s*([0-9]{1,2}\\.[0-9]{1,2})\\.\\s+(.{3,180})$",
    ]
'''
)

text = text.replace(
'''    doc = fitz.open(pdf_path)
    page_to = args.page_to if args.page_to > 0 else len(doc)
''',
'''    doc = fitz.open(pdf_path)
    ocr_text_by_page = load_ocr_text_by_page(out_dir)
    page_to = args.page_to if args.page_to > 0 else len(doc)
'''
)

text = text.replace(
'''        page = doc[page_no - 1]
        page_text = page.get_text("text") or ""
        image = page_to_image(page, args.zoom)
''',
'''        page = doc[page_no - 1]
        embedded_text = page.get_text("text") or ""
        page_text = embedded_text.strip() or ocr_text_by_page.get(page_no, "")

        # For scanned/image PDFs, do not extract random text blocks as figures.
        # Require an OCR-visible figure caption on the page.
        if ocr_text_by_page and not page_has_figure_caption(page_text):
            print(f"Skip page without figure caption: {page_no}")
            continue

        image = page_to_image(page, args.zoom)
'''
)

path.write_text(text, encoding="utf-8")
print("OK: visual fallback now uses OCR captions and skips pages without figure captions.")
