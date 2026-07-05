param(
    [string]$RepoRoot = "."
)

$ErrorActionPreference = "Stop"

$Milestone = "v0.7.11-owner-local-read-only-route-smoke-doc-no-build-no-distribution"

Write-Host "VOILA_V0_7_11_READ_ONLY_ROUTE_SMOKE_DOC_CHECK=START"
Write-Host "RepoRoot=$RepoRoot"
Write-Host "Milestone=$Milestone"

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
    "scripts/dev/check-voila-read-only-route-smoke-doc-v0.7.11.ps1"
)

foreach ($file in $requiredFiles) {
    $path = Join-Path $RepoRoot $file
    if (-not (Test-Path $path)) {
        throw "MISSING_REQUIRED_FILE $file"
    }
    Write-Host "FOUND $file"
}

$v0711Docs = @(
    "docs/dev/voila-read-only-route-smoke-runbook-v0.7.11.md",
    "docs/dev/voila-read-only-route-smoke-map-v0.7.11.md",
    "docs/dev/voila-read-only-route-smoke-evidence-template-v0.7.11.md",
    "docs/dev/voila-read-only-route-smoke-policy-v0.7.11.md"
)

$requiredTerms = @(
    "v0.7.11-owner-local-read-only-route-smoke-doc-no-build-no-distribution",
    "no build",
    "no ZIP",
    "no delivery",
    "no distribution",
    "owner-local only",
    "no behavior changes",
    "no feature changes",
    "no public UI expansion",
    "read-only",
    "GET-only"
)

foreach ($doc in $v0711Docs) {
    $path = Join-Path $RepoRoot $doc
    $content = Get-Content -Raw -Path $path
    foreach ($term in $requiredTerms) {
        if ($content -notmatch [regex]::Escape($term)) {
            throw "MISSING_TERM '$term' in $doc"
        }
    }
    Write-Host "POLICY_TERMS_OK $doc"
}

$evidencePath = Join-Path $RepoRoot "docs/dev/voila-read-only-route-smoke-evidence-template-v0.7.11.md"
$evidenceContent = Get-Content -Raw -Path $evidencePath
$requiredEvidenceTerms = @(
    "PENDING_MANUAL",
    "PASS",
    "EXPECTED_EMPTY",
    "EXPECTED_404",
    "SKIPPED_NO_SAMPLE",
    "SKIPPED_WRITE",
    "SKIPPED_DESTRUCTIVE",
    "BLOCKED"
)

foreach ($term in $requiredEvidenceTerms) {
    if ($evidenceContent -notmatch [regex]::Escape($term)) {
        throw "MISSING_EVIDENCE_TERM '$term'"
    }
}
Write-Host "EVIDENCE_VOCABULARY_OK docs/dev/voila-read-only-route-smoke-evidence-template-v0.7.11.md"

$scanFiles = $v0711Docs
$forbiddenPatterns = @(
    "npm\s+run\s+build",
    "pyinstaller",
    "Compress-Archive",
    "gh\s+release",
    "Invoke-RestMethod\s+.*-Method\s+Post",
    "Invoke-WebRequest\s+.*-Method\s+Post",
    "curl(\.exe)?\s+.*-X\s+POST",
    "Start-Process\s+.*OneDrive",
    "Remove-Item\s+.*data",
    "Remove-Item\s+.*courses",
    "git\s+tag",
    "git\s+push\s+.*--tags"
)

foreach ($scanFile in $scanFiles) {
    $path = Join-Path $RepoRoot $scanFile
    $content = Get-Content -Raw -Path $path
    foreach ($pattern in $forbiddenPatterns) {
        if ($content -match $pattern) {
            throw "FORBIDDEN_PATTERN '$pattern' found in $scanFile"
        }
    }
    Write-Host "FORBIDDEN_PATTERN_SCAN_OK $scanFile"
}

$webApp = Join-Path $RepoRoot "services/api/web_app.py"
if (-not (Test-Path $webApp)) {
    throw "MISSING_SOURCE services/api/web_app.py"
}

$routeDecorators = Select-String -Path $webApp -Pattern '@app\.(get|post)\('
$getDecorators = Select-String -Path $webApp -Pattern '@app\.get\('
$postDecorators = Select-String -Path $webApp -Pattern '@app\.post\('

Write-Host ("STATIC_ROUTE_SCAN web_app.py route_decorator_lines={0}" -f $routeDecorators.Count)
Write-Host ("STATIC_GET_ROUTE_SCAN web_app.py get_route_lines={0}" -f $getDecorators.Count)
Write-Host ("STATIC_POST_ROUTE_COUNT_ONLY web_app.py post_route_lines={0}" -f $postDecorators.Count)

$requiredRoutePatterns = @(
    '@app.get("/health"',
    '@app.get("/",',
    '@app.get("/quick-tools"',
    '@app.get("/course-tools"',
    '@app.get("/view-course"',
    '@app.get("/view-figures"',
    '@app.get("/review"',
    '@app.get("/review-concepts"',
    '@app.get("/review-ocr-text"',
    '@app.get("/review-ocr-corrected"',
    '@app.get("/edit-crops"',
    '@app.get("/progress"',
    '@app.get("/study"',
    '@app.get("/exam-prep"',
    '@app.get("/log"',
    '@app.get("/ocr-page-image"',
    '@app.get("/owner/ocr-math-report/{course_id}/summary.json"',
    '@app.get("/owner/ocr-math-report/{course_id}/ocr_math_report.md"',
    '@app.get("/owner/ocr-math-report/{course_id}/view"'
)

foreach ($pattern in $requiredRoutePatterns) {
    $matches = Select-String -Path $webApp -SimpleMatch $pattern
    if (-not $matches) {
        throw "MISSING_ROUTE_REFERENCE $pattern"
    }
    Write-Host "ROUTE_REFERENCE_FOUND $pattern"
}

$routeMapPath = Join-Path $RepoRoot "docs/dev/voila-read-only-route-smoke-map-v0.7.11.md"
$routeMap = Get-Content -Raw -Path $routeMapPath
$requiredMapRoutes = @(
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

foreach ($route in $requiredMapRoutes) {
    if ($routeMap -notmatch [regex]::Escape($route)) {
        throw "MISSING_ROUTE_IN_MAP $route"
    }
}
Write-Host "ROUTE_MAP_REFERENCES_OK docs/dev/voila-read-only-route-smoke-map-v0.7.11.md"

Write-Host "VOILA_V0_7_11_READ_ONLY_ROUTE_SMOKE_DOC_CHECK=PASS"
Write-Host "POLICY=no_build_no_zip_no_delivery_no_distribution_owner_local_only_no_behavior_changes_read_only_get_only"
