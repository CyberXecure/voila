$ErrorActionPreference = "Stop"

$module = "services/api/ocr_review_decisions.py"
$doc = "docs/dev/owner-local-ocr-review-decisions-artifact-builder-no-ui-no-generate-integration-no-build-no-zip-no-delivery.md"
$v0765Doc = "docs/dev/owner-local-ocr-review-queue-artifact-builder-no-ui-no-generate-integration-no-build-no-zip-no-delivery.md"
$decisionsJson = "D:\dev\tester-runs\voila-v0.7.66-owner-local-ocr-review-decisions-artifact-builder-no-ui-no-generate-integration-no-build-no-zip-no-delivery\real-course-ocr-review-decisions\ocr_review_decisions.json"
$decisionsMd = "D:\dev\tester-runs\voila-v0.7.66-owner-local-ocr-review-decisions-artifact-builder-no-ui-no-generate-integration-no-build-no-zip-no-delivery\real-course-ocr-review-decisions\ocr_review_decisions.md"

if (!(Test-Path $module)) { throw "Missing module: $module" }
if (!(Test-Path $doc)) { throw "Missing v0.7.66 doc: $doc" }
if (!(Test-Path $v0765Doc)) { throw "Missing v0.7.65 baseline doc: $v0765Doc" }
if (!(Test-Path $decisionsJson)) { throw "Missing real-course OCR Review decisions JSON evidence: $decisionsJson" }
if (!(Test-Path $decisionsMd)) { throw "Missing real-course OCR Review decisions MD evidence: $decisionsMd" }

python -m py_compile $module

$decisions = Get-Content $decisionsJson -Raw | ConvertFrom-Json

if ($decisions.artifact -ne "ocr_review_decisions") { throw "Unexpected artifact name" }
if ([int]$decisions.source_page_count -ne 5) { throw "Expected source_page_count=5" }
if ([int]$decisions.source_review_item_count -ne 20) { throw "Expected source_review_item_count=20" }
if ([int]$decisions.decision_count -ne 20) { throw "Expected decision_count=20" }
if ([int]$decisions.pending_decision_count -ne 20) { throw "Expected pending_decision_count=20" }
if ($decisions.quality_gate.all_required_decisions_resolved -ne $false) { throw "Expected all_required_decisions_resolved=False" }
if ($decisions.quality_gate.generation_should_wait_for_review -ne $true) { throw "Expected generation_should_wait_for_review=True" }

if ($decisions.learning_policy.ocr_review_is_user_assisted_document_learning -ne $true) { throw "Expected OCR Review learning policy" }
if ($decisions.learning_policy.user_corrections_become_verified_evidence -ne $true) { throw "Expected user corrections verified evidence policy" }
if ($decisions.learning_policy.feed_back_into_document_learning_pack -ne $true) { throw "Expected feedback into document learning pack policy" }
if ($decisions.learning_policy.do_not_generate_from_unresolved_blocked_items -ne $true) { throw "Expected unresolved blocked items generation policy" }
if ($decisions.learning_policy.pending_decisions_are_not_verified_evidence -ne $true) { throw "Expected pending decisions not verified evidence policy" }

if ($decisions.policy.no_ui_implementation -ne $true) { throw "Expected no UI implementation policy" }
if ($decisions.policy.no_generate_integration -ne $true) { throw "Expected no generate integration policy" }
if ($decisions.policy.no_build -ne $true) { throw "Expected no build policy" }
if ($decisions.policy.no_zip -ne $true) { throw "Expected no ZIP policy" }
if ($decisions.policy.no_delivery -ne $true) { throw "Expected no delivery policy" }
if ($decisions.policy.no_distribution -ne $true) { throw "Expected no distribution policy" }

$items = @($decisions.decisions)
if ($items.Count -ne 20) { throw "Expected 20 decision items" }

foreach ($field in @(
  "review_item_id",
  "decision",
  "allowed_decisions",
  "source_pdf_page",
  "source_text",
  "suggested_text",
  "corrected_text",
  "original_issue_type",
  "suggested_learning_role",
  "confirmed_learning_role",
  "linked_concept_terms",
  "user_note",
  "requires_user_decision",
  "applied_to_learning_pack",
  "created_at",
  "updated_at"
)) {
  foreach ($item in $items) {
    if (($item.PSObject.Properties.Name -notcontains $field)) {
      throw "Missing decision item field: $field"
    }
  }
}

foreach ($item in $items) {
  if ($item.decision -ne "pending") { throw "Expected all initial decisions to be pending" }
  if ($item.applied_to_learning_pack -ne $false) { throw "Pending decisions must not be applied to learning pack" }
}

$allowedText = (($items | ForEach-Object { $_.allowed_decisions }) -join "`n")
foreach ($expected in @(
  "pending",
  "accepted",
  "edited",
  "ignored",
  "marked_definition",
  "marked_formula",
  "marked_notation",
  "marked_theorem",
  "marked_example",
  "marked_glossary_term",
  "marked_not_relevant"
)) {
  if ($allowedText -notlike "*$expected*") { throw "Missing allowed decision: $expected" }
}

$roles = (($items | ForEach-Object { $_.suggested_learning_role }) -join "`n")
foreach ($expected in @("formula", "definition", "notation", "theorem")) {
  if ($roles -notlike "*$expected*") { throw "Missing expected suggested learning role: $expected" }
}

$moduleText = Get-Content $module -Raw
foreach ($item in @(
  "build_ocr_review_decisions",
  "build_pending_decision",
  "write_ocr_review_decisions",
  "ocr_review_decisions.json",
  "ocr_review_decisions.md",
  "pending_decisions_are_not_verified_evidence",
  "user_corrections_become_verified_evidence",
  "feed_back_into_document_learning_pack",
  "do_not_generate_from_unresolved_blocked_items"
)) {
  if ($moduleText -notlike "*$item*") { throw "Module missing expected text: $item" }
}

$docText = Get-Content $doc -Raw
$docCheckText = $docText.Replace('`', '')
foreach ($item in @(
  "VOILA_V0_7_66_OCR_REVIEW_DECISIONS_ARTIFACT_BUILDER_CHECK=PASS",
  "PASS_DECISIONS_ARTIFACT_BUILDER",
  "OCR Review is user-assisted document learning",
  "ocr_review_decisions.json",
  "ocr_review_decisions.md",
  "decision_count=20",
  "pending_decision_count=20",
  "all_required_decisions_resolved=False",
  "generation_should_wait_for_review=True",
  "pending decisions are not verified evidence",
  "No /generate route change.",
  "No UI implementation.",
  "No build.",
  "No ZIP.",
  "No share.",
  "No delivery.",
  "No distribution.",
  "Tester readiness remains BLOCKED"
)) {
  if ($docCheckText -notlike "*$item*") { throw "Doc missing expected v0.7.66 text: $item" }
}

$webAppText = Get-Content "services/api/web_app.py" -Raw
if ($webAppText -like "*ocr_review_decisions*" -or $webAppText -like "*ocr_review_queue*" -or $webAppText -like "*document_learning_pack*") {
  throw "v0.7.66 must not integrate OCR Review decisions into web_app.py"
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/ocr_review_decisions.py",
  "docs/dev/owner-local-ocr-review-decisions-artifact-builder-no-ui-no-generate-integration-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-ocr-review-decisions-artifact-builder-no-ui-no-generate-integration-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.66: $line"
  }
}

"VOILA_V0_7_66_OCR_REVIEW_DECISIONS_ARTIFACT_BUILDER_CHECK=PASS"
"OCR_REVIEW_DECISIONS_ARTIFACT=PASS"
"REAL_COURSE_DECISION_COUNT=$($decisions.decision_count)"
"PENDING_DECISION_COUNT=$($decisions.pending_decision_count)"
"ALL_REQUIRED_DECISIONS_RESOLVED=False"
"GENERATION_SHOULD_WAIT_FOR_REVIEW=True"
"OCR_REVIEW_IS_USER_ASSISTED_DOCUMENT_LEARNING=True"
"PENDING_DECISIONS_ARE_NOT_VERIFIED_EVIDENCE=True"
"DOCUMENT_LEARNING_PACK_FEEDBACK_LOOP=DEFINED"
"GENERATE_INTEGRATION=NOT_CHANGED"
"UI_IMPLEMENTATION=NOT_CHANGED"
"LESSONS_QUIZ_FLASHCARDS_GLOSSARY=NOT_CHANGED"
"TESTER_READINESS=BLOCKED"
"POLICY=owner_local_ocr_review_decisions_artifact_only_no_ui_no_generate_integration_no_regeneration_no_build_no_zip_no_share_no_delivery_no_distribution"
