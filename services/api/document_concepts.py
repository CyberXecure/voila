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


def normalize_legacy_ro(text: str) -> str:
    return str(text or "").translate(
        str.maketrans(
            {
                "ş": "ș",
                "Ş": "Ș",
                "ţ": "ț",
                "Ţ": "Ț",
            }
        )
    )


def normalize_term(term: str) -> str:
    term = normalize_legacy_ro(compact(term)).strip(" ,.;:-")
    term = re.sub(r"^(?:definiție|definitie|observații|observatii)\s*:\s*", "", term, flags=re.IGNORECASE)
    term = term.replace("vectoruluiv", "vectorului v")
    term = term.replace("vectorulu i", "vectorului")
    lower = compact(term.lower())

    replacements = {
        "modulul unui vector": "modul",
        "modulul vectorului": "modul",
        "modulul": "modul",
        "modul": "modul",
        "segmentul orientat": "segment orientat",
        "un segment orientat": "segment orientat",
        "vectorii egali": "vectori egali",
        "vectorii opuși": "vectori opuși",
        "vectorii coliniari": "vectori coliniari",
        "vectorii necoliniari": "vectori necoliniari",
        "direcție": "direcție",
        "directie": "direcție",
        "sensul": "sens",
        "baza ortonormată": "bază ortonormată",
        "bază ortonormata": "bază ortonormată",
    }

    if lower.startswith("modul("):
        return "modul"
    if lower.startswith("coordonatele vectorului"):
        return "coordonatele vectorului"
    if lower.startswith("versorii axelor de coordonate"):
        return "versorii axelor de coordonate"

    return replacements.get(lower, lower)


def pages_from_data(data: dict[str, Any]) -> list[dict[str, Any]]:
    pages = data.get("pages")
    return pages if isinstance(pages, list) else []


def all_text(data: dict[str, Any]) -> str:
    return "\n".join(str(page.get("text") or "") for page in pages_from_data(data))


def page_refs(pages: list[dict[str, Any]], evidence: str) -> list[int]:
    refs: list[int] = []
    needle = normalize_legacy_ro(compact(evidence)).lower()[:80]
    if not needle:
        return refs

    for page in pages:
        text = normalize_legacy_ro(compact(page.get("text") or "")).lower()
        if needle in text and isinstance(page.get("page"), int):
            refs.append(page["page"])

    return sorted(set(refs))


def detect_language(text: str) -> dict[str, Any]:
    normalized = normalize_legacy_ro(text)
    lower = compact(normalized).lower()
    ro_hits = sum(1 for word in RO_SIGNALS if word in lower)
    diacritics = len(re.findall(r"[ăâîșțĂÂÎȘȚ]", normalized))

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
    lower = compact(normalize_legacy_ro(text)).lower()
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
    normalized = normalize_legacy_ro(text)
    parts = re.split(r"(?<=[.!?])\s+", compact(normalized))
    return [part.strip() for part in parts if len(part.strip()) >= 12]


def split_candidate_units(text: str) -> list[str]:
    units: list[str] = []

    for sentence in split_sentences(text):
        for part in re.split(r"\s*;\s*", sentence):
            cleaned = compact(part)
            if len(cleaned) >= 12:
                units.append(cleaned)

    return units


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
    clean_definition = compact(normalize_legacy_ro(definition)).strip(" ,.;:-")
    clean_definition = clean_definition.replace("vectoruluiv", "vectorului v").replace("vectorulu i", "vectorului")

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
            "evidence": compact(normalize_legacy_ro(evidence))[:500],
            "extraction_method": method,
        }


def extract_definition_markers(unit: str, pages: list[dict[str, Any]], concepts: dict[str, dict[str, Any]]) -> None:
    text = normalize_legacy_ro(unit)

    for match in re.finditer(
        r"(?:^|:\s*)se\s+numește\s+(?P<term>[^,.;:]{2,90})\s*,\s*(?P<definition>.+)$",
        text,
        flags=re.IGNORECASE,
    ):
        add_concept(
            concepts,
            term=match.group("term"),
            definition=match.group("definition"),
            evidence=unit,
            pages=pages,
            method="romanian_definition_se_numeste",
        )

    for match in re.finditer(
        r"(?:^|:\s*)se\s+numesc\s+(?P<term>[^,.;:]{2,90})\s*,\s*(?P<definition>.+)$",
        text,
        flags=re.IGNORECASE,
    ):
        add_concept(
            concepts,
            term=match.group("term"),
            definition=match.group("definition"),
            evidence=unit,
            pages=pages,
            method="romanian_definition_se_numesc",
        )

    match = re.search(
        r"doi\s+vectori\s+se\s+numesc\s+(?P<name>[^,.;:]+?)\s+dacă\s+(?P<definition>.+)$",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        add_concept(
            concepts,
            term=f"vectori {match.group('name')}",
            definition=f"Doi vectori se numesc {match.group('name')} dacă {match.group('definition')}",
            evidence=unit,
            pages=pages,
            method="romanian_vector_relation_daca",
        )

    match = re.search(
        r"^(?P<term>Segmentul orientat|Modulul unui vector|Modulul)\s+este\s+(?P<definition>.+)$",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        add_concept(
            concepts,
            term=match.group("term"),
            definition=match.group("definition"),
            evidence=unit,
            pages=pages,
            method="romanian_definition_este",
        )

    if re.search(r"\bse\s+numesc\s+necoliniari\b", text, flags=re.IGNORECASE):
        add_concept(
            concepts,
            term="vectori necoliniari",
            definition="vectori care nu sunt coliniari",
            evidence=unit,
            pages=pages,
            method="romanian_definition_necoliniari",
        )


def extract_characteristics(unit: str, pages: list[dict[str, Any]], concepts: dict[str, dict[str, Any]]) -> None:
    text = normalize_legacy_ro(unit)

    match = re.search(
        r"(?P<term>modul\s*\([^)]*\)|direcție|sens)\s*,\s*(?P<prefix>dat[ăa]?\s+de|indic(?:at|ată)\s+prin)\s+(?P<definition>.+)$",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        add_concept(
            concepts,
            term=match.group("term"),
            definition=match.group("definition"),
            evidence=unit,
            pages=pages,
            method="romanian_vector_characteristic",
        )


def extract_named_notation(unit: str, pages: list[dict[str, Any]], concepts: dict[str, dict[str, Any]]) -> None:
    text = normalize_legacy_ro(unit)

    if re.search(r"\bvectorii\s+.+\bformează\s+o\s+bază\b", text, flags=re.IGNORECASE):
        add_concept(
            concepts,
            term="bază",
            definition="vectori folosiți pentru exprimarea unui vector prin coordonate în acea bază",
            evidence=unit,
            pages=pages,
            method="romanian_named_structure_baza",
        )

    match = re.search(r"se\s+numesc\s+(coordonatele\s+vectorului\s*v[^.;]*)", text, flags=re.IGNORECASE)
    if match:
        add_concept(
            concepts,
            term="coordonatele vectorului",
            definition=match.group(1),
            evidence=unit,
            pages=pages,
            method="romanian_named_notation_coordinates",
        )

    match = re.search(r"se\s+numesc\s+(versorii\s+axelor\s+de\s+coordonate)", text, flags=re.IGNORECASE)
    if match:
        add_concept(
            concepts,
            term="versorii axelor de coordonate",
            definition="vectorii asociați axelor de coordonate",
            evidence=unit,
            pages=pages,
            method="romanian_named_notation_versors",
        )

    match = re.search(r"se\s+numește\s+(bază\s+ortonormată)", text, flags=re.IGNORECASE)
    if match:
        add_concept(
            concepts,
            term=match.group(1),
            definition="baza formată de versorii axelor de coordonate",
            evidence=unit,
            pages=pages,
            method="romanian_named_notation_orthonormal_basis",
        )

    if re.search(r"produsul\s+scalar\s+a\s+doi\s+vectori", text, flags=re.IGNORECASE):
        add_concept(
            concepts,
            term="produsul scalar",
            definition="operație între doi vectori nenuli, exprimată în document prin formule și unghiul dintre vectori",
            evidence=unit,
            pages=pages,
            method="romanian_named_formula_scalar_product",
        )

    if re.search(r"funcții\s+trigonometrice|funcţii\s+trigonometrice", text, flags=re.IGNORECASE):
        add_concept(
            concepts,
            term="funcții trigonometrice",
            definition="funcții precum sinus, cosinus, arcsinus și arccosinus, cu domenii și valori indicate în document",
            evidence=unit,
            pages=pages,
            method="romanian_named_section_trigonometric_functions",
        )


def extract_concepts(text: str, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    concepts: dict[str, dict[str, Any]] = {}

    for unit in split_candidate_units(text):
        extract_definition_markers(unit, pages, concepts)
        extract_characteristics(unit, pages, concepts)
        extract_named_notation(unit, pages, concepts)

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
