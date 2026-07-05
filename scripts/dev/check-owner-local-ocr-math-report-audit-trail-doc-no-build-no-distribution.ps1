# v0.7.8 owner-local OCR Math report audit trail doc check
# Policy: no build, no ZIP, no delivery, no distribution.
# Scope: documentation/audit trail only.

[CmdletBinding()]
param([string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Fail([string]$Message) { throw $Message }
function OutText {
    param([Parameter(Mandatory = $true)][string]$Exe, [Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    $lines = @(& $Exe @Args 2>$null)
    if ($null -eq $lines -or $lines.Count -eq 0) { return "" }
    return (($lines | ForEach-Object { [string]$_ }) -join "`n")
}
function Assert-File([string]$Path) { if (-not (Test-Path $Path)) { Fail "Missing required file: $Path" } }
function Assert-Contains([string]$Text, [string]$Needle, [string]$Label) { if (-not $Text.Contains($Needle)) { Fail "Missing expected content [$Label]: $Needle" } }
function Assert-NotContains([string]$Text, [string]$Needle, [string]$Label) { if ($Text.Contains($Needle)) { Fail "Forbidden content found [$Label]: $Needle" } }

Set-Location $RepoRoot
$doc = "docs/dev/v0.7.8-owner-local-ocr-math-report-audit-trail-doc-no-build-no-distribution.md"
$check = "scripts/dev/check-owner-local-ocr-math-report-audit-trail-doc-no-build-no-distribution.ps1"
Assert-File $doc
Assert-File $check
$docText = [System.IO.File]::ReadAllText((Resolve-Path $doc))
$checkText = [System.IO.File]::ReadAllText((Resolve-Path $check))

Assert-Contains $docText "Baseline FINAL_MAIN_HEAD=ba7a04d" "baseline head"
Assert-Contains $docText "v0.7.3" "v0.7.3 chain entry"
Assert-Contains $docText "v0.7.4 / v0.7.5" "v0.7.4/v0.7.5 chain entry"
Assert-Contains $docText "v0.7.6" "v0.7.6 chain entry"
Assert-Contains $docText "v0.7.7" "v0.7.7 chain entry"
Assert-Contains $docText "fd41900" "v0.7.5 final head"
Assert-Contains $docText "644518b" "v0.7.6 final head"
Assert-Contains $docText "ba7a04d" "v0.7.7 final head"
Assert-Contains $docText "/owner/ocr-math-report/{course_id}/view" "owner OCR Math viewer route"
Assert-Contains $docText "Sugestii detectate" "viewer summary metric reference"
Assert-Contains $docText "Linii posibil afectate" "viewer affected lines metric reference"
Assert-Contains $docText "Diagnostic local · read-only" "viewer local read-only diagnostic reference"
Assert-Contains $docText "raw Markdown report link" "raw Markdown link reference"
Assert-Contains $docText "no build" "no build policy"
Assert-Contains $docText "no ZIP" "no ZIP policy"
Assert-Contains $docText "no delivery" "no delivery policy"
Assert-Contains $docText "no distribution" "no distribution policy"
Assert-Contains $docText "OCR generation" "OCR non-goal"
Assert-Contains $docText "pages generation" "pages non-goal"
Assert-Contains $docText "course generation" "course non-goal"
Assert-Contains $docText "course.cleaned.md" "course cleaned non-goal"
Assert-Contains $docText "Study flow" "Study non-goal"
Assert-Contains $docText "Progress flow" "Progress non-goal"
Assert-Contains $docText "documentation/audit-trail only" "doc-only scope"
Assert-Contains $docText "VOILA_V0_7_8_OWNER_LOCAL_OCR_MATH_REPORT_AUDIT_TRAIL_DOC=PASS" "expected milestone PASS marker"
Assert-Contains $docText "VOILA_V0_7_8_MERGED_FINAL_MAIN_CHECK=PASS" "expected final main PASS marker"
Assert-Contains $docText "ocr_pages_course_study_progress_rewrite_touched=false" "rewrite untouched marker"
Assert-Contains $docText "POLICY=no_build_no_zip_no_delivery_no_distribution" "policy marker"

$changedNames = OutText git diff --name-only main...HEAD
$workingChanges = OutText git diff --name-only
$stagedChanges = OutText git diff --cached --name-only
$untracked = OutText git ls-files --others --exclude-standard
$allChanged = @()
foreach ($block in @($changedNames, $workingChanges, $stagedChanges, $untracked)) {
    if (-not [string]::IsNullOrWhiteSpace($block)) { $allChanged += $block -split "`n" }
}
$allChanged = $allChanged | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique
foreach ($path in $allChanged) {
    $p = $path.Replace("\", "/")
    if (-not ($p.StartsWith("docs/dev/") -or $p.StartsWith("scripts/dev/"))) { Fail "Forbidden modified path for v0.7.8 policy: $path" }
}

Assert-NotContains $docText "build-windows" "build script reference"
Assert-NotContains $docText "create-windows" "package creation reference"
Assert-NotContains $docText ".zip.sha256" "zip checksum artifact"
Assert-NotContains $docText "GitHub release upload" "release upload reference"
Assert-NotContains $docText "OneDrive target" "distribution target reference"
Assert-Contains $checkText "documentation/audit trail only" "check script scope"
Assert-Contains $checkText "no build, no ZIP, no delivery, no distribution" "check script policy"

Write-Host "VOILA_V0_7_8_OWNER_LOCAL_OCR_MATH_REPORT_AUDIT_TRAIL_DOC=PASS"
Write-Host "baseline_main_head=ba7a04d"
Write-Host "audit_chain_recorded=true"
Write-Host "viewer_route_reference_recorded=true"
Write-Host "viewer_copy_reference_recorded=true"
Write-Host "ocr_pages_course_study_progress_rewrite_touched=false"
Write-Host "POLICY=no_build_no_zip_no_delivery_no_distribution"