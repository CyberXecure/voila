$ErrorActionPreference = "Stop"

Write-Host "v0.7.81 check: start"

$courseId = "03-pag-30-34-vectori-trigonometrie"
$outDir = "data/output/$courseId"
$generator = "services/api/study_item_generator.py"
$doc = "docs/dev/study-question-quality-from-learning-pack-preview-no-build-no-zip-no-delivery.md"
$preview = "$outDir/study_items.preview.json"

$evidenceDir = "D:\dev\tester-runs\v0781-study-question-quality-preview"
$requiredEvidence = @(
  "$evidenceDir\V0.7.81-STUDY-QUESTION-QUALITY-SOURCE-INSPECT.json",
  "$evidenceDir\V0.7.81-LEARNING-PACK-SCHEMA-INSPECT.json",
  "$evidenceDir\V0.7.81-STUDY-ITEM-SOURCE-CONTENT-SAMPLE.json",
  "$evidenceDir\V0.7.81-STUDY-ITEMS-PREVIEW-QUALITY-SMOKE.json",
  "$evidenceDir\V0.7.81-STUDY-ITEMS-PREVIEW-VISIBLE-FIELDS-SMOKE.json"
)

foreach ($p in @($generator, $doc, "$outDir/document_learning_pack.json", "$outDir/generate_readiness_gate.json") + $requiredEvidence) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence: $p" }
}

python -m py_compile $generator
python $generator --output-dir $outDir

if (!(Test-Path $preview)) { throw "Preview was not generated: $preview" }

$generatorText = Get-Content $generator -Raw
foreach ($item in @(
  "BAD_PROMPT_PATTERNS",
  "deterministic_learning_pack_pedagogical_templates_no_llm",
  "v0.7.81_learning_pack_pedagogical_template_preview",
  "preview_only_not_used_by_study",
  "vectori opuși",
  "Cum recunoști doi vectori opuși?",
  "Care este diferența dintre vectori egali și vectori opuși?"
)) {
  if ($generatorText -notlike "*$item*") { throw "Generator missing expected text: $item" }
}

$previewData = Get-Content $preview -Raw | ConvertFrom-Json
$gate = $previewData.quality_gate
$policy = $previewData.policy

if ($previewData.artifact -ne "study_items_preview") { throw "Preview artifact mismatch" }
if ($previewData.artifact_version -ne "v0.7.81") { throw "Preview artifact_version mismatch" }
if ($previewData.integration_status -ne "preview_only_not_used_by_study") { throw "Preview integration_status mismatch" }
if ($previewData.item_count -lt 14) { throw "Too few preview items" }
if ($previewData.concept_count -ne 14) { throw "Concept count mismatch" }
if ($previewData.items.Count -ne $previewData.item_count) { throw "Item count mismatch" }

$covered = @($previewData.items | ForEach-Object { $_.concept_id } | Sort-Object -Unique)
if ($covered.Count -ne 14) { throw "Covered concept count mismatch: $($covered.Count)" }

if ($gate.preview_quality_status -ne "PASS") { throw "Preview quality gate is not PASS" }
if ($gate.bad_prompt_hit_count -ne 0) { throw "bad_prompt_hit_count mismatch" }
if ($gate.copied_answer_hit_count -ne 0) { throw "copied_answer_hit_count mismatch" }
if ($gate.too_short_explanation_hit_count -ne 0) { throw "too_short_explanation_hit_count mismatch" }
if ($gate.missing_hint_hit_count -ne 0) { throw "missing_hint_hit_count mismatch" }
if ($gate.question_generation_changed -ne $false) { throw "question_generation_changed mismatch" }
if ($gate.bkt_logic_changed -ne $false) { throw "bkt_logic_changed mismatch" }
if ($gate.study_integration_changed -ne $false) { throw "study_integration_changed mismatch" }
if ($gate.preview_only -ne $true) { throw "preview_only mismatch" }

if ($policy.uses_llm -ne $false) { throw "uses_llm mismatch" }
if ($policy.uses_cloud -ne $false) { throw "uses_cloud mismatch" }
if ($policy.build_performed -ne $false) { throw "build_performed mismatch" }
if ($policy.zip_created -ne $false) { throw "zip_created mismatch" }
if ($policy.share_created -ne $false) { throw "share_created mismatch" }
if ($policy.delivery_performed -ne $false) { throw "delivery_performed mismatch" }
if ($policy.distribution_performed -ne $false) { throw "distribution_performed mismatch" }

$badPatterns = @(
  "Ce precizare tehnică face sursa",
  "Care este ideea importantă",
  "Care este ideea principală",
  "Ce spune sursa",
  "What should you remember",
  "Name one key point",
  "Identify the main purpose"
)

$visibleFields = @("question", "expected_answer", "hint", "explanation")
$rawMarkers = @("- AB = BA", ": -")

foreach ($it in $previewData.items) {
  foreach ($f in $visibleFields) {
    $value = [string]$it.$f
    if ([string]::IsNullOrWhiteSpace($value)) { throw "Empty visible field $f for item $($it.item_id)" }
    foreach ($bad in $badPatterns) {
      if ($value -like "*$bad*") { throw "Bad prompt pattern in visible field $f for item $($it.item_id): $bad" }
    }
    foreach ($raw in $rawMarkers) {
      if ($value -like "*$raw*") { throw "Raw notation visible in field $f for item $($it.item_id): $raw" }
    }
  }

  if ([string]$it.question -eq [string]$it.expected_answer) {
    throw "Question equals answer for item $($it.item_id)"
  }
  if (([string]$it.hint).Length -lt 20) {
    throw "Hint too short for item $($it.item_id)"
  }
  if (([string]$it.explanation).Length -lt 40) {
    throw "Explanation too short for item $($it.item_id)"
  }
}

$opusi = @($previewData.items | Where-Object { $_.term -eq "vectori opuși" })
if ($opusi.Count -lt 2) { throw "vectori opuși template not active" }

$docText = (Get-Content $doc -Raw).Replace('`','')
foreach ($item in @(
  "VOILA_V0_7_81_STUDY_QUESTION_QUALITY_PREVIEW_CHECK=PASS",
  "PASS_STUDY_ITEMS_PREVIEW_QUALITY",
  "item_count=27",
  "concept_count=14",
  "covered_concept_count=14",
  "bad_prompt_hit_count=0",
  "copied_answer_hit_count=0",
  "too_short_explanation_hit_count=0",
  "missing_hint_hit_count=0",
  "raw_notation_visible_fields=False",
  "question_generation_changed=False",
  "bkt_logic_changed=False",
  "study_integration_changed=False",
  "preview_only=True",
  "BUILD_PERFORMED=False",
  "ZIP_CREATED=False",
  "SHARE_CREATED=False",
  "DELIVERY_PERFORMED=False",
  "TESTER_READINESS=LOCAL_STUDY_QUESTION_QUALITY_PREVIEW_PASS_NOT_INTEGRATED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/study_item_generator.py",
  "docs/dev/study-question-quality-from-learning-pack-preview-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-study-question-quality-from-learning-pack-preview-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_81_STUDY_QUESTION_QUALITY_PREVIEW_CHECK=PASS"
"ITEM_COUNT=$($previewData.item_count)"
"CONCEPT_COUNT=$($previewData.concept_count)"
"COVERED_CONCEPT_COUNT=$($covered.Count)"
"BAD_PROMPT_HIT_COUNT=0"
"COPIED_ANSWER_HIT_COUNT=0"
"TOO_SHORT_EXPLANATION_HIT_COUNT=0"
"MISSING_HINT_HIT_COUNT=0"
"RAW_NOTATION_VISIBLE_FIELDS=False"
"VECTORI_OPUSI_TEMPLATE_ACTIVE=True"
"QUESTION_GENERATION_CHANGED=False"
"BKT_LOGIC_CHANGED=False"
"STUDY_INTEGRATION_CHANGED=False"
"PREVIEW_ONLY=True"
"USES_LLM=False"
"USES_CLOUD=False"
"BUILD_PERFORMED=False"
"ZIP_CREATED=False"
"SHARE_CREATED=False"
"DELIVERY_PERFORMED=False"
"TESTER_READINESS=LOCAL_STUDY_QUESTION_QUALITY_PREVIEW_PASS_NOT_INTEGRATED"
"POLICY=study_question_quality_preview_no_build_no_zip_no_share_no_delivery_no_distribution"
