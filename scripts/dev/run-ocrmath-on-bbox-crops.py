from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _fail(message: str) -> None:
    raise SystemExit(message)


def _safe_rel_path(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        _fail("FAILED_EMPTY_PATH_FIELD=" + label)
    rel = Path(value.replace("\\", "/"))
    if rel.is_absolute() or ".." in rel.parts:
        _fail("FAILED_UNSAFE_RELATIVE_PATH=" + label)
    return rel


def _normalize_math_candidate(text: str) -> str:
    cleaned = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    cleaned = "\n".join(line.strip() for line in cleaned.splitlines() if line.strip())
    cleaned = re.sub(r"[ \t]+", " ", cleaned).strip()

    replacements = {
        "÷": "/",
        "×": "x",
        "−": "-",
        "–": "-",
        "—": "-",
        "∕": "/",
        "𝑥": "x",
        "𝑦": "y",
        "𝑎": "a",
        "𝑏": "b",
        "𝑐": "c",
    }

    for src, dst in replacements.items():
        cleaned = cleaned.replace(src, dst)

    return cleaned


def _resolve_tesseract_cmd(tesseract_cmd: str) -> str:
    candidates = [
        tesseract_cmd,
        str(Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")),
        str(Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe")),
    ]

    env_candidate = str(__import__("os").environ.get("TESSERACT_CMD", "")).strip()
    if env_candidate:
        candidates.insert(0, env_candidate)

    for candidate in candidates:
        if not candidate:
            continue
        if shutil.which(candidate):
            return str(shutil.which(candidate))
        if Path(candidate).exists():
            return str(Path(candidate))

    _fail("FAILED_TESSERACT_NOT_FOUND=" + tesseract_cmd)


def _run_tesseract(crop_path: Path, tesseract_cmd: str, lang: str, psm: int, timeout_seconds: int) -> tuple[str, str]:
    cmd = [
        tesseract_cmd,
        str(crop_path),
        "stdout",
        "-l",
        lang,
        "--psm",
        str(psm),
    ]

    try:
        completed = subprocess.run(
            cmd,
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return "", "timeout"
    except Exception as exc:
        return "", "error:" + str(exc)

    if completed.returncode != 0:
        err = (completed.stderr or "").strip()
        return "", "failed:" + err[:500]

    return _normalize_math_candidate(completed.stdout), ""


def run_ocrmath_on_crops(
    visual_items_path: Path,
    output_root: Path,
    tesseract_cmd: str = "tesseract",
    lang: str = "eng",
    psm: int = 6,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    if not visual_items_path.exists():
        _fail("FAILED_VISUAL_ITEMS_PATH_MISSING=" + str(visual_items_path))

    tesseract_cmd = _resolve_tesseract_cmd(tesseract_cmd)

    payload = json.loads(visual_items_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        _fail("FAILED_VISUAL_ITEMS_PAYLOAD_NOT_OBJECT")

    items = payload.get("items")
    if not isinstance(items, list):
        _fail("FAILED_VISUAL_ITEMS_ITEMS_NOT_LIST")

    processed = []
    skipped = []

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            _fail(f"FAILED_ITEM_NOT_OBJECT={index}")

        if item.get("crop_exists") is not True:
            item["ocr_math_status"] = "not_run"
            skipped.append({"index": index, "reason": "crop_missing_or_not_confirmed"})
            continue

        crop_rel = _safe_rel_path(item.get("crop_path"), "crop_path")
        crop_path = output_root / crop_rel

        if not crop_path.exists():
            item["crop_exists"] = False
            item["ocr_math_status"] = "not_run"
            skipped.append({"index": index, "reason": "crop_path_missing", "crop_path": str(crop_path)})
            continue

        candidate, error = _run_tesseract(
            crop_path=crop_path,
            tesseract_cmd=tesseract_cmd,
            lang=lang,
            psm=psm,
            timeout_seconds=timeout_seconds,
        )

        if candidate:
            item["ocr_math_candidate_text"] = candidate
            item["ocr_math_status"] = "pending_user_validation"
        else:
            item["ocr_math_candidate_text"] = ""
            item["ocr_math_status"] = "failed"

        # OCR Math output is only a candidate. It must not approve Study automatically.
        item["user_decision"] = "pending"
        item["ready_for_study"] = False

        processed.append(
            {
                "index": index,
                "item_id": item.get("item_id"),
                "crop_path": str(crop_path),
                "candidate_text": item.get("ocr_math_candidate_text", ""),
                "ocr_math_status": item.get("ocr_math_status"),
                "error": error,
            }
        )

    out_dir = output_root / "formula_visual_evidence"
    out_dir.mkdir(parents=True, exist_ok=True)

    updated_path = out_dir / "visual_items.bbox.with-ocrmath-candidates.json"
    updated_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "visual_items_path": str(visual_items_path),
        "output_root": str(output_root),
        "tesseract_cmd": tesseract_cmd,
        "lang": lang,
        "psm": psm,
        "item_count": len(items),
        "processed_count": len(processed),
        "skipped_count": len(skipped),
        "candidate_generated_count": sum(1 for item in processed if item.get("candidate_text")),
        "pending_user_validation_count": sum(1 for item in payload.get("items", []) if isinstance(item, dict) and item.get("ocr_math_status") == "pending_user_validation"),
        "ready_for_study_count": sum(1 for item in payload.get("items", []) if isinstance(item, dict) and item.get("ready_for_study") is True),
        "processed_items": processed,
        "skipped_items": skipped,
        "updated_visual_items_path": str(updated_path),
    }

    summary_path = out_dir / "visual_items.bbox.ocrmath-candidates-summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run OCR Math candidate extraction on existing bbox crop PNG artifacts.")
    parser.add_argument("--visual-items", required=True, help="Path to visual_items.bbox.with-crops.json")
    parser.add_argument("--output-root", required=True, help="Output root containing the crop paths")
    parser.add_argument("--tesseract-cmd", default="tesseract", help="Tesseract executable")
    parser.add_argument("--lang", default="eng", help="Tesseract language")
    parser.add_argument("--psm", type=int, default=6, help="Tesseract page segmentation mode")
    parser.add_argument("--timeout-seconds", type=int, default=30, help="Tesseract timeout per crop")
    args = parser.parse_args()

    summary = run_ocrmath_on_crops(
        visual_items_path=Path(args.visual_items),
        output_root=Path(args.output_root),
        tesseract_cmd=args.tesseract_cmd,
        lang=args.lang,
        psm=args.psm,
        timeout_seconds=args.timeout_seconds,
    )

    print("BBOX_CROP_OCRMATH_CANDIDATES=PASS")
    print("visual_items_path=" + summary["visual_items_path"])
    print("output_root=" + summary["output_root"])
    print("processed_count=" + str(summary["processed_count"]))
    print("candidate_generated_count=" + str(summary["candidate_generated_count"]))
    print("pending_user_validation_count=" + str(summary["pending_user_validation_count"]))
    print("ready_for_study_count=" + str(summary["ready_for_study_count"]))
    print("updated_visual_items_path=" + summary["updated_visual_items_path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

