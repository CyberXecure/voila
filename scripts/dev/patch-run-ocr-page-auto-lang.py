from pathlib import Path

path = Path("scripts/dev/run-ocr-page.py")
text = path.read_text(encoding="utf-8")

if "import document_language as dl" not in text:
    text = text.replace(
'''PROJECT = Path(".").resolve()
INPUT_DIR = PROJECT / "data" / "input"
OUTPUT_DIR = PROJECT / "data" / "output"
''',
'''PROJECT = Path(".").resolve()
INPUT_DIR = PROJECT / "data" / "input"
OUTPUT_DIR = PROJECT / "data" / "output"

sys.path.insert(0, str(PROJECT / "services" / "api"))
import document_language as dl
'''
    )

text = text.replace(
'''    parser.add_argument("--lang", default="ron+eng")''',
'''    parser.add_argument("--lang", default="auto")'''
)

needle = '''    pdf_path = find_pdf(args.pdf)
    out_dir = OUTPUT_DIR / pdf_path.stem
'''

replacement = '''    pdf_path = find_pdf(args.pdf)

    if str(args.lang or "").lower() == "auto":
        args.lang = dl.get_ocr_lang(PROJECT, pdf_path.name)

    out_dir = OUTPUT_DIR / pdf_path.stem
'''

if needle in text and "dl.get_ocr_lang" not in text:
    text = text.replace(needle, replacement)

path.write_text(text, encoding="utf-8")
print("OK: run-ocr-page.py now supports --lang auto from document language config.")
