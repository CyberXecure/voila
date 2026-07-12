$ErrorActionPreference = "Stop"

$doc = "docs/dev/owner-local-ocr-review-contract-for-document-learning-gate-no-generate-integration-no-build-no-zip-no-delivery.md"
$v0763Doc = "docs/dev/owner-local-document-concepts-real-ocr-coverage-improvement-no-generate-integration-no-build-no-zip-no-delivery.md"

if (!(Test-Path $doc)) { throw "Missing v0.7.64 doc: $doc" }
if (!(Test-Path $v0763Doc)) { throw "Missing v0.7.63 baseline doc: $v0763Doc" }

$docText = Get-Content $doc -Raw
$docCheckText = $docText.Replace('`', '')

foreach ($item in @(
  "VOILA_V0_7_64_OCR_REVIEW_CONTRACT_FOR_DOCUMENT_LEARNING_GATE_CHECK=PASS",
  "PASS_CONTRACT_ONLY",
  "OCR Review is user-assisted document learning",
  "guided OCR Review",
  "ocr_review_queue.json",
  "ocr_review_decisions.json",
  "review_item_id",
  "suggested_learning_role",
  "requires_user_decision",
  "Mark as definition",
  "Mark as formula",
  "Mark as notation",
  "Mark as theorem",
  "Mark as example",
  "user-verified evidence",
  "document_learning_pack.json",
  "The course generator should not use unresolved blocked review items",
  "No /generate route change.",
  "No UI implementation.",
  "No build.",
  "No ZIP.",
  "No share.",
  "No delivery.",
  "No distribution.",
  "Tester readiness remains BLOCKED"
)) {
  if ($docCheckText -notlike "*$item*") { throw "Doc missing expected v0.7.64 text: $item" }
}

$webAppText = Get-Content "services/api/web_app.py" -Raw
if ($webAppText -like "*ocr_review_queue*" -or $webAppText -like "*ocr_review_decisions*" -or $webAppText -like "*document_learning_pack*") {
  throw "v0.7.64 must not integrate OCR Review/document learning pack into web_app.py"
}

$statusLines = git status --short -uall
$allowed = @(
  "docs/dev/owner-local-ocr-review-contract-for-document-learning-gate-no-generate-integration-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-ocr-review-contract-for-document-learning-gate-no-generate-integration-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.64: $line"
  }
}

"VOILA_V0_7_64_OCR_REVIEW_CONTRACT_FOR_DOCUMENT_LEARNING_GATE_CHECK=PASS"
"OCR_REVIEW_CONTRACT=DEFINED"
"OCR_REVIEW_IS_USER_ASSISTED_DOCUMENT_LEARNING=True"
"OCR_REVIEW_QUEUE_ARTIFACT=DEFINED"
"OCR_REVIEW_DECISIONS_ARTIFACT=DEFINED"
"USER_FRIENDLY_REVIEW_REQUIRED=True"
"DOCUMENT_LEARNING_PACK_FEEDBACK_LOOP=DEFINED"
"GENERATE_INTEGRATION=NOT_CHANGED"
"UI_IMPLEMENTATION=NOT_CHANGED"
"LESSONS_QUIZ_FLASHCARDS_GLOSSARY=NOT_CHANGED"
"TESTER_READINESS=BLOCKED"
"POLICY=contract_only_no_generate_integration_no_ui_no_regeneration_no_build_no_zip_no_share_no_delivery_no_distribution"
