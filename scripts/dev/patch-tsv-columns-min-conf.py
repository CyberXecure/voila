from pathlib import Path
import re

path = Path("services/api/ocr_tsv_columns_tesseract_pages.py")
text = path.read_text(encoding="utf-8")

text = text.replace(
'''def parse_words(tsv: str) -> list[dict]:''',
'''def parse_words(tsv: str, min_conf: float = -1.0) -> list[dict]:'''
)

text = text.replace(
'''        if conf >= 0 and conf < 15:
            continue
''',
'''        if min_conf >= 0 and conf >= 0 and conf < min_conf:
            continue
'''
)

text = text.replace(
'''    parser.add_argument("--replace-pages", action="store_true")''',
'''    parser.add_argument("--replace-pages", action="store_true")
    parser.add_argument("--min-conf", type=float, default=-1.0)'''
)

text = text.replace(
'''        words = parse_words(tsv)''',
'''        words = parse_words(tsv, min_conf=args.min_conf)'''
)

path.write_text(text, encoding="utf-8")
print("OK: TSV column OCR now supports --min-conf and keeps low-confidence words by default.")
