from pathlib import Path
import re

path = Path("services/api/ocr_body_columns_tesseract_pages.py")
text = path.read_text(encoding="utf-8")

# Add plain text tesseract fallback after run_tesseract_tsv
if "def run_tesseract_text(" not in text:
    marker = "\ndef parse_tsv_lines(tsv: str) -> list[dict]:"
    insert = r'''

def run_tesseract_text(
    img: Image.Image,
    tesseract: str,
    lang: str,
    psm: int,
    tessdata_prefix: str | None,
) -> tuple[str, float, int]:
    env = os.environ.copy()

    if tessdata_prefix:
        env["TESSDATA_PREFIX"] = tessdata_prefix

    start = time.time()

    with tempfile.TemporaryDirectory() as tmp:
        image_path = Path(tmp) / "crop.png"
        img.save(image_path)

        cmd = [
            tesseract,
            str(image_path),
            "stdout",
            "-l",
            lang,
            "--psm",
            str(psm),
        ]

        result = subprocess.run(
            cmd,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env=env,
        )

    return (result.stdout or "").replace("\f", "").strip(), time.time() - start, result.returncode
'''
    text = text.replace(marker, insert + marker)


# Add plain text filter before ocr_image_text
if "def plain_text_to_body_text(" not in text:
    marker = "\ndef ocr_image_text("
    insert = r'''

def looks_like_plain_body_line(line: str) -> bool:
    value = normalize_line(line)

    if not value:
        return False

    if is_caption_start(value):
        return False

    lower = value.lower()

    if re.match(r"^[\|\-—–_.,;:()\[\]{}<>/\\0-9\s%°]+$", value):
        return False

    letters = len(re.findall(rf"[{RO_LETTERS}]", value))
    digits = len(re.findall(r"\d", value))
    weird = len(re.findall(r"[|<>~`^_=◆◇□■]", value))
    chars = max(1, len(value))

    if letters < 4:
        return False

    if weird / chars > 0.22:
        return False

    if digits > letters * 2 and letters < 20:
        return False

    if re.search(r"\b(y[o0]|wey|fOr|isu|vv|sns|fires)\b", lower):
        return False

    return True


def plain_text_to_body_text(raw: str) -> str:
    lines = [normalize_line(line) for line in str(raw or "").splitlines()]
    lines = [line for line in lines if line]

    kept = []
    caption_skip = 0

    for line in lines:
        lower = line.lower()

        if is_caption_start(line):
            caption_skip = 5
            continue

        if caption_skip > 0:
            # Skip caption continuations: labels, numbered parts, short technical legend lines.
            if (
                len(line) < 95
                or re.match(r"^\s*[0-9a-z]\s*[-–]", lower)
                or re.match(r"^\s*[0-9]+\s*[-–]", lower)
                or re.search(r"\b(balonul|filamentul|electrodul|suportul|soclu|tubul|intrare curent|înveliș)\b", lower)
            ):
                caption_skip -= 1
                continue

            caption_skip = 0

        if looks_like_plain_body_line(line):
            kept.append(line)

    # Join paragraph-like lines, preserving visible paragraph gaps only lightly.
    out = []
    for line in kept:
        if out and out[-1].endswith("-"):
            out[-1] = out[-1][:-1] + line
        else:
            out.append(line)

    return "\n".join(out).strip()
'''
    text = text.replace(marker, insert + marker)


# Replace ocr_image_text with fallback-aware version
pattern = r'def ocr_image_text\([\s\S]*?\n\n(?=def save_json\()'

replacement = r'''def ocr_image_text(
    img: Image.Image,
    tesseract: str,
    lang: str,
    psm: int,
    tessdata_prefix: str | None,
) -> tuple[str, dict]:
    tsv, seconds, code = run_tesseract_tsv(
        img,
        tesseract=tesseract,
        lang=lang,
        psm=psm,
        tessdata_prefix=tessdata_prefix,
    )

    lines = parse_tsv_lines(tsv)
    text = lines_to_text(lines)

    report = {
        "seconds": round(seconds, 3),
        "returncode": code,
        "raw_lines": len(lines),
        "kept_chars": len(text),
        "fallback": False,
    }

    # If TSV filtering was too aggressive, fall back to plain OCR + gentler filtering.
    if len(text.strip()) >= 40:
        return text, report

    plain, seconds2, code2 = run_tesseract_text(
        img,
        tesseract=tesseract,
        lang=lang,
        psm=psm,
        tessdata_prefix=tessdata_prefix,
    )

    fallback_text = plain_text_to_body_text(plain)

    if fallback_text.strip():
        report.update(
            {
                "fallback": True,
                "fallback_seconds": round(seconds2, 3),
                "fallback_returncode": code2,
                "fallback_raw_chars": len(plain),
                "fallback_kept_chars": len(fallback_text),
            }
        )
        return fallback_text, report

    report.update(
        {
            "fallback": True,
            "fallback_seconds": round(seconds2, 3),
            "fallback_returncode": code2,
            "fallback_raw_chars": len(plain),
            "fallback_kept_chars": 0,
        }
    )

    return text, report

'''

text, count = re.subn(pattern, replacement, text)

if count != 1:
    raise SystemExit(f"Could not replace ocr_image_text safely. Replacements: {count}")

path.write_text(text, encoding="utf-8")
print("OK: body-column OCR fallback added.")
