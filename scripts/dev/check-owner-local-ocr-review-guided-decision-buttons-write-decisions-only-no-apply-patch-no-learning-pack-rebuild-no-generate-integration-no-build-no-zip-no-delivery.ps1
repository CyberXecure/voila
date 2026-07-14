$ErrorActionPreference = "Stop"

$webApp = "services/api/web_app.py"
$doc = "docs/dev/owner-local-ocr-review-guided-decision-buttons-write-decisions-only-no-apply-patch-no-learning-pack-rebuild-no-generate-integration-no-build-no-zip-no-delivery.md"
$v0771Doc = "docs/dev/owner-local-ocr-review-read-only-page-shell-no-decision-write-no-generate-integration-no-build-no-zip-no-delivery.md"
$htmlBefore = "D:\dev\tester-runs\v0772-ocr-review-buttons\before.html"
$htmlAfter = "D:\dev\tester-runs\v0772-ocr-review-buttons\after.html"
$smokeDecisions = "D:\dev\tester-runs\v0772-ocr-review-buttons\out\03-pag-30-34-vectori-trigonometrie\ocr_review_decisions.json"

foreach ($path in @($webApp, $doc, $v0771Doc, $htmlBefore, $htmlAfter, $smokeDecisions)) {
  if (!(Test-Path $path)) { throw "Missing required v0.7.72 file/evidence: $path" }
}

python -m py_compile $webApp

$text = Get-Content $webApp -Raw
$start = $text.IndexOf("# VOILA_V0_7_72_OWNER_LOCAL_OCR_REVIEW_GUIDED_DECISION_BUTTONS_START")
$end = $text.IndexOf("# VOILA_V0_7_72_OWNER_LOCAL_OCR_REVIEW_GUIDED_DECISION_BUTTONS_END")
if ($start -lt 0 -or $end -lt 0) { throw "Missing v0.7.72 markers in web_app.py" }

$block = $text.Substring($start, $end - $start)

foreach ($item in @(
  "/owner/ocr-review/{course_id}/decision",
  "_voila_owner_ocr_review_guided_decision",
  "_voila_ocr_review_save_guided_decision",
  "VOILA_V0_7_72_OCR_REVIEW_GUIDED_DECISIONS",
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
  "ocr_review_decisions.json",
  "decisions_path.write_text",
  "real_user_decision",
  "owner_local_guided_ui_v0.7.72",
  "applied_to_learning_pack",
  "owner_review_confirmed",
  "generation_should_wait_for_review",
  "owner_review_not_final_confirmed",
  "RedirectResponse",
  "status_code=303"
)) {
  if ($block -notlike "*$item*") { throw "web_app.py v0.7.72 block missing expected text: $item" }
}

foreach ($bad in @(
  "generate_for_pdf(",
  "ocr_review_decision_apply",
  "write_applied_decisions",
  "write_document_learning_pack",
  "build_document_learning_pack",
  "document_learning_pack.py",
  "subprocess",
  "course.cleaned",
  "quiz.json",
  "flashcards.json",
  "glossary.json"
)) {
  if ($block -like "*$bad*") { throw "Forbidden apply/generate/rebuild text in v0.7.72 block: $bad" }
}

$writeTextCount = ([regex]::Matches($block, "\.write_text\(")).Count
if ($writeTextCount -ne 1) { throw "Expected exactly one write_text call in v0.7.72 block, found $writeTextCount" }
if ($block -notlike '*decisions_path.write_text*') { throw "The only write_text call must target decisions_path" }

$htmlBeforeText = Get-Content $htmlBefore -Raw
foreach ($item in @(
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
  "/owner/ocr-review/03-pag-30-34-vectori-trigonometrie/decision",
  "Pending<strong>20</strong>",
  "nu cheamă /generate",
  "Nu aplică patch"
)) {
  if ($htmlBeforeText -notlike "*$item*") { throw "HTML before smoke missing expected text: $item" }
}

$htmlAfterText = Get-Content $htmlAfter -Raw
foreach ($item in @(
  "Pending<strong>19</strong>",
  "Rezolvate<strong>1</strong>",
  "Decizie curentă:</strong> <code>accepted</code>",
  "nu cheamă /generate"
)) {
  if ($htmlAfterText -notlike "*$item*") { throw "HTML after smoke missing expected text: $item" }
}

$decisions = Get-Content $smokeDecisions -Raw | ConvertFrom-Json
$r001 = $decisions.decisions | Where-Object { $_.review_item_id -eq "R001" } | Select-Object -First 1
if (!$r001) { throw "R001 not found in smoke decisions" }
if ($r001.decision -ne "accepted") { throw "R001 decision was not accepted" }
if ($r001.real_user_decision -ne $true) { throw "R001 real_user_decision is not true" }
if ($r001.decision_source -ne "owner_local_guided_ui_v0.7.72") { throw "R001 decision_source mismatch" }
if ($r001.applied_to_learning_pack -ne $false) { throw "R001 applied_to_learning_pack must be false" }
if ($decisions.pending_decision_count -ne 19) { throw "pending_decision_count should be 19" }
if ($decisions.resolved_decision_count -ne 1) { throw "resolved_decision_count should be 1" }
if ($decisions.real_user_decisions_performed -ne $true) { throw "real_user_decisions_performed should be true" }
if ($decisions.owner_review_confirmed -ne $false) { throw "owner_review_confirmed should remain false" }
if ($decisions.quality_gate.generation_should_wait_for_review -ne $true) { throw "generation_should_wait_for_review should remain true" }

$courseDir = Split-Path $smokeDecisions -Parent
foreach ($forbidden in @(
  "ocr_review_decisions.applied.json",
  "ocr_review_decisions.applied.md",
  "document_learning_pack.json",
  "document_learning_pack.md"
)) {
  if (Test-Path (Join-Path $courseDir $forbidden)) { throw "Forbidden output created by v0.7.72 smoke: $forbidden" }
}

$docText = (Get-Content $doc -Raw).Replace('`', '')
foreach ($item in @(
  "VOILA_V0_7_72_OCR_REVIEW_GUIDED_DECISION_BUTTONS_CHECK=PASS",
  "PASS_GUIDED_DECISION_BUTTONS_WRITE_DECISIONS_ONLY",
  "/owner/ocr-review/{course_id}/decision",
  "Write decisions only to ocr_review_decisions.json",
  "Acceptă sugestia",
  "Editează textul",
  "Este formulă",
  "VOILA_V0_7_72_GUIDED_DECISION_BUTTONS_SMOKE=PASS",
  "POST_STATUS=303",
  "DECISION_WRITE_TARGET=ocr_review_decisions.json",
  "UPDATED_REVIEW_ITEM=R001",
  "UPDATED_DECISION=accepted",
  "PENDING_DECISION_COUNT_AFTER=19",
  "RESOLVED_DECISION_COUNT_AFTER=1",
  "REAL_USER_DECISIONS_PERFORMED=True",
  "OWNER_REVIEW_CONFIRMED=False",
  "GENERATION_SHOULD_WAIT_FOR_REVIEW=True",
  "APPLIED_DECISIONS_JSON_CREATED=False",
  "DOCUMENT_LEARNING_PACK_REBUILD=False",
  "GENERATE_INTEGRATION=NOT_CHANGED",
  "No apply patch.",
  "No learning pack rebuild.",
  "No final owner confirmation.",
  "No generation approval.",
  "No /generate integration.",
  "No build.",
  "No ZIP.",
  "No share.",
  "No delivery.",
  "No distribution.",
  "Tester readiness remains BLOCKED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected v0.7.72 text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/web_app.py",
  "docs/dev/owner-local-ocr-review-guided-decision-buttons-write-decisions-only-no-apply-patch-no-learning-pack-rebuild-no-generate-integration-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-ocr-review-guided-decision-buttons-write-decisions-only-no-apply-patch-no-learning-pack-rebuild-no-generate-integration-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.72: $line"
  }
}

"VOILA_V0_7_72_OCR_REVIEW_GUIDED_DECISION_BUTTONS_CHECK=PASS"
"GUIDED_DECISION_BUTTONS=PASS"
"POST_ROUTE=/owner/ocr-review/{course_id}/decision"
"POST_STATUS=303"
"DECISION_WRITE_TARGET=ocr_review_decisions.json"
"UPDATED_REVIEW_ITEM=R001"
"UPDATED_DECISION=accepted"
"PENDING_DECISION_COUNT_AFTER=19"
"RESOLVED_DECISION_COUNT_AFTER=1"
"REAL_USER_DECISIONS_PERFORMED=True"
"OWNER_REVIEW_CONFIRMED=False"
"GENERATION_SHOULD_WAIT_FOR_REVIEW=True"
"APPLIED_DECISIONS_JSON_CREATED=False"
"DOCUMENT_LEARNING_PACK_REBUILD=False"
"GENERATE_INTEGRATION=NOT_CHANGED"
"TESTER_READINESS=BLOCKED"
"POLICY=owner_local_ocr_review_guided_decision_buttons_write_decisions_only_no_apply_patch_no_learning_pack_rebuild_no_generate_integration_no_build_no_zip_no_share_no_delivery_no_distribution"
