$ErrorActionPreference = "Stop"

$target = "services/api/web_app.py"
$doc = "docs/dev/fix-course-tools-ocr-math-report-lookup-bounded-owner-local-no-build-no-zip-no-delivery.md"
$evidenceRoot = "D:\dev\tester-runs\voila-v0.7.56-fix-course-tools-ocr-math-report-lookup-bounded-owner-local-no-build-no-zip-no-delivery"

$httpEvidence = Join-Path $evidenceRoot "V0.7.56-BOUNDED-OCR-MATH-LOOKUP-HTTP-EVIDENCE.json"
$directLookup = Join-Path $evidenceRoot "V0.7.56-DIRECT-OCR-MATH-LOOKUP-RESULT.json"
$sourceEvidence = Join-Path $evidenceRoot "V0.7.56-SOURCE-BOUNDED-LOOKUP-EVIDENCE.json"

foreach ($path in @($target, $doc, $httpEvidence, $directLookup, $sourceEvidence)) {
  if (!(Test-Path $path)) {
    throw "Missing required v0.7.56 path: $path"
  }
}

python -m py_compile $target

$text = Get-Content $target -Raw
if ($text -like '*root.rglob("ocr_math_report.md")*') {
  throw "Unbounded OCR Math root.rglob block still present"
}
if ($text -notlike '*v0.7.56: bounded owner-local lookup only*') {
  throw "Missing v0.7.56 bounded lookup marker"
}
if ($text -notlike '*Missing OCR Math reports must return quickly as unavailable*') {
  throw "Missing missing-report-fast note"
}

$docText = Get-Content $doc -Raw
$requiredDocText = @(
  "VOILA_V0_7_56_FIX_COURSE_TOOLS_OCR_MATH_REPORT_LOOKUP_BOUNDED_CHECK=PASS",
  "COURSE TOOLS HANG FIXED",
  "RESIDUAL RAW JS BLOCKER REMAINS",
  "root.rglob(`"ocr_math_report.md`")",
  "Instrumente curs",
  "OCR Math card is shown as unavailable",
  "Raw JavaScript is still visible",
  "DO NOT package for testers",
  "DO NOT create ZIP",
  "DO NOT share",
  "DO NOT deliver",
  "No raw JavaScript fix",
  "No build",
  "No ZIP",
  "No share",
  "No delivery",
  "No distribution"
)

foreach ($item in $requiredDocText) {
  if ($docText -notlike "*$item*") {
    throw "Doc missing expected v0.7.56 text: $item"
  }
}

$http = Get-Content $httpEvidence -Raw | ConvertFrom-Json
$courseTools = $http | Where-Object { $_.url -like "*/course-tools?pdf=*" } | Select-Object -First 1
$ocrView = $http | Where-Object { $_.url -like "*/owner/ocr-math-report/*/view" } | Select-Object -First 1
$quickTools = $http | Where-Object { $_.url -eq "http://127.0.0.1:8787/quick-tools" } | Select-Object -First 1

if ($null -eq $courseTools -or [int]$courseTools.status -ne 200) {
  throw "Expected course-tools HTTP 200"
}
if ([int]$courseTools.elapsed_ms -ge 10000) {
  throw "Expected course-tools to return under 10 seconds"
}
if ($courseTools.has_course_tools -ne $true) {
  throw "Expected course-tools content marker"
}

if ($null -eq $ocrView -or [int]$ocrView.status -ne 404) {
  throw "Expected OCR Math missing report view HTTP 404"
}
if ([int]$ocrView.elapsed_ms -ge 10000) {
  throw "Expected OCR Math missing report view to return under 10 seconds"
}

if ($null -eq $quickTools -or [int]$quickTools.status -ne 200) {
  throw "Expected quick-tools HTTP 200"
}

$direct = Get-Content $directLookup -Raw | ConvertFrom-Json
if ($direct.expected_missing_fast -ne $true) {
  throw "Expected direct OCR Math lookup to report expected_missing_fast=true"
}
if ([int]$direct.elapsed_ms -ge 1000) {
  throw "Expected direct OCR Math lookup under 1000 ms"
}
if ($null -ne $direct.md) {
  throw "Expected direct OCR Math lookup md=null for tested missing report"
}

$source = Get-Content $sourceEvidence -Raw | ConvertFrom-Json
if ($source.has_removed_rglob_block -ne $true) {
  throw "Expected source evidence removed rglob block"
}
if ($source.has_v0756_marker -ne $true) {
  throw "Expected source evidence v0.7.56 marker"
}
if ($source.has_missing_fast_note -ne $true) {
  throw "Expected source evidence missing-fast note"
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/web_app.py",
  "docs/dev/fix-course-tools-ocr-math-report-lookup-bounded-owner-local-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-fix-course-tools-ocr-math-report-lookup-bounded-owner-local-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) {
    continue
  }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.56 fix: $line"
  }
}

"VOILA_V0_7_56_FIX_COURSE_TOOLS_OCR_MATH_REPORT_LOOKUP_BOUNDED_CHECK=PASS"
"FIXED=course_tools_ocr_math_report_lookup_bounded_missing_report_returns_fast"
"KNOWN_RESIDUAL_BLOCKER=raw_javascript_visible_bottom_nav"
"POLICY=no_build_no_zip_no_share_no_delivery_no_distribution"
