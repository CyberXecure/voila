"""Non-destructive Exam Prep local exercise bank source preview.

This module previews whether a valid exercise_bank.local.json is available for
future Exam Prep usage. It does not replace existing legacy quiz/question
behavior and does not modify progress, scoring, routes, or UI.

It is intentionally backend/diagnostic-only for v0.4.46.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from local_exercise_bank import choose_best_exercise_bank, discovery_summary


PREVIEW_VERSION = "v0.4.46"


def build_exam_prep_local_bank_preview(
    root: str | Path,
    *,
    course_id: str | None = None,
) -> dict[str, Any]:
    """Return a non-destructive source preview for Exam Prep.

    The result tells future callers whether a valid local exercise bank is
    available. The legacy path remains the fallback and is explicitly recorded.
    """

    root_path = Path(root)
    selected = choose_best_exercise_bank(root_path, course_id=course_id)
    discovery = discovery_summary(root_path, course_id=course_id)

    if selected is None:
        active_source = "legacy_fallback"
        selected_path = ""
        selected_count = 0
        local_bank_available = False
    else:
        active_source = "local_exercise_bank_preview"
        selected_path = str(selected.path)
        selected_count = selected.exercise_count
        local_bank_available = True

    return {
        "schema_version": "1",
        "preview_version": PREVIEW_VERSION,
        "mode": "non_destructive_preview",
        "course_id_filter": course_id or "",
        "root": str(root_path),
        "local_bank_available": local_bank_available,
        "active_source_preview": active_source,
        "selected_bank_path": selected_path,
        "selected_exercise_count": selected_count,
        "legacy_fallback_available": True,
        "legacy_fallback_policy": "Keep using legacy quiz/question data unless a future milestone explicitly enables local exercise bank consumption.",
        "will_modify_progress": False,
        "will_modify_exam_prep_ui": False,
        "will_replace_legacy_generator": False,
        "requires_cloud_or_api": False,
        "discovery": discovery,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview Exam Prep local exercise bank source availability.")
    parser.add_argument("--root", required=True, help="Root directory to search.")
    parser.add_argument("--course-id", default="", help="Optional course_id filter.")
    parser.add_argument("--strict-local", action="store_true", help="Exit non-zero when local bank preview is unavailable.")
    args = parser.parse_args()

    preview = build_exam_prep_local_bank_preview(args.root, course_id=args.course_id or None)
    print(json.dumps(preview, ensure_ascii=False, indent=2))

    if args.strict_local and not preview["local_bank_available"]:
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

