$ErrorActionPreference = "Stop"

Write-Host "v0.7.83 check: start"

$web = "services/api/web_app.py"
$doc = "docs/dev/study-items-preview-link-no-build-no-zip-no-delivery.md"

$evidenceDir = "D:\dev\tester-runs\v0783-study-items-preview-link"
$sourceInspect = "$evidenceDir\V0.7.83-STUDY-ITEMS-PREVIEW-LINK-SOURCE-INSPECT.json"
$targetInspect = "$evidenceDir\V0.7.83-STUDY-ITEMS-PREVIEW-LINK-TARGET-INSPECT.json"
$smoke = "$evidenceDir\V0.7.83-STUDY-ITEMS-PREVIEW-LINK-SMOKE.json"

foreach ($p in @($web, $doc, $sourceInspect, $targetInspect, $smoke)) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence: $p" }
}

python -m py_compile $web

$webText = Get-Content $web -Raw
foreach ($item in @(
  "VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_START",
  "VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_END",
  "VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_AVAILABLE_START",
  "VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_AVAILABLE_END",
  "study_items.preview.json",
  "Study Items Preview",
  "/owner/study-items-preview/",
  "Previzualizare owner-local read-only",
  "nu modifică Study, BKT sau Progress"
)) {
  if ($webText -notlike "*$item*") { throw "web_app.py missing expected link text: $item" }
}

$sourceData = Get-Content $sourceInspect -Raw | ConvertFrom-Json
if ($sourceData.VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_SOURCE_INSPECT -ne "PASS") { throw "Source inspect marker mismatch" }
if ($sourceData.preview_exists -ne $true) { throw "Source inspect preview_exists mismatch" }
if ($sourceData.BUILD_PERFORMED -ne $false) { throw "Source inspect BUILD_PERFORMED mismatch" }
if ($sourceData.ZIP_CREATED -ne $false) { throw "Source inspect ZIP_CREATED mismatch" }
if ($sourceData.SHARE_CREATED -ne $false) { throw "Source inspect SHARE_CREATED mismatch" }
if ($sourceData.DELIVERY_PERFORMED -ne $false) { throw "Source inspect DELIVERY_PERFORMED mismatch" }

$targetData = Get-Content $targetInspect -Raw | ConvertFrom-Json
if ($targetData.VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_TARGET_INSPECT -ne "PASS") { throw "Target inspect marker mismatch" }
if ($targetData.hit_count -lt 1) { throw "Target inspect hit_count mismatch" }
if ($targetData.BUILD_PERFORMED -ne $false) { throw "Target inspect BUILD_PERFORMED mismatch" }
if ($targetData.ZIP_CREATED -ne $false) { throw "Target inspect ZIP_CREATED mismatch" }
if ($targetData.SHARE_CREATED -ne $false) { throw "Target inspect SHARE_CREATED mismatch" }
if ($targetData.DELIVERY_PERFORMED -ne $false) { throw "Target inspect DELIVERY_PERFORMED mismatch" }

$smokeData = Get-Content $smoke -Raw | ConvertFrom-Json
if ($smokeData.VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_SMOKE -ne "PASS") { throw "Smoke marker mismatch" }
if ($smokeData.course_tools_status -ne 200) { throw "course_tools_status mismatch" }
if ($smokeData.link_visible -ne $true) { throw "link_visible mismatch" }
if ($smokeData.viewer_href_visible -ne $true) { throw "viewer_href_visible mismatch" }
if ($smokeData.viewer_target_status -ne 200) { throw "viewer_target_status mismatch" }
if ($smokeData.preview_card_available -ne $true) { throw "preview_card_available mismatch" }
if ($smokeData.study_integration_changed -ne $false) { throw "study_integration_changed mismatch" }
if ($smokeData.bkt_logic_changed -ne $false) { throw "bkt_logic_changed mismatch" }
if ($smokeData.progress_logic_changed -ne $false) { throw "progress_logic_changed mismatch" }
if ($smokeData.generator_logic_changed -ne $false) { throw "generator_logic_changed mismatch" }
if ($smokeData.preview_only -ne $true) { throw "preview_only mismatch" }
if ($smokeData.BUILD_PERFORMED -ne $false) { throw "Smoke BUILD_PERFORMED mismatch" }
if ($smokeData.ZIP_CREATED -ne $false) { throw "Smoke ZIP_CREATED mismatch" }
if ($smokeData.SHARE_CREATED -ne $false) { throw "Smoke SHARE_CREATED mismatch" }
if ($smokeData.DELIVERY_PERFORMED -ne $false) { throw "Smoke DELIVERY_PERFORMED mismatch" }

$docText = (Get-Content $doc -Raw).Replace('`','')
foreach ($item in @(
  "VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_CHECK=PASS",
  "PASS_STUDY_ITEMS_PREVIEW_LINK",
  "VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_SOURCE_INSPECT=PASS",
  "VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_TARGET_INSPECT=PASS",
  "VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_SMOKE=PASS",
  "course_tools_status=200",
  "link_visible=True",
  "viewer_href_visible=True",
  "viewer_target_status=200",
  "preview_card_available=True",
  "study_integration_changed=False",
  "bkt_logic_changed=False",
  "progress_logic_changed=False",
  "generator_logic_changed=False",
  "preview_only=True",
  "BUILD_PERFORMED=False",
  "ZIP_CREATED=False",
  "SHARE_CREATED=False",
  "DELIVERY_PERFORMED=False",
  "TESTER_READINESS=LOCAL_STUDY_ITEMS_PREVIEW_LINK_PASS_NOT_INTEGRATED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/web_app.py",
  "docs/dev/study-items-preview-link-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-study-items-preview-link-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_CHECK=PASS"
"COURSE_TOOLS_STATUS=200"
"LINK_VISIBLE=True"
"VIEWER_HREF_VISIBLE=True"
"VIEWER_TARGET_STATUS=200"
"PREVIEW_CARD_AVAILABLE=True"
"STUDY_INTEGRATION_CHANGED=False"
"BKT_LOGIC_CHANGED=False"
"PROGRESS_LOGIC_CHANGED=False"
"GENERATOR_LOGIC_CHANGED=False"
"PREVIEW_ONLY=True"
"BUILD_PERFORMED=False"
"ZIP_CREATED=False"
"SHARE_CREATED=False"
"DELIVERY_PERFORMED=False"
"TESTER_READINESS=LOCAL_STUDY_ITEMS_PREVIEW_LINK_PASS_NOT_INTEGRATED"
"POLICY=study_items_preview_link_no_build_no_zip_no_share_no_delivery_no_distribution"
