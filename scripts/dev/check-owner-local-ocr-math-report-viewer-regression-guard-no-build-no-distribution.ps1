param(
  [string]$RepoRoot
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$Milestone = "v0.7.6-owner-local-ocr-math-report-viewer-regression-guard-no-build-no-distribution"
$PassMarker = "VOILA_V0_7_6_OWNER_LOCAL_OCR_MATH_REPORT_VIEWER_REGRESSION_GUARD=PASS"

if (-not $RepoRoot -or $RepoRoot.Trim() -eq "") {
  $RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}

function Assert-True {
  param(
    [bool]$Condition,
    [string]$Message
  )
  if (-not $Condition) {
    throw $Message
  }
}

function Assert-File {
  param([string]$Path)
  Assert-True (Test-Path -LiteralPath $Path -PathType Leaf) "Missing file: $Path"
}

function Get-GitChangedFiles {
  $lines = @(git status --porcelain=v1)
  $files = New-Object System.Collections.Generic.List[string]

  foreach ($line in $lines) {
    if ($line.Length -lt 4) { continue }
    $path = $line.Substring(3)
    if ($path -match " -> ") {
      $path = ($path -split " -> ")[-1]
    }
    $path = $path.Trim('"').Replace("\", "/")
    if ($path) {
      $files.Add($path)
    }
  }

  return @($files)
}

function Invoke-PythonCompile {
  param([string]$Target)

  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($python) {
    & $python.Source -m py_compile $Target
    if ($LASTEXITCODE -eq 0) { return }
  }

  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) {
    & $py.Source -3 -m py_compile $Target
    if ($LASTEXITCODE -eq 0) { return }
  }

  throw "Python compile failed for $Target"
}

Set-Location -LiteralPath $RepoRoot

$webAppRel = "services/api/web_app.py"
$webApp = Join-Path $RepoRoot $webAppRel
$checkRel = "scripts/dev/check-owner-local-ocr-math-report-viewer-regression-guard-no-build-no-distribution.ps1"
$docRel = "docs/dev/$Milestone.md"
$checkPath = Join-Path $RepoRoot $checkRel
$docPath = Join-Path $RepoRoot $docRel

Assert-File $webApp
Assert-File $checkPath
Assert-File $docPath

Invoke-PythonCompile $webApp

$web = Get-Content -LiteralPath $webApp -Raw -Encoding UTF8
Assert-True ($web.Contains('/owner/ocr-math-report/{course_id}/view')) "Missing owner-local OCR Math report viewer route."
Assert-True ($web.Contains('Sugestii detectate')) "Missing summary metric copy: Sugestii detectate."
Assert-True ($web.Contains('Linii posibil afectate')) "Missing summary metric copy: Linii posibil afectate."
Assert-True ($web.Contains('Diagnostic local · read-only')) "Missing diagnostic read-only copy."
Assert-True ($web.Contains('ocr_math_report.md')) "Missing preserved raw Markdown report reference/link."
Assert-True (($web -match 'html\.escape') -or ($web -match 'escape\(')) "Expected safe escaping in report viewer rendering."

$doc = Get-Content -LiteralPath $docPath -Raw -Encoding UTF8
Assert-True ($doc.Contains('baseline: v0.7.5')) "Doc must record v0.7.5 baseline."
Assert-True ($doc.Contains('fd41900')) "Doc must record final main HEAD fd41900."
Assert-True ($doc.Contains('no build')) "Doc must record no build policy."
Assert-True ($doc.Contains('no ZIP')) "Doc must record no ZIP policy."
Assert-True ($doc.Contains('no delivery')) "Doc must record no delivery policy."
Assert-True ($doc.Contains('no distribution')) "Doc must record no distribution policy."
Assert-True ($doc.Contains('OCR/pages/course/Study/Progress')) "Doc must record forbidden rewrite areas."

$allowedChanged = @(
  $checkRel,
  $docRel
)

$changedFiles = @(Get-GitChangedFiles)
foreach ($changed in $changedFiles) {
  Assert-True ($allowedChanged -contains $changed) "Forbidden changed file for this milestone: $changed"
  Assert-True (-not ($changed -match '\.(zip|exe|msi|7z|tar|gz)$')) "Forbidden release/delivery artifact changed: $changed"
}

$forbiddenChangedPatterns = @(
  '^services/api/(ocr|ocr_|pages|course|study|progress)',
  '^services/api/web_app\.py$',
  '^services/api/exam_prep',
  '^data/',
  '^dist/',
  '^build/',
  '^release/',
  '^packages/'
)

foreach ($changed in $changedFiles) {
  foreach ($pattern in $forbiddenChangedPatterns) {
    Assert-True (-not ($changed -match $pattern)) "Forbidden rewrite/delivery area changed: $changed"
  }
}

$result = [ordered]@{
  milestone = $Milestone
  status = "PASS"
  no_build = $true
  no_zip = $true
  no_delivery = $true
  no_distribution = $true
  ocr_pages_course_study_progress_rewrite_touched = $false
  viewer_route_present = $true
  viewer_read_only = $true
  raw_markdown_link_preserved = $true
  summary_metrics_present = $true
  final_status_check = "PASS"
}

Write-Host ""
Write-Host ($result | ConvertTo-Json -Depth 4)
Write-Host ""
Write-Host $PassMarker