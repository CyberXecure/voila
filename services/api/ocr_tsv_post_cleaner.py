from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

RO = "A-Za-zĂÂÎȘȚăâîșț"


def norm(s: str) -> str:
    s = str(s or "")
    s = s.replace("ﬁ", "fi").replace("ﬂ", "fl")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def strip_leading_noise(s: str) -> str:
    s = norm(s)
    s = re.sub(r"^[\s\|\]\[\(\)'\"`´~:;.,_—–\\/-]+", "", s)
    s = re.sub(r"^[a-z]\s+(?=[A-ZĂÂÎȘȚ])", "", s)
    return s.strip()


def remove_tsv_number_leaks(s: str) -> str:
    # Example: "metal 5 1 1 1 10 9 832 403 74 18 96.367599 halide"
    s = re.sub(r"(?:\s+\d+(?:\.\d+)?){5,}\s*", " ", s)
    return norm(s)


def is_fig_or_caption_start(s: str) -> bool:
    x = strip_leading_noise(s).lower()
    return bool(
        re.search(r"\bfig[\.\s]*[0-9ivxl]+", x)
        or re.search(r"\bfigura\s*[0-9ivxl]+", x)
        or re.search(r"\bvariația procentuală\b", x)
        or re.search(r"\bvariatia procentuala\b", x)
        or re.search(r"\blampa cu lumin[ăa] mixt", x)
    )


def is_noise(s: str) -> bool:
    x = strip_leading_noise(s)
    low = x.lower()

    if not x:
        return True

    if is_fig_or_caption_start(x):
        return True

    if re.match(r"^[\|\-—–_.,;:()\[\]{}<>/\\0-9\s%°]+$", x):
        return True

    bad = [
        "deea", "ft)", "dee", "ioe", "fey", "wate", "sires", "fires",
        "sns", "isu", "wth", "tan", "bora mi", "ciot", "cuvapori",
        "cere]", "eai", "sue saul", "alimnentaa", "dliieriieja",
    ]

    if any(token in low for token in bad):
        return True

    legend_words = [
        "balonul", "filamentul", "electrodul", "suportul", "soclu",
        "tubul", "tubului", "intrare curent", "înveliș", "invelis",
        "dispozitiv", "vidului", "intensitatea", "puterea",
        "fluxul luminos", "tensiunea",
    ]

    if any(w in low for w in legend_words) and len(x) < 170:
        return True

    letters = len(re.findall(rf"[{RO}]", x))
    digits = len(re.findall(r"\d", x))
    weird = len(re.findall(r"[|<>~`^_=◆◇□■\\]", x))
    chars = max(1, len(x))

    if letters < 4:
        return True

    if weird / chars > 0.15:
        return True

    if digits > letters * 2 and letters < 35:
        return True

    tokens = re.findall(rf"[{RO}0-9]+", x)
    if tokens:
        short = [t for t in tokens if len(t) <= 2]
        if len(tokens) <= 6 and len(short) >= max(3, len(tokens) - 1):
            return True

    return False


def clean_text(text: str) -> str:
    lines = [norm(line) for line in str(text or "").splitlines()]
    lines = [line for line in lines if line]

    out = []
    skip_caption = 0

    for raw in lines:
        line = strip_leading_noise(raw)
        line = remove_tsv_number_leaks(line)

        if not line:
            continue

        if is_fig_or_caption_start(line):
            skip_caption = 10
            continue

        if skip_caption > 0:
            if is_noise(line) or len(line) < 140:
                skip_caption -= 1
                continue
            skip_caption = 0

        if is_noise(line):
            continue

        # Light cleanup only, no invented text.
        line = re.sub(r"\bprincipiu!\b", "principiul", line)
        line = re.sub(r"\bdoficitară\b", "deficitară", line)
        line = re.sub(r"\bfilarnentul\b", "filamentul", line)
        line = re.sub(r"\binalta\b", "înaltă", line)
        line = re.sub(r"\bmixta\b", "mixtă", line)
        line = re.sub(r"\blumina\b", "lumină", line)
        line = re.sub(r"\bPalpairea\b", "Pâlpâirea", line)
        line = re.sub(r"\bVariatia\b", "Variația", line)

        line = norm(line)

        if line:
            out.append(line)

    merged = []

    for line in out:
        if merged and merged[-1].endswith("-"):
            merged[-1] = merged[-1][:-1] + line
        else:
            merged.append(line)

    return "\n".join(merged).strip()


def write_md(path: Path, payload: dict) -> None:
    lines = [
        "# OCR TSV columns post-cleaned pages",
        "",
    ]

    for page in payload.get("pages", []):
        lines.append(f"## Page {page.get('page_number')}")
        lines.append("")
        lines.append(str(page.get("text") or "").strip())
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_json")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()

    src = Path(args.input_json)
    payload = json.loads(src.read_text(encoding="utf-8"))

    before = 0
    after = 0

    for page in payload.get("pages", []):
        old = str(page.get("text") or "")
        new = clean_text(old)

        before += len(old)
        after += len(new)

        page["text_before_post_clean_chars"] = len(old)
        page["text"] = new
        page["text_source"] = str(page.get("text_source") or "") + "+tsv_post_clean_v2"

    if args.replace:
        backup = src.with_name(src.name + ".before_tsv_post_clean_v2")
        if not backup.exists():
            backup.write_text(src.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
        out_json = src
    else:
        out_json = src.with_name(src.stem + ".post_clean.json")

    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    out_md = out_json.with_suffix(".md")
    write_md(out_md, payload)

    print("Voila TSV post-clean complete.")
    print("Input:", src)
    print("Output JSON:", out_json)
    print("Output MD:", out_md)
    print("Chars before:", before)
    print("Chars after:", after)


if __name__ == "__main__":
    main()
