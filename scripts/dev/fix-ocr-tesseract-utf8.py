from pathlib import Path

path = Path("services/api/ocr_tesseract_pages.py")
text = path.read_text(encoding="utf-8")

text = text.replace(
'''    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        env=env,
    )
''',
'''    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        env=env,
        encoding="utf-8",
        errors="replace",
    )
'''
)

text = text.replace(
'''    text = result.stdout.replace("\\f", "").strip()
''',
'''    text = (result.stdout or "").replace("\\f", "").strip()
'''
)

# Add page range args if missing
if '--page-from' not in text:
    text = text.replace(
'''    parser.add_argument("--zoom", type=float, default=2.0)
    parser.add_argument("--replace-pages", action="store_true")
''',
'''    parser.add_argument("--zoom", type=float, default=2.0)
    parser.add_argument("--page-from", type=int, default=1)
    parser.add_argument("--page-to", type=int, default=0)
    parser.add_argument("--replace-pages", action="store_true")
'''
    )

text = text.replace(
'''    for index, page in enumerate(doc, start=1):
        image_path = images_dir / f"page_{index:04d}.png"
''',
'''    page_from = max(1, args.page_from)
    page_to = min(len(doc), args.page_to if args.page_to > 0 else len(doc))

    print(f"Page range: {page_from}-{page_to}")

    for index in range(page_from, page_to + 1):
        page = doc[index - 1]
        image_path = images_dir / f"page_{index:04d}.png"
'''
)

path.write_text(text, encoding="utf-8")

print("OK: OCR script patched for UTF-8 output and page ranges.")
