from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


MATH_TOKEN_RE = re.compile(
    r"(=|→|->|∈|⊂|€|ℝ|\bR\b|\blim\b|f\(x\)|g\(x\)|x[0o]|x₀|∞|oo|\+|-|ε|δ|sin|cos|tan|ln|arctan|arcsin)",
    re.IGNORECASE,
)

HIGH_CONFIDENCE_MATH_RE = re.compile(
    r"(\b[A-Z]\s*C\s*(?:R|ℝ)\b|\b[A-Z]\s*CR\b|\b(?:x[0o]|x₀)\s*[€E]\s*(?:R|ℝ)\b|\bx\s*(?:->|→)\s*x[0o]\b|[+\-−]\s*oo\b)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class OcrMathSuggestion:
    rule_id: str
    line_number: int
    original: str
    replacement: str
    severity: str
    reason: str


@dataclass(frozen=True)
class OcrMathLineResult:
    line_number: int
    original: str
    normalized: str
    line_type: str
    math_density: int
    suggestions: list[OcrMathSuggestion]


@dataclass(frozen=True)
class OcrMathDocumentResult:
    original_text: str
    normalized_text: str
    line_results: list[OcrMathLineResult]

    @property
    def suggestion_count(self) -> int:
        return sum(len(line.suggestions) for line in self.line_results)

    @property
    def changed_line_count(self) -> int:
        return sum(1 for line in self.line_results if line.original != line.normalized)


@dataclass(frozen=True)
class Rule:
    rule_id: str
    pattern: re.Pattern[str]
    replacement: str
    severity: str
    reason: str
    math_only: bool = True


RULES: tuple[Rule, ...] = (
    Rule(
        "arrow_x_to_x0",
        re.compile(r"\bx\s*(?:->|→)\s*x[0o]\b", re.IGNORECASE),
        "x → x₀",
        "high",
        "Normalizează limita x -> x0 la notația x → x₀.",
    ),
    Rule(
        "x0_element_real",
        re.compile(r"\b(?:x[0o]|x₀)\s*[€E]\s*(?:R|ℝ)\b", re.IGNORECASE),
        "x₀ ∈ ℝ",
        "high",
        "OCR a confundat simbolul ∈ cu € / E.",
    ),
    Rule(
        "variable_element_real",
        re.compile(r"\b([a-z])\s*[€]\s*(?:R|ℝ)\b"),
        r"\1 ∈ ℝ",
        "medium",
        "OCR a confundat simbolul ∈ cu €.",
    ),
    Rule(
        "subset_real_spaced",
        re.compile(r"\b([A-Z])\s*C\s*(?:R|ℝ)\b"),
        r"\1 ⊂ ℝ",
        "high",
        "OCR a citit incluziunea ca C R.",
    ),
    Rule(
        "subset_real_compact",
        re.compile(r"\b([A-Z])\s*CR\b"),
        r"\1 ⊂ ℝ",
        "high",
        "OCR a citit incluziunea compact, ca CR.",
    ),
    Rule(
        "element_plain_real",
        re.compile(r"∈\s*R\b"),
        "∈ ℝ",
        "medium",
        "Normalizează mulțimea numerelor reale la ℝ.",
    ),
    Rule(
        "subset_plain_real",
        re.compile(r"⊂\s*R\b"),
        "⊂ ℝ",
        "medium",
        "Normalizează mulțimea numerelor reale la ℝ.",
    ),
    Rule(
        "x0_subscript",
        re.compile(r"\bx[0o]\b", re.IGNORECASE),
        "x₀",
        "high",
        "Normalizează indicele OCR xo/x0 la x₀.",
    ),
    Rule(
        "plus_infinity",
        re.compile(r"\+\s*oo\b", re.IGNORECASE),
        "+∞",
        "medium",
        "Normalizează +oo la +∞.",
    ),
    Rule(
        "minus_infinity",
        re.compile(r"(?:-|\−)\s*oo\b", re.IGNORECASE),
        "−∞",
        "medium",
        "Normalizează -oo la −∞.",
    ),
    Rule(
        "romanian_functii",
        re.compile(r"\bfunctii\b", re.IGNORECASE),
        "funcții",
        "low",
        "Corectează diacritice românești frecvente în OCR.",
        math_only=False,
    ),
    Rule(
        "romanian_numeste",
        re.compile(r"\bnumeste\b", re.IGNORECASE),
        "numește",
        "low",
        "Corectează diacritice românești frecvente în OCR.",
        math_only=False,
    ),
    Rule(
        "romanian_vecinatate",
        re.compile(r"\bvecina?tate\b", re.IGNORECASE),
        "vecinătate",
        "low",
        "Corectează diacritice românești frecvente în OCR.",
        math_only=False,
    ),
    Rule(
        "romanian_vecindate",
        re.compile(r"\bvecindate\b", re.IGNORECASE),
        "vecinătate",
        "low",
        "Corectează eroarea OCR vecindate.",
        math_only=False,
    ),
    Rule(
        "romanian_incat",
        re.compile(r"\bincat\b", re.IGNORECASE),
        "încât",
        "low",
        "Corectează diacritice românești frecvente în OCR.",
        math_only=False,
    ),
    Rule(
        "romanian_daca",
        re.compile(r"\bdaca\b", re.IGNORECASE),
        "dacă",
        "low",
        "Corectează diacritice românești frecvente în OCR.",
        math_only=False,
    ),
    Rule(
        "romanian_exista",
        re.compile(r"\bexista\b", re.IGNORECASE),
        "există",
        "low",
        "Corectează diacritice românești frecvente în OCR.",
        math_only=False,
    ),
)


def math_density(line: str) -> int:
    return len(MATH_TOKEN_RE.findall(line or ""))


def classify_line(line: str) -> str:
    density = math_density(line)
    if HIGH_CONFIDENCE_MATH_RE.search(line or ""):
        return "math"
    if density >= 6:
        return "math"
    if density >= 2:
        return "mixed"
    return "text"


def _replacement_for_match(rule: Rule, match: re.Match[str]) -> str:
    return match.expand(rule.replacement)


def normalize_line(line: str, line_number: int = 1) -> OcrMathLineResult:
    line_type = classify_line(line)
    density = math_density(line)
    normalized = line
    suggestions: list[OcrMathSuggestion] = []

    for rule in RULES:
        if rule.math_only and line_type == "text":
            continue

        matches = list(rule.pattern.finditer(normalized))
        if not matches:
            continue

        for match in matches:
            original = match.group(0)
            replacement = _replacement_for_match(rule, match)
            if original != replacement:
                suggestions.append(
                    OcrMathSuggestion(
                        rule_id=rule.rule_id,
                        line_number=line_number,
                        original=original,
                        replacement=replacement,
                        severity=rule.severity,
                        reason=rule.reason,
                    )
                )

        normalized = rule.pattern.sub(rule.replacement, normalized)

    return OcrMathLineResult(
        line_number=line_number,
        original=line,
        normalized=normalized,
        line_type=line_type,
        math_density=density,
        suggestions=suggestions,
    )


def normalize_text(text: str) -> OcrMathDocumentResult:
    original_text = str(text or "")
    lines = original_text.splitlines()
    results = [normalize_line(line, index + 1) for index, line in enumerate(lines)]
    normalized_text = "\n".join(result.normalized for result in results)

    if original_text.endswith("\n"):
        normalized_text += "\n"

    return OcrMathDocumentResult(
        original_text=original_text,
        normalized_text=normalized_text,
        line_results=results,
    )


def document_result_to_dict(result: OcrMathDocumentResult) -> dict:
    data = asdict(result)
    data["suggestion_count"] = result.suggestion_count
    data["changed_line_count"] = result.changed_line_count
    return data


def run_self_test() -> dict:
    sample = "\n".join(
        [
            "V CR se numeste:",
            "a) vecindate a unui numar real xo € R, daca exista φ > 0 astfel incat (xo - ε, xo + ε) C V;",
            "x -> xo f(x) = 0; +oo si -oo",
        ]
    )

    result = normalize_text(sample)
    normalized = result.normalized_text

    expected = [
        "V ⊂ ℝ",
        "x₀ ∈ ℝ",
        "x → x₀",
        "+∞",
        "−∞",
        "numește",
        "vecinătate",
        "dacă",
        "există",
        "încât",
    ]

    missing = [item for item in expected if item not in normalized]

    return {
        "sample": sample,
        "normalized": normalized,
        "expected_missing": missing,
        "suggestion_count": result.suggestion_count,
        "changed_line_count": result.changed_line_count,
        "pass": not missing and result.suggestion_count >= 8,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Voila OCR math normalizer engine")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--text-file", type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-text", type=Path)
    args = parser.parse_args()

    if args.self_test:
        data = run_self_test()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0 if data["pass"] else 1

    if not args.text_file:
        parser.error("--text-file is required unless --self-test is used")

    text = args.text_file.read_text(encoding="utf-8", errors="replace")
    result = normalize_text(text)

    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(
            json.dumps(document_result_to_dict(result), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    if args.out_text:
        args.out_text.parent.mkdir(parents=True, exist_ok=True)
        args.out_text.write_text(result.normalized_text, encoding="utf-8")

    print(
        json.dumps(
            {
                "suggestion_count": result.suggestion_count,
                "changed_line_count": result.changed_line_count,
            },
            ensure_ascii=False,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
