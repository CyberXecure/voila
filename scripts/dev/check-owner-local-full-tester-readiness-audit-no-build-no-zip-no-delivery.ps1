$ErrorActionPreference = "Stop"

$doc = "docs/dev/owner-local-full-tester-readiness-audit-no-build-no-zip-no-delivery.md"
$evidenceRoot = "D:\dev\tester-runs\voila-v0.7.54-owner-local-full-tester-readiness-audit-no-build-no-zip-no-delivery"
$routeEvidence = Join-Path $evidenceRoot "V0.7.54-ROUTE-EVIDENCE.json"
$rawJsSnippet = Join-Path $evidenceRoot "V0.7.54-QUICK-TOOLS-RAW-JS-SNIPPET.txt"

foreach ($path in @($doc, $routeEvidence, $rawJsSnippet)) {
  if (!(Test-Path $path)) {
    throw "Missing required v0.7.54 audit evidence path: $path"
  }
}

$docText = Get-Content $doc -Raw
$routeText = Get-Content $routeEvidence -Raw
$snippetText = Get-Content $rawJsSnippet -Raw

$requiredDocText = @(
  "VOILA_V0_7_54_OWNER_LOCAL_FULL_TESTER_READINESS_AUDIT_BLOCKED_NO_BUILD_NO_ZIP_NO_DELIVERY=FAIL",
  "Status: BLOCKED / FAIL EVIDENCE",
  "Course Tools does not respond",
  "raw JavaScript is visible in Quick Tools",
  "DO NOT package for testers",
  "DO NOT create ZIP",
  "DO NOT share",
  "DO NOT deliver",
  "No product fix",
  "No build",
  "No ZIP",
  "No share",
  "No delivery",
  "No distribution"
)

foreach ($item in $requiredDocText) {
  if ($docText -notlike "*$item*") {
    throw "Doc missing expected v0.7.54 text: $item"
  }
}

$routeEvidenceJson = $routeText | ConvertFrom-Json

$courseTools = $routeEvidenceJson | Where-Object { $_.url -like "*/course-tools?pdf=*" } | Select-Object -First 1
if ($null -eq $courseTools) {
  throw "Route evidence missing course-tools URL"
}
if ([string]$courseTools.status -ne "ERROR") {
  throw "Expected course-tools route evidence to be ERROR"
}
if ([string]$courseTools.error -notlike "*Timeout*") {
  throw "Expected course-tools route evidence timeout"
}

$quickTools = $routeEvidenceJson | Where-Object { $_.url -eq "http://127.0.0.1:8787/quick-tools" } | Select-Object -First 1
if ($null -eq $quickTools) {
  throw "Route evidence missing /quick-tools URL"
}
if ([int]$quickTools.status -ne 200) {
  throw "Expected /quick-tools route status 200"
}

$requiredSnippetText = @(
  "voilaTesterFlowBottomNav",
  "document.createElement",
  "window.location.search",
  "addLink(nav",
  "function"
)

foreach ($item in $requiredSnippetText) {
  if ($snippetText -notlike "*$item*") {
    throw "Raw JS snippet missing expected marker: $item"
  }
}

$statusLines = git status --short -uall
$allowed = @(
  "docs/dev/owner-local-full-tester-readiness-audit-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-full-tester-readiness-audit-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) {
    continue
  }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.54 audit: $line"
  }
}

"VOILA_V0_7_54_OWNER_LOCAL_FULL_TESTER_READINESS_AUDIT_BLOCKED_NO_BUILD_NO_ZIP_NO_DELIVERY=FAIL"
"VOILA_V0_7_54_BLOCKED_EVIDENCE_CHECK=PASS"
"POLICY=audit_only_no_product_fix_no_build_no_zip_no_share_no_delivery_no_distribution"
