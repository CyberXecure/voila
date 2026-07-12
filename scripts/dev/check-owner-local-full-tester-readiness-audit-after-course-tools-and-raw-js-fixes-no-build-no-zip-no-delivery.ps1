$ErrorActionPreference = "Stop"

$doc = "docs/dev/owner-local-full-tester-readiness-audit-after-course-tools-and-raw-js-fixes-no-build-no-zip-no-delivery.md"
$evidenceRoot = "D:\dev\tester-runs\voila-v0.7.58-owner-local-full-tester-readiness-audit-after-course-tools-and-raw-js-fixes-no-build-no-zip-no-delivery"

$requiredEvidence = @(
  "V0.7.58-REPO-BASELINE.json",
  "V0.7.58-PDF-OUTPUT-INVENTORY.json",
  "V0.7.58-OCR-MATH-REPORT-INVENTORY.json",
  "V0.7.58-INVENTORY-SUMMARY.json",
  "V0.7.58-ACTIVE-COURSE-ROUTE-SMOKE.json",
  "V0.7.58-CONTENT-MARKERS-SMOKE.json",
  "V0.7.58-CONTENT-DETAIL-INSPECTION.json",
  "V0.7.58-COURSE-TOOLS-LINK-INVENTORY.json",
  "V0.7.58-CLICK-TARGET-SMOKE.json",
  "V0.7.58-ACTIVE-COURSE-ARTIFACT-CONTENT-AUDIT.json",
  "V0.7.58-ACTIVE-COURSE-ARTIFACT-PRECISE-COUNTS.json",
  "V0.7.58-STUDY-PROGRESS-EXAM-CONTENT-DETAIL.json"
)

if (!(Test-Path $doc)) {
  throw "Missing v0.7.58 audit doc: $doc"
}

foreach ($name in $requiredEvidence) {
  $path = Join-Path $evidenceRoot $name
  if (!(Test-Path $path)) {
    throw "Missing required v0.7.58 evidence: $path"
  }
}

$summary = Get-Content (Join-Path $evidenceRoot "V0.7.58-INVENTORY-SUMMARY.json") -Raw | ConvertFrom-Json
if ([int]$summary.output_dir_count -ne 1) {
  throw "Expected exactly one active generated output dir in this audit"
}
if ([int]$summary.active_ocr_math_md_count -ne 0) {
  throw "Expected zero active OCR Math markdown reports in this audit"
}
if ([int]$summary.active_ocr_math_json_count -ne 0) {
  throw "Expected zero active OCR Math JSON reports in this audit"
}
if ([int]$summary.active_report_file_count -ne 0) {
  throw "Expected zero active OCR Math report files outside trash"
}

$route = Get-Content (Join-Path $evidenceRoot "V0.7.58-ACTIVE-COURSE-ROUTE-SMOKE.json") -Raw | ConvertFrom-Json
if (@($route | Where-Object { $_.expected_ok -ne $true }).Count -ne 0) {
  throw "Route smoke had unexpected status results"
}
if (@($route | Where-Object { $_.has_traceback -eq $true }).Count -ne 0) {
  throw "Route smoke found traceback"
}
if (@($route | Where-Object { $_.has_raw_js_visual_risk -eq $true }).Count -ne 0) {
  throw "Route smoke found raw JS visual risk"
}

$click = Get-Content (Join-Path $evidenceRoot "V0.7.58-CLICK-TARGET-SMOKE.json") -Raw | ConvertFrom-Json
if (@($click | Where-Object { $_.expected_ok -ne $true }).Count -ne 0) {
  throw "Click target smoke had unexpected status results"
}
if (@($click | Where-Object { $_.has_traceback -eq $true }).Count -ne 0) {
  throw "Click target smoke found traceback"
}
if (@($click | Where-Object { $_.has_raw_js_visual_risk -eq $true }).Count -ne 0) {
  throw "Click target smoke found raw JS visual risk"
}

$links = Get-Content (Join-Path $evidenceRoot "V0.7.58-COURSE-TOOLS-LINK-INVENTORY.json") -Raw | ConvertFrom-Json
if ($links.course_tools_expected_links_ok -ne $true) {
  throw "Expected Course Tools links to be present"
}

$precise = Get-Content (Join-Path $evidenceRoot "V0.7.58-ACTIVE-COURSE-ARTIFACT-PRECISE-COUNTS.json") -Raw | ConvertFrom-Json
if ($precise.tester_quality_flags.quiz_too_thin -ne $true) {
  throw "Expected quiz_too_thin=true blocker"
}
if ($precise.tester_quality_flags.flashcards_empty -ne $true) {
  throw "Expected flashcards_empty=true blocker"
}
if ($precise.tester_quality_flags.glossary_empty -ne $true) {
  throw "Expected glossary_empty=true blocker"
}

$docText = Get-Content $doc -Raw
$requiredDocText = @(
  'VOILA_V0_7_58_OWNER_LOCAL_FULL_TESTER_READINESS_AUDIT_AFTER_FIXES_CHECK=FAIL_BLOCKED',
  'Status: BLOCKED / NOT TESTER READY',
  'ROUTE_SMOKE_ALL_EXPECTED_OK=True',
  'CLICK_TARGETS_ALL_EXPECTED_OK=True',
  'quiz_too_thin=true',
  'flashcards_empty=true',
  'glossary_empty=true',
  'No active OCR Math report exists in',
  'data\output',
  'Tester package is BLOCKED',
  'DO NOT package for testers',
  'DO NOT create ZIP',
  'DO NOT share',
  'DO NOT deliver',
  'No product patch',
  'No build',
  'No ZIP',
  'No share',
  'No delivery',
  'No distribution'
)

foreach ($item in $requiredDocText) {
  if ($docText -notlike "*$item*") {
    throw "Doc missing expected v0.7.58 text: $item"
  }
}

$statusLines = git status --short -uall
$allowed = @(
  "docs/dev/owner-local-full-tester-readiness-audit-after-course-tools-and-raw-js-fixes-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-full-tester-readiness-audit-after-course-tools-and-raw-js-fixes-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) {
    continue
  }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.58 audit: $line"
  }
}

"VOILA_V0_7_58_OWNER_LOCAL_FULL_TESTER_READINESS_AUDIT_AFTER_FIXES_CHECK=FAIL_BLOCKED"
"TECHNICAL_NAVIGATION_AFTER_V0756_V0757=PASS"
"TESTER_READINESS=BLOCKED"
"BLOCKERS=quiz_too_thin_flashcards_empty_glossary_empty_no_active_ocr_math_available_state"
"POLICY=audit_only_no_product_patch_no_build_no_zip_no_share_no_delivery_no_distribution"
