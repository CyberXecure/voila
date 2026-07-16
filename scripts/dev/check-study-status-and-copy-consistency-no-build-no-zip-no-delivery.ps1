$ErrorActionPreference = "Stop"

Write-Host "v0.7.87 check: start"

$web = "services/api/web_app.py"
$doc = "docs/dev/study-status-and-copy-consistency-no-build-no-zip-no-delivery.md"

$evidenceDir = "D:\dev\tester-runs\v0787-study-status-and-copy-consistency"
$sourceInspect = "$evidenceDir\V0.7.87-STUDY-STATUS-COPY-CONSISTENCY-SOURCE-INSPECT.json"
$smoke = "$evidenceDir\V0.7.87-STUDY-STATUS-COPY-CONSISTENCY-SMOKE.json"

foreach ($p in @($web, $doc, $sourceInspect, $smoke)) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence: $p" }
}

python -m py_compile $web

$webText = Get-Content $web -Raw
foreach ($item in @(
  "VOILA_V0_7_87_STUDY_STATUS_COPY_CONSISTENCY_START",
  "VOILA_V0_7_87_STUDY_STATUS_COPY_CONSISTENCY_END",
  "VOILA_V0_7_87_QUICK_TOOLS_STUDY_STATUS_CONSISTENCY_START",
  "VOILA_V0_7_87_QUICK_TOOLS_STUDY_STATUS_CONSISTENCY_END",
  "_voila_v087_preview_quality_pass",
  "preview_quality_pass",
  "study_preview_pass",
  "Întrebări de studiu din study_items.preview.json când Quality gate este PASS, cu fallback la quiz.json / quiz.study.json.",
  "Dashboard de progres pentru întrebările de studiu disponibile în Study.",
  "Progress are nevoie de study_items.preview.json PASS sau quiz.json / quiz.study.json."
)) {
  if ($webText -notlike "*$item*") { throw "web_app.py missing expected v0.7.87 text: $item" }
}

foreach ($bad in @(
  "Întrebări de studiu din quiz.json / quiz.study.json.",
  "Progress are nevoie de quiz.json / quiz.study.json."
)) {
  if ($webText -like "*$bad*") { throw "web_app.py still contains stale copy: $bad" }
}

$sourceData = Get-Content $sourceInspect -Raw | ConvertFrom-Json
if ($sourceData.VOILA_V0_7_87_STUDY_STATUS_COPY_CONSISTENCY_SOURCE_INSPECT -ne "PASS") { throw "Source inspect marker mismatch" }
if ($sourceData.BUILD_PERFORMED -ne $false) { throw "Source inspect BUILD_PERFORMED mismatch" }
if ($sourceData.ZIP_CREATED -ne $false) { throw "Source inspect ZIP_CREATED mismatch" }
if ($sourceData.SHARE_CREATED -ne $false) { throw "Source inspect SHARE_CREATED mismatch" }
if ($sourceData.DELIVERY_PERFORMED -ne $false) { throw "Source inspect DELIVERY_PERFORMED mismatch" }

$smokeData = Get-Content $smoke -Raw | ConvertFrom-Json
if ($smokeData.VOILA_V0_7_87_STUDY_STATUS_COPY_CONSISTENCY_SMOKE -ne "PASS") { throw "Smoke marker mismatch" }
if ($smokeData.course_tools_status -ne 200) { throw "course_tools_status mismatch" }
if ($smokeData.quick_tools_status -ne 200) { throw "quick_tools_status mismatch" }
if ($smokeData.study_status -ne 200) { throw "study_status mismatch" }
if ($smokeData.course_tools_study_copy_updated -ne $true) { throw "course_tools_study_copy_updated mismatch" }
if ($smokeData.course_tools_progress_copy_updated -ne $true) { throw "course_tools_progress_copy_updated mismatch" }
if ($smokeData.progress_missing_copy_updated_in_source -ne $true) { throw "progress_missing_copy_updated_in_source mismatch" }
if ($smokeData.quick_tools_study_status_ok -ne $true) { throw "quick_tools_study_status_ok mismatch" }
if ($smokeData.quick_tools_study_dash_visible -ne $false) { throw "quick_tools_study_dash_visible mismatch" }
if ($smokeData.study_preview_labels_visible -ne $true) { throw "study_preview_labels_visible mismatch" }
if ($smokeData.study_logic_changed -ne $false) { throw "study_logic_changed mismatch" }
if ($smokeData.bkt_logic_changed -ne $false) { throw "bkt_logic_changed mismatch" }
if ($smokeData.progress_logic_changed -ne $false) { throw "progress_logic_changed mismatch" }
if ($smokeData.generator_logic_changed -ne $false) { throw "generator_logic_changed mismatch" }
if ($smokeData.BUILD_PERFORMED -ne $false) { throw "Smoke BUILD_PERFORMED mismatch" }
if ($smokeData.ZIP_CREATED -ne $false) { throw "Smoke ZIP_CREATED mismatch" }
if ($smokeData.SHARE_CREATED -ne $false) { throw "Smoke SHARE_CREATED mismatch" }
if ($smokeData.DELIVERY_PERFORMED -ne $false) { throw "Smoke DELIVERY_PERFORMED mismatch" }

$docText = (Get-Content $doc -Raw).Replace('`','')
foreach ($item in @(
  "VOILA_V0_7_87_STUDY_STATUS_COPY_CONSISTENCY_CHECK=PASS",
  "PASS_STUDY_STATUS_COPY_CONSISTENCY",
  "VOILA_V0_7_87_STUDY_STATUS_COPY_CONSISTENCY_SOURCE_INSPECT=PASS",
  "VOILA_V0_7_87_STUDY_STATUS_COPY_CONSISTENCY_SMOKE=PASS",
  "course_tools_status=200",
  "quick_tools_status=200",
  "study_status=200",
  "course_tools_study_copy_updated=True",
  "course_tools_progress_copy_updated=True",
  "progress_missing_copy_updated_in_source=True",
  "quick_tools_study_status_ok=True",
  "quick_tools_study_dash_visible=False",
  "study_preview_labels_visible=True",
  "study_logic_changed=False",
  "bkt_logic_changed=False",
  "progress_logic_changed=False",
  "generator_logic_changed=False",
  "BUILD_PERFORMED=False",
  "ZIP_CREATED=False",
  "SHARE_CREATED=False",
  "DELIVERY_PERFORMED=False",
  "TESTER_READINESS=LOCAL_STUDY_STATUS_COPY_CONSISTENCY_PASS_NOT_PACKAGED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/web_app.py",
  "docs/dev/study-status-and-copy-consistency-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-study-status-and-copy-consistency-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_87_STUDY_STATUS_COPY_CONSISTENCY_CHECK=PASS"
"COURSE_TOOLS_STATUS=200"
"QUICK_TOOLS_STATUS=200"
"STUDY_STATUS=200"
"COURSE_TOOLS_STUDY_COPY_UPDATED=True"
"COURSE_TOOLS_PROGRESS_COPY_UPDATED=True"
"PROGRESS_MISSING_COPY_UPDATED_IN_SOURCE=True"
"QUICK_TOOLS_STUDY_STATUS_OK=True"
"STUDY_PREVIEW_LABELS_VISIBLE=True"
"STUDY_LOGIC_CHANGED=False"
"BKT_LOGIC_CHANGED=False"
"PROGRESS_LOGIC_CHANGED=False"
"GENERATOR_LOGIC_CHANGED=False"
"BUILD_PERFORMED=False"
"ZIP_CREATED=False"
"SHARE_CREATED=False"
"DELIVERY_PERFORMED=False"
"TESTER_READINESS=LOCAL_STUDY_STATUS_COPY_CONSISTENCY_PASS_NOT_PACKAGED"
"POLICY=study_status_copy_consistency_no_build_no_zip_no_share_no_delivery_no_distribution"
