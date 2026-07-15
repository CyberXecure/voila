$ErrorActionPreference = "Stop"

Write-Host "v0.7.75 check: start"

$module = "services/api/document_learning_pack_rebuild_from_applied_review.py"
$doc = "docs/dev/owner-local-document-learning-pack-rebuild-from-applied-ocr-review-no-generate-integration-no-build-no-zip-no-delivery.md"
$packJson = "D:\dev\tester-runs\v0775-learning-pack-from-applied-review\out\03-pag-30-34-vectori-trigonometrie\document_learning_pack.json"
$packMd = "D:\dev\tester-runs\v0775-learning-pack-from-applied-review\out\03-pag-30-34-vectori-trigonometrie\document_learning_pack.md"

foreach ($p in @($module, $doc, $packJson, $packMd)) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence: $p" }
}

python -m py_compile $module

$text = Get-Content $module -Raw
foreach ($item in @(
  "VOILA_V0_7_75_OWNER_LOCAL_DOCUMENT_LEARNING_PACK_REBUILD_FROM_APPLIED_OCR_REVIEW_START",
  "AppliedReviewLearningPackError",
  "validate_applied_review_artifact",
  "build_document_learning_pack_from_applied_review",
  "write_document_learning_pack_from_applied_review",
  "ocr_review_decisions.applied.json",
  "document_learning_pack.json",
  "document_learning_pack.md",
  "verified_user_evidence",
  "document_learning_pack_rebuilt_from_applied_ocr_review",
  "generate_integration_changed",
  "course_regeneration_performed"
)) {
  if ($text -notlike "*$item*") { throw "Helper missing expected text: $item" }
}

foreach ($bad in @(
  "FastAPI",
  "@app.",
  "generate_for_pdf(",
  "course.cleaned",
  "quiz.json",
  "flashcards.json",
  "glossary.json"
)) {
  if ($text -like "*$bad*") { throw "Forbidden UI/generate/regeneration text in helper: $bad" }
}

$report = Get-Content $packJson -Raw | ConvertFrom-Json
if ($report.artifact -ne "document_learning_pack") { throw "artifact mismatch" }
if ($report.rebuild_artifact_version -ne "v0.7.75") { throw "rebuild version mismatch" }
if ($report.document_learning_pack_rebuilt_from_applied_ocr_review -ne $true) { throw "rebuild flag mismatch" }
if ($report.quality_gate.concept_count -ne 14) { throw "concept_count mismatch" }
if ($report.quality_gate.review_item_count -ne 20) { throw "review_item_count mismatch" }
if ($report.quality_gate.pending_decision_count -ne 0) { throw "pending_decision_count mismatch" }
if ($report.quality_gate.document_learning_status -ne "PASS") { throw "document_learning_status mismatch" }
if ($report.quality_gate.generation_allowed -ne $true) { throw "generation_allowed mismatch" }
if ($report.quality_gate.verified_user_evidence_count -ne 20) { throw "verified_user_evidence_count mismatch" }
if ($report.quality_gate.generate_integration_enabled -ne $false) { throw "generate_integration_enabled mismatch" }
if ($report.quality_gate.course_regeneration_performed -ne $false) { throw "course_regeneration_performed mismatch" }
if ($report.policy.document_learning_pack_rebuild_performed -ne $true) { throw "pack rebuild policy mismatch" }
if ($report.policy.generate_integration_changed -ne $false) { throw "generate integration policy mismatch" }
if ($report.policy.course_regeneration_performed -ne $false) { throw "course regeneration policy mismatch" }
if ($report.policy.build_performed -ne $false) { throw "build policy mismatch" }
if ($report.policy.zip_created -ne $false) { throw "zip policy mismatch" }
if ($report.policy.delivery_performed -ne $false) { throw "delivery policy mismatch" }

$md = (Get-Content $packMd -Raw).Replace('`', '')
if ($md -notlike "*v0.7.75 Applied OCR Review rebuild*") { throw "markdown v0.7.75 section missing" }
if ($md -notlike "*Verified user evidence count: 20*") { throw "markdown evidence count missing" }
if ($md -notlike "*Generate integration enabled: False*") { throw "markdown no-generate marker missing" }

$docText = (Get-Content $doc -Raw).Replace('`', '')
foreach ($item in @(
  "VOILA_V0_7_75_DOCUMENT_LEARNING_PACK_REBUILD_FROM_APPLIED_OCR_REVIEW_CHECK=PASS",
  "PASS_DOCUMENT_LEARNING_PACK_REBUILD_FROM_APPLIED_OCR_REVIEW",
  "DOCUMENT_LEARNING_STATUS=PASS",
  "GENERATION_ALLOWED_IN_PACK=True",
  "VERIFIED_USER_EVIDENCE_COUNT=20",
  "GENERATE_INTEGRATION=NOT_CHANGED",
  "COURSE_REGENERATION=False",
  "TESTER_READINESS=BLOCKED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/document_learning_pack_rebuild_from_applied_review.py",
  "docs/dev/owner-local-document-learning-pack-rebuild-from-applied-ocr-review-no-generate-integration-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-document-learning-pack-rebuild-from-applied-ocr-review-no-generate-integration-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_75_DOCUMENT_LEARNING_PACK_REBUILD_FROM_APPLIED_OCR_REVIEW_CHECK=PASS"
"DOCUMENT_LEARNING_PACK_REBUILD_FROM_APPLIED_OCR_REVIEW=PASS"
"CONCEPT_COUNT=14"
"REVIEW_ITEM_COUNT=20"
"PENDING_DECISION_COUNT=0"
"DOCUMENT_LEARNING_STATUS=PASS"
"GENERATION_ALLOWED_IN_PACK=True"
"VERIFIED_USER_EVIDENCE_COUNT=20"
"TEACHING_PLAN_STATUS=candidate_ready_for_future_generator"
"DOCUMENT_LEARNING_PACK_REBUILD=True"
"GENERATE_INTEGRATION=NOT_CHANGED"
"COURSE_REGENERATION=False"
"BUILD_PERFORMED=False"
"ZIP_CREATED=False"
"DELIVERY_PERFORMED=False"
"TESTER_READINESS=BLOCKED"
"POLICY=owner_local_document_learning_pack_rebuild_from_applied_ocr_review_no_generate_integration_no_build_no_zip_no_share_no_delivery_no_distribution"
