$ErrorActionPreference = "Stop"

Write-Host "v0.7.82 check: start"

$web = "services/api/web_app.py"
$doc = "docs/dev/study-items-preview-viewer-no-build-no-zip-no-delivery.md"
$preview = "data/output/03-pag-30-34-vectori-trigonometrie/study_items.preview.json"

$evidenceDir = "D:\dev\tester-runs\v0782-study-items-preview-viewer"
$sourceInspect = "$evidenceDir\V0.7.82-STUDY-ITEMS-PREVIEW-VIEWER-SOURCE-INSPECT.json"
$smoke = "$evidenceDir\V0.7.82-STUDY-ITEMS-PREVIEW-VIEWER-SMOKE.json"

foreach ($p in @($web, $doc, $preview, $sourceInspect, $smoke)) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence: $p" }
}

python -m py_compile $web

$webText = Get-Content $web -Raw
foreach ($item in @(
  "VOILA_V0_7_82_STUDY_ITEMS_PREVIEW_VIEWER_START",
  "VOILA_V0_7_82_STUDY_ITEMS_PREVIEW_VIEWER_END",
  "/owner/study-items-preview/{course_id}/view",
  "def owner_study_items_preview_view",
  "study_items.preview.json",
  "Previzualizare Study items",
  "preview only",
  "nu este integrat încă în Study",
  "Răspuns așteptat:",
  "Hint:",
  "Explicație:"
)) {
  if ($webText -notlike "*$item*") { throw "web_app.py missing expected viewer text: $item" }
}

$sourceData = Get-Content $sourceInspect -Raw | ConvertFrom-Json
if ($sourceData.VOILA_V0_7_82_STUDY_ITEMS_PREVIEW_VIEWER_SOURCE_INSPECT -ne "PASS") { throw "Source inspect marker mismatch" }
if ($sourceData.preview_exists -ne $true) { throw "Source inspect preview_exists mismatch" }
if ($sourceData.preview_summary.quality_status -ne "PASS") { throw "Source inspect preview quality mismatch" }
if ($sourceData.preview_summary.item_count -ne 27) { throw "Source inspect item count mismatch" }
if ($sourceData.preview_summary.concept_count -ne 14) { throw "Source inspect concept count mismatch" }
if ($sourceData.BUILD_PERFORMED -ne $false) { throw "Source inspect BUILD_PERFORMED mismatch" }
if ($sourceData.ZIP_CREATED -ne $false) { throw "Source inspect ZIP_CREATED mismatch" }
if ($sourceData.SHARE_CREATED -ne $false) { throw "Source inspect SHARE_CREATED mismatch" }
if ($sourceData.DELIVERY_PERFORMED -ne $false) { throw "Source inspect DELIVERY_PERFORMED mismatch" }

$smokeData = Get-Content $smoke -Raw | ConvertFrom-Json
if ($smokeData.VOILA_V0_7_82_STUDY_ITEMS_PREVIEW_VIEWER_SMOKE -ne "PASS") { throw "Smoke marker mismatch" }
if ($smokeData.route_status -ne 200) { throw "Smoke route_status mismatch" }
if ($smokeData.card_count -ne 27) { throw "Smoke card_count mismatch" }
if ($smokeData.raw_notation_visible -ne $false) { throw "raw_notation_visible mismatch" }
if ($smokeData.legacy_prompt_visible -ne $false) { throw "legacy_prompt_visible mismatch" }
if ($smokeData.study_integration_changed -ne $false) { throw "study_integration_changed mismatch" }
if ($smokeData.bkt_logic_changed -ne $false) { throw "bkt_logic_changed mismatch" }
if ($smokeData.preview_only -ne $true) { throw "preview_only mismatch" }
if ($smokeData.BUILD_PERFORMED -ne $false) { throw "Smoke BUILD_PERFORMED mismatch" }
if ($smokeData.ZIP_CREATED -ne $false) { throw "Smoke ZIP_CREATED mismatch" }
if ($smokeData.SHARE_CREATED -ne $false) { throw "Smoke SHARE_CREATED mismatch" }
if ($smokeData.DELIVERY_PERFORMED -ne $false) { throw "Smoke DELIVERY_PERFORMED mismatch" }

$docText = (Get-Content $doc -Raw).Replace('`','')
foreach ($item in @(
  "VOILA_V0_7_82_STUDY_ITEMS_PREVIEW_VIEWER_CHECK=PASS",
  "PASS_STUDY_ITEMS_PREVIEW_VIEWER",
  "VOILA_V0_7_82_STUDY_ITEMS_PREVIEW_VIEWER_SOURCE_INSPECT=PASS",
  "VOILA_V0_7_82_STUDY_ITEMS_PREVIEW_VIEWER_SMOKE=PASS",
  "route_status=200",
  "card_count=27",
  "raw_notation_visible=False",
  "legacy_prompt_visible=False",
  "study_integration_changed=False",
  "bkt_logic_changed=False",
  "preview_only=True",
  "BUILD_PERFORMED=False",
  "ZIP_CREATED=False",
  "SHARE_CREATED=False",
  "DELIVERY_PERFORMED=False",
  "TESTER_READINESS=LOCAL_STUDY_ITEMS_PREVIEW_VIEWER_PASS_NOT_INTEGRATED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/web_app.py",
  "docs/dev/study-items-preview-viewer-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-study-items-preview-viewer-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_82_STUDY_ITEMS_PREVIEW_VIEWER_CHECK=PASS"
"ROUTE_STATUS=200"
"CARD_COUNT=27"
"RAW_NOTATION_VISIBLE=False"
"LEGACY_PROMPT_VISIBLE=False"
"STUDY_INTEGRATION_CHANGED=False"
"BKT_LOGIC_CHANGED=False"
"PREVIEW_ONLY=True"
"BUILD_PERFORMED=False"
"ZIP_CREATED=False"
"SHARE_CREATED=False"
"DELIVERY_PERFORMED=False"
"TESTER_READINESS=LOCAL_STUDY_ITEMS_PREVIEW_VIEWER_PASS_NOT_INTEGRATED"
"POLICY=study_items_preview_viewer_no_build_no_zip_no_share_no_delivery_no_distribution"
