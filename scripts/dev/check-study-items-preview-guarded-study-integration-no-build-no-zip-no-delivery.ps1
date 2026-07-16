$ErrorActionPreference = "Stop"

Write-Host "v0.7.84 check: start"

$engine = "services/api/study_engine.py"
$web = "services/api/web_app.py"
$doc = "docs/dev/study-items-preview-guarded-study-integration-no-build-no-zip-no-delivery.md"

$evidenceDir = "D:\dev\tester-runs\v0784-study-items-preview-guarded-study-integration"
$sourceInspect = "$evidenceDir\V0.7.84-STUDY-PREVIEW-INTEGRATION-SOURCE-INSPECT.json"
$engineInspect = "$evidenceDir\V0.7.84-STUDY-ENGINE-SOURCE-INSPECT.json"
$smoke = "$evidenceDir\V0.7.84-STUDY-ITEMS-PREVIEW-GUARDED-INTEGRATION-SMOKE.json"

foreach ($p in @($engine, $web, $doc, $sourceInspect, $engineInspect, $smoke)) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence: $p" }
}

python -m py_compile $engine $web

$engineText = Get-Content $engine -Raw
foreach ($item in @(
  "VOILA_V0_7_84_STUDY_ITEMS_PREVIEW_GUARDED_LOAD_START",
  "VOILA_V0_7_84_STUDY_ITEMS_PREVIEW_GUARDED_LOAD_END",
  "VOILA_V0_7_84_STUDY_ITEMS_PREVIEW_GUARDED_FALLBACK_START",
  "VOILA_V0_7_84_STUDY_ITEMS_PREVIEW_GUARDED_FALLBACK_END",
  "VOILA_V0_7_84_STUDY_ITEMS_PREVIEW_VIEW_METADATA_START",
  "VOILA_V0_7_84_STUDY_ITEMS_PREVIEW_VIEW_RETURN_START",
  "_load_study_items_preview_questions",
  "study_items.preview.json",
  "preview_quality_status",
  "v0.7.84_study_items_preview_guarded_study_integration",
  "study_items_preview_used",
  "question_source"
)) {
  if ($engineText -notlike "*$item*") { throw "study_engine.py missing expected text: $item" }
}

$webText = Get-Content $web -Raw
foreach ($item in @(
  "VOILA_V0_7_84_STUDY_ITEMS_PREVIEW_DISPLAY_GUARD_START",
  "VOILA_V0_7_84_STUDY_ITEMS_PREVIEW_DISPLAY_GUARD_END",
  'source_artifact") == "study_items.preview.json"',
  "return _study_question_display"
)) {
  if ($webText -notlike "*$item*") { throw "web_app.py missing expected display guard text: $item" }
}

$sourceData = Get-Content $sourceInspect -Raw | ConvertFrom-Json
if ($sourceData.VOILA_V0_7_84_STUDY_PREVIEW_INTEGRATION_SOURCE_INSPECT -ne "PASS") { throw "Source inspect marker mismatch" }
if ($sourceData.BUILD_PERFORMED -ne $false) { throw "Source inspect BUILD_PERFORMED mismatch" }
if ($sourceData.ZIP_CREATED -ne $false) { throw "Source inspect ZIP_CREATED mismatch" }
if ($sourceData.SHARE_CREATED -ne $false) { throw "Source inspect SHARE_CREATED mismatch" }
if ($sourceData.DELIVERY_PERFORMED -ne $false) { throw "Source inspect DELIVERY_PERFORMED mismatch" }

$engineData = Get-Content $engineInspect -Raw | ConvertFrom-Json
if ($engineData.VOILA_V0_7_84_STUDY_ENGINE_SOURCE_INSPECT -ne "PASS") { throw "Engine inspect marker mismatch" }
if ($engineData.files.'services\api\study_engine.py'.exists -ne $true) { throw "Engine inspect missing study_engine.py" }
if ($engineData.files.'services\api\study_questions.py'.exists -ne $true) { throw "Engine inspect missing study_questions.py" }
if ($engineData.BUILD_PERFORMED -ne $false) { throw "Engine inspect BUILD_PERFORMED mismatch" }
if ($engineData.ZIP_CREATED -ne $false) { throw "Engine inspect ZIP_CREATED mismatch" }
if ($engineData.SHARE_CREATED -ne $false) { throw "Engine inspect SHARE_CREATED mismatch" }
if ($engineData.DELIVERY_PERFORMED -ne $false) { throw "Engine inspect DELIVERY_PERFORMED mismatch" }

$smokeData = Get-Content $smoke -Raw | ConvertFrom-Json
if ($smokeData.VOILA_V0_7_84_STUDY_ITEMS_PREVIEW_GUARDED_INTEGRATION_SMOKE -ne "PASS") { throw "Smoke marker mismatch" }
if ($smokeData.loaded_question_count -ne 27) { throw "loaded_question_count mismatch" }
if ($smokeData.view_total_questions -ne 27) { throw "view_total_questions mismatch" }
if ($smokeData.study_items_preview_used -ne $true) { throw "study_items_preview_used mismatch" }
if ($smokeData.question_source -ne "study_items.preview.json") { throw "question_source mismatch" }
if ($smokeData.study_route_status -ne 200) { throw "study_route_status mismatch" }
if ($smokeData.preview_question_visible_in_study -ne $true) { throw "preview_question_visible_in_study mismatch" }
if ($smokeData.display_builder_preserves_preview_question -ne $true) { throw "display_builder_preserves_preview_question mismatch" }
if ($smokeData.hint_visible -ne $true) { throw "hint_visible mismatch" }
if ($smokeData.explanation_visible -ne $true) { throw "explanation_visible mismatch" }
if ($smokeData.legacy_prompt_visible -ne $false) { throw "legacy_prompt_visible mismatch" }
if ($smokeData.legacy_short_answer_visible -ne $false) { throw "legacy_short_answer_visible mismatch" }
if ($smokeData.fallback_without_preview_works -ne $true) { throw "fallback_without_preview_works mismatch" }
if ($smokeData.question_generation_changed -ne $false) { throw "question_generation_changed mismatch" }
if ($smokeData.bkt_logic_changed -ne $false) { throw "bkt_logic_changed mismatch" }
if ($smokeData.progress_logic_changed -ne $false) { throw "progress_logic_changed mismatch" }
if ($smokeData.generator_logic_changed -ne $false) { throw "generator_logic_changed mismatch" }
if ($smokeData.BUILD_PERFORMED -ne $false) { throw "Smoke BUILD_PERFORMED mismatch" }
if ($smokeData.ZIP_CREATED -ne $false) { throw "Smoke ZIP_CREATED mismatch" }
if ($smokeData.SHARE_CREATED -ne $false) { throw "Smoke SHARE_CREATED mismatch" }
if ($smokeData.DELIVERY_PERFORMED -ne $false) { throw "Smoke DELIVERY_PERFORMED mismatch" }

$docText = (Get-Content $doc -Raw).Replace('`','')
foreach ($item in @(
  "VOILA_V0_7_84_STUDY_ITEMS_PREVIEW_GUARDED_INTEGRATION_CHECK=PASS",
  "PASS_STUDY_ITEMS_PREVIEW_GUARDED_STUDY_INTEGRATION",
  "VOILA_V0_7_84_STUDY_ITEMS_PREVIEW_GUARDED_INTEGRATION_SMOKE=PASS",
  "loaded_question_count=27",
  "view_total_questions=27",
  "study_items_preview_used=True",
  "question_source=study_items.preview.json",
  "preview_question_visible_in_study=True",
  "display_builder_preserves_preview_question=True",
  "hint_visible=True",
  "explanation_visible=True",
  "legacy_prompt_visible=False",
  "legacy_short_answer_visible=False",
  "fallback_without_preview_works=True",
  "question_generation_changed=False",
  "bkt_logic_changed=False",
  "progress_logic_changed=False",
  "generator_logic_changed=False",
  "BUILD_PERFORMED=False",
  "ZIP_CREATED=False",
  "SHARE_CREATED=False",
  "DELIVERY_PERFORMED=False",
  "TESTER_READINESS=LOCAL_STUDY_ITEMS_PREVIEW_GUARDED_INTEGRATION_PASS_NOT_PACKAGED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/study_engine.py",
  "services/api/web_app.py",
  "docs/dev/study-items-preview-guarded-study-integration-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-study-items-preview-guarded-study-integration-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_84_STUDY_ITEMS_PREVIEW_GUARDED_INTEGRATION_CHECK=PASS"
"LOADED_QUESTION_COUNT=27"
"VIEW_TOTAL_QUESTIONS=27"
"STUDY_ITEMS_PREVIEW_USED=True"
"QUESTION_SOURCE=study_items.preview.json"
"STUDY_ROUTE_STATUS=200"
"PREVIEW_QUESTION_VISIBLE_IN_STUDY=True"
"DISPLAY_BUILDER_PRESERVES_PREVIEW_QUESTION=True"
"HINT_VISIBLE=True"
"EXPLANATION_VISIBLE=True"
"LEGACY_PROMPT_VISIBLE=False"
"LEGACY_SHORT_ANSWER_VISIBLE=False"
"FALLBACK_WITHOUT_PREVIEW_WORKS=True"
"QUESTION_GENERATION_CHANGED=False"
"BKT_LOGIC_CHANGED=False"
"PROGRESS_LOGIC_CHANGED=False"
"GENERATOR_LOGIC_CHANGED=False"
"BUILD_PERFORMED=False"
"ZIP_CREATED=False"
"SHARE_CREATED=False"
"DELIVERY_PERFORMED=False"
"TESTER_READINESS=LOCAL_STUDY_ITEMS_PREVIEW_GUARDED_INTEGRATION_PASS_NOT_PACKAGED"
"POLICY=study_items_preview_guarded_study_integration_no_build_no_zip_no_share_no_delivery_no_distribution"
