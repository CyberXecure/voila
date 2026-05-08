from pathlib import Path
import re

path = Path("services/api/ocr_tsv_columns_tesseract_pages.py")
text = path.read_text(encoding="utf-8")

# 1. Replace run_tesseract_tsv with -c tessedit_create_tsv=1
pattern = r'def run_tesseract_tsv\([\s\S]*?\n\n(?=def parse_words\()'

replacement = r'''def run_tesseract_tsv(
    img: Image.Image,
    tesseract: str,
    lang: str,
    psm: int,
    tessdata: str | None,
) -> tuple[str, float, int]:
    env = os.environ.copy()

    if tessdata:
        env["TESSDATA_PREFIX"] = tessdata

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        image_path = tmp_dir / "page.png"
        output_base = tmp_dir / "ocr_out"
        tsv_path = tmp_dir / "ocr_out.tsv"

        img.save(image_path)

        cmd = [
            tesseract,
            str(image_path),
            str(output_base),
            "-l",
            lang,
            "--psm",
            str(psm),
            "-c",
            "tessedit_create_tsv=1",
        ]

        start = time.time()

        result = subprocess.run(
            cmd,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env=env,
        )

        elapsed = time.time() - start

        if tsv_path.exists():
            tsv = tsv_path.read_text(encoding="utf-8", errors="replace")
        else:
            tsv = result.stdout or ""

    return tsv, elapsed, result.returncode

'''

text, count = re.subn(pattern, replacement, text)

if count != 1:
    raise SystemExit(f"Could not replace run_tesseract_tsv. Replacements: {count}")


# 2. Replace parse_words with robust parser
pattern = r'def parse_words\(tsv: str, min_conf: float = -1\.0\) -> list\[dict\]:[\s\S]*?\n\n(?=def normalize_line\()'

replacement = r'''def parse_words(tsv: str, min_conf: float = -1.0) -> list[dict]:
    raw = str(tsv or "").lstrip("\ufeff")

    if not raw.strip():
        return []

    reader = csv.DictReader(io.StringIO(raw), delimiter="\t")
    words = []

    for row in reader:
        clean_row = {
            str(k or "").lstrip("\ufeff").strip(): v
            for k, v in row.items()
        }

        level = str(clean_row.get("level") or "").strip()

        if level != "5":
            continue

        word_text = str(clean_row.get("text") or "").strip()

        if not word_text:
            continue

        try:
            conf = float(str(clean_row.get("conf") or "-1").replace(",", "."))
            left = int(float(str(clean_row.get("left") or "0").replace(",", ".")))
            top = int(float(str(clean_row.get("top") or "0").replace(",", ".")))
            width = int(float(str(clean_row.get("width") or "0").replace(",", ".")))
            height = int(float(str(clean_row.get("height") or "0").replace(",", ".")))
        except Exception:
            continue

        if min_conf >= 0 and conf >= 0 and conf < min_conf:
            continue

        if width <= 0 or height <= 0:
            continue

        words.append(
            {
                "text": word_text,
                "conf": conf,
                "left": left,
                "top": top,
                "right": left + width,
                "bottom": top + height,
                "cx": left + width / 2,
                "cy": top + height / 2,
                "height": height,
            }
        )

    return words

'''

text, count = re.subn(pattern, replacement, text)

if count != 1:
    raise SystemExit(f"Could not replace parse_words. Replacements: {count}")


# 3. Ensure diagnostics are added
if "tsv_preview =" not in text:
    text = text.replace(
'''        words = parse_words(tsv, min_conf=args.min_conf)

        text, layout_report = page_words_to_text(
''',
'''        tsv_preview = "\\n".join(str(tsv or "").splitlines()[:8])
        words = parse_words(tsv, min_conf=args.min_conf)

        text, layout_report = page_words_to_text(
'''
    )

if '"tsv_chars": len(tsv or ""),' not in text:
    text = text.replace(
'''                "returncode": code,
                **layout_report,
''',
'''                "returncode": code,
                "tsv_chars": len(tsv or ""),
                "tsv_preview": tsv_preview,
                "parsed_words": len(words),
                **layout_report,
'''
    )

path.write_text(text, encoding="utf-8")
print("OK: TSV OCR fixed to use tessedit_create_tsv=1 and robust parser.")
