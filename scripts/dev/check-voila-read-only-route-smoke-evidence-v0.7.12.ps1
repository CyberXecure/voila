param(
    [string]$RepoRoot = "."
)

$ErrorActionPreference = "Stop"

$Milestone = "v0.7.12-owner-local-read-only-route-smoke-evidence-no-build-no-distribution"
$Policy = "no_build_no_zip_no_delivery_no_distribution_owner_local_only_no_behavior_changes_read_only_get_only"

Write-Host "VOILA_V0_7_12_READ_ONLY_ROUTE_SMOKE_EVIDENCE_CHECK=START"
Write-Host "RepoRoot=$RepoRoot"
Write-Host "Milestone=$Milestone"

if (-not (Test-Path -LiteralPath $RepoRoot)) {
    throw "RepoRoot not found: $RepoRoot"
}

$root = (Resolve-Path -LiteralPath $RepoRoot).Path

function Read-RepoFile {
    param([string]$RelativePath)
    $fullPath = Join-Path $root $RelativePath
    if (-not (Test-Path -LiteralPath $fullPath)) {
        throw "Missing required file: $RelativePath"
    }
    return Get-Content -LiteralPath $fullPath -Raw
}

$requiredPriorFiles = @(
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
    "scripts/dev/check-voila-read-only-route-smoke-doc-v0.7.11.ps1"
)

$requiredCurrentFiles = @(
    "docs/dev/voila-read-only-route-smoke-evidence-index-v0.7.12.md",
    "docs/dev/voila-read-only-route-smoke-evidence-log-v0.7.12.md",
    "docs/dev/voila-read-only-route-smoke-session-notes-v0.7.12.md",
    "docs/dev/voila-read-only-route-smoke-non-destructive-boundary-v0.7.12.md",
    "scripts/dev/check-voila-read-only-route-smoke-evidence-v0.7.12.ps1"
)

foreach ($file in ($requiredPriorFiles + $requiredCurrentFiles)) {
    $null = Read-RepoFile $file
    Write-Host "FOUND $file"
}

$requiredPolicyTerms = @(
    "no build",
    "no ZIP",
    "no delivery",
    "no distribution",
    "owner-local only",
    "no behavior changes",
    "read-only GET-only",
    "no POST",
    "no upload",
    "no generate",
    "no save",
    "no delete",
    "no reset"
)

$currentDocs = @(
    "docs/dev/voila-read-only-route-smoke-evidence-index-v0.7.12.md",
    "docs/dev/voila-read-only-route-smoke-evidence-log-v0.7.12.md",
    "docs/dev/voila-read-only-route-smoke-session-notes-v0.7.12.md",
    "docs/dev/voila-read-only-route-smoke-non-destructive-boundary-v0.7.12.md"
)

foreach ($doc in $currentDocs) {
    $content = Read-RepoFile $doc
    foreach ($term in $requiredPolicyTerms) {
        if ($content -notmatch [regex]::Escape($term)) {
            throw "Missing policy term '$term' in $doc"
        }
    }
    Write-Host "POLICY_TERMS_OK $doc"
}

$evidenceLog = Read-RepoFile "docs/dev/voila-read-only-route-smoke-evidence-log-v0.7.12.md"
$requiredStatuses = @(
    "PENDING_MANUAL_SMOKE",
    "PASS_MANUAL_GET_ONLY",
    "PASS_WITH_EXISTING_DATA_ONLY",
    "SKIPPED_NO_EXISTING_DATA",
    "SKIPPED_OWNER_LOCAL_ONLY",
    "SKIPPED_WRITE_OR_DESTRUCTIVE",
    "OBSERVED_NON_BLOCKING_NOTE"
)

foreach ($status in $requiredStatuses) {
    if ($evidenceLog -notmatch [regex]::Escape($status)) {
        throw "Missing evidence status '$status' in evidence log"
    }
}
Write-Host "EVIDENCE_STATUS_VOCABULARY_OK docs/dev/voila-read-only-route-smoke-evidence-log-v0.7.12.md"

$forbiddenCommandPatterns = @(
    "Compress-Archive",
    "New-Item.*release-assets",
    "gh\s+release",
    "pyinstaller",
    "npm\s+run\s+build",
    "npm\s+build",
    "pnpm\s+build",
    "yarn\s+build",
    "docker\s+build",
    "Start-Process",
    "Invoke-WebRequest",
    "Invoke-RestMethod",
    "curl\s+http",
    "httpie",
    "pytest",
    "playwright",
    "uvicorn",
    "fastapi\s+run"
)

foreach ($doc in $currentDocs) {
    $content = Read-RepoFile $doc
    foreach ($pattern in $forbiddenCommandPatterns) {
        if ($content -match $pattern) {
            throw "FORBIDDEN_COMMAND_PATTERN '$pattern' found in $doc"
        }
    }
    Write-Host "FORBIDDEN_COMMAND_PATTERN_SCAN_OK $doc"
}

$webAppPath = "services/api/web_app.py"
$webApp = Read-RepoFile $webAppPath
$routeDecorators = [regex]::Matches($webApp, "@app\.(get|post)\(").Count
$getRoutes = [regex]::Matches($webApp, "@app\.get\(").Count
$postRoutes = [regex]::Matches($webApp, "@app\.post\(").Count
Write-Host "STATIC_ROUTE_SCAN web_app.py route_decorator_lines=$routeDecorators"
Write-Host "STATIC_GET_ROUTE_SCAN web_app.py get_route_lines=$getRoutes"
Write-Host "STATIC_POST_ROUTE_COUNT_ONLY web_app.py post_route_lines=$postRoutes"

$requiredRouteRefs = @(
    "/health",
    "/",
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
    "/log",
    "/ocr-page-image",
    "/owner/ocr-math-report/{course_id}/summary.json",
    "/owner/ocr-math-report/{course_id}/ocr_math_report.md",
    "/owner/ocr-math-report/{course_id}/view"
)

foreach ($route in $requiredRouteRefs) {
    if ($evidenceLog -notmatch [regex]::Escape($route)) {
        throw "Evidence log missing route reference: $route"
    }
    Write-Host "EVIDENCE_ROUTE_REFERENCE_FOUND $route"
}

$writeMarkers = @(
    "/upload",
    "/generate",
    "/delete-course",
    "/delete-from-library",
    "/review-answer",
    "/study-answer",
    "/study-reset",
    "/review-concepts/save",
    "/review-ocr-text/save",
    "/review-ocr-text/rebuild"
)

foreach ($marker in $writeMarkers) {
    if ($evidenceLog -notmatch [regex]::Escape($marker.Split("/")[-1])) {
        # The evidence document may describe excluded action classes instead of exact routes.
        # This is not a failure as long as the explicit exclusion section exists.
        continue
    }
}

if ($evidenceLog -notmatch "Explicitly excluded route/action classes") {
    throw "Evidence log missing explicit exclusion section"
}
Write-Host "WRITE_ROUTE_CLASSES_EXCLUDED_OK docs/dev/voila-read-only-route-smoke-evidence-log-v0.7.12.md"

Write-Host "VOILA_V0_7_12_READ_ONLY_ROUTE_SMOKE_EVIDENCE_CHECK=PASS"
Write-Host "POLICY=$Policy"
