param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"

$Milestone = "v0.7.9-owner-local-functional-audit-baseline-no-build-no-distribution"
$RequiredFiles = @(
    "docs/dev/voila-functional-audit-inventory-v0.7.9.md",
    "docs/dev/voila-functional-smoke-map-v0.7.9.md",
    "docs/dev/voila-functional-test-checklist-v0.7.9.md",
    "docs/dev/voila-functional-audit-policy-v0.7.9.md",
    "scripts/dev/check-voila-functional-audit-baseline-v0.7.9.ps1"
)

$RequiredPolicyPhrases = @(
    "no build",
    "no ZIP",
    "no delivery",
    "no distribution",
    "owner-local only",
    "no feature changes",
    "no OCR/pages/course/Study/Progress rewrite",
    "no public UI expansion",
    "no behavior changes"
)

$RequiredSectionsByFile = @{
    "docs/dev/voila-functional-audit-inventory-v0.7.9.md" = @(
        "# Voila Functional Audit Inventory v0.7.9",
        "## Policy",
        "## Purpose",
        "## Core application surfaces",
        "## Owner-local OCR Math report surfaces",
        "## Risk classification",
        "## Completion criteria"
    )
    "docs/dev/voila-functional-smoke-map-v0.7.9.md" = @(
        "# Voila Functional Smoke Map v0.7.9",
        "## Policy",
        "## Smoke map purpose",
        "## Smoke levels",
        "## Application smoke map",
        "## Static validation smoke map"
    )
    "docs/dev/voila-functional-test-checklist-v0.7.9.md" = @(
        "# Voila Functional Test Checklist v0.7.9",
        "## Policy",
        "## Checklist use",
        "## Checklist table",
        "## Required result statuses",
        "## Non-destructive execution rules"
    )
    "docs/dev/voila-functional-audit-policy-v0.7.9.md" = @(
        "# Voila Functional Audit Policy v0.7.9",
        "## Policy summary",
        "## Mandatory constraints",
        "## Allowed changes",
        "## Forbidden changes",
        "## Allowed validation behavior",
        "## Server policy",
        "## Evidence policy",
        "## Next milestone boundary"
    )
}

function Fail {
    param([string]$Message)
    throw "VOILA_V0_7_9_FUNCTIONAL_AUDIT_BASELINE_CHECK=FAIL :: $Message"
}

function Read-FileText {
    param([string]$RelativePath)
    $full = Join-Path $RepoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $full)) {
        Fail "Missing required file: $RelativePath"
    }
    return [System.IO.File]::ReadAllText($full)
}

Write-Host "VOILA_V0_7_9_FUNCTIONAL_AUDIT_BASELINE_CHECK=START"
Write-Host "RepoRoot=$RepoRoot"
Write-Host "Milestone=$Milestone"

foreach ($file in $RequiredFiles) {
    $full = Join-Path $RepoRoot $file
    if (-not (Test-Path -LiteralPath $full)) {
        Fail "Missing required file: $file"
    }
    Write-Host "FOUND $file"
}

foreach ($file in $RequiredSectionsByFile.Keys) {
    $text = Read-FileText -RelativePath $file
    foreach ($section in $RequiredSectionsByFile[$file]) {
        if ($text -notlike "*$section*") {
            Fail "Missing required section '$section' in $file"
        }
    }
    foreach ($phrase in $RequiredPolicyPhrases) {
        if ($text -notlike "*$phrase*") {
            Fail "Missing policy phrase '$phrase' in $file"
        }
    }
    Write-Host "POLICY_AND_SECTIONS_OK $file"
}

# Keep these command patterns split/constructed so the check script does not accidentally match itself as policy-violating documentation.
$ForbiddenPatterns = @(
    ("npm" + "\s+" + "run" + "\s+" + "build"),
    ("pnpm" + "\s+" + "build"),
    ("yarn" + "\s+" + "build"),
    ("py" + "installer"),
    ("cx" + "_" + "Freeze"),
    ("Compress" + "-" + "Archive"),
    ("7z" + "\s+a"),
    ("gh" + "\s+" + "release"),
    ("twine" + "\s+" + "upload"),
    ("Invoke" + "-" + "WebRequest"),
    ("curl" + "\s+.*" + "upload"),
    ("scp" + "\s+"),
    ("robo" + "copy" + ".*" + "One" + "Drive"),
    ("Start" + "-" + "Process" + ".*" + "OneDrive"),
    ("START" + "-" + "VOILA"),
    ("start" + "-" + "voila"),
    ("VOILA_ENABLE_OCR_MATH_REPORT_HOOK" + "=1" + ".*" + "gen" + "erate")
)

foreach ($file in $RequiredFiles) {
    $text = Read-FileText -RelativePath $file
    foreach ($pattern in $ForbiddenPatterns) {
        if ($text -match $pattern) {
            Fail "Forbidden build/package/delivery/distribution/execution pattern '$pattern' found in $file"
        }
    }
    Write-Host "FORBIDDEN_PATTERN_SCAN_OK $file"
}

$webApp = Join-Path $RepoRoot "services/api/web_app.py"
if (Test-Path -LiteralPath $webApp) {
    $routeMatches = Select-String -Path $webApp -Pattern '@app\.(get|post|put|patch|delete)\(' -AllMatches
    Write-Host "STATIC_ROUTE_SCAN web_app.py route_decorator_lines=$($routeMatches.Count)"
    foreach ($match in $routeMatches | Select-Object -First 30) {
        Write-Host ("ROUTE_TEXT_LINE {0}: {1}" -f $match.LineNumber, $match.Line.Trim())
    }
    if ($routeMatches.Count -gt 30) {
        Write-Host "ROUTE_TEXT_LINE additional_lines_omitted=$($routeMatches.Count - 30)"
    }
} else {
    Write-Host "STATIC_ROUTE_SCAN_SKIPPED services/api/web_app.py not found"
}

Write-Host "VOILA_V0_7_9_FUNCTIONAL_AUDIT_BASELINE_CHECK=PASS"
Write-Host "POLICY=no_build_no_zip_no_delivery_no_distribution_owner_local_only_no_behavior_changes"