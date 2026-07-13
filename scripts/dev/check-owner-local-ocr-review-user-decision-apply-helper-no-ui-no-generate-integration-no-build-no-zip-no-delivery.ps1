$ErrorActionPreference = "Stop"

$module = "services/api/ocr_review_decision_apply.py"
$doc = "docs/dev/owner-local-ocr-review-user-decision-apply-helper-no-ui-no-generate-integration-no-build-no-zip-no-delivery.md"
$v0768Doc = "docs/dev/owner-local-ocr-review-resolved-decisions-fixture-and-learning-pack-pass-smoke-no-ui-no-generate-integration-no-build-no-zip-no-delivery.md"

$appliedJson = "D:\dev\tester-runs\voila-v0.7.69-owner-local-ocr-review-user-decision-apply-helper-no-ui-no-generate-integration-no-build-no-zip-no-delivery\applied-decisions-smoke\ocr_review_decisions.applied.json"
$appliedMd = "D:\dev\tester-runs\voila-v0.7.69-owner-local-ocr-review-user-decision-apply-helper-no-ui-no-generate-integration-no-build-no-zip-no-delivery\applied-decisions-smoke\ocr_review_decisions.applied.md"
$patchJson = "D:\dev\tester-runs\voila-v0.7.69-owner-local-ocr-review-user-decision-apply-helper-no-ui-no-generate-integration-no-build-no-zip-no-delivery\decision-patch\ocr_review_user_decision_patch.unconfirmed-smoke.json"

if (!(Test-Path $module)) { throw "Missing module: $module" }
if (!(Test-Path $doc)) { throw "Missing v0.7.69 doc: $doc" }
if (!(Test-Path $v0768Doc)) { throw "Missing v0.7.68 baseline doc: $v0768Doc" }
if (!(Test-Path $appliedJson)) { throw "Missing applied decisions JSON evidence: $appliedJson" }
if (!(Test-Path $appliedMd)) { throw "Missing applied decisions MD evidence: $appliedMd" }
if (!(Test-Path $patchJson)) { throw "Missing decision patch smoke evidence: $patchJson" }

python -m py_compile $module

$applied = Get-Content $appliedJson -Raw | ConvertFrom-Json
$patch = Get-Content $patchJson -Raw | ConvertFrom-Json

if ($applied.artifact -ne "ocr_review_decisions") { throw "Unexpected artifact name" }
if ([int]$applied.decision_count -ne 20) { throw "Expected decision_count=20" }
if ([int]$applied.applied_patch_decision_count -ne 3) { throw "Expected applied_patch_decision_count=3" }
if ([int]$applied.pending_decision_count -ne 17) { throw "Expected pending_decision_count=17" }
if ([int]$applied.resolved_decision_count -ne 3) { throw "Expected resolved_decision_count=3" }
if ($applied.quality_gate.all_required_decisions_resolved -ne $false) { throw "Expected all_required_decisions_resolved=False" }
if ($applied.quality_gate.generation_should_wait_for_review -ne $true) { throw "Expected generation_should_wait_for_review=True" }
if ($applied.decision_patch.real_user_decisions_performed -ne $false) { throw "Expected real_user_decisions_performed=False" }
if ($applied.decision_patch.synthetic_or_unconfirmed_patch -ne $true) { throw "Expected synthetic_or_unconfirmed_patch=True" }
if ($applied.quality_gate.synthetic_or_unconfirmed_patch -ne $true) { throw "Expected quality gate synthetic_or_unconfirmed_patch=True" }

if ($applied.learning_policy.ocr_review_is_user_assisted_document_learning -ne $true) { throw "Expected OCR Review learning policy" }
if ($applied.learning_policy.user_corrections_become_verified_evidence -ne $false) { throw "Expected unconfirmed patch not to become verified evidence" }
if ($applied.learning_policy.synthetic_or_unconfirmed_patch_is_not_verified_evidence -ne $true) { throw "Expected synthetic/unconfirmed patch evidence policy" }
if ($applied.learning_policy.real_user_review_required_for_actual_delivery -ne $true) { throw "Expected real user review required policy" }
if ($applied.learning_policy.pending_decisions_are_not_verified_evidence -ne $true) { throw "Expected pending decisions policy" }

if ($applied.policy.no_ui_implementation -ne $true) { throw "Expected no UI implementation policy" }
if ($applied.policy.no_generate_integration -ne $true) { throw "Expected no generate integration policy" }
if ($applied.policy.no_build -ne $true) { throw "Expected no build policy" }
if ($applied.policy.no_zip -ne $true) { throw "Expected no ZIP policy" }
if ($applied.policy.no_delivery -ne $true) { throw "Expected no delivery policy" }
if ($applied.policy.no_distribution -ne $true) { throw "Expected no distribution policy" }

if ($patch.owner_review_confirmed -ne $false) { throw "Expected smoke patch owner_review_confirmed=False" }
if ($patch.real_user_decisions_performed -ne $false) { throw "Expected smoke patch real_user_decisions_performed=False" }
if ($patch.synthetic_or_unconfirmed_patch -ne $true) { throw "Expected smoke patch synthetic_or_unconfirmed_patch=True" }
if ($patch.must_not_be_used_for_real_generation -ne $true) { throw "Expected smoke patch must_not_be_used_for_real_generation=True" }

$items = @($applied.decisions)
if ($items.Count -ne 20) { throw "Expected 20 decision items" }

$patched = @($items | Where-Object { $_.review_item_id -in @("R001","R003","R020") })
if ($patched.Count -ne 3) { throw "Expected 3 patched decisions" }

foreach ($item in $patched) {
  if ($item.requires_user_decision -ne $false) { throw "Expected patched item requires_user_decision=False" }
  if ($item.applied_to_learning_pack -ne $true) { throw "Expected patched item applied_to_learning_pack=True" }
  if ($item.decision_source -ne "owner_local_synthetic_or_unconfirmed_patch") { throw "Expected unconfirmed decision source" }
  if ($item.real_user_decision -ne $false) { throw "Expected patched item real_user_decision=False" }
  if ($item.fixture_only_not_real_user_decision -ne $true) { throw "Expected patched item fixture_only_not_real_user_decision=True" }
}

$pending = @($items | Where-Object { $_.decision -eq "pending" })
if ($pending.Count -ne 17) { throw "Expected 17 pending decisions" }

foreach ($item in $pending) {
  if ($item.requires_user_decision -ne $true) { throw "Expected pending item requires_user_decision=True" }
  if ($item.applied_to_learning_pack -ne $false) { throw "Expected pending item applied_to_learning_pack=False" }
}

$r001 = $items | Where-Object { $_.review_item_id -eq "R001" } | Select-Object -First 1
$r003 = $items | Where-Object { $_.review_item_id -eq "R003" } | Select-Object -First 1
$r020 = $items | Where-Object { $_.review_item_id -eq "R020" } | Select-Object -First 1

if ($r001.decision -ne "accepted") { throw "Expected R001 accepted" }
if ($r003.decision -ne "marked_definition") { throw "Expected R003 marked_definition" }
if ($r020.decision -ne "marked_formula") { throw "Expected R020 marked_formula" }
if ($r003.corrected_text -ne "În caz contrar se numesc necoliniari.") { throw "Expected R003 corrected text" }

$moduleText = Get-Content $module -Raw
foreach ($item in @(
  "apply_decision_patch",
  "write_applied_decisions",
  "ocr_review_decisions.applied.json",
  "ocr_review_decisions.applied.md",
  "owner_review_confirmed",
  "real_user_decisions_performed",
  "synthetic_or_unconfirmed_patch",
  "owner_user_decision_patch",
  "owner_local_synthetic_or_unconfirmed_patch",
  "DecisionPatchError"
)) {
  if ($moduleText -notlike "*$item*") { throw "Module missing expected text: $item" }
}

$docText = Get-Content $doc -Raw
$docCheckText = $docText.Replace('`', '')
foreach ($item in @(
  "VOILA_V0_7_69_OCR_REVIEW_USER_DECISION_APPLY_HELPER_CHECK=PASS_UNCONFIRMED_PATCH_SMOKE",
  "PASS_UNCONFIRMED_PATCH_SMOKE",
  "ocr_review_decisions.applied.json",
  "ocr_review_decisions.applied.md",
  "OCR_REVIEW_USER_DECISION_APPLY_HELPER=PASS",
  "decision_count=20",
  "applied_patch_decision_count=3",
  "pending_decision_count=17",
  "resolved_decision_count=3",
  "all_required_decisions_resolved=False",
  "generation_should_wait_for_review=True",
  "real_user_decisions_performed=False",
  "synthetic_or_unconfirmed_patch=True",
  "Synthetic or unconfirmed patches are not verified user evidence.",
  "No /generate route change.",
  "No UI implementation.",
  "No real user review performed in the smoke.",
  "No real generation approval.",
  "No build.",
  "No ZIP.",
  "No share.",
  "No delivery.",
  "No distribution.",
  "Tester readiness remains BLOCKED"
)) {
  if ($docCheckText -notlike "*$item*") { throw "Doc missing expected v0.7.69 text: $item" }
}

$webAppText = Get-Content "services/api/web_app.py" -Raw
if ($webAppText -like "*ocr_review_decision_apply*" -or $webAppText -like "*ocr_review_decisions.applied*" -or $webAppText -like "*document_learning_pack*") {
  throw "v0.7.69 must not integrate decision apply helper into web_app.py"
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/ocr_review_decision_apply.py",
  "docs/dev/owner-local-ocr-review-user-decision-apply-helper-no-ui-no-generate-integration-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-ocr-review-user-decision-apply-helper-no-ui-no-generate-integration-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.69: $line"
  }
}

"VOILA_V0_7_69_OCR_REVIEW_USER_DECISION_APPLY_HELPER_CHECK=PASS_UNCONFIRMED_PATCH_SMOKE"
"OCR_REVIEW_USER_DECISION_APPLY_HELPER=PASS"
"DECISION_COUNT=20"
"APPLIED_PATCH_DECISION_COUNT=3"
"PENDING_DECISION_COUNT=17"
"RESOLVED_DECISION_COUNT=3"
"ALL_REQUIRED_DECISIONS_RESOLVED=False"
"GENERATION_SHOULD_WAIT_FOR_REVIEW=True"
"REAL_USER_DECISIONS_PERFORMED=False"
"SYNTHETIC_OR_UNCONFIRMED_PATCH=True"
"PATCHED_ITEMS=R001_R003_R020"
"GENERATE_INTEGRATION=NOT_CHANGED"
"UI_IMPLEMENTATION=NOT_CHANGED"
"LESSONS_QUIZ_FLASHCARDS_GLOSSARY=NOT_CHANGED"
"TESTER_READINESS=BLOCKED"
"POLICY=owner_local_ocr_review_decision_apply_helper_only_no_ui_no_generate_integration_no_regeneration_no_build_no_zip_no_share_no_delivery_no_distribution"
