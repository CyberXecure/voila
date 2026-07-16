$ErrorActionPreference = "Stop"

Write-Host "v0.7.85 check: start"

$web = "services/api/web_app.py"
$doc = "docs/dev/study-items-preview-romanian-label-polish-no-build-no-zip-no-delivery.md"

$evidenceDir = "D:\dev\tester-runs\v0785-study-items-preview-romanian-label-polish"
$sourceInspect = "$evidenceDir\V0.7.85-STUDY-ITEMS-PREVIEW-LABEL-POLISH-SOURCE-INSPECT.json"
$smoke = "$evidenceDir\V0.7.85-STUDY-ITEMS-PREVIEW-LABEL-POLISH-SMOKE.json"

foreach ($p in @($web, $doc, $sourceInspect, $smoke)) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence: $p" }
}

python -m py_compile $web

$webText = Get-Content $web -Raw
foreach ($item in @(
  "VOILA_V0_7_85_STUDY_ITEMS_PREVIEW_LABEL_POLISH_START",
  "VOILA_V0_7_85_STUDY_ITEMS_PREVIEW_LABEL_POLISH_END",
  "_voila_v085_study_item_question_type_label",
  "Indiciu:",
  "înțelegere concept",
  "verificare condiții",
  "diferențiere",
  "adevărat/fals",
  "de ce contează",
  "aplicare/verificare"
)) {
  if ($webText -notlike "*$item*") { throw "web_app.py missing expected label polish text: $item" }
}

if ($webText -like "*<strong>Hint:</strong>*") {
  throw "web_app.py still displays Hint label in preview viewer"
}

$sourceData = Get-Content $sourceInspect -Raw | ConvertFrom-Json
if ($sourceData.VOILA_V0_7_85_STUDY_ITEMS_PREVIEW_LABEL_POLISH_SOURCE_INSPECT -ne "PASS") { throw "Source inspect marker mismatch" }
if ($sourceData.BUILD_PERFORMED -ne $false) { throw "Source inspect BUILD_PERFORMED mismatch" }
if ($sourceData.ZIP_CREATED -ne $false) { throw "Source inspect ZIP_CREATED mismatch" }
if ($sourceData.SHARE_CREATED -ne $false) { throw "Source inspect SHARE_CREATED mismatch" }
if ($sourceData.DELIVERY_PERFORMED -ne $false) { throw "Source inspect DELIVERY_PERFORMED mismatch" }

$smokeData = Get-Content $smoke -Raw | ConvertFrom-Json
if ($smokeData.VOILA_V0_7_85_STUDY_ITEMS_PREVIEW_LABEL_POLISH_SMOKE -ne "PASS") { throw "Smoke marker mismatch" }
if ($smokeData.viewer_status -ne 200) { throw "viewer_status mismatch" }
if ($smokeData.study_status -ne 200) { throw "study_status mismatch" }
if ($smokeData.hint_label_polished -ne $true) { throw "hint_label_polished mismatch" }
if ($smokeData.question_type_labels_polished -ne $true) { throw "question_type_labels_polished mismatch" }
if ($smokeData.raw_question_type_visible -ne $false) { throw "raw_question_type_visible mismatch" }
if ($smokeData.legacy_short_answer_visible -ne $false) { throw "legacy_short_answer_visible mismatch" }
if ($smokeData.study_integration_changed -ne $false) { throw "study_integration_changed mismatch" }
if ($smokeData.bkt_logic_changed -ne $false) { throw "bkt_logic_changed mismatch" }
if ($smokeData.progress_logic_changed -ne $false) { throw "progress_logic_changed mismatch" }
if ($smokeData.generator_logic_changed -ne $false) { throw "generator_logic_changed mismatch" }
if ($smokeData.BUILD_PERFORMED -ne $false) { throw "Smoke BUILD_PERFORMED mismatch" }
if ($smokeData.ZIP_CREATED -ne $false) { throw "Smoke ZIP_CREATED mismatch" }
if ($smokeData.SHARE_CREATED -ne $false) { throw "Smoke SHARE_CREATED mismatch" }
if ($smokeData.DELIVERY_PERFORMED -ne $false) { throw "Smoke DELIVERY_PERFORMED mismatch" }

$docText = (Get-Content $doc -Raw).Replace('`','')
foreach ($item in @(
  "VOILA_V0_7_85_STUDY_ITEMS_PREVIEW_LABEL_POLISH_CHECK=PASS",
  "PASS_STUDY_ITEMS_PREVIEW_ROMANIAN_LABEL_POLISH",
  "VOILA_V0_7_85_STUDY_ITEMS_PREVIEW_LABEL_POLISH_SOURCE_INSPECT=PASS",
  "VOILA_V0_7_85_STUDY_ITEMS_PREVIEW_LABEL_POLISH_SMOKE=PASS",
  "hint_label_polished=True",
  "question_type_labels_polished=True",
  "raw_question_type_visible=False",
  "legacy_short_answer_visible=False",
  "study_integration_changed=False",
  "bkt_logic_changed=False",
  "progress_logic_changed=False",
  "generator_logic_changed=False",
  "BUILD_PERFORMED=False",
  "ZIP_CREATED=False",
  "SHARE_CREATED=False",
  "DELIVERY_PERFORMED=False",
  "TESTER_READINESS=LOCAL_STUDY_ITEMS_PREVIEW_ROMANIAN_LABEL_POLISH_PASS_NOT_PACKAGED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/web_app.py",
  "docs/dev/study-items-preview-romanian-label-polish-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-study-items-preview-romanian-label-polish-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_85_STUDY_ITEMS_PREVIEW_LABEL_POLISH_CHECK=PASS"
"HINT_LABEL_POLISHED=True"
"QUESTION_TYPE_LABELS_POLISHED=True"
"RAW_QUESTION_TYPE_VISIBLE=False"
"LEGACY_SHORT_ANSWER_VISIBLE=False"
"STUDY_INTEGRATION_CHANGED=False"
"BKT_LOGIC_CHANGED=False"
"PROGRESS_LOGIC_CHANGED=False"
"GENERATOR_LOGIC_CHANGED=False"
"BUILD_PERFORMED=False"
"ZIP_CREATED=False"
"SHARE_CREATED=False"
"DELIVERY_PERFORMED=False"
"TESTER_READINESS=LOCAL_STUDY_ITEMS_PREVIEW_ROMANIAN_LABEL_POLISH_PASS_NOT_PACKAGED"
"POLICY=study_items_preview_romanian_label_polish_no_build_no_zip_no_share_no_delivery_no_distribution"
