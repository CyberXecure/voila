$ErrorActionPreference = "Stop"

Write-Host "v0.7.86 check: start"

$web = "services/api/web_app.py"
$doc = "docs/dev/study-items-preview-status-copy-polish-no-build-no-zip-no-delivery.md"

$evidenceDir = "D:\dev\tester-runs\v0786-study-items-preview-status-copy-polish"
$sourceInspect = "$evidenceDir\V0.7.86-STUDY-ITEMS-PREVIEW-STATUS-COPY-SOURCE-INSPECT.json"
$smoke = "$evidenceDir\V0.7.86-STUDY-ITEMS-PREVIEW-STATUS-COPY-POLISH-SMOKE.json"

foreach ($p in @($web, $doc, $sourceInspect, $smoke)) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence: $p" }
}

python -m py_compile $web

$webText = Get-Content $web -Raw
foreach ($item in @(
  "VOILA_V0_7_86_STUDY_ITEMS_PREVIEW_STATUS_COPY_POLISH_START",
  "VOILA_V0_7_86_STUDY_ITEMS_PREVIEW_STATUS_COPY_POLISH_END",
  "integrat în Study când Quality gate este PASS",
  "Study integration:",
  "study_integration_badge",
  "Study folosește artifactul când Quality gate este PASS",
  "nu modifică BKT sau Progress"
)) {
  if ($webText -notlike "*$item*") { throw "web_app.py missing expected status copy polish text: $item" }
}

foreach ($bad in @(
  "preview only · nu este integrat încă în Study",
  "Preview only: nu modifică Study"
)) {
  if ($webText -like "*$bad*") { throw "web_app.py still contains stale copy: $bad" }
}

$sourceData = Get-Content $sourceInspect -Raw | ConvertFrom-Json
if ($sourceData.VOILA_V0_7_86_STUDY_ITEMS_PREVIEW_STATUS_COPY_SOURCE_INSPECT -ne "PASS") { throw "Source inspect marker mismatch" }
if ($sourceData.BUILD_PERFORMED -ne $false) { throw "Source inspect BUILD_PERFORMED mismatch" }
if ($sourceData.ZIP_CREATED -ne $false) { throw "Source inspect ZIP_CREATED mismatch" }
if ($sourceData.SHARE_CREATED -ne $false) { throw "Source inspect SHARE_CREATED mismatch" }
if ($sourceData.DELIVERY_PERFORMED -ne $false) { throw "Source inspect DELIVERY_PERFORMED mismatch" }

$smokeData = Get-Content $smoke -Raw | ConvertFrom-Json
if ($smokeData.VOILA_V0_7_86_STUDY_ITEMS_PREVIEW_STATUS_COPY_POLISH_SMOKE -ne "PASS") { throw "Smoke marker mismatch" }
if ($smokeData.viewer_status -ne 200) { throw "viewer_status mismatch" }
if ($smokeData.course_tools_status -ne 200) { throw "course_tools_status mismatch" }
if ($smokeData.status_copy_polished -ne $true) { throw "status_copy_polished mismatch" }
if ($smokeData.study_integration_badge_polished -ne $true) { throw "study_integration_badge_polished mismatch" }
if ($smokeData.course_tools_copy_polished -ne $true) { throw "course_tools_copy_polished mismatch" }
if ($smokeData.stale_preview_only_copy_visible -ne $false) { throw "stale_preview_only_copy_visible mismatch" }
if ($smokeData.stale_not_integrated_copy_visible -ne $false) { throw "stale_not_integrated_copy_visible mismatch" }
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
  "VOILA_V0_7_86_STUDY_ITEMS_PREVIEW_STATUS_COPY_POLISH_CHECK=PASS",
  "PASS_STUDY_ITEMS_PREVIEW_STATUS_COPY_POLISH",
  "VOILA_V0_7_86_STUDY_ITEMS_PREVIEW_STATUS_COPY_SOURCE_INSPECT=PASS",
  "VOILA_V0_7_86_STUDY_ITEMS_PREVIEW_STATUS_COPY_POLISH_SMOKE=PASS",
  "viewer_status=200",
  "course_tools_status=200",
  "status_copy_polished=True",
  "study_integration_badge_polished=True",
  "course_tools_copy_polished=True",
  "stale_preview_only_copy_visible=False",
  "stale_not_integrated_copy_visible=False",
  "study_logic_changed=False",
  "bkt_logic_changed=False",
  "progress_logic_changed=False",
  "generator_logic_changed=False",
  "BUILD_PERFORMED=False",
  "ZIP_CREATED=False",
  "SHARE_CREATED=False",
  "DELIVERY_PERFORMED=False",
  "TESTER_READINESS=LOCAL_STUDY_ITEMS_PREVIEW_STATUS_COPY_POLISH_PASS_NOT_PACKAGED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/web_app.py",
  "docs/dev/study-items-preview-status-copy-polish-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-study-items-preview-status-copy-polish-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_86_STUDY_ITEMS_PREVIEW_STATUS_COPY_POLISH_CHECK=PASS"
"VIEWER_STATUS=200"
"COURSE_TOOLS_STATUS=200"
"STATUS_COPY_POLISHED=True"
"STUDY_INTEGRATION_BADGE_POLISHED=True"
"COURSE_TOOLS_COPY_POLISHED=True"
"STALE_PREVIEW_ONLY_COPY_VISIBLE=False"
"STALE_NOT_INTEGRATED_COPY_VISIBLE=False"
"STUDY_LOGIC_CHANGED=False"
"BKT_LOGIC_CHANGED=False"
"PROGRESS_LOGIC_CHANGED=False"
"GENERATOR_LOGIC_CHANGED=False"
"BUILD_PERFORMED=False"
"ZIP_CREATED=False"
"SHARE_CREATED=False"
"DELIVERY_PERFORMED=False"
"TESTER_READINESS=LOCAL_STUDY_ITEMS_PREVIEW_STATUS_COPY_POLISH_PASS_NOT_PACKAGED"
"POLICY=study_items_preview_status_copy_polish_no_build_no_zip_no_share_no_delivery_no_distribution"
