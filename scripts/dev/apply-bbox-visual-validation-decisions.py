from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ALLOWED_DECISIONS = {"accept", "edit", "ignore"}


def _fail(message: str) -> None:
    raise SystemExit(message)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        _fail("FAILED_LOAD_JSON=" + str(path) + "::" + str(exc))


def _decision_map(decisions_payload: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(decisions_payload, dict):
        _fail("FAILED_DECISIONS_PAYLOAD_NOT_OBJECT")

    raw_decisions = decisions_payload.get("decisions")
    if not isinstance(raw_decisions, list):
        _fail("FAILED_DECISIONS_LIST_MISSING")

    by_id: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(raw_decisions):
        if not isinstance(entry, dict):
            _fail(f"FAILED_DECISION_NOT_OBJECT={index}")

        item_id = _text(entry.get("item_id"))
        decision = _text(entry.get("user_decision"))

        if not item_id:
            _fail(f"FAILED_DECISION_ITEM_ID_EMPTY={index}")

        if decision not in ALLOWED_DECISIONS:
            _fail(f"FAILED_DECISION_VALUE_NOT_ALLOWED={index}:{decision}")

        if item_id in by_id:
            _fail("FAILED_DUPLICATE_DECISION_ITEM_ID=" + item_id)

        by_id[item_id] = entry

    return by_id


def _apply_decision(item: dict[str, Any], decision_entry: dict[str, Any]) -> dict[str, Any]:
    item_id = _text(item.get("item_id"))
    decision = _text(decision_entry.get("user_decision"))
    candidate = _text(item.get("ocr_math_candidate_text"))
    corrected = _text(decision_entry.get("user_corrected_text"))
    explanation = _text(decision_entry.get("user_explanation"))
    notes = _text(decision_entry.get("review_notes"))

    if item.get("crop_exists") is not True and decision in {"accept", "edit"}:
        _fail("FAILED_READY_DECISION_REQUIRES_CROP_EXISTS_TRUE=" + item_id)

    if decision == "accept":
        if not candidate:
            _fail("FAILED_ACCEPT_REQUIRES_CANDIDATE_TEXT=" + item_id)

        item["user_decision"] = "accept"
        item["user_corrected_text"] = ""
        item["user_explanation"] = explanation
        item["ready_for_study"] = True
        item["ocr_math_status"] = "validated_by_user"
        item["review_notes"] = notes or _text(item.get("review_notes"))

    elif decision == "edit":
        if not corrected:
            _fail("FAILED_EDIT_REQUIRES_USER_CORRECTED_TEXT=" + item_id)

        item["user_decision"] = "edit"
        item["user_corrected_text"] = corrected
        item["user_explanation"] = explanation
        item["ready_for_study"] = True
        item["ocr_math_status"] = "validated_by_user"
        item["review_notes"] = notes or _text(item.get("review_notes"))

    elif decision == "ignore":
        item["user_decision"] = "ignore"
        item["user_corrected_text"] = ""
        item["user_explanation"] = explanation
        item["ready_for_study"] = False
        item["ocr_math_status"] = "not_applicable"
        item["review_notes"] = notes or _text(item.get("review_notes"))

    else:
        _fail("FAILED_UNREACHABLE_DECISION=" + decision)

    return item


def apply_validation_decisions(
    visual_items_path: Path,
    decisions_path: Path,
    output_root: Path,
) -> dict[str, Any]:
    payload = _load_json(visual_items_path)
    decisions_payload = _load_json(decisions_path)

    if not isinstance(payload, dict):
        _fail("FAILED_VISUAL_ITEMS_PAYLOAD_NOT_OBJECT")

    items = payload.get("items")
    if not isinstance(items, list):
        _fail("FAILED_VISUAL_ITEMS_ITEMS_NOT_LIST")

    decisions = _decision_map(decisions_payload)

    seen_items: set[str] = set()
    applied = []
    unchanged_pending = []

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            _fail(f"FAILED_ITEM_NOT_OBJECT={index}")

        item_id = _text(item.get("item_id"))
        if not item_id:
            _fail(f"FAILED_ITEM_ID_EMPTY={index}")

        seen_items.add(item_id)

        if item_id not in decisions:
            item["user_decision"] = "pending"
            item["ready_for_study"] = False
            unchanged_pending.append(item_id)
            continue

        _apply_decision(item, decisions[item_id])
        applied.append(
            {
                "item_id": item_id,
                "user_decision": item.get("user_decision"),
                "ocr_math_status": item.get("ocr_math_status"),
                "ready_for_study": item.get("ready_for_study"),
            }
        )

    unknown_decision_ids = sorted(set(decisions) - seen_items)
    if unknown_decision_ids:
        _fail("FAILED_DECISIONS_REFERENCE_UNKNOWN_ITEM_IDS=" + json.dumps(unknown_decision_ids, ensure_ascii=False))

    ready_for_study_count = sum(
        1 for item in items if isinstance(item, dict) and item.get("ready_for_study") is True
    )
    accepted_count = sum(
        1 for item in items if isinstance(item, dict) and item.get("user_decision") == "accept"
    )
    edited_count = sum(
        1 for item in items if isinstance(item, dict) and item.get("user_decision") == "edit"
    )
    ignored_count = sum(
        1 for item in items if isinstance(item, dict) and item.get("user_decision") == "ignore"
    )
    pending_count = sum(
        1 for item in items if isinstance(item, dict) and item.get("user_decision") == "pending"
    )

    out_dir = output_root / "formula_visual_evidence"
    out_dir.mkdir(parents=True, exist_ok=True)

    validated_path = out_dir / "visual_items.bbox.validated.json"
    validated_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "visual_items_path": str(visual_items_path),
        "decisions_path": str(decisions_path),
        "output_root": str(output_root),
        "item_count": len(items),
        "decision_count": len(decisions),
        "applied_count": len(applied),
        "unchanged_pending_count": len(unchanged_pending),
        "ready_for_study_count": ready_for_study_count,
        "accepted_count": accepted_count,
        "edited_count": edited_count,
        "ignored_count": ignored_count,
        "pending_count": pending_count,
        "applied_items": applied,
        "unchanged_pending_item_ids": unchanged_pending,
        "validated_visual_items_path": str(validated_path),
    }

    summary_path = out_dir / "visual_items.bbox.validation-summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply manual validation decisions to bbox visual OCR Math candidates.")
    parser.add_argument("--visual-items", required=True, help="Path to visual_items.bbox.with-ocrmath-candidates.json")
    parser.add_argument("--decisions", required=True, help="Path to local manual validation decisions JSON")
    parser.add_argument("--output-root", required=True, help="Output root for validated visual item artifact")
    args = parser.parse_args()

    summary = apply_validation_decisions(
        visual_items_path=Path(args.visual_items),
        decisions_path=Path(args.decisions),
        output_root=Path(args.output_root),
    )

    print("BBOX_VISUAL_VALIDATION_GATE=PASS")
    print("visual_items_path=" + summary["visual_items_path"])
    print("decisions_path=" + summary["decisions_path"])
    print("output_root=" + summary["output_root"])
    print("decision_count=" + str(summary["decision_count"]))
    print("applied_count=" + str(summary["applied_count"]))
    print("ready_for_study_count=" + str(summary["ready_for_study_count"]))
    print("accepted_count=" + str(summary["accepted_count"]))
    print("edited_count=" + str(summary["edited_count"]))
    print("ignored_count=" + str(summary["ignored_count"]))
    print("pending_count=" + str(summary["pending_count"]))
    print("validated_visual_items_path=" + summary["validated_visual_items_path"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
