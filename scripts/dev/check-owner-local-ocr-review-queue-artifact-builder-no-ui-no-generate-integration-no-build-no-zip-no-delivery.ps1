$ErrorActionPreference = "Stop"

$module = "services/api/ocr_review_queue.py"
$doc = "docs/dev/owner-local-ocr-review-queue-artifact-builder-no-ui-no-generate-integration-no-build-no-zip-no-delivery.md"
$v0764Doc = "docs/dev/owner-local-ocr-review-contract-for-document-learning-gate-no-generate-integration-no-build-no-zip-no-delivery.md"
$queueJson = "D:\dev\tester-runs\voila-v0.7.65-owner-local-ocr-review-queue-artifact-builder-no-ui-no-generate-integration-no-build-no-zip-no-delivery\real-course-ocr-review-queue\ocr_review_queue.json"
$queueMd = "D:\dev\tester-runs\voila-v0.7.65-owner-local-ocr-review-queue-artifact-builder-no-ui-no-generate-integration-no-build-no-zip-no-delivery\real-course-ocr-review-queue\ocr_review_queue.md"

if (!(Test-Path $module)) { throw "Missing module: $module" }
if (!(Test-Path $doc)) { throw "Missing v0.7.65 doc: $doc" }
if (!(Test-Path $v0764Doc)) { throw "Missing v0.7.64 baseline doc: $v0764Doc" }
if (!(Test-Path $queueJson)) { throw "Missing real-course OCR Review queue JSON evidence: $queueJson" }
if (!(Test-Path $queueMd)) { throw "Missing real-course OCR Review queue MD evidence: $queueMd" }

python -m py_compile $module

$queue = Get-Content $queueJson -Raw | ConvertFrom-Json

if ($queue.artifact -ne "ocr_review_queue") { throw "Unexpected artifact name" }
if ([int]$queue.source_page_count -ne 5) { throw "Expected source_page_count=5" }
if ([int]$queue.review_item_count -lt 10) { throw "Expected at least 10 review items for real OCR/OCR Math smoke" }
if ($queue.quality_gate.review_required -ne $true) { throw "Expected review_required=True" }
if ($queue.quality_gate.generation_should_wait_for_review -ne $true) { throw "Expected generation_should_wait_for_review=True" }

if ($queue.learning_policy.ocr_review_is_user_assisted_document_learning -ne $true) { throw "Expected OCR Review learning policy" }
if ($queue.learning_policy.user_corrections_become_verified_evidence -ne $true) { throw "Expected user corrections verified evidence policy" }
if ($queue.learning_policy.feed_back_into_document_learning_pack -ne $true) { throw "Expected feedback into document learning pack policy" }
if ($queue.learning_policy.do_not_generate_from_unresolved_blocked_items -ne $true) { throw "Expected unresolved blocked items generation policy" }

if ($queue.policy.no_ui_implementation -ne $true) { throw "Expected no UI implementation policy" }
if ($queue.policy.no_generate_integration -ne $true) { throw "Expected no generate integration policy" }
if ($queue.policy.no_build -ne $true) { throw "Expected no build policy" }
if ($queue.policy.no_zip -ne $true) { throw "Expected no ZIP policy" }
if ($queue.policy.no_delivery -ne $true) { throw "Expected no delivery policy" }
if ($queue.policy.no_distribution -ne $true) { throw "Expected no distribution policy" }

$items = @($queue.review_items)
if ($items.Count -ne [int]$queue.review_item_count) { throw "Review item count mismatch" }

foreach ($field in @(
  "review_item_id",
  "source_pdf_page",
  "source_text",
  "suspect_text",
  "suggested_text",
  "issue_type",
  "confidence",
  "reason_codes",
  "suggested_learning_role",
  "linked_concept_terms",
  "ocr_math_context",
  "requires_user_decision",
  "allowed_decisions"
)) {
  foreach ($item in $items) {
    if ($null -eq $item.$field) { throw "Missing review item field: $field" }
  }
}

$itemTypes = (($items | ForEach-Object { $_.issue_type }) -join "`n")
foreach ($expected in @("ocr_math_uncertain", "broken_line_join", "definition_candidate_uncertain")) {
  if ($itemTypes -notlike "*$expected*") { throw "Missing expected issue type: $expected" }
}

$roles = (($items | ForEach-Object { $_.suggested_learning_role }) -join "`n")
foreach ($expected in @("formula", "definition", "notation", "theorem")) {
  if ($roles -notlike "*$expected*") { throw "Missing expected suggested learning role: $expected" }
}

$sourceText = (($items | ForEach-Object { $_.source_text }) -join "`n").ToLowerInvariant()
foreach ($expected in @("vector", "coordonatele", "produsul scalar", "funcții trigonometrice")) {
  if ($sourceText -notlike "*$expected*") { throw "Missing expected real OCR review source fragment: $expected" }
}

$moduleText = Get-Content $module -Raw
foreach ($item in @(
  "build_ocr_review_queue",
  "build_review_items",
  "write_ocr_review_queue",
  "ocr_review_queue.json",
  "ocr_review_queue.md",
  "ocr_review_is_user_assisted_document_learning",
  "user_corrections_become_verified_evidence",
  "feed_back_into_document_learning_pack",
  "do_not_generate_from_unresolved_blocked_items"
)) {
  if ($moduleText -notlike "*$item*") { throw "Module missing expected text: $item" }
}

$docText = Get-Content $doc -Raw
$docCheckText = $docText.Replace('`', '')
foreach ($item in @(
  "VOILA_V0_7_65_OCR_REVIEW_QUEUE_ARTIFACT_BUILDER_CHECK=PASS",
  "PASS_QUEUE_ARTIFACT_BUILDER",
  "OCR Review is user-assisted document learning",
  "ocr_review_queue.json",
  "ocr_review_queue.md",
  "review_item_count=20",
  "review_required=True",
  "generation_should_wait_for_review=True",
  "user corrections become verified evidence",
  "No /generate route change.",
  "No UI implementation.",
  "No build.",
  "No ZIP.",
  "No share.",
  "No delivery.",
  "No distribution.",
  "Tester readiness remains BLOCKED"
)) {
  if ($docCheckText -notlike "*$item*") { throw "Doc missing expected v0.7.65 text: $item" }
}

$webAppText = Get-Content "services/api/web_app.py" -Raw
if ($webAppText -like "*ocr_review_queue*" -or $webAppText -like "*ocr_review_decisions*" -or $webAppText -like "*document_learning_pack*") {
  throw "v0.7.65 must not integrate OCR Review queue into web_app.py"
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/ocr_review_queue.py",
  "docs/dev/owner-local-ocr-review-queue-artifact-builder-no-ui-no-generate-integration-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-ocr-review-queue-artifact-builder-no-ui-no-generate-integration-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.65: $line"
  }
}

"VOILA_V0_7_65_OCR_REVIEW_QUEUE_ARTIFACT_BUILDER_CHECK=PASS"
"OCR_REVIEW_QUEUE_ARTIFACT=PASS"
"REAL_COURSE_REVIEW_ITEM_COUNT=$($queue.review_item_count)"
"REVIEW_REQUIRED=True"
"GENERATION_SHOULD_WAIT_FOR_REVIEW=True"
"OCR_REVIEW_IS_USER_ASSISTED_DOCUMENT_LEARNING=True"
"DOCUMENT_LEARNING_PACK_FEEDBACK_LOOP=DEFINED"
"GENERATE_INTEGRATION=NOT_CHANGED"
"UI_IMPLEMENTATION=NOT_CHANGED"
"LESSONS_QUIZ_FLASHCARDS_GLOSSARY=NOT_CHANGED"
"TESTER_READINESS=BLOCKED"
"POLICY=owner_local_ocr_review_queue_artifact_only_no_ui_no_generate_integration_no_regeneration_no_build_no_zip_no_share_no_delivery_no_distribution"
