param(
    [string]$RepoRoot = "."
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Milestone = "v0.7.13-owner-local-read-only-smoke-index-consolidation-no-build-no-distribution"
Write-Host "VOILA_V0_7_13_READ_ONLY_SMOKE_INDEX_CONSOLIDATION_CHECK=START"
Write-Host "RepoRoot=$RepoRoot"
Write-Host "Milestone=$Milestone"

$root = Resolve-Path -LiteralPath $RepoRoot
Set-Location $root

$requiredFiles = @(
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

foreach ($file in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $file)) {
        throw "Missing required file: $file"
    }
    Write-Host "FOUND $file"
}

$docsToScan = @(
    "docs/dev/voila-read-only-smoke-index-consolidation-v0.7.13.md",
    "docs/dev/voila-read-only-smoke-next-step-gate-v0.7.13.md",
    "docs/dev/voila-read-only-smoke-consolidated-risk-notes-v0.7.13.md"
)

$requiredPolicyTerms = @(
    "no build",
    "no ZIP",
    "no delivery",
    "no distribution",
    "owner-local only",
    "no behavior changes",
    "read-only",
    "GET-only",
    "no non-GET write requests",
    "no upload/generate/save/delete/reset"
)

foreach ($doc in $docsToScan) {
    $text = Get-Content -Raw -LiteralPath $doc
    foreach ($term in $requiredPolicyTerms) {
        if ($text -notmatch [regex]::Escape($term)) {
            throw "Missing policy term '$term' in $doc"
        }
    }
    Write-Host "POLICY_TERMS_OK $doc"
}

$indexText = Get-Content -Raw -LiteralPath "docs/dev/voila-read-only-smoke-index-consolidation-v0.7.13.md"
foreach ($version in @("v0.7.9", "v0.7.10", "v0.7.11", "v0.7.12", "v0.7.13")) {
    if ($indexText -notmatch [regex]::Escape($version)) {
        throw "Missing version reference $version in consolidation index"
    }
}
Write-Host "VERSION_REFERENCE_CHAIN_OK docs/dev/voila-read-only-smoke-index-consolidation-v0.7.13.md"

$requiredRouteRefs = @(
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

foreach ($route in $requiredRouteRefs) {
    if ($indexText -notmatch [regex]::Escape($route)) {
        throw "Missing route reference '$route' in consolidation index"
    }
    Write-Host "CONSOLIDATED_ROUTE_REFERENCE_FOUND $route"
}

$forbiddenCommandPatterns = @(
    "npm\s+run\s+build",
    "pyinstaller",
    "Compress-Archive",
    "gh\s+release",
    "OneDrive",
    "Start-Process",
    "Invoke-WebRequest",
    "Invoke-RestMethod",
    "curl\s+",
    "POST",
    "UploadFile",
    "delete-course",
    "delete-from-library",
    "study-reset"
)

foreach ($doc in $docsToScan) {
    $text = Get-Content -Raw -LiteralPath $doc
    foreach ($pattern in $forbiddenCommandPatterns) {
        if ($text -match $pattern) {
            throw "Forbidden command/action pattern '$pattern' found in $doc"
        }
    }
    Write-Host "FORBIDDEN_COMMAND_PATTERN_SCAN_OK $doc"
}

$webApp = "services/api/web_app.py"
if (Test-Path -LiteralPath $webApp) {
    $routeLines = Select-String -LiteralPath $webApp -Pattern "@app\." -AllMatches
    $getLines = Select-String -LiteralPath $webApp -Pattern "@app\.get" -AllMatches
    $postLines = Select-String -LiteralPath $webApp -Pattern "@app\.post" -AllMatches
    Write-Host ("STATIC_ROUTE_SCAN web_app.py route_decorator_lines=" + $routeLines.Count)
    Write-Host ("STATIC_GET_ROUTE_SCAN web_app.py get_route_lines=" + $getLines.Count)
    Write-Host ("STATIC_POST_ROUTE_COUNT_ONLY web_app.py post_route_lines=" + $postLines.Count)
} else {
    Write-Host "STATIC_ROUTE_SCAN_SKIPPED services/api/web_app.py not found"
}

Write-Host "VOILA_V0_7_13_READ_ONLY_SMOKE_INDEX_CONSOLIDATION_CHECK=PASS"
Write-Host "POLICY=no_build_no_zip_no_delivery_no_distribution_owner_local_only_no_behavior_changes_read_only_get_only"

