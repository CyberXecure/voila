from pathlib import Path

path = Path("scripts/dev/run-ocr-page.py")
text = path.read_text(encoding="utf-8")

# Add --columns argument
if 'parser.add_argument("--columns"' not in text:
    text = text.replace(
'''    parser.add_argument("--zoom", type=float, default=3.0)
''',
'''    parser.add_argument("--zoom", type=float, default=3.0)
    parser.add_argument("--columns", type=int, default=0, help="0/1 = normal OCR, 2/3 = OCR left-to-right by columns")
'''
    )

# Add render_page_columns function after render_page
if "def render_page_columns(" not in text:
    marker = '''def run_tesseract(image_path: Path, lang: str, psm: int) -> str:
'''
    helper = r'''

def render_page_columns(pdf_path: Path, page_number: int, zoom: float, tmp_dir: Path, columns: int) -> list[Path]:
    doc = fitz.open(pdf_path)

    if page_number < 1 or page_number > doc.page_count:
        raise SystemExit(f"Pagina {page_number} este în afara intervalului 1..{doc.page_count}")

    page = doc.load_page(page_number - 1)
    rect = page.rect

    image_paths: list[Path] = []

    for index in range(columns):
        x0 = rect.x0 + (rect.width * index / columns)
        x1 = rect.x0 + (rect.width * (index + 1) / columns)

        # Small overlap helps avoid cutting words close to column boundaries.
        overlap = rect.width * 0.01

        if index > 0:
            x0 -= overlap

        if index < columns - 1:
            x1 += overlap

        clip = fitz.Rect(x0, rect.y0, x1, rect.y1)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False)

        image_path = tmp_dir / f"page_{page_number:04d}_col_{index + 1}.png"
        pix.save(str(image_path))
        image_paths.append(image_path)

    doc.close()
    return image_paths


'''
    if marker not in text:
        raise SystemExit("Nu găsesc def run_tesseract ca marker.")

    text = text.replace(marker, helper + marker)

old = '''    with tempfile.TemporaryDirectory() as tmp:
        image_path = Path(tmp) / f"page_{args.page:04d}.png"

        print("PDF:", pdf_path)
        print("Page:", args.page)
        print("Lang:", args.lang)
        print("PSM:", args.psm)
        print("Zoom:", args.zoom)
        print("")

        render_page(pdf_path, args.page, args.zoom, image_path)
        text = run_tesseract(image_path, args.lang, args.psm)
'''

new = '''    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        image_path = tmp_dir / f"page_{args.page:04d}.png"

        print("PDF:", pdf_path)
        print("Page:", args.page)
        print("Lang:", args.lang)
        print("PSM:", args.psm)
        print("Zoom:", args.zoom)
        print("Columns:", args.columns)
        print("")

        if int(args.columns or 0) > 1:
            image_paths = render_page_columns(
                pdf_path=pdf_path,
                page_number=args.page,
                zoom=args.zoom,
                tmp_dir=tmp_dir,
                columns=int(args.columns),
            )

            chunks = []

            for col_index, col_image in enumerate(image_paths, start=1):
                print(f"OCR column {col_index}/{len(image_paths)}...")
                chunk = run_tesseract(col_image, args.lang, args.psm).strip()

                if chunk:
                    chunks.append(chunk)

            text = "\\n\\n".join(chunks).strip()
        else:
            render_page(pdf_path, args.page, args.zoom, image_path)
            text = run_tesseract(image_path, args.lang, args.psm)
'''

if old not in text:
    raise SystemExit("Nu găsesc blocul tempfile/main OCR de înlocuit.")

text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
print("OK: run-ocr-page.py supports OCR by columns.")
