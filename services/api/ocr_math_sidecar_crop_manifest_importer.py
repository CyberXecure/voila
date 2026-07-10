"""Explicit owner-local import from OCR Math sidecar into Crop Editor manifest.

v0.7.46:
- default mode is dry-run;
- --apply is required to modify figures_manifest.hybrid.json;
- creates a backup before writing;
- imports OCR Math sidecar candidates idempotently by source_candidate_id;
- does not modify OCR text, Course, Study, Progress, ZIP, share, delivery, or distribution.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any


MARKER = "VOILA_V0_7_46_OCR_MATH_SIDECAR_EXPLICIT_IMPORT_TO_CROP_MANIFEST_OWNER_LOCAL"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _safe_name(value: Any) -> str:
    text = str(value or "ocr-math").strip().lower()
    text = re.sub(r"[^a-z0-9._-]+", "_", text)
    text = text.strip("._-")
    return text or "ocr-math"


def _next_number(existing: list[dict[str, Any]], fallback_index: int) -> str:
    numbers: list[int] = []
    for item in existing:
        raw = str(item.get("number") or "")
        if raw.isdigit():
            numbers.append(int(raw))
    if numbers:
        return str(max(numbers) + fallback_index + 1)
    return f"ocr-math-{fallback_index + 1}"


def _existing_source_ids(items: list[dict[str, Any]]) -> set[str]:
    found: set[str] = set()
    for item in items:
        for key in ("source_candidate_id", "ocr_math_source_candidate_id"):
            value = str(item.get(key) or "").strip()
            if value:
                found.add(value)
    return found


def _resolve_sidecar_preview(output_folder: Path, figures_dir: Path, item: dict[str, Any]) -> Path | None:
    capture_source = str(item.get("capture_source") or "").replace("\\", "/").strip()
    if capture_source:
        path = output_folder / capture_source
        if path.exists():
            return path

    relative_path = str(item.get("relative_path") or "").replace("\\", "/").strip()
    if relative_path:
        path = figures_dir / relative_path
        try:
            if path.resolve().exists():
                return path
        except Exception:
            if path.exists():
                return path

    return None


def _import_item(
    sidecar_item: dict[str, Any],
    existing_items: list[dict[str, Any]],
    import_index: int,
) -> dict[str, Any]:
    source_candidate_id = str(sidecar_item.get("source_candidate_id") or sidecar_item.get("candidate_id") or "").strip()
    number = _next_number(existing_items, import_index)
    safe_source = _safe_name(source_candidate_id or number)

    page_number = sidecar_item.get("pdf_page") or sidecar_item.get("page_number")
    if not isinstance(page_number, int):
        page_number = None

    return {
        "number": number,
        "caption": str(sidecar_item.get("caption") or "OCR Math visual fallback imported candidate"),
        "pdf_page": page_number,
        "crop_method": "ocr_math_visual_fallback_imported_from_sidecar",
        "relative_path": f"crops/ocr_math_{safe_source}.png",
        "crop_rect": [0.0, 0.0, 595.0, 842.0],
        "crop_rect_status": "default_full_page_pending_owner_crop",
        "status": "accepted",
        "import_source": "ocr_math_visual_fallback_sidecar",
        "import_status": "imported_from_sidecar_pending_owner_crop",
        "source_candidate_id": source_candidate_id,
        "ocr_math_source_candidate_id": source_candidate_id,
        "source_line_number": sidecar_item.get("source_line_number"),
        "source_file": sidecar_item.get("source_file"),
        "risk_level": sidecar_item.get("risk_level"),
        "severity": sidecar_item.get("severity"),
        "rule_id": sidecar_item.get("rule_id"),
        "reason": sidecar_item.get("reason"),
        "original": sidecar_item.get("original"),
        "replacement": sidecar_item.get("replacement"),
        "capture_source": sidecar_item.get("capture_source"),
        "capture_exists": bool(sidecar_item.get("capture_exists")),
        "study_reference_allowed": bool(sidecar_item.get("study_reference_allowed")),
        "imported_by": MARKER,
        "preview_copied": False,
    }


def import_sidecar_to_crop_manifest(output_folder: Path, *, apply: bool = False) -> dict[str, Any]:
    output_folder = Path(output_folder)
    figures_dir = output_folder / "figures_hybrid"
    manifest_path = figures_dir / "figures_manifest.hybrid.json"
    sidecar_path = figures_dir / "ocr_math_visual_fallback_manifest.json"
    backup_path = figures_dir / "figures_manifest.hybrid.json.v0.7.46.bak"

    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing Crop Editor manifest: {manifest_path}")
    if not sidecar_path.exists():
        raise FileNotFoundError(f"Missing OCR Math sidecar: {sidecar_path}")

    manifest = _read_json(manifest_path)
    sidecar = _read_json(sidecar_path)

    items = manifest.get("figure_crops")
    if not isinstance(items, list):
        items = []
        manifest["figure_crops"] = items

    sidecar_items = sidecar.get("figure_crops")
    if not isinstance(sidecar_items, list):
        sidecar_items = []

    existing_ids = _existing_source_ids(items)
    imported: list[dict[str, Any]] = []
    skipped_duplicate: list[str] = []

    for sidecar_item in sidecar_items:
        if not isinstance(sidecar_item, dict):
            continue

        source_candidate_id = str(
            sidecar_item.get("source_candidate_id") or sidecar_item.get("candidate_id") or ""
        ).strip()

        if source_candidate_id and source_candidate_id in existing_ids:
            skipped_duplicate.append(source_candidate_id)
            continue

        imported_item = _import_item(sidecar_item, items + imported, len(imported))
        imported.append(imported_item)

        if source_candidate_id:
            existing_ids.add(source_candidate_id)

    if apply and imported:
        if not backup_path.exists():
            shutil.copyfile(manifest_path, backup_path)

        for imported_item, sidecar_item in zip(imported, sidecar_items):
            source_preview = _resolve_sidecar_preview(output_folder, figures_dir, sidecar_item)
            target_preview = figures_dir / imported_item["relative_path"]

            if source_preview and source_preview.exists():
                target_preview.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source_preview, target_preview)
                imported_item["preview_copied"] = True

        items.extend(imported)
        manifest["figure_crops"] = items
        manifest["ocr_math_sidecar_import"] = {
            "marker": MARKER,
            "apply": True,
            "imported_count": len(imported),
            "skipped_duplicate_count": len(skipped_duplicate),
            "backup_path": str(backup_path),
            "policy": "owner_local_explicit_import_no_build_no_zip_no_share_no_delivery_no_distribution",
        }
        _write_json(manifest_path, manifest)

    return {
        "marker": MARKER,
        "apply": apply,
        "source_sidecar": str(sidecar_path),
        "target_manifest": str(manifest_path),
        "backup_path": str(backup_path),
        "manifest_written": bool(apply and imported),
        "backup_created_or_existing": bool(apply and backup_path.exists()),
        "existing_count": len(items),
        "sidecar_count": len(sidecar_items),
        "imported_count": len(imported),
        "skipped_duplicate_count": len(skipped_duplicate),
        "skipped_duplicate_ids": skipped_duplicate,
        "imported_items": imported,
        "policy": "no_ocr_course_study_progress_rewrite_no_build_no_zip_no_share_no_delivery_no_distribution",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Import OCR Math sidecar candidates into Crop Editor manifest.")
    parser.add_argument("--output-folder", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    result = import_sidecar_to_crop_manifest(Path(args.output_folder), apply=args.apply)
    print(
        f"{MARKER}=PASS "
        f"apply={str(result['apply']).lower()} "
        f"imported_count={result['imported_count']} "
        f"skipped_duplicate_count={result['skipped_duplicate_count']} "
        f"manifest_written={str(result['manifest_written']).lower()}"
    )


if __name__ == "__main__":
    main()
