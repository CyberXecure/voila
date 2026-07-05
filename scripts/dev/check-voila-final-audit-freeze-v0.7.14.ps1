param(
    [Parameter(Mandatory=$false)]
    [string]$RepoRoot = "."
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Milestone = "v0.7.14-owner-local-final-audit-freeze-no-build-no-distribution"

function Get-RepoPath {
    param([string]$RelativePath)
    return Join-Path $RepoRoot $RelativePath
}

function Assert-FileExists {
    param([string]$RelativePath)

    $Path = Get-RepoPath $RelativePath
    if (-not (Test-Path $Path)) {
        throw "Missing required file: $RelativePath"
    }

    Write-Output "FOUND $RelativePath"
}

function Assert-Contains {
    param(
        [string]$RelativePath,
        [string]$Needle
    )

    $Path = Get-RepoPath $RelativePath
    $Text = Get-Content -Raw -Path $Path
    if ($Text -notmatch [regex]::Escape($Needle)) {
        throw "Missing required text '$Needle' in $RelativePath"
    }
}

function Assert-NotContainsPattern {
    param(
        [string]$RelativePath,
        [string]$Pattern
    )

    $Path = Get-RepoPath $RelativePath
    $Text = Get-Content -Raw -Path $Path
    if ($Text -match $Pattern) {
        throw "Forbidden command/action pattern '$Pattern' found in $RelativePath"
    }
}

Write-Output "VOILA_V0_7_14_FINAL_AUDIT_FREEZE_CHECK=START"
Write-Output "RepoRoot=$RepoRoot"
Write-Output "Milestone=$Milestone"

$requiredPrevious = @(
    "docs/dev/voila-functional-audit-inventory-v0.7.9.md",
    "docs/dev/voila-functional-smoke-map-v0.7.9.md",
    "docs/dev/voila-functional-test-checklist-v0.7.9.md",
    "docs/dev/voila-functional-audit-policy-v0.7.9.md",
    "scripts/dev/check-voila-functional-audit-baseline-v0.7.9.ps1",
    "docs/dev/voila-manual-smoke-runbook-v0.7.10.md",
    "docs/dev/voila-manual-smoke-evidence-v0.7.10.md",
    "docs/dev/voila-manual-smoke-risk-register-v0.7.10.md",
    "scripts/dev/check-voila-manual-smoke-evidence-v0.7.10.ps1",
    "docs/dev/voila-read-only-route-smoke-runbook-v0.7.11.md",
    "docs/dev/voila-read-only-route-smoke-map-v0.7.11.md",
    "docs/dev/voila-read-only-route-smoke-evidence-template-v0.7.11.md",
    "docs/dev/voila-read-only-route-smoke-policy-v0.7.11.md",
    "scripts/dev/check-voila-read-only-route-smoke-doc-v0.7.11.ps1",
    "docs/dev/voila-read-only-route-smoke-evidence-index-v0.7.12.md",
    "docs/dev/voila-read-only-route-smoke-evidence-log-v0.7.12.md",
    "docs/dev/voila-read-only-route-smoke-session-notes-v0.7.12.md",
    "docs/dev/voila-read-only-route-smoke-non-destructive-boundary-v0.7.12.md",
    "scripts/dev/check-voila-read-only-route-smoke-evidence-v0.7.12.ps1",
    "docs/dev/voila-read-only-smoke-index-consolidation-v0.7.13.md",
    "docs/dev/voila-read-only-smoke-next-step-gate-v0.7.13.md",
    "docs/dev/voila-read-only-smoke-consolidated-risk-notes-v0.7.13.md",
    "scripts/dev/check-voila-read-only-smoke-index-consolidation-v0.7.13.ps1"
)

$requiredCurrent = @(
    "docs/dev/voila-final-audit-freeze-v0.7.14.md",
    "docs/dev/voila-final-audit-freeze-index-v0.7.14.md",
    "docs/dev/voila-final-audit-freeze-policy-v0.7.14.md",
    "docs/dev/voila-final-audit-freeze-next-step-gate-v0.7.14.md",
    "scripts/dev/check-voila-final-audit-freeze-v0.7.14.ps1"
)

foreach ($file in ($requiredPrevious + $requiredCurrent)) {
    Assert-FileExists $file
}

$currentDocs = @(
    "docs/dev/voila-final-audit-freeze-v0.7.14.md",
    "docs/dev/voila-final-audit-freeze-index-v0.7.14.md",
    "docs/dev/voila-final-audit-freeze-policy-v0.7.14.md",
    "docs/dev/voila-final-audit-freeze-next-step-gate-v0.7.14.md"
)

$requiredPolicyTerms = @(
    "v0.7.14-owner-local-final-audit-freeze-no-build-no-distribution",
    "no build",
    "no ZIP",
    "no delivery",
    "no distribution",
    "owner-local only",
    "no behavior changes",
    "no feature changes",
    "no public UI expansion",
    "read-only GET-only",
    "no non-GET write requests",
    "no upload/generate/save/delete/reset",
    "no server startup",
    "no live HTTP smoke",
    "documentation-only",
    "static/read-only validation"
)

foreach ($doc in $currentDocs) {
    foreach ($term in $requiredPolicyTerms) {
        Assert-Contains $doc $term
    }
    Write-Output "POLICY_TERMS_OK $doc"
}

$freezeIndex = "docs/dev/voila-final-audit-freeze-index-v0.7.14.md"
foreach ($version in @("v0.7.9", "v0.7.10", "v0.7.11", "v0.7.12", "v0.7.13", "v0.7.14")) {
    Assert-Contains $freezeIndex $version
}
Write-Output "VERSION_REFERENCE_CHAIN_OK $freezeIndex"

$expectedRoutes = @(
    "/health",
    "/quick-tools",
    "/course-tools",
    "/view-course",
    "/view-figures",
    "/review",
    "/review-concepts",
    "/review-ocr-text",
    "/review-ocr-corrected",
    "/edit-crops",
    "/progress",
    "/study",
    "/exam-prep",
    "/owner/ocr-math-report/{course_id}/view"
)

foreach ($route in $expectedRoutes) {
    Assert-Contains $freezeIndex $route
    Write-Output "FREEZE_ROUTE_REFERENCE_FOUND $route"
}

$forbiddenCommandPatterns = @(
    "Invoke-WebRequest",
    "Invoke-RestMethod",
    "\bcurl\b",
    "\bwget\b",
    "Start-Process",
    "npm\s+run\s+build",
    "pyinstaller",
    "Compress-Archive",
    "Expand-Archive",
    "\.zip\b",
    "gh\s+release",
    "docker\s+build",
    "\bscp\b",
    "\brsync\b",
    "OneDrive",
    "Dropbox",
    "Google Drive",
    "\bPOST\b"
)

foreach ($doc in $currentDocs) {
    foreach ($pattern in $forbiddenCommandPatterns) {
        Assert-NotContainsPattern $doc $pattern
    }
    Write-Output "FORBIDDEN_COMMAND_PATTERN_SCAN_OK $doc"
}

$webApp = Get-RepoPath "services/api/web_app.py"
if (Test-Path $webApp) {
    $webText = Get-Content -Raw -Path $webApp
    $routeCount = ([regex]::Matches($webText, "@app\.(get|post|put|delete|patch)\(")).Count
    $getRouteCount = ([regex]::Matches($webText, "@app\.get\(")).Count
    $nonGetRouteCount = ([regex]::Matches($webText, "@app\.(post|put|delete|patch)\(")).Count
    Write-Output "STATIC_ROUTE_SCAN web_app.py route_decorator_lines=$routeCount"
    Write-Output "STATIC_GET_ROUTE_SCAN web_app.py get_route_lines=$getRouteCount"
    Write-Output "STATIC_NON_GET_ROUTE_COUNT_ONLY web_app.py non_get_route_lines=$nonGetRouteCount"
} else {
    throw "Missing source file for static route scan: services/api/web_app.py"
}

Write-Output "VOILA_V0_7_14_FINAL_AUDIT_FREEZE_CHECK=PASS"
Write-Output "POLICY=no_build_no_zip_no_delivery_no_distribution_owner_local_only_no_behavior_changes_read_only_get_only"
