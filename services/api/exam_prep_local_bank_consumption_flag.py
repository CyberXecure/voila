"""Controlled local-bank consumption flag scaffold for Exam Prep.

v0.4.52 introduces an explicit disabled-by-default flag that can preview source
selection for future local-bank consumption.

This module intentionally does not expose a web route and does not accept a
filesystem root from user input. It generates an internal temporary sample for
diagnostics only.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from exam_prep_local_bank_study_preview import build_local_bank_read_only_study_preview
from local_pedagogy_engine import generate_local_pedagogy_bundle


CONSUMPTION_FLAG_VERSION = "v0.4.52"
CONSUMPTION_FLAG_NAME = "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION"
LOCAL_SOURCE = "local_exercise_bank_adapter"
LEGACY_SOURCE = "legacy_fallback"

_SAMPLE_TEXT = (
    "Funcțiile sunt relații matematice între două mulțimi. "
    "O funcție este definită prin domeniu, codomeniu și lege de corespondență. "
    "Derivata descrie variația locală a unei funcții. "
    "Apoi se poate studia monotonia și se pot identifica punctele critice. "
    "Formula f'(x)=lim h->0 (f(x+h)-f(x))/h este folosită pentru calculul derivatei."
)


def is_local_bank_consumption_enabled(env: dict[str, str] | None = None) -> bool:
    """Return whether controlled local-bank consumption is enabled."""

    source = env if env is not None else os.environ
    value = str(source.get(CONSUMPTION_FLAG_NAME, "")).strip().lower()
    return value in {"1", "true", "yes", "on"}


def build_controlled_consumption_snapshot(
    *,
    course_id: str = "v052-sample",
    skill_id: str = "local_concept_001_functiile",
    limit: int = 3,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a diagnostic source-selection snapshot.

    The local-bank sample is generated in a temporary internal directory. No
    caller-provided filesystem root is accepted or used.
    """

    enabled = is_local_bank_consumption_enabled(env)

    with tempfile.TemporaryDirectory(prefix="voila-local-bank-consumption-") as tmp_root:
        generate_local_pedagogy_bundle(
            _SAMPLE_TEXT,
            tmp_root,
            course_id=course_id,
            source_path="internal_v052_sample",
            language="ro",
        )

        preview = build_local_bank_read_only_study_preview(
            Path(tmp_root),
            course_id=course_id,
            skill_id=skill_id,
            limit=limit,
        )

    local_available = (
        preview.get("active_source") == LOCAL_SOURCE
        and int(preview.get("preview_question_count", 0)) > 0
    )

    if enabled and local_available:
        selected_source = LOCAL_SOURCE
        selection_reason = "flag_enabled_and_valid_local_preview_available"
        selected_questions = preview.get("questions", [])
    else:
        selected_source = LEGACY_SOURCE
        selection_reason = (
            "flag_disabled_legacy_default"
            if not enabled
            else "flag_enabled_but_no_valid_local_preview"
        )
        selected_questions = []

    return {
        "schema_version": "1",
        "consumption_flag_version": CONSUMPTION_FLAG_VERSION,
        "mode": "controlled_consumption_flag_scaffold",
        "flag_name": CONSUMPTION_FLAG_NAME,
        "flag_enabled": enabled,
        "default_source": LEGACY_SOURCE,
        "selected_source": selected_source,
        "selection_reason": selection_reason,
        "local_preview_available": local_available,
        "local_preview_question_count": int(preview.get("preview_question_count", 0)),
        "selected_question_count": len(selected_questions),
        "selected_questions": selected_questions,
        "legacy_fallback_available": True,
        "path_policy": "no_user_provided_filesystem_root",
        "will_save_attempt": False,
        "will_update_progress": False,
        "will_score_answer": False,
        "will_modify_exam_prep_ui": False,
        "will_modify_weak_review": False,
        "will_replace_live_study_session": False,
        "will_replace_legacy_generator": False,
        "will_enable_live_consumption": False,
        "requires_cloud_or_api": False,
        "preview": preview,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview the controlled local-bank consumption flag.")
    parser.add_argument("--course-id", default="v052-sample", help="Diagnostic course id.")
    parser.add_argument("--skill-id", default="local_concept_001_functiile", help="Diagnostic skill id.")
    parser.add_argument("--limit", type=int, default=3, help="Maximum diagnostic questions.")
    parser.add_argument("--strict-enabled", action="store_true", help="Exit non-zero unless local source is selected.")
    parser.add_argument("--strict-disabled", action="store_true", help="Exit non-zero unless legacy fallback is selected.")
    args = parser.parse_args()

    snapshot = build_controlled_consumption_snapshot(
        course_id=args.course_id,
        skill_id=args.skill_id,
        limit=args.limit,
    )

    print(json.dumps(snapshot, ensure_ascii=True, indent=2))

    if args.strict_enabled and snapshot["selected_source"] != LOCAL_SOURCE:
        return 2
    if args.strict_disabled and snapshot["selected_source"] != LEGACY_SOURCE:
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

