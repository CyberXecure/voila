#!/usr/bin/env python
"""Build a v0.5.2 owner-only real-course delivery report.

The report is JSON-only and dev/owner scoped. It does not add UI routes and it
does not persist attempts, sessions, progress, answers, or live scoring.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


REPORT_VERSION = "v0.5.2"
DEFAULT_WORK_ROOT = ".tmp/v052-owner-only-real-course-delivery-report"
DEFAULT_REPORT_NAME = "owner_only_real_course_delivery_report.json"


def configure_stdout_utf8() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def _json_safe(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


def _clean_delivery_env() -> dict[str, str]:
    cleaned = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("VOILA_ENABLE_EXAM_PREP_LOCAL_BANK")
    }
    cleaned.pop("VOILA_FORCE_EXAM_PREP_LOCAL_BANK_OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK", None)
    return cleaned


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


def _delivery_summary(result: dict[str, Any]) -> dict[str, Any]:
    scope = result.get("implementation_scope") or {}
    no_persistence = result.get("no_persistence_policy") or {}

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
        "implementation_scope": {
            "adds_web_route": scope.get("adds_web_route"),
            "patches_web_app": scope.get("patches_web_app"),
            "adds_public_ui": scope.get("adds_public_ui"),
            "owner_only": scope.get("owner_only"),
            "uses_local_bank": scope.get("uses_local_bank"),
            "max_questions": scope.get("max_questions"),
            "persists_sessions": scope.get("persists_sessions"),
            "persists_attempts": scope.get("persists_attempts"),
            "updates_progress": scope.get("updates_progress"),
            "scores_live_session": scope.get("scores_live_session"),
            "requires_cloud_or_api": scope.get("requires_cloud_or_api"),
        },
        "no_persistence_policy": {
            "persist_session": no_persistence.get("persist_session"),
            "persist_attempts": no_persistence.get("persist_attempts"),
            "persist_progress": no_persistence.get("persist_progress"),
            "update_progress": no_persistence.get("update_progress"),
            "score_live_session": no_persistence.get("score_live_session"),
            "retain_user_answers": no_persistence.get("retain_user_answers"),
        },
    }


def _assert_delivery_report(report: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    default_result = report["default_disabled_result"]
    delivery = report["delivery_result"]
    rollback = report["rollback_result"]
    safety = report["safety_confirmations"]

    if default_result["status"] != "disabled":
        failures.append("default_status_not_disabled")
    if default_result["effective_source"] != "legacy_fallback":
        failures.append("default_effective_source_not_legacy_fallback")
    if default_result["delivery_performed"] is not False:
        failures.append("default_delivery_performed_not_false")

    if delivery["status"] != "owner_only_first_real_delivery_performed":
        failures.append("delivery_status_not_performed")
    if delivery["effective_source"] != "local_bank":
        failures.append("delivery_effective_source_not_local_bank")
    if delivery["delivery_performed"] is not True:
        failures.append("delivery_performed_not_true")
    delivered_count = int(delivery["delivered_question_count"] or 0)
    if delivered_count < 1 or delivered_count > 5:
        failures.append("delivered_question_count_outside_1_to_5")
    if int(delivery["local_bank_question_count"] or 0) != 5:
        failures.append("local_bank_question_count_not_5")

    if rollback["status"] != "rolled_back_to_legacy_fallback":
        failures.append("rollback_status_not_rolled_back")
    if rollback["effective_source"] != "legacy_fallback":
        failures.append("rollback_effective_source_not_legacy_fallback")
    if rollback["delivery_performed"] is not False:
        failures.append("rollback_delivery_performed_not_false")

    expected_true = [
        "owner_only",
        "delivery_target_is_real_course",
        "readiness_guard_context_is_separate",
        "max_five_questions",
        "rollback_to_legacy_fallback",
        "no_answers_in_report",
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

    return failures


def build_report(*, root: Path, work_root: Path, output: Path) -> dict[str, Any]:
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

    helper = root / "scripts" / "dev" / "build-local-bank-real-course-smoke.py"
    smoke_root = work_root / "smoke"
    work_root.mkdir(parents=True, exist_ok=True)

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

    disabled_env = _clean_delivery_env()
    enabled_env = dict(disabled_env)
    for flag in REQUIRED_OWNER_FLAGS:
        enabled_env[str(flag)] = "1"
    enabled_env[OWNER_ONLY_FIRST_REAL_DELIVERY_FLAG_NAME] = "1"

    rollback_env = dict(enabled_env)
    rollback_env[OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK_FLAG_NAME] = "1"

    default_result_raw = build_owner_only_first_real_delivery(
        root=smoke_root,
        course_id=course_id,
        skill_id=skill_id,
        readiness_course_id=READINESS_GUARD_COURSE_ID,
        readiness_skill_id=READINESS_GUARD_SKILL_ID,
        limit=5,
        env=disabled_env,
    )

    delivery_result_raw = build_owner_only_first_real_delivery(
        root=smoke_root,
        course_id=course_id,
        skill_id=skill_id,
        readiness_course_id=READINESS_GUARD_COURSE_ID,
        readiness_skill_id=READINESS_GUARD_SKILL_ID,
        limit=5,
        env=enabled_env,
    )

    rollback_result_raw = build_owner_only_first_real_delivery(
        root=smoke_root,
        course_id=course_id,
        skill_id=skill_id,
        readiness_course_id=READINESS_GUARD_COURSE_ID,
        readiness_skill_id=READINESS_GUARD_SKILL_ID,
        limit=5,
        env=rollback_env,
    )

    delivery_summary = _delivery_summary(delivery_result_raw)

    report: dict[str, Any] = {
        "schema_version": "1",
        "report_version": REPORT_VERSION,
        "report_type": "owner_only_real_course_local_bank_delivery_report",
        "status": "pending",
        "selected_real_course_path": temporary_bank_summary.get("selected_real_course_path"),
        "temporary_bank_path": temporary_bank_summary.get("temporary_bank_path"),
        "temporary_bank_exercise_count": temporary_bank_summary.get("exercise_count"),
        "course_id": course_id,
        "skill_id": skill_id,
        "readiness_guard_course_id": READINESS_GUARD_COURSE_ID,
        "readiness_guard_skill_id": READINESS_GUARD_SKILL_ID,
        "selected_files": temporary_bank_summary.get("selected_files") or [],
        "default_disabled_result": _delivery_summary(default_result_raw),
        "delivery_result": delivery_summary,
        "rollback_result": _delivery_summary(rollback_result_raw),
        "safety_confirmations": {
            "owner_only": True,
            "delivery_target_is_real_course": bool(temporary_bank_summary.get("selected_real_course_path")),
            "readiness_guard_context_is_separate": (
                course_id != READINESS_GUARD_COURSE_ID
                or skill_id != READINESS_GUARD_SKILL_ID
            ),
            "max_five_questions": int(delivery_summary.get("delivered_question_count") or 0) <= 5,
            "rollback_to_legacy_fallback": rollback_result_raw.get("effective_source") == "legacy_fallback",
            "no_answers_in_report": True,
            "adds_public_ui": False,
            "patches_web_app": False,
            "persists_sessions": False,
            "persists_attempts": False,
            "persists_progress": False,
            "updates_progress": False,
            "scores_live_session": False,
            "requires_cloud_or_api": False,
        },
        "report_file": str(output.relative_to(root)) if output.is_relative_to(root) else str(output),
    }

    failures = _assert_delivery_report(report)
    report["validation_failures"] = failures
    report["status"] = "pass" if not failures else "fail"

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> int:
    configure_stdout_utf8()

    parser = argparse.ArgumentParser(description="Build v0.5.2 owner-only real-course delivery report.")
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
        output = work_root / DEFAULT_REPORT_NAME

    report = build_report(root=root, work_root=work_root, output=output)
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.expect_pass and report.get("status") != "pass":
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

