$ErrorActionPreference = "Stop"

$webApp = "services/api/web_app.py"
$doc = "docs/dev/owner-local-ocr-review-final-confirm-button-no-apply-patch-no-learning-pack-rebuild-no-generate-integration-no-build-no-zip-no-delivery.md"
$v0772Doc = "docs/dev/owner-local-ocr-review-guided-decision-buttons-write-decisions-only-no-apply-patch-no-learning-pack-rebuild-no-generate-integration-no-build-no-zip-no-delivery.md"
$htmlPending = "D:\dev\tester-runs\v0773-ocr-review-confirm\pending-before-confirm.html"
$htmlReady = "D:\dev\tester-runs\v0773-ocr-review-confirm\ready-before-confirm.html"
$htmlAfter = "D:\dev\tester-runs\v0773-ocr-review-confirm\after-confirm.html"
$smokeDecisions = "D:\dev\tester-runs\v0773-ocr-review-confirm\out\03-pag-30-34-vectori-trigonometrie\ocr_review_decisions.json"

foreach ($path in @($webApp, $doc, $v0772Doc, $htmlPending, $htmlReady, $htmlAfter, $smokeDecisions)) {
  if (!(Test-Path $path)) { throw "Missing required v0.7.73 file/evidence: $path" }
}

python -m py_compile $webApp

$text = Get-Content $webApp -Raw
$start = $text.IndexOf("# VOILA_V0_7_73_OWNER_LOCAL_OCR_REVIEW_FINAL_CONFIRM_BUTTON_START")
$end = $text.IndexOf("# VOILA_V0_7_73_OWNER_LOCAL_OCR_REVIEW_FINAL_CONFIRM_BUTTON_END")
if ($start -lt 0 -or $end -lt 0) { throw "Missing v0.7.73 markers in web_app.py" }

$block = $text.Substring($start, $end - $start)

foreach ($item in @(
  "/owner/ocr-review/{course_id}/confirm",
  "_voila_owner_ocr_review_final_confirm",
  "_voila_ocr_review_save_final_confirmation",
  "ocr_review_decisions.json",
  "decisions_path.write_text",
  "owner_review_confirmed",
  "owner_review_confirmed_at",
  "real_user_decisions_performed",
  "final_confirmation_source",
  "owner_local_guided_ui_v0.7.73",
  "pending_decision_count",
  "resolved_decision_count",
  "all_required_decisions_resolved",
  "generation_should_wait_for_review",
  "generate_integration_not_enabled_v0.7.73",
  "RedirectResponse",
  "status_code=303"
)) {
  if ($block -notlike "*$item*") { throw "web_app.py v0.7.73 block missing expected text: $item" }
}

foreach ($item in @(
  "Confirmă OCR Review",
  "Confirmarea finală este blocată",
  "OCR Review confirmat final",
  "/owner/ocr-review/",
  "/confirm",
  "nu aplică patch",
  "nu reconstruiește learning pack",
  "nu cheamă /generate"
)) {
  if ($text -notlike "*$item*") { throw "web_app.py missing expected v0.7.73 UI text: $item" }
}

foreach ($bad in @(
  "generate_for_pdf(",
  "ocr_review_decision_apply",
  "write_applied_decisions",
  "write_document_learning_pack",
  "build_document_learning_pack",
  "subprocess",
  "course.cleaned",
  "quiz.json",
  "flashcards.json",
  "glossary.json"
)) {
  if ($block -like "*$bad*") { throw "Forbidden apply/generate/rebuild text in v0.7.73 block: $bad" }
}

$writeTextCount = ([regex]::Matches($block, "\.write_text\(")).Count
if ($writeTextCount -ne 1) { throw "Expected exactly one write_text call in v0.7.73 block, found $writeTextCount" }
if ($block -notlike '*decisions_path.write_text*') { throw "The only write_text call must target decisions_path" }

$htmlPendingText = Get-Content $htmlPending -Raw
foreach ($item in @(
  "Confirmarea finală este blocată",
  "Mai există <strong>20</strong> decizii pending",
  "Confirmă OCR Review"
)) {
  if ($htmlPendingText -notlike "*$item*") { throw "Pending HTML missing expected text: $item" }
}
if ($htmlPendingText -like "*/owner/ocr-review/03-pag-30-34-vectori-trigonometrie/confirm*") {
  throw "Pending HTML must not expose confirm POST form while pending decisions remain"
}

$htmlReadyText = Get-Content $htmlReady -Raw
foreach ($item in @(
  "/owner/ocr-review/03-pag-30-34-vectori-trigonometrie/confirm",
  "Confirmă OCR Review",
  "Pending<strong>0</strong>",
  "Rezolvate<strong>20</strong>",
  "nu cheamă /generate"
)) {
  if ($htmlReadyText -notlike "*$item*") { throw "Ready HTML missing expected text: $item" }
}

$htmlAfterText = Get-Content $htmlAfter -Raw
foreach ($item in @(
  "OCR Review confirmat final",
  "generarea blocată până la un milestone separat"
)) {
  if ($htmlAfterText -notlike "*$item*") { throw "After-confirm HTML missing expected text: $item" }
}

$decisions = Get-Content $smokeDecisions -Raw | ConvertFrom-Json
if ($decisions.owner_review_confirmed -ne $true) { throw "owner_review_confirmed should be true" }
if (!$decisions.owner_review_confirmed_at) { throw "owner_review_confirmed_at missing" }
if ($decisions.real_user_decisions_performed -ne $true) { throw "real_user_decisions_performed should be true" }
if ($decisions.pending_decision_count -ne 0) { throw "pending_decision_count should be 0" }
if ($decisions.resolved_decision_count -ne 20) { throw "resolved_decision_count should be 20" }
if ($decisions.applied_to_learning_pack -ne $false) { throw "applied_to_learning_pack should remain false" }
if ($decisions.final_confirmation_source -ne "owner_local_guided_ui_v0.7.73") { throw "final_confirmation_source mismatch" }
if ($decisions.quality_gate.owner_review_confirmed -ne $true) { throw "quality_gate.owner_review_confirmed should be true" }
if ($decisions.quality_gate.all_required_decisions_resolved -ne $true) { throw "quality_gate.all_required_decisions_resolved should be true" }
if ($decisions.quality_gate.generation_should_wait_for_review -ne $true) { throw "generation_should_wait_for_review should remain true" }
if ($decisions.quality_gate.generation_block_reason -ne "generate_integration_not_enabled_v0.7.73") { throw "generation_block_reason mismatch" }

$courseDir = Split-Path $smokeDecisions -Parent
foreach ($forbidden in @(
  "ocr_review_decisions.applied.json",
  "ocr_review_decisions.applied.md",
  "document_learning_pack.json",
  "document_learning_pack.md"
)) {
  if (Test-Path (Join-Path $courseDir $forbidden)) { throw "Forbidden output created by v0.7.73 smoke: $forbidden" }
}

$docText = (Get-Content $doc -Raw).Replace('`', '')
foreach ($item in @(
  "VOILA_V0_7_73_OCR_REVIEW_FINAL_CONFIRM_BUTTON_CHECK=PASS",
  "PASS_FINAL_CONFIRM_BUTTON",
  "/owner/ocr-review/{course_id}/confirm",
  "Confirmă OCR Review",
  "owner_review_confirmed=true",
  "generation_should_wait_for_review=true",
  "generate_integration_not_enabled_v0.7.73",
  "VOILA_V0_7_73_FINAL_CONFIRM_BUTTON_SMOKE=PASS",
  "CONFIRM_BLOCKED_WHEN_PENDING=PASS",
  "CONFIRM_READY_WHEN_PENDING_ZERO=PASS",
  "POST_STATUS=303",
  "DECISION_WRITE_TARGET=ocr_review_decisions.json",
  "OWNER_REVIEW_CONFIRMED=True",
  "PENDING_DECISION_COUNT_AFTER=0",
  "RESOLVED_DECISION_COUNT_AFTER=20",
  "APPLIED_DECISIONS_JSON_CREATED=False",
  "DOCUMENT_LEARNING_PACK_REBUILD=False",
  "GENERATE_INTEGRATION=NOT_CHANGED",
  "No apply patch.",
  "No applied decisions artifact.",
  "No learning pack rebuild.",
  "No /generate integration.",
  "No build.",
  "No ZIP.",
  "No share.",
  "No delivery.",
  "No distribution.",
  "Tester readiness remains BLOCKED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected v0.7.73 text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/web_app.py",
  "docs/dev/owner-local-ocr-review-final-confirm-button-no-apply-patch-no-learning-pack-rebuild-no-generate-integration-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-ocr-review-final-confirm-button-no-apply-patch-no-learning-pack-rebuild-no-generate-integration-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.73: $line"
  }
}

"VOILA_V0_7_73_OCR_REVIEW_FINAL_CONFIRM_BUTTON_CHECK=PASS"
"FINAL_CONFIRM_BUTTON=PASS"
"POST_ROUTE=/owner/ocr-review/{course_id}/confirm"
"CONFIRM_BLOCKED_WHEN_PENDING=PASS"
"CONFIRM_READY_WHEN_PENDING_ZERO=PASS"
"POST_STATUS=303"
"DECISION_WRITE_TARGET=ocr_review_decisions.json"
"OWNER_REVIEW_CONFIRMED=True"
"PENDING_DECISION_COUNT_AFTER=0"
"RESOLVED_DECISION_COUNT_AFTER=20"
"GENERATION_SHOULD_WAIT_FOR_REVIEW=True"
"GENERATION_BLOCK_REASON=generate_integration_not_enabled_v0.7.73"
"APPLIED_DECISIONS_JSON_CREATED=False"
"DOCUMENT_LEARNING_PACK_REBUILD=False"
"GENERATE_INTEGRATION=NOT_CHANGED"
"TESTER_READINESS=BLOCKED"
"POLICY=owner_local_ocr_review_final_confirm_button_write_confirm_only_no_apply_patch_no_learning_pack_rebuild_no_generate_integration_no_build_no_zip_no_share_no_delivery_no_distribution"
