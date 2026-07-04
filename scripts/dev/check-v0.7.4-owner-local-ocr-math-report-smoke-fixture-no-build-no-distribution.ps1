param(
  [switch] $FinalMainCheck
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$WebApp = Join-Path $RepoRoot "services\api\web_app.py"
$Doc = Join-Path $RepoRoot "docs\dev\v0.7.4-owner-local-ocr-math-report-smoke-fixture-no-build-no-distribution.md"

if (-not (Test-Path $WebApp)) {
  throw "Missing services/api/web_app.py"
}

if (-not (Test-Path $Doc)) {
  throw "Missing v0.7.4 docs file"
}

$WebText = Get-Content $WebApp -Raw -Encoding UTF8
$DocText = Get-Content $Doc -Raw -Encoding UTF8

$RequiredExistingWebMarkers = @(
  "VOILA_V0_7_1_OWNER_LOCAL_OCR_MATH_REPORT_UI_LINK_START",
  "VOILA_V0_7_2_OWNER_LOCAL_OCR_MATH_REPORT_UX_POLISH_APPLIED",
  "VOILA_V0_7_3_OWNER_LOCAL_OCR_MATH_REPORT_VIEWER_PAGE_APPLIED",
  "/owner/ocr-math-report/{course_id}/summary.json",
  "/owner/ocr-math-report/{course_id}/ocr_math_report.md",
  "/owner/ocr-math-report/{course_id}/view",
  "_voila_owner_ocr_math_report_viewer",
  "_voila_ocr_math_report_markdown_to_html",
  "Diagnostic local · read-only",
  "Sugestii detectate",
  "Linii posibil afectate"
)

foreach ($marker in $RequiredExistingWebMarkers) {
  if ($WebText -notlike "*$marker*") {
    throw "Missing expected existing web marker before v0.7.4 smoke: $marker"
  }
}

$RequiredDocMarkers = @(
  "smoke fixture and validation only",
  "v0-7-4-ocr-math-smoke-course",
  "/owner/ocr-math-report/{course_id}/summary.json",
  "/owner/ocr-math-report/{course_id}/ocr_math_report.md",
  "/owner/ocr-math-report/{course_id}/view",
  "Sugestii detectate",
  "Linii posibil afectate",
  "Diagnostic local · read-only",
  "no build",
  "no ZIP",
  "no delivery",
  "no distribution",
  "VOILA_ENABLE_OCR_MATH_REPORT_HOOK=1",
  "does not",
  "Formula OCR"
)

foreach ($marker in $RequiredDocMarkers) {
  if ($DocText -notlike "*$marker*") {
    throw "Missing doc marker: $marker"
  }
}

Write-Host "== Python syntax check =="
python -m py_compile $WebApp

Write-Host "== Prepare temporary local smoke fixture =="
$FixtureRoot = Join-Path ([System.IO.Path]::GetTempPath()) "voila-v0.7.4-ocr-math-report-smoke-fixture"
$CourseId = "v0-7-4-ocr-math-smoke-course"
$CourseDir = Join-Path $FixtureRoot $CourseId

if (Test-Path $FixtureRoot) {
  Remove-Item -Recurse -Force $FixtureRoot
}
New-Item -ItemType Directory -Force -Path $CourseDir | Out-Null

$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

$ReportJson = [ordered]@{
  total_suggestions = 3
  changed_line_count = 2
  suggestions = @(
    [ordered]@{ line = 3; original = "x2 + y2"; suggestion = "x^2 + y^2" },
    [ordered]@{ line = 5; original = "int_0^1"; suggestion = "\int_0^1" },
    [ordered]@{ line = 8; original = "lim x->0"; suggestion = "\lim_{x\to0}" }
  )
  changed_lines = @(3, 5)
  fixture = "v0.7.4 owner-local smoke fixture"
} | ConvertTo-Json -Depth 8

$ReportMd = @"
# OCR Math smoke fixture

This is a temporary owner-local diagnostic report used only by v0.7.4 smoke validation.

## Summary

- total_suggestions: 3
- changed_line_count: 2

## Suggestions

- line 3: x2 + y2 -> x^2 + y^2
- line 5: int_0^1 -> \int_0^1
- line 8: lim x->0 -> \lim_{x\to0}

```text
No auto-correction is performed by this smoke fixture.
```
"@

[System.IO.File]::WriteAllText((Join-Path $CourseDir "ocr_math_report.json"), $ReportJson, $Utf8NoBom)
[System.IO.File]::WriteAllText((Join-Path $CourseDir "ocr_math_report.md"), $ReportMd, $Utf8NoBom)

$SmokePy = @"
from pathlib import Path
import json
import os
import sys

repo = Path(os.environ["VOILA_REPO_ROOT"]).resolve()
fixture_root = Path(os.environ["VOILA_V074_FIXTURE_ROOT"]).resolve()
course_id = os.environ["VOILA_V074_COURSE_ID"]

for env_name in ("VOILA_DATA_DIR", "VOILA_LIBRARY_DIR", "VOILA_OWNER_LIBRARY_DIR", "VOILA_STORAGE_DIR"):
    os.environ[env_name] = str(fixture_root)

sys.path.insert(0, str(repo))
sys.path.insert(0, str(repo / "services" / "api"))

try:
    from fastapi.testclient import TestClient
except Exception as exc:
    raise SystemExit(f"FastAPI TestClient is unavailable: {exc}") from exc

try:
    import web_app
except Exception as exc:
    raise SystemExit(f"Could not import services/api/web_app.py for smoke test: {exc}") from exc

client = TestClient(web_app.app)

summary_response = client.get(f"/owner/ocr-math-report/{course_id}/summary.json")
if summary_response.status_code != 200:
    raise SystemExit(f"summary.json returned {summary_response.status_code}: {summary_response.text[:500]}")

summary = summary_response.json()
if summary.get("exists") is not True:
    raise SystemExit(f"summary exists flag is not true: {summary}")
if summary.get("total_suggestions") != 3:
    raise SystemExit(f"unexpected total_suggestions: {summary}")
if summary.get("changed_line_count") != 2:
    raise SystemExit(f"unexpected changed_line_count: {summary}")

raw_response = client.get(f"/owner/ocr-math-report/{course_id}/ocr_math_report.md")
if raw_response.status_code != 200:
    raise SystemExit(f"raw markdown returned {raw_response.status_code}: {raw_response.text[:500]}")
raw_text = raw_response.text
for marker in ("OCR Math smoke fixture", "total_suggestions: 3", "changed_line_count: 2", "No auto-correction is performed"):
    if marker not in raw_text:
        raise SystemExit(f"raw markdown missing marker: {marker}")

viewer_response = client.get(f"/owner/ocr-math-report/{course_id}/view")
if viewer_response.status_code != 200:
    raise SystemExit(f"viewer returned {viewer_response.status_code}: {viewer_response.text[:500]}")

viewer_text = viewer_response.text
required_viewer_markers = [
    "Raport diagnostic OCR Math",
    "Diagnostic local · read-only",
    "Sugestii detectate",
    "Linii posibil afectate",
    "Deschide raw .md",
    "Această pagină este doar pentru citire",
    "Nu modifică OCR-ul, cursul, Study sau Progress",
    "OCR Math smoke fixture",
    "No auto-correction is performed",
]
missing = [marker for marker in required_viewer_markers if marker not in viewer_text]
if missing:
    raise SystemExit("viewer missing markers: " + json.dumps(missing, ensure_ascii=False))

for forbidden in (
    "Accept suggestion",
    "Reject suggestion",
    "Apply correction",
    "Auto-correct",
    "Formula OCR enabled",
):
    if forbidden in viewer_text:
        raise SystemExit(f"viewer unexpectedly contains interactive/correction marker: {forbidden}")

missing_response = client.get("/owner/ocr-math-report/v0-7-4-missing-report/view")
if missing_response.status_code != 404:
    raise SystemExit(f"missing viewer should return 404, got {missing_response.status_code}")

print(json.dumps({
    "milestone": "v0.7.4-owner-local-ocr-math-report-smoke-fixture-no-build-no-distribution",
    "status": "PASS",
    "fixture_root": str(fixture_root),
    "course_id": course_id,
    "summary_route": f"/owner/ocr-math-report/{course_id}/summary.json",
    "raw_route": f"/owner/ocr-math-report/{course_id}/ocr_math_report.md",
    "viewer_route": f"/owner/ocr-math-report/{course_id}/view",
    "total_suggestions": summary.get("total_suggestions"),
    "changed_line_count": summary.get("changed_line_count"),
    "missing_viewer_404": True,
    "read_only": True,
    "no_auto_correction": True,
    "no_formula_ocr": True
}, ensure_ascii=False, indent=2))
"@

$SmokePyPath = Join-Path $FixtureRoot "run-v0.7.4-smoke.py"
[System.IO.File]::WriteAllText($SmokePyPath, $SmokePy, $Utf8NoBom)

$env:VOILA_REPO_ROOT = [string]$RepoRoot
$env:VOILA_V074_FIXTURE_ROOT = $FixtureRoot
$env:VOILA_V074_COURSE_ID = $CourseId

Write-Host "== Run owner-local OCR Math report viewer smoke =="
python $SmokePyPath

Write-Host "== PowerShell syntax check =="
$tokens = $null
$parseErrors = $null
[System.Management.Automation.Language.Parser]::ParseFile($PSCommandPath, [ref]$tokens, [ref]$parseErrors) | Out-Null
if ($parseErrors -and $parseErrors.Count -gt 0) {
  throw ($parseErrors | Out-String)
}

Write-Host "== Policy artifact check =="
$ForbiddenMilestoneArtifacts = Get-ChildItem $RepoRoot -Recurse -File -ErrorAction SilentlyContinue |
  Where-Object {
    $_.FullName -notmatch "\\\.git\\|\\\.venv\\|\\node_modules\\|\\__pycache__\\" -and
    $_.Name -match "v0\.7\.4.*\.(zip|msi|exe)$"
  }

if ($ForbiddenMilestoneArtifacts) {
  throw "Forbidden v0.7.4 build/distribution artifacts found: $($ForbiddenMilestoneArtifacts.FullName -join ', ')"
}

$AllowedChangedPaths = @(
  "docs/dev/v0.7.4-owner-local-ocr-math-report-smoke-fixture-no-build-no-distribution.md",
  "scripts/dev/check-v0.7.4-owner-local-ocr-math-report-smoke-fixture-no-build-no-distribution.ps1"
)

$Changed = git -C $RepoRoot status --short --untracked-files=all
foreach ($line in $Changed) {
  if (-not $line.Trim()) { continue }
  $path = $line.Substring(3).Trim()
  if ($path -match " -> ") {
    $path = ($path -split " -> ")[-1]
  }
  $normalized = $path -replace "\\", "/"
  if ($AllowedChangedPaths -notcontains $normalized) {
    throw "Unexpected changed path for v0.7.4 smoke-only milestone: $normalized"
  }
}

$Result = [ordered]@{
  milestone = "v0.7.4-owner-local-ocr-math-report-smoke-fixture-no-build-no-distribution"
  status = "PASS"
  final_main_check = [bool]$FinalMainCheck
  smoke_fixture_created_outside_repo = $true
  fixture_root = $FixtureRoot
  course_id = $CourseId
  summary_route_checked = $true
  raw_markdown_route_checked = $true
  viewer_route_checked = $true
  missing_report_404_checked = $true
  displays_sugestii_detectate = $true
  displays_linii_posibil_afectate = $true
  displays_diagnostic_local_read_only = $true
  no_auto_formula_correction = $true
  no_formula_ocr = $true
  no_ocr_pages_course_study_progress_rewrite = $true
  no_build = $true
  no_zip = $true
  no_delivery = $true
  no_distribution = $true
}

$Result | ConvertTo-Json -Depth 5