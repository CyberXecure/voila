from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1"

MATH_SYMBOL_RE = re.compile(r"[∈∀∃⇔⇒≠≤≥〈〉⋅λβαπ√⎥⎦⎤⎢⎣]")
BROKEN_MATH_RE = re.compile(r"(?:[A-Za-z]\s*){0,2}[=+\-−⋅]\s*[=+\-−⋅]|[.,]\s*[.,]|\.{2,}")
LEARNING_CANDIDATE_RE = re.compile(
    r"defini[țt]ie|se\s+nume[șs]te|se\s+numesc|teorem[ăa]|observa[țt]ii|nota[țt]ii|produsul\s+scalar|func[țt]ii\s+trigonometrice",
    re.IGNORECASE,
)


def normalize_legacy_ro(text: str) -> str:
    return str(text or "").translate(
        str.maketrans({"ş": "ș", "Ş": "Ș", "ţ": "ț", "Ţ": "Ț"})
    )


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", normalize_legacy_ro(text)).strip()


def pages_from_data(data: dict[str, Any]) -> list[dict[str, Any]]:
    pages = data.get("pages")
    return pages if isinstance(pages, list) else []


def split_candidate_units(text: str) -> list[str]:
    normalized = compact(text)
    units: list[str] = []
    for sentence in re.split(r"(?<=[.!?])\s+", normalized):
        for part in re.split(r"\s*;\s*", sentence):
            item = compact(part)
            if len(item) >= 20:
                units.append(item)
    return units


def symbol_count(text: str) -> int:
    return len(MATH_SYMBOL_RE.findall(text))


def concept_terms(document_concepts: dict[str, Any] | None) -> set[str]:
    if not document_concepts:
        return set()
    concepts = document_concepts.get("concepts")
    if not isinstance(concepts, list):
        return set()
    return {
        compact(item.get("term", "")).lower()
        for item in concepts
        if isinstance(item, dict) and compact(item.get("term", ""))
    }


def has_concept_coverage(text: str, terms: set[str]) -> bool:
    lower = compact(text).lower()
    return any(term and term in lower for term in terms)


def learning_role_for(text: str) -> str:
    lower = compact(text).lower()

    if "se numește" in lower or "se numesc" in lower or "definiție" in lower or "definitie" in lower:
        return "definition"
    if "teoremă" in lower or "teorema" in lower:
        return "theorem"
    if "notații" in lower or "notatii" in lower or "coordonat" in lower:
        return "notation"
    if symbol_count(text) >= 4:
        return "formula"
    if "exemplu" in lower:
        return "example"
    return "glossary_term"


def issue_type_for(text: str, covered: bool) -> str:
    lower = compact(text).lower()

    if symbol_count(text) >= 6:
        return "ocr_math_uncertain"
    if BROKEN_MATH_RE.search(text):
        return "broken_line_join"
    if LEARNING_CANDIDATE_RE.search(text) and not covered:
        return "definition_candidate_uncertain"
    if "ş" in text or "ţ" in text:
        return "legacy_diacritic_or_encoding"
    if "vectoruluiv" in lower or "si " in lower:
        return "ocr_text_uncertain"
    return "concept_relation_uncertain"


def reason_codes_for(text: str, covered: bool) -> list[str]:
    reasons: list[str] = []

    if symbol_count(text) >= 6:
        reasons.append("many_math_symbols_or_formula_fragments")
    if BROKEN_MATH_RE.search(text):
        reasons.append("possible_broken_formula_or_joined_line")
    if LEARNING_CANDIDATE_RE.search(text) and not covered:
        reasons.append("learning_candidate_not_verified_by_extracted_concepts")
    if "ş" in text or "ţ" in text:
        reasons.append("legacy_romanian_diacritic")
    if "vectoruluiv" in text.lower():
        reasons.append("possible_missing_space_in_ocr")
    if not reasons:
        reasons.append("low_confidence_learning_context")

    return reasons


def confidence_for(text: str, covered: bool) -> float:
    confidence = 0.65

    if symbol_count(text) >= 6:
        confidence -= 0.25
    if BROKEN_MATH_RE.search(text):
        confidence -= 0.15
    if LEARNING_CANDIDATE_RE.search(text) and not covered:
        confidence -= 0.20
    if covered:
        confidence += 0.10

    return max(0.05, min(0.95, round(confidence, 2)))


def suggested_text_for(text: str) -> str:
    return compact(text).replace("vectoruluiv", "vectorului v").replace(" si ", " și ")


def build_review_items(pages: list[dict[str, Any]], document_concepts: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    terms = concept_terms(document_concepts)
    items: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()

    for page in pages:
        page_num = page.get("page")
        if not isinstance(page_num, int):
            continue

        for unit in split_candidate_units(str(page.get("text") or "")):
            covered = has_concept_coverage(unit, terms)
            should_review = (
                symbol_count(unit) >= 4
                or BROKEN_MATH_RE.search(unit) is not None
                or (LEARNING_CANDIDATE_RE.search(unit) is not None and not covered)
                or "vectoruluiv" in unit.lower()
            )

            if not should_review:
                continue

            key = (page_num, compact(unit).lower()[:160])
            if key in seen:
                continue
            seen.add(key)

            item_index = len(items) + 1
            issue_type = issue_type_for(unit, covered)
            learning_role = learning_role_for(unit)

            items.append(
                {
                    "review_item_id": f"R{item_index:03d}",
                    "source_pdf_page": page_num,
                    "source_text": compact(unit),
                    "suspect_text": compact(unit),
                    "suggested_text": suggested_text_for(unit),
                    "issue_type": issue_type,
                    "confidence": confidence_for(unit, covered),
                    "reason_codes": reason_codes_for(unit, covered),
                    "suggested_learning_role": learning_role,
                    "linked_concept_terms": sorted(term for term in terms if term and term in compact(unit).lower()),
                    "ocr_math_context": {
                        "symbol_count": symbol_count(unit),
                        "has_math_symbols": symbol_count(unit) > 0,
                        "ocr_math_report_available": False,
                    },
                    "requires_user_decision": True,
                    "allowed_decisions": [
                        "accepted",
                        "edited",
                        "ignored",
                        "marked_definition",
                        "marked_formula",
                        "marked_notation",
                        "marked_theorem",
                        "marked_example",
                        "marked_glossary_term",
                        "marked_not_relevant",
                    ],
                }
            )

    return items


def build_ocr_review_queue(pages_data: dict[str, Any], document_concepts: dict[str, Any] | None = None) -> dict[str, Any]:
    pages = pages_from_data(pages_data)
    items = build_review_items(pages, document_concepts)

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact": "ocr_review_queue",
        "source_file": pages_data.get("source_file"),
        "source_page_count": pages_data.get("page_count") or len(pages),
        "review_item_count": len(items),
        "review_items": items,
        "quality_gate": {
            "review_required": len(items) > 0,
            "generation_should_wait_for_review": len(items) > 0,
            "reason_codes": ["ocr_review_items_detected"] if items else [],
        },
        "learning_policy": {
            "ocr_review_is_user_assisted_document_learning": True,
            "user_corrections_become_verified_evidence": True,
            "feed_back_into_document_learning_pack": True,
            "do_not_generate_from_unresolved_blocked_items": True,
        },
        "policy": {
            "no_ui_implementation": True,
            "no_generate_integration": True,
            "no_lesson_generation": True,
            "no_quiz_generation": True,
            "no_flashcard_generation": True,
            "no_glossary_generation": True,
            "no_build": True,
            "no_zip": True,
            "no_delivery": True,
            "no_distribution": True,
        },
    }


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# OCR Review Queue",
        "",
        f"Source file: `{report.get('source_file')}`",
        f"Source pages: `{report.get('source_page_count')}`",
        f"Review item count: `{report.get('review_item_count')}`",
        f"Review required: `{report.get('quality_gate', {}).get('review_required')}`",
        "",
        "## Review items",
        "",
    ]

    for item in report.get("review_items") or []:
        reasons = ", ".join(item.get("reason_codes") or [])
        linked = ", ".join(item.get("linked_concept_terms") or [])
        lines.extend(
            [
                f"### {item.get('review_item_id')} · page {item.get('source_pdf_page')}",
                "",
                f"- Issue type: `{item.get('issue_type')}`",
                f"- Suggested learning role: `{item.get('suggested_learning_role')}`",
                f"- Confidence: `{item.get('confidence')}`",
                f"- Reasons: `{reasons}`",
                f"- Linked concepts: `{linked or 'n/a'}`",
                f"- Source text: {item.get('source_text')}",
                f"- Suggested text: {item.get('suggested_text')}",
                "",
            ]
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def load_json_optional(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    if not path.exists():
        raise FileNotFoundError(f"Optional JSON path not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_ocr_review_queue(
    pages_json: Path,
    output_dir: Path | None = None,
    document_concepts_json: Path | None = None,
) -> dict[str, Any]:
    pages_json = Path(pages_json).resolve()
    if not pages_json.exists():
        raise FileNotFoundError(f"pages.json not found: {pages_json}")

    pages_data = json.loads(pages_json.read_text(encoding="utf-8"))
    concepts_data = load_json_optional(Path(document_concepts_json).resolve() if document_concepts_json else None)
    report = build_ocr_review_queue(pages_data, concepts_data)

    target_dir = Path(output_dir).resolve() if output_dir else pages_json.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    json_path = target_dir / "ocr_review_queue.json"
    md_path = target_dir / "ocr_review_queue.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, md_path)

    return {
        "OCR_REVIEW_QUEUE_ARTIFACT": "PASS",
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "review_item_count": report["review_item_count"],
        "review_required": report["quality_gate"]["review_required"],
        "scope": "owner-local OCR Review queue artifact only; no UI, no generate integration, no build, no ZIP, no delivery, no distribution",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build owner-local OCR Review queue artifact from pages.json")
    parser.add_argument("pages_json", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--document-concepts-json", type=Path, default=None)
    args = parser.parse_args()

    print(
        json.dumps(
            write_ocr_review_queue(args.pages_json, args.output_dir, args.document_concepts_json),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
