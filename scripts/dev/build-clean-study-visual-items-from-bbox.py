from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _fail(message: str) -> None:
    raise SystemExit(message)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        _fail("FAILED_LOAD_JSON=" + str(path) + "::" + str(exc))

    if not isinstance(payload, dict):
        _fail("FAILED_PAYLOAD_NOT_OBJECT=" + str(path))

    return payload


def _study_answer_for_item(item: dict[str, Any]) -> str:
    decision = _text(item.get("user_decision"))
    candidate = _text(item.get("ocr_math_candidate_text"))
    corrected = _text(item.get("user_corrected_text"))

    if decision == "edit":
        if not corrected:
            _fail("FAILED_EDITED_READY_ITEM_WITHOUT_CORRECTED_TEXT=" + _text(item.get("item_id")))
        return corrected

    if decision == "accept":
        if not candidate:
            _fail("FAILED_ACCEPTED_READY_ITEM_WITHOUT_CANDIDATE_TEXT=" + _text(item.get("item_id")))
        return candidate

    _fail("FAILED_UNSUPPORTED_READY_DECISION=" + decision)


def _prompt_for_kind(kind: str, page: int) -> str:
    labels = {
        "formula": "Explică formula validată din document.",
        "figure": "Explică figura validată din document.",
        "diagram": "Explică diagrama validată din document.",
        "table": "Explică tabelul validat din document.",
        "symbol": "Explică simbolul validat din document.",
        "mixed": "Explică elementul vizual validat din document.",
        "unknown": "Explică elementul vizual validat din document.",
    }
    base = labels.get(kind, labels["unknown"])
    return f"{base} Sursa: pagina {page}."


def build_clean_study_visual_items(visual_items_path: Path, output_root: Path) -> dict[str, Any]:
    payload = _load_json(visual_items_path)

    if payload.get("schema_version") != "v0.8.67":
        _fail("FAILED_SCHEMA_VERSION_NOT_V0867")

    items = payload.get("items")
    if not isinstance(items, list):
        _fail("FAILED_ITEMS_NOT_LIST")

    course_id = _text(payload.get("course_id"))
    source_pdf = _text(payload.get("source_pdf"))

    study_items: list[dict[str, Any]] = []
    excluded_items: list[dict[str, Any]] = []

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            _fail(f"FAILED_ITEM_NOT_OBJECT={index}")

        item_id = _text(item.get("item_id"))
        decision = _text(item.get("user_decision"))
        ready = item.get("ready_for_study") is True
        kind = _text(item.get("kind")) or "unknown"
        page = item.get("page")

        if not isinstance(page, int) or page < 1:
            _fail("FAILED_ITEM_PAGE_INVALID=" + item_id)

        if not ready or decision not in {"accept", "edit"}:
            excluded_items.append(
                {
                    "source_visual_item_id": item_id,
                    "user_decision": decision or "pending",
                    "ready_for_study": bool(ready),
                    "reason": "not_ready_or_not_accept_edit",
                }
            )
            continue

        if item.get("crop_exists") is not True:
            _fail("FAILED_READY_ITEM_REQUIRES_CROP_EXISTS_TRUE=" + item_id)

        crop_path = _text(item.get("crop_path"))
        if not crop_path:
            _fail("FAILED_READY_ITEM_REQUIRES_CROP_PATH=" + item_id)

        answer = _study_answer_for_item(item)
        explanation = _text(item.get("user_explanation"))

        study_items.append(
            {
                "schema_version": "v0.8.72",
                "study_item_id": "visual-study-" + item_id,
                "source_visual_item_id": item_id,
                "source_pdf": source_pdf,
                "page": page,
                "kind": kind,
                "title": f"Element vizual validat — pagina {page}",
                "prompt": _prompt_for_kind(kind, page),
                "answer": answer,
                "explanation": explanation,
                "image": {
                    "crop_path": crop_path,
                    "alt": f"Element vizual validat din pagina {page}",
                },
                "learning_source": "validated_bbox_visual_item",
                "user_decision": decision,
                "ready_for_clean_study": True,
            }
        )

    output_dir = output_root / "formula_visual_evidence"
    output_dir.mkdir(parents=True, exist_ok=True)

    clean_study_path = output_dir / "visual_items.clean-study.preview.json"
    clean_study_payload = {
        "schema_version": "v0.8.72",
        "course_id": course_id,
        "source_pdf": source_pdf,
        "source_visual_items_path": str(visual_items_path),
        "item_count": len(study_items),
        "items": study_items,
        "excluded_count": len(excluded_items),
        "excluded_items": excluded_items,
    }
    clean_study_path.write_text(json.dumps(clean_study_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "visual_items_path": str(visual_items_path),
        "output_root": str(output_root),
        "clean_study_visual_items_path": str(clean_study_path),
        "source_item_count": len(items),
        "clean_study_item_count": len(study_items),
        "excluded_item_count": len(excluded_items),
        "accepted_count": sum(1 for item in study_items if item.get("user_decision") == "accept"),
        "edited_count": sum(1 for item in study_items if item.get("user_decision") == "edit"),
        "ignored_or_pending_excluded": len(excluded_items),
    }

    summary_path = output_dir / "visual_items.clean-study.preview-summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Clean Study visual preview items from validated bbox visual items.")
    parser.add_argument("--visual-items", required=True, help="Path to visual_items.bbox.validated.json")
    parser.add_argument("--output-root", required=True, help="Output root for clean study preview artifact")
    args = parser.parse_args()

    summary = build_clean_study_visual_items(
        visual_items_path=Path(args.visual_items),
        output_root=Path(args.output_root),
    )

    print("CLEAN_STUDY_VISUAL_ITEM_INGESTION=PASS")
    print("visual_items_path=" + summary["visual_items_path"])
    print("output_root=" + summary["output_root"])
    print("clean_study_visual_items_path=" + summary["clean_study_visual_items_path"])
    print("source_item_count=" + str(summary["source_item_count"]))
    print("clean_study_item_count=" + str(summary["clean_study_item_count"]))
    print("excluded_item_count=" + str(summary["excluded_item_count"]))
    print("accepted_count=" + str(summary["accepted_count"]))
    print("edited_count=" + str(summary["edited_count"]))
    print("ignored_or_pending_excluded=" + str(summary["ignored_or_pending_excluded"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
