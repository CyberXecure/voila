from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1"

RO_SIGNALS = {
    "vector", "segment", "orientat", "direcție", "directie", "sens",
    "modul", "coordonate", "trigonometrie", "punct", "dreaptă", "dreapta",
}

MATH_SIGNALS = {
    "vector", "vectori", "segment", "orientat", "direcție", "directie",
    "sens", "modul", "coordonate", "trigonometrie", "coliniari", "punct",
}


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def normalize_term(term: str) -> str:
    term = compact(term).strip(" ,.;:-")
    lower = term.lower()

    replacements = {
        "modulul unui vector": "modul",
        "modulul": "modul",
        "segmentul orientat": "segment orientat",
        "un segment orientat": "segment orientat",
    }

    return replacements.get(lower, lower)


def pages_from_data(data: dict[str, Any]) -> list[dict[str, Any]]:
    pages = data.get("pages")
    return pages if isinstance(pages, list) else []


def all_text(data: dict[str, Any]) -> str:
    return "\n".join(str(page.get("text") or "") for page in pages_from_data(data))


def page_refs(pages: list[dict[str, Any]], evidence: str) -> list[int]:
    refs: list[int] = []
    needle = compact(evidence).lower()[:80]
    if not needle:
        return refs

    for page in pages:
        text = compact(page.get("text") or "").lower()
        if needle in text and isinstance(page.get("page"), int):
            refs.append(page["page"])

    return sorted(set(refs))


def detect_language(text: str) -> dict[str, Any]:
    lower = compact(text).lower()
    ro_hits = sum(1 for word in RO_SIGNALS if word in lower)
    diacritics = len(re.findall(r"[ăâîșțĂÂÎȘȚ]", text))

    if ro_hits or diacritics:
        return {
            "code": "ro",
            "confidence": min(0.95, 0.5 + ro_hits * 0.05 + min(0.2, diacritics * 0.01)),
            "signals": {"romanian_hits": ro_hits, "diacritic_hits": diacritics},
        }

    return {
        "code": "unknown",
        "confidence": 0.2,
        "signals": {"romanian_hits": 0, "diacritic_hits": 0},
    }


def detect_domain(text: str) -> dict[str, Any]:
    lower = compact(text).lower()
    hits = sorted(word for word in MATH_SIGNALS if word in lower)

    if len(hits) >= 2:
        return {
            "name": "mathematics",
            "confidence": min(0.95, 0.5 + len(hits) * 0.05),
            "signals": hits,
        }

    return {
        "name": "general",
        "confidence": 0.25,
        "signals": hits,
    }


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", compact(text))
    return [part.strip() for part in parts if len(part.strip()) >= 12]


def add_concept(
    concepts: dict[str, dict[str, Any]],
    *,
    term: str,
    definition: str,
    evidence: str,
    pages: list[dict[str, Any]],
    method: str,
) -> None:
    clean_term = normalize_term(term)
    clean_definition = compact(definition).strip(" ,.;:-")

    if not clean_term or len(clean_term) < 2:
        return
    if not clean_definition or len(clean_definition) < 8:
        return

    key = clean_term.lower()

    if key not in concepts:
        concepts[key] = {
            "term": clean_term,
            "definition": clean_definition,
            "kind": "concept",
            "source_pdf_pages": page_refs(pages, evidence),
            "evidence": compact(evidence)[:500],
            "extraction_method": method,
        }


def extract_concepts(text: str, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    concepts: dict[str, dict[str, Any]] = {}

    for sentence in split_sentences(text):
        lower = sentence.lower()

        if "se numește" in lower or "se numeste" in lower:
            marker = "se numește" if "se numește" in lower else "se numeste"
            after = sentence[lower.index(marker) + len(marker):].strip(" ,.;:-")
            if "," in after:
                term, definition = after.split(",", 1)
                add_concept(
                    concepts,
                    term=term,
                    definition=definition,
                    evidence=sentence,
                    pages=pages,
                    method="romanian_definition_se_numeste",
                )

        match = re.search(r"\b(Segmentul orientat|Modulul unui vector|Modulul)\s+este\s+(.+)", sentence, flags=re.IGNORECASE)
        if match:
            add_concept(
                concepts,
                term=match.group(1),
                definition=match.group(2),
                evidence=sentence,
                pages=pages,
                method="romanian_definition_este",
            )

    return list(concepts.values())


def build_document_concepts(data: dict[str, Any]) -> dict[str, Any]:
    pages = pages_from_data(data)
    text = all_text(data)
    concepts = extract_concepts(text, pages)
    quality = "PASS" if len(concepts) >= 3 else "LOW_QUALITY_BLOCKED"

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact": "document_concepts",
        "source_file": data.get("source_file"),
        "source_page_count": data.get("page_count") or len(pages),
        "source_language": detect_language(text),
        "detected_domain": detect_domain(text),
        "concept_count": len(concepts),
        "concepts": concepts,
        "quality": {
            "generation_quality_status": quality,
            "reason_codes": [] if quality == "PASS" else ["too_few_document_concepts_detected"],
            "minimum_recommended_concepts": 3,
            "content_is_document_specific": True,
            "static_technical_terms_primary_source": False,
        },
        "policy": {
            "source_language_preserved": True,
            "translation_is_additive_not_replacement": True,
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
        "# Document concepts",
        "",
        f"Source file: `{report.get('source_file')}`",
        f"Language: `{report.get('source_language', {}).get('code')}`",
        f"Domain: `{report.get('detected_domain', {}).get('name')}`",
        f"Concept count: `{report.get('concept_count')}`",
        f"Quality: `{report.get('quality', {}).get('generation_quality_status')}`",
        "",
        "## Concepts",
        "",
    ]

    for index, concept in enumerate(report.get("concepts") or [], start=1):
        pages = ", ".join(str(p) for p in concept.get("source_pdf_pages") or [])
        lines.extend([
            f"### {index}. {concept.get('term')}",
            "",
            f"- Definition: {concept.get('definition')}",
            f"- Source pages: `{pages or 'n/a'}`",
            f"- Method: `{concept.get('extraction_method')}`",
            "",
        ])

    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_document_concepts(pages_json: Path, output_dir: Path | None = None) -> dict[str, Any]:
    pages_json = Path(pages_json).resolve()
    if not pages_json.exists():
        raise FileNotFoundError(f"pages.json not found: {pages_json}")

    data = json.loads(pages_json.read_text(encoding="utf-8"))
    report = build_document_concepts(data)

    target_dir = Path(output_dir).resolve() if output_dir else pages_json.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    json_path = target_dir / "document_concepts.json"
    md_path = target_dir / "document_concepts.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, md_path)

    return {
        "DOCUMENT_CONCEPTS_ARTIFACT": "PASS",
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "concept_count": report["concept_count"],
        "quality_status": report["quality"]["generation_quality_status"],
        "source_language": report["source_language"]["code"],
        "detected_domain": report["detected_domain"]["name"],
        "scope": "owner-local document concepts only; no generate integration; no build, no ZIP, no delivery, no distribution",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build owner-local document concepts artifact from pages.json")
    parser.add_argument("pages_json", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    print(json.dumps(write_document_concepts(args.pages_json, args.output_dir), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
