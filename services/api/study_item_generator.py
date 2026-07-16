
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


BAD_PROMPT_PATTERNS = [
    "Ce precizare tehnică face sursa",
    "Care este ideea importantă",
    "Care este ideea principală",
    "Ce spune sursa",
    "What should you remember",
    "Name one key point",
    "Identify the main purpose",
]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _pages(value: Any) -> list[int]:
    if isinstance(value, list):
        result: list[int] = []
        for item in value:
            try:
                result.append(int(item))
            except Exception:
                continue
        return result
    try:
        return [int(value)]
    except Exception:
        return []


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_ready_gate(gate: dict[str, Any]) -> None:
    if gate.get("generate_readiness_status") != "PASS":
        raise ValueError("generate_readiness_gate is not PASS")
    if gate.get("ready_for_separate_generate_integration_milestone") is not True:
        raise ValueError("generate_readiness_gate does not allow separate integration milestone")


def _concept_specific_items(concept: dict[str, Any]) -> list[dict[str, Any]]:
    concept_id = _text(concept.get("concept_id"))
    term = _text(concept.get("term"))
    definition = _text(concept.get("definition"))
    evidence = _text(concept.get("evidence"))
    pages = _pages(concept.get("source_pdf_pages"))

    if not concept_id or not term or not definition:
        return []

    lower = term.lower()
    items: list[dict[str, Any]] = []

    def item(kind: str, question: str, answer: str, explanation: str, hint: str) -> dict[str, Any]:
        return {
            "item_id": f"{concept_id}-{kind}",
            "concept_id": concept_id,
            "term": term,
            "question_type": kind,
            "question": question,
            "expected_answer": answer,
            "hint": hint,
            "explanation": explanation,
            "source_pdf_pages": pages,
            "source_evidence": evidence,
            "generation_method": "v0.7.81_learning_pack_pedagogical_template_preview",
            "integration_status": "preview_only_not_used_by_study",
        }

    if lower == "segment orientat":
        items.append(item(
            "concept_understanding",
            "Ce înseamnă, în practică, un segment orientat?",
            "Un segment orientat este o pereche ordonată de puncte: primul punct indică originea, iar al doilea punct indică extremitatea.",
            "Cuvântul «ordonată» este important: ordinea punctelor arată direcția de parcurgere a segmentului.",
            "Gândește-te la o săgeată care pleacă din primul punct și ajunge în al doilea.",
        ))
        items.append(item(
            "why_it_matters",
            "De ce contează ordinea punctelor într-un segment orientat?",
            "Pentru că schimbarea ordinii schimbă sensul segmentului orientat: AB și BA au sensuri opuse.",
            "Un segment simplu nu are sens; un segment orientat are început și sfârșit.",
            "Compară segmentul AB cu segmentul BA și observă că sensul se schimbă.",
        ))

    elif lower == "vector":
        items.append(item(
            "concept_understanding",
            "Ce reprezintă un vector în lecția despre segmente orientate?",
            "Un vector reprezintă clasa segmentelor orientate care au aceeași direcție, aceeași lungime și același sens.",
            "Vectorul nu depinde doar de un desen anume, ci de proprietățile comune ale segmentelor orientate echivalente.",
            "Caută cele trei condiții: direcție, lungime, sens.",
        ))
        items.append(item(
            "conditions_check",
            "Ce trebuie să rămână la fel pentru ca două segmente orientate să reprezinte același vector?",
            "Trebuie să aibă aceeași direcție, aceeași lungime și același sens.",
            "Dacă una dintre aceste condiții se schimbă, nu mai vorbim despre același vector.",
            "Sunt trei condiții, nu una singură.",
        ))

    elif lower == "modul":
        items.append(item(
            "concept_understanding",
            "Ce măsoară modulul unui vector?",
            "Modulul măsoară lungimea vectorului, adică lungimea segmentului care îl reprezintă.",
            "În lecție, modulul este numit și lungime sau normă.",
            "Modulul răspunde la întrebarea «cât de lung este vectorul?»",
        ))

    elif lower == "direcție":
        items.append(item(
            "concept_understanding",
            "Cum recunoști direcția unui vector?",
            "Direcția este dată de dreapta pe care se află vectorul sau de orice dreaptă paralelă cu aceasta.",
            "Vectorii pot avea aceeași direcție chiar dacă sunt desenați în locuri diferite, dacă sunt pe drepte paralele.",
            "Nu confunda direcția cu sensul.",
        ))
        items.append(item(
            "distinction",
            "Care este diferența dintre direcție și sens?",
            "Direcția arată dreapta sau familia de drepte paralele, iar sensul arată orientarea pe acea direcție.",
            "Pe aceeași direcție poți avea două sensuri opuse.",
            "Imaginează o șosea: direcția este șoseaua, sensul este înainte sau înapoi.",
        ))

    elif lower == "vectori egali":
        items.append(item(
            "conditions_check",
            "Ce condiții trebuie să îndeplinească doi vectori ca să fie egali?",
            "Doi vectori sunt egali dacă au aceeași direcție, același sens și același modul.",
            "Egalitatea vectorilor cere toate cele trei condiții, nu doar aceeași lungime.",
            "Verifică direcția, sensul și lungimea.",
        ))
        items.append(item(
            "true_false",
            "Adevărat sau fals: doi vectori cu același modul sunt automat egali.",
            "Fals. Ei mai trebuie să aibă și aceeași direcție și același sens.",
            "Această întrebare verifică diferența dintre lungime și egalitate de vectori.",
            "Modulul este doar una dintre condiții.",
        ))

    elif lower == "vectori opuși":
        items.append(item(
            "concept_understanding",
            "Cum recunoști doi vectori opuși?",
            "Doi vectori sunt opuși dacă au aceeași direcție și același modul, dar sensuri contrare.",
            "Vectorii opuși păstrează direcția și lungimea, însă orientarea lor este inversă.",
            "Verifică mai întâi direcția și lungimea, apoi vezi dacă sensurile sunt contrare.",
        ))
        items.append(item(
            "distinction",
            "Care este diferența dintre vectori egali și vectori opuși?",
            "Vectorii egali au același sens, iar vectorii opuși au sensuri contrare, deși pot avea aceeași direcție și același modul.",
            "Diferența principală este sensul: egal înseamnă aceeași orientare, opus înseamnă orientare inversă.",
            "Compară cele trei criterii: direcție, modul și sens.",
        ))

    else:
        clean_definition = definition.rstrip(".")
        items.append(item(
            "concept_understanding",
            f"Cum ai explica pe scurt conceptul «{term}»?",
            f"Conceptul «{term}» înseamnă: {clean_definition}.",
            f"Este important să legi definiția de rolul ei în lecție, nu doar să repeți termenul.",
            "Încearcă să formulezi definiția cu propriile cuvinte.",
        ))

        if len(clean_definition) > 20:
            items.append(item(
                "apply_or_check",
                f"Ce trebuie să verifici când întâlnești «{term}» într-un exercițiu?",
                f"Trebuie să verifici ideea de bază: {clean_definition}.",
                "Întrebarea transformă definiția într-un criteriu de lucru pentru exerciții.",
                "Caută proprietatea principală a conceptului.",
            ))

    return items


def build_study_items_preview(output_dir: Path) -> dict[str, Any]:
    learning_pack_path = output_dir / "document_learning_pack.json"
    gate_path = output_dir / "generate_readiness_gate.json"

    if not learning_pack_path.exists():
        raise FileNotFoundError(learning_pack_path)
    if not gate_path.exists():
        raise FileNotFoundError(gate_path)

    learning_pack = _load_json(learning_pack_path)
    gate = _load_json(gate_path)

    if not isinstance(learning_pack, dict):
        raise ValueError("document_learning_pack.json must be an object")
    if not isinstance(gate, dict):
        raise ValueError("generate_readiness_gate.json must be an object")

    _require_ready_gate(gate)

    concepts = learning_pack.get("concept_summary", {}).get("concepts", [])
    if not isinstance(concepts, list):
        concepts = []

    items: list[dict[str, Any]] = []
    for concept in concepts:
        if isinstance(concept, dict):
            items.extend(_concept_specific_items(concept))

    item_ids: set[str] = set()
    unique_items: list[dict[str, Any]] = []
    for item in items:
        item_id = item["item_id"]
        if item_id in item_ids:
            continue
        item_ids.add(item_id)
        unique_items.append(item)

    bad_prompt_hits = [
        item for item in unique_items
        if any(pattern in item["question"] for pattern in BAD_PROMPT_PATTERNS)
    ]
    copied_answer_hits = [
        item for item in unique_items
        if item["question"].strip().lower() == item["expected_answer"].strip().lower()
    ]
    too_short_explanation_hits = [
        item for item in unique_items
        if len(item.get("explanation", "").strip()) < 40
    ]
    missing_hint_hits = [
        item for item in unique_items
        if len(item.get("hint", "").strip()) < 20
    ]

    quality_pass = (
        len(unique_items) >= 14
        and not bad_prompt_hits
        and not copied_answer_hits
        and not too_short_explanation_hits
        and not missing_hint_hits
    )

    return {
        "artifact": "study_items_preview",
        "artifact_version": "v0.7.81",
        "source_artifact": "document_learning_pack.json",
        "source_gate": "generate_readiness_gate.json",
        "generation_method": "deterministic_learning_pack_pedagogical_templates_no_llm",
        "integration_status": "preview_only_not_used_by_study",
        "course_id": output_dir.name,
        "item_count": len(unique_items),
        "concept_count": len(concepts),
        "items": unique_items,
        "quality_gate": {
            "preview_quality_status": "PASS" if quality_pass else "FAIL",
            "minimum_item_count": 14,
            "bad_prompt_hit_count": len(bad_prompt_hits),
            "copied_answer_hit_count": len(copied_answer_hits),
            "too_short_explanation_hit_count": len(too_short_explanation_hits),
            "missing_hint_hit_count": len(missing_hint_hits),
            "question_generation_changed": False,
            "bkt_logic_changed": False,
            "study_integration_changed": False,
            "preview_only": True,
        },
        "policy": {
            "uses_llm": False,
            "uses_cloud": False,
            "build_performed": False,
            "zip_created": False,
            "share_created": False,
            "delivery_performed": False,
            "distribution_performed": False,
        },
    }


def write_study_items_preview(output_dir: Path) -> Path:
    preview = build_study_items_preview(output_dir)
    path = output_dir / "study_items.preview.json"
    path.write_text(json.dumps(preview, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    path = write_study_items_preview(output_dir)
    preview = _load_json(path)
    gate = preview["quality_gate"]

    print("VOILA_V0_7_81_STUDY_ITEMS_PREVIEW_GENERATED=" + gate["preview_quality_status"])
    print("preview_path=" + str(path))
    print("item_count=" + str(preview["item_count"]))
    print("concept_count=" + str(preview["concept_count"]))
    print("bad_prompt_hit_count=" + str(gate["bad_prompt_hit_count"]))
    print("copied_answer_hit_count=" + str(gate["copied_answer_hit_count"]))
    print("too_short_explanation_hit_count=" + str(gate["too_short_explanation_hit_count"]))
    print("missing_hint_hit_count=" + str(gate["missing_hint_hit_count"]))
    print("question_generation_changed=False")
    print("bkt_logic_changed=False")
    print("study_integration_changed=False")
    print("BUILD_PERFORMED=False")
    print("ZIP_CREATED=False")
    print("SHARE_CREATED=False")
    print("DELIVERY_PERFORMED=False")
    return 0 if gate["preview_quality_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
