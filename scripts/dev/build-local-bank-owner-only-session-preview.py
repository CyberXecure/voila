#!/usr/bin/env python
"""Build a v0.5.3 owner-only Exam Prep session preview JSON.

This is a no-persistence session preview built from the v0.5.0 owner-only
delivery module and the v0.5.1 real-course smoke helper. It does not add UI,
does not persist attempts/sessions/progress, and does not expose answers.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any


PREVIEW_VERSION = "v0.5.3"
DEFAULT_WORK_ROOT = ".tmp/v053-owner-only-session-preview-json"
DEFAULT_OUTPUT_NAME = "owner_only_session_preview.json"
MAX_PREVIEW_QUESTIONS = 5


def configure_stdout_utf8() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def _run_json_command(command: list[str], *, cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        check=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    return json.loads(completed.stdout)


def _clean_delivery_env() -> dict[str, str]:
    cleaned = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("VOILA_ENABLE_EXAM_PREP_LOCAL_BANK")
    }
    cleaned.pop("VOILA_FORCE_EXAM_PREP_LOCAL_BANK_OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK", None)
    return cleaned


def _delivery_rollup(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result.get("status"),
        "blocking_reasons": result.get("blocking_reasons") or [],
        "activation_effective": result.get("activation_effective"),
        "may_deliver_live": result.get("may_deliver_live"),
        "real_delivery_allowed_now": result.get("real_delivery_allowed_now"),
        "delivery_attempted": result.get("delivery_attempted"),
        "delivery_performed": result.get("delivery_performed"),
        "delivered_question_count": result.get("delivered_question_count"),
        "delivered_question_ids": result.get("delivered_question_ids") or [],
        "effective_source": result.get("effective_source"),
        "fallback_source": result.get("fallback_source"),
        "readiness_freeze_status": result.get("readiness_freeze_status"),
        "readiness_freeze_version": result.get("readiness_freeze_version"),
        "local_bank_preview_status": result.get("local_bank_preview_status"),
        "local_bank_question_count": result.get("local_bank_question_count"),
    }



def polish_preview_copy(value: str, *, max_length: int = 320) -> str:
    # Return readable owner-preview copy without common console/OCR mojibake.
    # This polishes displayed prompt text only and never reconstructs answers.

    text = str(value or "")

    replacements = {
        "╦ÿ": "a",
        "╦å": "o",
        "─â": "a",
        "ΓÇÖ": "'",
        "ΓÇ£": '"',
        "ΓÇ¥": '"',
        "ΓÇô": "-",
        "ΓÇ": "",
        "┬╕": "",
        "∩¼ü": "fi",
        "\\ufffd": "",
    }
    for broken, fixed in replacements.items():
        text = text.replace(broken, fixed)

    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))

    text = text.replace("“", '"').replace("”", '"').replace("„", '"').replace("’", "'")
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")

    text = "".join(" " if (ord(ch) < 32 and ch not in "\\n\\t") else ch for ch in text)
    text = re.sub(r"\\s+", " ", text).strip()

    match = re.fullmatch(r"Name one key point supported by the source text in '([^']+)'.", text)
    if match:
        topic = match.group(1).strip()
        text = f'Mentioneaza o idee-cheie sustinuta de fragmentul "{topic}".'

    text = text.replace("functiiei", "functiei")

    if len(text) > max_length:
        text = text[: max_length - 1].rstrip() + "…"

    return text


def polish_preview_copy(value: str, *, max_length: int = 320) -> str:
    # v0.5.4 override: ASCII-safe owner-preview copy polish.
    text = str(value or "")

    import re
    import unicodedata

    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("'", "'").replace('"', '"')
    text = text.encode("ascii", "ignore").decode("ascii", errors="replace")
    text = "".join(" " if ord(ch) < 32 else ch for ch in text)
    text = re.sub(r"\s+", " ", text).strip()

    prefix = "Name one key point supported by the source text in "
    if text.startswith(prefix):
        topic = text[len(prefix):].strip()
        if topic.endswith("."):
            topic = topic[:-1].strip()
        topic = topic.strip().strip("'").strip('"').strip()
        text = f'Mentioneaza o idee-cheie sustinuta de fragmentul "{topic}".'

    replacements = {
        "Dac a": "Daca",
        "exist a": "exista",
        "dat a": "data",
        "prim a": "prima",
        "aplicat ie": "aplicatie",
        "not iunii": "notiunii",
        "limit a": "limita",
        "existent ei": "existentei",
        "funct ii": "functii",
        "funct iei": "functiei",
        "urm atoarea": "urmatoarea",
        "definit ie": "definitie",
    }
    for broken, fixed in replacements.items():
        text = text.replace(broken, fixed)

    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_length:
        text = text[: max_length - 3].rstrip() + "..."
    return text

def _session_question(question: dict[str, Any]) -> dict[str, Any]:
    return {
        "display_index": int(question.get("display_index") or 0),
        "question_id": str(question.get("question_id") or ""),
        "skill_id": str(question.get("skill_id") or ""),
        "question_type": str(question.get("question_type") or ""),
        "difficulty": str(question.get("difficulty") or ""),
        "prompt": polish_preview_copy(str(question.get("prompt") or "")),
        "choices": [
            polish_preview_copy(str(choice))
            for choice in question.get("choices")
        ] if isinstance(question.get("choices"), list) else [],
        "answer_hidden_until_submission": True,
        "explanation_hidden_until_submission": True,
        "will_save_attempt": False,
        "will_update_progress": False,
        "will_score_answer": False,
    }


def _contains_forbidden_keys(value: Any) -> list[str]:
    forbidden = {
        "correct_answer",
        "correct_answer_preview",
        "answer",
        "expected_answer",
        "solution",
        "explanation",
        "explanation_preview",
        "source_excerpt",
        "raw_snapshots",
        "raw_contract",
        "dry_run_items",
        "selected_questions",
        "source_bank_path",
    }
    found: list[str] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            for key, nested in node.items():
                child_path = f"{path}.{key}" if path else str(key)
                if key in forbidden:
                    found.append(child_path)
                walk(nested, child_path)
        elif isinstance(node, list):
            for index, item in enumerate(node):
                walk(item, f"{path}[{index}]")

    walk(value, "")
    return found


def _validate_preview(preview: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    delivery = preview["delivery_result"]
    rollback = preview["rollback_result"]
    session = preview["session_preview"]
    safety = preview["safety_confirmations"]

    if delivery["status"] != "owner_only_first_real_delivery_performed":
        failures.append("delivery_status_not_performed")
    if delivery["effective_source"] != "local_bank":
        failures.append("delivery_effective_source_not_local_bank")
    if delivery["delivery_performed"] is not True:
        failures.append("delivery_performed_not_true")
    if int(delivery["delivered_question_count"] or 0) != MAX_PREVIEW_QUESTIONS:
        failures.append("delivered_question_count_not_5")

    if rollback["status"] != "rolled_back_to_legacy_fallback":
        failures.append("rollback_status_not_rolled_back")
    if rollback["effective_source"] != "legacy_fallback":
        failures.append("rollback_effective_source_not_legacy_fallback")
    if rollback["delivery_performed"] is not False:
        failures.append("rollback_delivery_performed_not_false")

    if int(session["question_count"] or 0) != MAX_PREVIEW_QUESTIONS:
        failures.append("session_question_count_not_5")
    if len(session.get("questions") or []) != MAX_PREVIEW_QUESTIONS:
        failures.append("session_questions_length_not_5")

    for index, question in enumerate(session.get("questions") or [], start=1):
        if int(question.get("display_index") or 0) != index:
            failures.append(f"question_{index}_display_index_invalid")
        if not str(question.get("question_id") or "").strip():
            failures.append(f"question_{index}_missing_question_id")
        if not str(question.get("prompt") or "").strip():
            failures.append(f"question_{index}_missing_prompt")
        if question.get("will_save_attempt") is not False:
            failures.append(f"question_{index}_will_save_attempt_not_false")
        if question.get("will_update_progress") is not False:
            failures.append(f"question_{index}_will_update_progress_not_false")
        if question.get("will_score_answer") is not False:
            failures.append(f"question_{index}_will_score_answer_not_false")

    expected_true = [
        "owner_only",
        "session_preview_only",
        "delivery_target_is_real_course",
        "readiness_guard_context_is_separate",
        "max_five_questions",
        "rollback_to_legacy_fallback",
        "answers_hidden",
        "no_forbidden_answer_fields",
    ]
    expected_false = [
        "adds_public_ui",
        "patches_web_app",
        "persists_sessions",
        "persists_attempts",
        "persists_progress",
        "updates_progress",
        "scores_live_session",
        "requires_cloud_or_api",
    ]

    for key in expected_true:
        if safety.get(key) is not True:
            failures.append(f"safety_{key}_not_true")
    for key in expected_false:
        if safety.get(key) is not False:
            failures.append(f"safety_{key}_not_false")

    forbidden_paths = _contains_forbidden_keys(preview)
    if forbidden_paths:
        failures.append("forbidden_keys_present:" + ",".join(forbidden_paths[:10]))

    return failures


def build_preview(*, root: Path, work_root: Path, output: Path) -> dict[str, Any]:
    services_api = root / "services" / "api"
    if str(services_api) not in sys.path:
        sys.path.insert(0, str(services_api))

    from exam_prep_local_bank_first_live_trial_readiness_freeze import REQUIRED_OWNER_FLAGS
    from exam_prep_local_bank_owner_only_first_real_delivery import (
        OWNER_ONLY_FIRST_REAL_DELIVERY_FLAG_NAME,
        OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK_FLAG_NAME,
        READINESS_GUARD_COURSE_ID,
        READINESS_GUARD_SKILL_ID,
        build_owner_only_first_real_delivery,
    )

    work_root.mkdir(parents=True, exist_ok=True)
    smoke_root = work_root / "smoke"
    helper = root / "scripts" / "dev" / "build-local-bank-real-course-smoke.py"

    temporary_bank_summary = _run_json_command(
        [
            sys.executable,
            str(helper),
            "--root",
            str(root),
            "--smoke-root",
            str(smoke_root),
        ],
        cwd=root,
    )

    course_id = str(temporary_bank_summary["course_id"])
    skill_id = str(temporary_bank_summary["skill_id"])

    enabled_env = _clean_delivery_env()
    for flag in REQUIRED_OWNER_FLAGS:
        enabled_env[str(flag)] = "1"
    enabled_env[OWNER_ONLY_FIRST_REAL_DELIVERY_FLAG_NAME] = "1"

    rollback_env = dict(enabled_env)
    rollback_env[OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK_FLAG_NAME] = "1"

    delivery_raw = build_owner_only_first_real_delivery(
        root=smoke_root,
        course_id=course_id,
        skill_id=skill_id,
        readiness_course_id=READINESS_GUARD_COURSE_ID,
        readiness_skill_id=READINESS_GUARD_SKILL_ID,
        limit=MAX_PREVIEW_QUESTIONS,
        env=enabled_env,
    )
    rollback_raw = build_owner_only_first_real_delivery(
        root=smoke_root,
        course_id=course_id,
        skill_id=skill_id,
        readiness_course_id=READINESS_GUARD_COURSE_ID,
        readiness_skill_id=READINESS_GUARD_SKILL_ID,
        limit=MAX_PREVIEW_QUESTIONS,
        env=rollback_env,
    )

    session_questions = [
        _session_question(question)
        for question in (delivery_raw.get("questions") or [])
    ][:MAX_PREVIEW_QUESTIONS]

    session_preview = {
        "session_preview_id": f"owner_only_session_preview::{course_id}::{skill_id}::{MAX_PREVIEW_QUESTIONS}",
        "session_preview_version": PREVIEW_VERSION,
        "course_id": course_id,
        "skill_id": skill_id,
        "question_count": len(session_questions),
        "max_question_count": MAX_PREVIEW_QUESTIONS,
        "delivery_source": "local_bank",
        "fallback_source": "legacy_fallback",
        "questions": session_questions,
        "interaction_policy": {
            "submit_supported": False,
            "save_attempt_supported": False,
            "progress_update_supported": False,
            "live_scoring_supported": False,
            "answers_available_in_preview": False,
        },
    }

    preview: dict[str, Any] = {
        "schema_version": "1",
        "preview_version": PREVIEW_VERSION,
        "preview_type": "owner_only_real_course_session_preview_json",
        "status": "pending",
        "selected_real_course_path": temporary_bank_summary.get("selected_real_course_path"),
        "temporary_bank_path": temporary_bank_summary.get("temporary_bank_path"),
        "temporary_bank_exercise_count": temporary_bank_summary.get("exercise_count"),
        "course_id": course_id,
        "skill_id": skill_id,
        "readiness_guard_course_id": READINESS_GUARD_COURSE_ID,
        "readiness_guard_skill_id": READINESS_GUARD_SKILL_ID,
        "selected_files": temporary_bank_summary.get("selected_files") or [],
        "delivery_result": _delivery_rollup(delivery_raw),
        "rollback_result": _delivery_rollup(rollback_raw),
        "session_preview": session_preview,
        "safety_confirmations": {
            "owner_only": True,
            "session_preview_only": True,
            "delivery_target_is_real_course": bool(temporary_bank_summary.get("selected_real_course_path")),
            "readiness_guard_context_is_separate": (
                course_id != READINESS_GUARD_COURSE_ID
                or skill_id != READINESS_GUARD_SKILL_ID
            ),
            "max_five_questions": len(session_questions) <= MAX_PREVIEW_QUESTIONS,
            "rollback_to_legacy_fallback": rollback_raw.get("effective_source") == "legacy_fallback",
            "answers_hidden": True,
            "no_forbidden_answer_fields": True,
            "adds_public_ui": False,
            "patches_web_app": False,
            "persists_sessions": False,
            "persists_attempts": False,
            "persists_progress": False,
            "updates_progress": False,
            "scores_live_session": False,
            "requires_cloud_or_api": False,
        },
        "preview_file": str(output.relative_to(root)) if output.is_relative_to(root) else str(output),
    }

    failures = _validate_preview(preview)
    preview["validation_failures"] = failures
    preview["status"] = "pass" if not failures else "fail"

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(preview, ensure_ascii=False, indent=2), encoding="utf-8")
    return preview


def main() -> int:
    configure_stdout_utf8()

    parser = argparse.ArgumentParser(description="Build v0.5.3 owner-only session preview JSON.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--work-root", default=DEFAULT_WORK_ROOT)
    parser.add_argument("--output", default="")
    parser.add_argument("--expect-pass", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    work_root = Path(args.work_root)
    if not work_root.is_absolute():
        work_root = (root / work_root).resolve()

    if args.output:
        output = Path(args.output)
        if not output.is_absolute():
            output = (root / output).resolve()
    else:
        output = work_root / DEFAULT_OUTPUT_NAME

    preview = build_preview(root=root, work_root=work_root, output=output)
    print(json.dumps(preview, ensure_ascii=True, indent=2))

    if args.expect_pass and preview.get("status") != "pass":
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
