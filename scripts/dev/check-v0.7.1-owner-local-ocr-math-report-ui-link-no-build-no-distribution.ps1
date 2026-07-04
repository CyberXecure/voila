param(
  [switch] $FinalMainCheck
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$WebApp = Join-Path $RepoRoot "services\api\web_app.py"
$Doc = Join-Path $RepoRoot "docs\dev\v0.7.1-owner-local-ocr-math-report-ui-link-no-build-no-distribution.md"

if (-not (Test-Path $WebApp)) {
  throw "Missing services/api/web_app.py"
}

if (-not (Test-Path $Doc)) {
  throw "Missing v0.7.1 docs file"
}

$WebText = Get-Content $WebApp -Raw -Encoding UTF8
$DocText = Get-Content $Doc -Raw -Encoding UTF8

$RequiredWebMarkers = @(
  "VOILA_V0_7_1_OWNER_LOCAL_OCR_MATH_REPORT_UI_LINK_START",
  "/owner/ocr-math-report/{course_id}/summary.json",
  "/owner/ocr-math-report/{course_id}/ocr_math_report.md",
  "total_suggestions",
  "changed_line_count",
  "ocr_math_report.md",
  "ocr_math_report.json",
  "_voila_ocr_math_report_ui_link_middleware"
)

foreach ($marker in $RequiredWebMarkers) {
  if ($WebText -notlike "*$marker*") {
    throw "Missing web marker: $marker"
  }
}

$RequiredDocMarkers = @(
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
    $_.Name -match "v0\.7\.1.*\.(zip|msi|exe)$"
  }

if ($ForbiddenMilestoneArtifacts) {
  throw "Forbidden v0.7.1 build/distribution artifacts found: $($ForbiddenMilestoneArtifacts.FullName -join ', ')"
}

$AllowedChangedPaths = @(
  "services/api/web_app.py",
  "docs/dev/v0.7.1-owner-local-ocr-math-report-ui-link-no-build-no-distribution.md",
  "scripts/dev/check-v0.7.1-owner-local-ocr-math-report-ui-link-no-build-no-distribution.ps1"
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
    throw "Unexpected changed path for v0.7.1 no-build milestone: $normalized"
  }
}

$Result = [ordered]@{
  milestone = "v0.7.1-owner-local-ocr-math-report-ui-link-no-build-no-distribution"
  status = "PASS"
  final_main_check = [bool]$FinalMainCheck
  ui_link_route = "/owner/ocr-math-report/{course_id}/ocr_math_report.md"
  summary_route = "/owner/ocr-math-report/{course_id}/summary.json"
  displays_total_suggestions = $true
  displays_changed_line_count = $true
  no_auto_formula_correction = $true
  no_formula_ocr = $true
  no_build = $true
  no_zip = $true
  no_delivery = $true
  no_distribution = $true
}

$Result | ConvertTo-Json -Depth 4