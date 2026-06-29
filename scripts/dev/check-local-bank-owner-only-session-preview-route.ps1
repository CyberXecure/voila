$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

Write-Host "=== v0.5.5 hidden owner-only session preview route check ===" -ForegroundColor Cyan

$ApiPath = Join-Path $RepoRoot "services\api"
$env:PYTHONPATH = $ApiPath

Write-Host "`n=== Static route checks ===" -ForegroundColor Yellow
$webApp = "services/api/web_app.py"
$content = Get-Content $webApp -Raw -Encoding UTF8

if ($content -notmatch "/owner/exam-prep/session-preview\.json") {
  throw "Hidden owner session preview route path missing"
}
if ($content -notmatch "include_in_schema=False") {
  throw "Hidden owner session preview route must be excluded from OpenAPI schema"
}
if ($content -match "href=.*/owner/exam-prep/session-preview\.json") {
  throw "Route appears linked from public UI"
}


Write-Host "`n=== Ensure route does not disclose exception details ===" -ForegroundColor Yellow
$routeStart = $content.IndexOf("# --- v0.5.5 owner-only hidden session preview route ---")
$routeEnd = $content.IndexOf("# --- end v0.5.5 owner-only hidden session preview route ---")

if ($routeStart -lt 0 -or $routeEnd -lt 0) {
  throw "v0.5.5 route block markers missing"
}

$routeBlock = $content.Substring($routeStart, $routeEnd - $routeStart)

if ($routeBlock -match "str\(exc\)" -or $routeBlock -match "type\(exc\).__name__" -or $routeBlock -match "traceback" -or $routeBlock -match "format_exc") {
  throw "Hidden route must not disclose exception details"
}

Write-Host "`n=== Dynamic route checks ===" -ForegroundColor Yellow

@'
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "services" / "api"))

ROUTE_PATH = "/owner/exam-prep/session-preview.json"
ROUTE_FLAG = "VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_ROUTE"

import web_app  # noqa: E402

routes = [
    route
    for route in getattr(web_app.app, "routes", [])
    if getattr(route, "path", "") == ROUTE_PATH
]

if len(routes) != 1:
    raise SystemExit(f"Expected exactly one hidden owner route, found {len(routes)}")

route = routes[0]
if getattr(route, "include_in_schema", None) is not False:
    raise SystemExit("Hidden route include_in_schema is not False")


class FakeRequest:
    def __init__(self, host: str) -> None:
        self.client = SimpleNamespace(host=host)


async def call_endpoint(host: str):
    result = route.endpoint(FakeRequest(host))
    if asyncio.iscoroutine(result):
        result = await result
    return result


def decode_json_response(response):
    body = getattr(response, "body", b"")
    if isinstance(body, str):
        body = body.encode("utf-8")
    return json.loads(body.decode("utf-8"))


os.environ.pop(ROUTE_FLAG, None)
disabled_response = asyncio.run(call_endpoint("127.0.0.1"))
if int(getattr(disabled_response, "status_code", 0)) != 404:
    raise SystemExit("Disabled route must return 404")
disabled_payload = decode_json_response(disabled_response)
if disabled_payload.get("effective_source") != "legacy_fallback":
    raise SystemExit("Disabled route must report legacy_fallback")
if disabled_payload.get("delivery_performed") is not False:
    raise SystemExit("Disabled route must not perform delivery")

os.environ[ROUTE_FLAG] = "1"
nonlocal_response = asyncio.run(call_endpoint("203.0.113.10"))
if int(getattr(nonlocal_response, "status_code", 0)) != 404:
    raise SystemExit("Non-local request must return 404")

enabled_response = asyncio.run(call_endpoint("127.0.0.1"))
if int(getattr(enabled_response, "status_code", 0)) != 200:
    payload = decode_json_response(enabled_response)
    raise SystemExit(f"Enabled local route status was not 200: {payload}")

payload = decode_json_response(enabled_response)

if payload.get("status") != "pass":
    raise SystemExit("Enabled route payload status is not pass")
if payload.get("route_version") != "v0.5.5":
    raise SystemExit("Route version is not v0.5.5")
if payload.get("route_enabled") is not True:
    raise SystemExit("route_enabled is not true")
if payload.get("hidden_route") is not True:
    raise SystemExit("hidden_route is not true")
if payload.get("owner_only_route") is not True:
    raise SystemExit("owner_only_route is not true")
if payload.get("adds_public_ui") is not False:
    raise SystemExit("adds_public_ui is not false")
if payload.get("persists_sessions") is not False:
    raise SystemExit("persists_sessions is not false")
if payload.get("persists_attempts") is not False:
    raise SystemExit("persists_attempts is not false")
if payload.get("updates_progress") is not False:
    raise SystemExit("updates_progress is not false")
if payload.get("scores_live_session") is not False:
    raise SystemExit("scores_live_session is not false")

session = payload.get("session_preview") or {}
if int(session.get("question_count") or 0) != 5:
    raise SystemExit("Session preview question_count is not 5")

policy = session.get("interaction_policy") or {}
if policy.get("submit_supported") is not False:
    raise SystemExit("submit_supported is not false")
if policy.get("save_attempt_supported") is not False:
    raise SystemExit("save_attempt_supported is not false")
if policy.get("progress_update_supported") is not False:
    raise SystemExit("progress_update_supported is not false")
if policy.get("live_scoring_supported") is not False:
    raise SystemExit("live_scoring_supported is not false")
if policy.get("answers_available_in_preview") is not False:
    raise SystemExit("answers_available_in_preview is not false")

for question in session.get("questions") or []:
    if not question.get("prompt"):
        raise SystemExit("Question prompt is empty")
    if question.get("answer_hidden_until_submission") is not True:
        raise SystemExit("answer_hidden_until_submission is not true")
    if question.get("explanation_hidden_until_submission") is not True:
        raise SystemExit("explanation_hidden_until_submission is not true")
    if question.get("will_save_attempt") is not False:
        raise SystemExit("will_save_attempt is not false")
    if question.get("will_update_progress") is not False:
        raise SystemExit("will_update_progress is not false")
    if question.get("will_score_answer") is not False:
        raise SystemExit("will_score_answer is not false")

if (ROOT / ".tmp" / "v055-owner-only-session-preview-route").exists():
    raise SystemExit("Route temporary work root was not cleaned")

print(json.dumps({
    "status": "pass",
    "route_path": ROUTE_PATH,
    "route_version": payload.get("route_version"),
    "question_count": session.get("question_count"),
    "effective_source": (payload.get("delivery_result") or {}).get("effective_source"),
    "rollback_source": (payload.get("rollback_result") or {}).get("effective_source"),
    "hidden_route": payload.get("hidden_route"),
    "adds_public_ui": payload.get("adds_public_ui"),
    "persists_sessions": payload.get("persists_sessions"),
    "persists_attempts": payload.get("persists_attempts"),
    "updates_progress": payload.get("updates_progress"),
    "scores_live_session": payload.get("scores_live_session"),
}, ensure_ascii=False, indent=2))
'@ | python

Write-Host "`n=== Ensure no public navigation was added ===" -ForegroundColor Yellow
$changed = git diff --name-only
$changed | Out-Host

$changedText = $changed -join "`n"
if ($changedText -match "templates|static|assets") {
  throw "Unexpected public UI/template/static asset change in v0.5.5"
}

Write-Host "`n=== Clean temporary route data ===" -ForegroundColor Yellow
if (Test-Path ".tmp\v055-owner-only-session-preview-route") {
  Remove-Item ".tmp\v055-owner-only-session-preview-route" -Recurse -Force
}
if (Test-Path ".tmp") {
  $remaining = Get-ChildItem ".tmp" -Force -ErrorAction SilentlyContinue
  if (-not $remaining) {
    Remove-Item ".tmp" -Force
  }
}

Write-Host "`n=== Compile touched Python files ===" -ForegroundColor Yellow
python -m compileall `
  "services/api/web_app.py" `
  "scripts/dev/build-local-bank-owner-only-session-preview.py"

Write-Host "`n=== Diff whitespace check ===" -ForegroundColor Yellow
git diff --check

Write-Host "`n=== v0.5.5 HIDDEN OWNER ROUTE CHECK PASS ===" -ForegroundColor Green
