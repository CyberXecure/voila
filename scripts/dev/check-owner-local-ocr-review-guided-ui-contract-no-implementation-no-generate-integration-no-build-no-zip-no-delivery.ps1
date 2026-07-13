$ErrorActionPreference = "Stop"

$doc = "docs/dev/owner-local-ocr-review-guided-ui-contract-no-implementation-no-generate-integration-no-build-no-zip-no-delivery.md"
$v0769Doc = "docs/dev/owner-local-ocr-review-user-decision-apply-helper-no-ui-no-generate-integration-no-build-no-zip-no-delivery.md"

$queueModule = "services/api/ocr_review_queue.py"
$decisionsModule = "services/api/ocr_review_decisions.py"
$applyModule = "services/api/ocr_review_decision_apply.py"
$packModule = "services/api/document_learning_pack.py"

if (!(Test-Path $doc)) { throw "Missing v0.7.70 doc: $doc" }
if (!(Test-Path $v0769Doc)) { throw "Missing v0.7.69 baseline doc: $v0769Doc" }

foreach ($p in @($queueModule,$decisionsModule,$applyModule,$packModule)) {
  if (!(Test-Path $p)) { throw "Missing existing artifact module required by UI contract: $p" }
  python -m py_compile $p
}

$docText = Get-Content $doc -Raw
$docCheckText = $docText.Replace('`', '')

foreach ($item in @(
  "VOILA_V0_7_70_OCR_REVIEW_GUIDED_UI_CONTRACT_CHECK=PASS_CONTRACT_ONLY",
  "PASS_CONTRACT_ONLY_NO_IMPLEMENTATION",
  "The user should not edit JSON manually.",
  "No UI is implemented in this milestone.",
  "No /generate integration is implemented in this milestone.",
  "ocr_review_queue.json",
  "ocr_review_decisions.json",
  "ocr_review_decisions.applied.json",
  "document_learning_pack.json",
  "services/api/ocr_review_queue.py",
  "services/api/ocr_review_decisions.py",
  "services/api/ocr_review_decision_apply.py",
  "services/api/document_learning_pack.py",
  "/owner/ocr-review/{course_id}",
  "review item id",
  "source PDF page",
  "issue type",
  "suggested learning role",
  "linked concept terms",
  "corrected text editor",
  "accepted",
  "edited",
  "ignored",
  "marked_definition",
  "marked_formula",
  "marked_notation",
  "marked_theorem",
  "marked_example",
  "marked_glossary_term",
  "marked_not_relevant",
  "Acceptă sugestia",
  "Editează textul",
  "Ignoră",
  "Este definiție",
  "Este formulă",
  "Este notație",
  "Este teoremă",
  "Este exemplu",
  "Este termen de glosar",
  "Nu este relevant",
  "owner_review_confirmed=True",
  "real_user_decisions_performed=True",
  "generation_should_wait_for_review=True",
  "all_required_decisions_resolved=False",
  "generation_should_wait_for_review=False",
  "all_required_decisions_resolved=True",
  "Pending, synthetic, or unconfirmed decisions must not be treated as verified evidence.",
  "missing ocr_review_queue.json",
  "missing ocr_review_decisions.json",
  "recommended future order",
  "Acceptance criteria for a future UI milestone",
  "Contract only.",
  "No UI implementation.",
  "No route implementation.",
  "No /generate route change.",
  "No real user review performed.",
  "No build.",
  "No ZIP.",
  "No share.",
  "No delivery.",
  "No distribution.",
  "Tester readiness remains BLOCKED"
)) {
  if ($docCheckText -notlike "*$item*") { throw "Doc missing expected v0.7.70 text: $item" }
}

$webAppText = Get-Content "services/api/web_app.py" -Raw
if ($webAppText -like "*/owner/ocr-review*" -or $webAppText -like "*ocr_review_decision_apply*" -or $webAppText -like "*ocr_review_decisions.applied*" -or $webAppText -like "*document_learning_pack*") {
  throw "v0.7.70 is contract-only and must not add guided OCR Review UI or integration to web_app.py"
}

$statusLines = git status --short -uall
$allowed = @(
  "docs/dev/owner-local-ocr-review-guided-ui-contract-no-implementation-no-generate-integration-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-ocr-review-guided-ui-contract-no-implementation-no-generate-integration-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.70: $line"
  }
}

"VOILA_V0_7_70_OCR_REVIEW_GUIDED_UI_CONTRACT_CHECK=PASS_CONTRACT_ONLY"
"OCR_REVIEW_GUIDED_UI_CONTRACT=DEFINED"
"USER_SHOULD_NOT_EDIT_JSON_MANUALLY=True"
"OWNER_LOCAL_ROUTE_CONTRACT=/owner/ocr-review/{course_id}"
"REAL_USER_CONFIRMATION_REQUIRED=True"
"OWNER_REVIEW_CONFIRMED_FLAG_REQUIRED=True"
"REAL_USER_DECISIONS_PERFORMED_FLAG_REQUIRED=True"
"GENERATION_GATE_CONTRACT=DEFINED"
"DOCUMENT_LEARNING_PACK_FEEDBACK_CONTRACT=DEFINED"
"UI_IMPLEMENTATION=NOT_CHANGED"
"ROUTE_IMPLEMENTATION=NOT_CHANGED"
"GENERATE_INTEGRATION=NOT_CHANGED"
"REAL_USER_REVIEW_PERFORMED=False"
"TESTER_READINESS=BLOCKED"
"POLICY=contract_only_no_ui_no_route_no_generate_integration_no_regeneration_no_build_no_zip_no_share_no_delivery_no_distribution"
