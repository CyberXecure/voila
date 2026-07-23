from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ALLOWED_KIND = {"formula", "figure", "diagram", "table", "symbol", "mixed", "unknown"}
ALLOWED_BBOX_UNITS = {"page_pixels", "pdf_points"}
ALLOWED_OCR_MATH_STATUS = {
    "not_run",
    "candidate_generated",
    "failed",
    "not_applicable",
    "pending_user_validation",
    "validated_by_user",
}
ALLOWED_USER_DECISION = {"pending", "accept", "edit", "ignore"}

REQUIRED_TOP_FIELDS = ["schema_version", "course_id", "source_pdf", "items"]
REQUIRED_ITEM_FIELDS = [
    "item_id",
    "kind",
    "page",
    "bbox",
    "bbox_units",
    "page_image_path",
    "crop_path",
    "crop_exists",
    "ocr_math_candidate_text",
    "ocr_math_status",
    "user_decision",
    "user_corrected_text",
    "user_explanation",
    "ready_for_study",
    "created_by",
    "review_notes",
]


def _fail(errors: list[str], message: str) -> None:
    errors.append(message)


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_bbox(value: Any) -> bool:
    if not isinstance(value, list) or len(value) != 4:
        return False
    if not all(isinstance(x, int) for x in value):
        return False
    x1, y1, x2, y2 = value
    return x2 > x1 and y2 > y1


def validate_visual_items_payload(payload: Any) -> tuple[bool, list[str]]:
    errors: list[str] = []

    if not isinstance(payload, dict):
        return False, ["payload_must_be_object"]

    for field in REQUIRED_TOP_FIELDS:
        if field not in payload:
            _fail(errors, f"missing_top_field:{field}")

    if payload.get("schema_version") != "v0.8.67":
        _fail(errors, "schema_version_must_be_v0.8.67")

    if not _is_non_empty_string(payload.get("course_id")):
        _fail(errors, "course_id_must_be_non_empty_string")

    if not _is_non_empty_string(payload.get("source_pdf")):
        _fail(errors, "source_pdf_must_be_non_empty_string")

    items = payload.get("items")
    if not isinstance(items, list):
        _fail(errors, "items_must_be_list")
        return False, errors

    seen_item_ids: set[str] = set()

    for index, item in enumerate(items):
        prefix = f"items[{index}]"

        if not isinstance(item, dict):
            _fail(errors, f"{prefix}:must_be_object")
            continue

        for field in REQUIRED_ITEM_FIELDS:
            if field not in item:
                _fail(errors, f"{prefix}:missing_item_field:{field}")

        item_id = item.get("item_id")
        if not _is_non_empty_string(item_id):
            _fail(errors, f"{prefix}:item_id_must_be_non_empty_string")
        elif item_id in seen_item_ids:
            _fail(errors, f"{prefix}:duplicate_item_id:{item_id}")
        else:
            seen_item_ids.add(item_id)

        if item.get("kind") not in ALLOWED_KIND:
            _fail(errors, f"{prefix}:kind_not_allowed")

        page = item.get("page")
        if not isinstance(page, int) or page < 1:
            _fail(errors, f"{prefix}:page_must_be_positive_integer")

        if not _validate_bbox(item.get("bbox")):
            _fail(errors, f"{prefix}:bbox_must_be_four_ordered_integers")

        if item.get("bbox_units") not in ALLOWED_BBOX_UNITS:
            _fail(errors, f"{prefix}:bbox_units_not_allowed")

        if not _is_non_empty_string(item.get("page_image_path")):
            _fail(errors, f"{prefix}:page_image_path_must_be_non_empty_string")

        if not _is_non_empty_string(item.get("crop_path")):
            _fail(errors, f"{prefix}:crop_path_must_be_non_empty_string")

        if not isinstance(item.get("crop_exists"), bool):
            _fail(errors, f"{prefix}:crop_exists_must_be_boolean")

        if not isinstance(item.get("ocr_math_candidate_text"), str):
            _fail(errors, f"{prefix}:ocr_math_candidate_text_must_be_string")

        if item.get("ocr_math_status") not in ALLOWED_OCR_MATH_STATUS:
            _fail(errors, f"{prefix}:ocr_math_status_not_allowed")

        if item.get("user_decision") not in ALLOWED_USER_DECISION:
            _fail(errors, f"{prefix}:user_decision_not_allowed")

        if not isinstance(item.get("user_corrected_text"), str):
            _fail(errors, f"{prefix}:user_corrected_text_must_be_string")

        if not isinstance(item.get("user_explanation"), str):
            _fail(errors, f"{prefix}:user_explanation_must_be_string")

        if not isinstance(item.get("ready_for_study"), bool):
            _fail(errors, f"{prefix}:ready_for_study_must_be_boolean")

        if not _is_non_empty_string(item.get("created_by")):
            _fail(errors, f"{prefix}:created_by_must_be_non_empty_string")

        if not isinstance(item.get("review_notes"), str):
            _fail(errors, f"{prefix}:review_notes_must_be_string")

        decision = item.get("user_decision")
        ready = item.get("ready_for_study")
        crop_exists = item.get("crop_exists")
        candidate = str(item.get("ocr_math_candidate_text") or "").strip()
        corrected = str(item.get("user_corrected_text") or "").strip()

        if decision == "ignore" and ready is True:
            _fail(errors, f"{prefix}:ignored_item_must_not_be_ready_for_study")

        if decision == "pending" and ready is True:
            _fail(errors, f"{prefix}:pending_item_must_not_be_ready_for_study")

        if ready is True:
            if decision not in {"accept", "edit"}:
                _fail(errors, f"{prefix}:ready_item_requires_accept_or_edit")
            if crop_exists is not True:
                _fail(errors, f"{prefix}:ready_item_requires_crop_exists_true")
            if not candidate and not corrected:
                _fail(errors, f"{prefix}:ready_item_requires_candidate_or_corrected_text")
            if decision == "edit" and not corrected:
                _fail(errors, f"{prefix}:edited_ready_item_requires_user_corrected_text")

    return not errors, errors


def validate_file(path: Path) -> tuple[bool, list[str], dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, [f"json_load_failed:{exc}"], {}

    ok, errors = validate_visual_items_payload(payload)
    summary = {
        "path": str(path),
        "ok": ok,
        "error_count": len(errors),
        "item_count": len(payload.get("items", [])) if isinstance(payload, dict) else 0,
        "ready_for_study_count": 0,
        "pending_count": 0,
        "ignored_count": 0,
    }

    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        for item in payload["items"]:
            if isinstance(item, dict):
                if item.get("ready_for_study") is True:
                    summary["ready_for_study_count"] += 1
                if item.get("user_decision") == "pending":
                    summary["pending_count"] += 1
                if item.get("user_decision") == "ignore":
                    summary["ignored_count"] += 1

    return ok, errors, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Voila bbox visual item artifacts.")
    parser.add_argument("path", help="Path to visual_items.bbox.json")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    args = parser.parse_args()

    path = Path(args.path)
    ok, errors, summary = validate_file(path)

    if args.json:
        print(json.dumps({"summary": summary, "errors": errors}, ensure_ascii=False, indent=2))
    else:
        print("BBOX_VISUAL_ITEMS_VALIDATION=" + ("PASS" if ok else "FAIL"))
        for key, value in summary.items():
            print(f"{key}={value}")
        for error in errors:
            print("ERROR=" + error)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
