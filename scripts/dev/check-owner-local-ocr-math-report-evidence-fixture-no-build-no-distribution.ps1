# v0.7.7 owner-local OCR Math report evidence fixture check
# Policy: no build, no ZIP, no delivery, no distribution.

[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Fail {
    param([string]$Message)
    throw $Message
}

function OutText {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Exe,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Args
    )
    $lines = @(& $Exe @Args 2>$null)
    if ($null -eq $lines -or $lines.Count -eq 0) {
        return ""
    }
    return (($lines | ForEach-Object { [string]$_ }) -join "`n")
}

function Assert-File {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        Fail "Missing required file: $Path"
    }
}

function Assert-Contains {
    param(
        [string]$Text,
        [string]$Needle,
        [string]$Label
    )
    if (-not $Text.Contains($Needle)) {
        Fail "Missing expected content [$Label]: $Needle"
    }
}

function Assert-NotContains {
    param(
        [string]$Text,
        [string]$Needle,
        [string]$Label
    )
    if ($Text.Contains($Needle)) {
        Fail "Forbidden content found [$Label]: $Needle"
    }
}

Set-Location $RepoRoot

$webApp = "services/api/web_app.py"
$fixture = "docs/dev/fixtures/ocr_math_report_v0_7_7.fixture.md"
$doc = "docs/dev/v0.7.7-owner-local-ocr-math-report-evidence-fixture-check-no-build-no-distribution.md"

Assert-File $webApp
Assert-File $fixture
Assert-File $doc

python -m py_compile $webApp
if ($LASTEXITCODE -ne 0) {
    Fail "Python compile failed for $webApp"
}

$webText = [System.IO.File]::ReadAllText((Resolve-Path $webApp))
$fixtureText = [System.IO.File]::ReadAllText((Resolve-Path $fixture))
$docText = [System.IO.File]::ReadAllText((Resolve-Path $doc))

Assert-Contains $webText "/owner/ocr-math-report/{course_id}/view" "owner OCR Math viewer route"
Assert-Contains $webText "Sugestii detectate" "viewer summary metric"
Assert-Contains $webText "Linii posibil afectate" "viewer affected lines metric"
Assert-Contains $webText "Diagnostic local · read-only" "viewer local read-only diagnostic copy"

Assert-Contains $fixtureText "Diagnostic local · read-only" "fixture diagnostic marker"
Assert-Contains $fixtureText "Sugestii detectate: 2" "fixture suggestions metric"
Assert-Contains $fixtureText "Linii posibil afectate: 3" "fixture affected lines metric"
Assert-Contains $fixtureText "[Open raw Markdown report](ocr_math_report.md)" "fixture raw Markdown link expectation"
Assert-Contains $fixtureText "local-only evidence" "fixture local-only marker"
Assert-Contains $fixtureText "must not trigger generation" "fixture non-generation marker"

Assert-Contains $docText "Baseline: v0.7.6" "doc baseline"
Assert-Contains $docText "FINAL_MAIN_HEAD=644518b" "doc baseline head"
Assert-Contains $docText "no build" "doc no build policy"
Assert-Contains $docText "no ZIP" "doc no ZIP policy"
Assert-Contains $docText "no delivery" "doc no delivery policy"
Assert-Contains $docText "no distribution" "doc no distribution policy"
Assert-Contains $docText "OCR/pages/course/Study/Progress rewrite" "doc forbidden rewrite policy"

# Make sure this milestone changed only docs/dev and scripts/dev paths.
$changedNames = OutText git diff --name-only main...HEAD
$workingChanges = OutText git diff --name-only
$stagedChanges = OutText git diff --cached --name-only
$untracked = OutText git ls-files --others --exclude-standard
$allChanged = @()

foreach ($block in @($changedNames, $workingChanges, $stagedChanges, $untracked)) {
    if (-not [string]::IsNullOrWhiteSpace($block)) {
        $allChanged += $block -split "`n"
    }
}

$allChanged = $allChanged | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique

foreach ($path in $allChanged) {
    $p = $path.Replace("\", "/")
    if (-not ($p.StartsWith("docs/dev/") -or $p.StartsWith("scripts/dev/"))) {
        Fail "Forbidden modified path for v0.7.7 policy: $path"
    }
}

# Forbidden artifact/distribution keywords in the new milestone doc and fixture files.
# Context words may appear in policy text only; these commands must not appear as executable actions.
$combined = $docText + "`n" + $fixtureText
Assert-NotContains $combined "build-windows" "build script reference"
Assert-NotContains $combined "create-windows" "package creation reference"
Assert-NotContains $combined ".zip.sha256" "zip checksum artifact"
Assert-NotContains $combined "GitHub release upload" "release upload reference"
Assert-NotContains $combined "OneDrive target" "distribution target reference"

Write-Host "VOILA_V0_7_7_OWNER_LOCAL_OCR_MATH_REPORT_EVIDENCE_FIXTURE_CHECK=PASS"
Write-Host "fixture_present=true"
Write-Host "fixture_is_local_only=true"
Write-Host "viewer_expected_copy_verified=true"
Write-Host "raw_markdown_link_expectation_verified=true"
Write-Host "ocr_pages_course_study_progress_rewrite_touched=false"
Write-Host "POLICY=no_build_no_zip_no_delivery_no_distribution"