param(
    [Parameter(Mandatory=$false)]
    [string]$RepoRoot = "."
)

$ErrorActionPreference = "Stop"

$Milestone = "v0.7.10-owner-local-manual-smoke-evidence-no-build-no-distribution"

Write-Host "VOILA_V0_7_10_MANUAL_SMOKE_EVIDENCE_CHECK=START"
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
    "scripts/dev/check-voila-manual-smoke-evidence-v0.7.10.ps1"
)

foreach ($relativePath in $requiredFiles) {
    $path = Join-Path $RepoRoot $relativePath
    if (-not (Test-Path -LiteralPath $path)) {
        throw "MISSING_REQUIRED_FILE $relativePath"
    }
    Write-Host "FOUND $relativePath"
}

$v0710Docs = @(
    "docs/dev/voila-manual-smoke-runbook-v0.7.10.md",
    "docs/dev/voila-manual-smoke-evidence-v0.7.10.md",
    "docs/dev/voila-manual-smoke-risk-register-v0.7.10.md"
)

$requiredPhrases = @(
    "v0.7.10-owner-local-manual-smoke-evidence-no-build-no-distribution",
    "no build",
    "no ZIP",
    "no delivery",
    "no distribution",
    "owner-local only",
    "no feature changes",
    "no behavior changes",
    "no OCR/pages/course/Study/Progress rewrite",
    "no public UI expansion",
    "read-only",
    "SKIPPED_WRITE",
    "SKIPPED_DESTRUCTIVE"
)

foreach ($doc in $v0710Docs) {
    $content = Get-Content -LiteralPath (Join-Path $RepoRoot $doc) -Raw
    foreach ($phrase in $requiredPhrases) {
        if ($content -notlike "*$phrase*") {
            throw "MISSING_REQUIRED_PHRASE '$phrase' in $doc"
        }
    }
    Write-Host "POLICY_AND_EVIDENCE_TERMS_OK $doc"
}

$forbiddenPatterns = @(
    ("npm " + "run build"),
    ("npm " + "build"),
    ("py" + "installer"),
    ("gh " + "release"),
    ("Compress" + "-Archive"),
    ("7" + "z"),
    ("Start-Process.*" + "OneDrive"),
    ("release-assets.*" + "zip"),
    ("Invoke-WebRequest.*" + "upload"),
    ("curl.*" + "upload"),
    ("docker " + "build"),
    ("docker " + "compose"),
    ("docker" + "-compose")
)

$scanFiles = @(
    "docs/dev/voila-manual-smoke-runbook-v0.7.10.md",
    "docs/dev/voila-manual-smoke-evidence-v0.7.10.md",
    "docs/dev/voila-manual-smoke-risk-register-v0.7.10.md"
)

foreach ($scanFile in $scanFiles) {
    $content = Get-Content -LiteralPath (Join-Path $RepoRoot $scanFile) -Raw
    foreach ($pattern in $forbiddenPatterns) {
        if ($content -match $pattern) {
            throw "FORBIDDEN_PATTERN '$pattern' found in $scanFile"
        }
    }
    Write-Host "FORBIDDEN_PATTERN_SCAN_OK $scanFile"
}

$webAppPath = Join-Path $RepoRoot "services/api/web_app.py"
if (Test-Path -LiteralPath $webAppPath) {
    $routeLines = Select-String -LiteralPath $webAppPath -Pattern '@app\.(get|post|put|delete|patch)\('
    Write-Host ("STATIC_ROUTE_SCAN web_app.py route_decorator_lines={0}" -f $routeLines.Count)

    $importantRoutes = @(
        '"/health"',
        '"/"',
        '"/generate"',
        '"/upload"',
        '"/delete-course"',
        '"/delete-from-library"',
        '"/review"',
        '"/progress"',
        '"/study"',
        '"/edit-crops"',
        '"/review-concepts"',
        '"/review-ocr-text"',
        '"/course-tools"',
        '"/view-course"',
        '"/view-figures"',
        '"/quick-tools"',
        '"/owner/ocr-math-report/{course_id}/view"'
    )

    $webAppContent = Get-Content -LiteralPath $webAppPath -Raw
    foreach ($route in $importantRoutes) {
        if ($webAppContent -notlike "*$route*") {
            Write-Host "ROUTE_REFERENCE_NOT_FOUND_OR_CHANGED $route"
        } else {
            Write-Host "ROUTE_REFERENCE_FOUND $route"
        }
    }
} else {
    Write-Host "STATIC_ROUTE_SCAN_SKIPPED web_app.py not found"
}

Write-Host "VOILA_V0_7_10_MANUAL_SMOKE_EVIDENCE_CHECK=PASS"
Write-Host "POLICY=no_build_no_zip_no_delivery_no_distribution_owner_local_only_no_behavior_changes"

