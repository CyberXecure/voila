#!/usr/bin/env python
"""Build a v0.5.9 owner manual smoke report for the hidden Exam Prep preview page."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any


REPORT_VERSION = "v0.5.9"
PAGE_PATH = "/owner/exam-prep/session-preview"
PAGE_FLAG = "VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_PAGE"
JSON_PATH = "/owner/exam-prep/session-preview.json"
ROUTE_FLAG = "VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_ROUTE"


def _decode_response_text(response: Any) -> str:
    body = getattr(response, "body", b"")
    if isinstance(body, str):
        return body
    return body.decode("utf-8", errors="replace")


async def _call_route(route: Any, host: str) -> Any:
    request = SimpleNamespace(client=SimpleNamespace(host=host))
    result = route.endpoint(request)
    if asyncio.iscoroutine(result):
        result = await result
    return result


def _find_route(app: Any, path: str) -> Any:
    matches = [
        route
        for route in getattr(app, "routes", [])
        if getattr(route, "path", "") == path
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one route for {path}, found {len(matches)}")
    return matches[0]


def _build_report(root: Path, port: int) -> dict[str, Any]:
    services_api = root / "services" / "api"
    if str(services_api) not in sys.path:
        sys.path.insert(0, str(services_api))

    import web_app  # noqa: E402

    page_route = _find_route(web_app.app, PAGE_PATH)
    json_route = _find_route(web_app.app, JSON_PATH)

    if getattr(page_route, "include_in_schema", None) is not False:
        raise RuntimeError("Owner preview page must be excluded from OpenAPI schema")
    if getattr(json_route, "include_in_schema", None) is not False:
        raise RuntimeError("Owner preview JSON route must be excluded from OpenAPI schema")

    os.environ.pop(PAGE_FLAG, None)
    disabled_page = asyncio.run(_call_route(page_route, "127.0.0.1"))
    disabled_page_status = int(getattr(disabled_page, "status_code", 0))

    os.environ[PAGE_FLAG] = "1"
    nonlocal_page = asyncio.run(_call_route(page_route, "203.0.113.10"))
    nonlocal_page_status = int(getattr(nonlocal_page, "status_code", 0))

    enabled_page = asyncio.run(_call_route(page_route, "127.0.0.1"))
    enabled_page_status = int(getattr(enabled_page, "status_code", 0))
    html = _decode_response_text(enabled_page)

    os.environ[ROUTE_FLAG] = "1"
    json_response = asyncio.run(_call_route(json_route, "127.0.0.1"))
    json_status = int(getattr(json_response, "status_code", 0))
    json_payload = json.loads(_decode_response_text(json_response))

    session = json_payload.get("session_preview") or {}
    delivery = json_payload.get("delivery_result") or {}
    rollback = json_payload.get("rollback_result") or {}

    checklist = {
        "page_title_visible": "Previzualizare sesiune Pregătire examene" in html,
        "owner_badge_visible": "Owner-only hidden preview" in html,
        "five_question_cards_visible": html.count('class="question-card"') == 5,
        "question_1_visible": "Întrebarea 1" in html,
        "question_5_visible": "Întrebarea 5" in html,
        "romanian_copy_visible": "Menționează o idee-cheie susținută" in html,
        "answer_policy_visible": "Răspunsul și explicația sunt ascunse" in html,
        "no_form": "<form" not in html,
        "no_input": "<input" not in html,
        "no_button": "<button" not in html,
        "no_correct_answer_exposed": "correct_answer" not in html,
        "no_source_excerpt_exposed": "source_excerpt" not in html,
        "no_raw_snapshot_exposed": "raw_snapshots" not in html,
        "disabled_page_returns_404": disabled_page_status == 404,
        "nonlocal_page_returns_404": nonlocal_page_status == 404,
        "enabled_local_page_returns_200": enabled_page_status == 200,
        "json_route_returns_200": json_status == 200,
        "json_question_count_is_5": int(session.get("question_count") or 0) == 5,
        "json_effective_source_local_bank": delivery.get("effective_source") == "local_bank",
        "json_rollback_source_legacy_fallback": rollback.get("effective_source") == "legacy_fallback",
        "no_submit_supported": (session.get("interaction_policy") or {}).get("submit_supported") is False,
        "no_save_attempt_supported": (session.get("interaction_policy") or {}).get("save_attempt_supported") is False,
        "no_progress_update_supported": (session.get("interaction_policy") or {}).get("progress_update_supported") is False,
        "no_live_scoring_supported": (session.get("interaction_policy") or {}).get("live_scoring_supported") is False,
    }

    manual_screenshot_checklist = [
        "Open scripts/dev/start-owner-session-preview-page.ps1 -OpenBrowser.",
        f"Confirm the browser URL is http://127.0.0.1:{port}{PAGE_PATH}.",
        "Capture a screenshot showing the title and at least the first three question cards.",
        "Confirm there is no form, input, or submit button.",
        "Confirm the policy text says answers/explanations are hidden and no attempts/progress/scoring are saved.",
        "Keep the screenshot local; do not add it to git unless a future milestone explicitly requests a sanitized artifact.",
    ]

    failures = [key for key, value in checklist.items() if value is not True]

    return {
        "schema_version": "1",
        "report_version": REPORT_VERSION,
        "report_type": "owner_preview_manual_smoke_report",
        "status": "pass" if not failures else "fail",
        "validation_failures": failures,
        "page_path": PAGE_PATH,
        "json_path": JSON_PATH,
        "page_flag": PAGE_FLAG,
        "json_flag": ROUTE_FLAG,
        "owner_only": True,
        "hidden_page": True,
        "hidden_json_route": True,
        "disabled_by_default": True,
        "local_owner_only": True,
        "manual_screenshot_required": True,
        "manual_screenshot_should_be_committed": False,
        "page_url": f"http://127.0.0.1:{port}{PAGE_PATH}",
        "json_url": f"http://127.0.0.1:{port}{JSON_PATH}",
        "expected_browser_url": f"http://127.0.0.1:{port}{PAGE_PATH}",
        "expected_json_url": f"http://127.0.0.1:{port}{JSON_PATH}",
        "selected_real_course_path": json_payload.get("selected_real_course_path"),
        "question_count": session.get("question_count"),
        "effective_source": delivery.get("effective_source"),
        "rollback_source": rollback.get("effective_source"),
        "safety": {
            "adds_public_ui": False,
            "adds_public_navigation": False,
            "adds_tester_ui": False,
            "has_form": False,
            "has_input": False,
            "has_submit_button": False,
            "persists_sessions": False,
            "persists_attempts": False,
            "updates_progress": False,
            "scores_live_session": False,
            "requires_cloud_or_api": False,
        },
        "automated_browser_preview_checklist": checklist,
        "manual_screenshot_checklist": manual_screenshot_checklist,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default=".tmp/v059-owner-preview-manual-smoke-report/owner_preview_manual_smoke_report.json")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--expect-pass", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output

    output.parent.mkdir(parents=True, exist_ok=True)
    report = _build_report(root=root, port=args.port)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.expect_pass and report.get("status") != "pass":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
