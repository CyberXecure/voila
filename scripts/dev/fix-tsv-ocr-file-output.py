from pathlib import Path
import re

path = Path("services/api/ocr_tsv_columns_tesseract_pages.py")
text = path.read_text(encoding="utf-8")

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
            "tsv",
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
            # Fallback for Tesseract builds that still emit TSV to stdout.
            tsv = result.stdout or ""

    return tsv, elapsed, result.returncode

'''

text, count = re.subn(pattern, replacement, text)

if count != 1:
    raise SystemExit(f"Could not replace run_tesseract_tsv. Replacements: {count}")

path.write_text(text, encoding="utf-8")
print("OK: TSV OCR now reads Tesseract .tsv file output.")
