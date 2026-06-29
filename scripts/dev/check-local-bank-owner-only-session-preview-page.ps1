$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

Write-Host "=== v0.5.6 hidden owner-only session preview page check ===" -ForegroundColor Cyan

$ApiPath = Join-Path $RepoRoot "services\api"
$env:PYTHONPATH = $ApiPath

Write-Host "`n=== Static page checks ===" -ForegroundColor Yellow
$webApp = "services/api/web_app.py"
$content = Get-Content $webApp -Raw -Encoding UTF8

if ($content -notmatch "/owner/exam-prep/session-preview") {
  throw "Hidden owner session preview page path missing"
}
if ($content -notmatch "VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_PAGE") {
  throw "Hidden owner session preview page flag missing"
}
if ($content -notmatch "include_in_schema=False") {
  throw "Hidden owner session preview page must be excluded from OpenAPI schema"
}
if ($content -match "href=.*/owner/exam-prep/session-preview") {
  throw "Page appears linked from public UI"
}

Write-Host "`n=== Ensure page route does not disclose exception details ===" -ForegroundColor Yellow
$pageStart = $content.IndexOf("# --- v0.5.6 owner-only hidden session preview page ---")
$pageEnd = $content.IndexOf("# --- end v0.5.6 owner-only hidden session preview page ---")

if ($pageStart -lt 0 -or $pageEnd -lt 0) {
  throw "v0.5.6 page block markers missing"
}

$pageBlock = $content.Substring($pageStart, $pageEnd - $pageStart)

if ($pageBlock -match "str\\(exc\\)" -or $pageBlock -match "type\\(exc\\).__name__" -or $pageBlock -match "traceback" -or $pageBlock -match "format_exc") {
  throw "Hidden page must not disclose exception details"
}

Write-Host "`n=== Dynamic page checks ===" -ForegroundColor Yellow

@'
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "services" / "api"))

PAGE_PATH = "/owner/exam-prep/session-preview"
PAGE_FLAG = "VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_PAGE"

import web_app  # noqa: E402

routes = [
    route
    for route in getattr(web_app.app, "routes", [])
    if getattr(route, "path", "") == PAGE_PATH
]

if len(routes) != 1:
    raise SystemExit(f"Expected exactly one hidden owner page, found {len(routes)}")

route = routes[0]
if getattr(route, "include_in_schema", None) is not False:
    raise SystemExit("Hidden page include_in_schema is not False")


class FakeRequest:
    def __init__(self, host: str) -> None:
        self.client = SimpleNamespace(host=host)


async def call_endpoint(host: str):
    result = route.endpoint(FakeRequest(host))
    if asyncio.iscoroutine(result):
        result = await result
    return result


def decode_html_response(response):
    body = getattr(response, "body", b"")
    if isinstance(body, str):
        body = body.encode("utf-8")
    return body.decode("utf-8", errors="replace")


os.environ.pop(PAGE_FLAG, None)
disabled_response = asyncio.run(call_endpoint("127.0.0.1"))
if int(getattr(disabled_response, "status_code", 0)) != 404:
    raise SystemExit("Disabled page must return 404")

os.environ[PAGE_FLAG] = "1"
nonlocal_response = asyncio.run(call_endpoint("203.0.113.10"))
if int(getattr(nonlocal_response, "status_code", 0)) != 404:
    raise SystemExit("Non-local request must return 404")

enabled_response = asyncio.run(call_endpoint("127.0.0.1"))
if int(getattr(enabled_response, "status_code", 0)) != 200:
    raise SystemExit("Enabled local page status was not 200")

html = decode_html_response(enabled_response)

required = [
    "Owner Exam Prep Session Preview",
    "Exam Prep Session Preview",
    "Owner-only hidden preview",
    "data-route-version=\"v0.5.6\"",
    "data-owner-only=\"true\"",
    "data-hidden-route=\"true\"",
    "Effective source:",
    "Rollback source:",
    "Question 1",
    "Question 5",
]
for needle in required:
    if needle not in html:
        raise SystemExit(f"Missing expected page text: {needle}")

for forbidden in [
    "<form",
    "<input",
    "<button",
    "correct_answer",
    "source_excerpt",
    "raw_snapshots",
    "format_exc",
    "traceback",
    "str(exc)",
    "type(exc).__name__",
]:
    if forbidden in html:
        raise SystemExit(f"Forbidden page content found: {forbidden}")

if (ROOT / ".tmp" / "v056-owner-only-session-preview-page").exists():
    raise SystemExit("Page temporary work root was not cleaned")

print({
    "status": "pass",
    "page_path": PAGE_PATH,
    "page_version": "v0.5.6",
    "hidden_page": True,
    "question_cards": html.count("question-card"),
    "has_form": "<form" in html,
    "has_input": "<input" in html,
    "has_button": "<button" in html,
})
'@ | python

Write-Host "`n=== Ensure no public navigation/template/static asset was added ===" -ForegroundColor Yellow
$changed = git diff --name-only
$changed | Out-Host

$changedText = $changed -join "`n"
if ($changedText -match "templates|static|assets") {
  throw "Unexpected public UI/template/static asset change in v0.5.6"
}

Write-Host "`n=== Clean temporary page data ===" -ForegroundColor Yellow
if (Test-Path ".tmp\v056-owner-only-session-preview-page") {
  Remove-Item ".tmp\v056-owner-only-session-preview-page" -Recurse -Force
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

Write-Host "`n=== v0.5.6 HIDDEN OWNER PAGE CHECK PASS ===" -ForegroundColor Green
