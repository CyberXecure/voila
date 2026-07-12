$ErrorActionPreference = "Stop"

$target = "services/api/web_app.py"
$doc = "docs/dev/fix-visible-raw-bottom-nav-javascript-owner-local-no-build-no-zip-no-delivery.md"
$evidenceRoot = "D:\dev\tester-runs\voila-v0.7.57-fix-visible-raw-bottom-nav-javascript-owner-local-no-build-no-zip-no-delivery"

$sourceHits = Join-Path $evidenceRoot "V0.7.57-BOTTOM-NAV-SOURCE-HITS.json"
$htmlBefore = Join-Path $evidenceRoot "V0.7.57-BOTTOM-NAV-HTML-BEFORE-EVIDENCE.json"
$htmlAfter = Join-Path $evidenceRoot "V0.7.57-BOTTOM-NAV-HTML-AFTER-EVIDENCE.json"

foreach ($path in @($target, $doc, $sourceHits, $htmlBefore, $htmlAfter)) {
  if (!(Test-Path $path)) {
    throw "Missing required v0.7.57 path: $path"
  }
}

python -m py_compile $target

$text = Get-Content $target -Raw

$forbiddenCssSelectors = @(
  "'.voila-tester-flow-bottom-nav-v0724,'",
  "'#voila-tester-flow-bottom-nav-v0724 {'",
  "'.voila-tester-flow-bottom-nav-v0724 a,'",
  "'#voila-tester-flow-bottom-nav-v0724 a {'"
)

foreach ($selector in $forbiddenCssSelectors) {
  if ($text -like "*$selector*") {
    throw "Forbidden v0.7.57 CSS selector still targets script marker: $selector"
  }
}

$requiredSourceText = @(
  "# v0.7.57: target the injected nav element, not the script tag marker.",
  "'.voila-tester-flow-bottom-nav,'",
  "'#voilaTesterFlowBottomNav {'",
  "'.voila-tester-flow-bottom-nav a,'",
  "'#voilaTesterFlowBottomNav a {'",
  '<script id="voila-tester-flow-bottom-nav-v0724">',
  'nav.id = "voilaTesterFlowBottomNav";'
)

foreach ($item in $requiredSourceText) {
  if ($text -notlike "*$item*") {
    throw "Missing expected v0.7.57 source text: $item"
  }
}

$docText = Get-Content $doc -Raw
$requiredDocText = @(
  "VOILA_V0_7_57_FIX_VISIBLE_RAW_BOTTOM_NAV_JAVASCRIPT_CHECK=PASS",
  "RAW JAVASCRIPT TEXT FIXED",
  "Root cause",
  "#voila-tester-flow-bottom-nav-v0724",
  "#voilaTesterFlowBottomNav",
  "css_targets_script_marker",
  "has_raw_js_visual_risk",
  "raw JavaScript text is no longer visible",
  "Possible visual polish follow-up",
  "DO NOT package for testers",
  "DO NOT create ZIP",
  "DO NOT share",
  "DO NOT deliver",
  "No OCR Math lookup change",
  "No build",
  "No ZIP",
  "No share",
  "No delivery",
  "No distribution"
)

foreach ($item in $requiredDocText) {
  if ($docText -notlike "*$item*") {
    throw "Doc missing expected v0.7.57 text: $item"
  }
}

$after = Get-Content $htmlAfter -Raw | ConvertFrom-Json
$courseTools = $after | Where-Object { $_.page -eq "course-tools" } | Select-Object -First 1
$quickTools = $after | Where-Object { $_.page -eq "quick-tools" } | Select-Object -First 1

foreach ($row in @($courseTools, $quickTools)) {
  if ($null -eq $row) {
    throw "Missing after HTML evidence row"
  }
  if ([int]$row.status -ne 200) {
    throw "Expected after HTML HTTP 200 for $($row.page)"
  }
  if ($row.has_script_id -ne $true) {
    throw "Expected script id marker to remain present for $($row.page)"
  }
  if ($row.css_targets_script_marker -ne $false) {
    throw "Expected CSS not to target script marker for $($row.page)"
  }
  if ($row.css_targets_nav_id -ne $true) {
    throw "Expected CSS to target injected nav id for $($row.page)"
  }
  if ($row.css_targets_nav_class -ne $true) {
    throw "Expected CSS to target injected nav class for $($row.page)"
  }
  if ($row.has_raw_js_visual_risk -ne $false) {
    throw "Expected raw JS visual risk false for $($row.page)"
  }
  if ($row.has_traceback -ne $false) {
    throw "Expected no traceback for $($row.page)"
  }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/web_app.py",
  "docs/dev/fix-visible-raw-bottom-nav-javascript-owner-local-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-fix-visible-raw-bottom-nav-javascript-owner-local-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) {
    continue
  }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.57 fix: $line"
  }
}

"VOILA_V0_7_57_FIX_VISIBLE_RAW_BOTTOM_NAV_JAVASCRIPT_CHECK=PASS"
"FIXED=visible_raw_bottom_navigation_javascript_text"
"KNOWN_FOLLOW_UP=possible_empty_bottom_left_outline_visual_polish_if_still_visible"
"POLICY=no_build_no_zip_no_share_no_delivery_no_distribution"
