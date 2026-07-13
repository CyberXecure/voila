$ErrorActionPreference = "Stop"

$module = "services/api/document_learning_pack.py"
$doc = "docs/dev/owner-local-document-learning-pack-builder-from-concepts-and-review-artifacts-no-generate-integration-no-build-no-zip-no-delivery.md"
$v0766Doc = "docs/dev/owner-local-ocr-review-decisions-artifact-builder-no-ui-no-generate-integration-no-build-no-zip-no-delivery.md"
$packJson = "D:\dev\tester-runs\voila-v0.7.67-owner-local-document-learning-pack-builder-from-concepts-and-review-artifacts-no-generate-integration-no-build-no-zip-no-delivery\real-course-document-learning-pack-after-review-link\document_learning_pack.json"
$packMd = "D:\dev\tester-runs\voila-v0.7.67-owner-local-document-learning-pack-builder-from-concepts-and-review-artifacts-no-generate-integration-no-build-no-zip-no-delivery\real-course-document-learning-pack-after-review-link\document_learning_pack.md"

if (!(Test-Path $module)) { throw "Missing module: $module" }
if (!(Test-Path $doc)) { throw "Missing v0.7.67 doc: $doc" }
if (!(Test-Path $v0766Doc)) { throw "Missing v0.7.66 baseline doc: $v0766Doc" }
if (!(Test-Path $packJson)) { throw "Missing real-course document learning pack JSON evidence: $packJson" }
if (!(Test-Path $packMd)) { throw "Missing real-course document learning pack MD evidence: $packMd" }

python -m py_compile $module

$pack = Get-Content $packJson -Raw | ConvertFrom-Json

if ($pack.artifact -ne "document_learning_pack") { throw "Unexpected artifact name" }
if ([int]$pack.source_page_count -ne 5) { throw "Expected source_page_count=5" }
if ([int]$pack.quality_gate.concept_count -ne 14) { throw "Expected concept_count=14" }
if ([int]$pack.quality_gate.review_item_count -ne 20) { throw "Expected review_item_count=20" }
if ([int]$pack.quality_gate.pending_decision_count -ne 20) { throw "Expected pending_decision_count=20" }
if ($pack.quality_gate.document_learning_status -ne "OCR_REVIEW_PENDING_BLOCKED") { throw "Expected OCR_REVIEW_PENDING_BLOCKED" }
if ($pack.quality_gate.generation_allowed -ne $false) { throw "Expected generation_allowed=False" }

if ($pack.learning_policy.learn_document_before_teaching -ne $true) { throw "Expected learn-document-before-teaching policy" }
if ($pack.learning_policy.ocr_review_is_user_assisted_document_learning -ne $true) { throw "Expected OCR Review learning policy" }
if ($pack.learning_policy.user_corrections_become_verified_evidence -ne $true) { throw "Expected user corrections verified evidence policy" }
if ($pack.learning_policy.pending_decisions_are_not_verified_evidence -ne $true) { throw "Expected pending decisions not verified evidence policy" }
if ($pack.learning_policy.do_not_generate_from_unresolved_blocked_items -ne $true) { throw "Expected unresolved blocked items policy" }

if ($pack.policy.no_ui_implementation -ne $true) { throw "Expected no UI implementation policy" }
if ($pack.policy.no_generate_integration -ne $true) { throw "Expected no generate integration policy" }
if ($pack.policy.no_build -ne $true) { throw "Expected no build policy" }
if ($pack.policy.no_zip -ne $true) { throw "Expected no ZIP policy" }
if ($pack.policy.no_delivery -ne $true) { throw "Expected no delivery policy" }
if ($pack.policy.no_distribution -ne $true) { throw "Expected no distribution policy" }

$concepts = @($pack.concept_summary.concepts)
if ($concepts.Count -ne 14) { throw "Expected 14 concepts in learning pack" }

$terms = (($concepts | ForEach-Object { $_.term }) -join "`n").ToLowerInvariant()
foreach ($term in @(
  "segment orientat",
  "vector",
  "modul",
  "direcție",
  "vectori egali",
  "vectori opuși",
  "vectori coliniari",
  "vectori necoliniari",
  "bază",
  "coordonatele vectorului",
  "versorii axelor de coordonate",
  "bază ortonormată",
  "produsul scalar",
  "funcții trigonometrice"
)) {
  if ($terms -notlike "*$term*") { throw "Missing learning pack concept: $term" }
}

$reviewLinkedTerms = (($pack.ocr_review_summary.review_linked_concept_terms) -join "`n").ToLowerInvariant()
foreach ($term in @(
  "vector",
  "modul",
  "vectori necoliniari",
  "coordonatele vectorului",
  "versorii axelor de coordonate",
  "produsul scalar",
  "funcții trigonometrice"
)) {
  if ($reviewLinkedTerms -notlike "*$term*") { throw "Missing review-linked concept term: $term" }
}

foreach ($term in @(
  "vector",
  "modul",
  "vectori necoliniari",
  "coordonatele vectorului",
  "versorii axelor de coordonate",
  "produsul scalar",
  "funcții trigonometrice"
)) {
  $row = $concepts | Where-Object { $_.term -eq $term } | Select-Object -First 1
  if ($null -eq $row) { throw "Missing concept row for review flag: $term" }
  if ($row.needs_review_before_generation -ne $true) { throw "Expected needs_review_before_generation=True for $term" }
}

if ($pack.teaching_plan.teaching_plan_status -ne "blocked_until_review_resolved") { throw "Expected blocked teaching plan status" }
if (@($pack.teaching_plan.lesson_sequence_candidates).Count -lt 10) { throw "Expected lesson sequence candidates" }
if (@($pack.teaching_plan.glossary_candidates).Count -lt 10) { throw "Expected glossary candidates" }
if (@($pack.teaching_plan.flashcard_candidates).Count -lt 10) { throw "Expected flashcard candidates" }
if (@($pack.teaching_plan.quiz_candidates).Count -lt 10) { throw "Expected quiz candidates" }

$moduleText = Get-Content $module -Raw
foreach ($item in @(
  "build_document_learning_pack",
  "write_document_learning_pack",
  "document_learning_pack.json",
  "document_learning_pack.md",
  "OCR_REVIEW_PENDING_BLOCKED",
  "pending_review_terms",
  "needs_review_before_generation",
  "learn_document_before_teaching",
  "pending_decisions_are_not_verified_evidence",
  "do_not_generate_from_unresolved_blocked_items"
)) {
  if ($moduleText -notlike "*$item*") { throw "Module missing expected text: $item" }
}

$docText = Get-Content $doc -Raw
$docCheckText = $docText.Replace('`', '')
foreach ($item in @(
  "VOILA_V0_7_67_DOCUMENT_LEARNING_PACK_BUILDER_CHECK=PASS_BLOCKED_BY_PENDING_REVIEW",
  "PASS_DOCUMENT_LEARNING_PACK_BUILDER_BLOCKED_BY_PENDING_REVIEW",
  "document_learning_pack.json",
  "document_learning_pack.md",
  "concept_count=14",
  "review_item_count=20",
  "pending_decision_count=20",
  "document_learning_status=OCR_REVIEW_PENDING_BLOCKED",
  "generation_allowed=False",
  "needs_review_before_generation=True",
  "Pending OCR Review decisions are not verified evidence",
  "No /generate route change.",
  "No UI implementation.",
  "No build.",
  "No ZIP.",
  "No share.",
  "No delivery.",
  "No distribution.",
  "Tester readiness remains BLOCKED"
)) {
  if ($docCheckText -notlike "*$item*") { throw "Doc missing expected v0.7.67 text: $item" }
}

$webAppText = Get-Content "services/api/web_app.py" -Raw
if ($webAppText -like "*document_learning_pack*" -or $webAppText -like "*ocr_review_decisions*" -or $webAppText -like "*ocr_review_queue*") {
  throw "v0.7.67 must not integrate document learning pack into web_app.py"
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/document_learning_pack.py",
  "docs/dev/owner-local-document-learning-pack-builder-from-concepts-and-review-artifacts-no-generate-integration-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-document-learning-pack-builder-from-concepts-and-review-artifacts-no-generate-integration-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.67: $line"
  }
}

"VOILA_V0_7_67_DOCUMENT_LEARNING_PACK_BUILDER_CHECK=PASS_BLOCKED_BY_PENDING_REVIEW"
"DOCUMENT_LEARNING_PACK_ARTIFACT=PASS"
"REAL_COURSE_CONCEPT_COUNT=14"
"REAL_COURSE_REVIEW_ITEM_COUNT=20"
"PENDING_DECISION_COUNT=20"
"DOCUMENT_LEARNING_STATUS=OCR_REVIEW_PENDING_BLOCKED"
"GENERATION_ALLOWED=False"
"REVIEW_LINKED_CONCEPTS=PASS"
"TEACHING_PLAN_CANDIDATES=BLOCKED_UNTIL_REVIEW_RESOLVED"
"GENERATE_INTEGRATION=NOT_CHANGED"
"UI_IMPLEMENTATION=NOT_CHANGED"
"LESSONS_QUIZ_FLASHCARDS_GLOSSARY=NOT_CHANGED"
"TESTER_READINESS=BLOCKED"
"POLICY=owner_local_document_learning_pack_artifact_only_no_ui_no_generate_integration_no_regeneration_no_build_no_zip_no_share_no_delivery_no_distribution"
