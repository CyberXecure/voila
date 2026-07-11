$ErrorActionPreference = "Stop"

$doc = "docs/dev/course-tools-quick-tools-root-cause-investigation-no-fix-no-build-no-zip-no-delivery.md"
$evidenceRoot = "D:\dev\tester-runs\voila-v0.7.55-course-tools-quick-tools-root-cause-investigation-no-fix-no-build-no-zip-no-delivery"

$requiredEvidence = @(
  "V0.7.55-SOURCE-HITS.json",
  "V0.7.55-QUICK-TOOLS.html",
  "V0.7.55-QUICK-TOOLS-SCRIPT-BOUNDARY-AROUND-MARKER.txt",
  "V0.7.55-COURSE-TOOLS-TIMEOUT-DETAIL.json",
  "V0.7.55-DIRECT-V2-ROUTE-CALL-RESULTS.json",
  "V0.7.55-DIRECT-V2-course_tools-TRACE.txt",
  "V0.7.55-WEBAPP-ocr-math-report-paths-130-190.txt",
  "V0.7.55-WEBAPP-ocr-math-candidate-roots-90-142.txt",
  "V0.7.55-OCR-MATH-CANDIDATE-ROOTS-INVENTORY.json",
  "V0.7.55-CURRENT-PDF-OCR-MATH-FILES.json",
  "V0.7.55-EXISTING-OCR-MATH-REPORTS-UNDER-DATA.json"
)

if (!(Test-Path $doc)) {
  throw "Missing v0.7.55 doc: $doc"
}

foreach ($name in $requiredEvidence) {
  $path = Join-Path $evidenceRoot $name
  if (!(Test-Path $path)) {
    throw "Missing v0.7.55 evidence file: $path"
  }
}

$docText = Get-Content $doc -Raw

$requiredDocText = @(
  "VOILA_V0_7_55_COURSE_TOOLS_QUICK_TOOLS_ROOT_CAUSE_INVESTIGATION_NO_FIX_CHECK=PASS",
  "ROOT-CAUSE INVESTIGATION ONLY / NO FIX",
  "course_tools()",
  "_voila_ocr_math_report_paths(pdf_path.stem)",
  "root.rglob(`"ocr_math_report.md`")",
  "D:\dev\projects",
  "D:\dev",
  "D:\",
  "data\trash\courses",
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
    throw "Doc missing expected v0.7.55 text: $item"
  }
}

$direct = Get-Content (Join-Path $evidenceRoot "V0.7.55-DIRECT-V2-ROUTE-CALL-RESULTS.json") -Raw | ConvertFrom-Json
$quick = $direct | Where-Object { $_.name -eq "quick_tools" } | Select-Object -First 1
$course = $direct | Where-Object { $_.name -eq "course_tools" } | Select-Object -First 1

if ($null -eq $quick -or $quick.status -ne "returned") {
  throw "Expected quick_tools direct call to return"
}

if ($null -eq $course -or $course.status -ne "timeout_terminated") {
  throw "Expected course_tools direct call to timeout_terminated"
}

$traceText = Get-Content (Join-Path $evidenceRoot "V0.7.55-DIRECT-V2-course_tools-TRACE.txt") -Raw
foreach ($item in @("_voila_ocr_math_report_paths", "course_tools")) {
  if ($traceText -notlike "*$item*") {
    throw "Course tools trace missing expected item: $item"
  }
}

if (($traceText -notlike "*rglob*") -and ($traceText -notlike "*pathlib.py*")) {
  throw "Course tools trace missing expected recursive pathlib/rglob evidence"
}

$roots = Get-Content (Join-Path $evidenceRoot "V0.7.55-OCR-MATH-CANDIDATE-ROOTS-INVENTORY.json") -Raw | ConvertFrom-Json
foreach ($root in @("D:\dev\projects", "D:\dev", "D:\")) {
  $hit = $roots | Where-Object { $_.root -eq $root -and $_.is_above_repo -eq $true } | Select-Object -First 1
  if ($null -eq $hit) {
    throw "Candidate roots inventory missing above-repo root: $root"
  }
}

$currentPdf = Get-Content (Join-Path $evidenceRoot "V0.7.55-CURRENT-PDF-OCR-MATH-FILES.json") -Raw | ConvertFrom-Json
foreach ($row in $currentPdf) {
  if ($row.exists -ne $false) {
    throw "Expected current PDF OCR Math file to be absent: $($row.path)"
  }
}

$trashReports = Get-Content (Join-Path $evidenceRoot "V0.7.55-EXISTING-OCR-MATH-REPORTS-UNDER-DATA.json") -Raw
if ($trashReports -notlike "*data\\trash\\courses*") {
  throw "Expected existing OCR Math reports under data\trash\courses"
}

$statusLines = git status --short -uall
$allowed = @(
  "docs/dev/course-tools-quick-tools-root-cause-investigation-no-fix-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-course-tools-quick-tools-root-cause-investigation-no-fix-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) {
    continue
  }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.55 investigation: $line"
  }
}

"VOILA_V0_7_55_COURSE_TOOLS_QUICK_TOOLS_ROOT_CAUSE_INVESTIGATION_NO_FIX_CHECK=PASS"
"ROOT_CAUSE=course_tools_ocr_math_report_lookup_unbounded_rglob_candidate_roots_too_broad"
"POLICY=investigation_only_no_product_fix_no_build_no_zip_no_share_no_delivery_no_distribution"
