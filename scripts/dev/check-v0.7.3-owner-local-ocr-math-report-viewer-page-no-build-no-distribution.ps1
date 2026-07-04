param(
  [switch] $FinalMainCheck
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$WebApp = Join-Path $RepoRoot "services\api\web_app.py"
$Doc = Join-Path $RepoRoot "docs\dev\v0.7.3-owner-local-ocr-math-report-viewer-page-no-build-no-distribution.md"

if (-not (Test-Path $WebApp)) {
  throw "Missing services/api/web_app.py"
}

if (-not (Test-Path $Doc)) {
  throw "Missing v0.7.3 docs file"
}

$WebText = Get-Content $WebApp -Raw -Encoding UTF8
$DocText = Get-Content $Doc -Raw -Encoding UTF8

$RequiredWebMarkers = @(
  "VOILA_V0_7_1_OWNER_LOCAL_OCR_MATH_REPORT_UI_LINK_START",
  "VOILA_V0_7_2_OWNER_LOCAL_OCR_MATH_REPORT_UX_POLISH_APPLIED",
  "VOILA_V0_7_3_OWNER_LOCAL_OCR_MATH_REPORT_VIEWER_PAGE_APPLIED",
  "/owner/ocr-math-report/{course_id}/view",
  "_voila_owner_ocr_math_report_viewer",
  "_voila_ocr_math_report_markdown_to_html",
  "Diagnostic local · read-only",
  "Deschide raw .md",
  "Această pagină este doar pentru citire",
  "Nu modifică OCR-ul, cursul, Study sau Progress",
  "Sugestii detectate",
  "Linii posibil afectate",
  "/owner/ocr-math-report/{course_id}/summary.json",
  "/owner/ocr-math-report/{course_id}/ocr_math_report.md",
  "html.escape",
  "quote(str(course_id)"
)

foreach ($marker in $RequiredWebMarkers) {
  if ($WebText -notlike "*$marker*") {
    throw "Missing web marker: $marker"
  }
}

if ($WebText -notlike '*return "/owner/ocr-math-report/" + encodeURIComponent(id) + "/view";*') {
  throw "Card link was not updated to the read-only viewer route"
}

$RequiredDocMarkers = @(
  "read-only viewer",
  "/owner/ocr-math-report/{course_id}/view",
  "raw Markdown",
  "no build",
  "no ZIP",
  "no delivery",
  "no distribution",
  "VOILA_ENABLE_OCR_MATH_REPORT_HOOK=1",
  "does not",
  "Formula OCR",
  "accept suggestions",
  "reject suggestions"
)

foreach ($marker in $RequiredDocMarkers) {
  if ($DocText -notlike "*$marker*") {
    throw "Missing doc marker: $marker"
  }
}

Write-Host "== Python syntax check =="
python -m py_compile $WebApp

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
    $_.Name -match "v0\.7\.3.*\.(zip|msi|exe)$"
  }

if ($ForbiddenMilestoneArtifacts) {
  throw "Forbidden v0.7.3 build/distribution artifacts found: $($ForbiddenMilestoneArtifacts.FullName -join ', ')"
}

$AllowedChangedPaths = @(
  "services/api/web_app.py",
  "docs/dev/v0.7.3-owner-local-ocr-math-report-viewer-page-no-build-no-distribution.md",
  "scripts/dev/check-v0.7.3-owner-local-ocr-math-report-viewer-page-no-build-no-distribution.ps1"
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
    throw "Unexpected changed path for v0.7.3 no-build milestone: $normalized"
  }
}

$Result = [ordered]@{
  milestone = "v0.7.3-owner-local-ocr-math-report-viewer-page-no-build-no-distribution"
  status = "PASS"
  final_main_check = [bool]$FinalMainCheck
  viewer_route = "/owner/ocr-math-report/{course_id}/view"
  raw_markdown_route_preserved = "/owner/ocr-math-report/{course_id}/ocr_math_report.md"
  summary_route_preserved = "/owner/ocr-math-report/{course_id}/summary.json"
  read_only_viewer = $true
  raw_markdown_link_preserved = $true
  safe_markdown_escape = $true
  no_accept_reject_suggestions = $true
  no_auto_formula_correction = $true
  no_formula_ocr = $true
  no_ocr_pages_course_study_progress_rewrite = $true
  no_build = $true
  no_zip = $true
  no_delivery = $true
  no_distribution = $true
}

$Result | ConvertTo-Json -Depth 4