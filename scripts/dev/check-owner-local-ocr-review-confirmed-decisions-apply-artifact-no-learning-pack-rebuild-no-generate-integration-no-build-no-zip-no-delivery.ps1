$ErrorActionPreference = "Stop"

Write-Host "v0.7.74 check: start"

$module = "services/api/ocr_review_confirmed_apply.py"
$doc = "docs/dev/owner-local-ocr-review-confirmed-decisions-apply-artifact-no-learning-pack-rebuild-no-generate-integration-no-build-no-zip-no-delivery.md"
$appliedJson = "D:\dev\tester-runs\v0774-ocr-review-confirmed-apply\out\03-pag-30-34-vectori-trigonometrie\ocr_review_decisions.applied.json"
$appliedMd = "D:\dev\tester-runs\v0774-ocr-review-confirmed-apply\out\03-pag-30-34-vectori-trigonometrie\ocr_review_decisions.applied.md"

foreach ($p in @($module, $doc, $appliedJson, $appliedMd)) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence: $p" }
}

Write-Host "v0.7.74 check: py_compile"
python -m py_compile $module

Write-Host "v0.7.74 check: helper text"
$text = Get-Content $module -Raw
if ($text -notlike "*VOILA_V0_7_74_OWNER_LOCAL_OCR_REVIEW_CONFIRMED_DECISIONS_APPLY_ARTIFACT_START*") { throw "missing start marker" }
if ($text -notlike "*write_confirmed_decisions_applied_artifacts*") { throw "missing writer function" }
if ($text -notlike "*ocr_review_decisions.applied.json*") { throw "missing applied json text" }
if ($text -notlike "*ocr_review_decisions.applied.md*") { throw "missing applied md text" }
if ($text -like "*generate_for_pdf(*") { throw "forbidden generate_for_pdf" }
if ($text -like "*build_document_learning_pack*") { throw "forbidden learning pack rebuild" }
if ($text -like "*@app.*") { throw "forbidden web route" }

Write-Host "v0.7.74 check: applied json"
$report = Get-Content $appliedJson -Raw | ConvertFrom-Json
if ($report.artifact -ne "ocr_review_confirmed_decisions_applied") { throw "artifact mismatch" }
if ($report.artifact_version -ne "v0.7.74") { throw "artifact_version mismatch" }
if ($report.decision_count -ne 20) { throw "decision_count mismatch" }
if ($report.pending_decision_count -ne 0) { throw "pending_decision_count mismatch" }
if ($report.resolved_decision_count -ne 20) { throw "resolved_decision_count mismatch" }
if ($report.owner_review_confirmed -ne $true) { throw "owner_review_confirmed mismatch" }
if ($report.real_user_decisions_performed -ne $true) { throw "real_user_decisions_performed mismatch" }
if ($report.confirmed_decisions_applied -ne $true) { throw "confirmed_decisions_applied mismatch" }
if ($report.verified_user_evidence_count -ne 20) { throw "verified_user_evidence_count mismatch" }
if ($report.quality_gate.generation_should_wait_for_review -ne $true) { throw "generation_should_wait_for_review mismatch" }
if ($report.quality_gate.generation_block_reason -ne "learning_pack_rebuild_not_enabled_v0.7.74") { throw "generation_block_reason mismatch" }
if ($report.policy.document_learning_pack_rebuild_performed -ne $false) { throw "document_learning_pack_rebuild_performed mismatch" }
if ($report.policy.generate_integration_changed -ne $false) { throw "generate_integration_changed mismatch" }
if ($report.policy.course_regeneration_performed -ne $false) { throw "course_regeneration_performed mismatch" }
if ($report.policy.build_performed -ne $false) { throw "build_performed mismatch" }
if ($report.policy.zip_created -ne $false) { throw "zip_created mismatch" }
if ($report.policy.delivery_performed -ne $false) { throw "delivery_performed mismatch" }
if ($report.policy.distribution_performed -ne $false) { throw "distribution_performed mismatch" }

Write-Host "v0.7.74 check: applied markdown"
$md = (Get-Content $appliedMd -Raw).Replace('`', '')
if ($md -notlike "*# OCR Review Confirmed Decisions Applied*") { throw "markdown title missing" }
if ($md -notlike "*Artifact version: v0.7.74*") { throw "markdown artifact version missing" }
if ($md -notlike "*Decision count: 20*") { throw "markdown decision count missing" }
if ($md -notlike "*Pending decisions: 0*") { throw "markdown pending count missing" }
if ($md -notlike "*Generate integration changed: False*") { throw "markdown no-generate marker missing" }

Write-Host "v0.7.74 check: doc"
$docText = (Get-Content $doc -Raw).Replace('`', '')
if ($docText -notlike "*VOILA_V0_7_74_OCR_REVIEW_CONFIRMED_DECISIONS_APPLY_ARTIFACT_CHECK=PASS*") { throw "doc marker missing" }
if ($docText -notlike "*PENDING_OR_UNCONFIRMED_INPUT_BLOCKED=PASS*") { throw "doc pending block marker missing" }
if ($docText -notlike "*TESTER_READINESS*") { throw "doc tester marker missing" }

Write-Host "v0.7.74 check: git status allowlist"
$statusLines = git status --short -uall
$allowed = @(
  "services/api/ocr_review_confirmed_apply.py",
  "docs/dev/owner-local-ocr-review-confirmed-decisions-apply-artifact-no-learning-pack-rebuild-no-generate-integration-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-ocr-review-confirmed-decisions-apply-artifact-no-learning-pack-rebuild-no-generate-integration-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_74_OCR_REVIEW_CONFIRMED_DECISIONS_APPLY_ARTIFACT_CHECK=PASS"
"CONFIRMED_DECISIONS_APPLY_ARTIFACT=PASS"
"PENDING_OR_UNCONFIRMED_INPUT_BLOCKED=PASS"
"APPLIED_JSON_CREATED=True"
"APPLIED_MD_CREATED=True"
"DECISION_COUNT=20"
"PENDING_DECISION_COUNT=0"
"RESOLVED_DECISION_COUNT=20"
"OWNER_REVIEW_CONFIRMED=True"
"REAL_USER_DECISIONS_PERFORMED=True"
"CONFIRMED_DECISIONS_APPLIED=True"
"VERIFIED_USER_EVIDENCE_COUNT=20"
"GENERATION_SHOULD_WAIT_FOR_REVIEW=True"
"GENERATION_BLOCK_REASON=learning_pack_rebuild_not_enabled_v0.7.74"
"DOCUMENT_LEARNING_PACK_REBUILD=False"
"GENERATE_INTEGRATION=NOT_CHANGED"
"COURSE_REGENERATION=False"
"TESTER_READINESS=BLOCKED"
"POLICY=owner_local_ocr_review_confirmed_decisions_apply_artifact_no_learning_pack_rebuild_no_generate_integration_no_build_no_zip_no_share_no_delivery_no_distribution"
