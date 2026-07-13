$ErrorActionPreference = "Stop"

$fixtureBuilder = "scripts/dev/build-ocr-review-resolved-decisions-fixture.py"
$packModule = "services/api/document_learning_pack.py"
$doc = "docs/dev/owner-local-ocr-review-resolved-decisions-fixture-and-learning-pack-pass-smoke-no-ui-no-generate-integration-no-build-no-zip-no-delivery.md"
$v0767Doc = "docs/dev/owner-local-document-learning-pack-builder-from-concepts-and-review-artifacts-no-generate-integration-no-build-no-zip-no-delivery.md"

$fixtureJson = "D:\dev\tester-runs\voila-v0.7.68-owner-local-ocr-review-resolved-decisions-fixture-and-learning-pack-pass-smoke-no-ui-no-generate-integration-no-build-no-zip-no-delivery\resolved-decisions-fixture\ocr_review_decisions.resolved-fixture.json"
$fixtureMd = "D:\dev\tester-runs\voila-v0.7.68-owner-local-ocr-review-resolved-decisions-fixture-and-learning-pack-pass-smoke-no-ui-no-generate-integration-no-build-no-zip-no-delivery\resolved-decisions-fixture\ocr_review_decisions.resolved-fixture.md"
$packJson = "D:\dev\tester-runs\voila-v0.7.68-owner-local-ocr-review-resolved-decisions-fixture-and-learning-pack-pass-smoke-no-ui-no-generate-integration-no-build-no-zip-no-delivery\document-learning-pack-pass-smoke\document_learning_pack.json"
$packMd = "D:\dev\tester-runs\voila-v0.7.68-owner-local-ocr-review-resolved-decisions-fixture-and-learning-pack-pass-smoke-no-ui-no-generate-integration-no-build-no-zip-no-delivery\document-learning-pack-pass-smoke\document_learning_pack.md"

if (!(Test-Path $fixtureBuilder)) { throw "Missing fixture builder: $fixtureBuilder" }
if (!(Test-Path $packModule)) { throw "Missing document learning pack module: $packModule" }
if (!(Test-Path $doc)) { throw "Missing v0.7.68 doc: $doc" }
if (!(Test-Path $v0767Doc)) { throw "Missing v0.7.67 baseline doc: $v0767Doc" }
if (!(Test-Path $fixtureJson)) { throw "Missing resolved fixture JSON evidence: $fixtureJson" }
if (!(Test-Path $fixtureMd)) { throw "Missing resolved fixture MD evidence: $fixtureMd" }
if (!(Test-Path $packJson)) { throw "Missing learning pack PASS smoke JSON evidence: $packJson" }
if (!(Test-Path $packMd)) { throw "Missing learning pack PASS smoke MD evidence: $packMd" }

python -m py_compile $packModule $fixtureBuilder

$fixture = Get-Content $fixtureJson -Raw | ConvertFrom-Json
$pack = Get-Content $packJson -Raw | ConvertFrom-Json

if ($fixture.artifact -ne "ocr_review_decisions") { throw "Unexpected fixture artifact" }
if ([int]$fixture.decision_count -ne 20) { throw "Expected fixture decision_count=20" }
if ([int]$fixture.pending_decision_count -ne 0) { throw "Expected fixture pending_decision_count=0" }
if ([int]$fixture.resolved_decision_count -ne 20) { throw "Expected fixture resolved_decision_count=20" }
if ($fixture.quality_gate.all_required_decisions_resolved -ne $true) { throw "Expected all_required_decisions_resolved=True" }
if ($fixture.quality_gate.generation_should_wait_for_review -ne $false) { throw "Expected generation_should_wait_for_review=False" }
if ($fixture.fixture.fixture_only -ne $true) { throw "Expected fixture_only=True" }
if ($fixture.fixture.real_user_decisions_performed -ne $false) { throw "Expected real_user_decisions_performed=False" }
if ($fixture.fixture.must_not_be_used_for_real_generation -ne $true) { throw "Expected must_not_be_used_for_real_generation=True" }

$fixtureItems = @($fixture.decisions)
if ($fixtureItems.Count -ne 20) { throw "Expected 20 fixture decisions" }
foreach ($item in $fixtureItems) {
  if ($item.decision -ne "accepted") { throw "Expected synthetic fixture decision accepted" }
  if ($item.requires_user_decision -ne $false) { throw "Expected fixture requires_user_decision=False" }
  if ($item.applied_to_learning_pack -ne $true) { throw "Expected fixture applied_to_learning_pack=True" }
  if ($item.fixture_only_not_real_user_decision -ne $true) { throw "Expected fixture_only_not_real_user_decision=True" }
  if ($item.decision_source -ne "synthetic_resolved_fixture") { throw "Expected synthetic_resolved_fixture decision source" }
}

if ($pack.artifact -ne "document_learning_pack") { throw "Unexpected pack artifact" }
if ([int]$pack.quality_gate.concept_count -ne 14) { throw "Expected concept_count=14" }
if ([int]$pack.quality_gate.review_item_count -ne 20) { throw "Expected review_item_count=20" }
if ([int]$pack.quality_gate.pending_decision_count -ne 0) { throw "Expected pending_decision_count=0" }
if ($pack.quality_gate.document_learning_status -ne "PASS") { throw "Expected document_learning_status=PASS" }
if ($pack.quality_gate.generation_allowed -ne $true) { throw "Expected generation_allowed=True in fixture smoke" }
if ($pack.quality_gate.decisions_fixture_only -ne $true) { throw "Expected decisions_fixture_only=True" }
if ($pack.quality_gate.real_user_decisions_performed -ne $false) { throw "Expected real_user_decisions_performed=False" }

if ($pack.verified_user_evidence.verified_decision_count -ne 0) { throw "Expected no verified user evidence from fixture" }
if ($pack.learning_policy.synthetic_fixture_not_real_user_evidence -ne $true) { throw "Expected synthetic fixture not real user evidence policy" }
if ($pack.learning_policy.real_user_review_required_for_actual_delivery -ne $true) { throw "Expected real user review required policy" }
if ($pack.learning_policy.pending_decisions_are_not_verified_evidence -ne $true) { throw "Expected pending decisions not verified evidence policy" }

$concepts = @($pack.concept_summary.concepts)
if ($concepts.Count -ne 14) { throw "Expected 14 concepts" }
foreach ($concept in $concepts) {
  if ($concept.needs_review_before_generation -ne $false) {
    throw "Resolved fixture smoke should clear needs_review_before_generation flags"
  }
}

if ($pack.policy.no_ui_implementation -ne $true) { throw "Expected no UI implementation policy" }
if ($pack.policy.no_generate_integration -ne $true) { throw "Expected no generate integration policy" }
if ($pack.policy.no_build -ne $true) { throw "Expected no build policy" }
if ($pack.policy.no_zip -ne $true) { throw "Expected no ZIP policy" }
if ($pack.policy.no_delivery -ne $true) { throw "Expected no delivery policy" }
if ($pack.policy.no_distribution -ne $true) { throw "Expected no distribution policy" }

$fixtureBuilderText = Get-Content $fixtureBuilder -Raw
foreach ($item in @(
  "build_resolved_fixture",
  "ocr_review_decisions.resolved-fixture.json",
  "fixture_only",
  "real_user_decisions_performed",
  "must_not_be_used_for_real_generation",
  "fixture_only_not_real_user_decision",
  "synthetic_resolved_fixture"
)) {
  if ($fixtureBuilderText -notlike "*$item*") { throw "Fixture builder missing expected text: $item" }
}

$packModuleText = Get-Content $packModule -Raw
foreach ($item in @(
  "fixture_only_not_real_user_decision",
  "decisions_fixture_only",
  "real_user_decisions_performed",
  "synthetic_fixture_not_real_user_evidence",
  "real_user_review_required_for_actual_delivery",
  "pending_review_terms"
)) {
  if ($packModuleText -notlike "*$item*") { throw "Pack module missing expected v0.7.68 hardening text: $item" }
}

$docText = Get-Content $doc -Raw
$docCheckText = $docText.Replace('`', '')
foreach ($item in @(
  "VOILA_V0_7_68_RESOLVED_DECISIONS_FIXTURE_AND_LEARNING_PACK_PASS_SMOKE_CHECK=PASS_SYNTHETIC_FIXTURE_ONLY",
  "PASS_WITH_SYNTHETIC_FIXTURE_ONLY",
  "OCR_REVIEW_RESOLVED_DECISIONS_FIXTURE=PASS",
  "DOCUMENT_LEARNING_PACK_ARTIFACT=PASS",
  "decision_count=20",
  "pending_decision_count=0",
  "resolved_decision_count=20",
  "document_learning_status=PASS",
  "generation_allowed=True",
  "decisions_fixture_only=True",
  "real_user_decisions_performed=False",
  "verified_decision_count=0",
  "It is not a real user decision artifact.",
  "Must not be used for real generation.",
  "No /generate route change.",
  "No UI implementation.",
  "No real user review performed.",
  "No real generation approval.",
  "No build.",
  "No ZIP.",
  "No share.",
  "No delivery.",
  "No distribution.",
  "Tester readiness remains BLOCKED"
)) {
  if ($docCheckText -notlike "*$item*") { throw "Doc missing expected v0.7.68 text: $item" }
}

$webAppText = Get-Content "services/api/web_app.py" -Raw
if ($webAppText -like "*document_learning_pack*" -or $webAppText -like "*ocr_review_decisions*" -or $webAppText -like "*ocr_review_queue*") {
  throw "v0.7.68 must not integrate fixture or learning pack into web_app.py"
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/document_learning_pack.py",
  "scripts/dev/build-ocr-review-resolved-decisions-fixture.py",
  "docs/dev/owner-local-ocr-review-resolved-decisions-fixture-and-learning-pack-pass-smoke-no-ui-no-generate-integration-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-ocr-review-resolved-decisions-fixture-and-learning-pack-pass-smoke-no-ui-no-generate-integration-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.68: $line"
  }
}

"VOILA_V0_7_68_RESOLVED_DECISIONS_FIXTURE_AND_LEARNING_PACK_PASS_SMOKE_CHECK=PASS_SYNTHETIC_FIXTURE_ONLY"
"OCR_REVIEW_RESOLVED_DECISIONS_FIXTURE=PASS"
"FIXTURE_DECISION_COUNT=20"
"FIXTURE_PENDING_DECISION_COUNT=0"
"FIXTURE_RESOLVED_DECISION_COUNT=20"
"FIXTURE_ONLY=True"
"REAL_USER_DECISIONS_PERFORMED=False"
"DOCUMENT_LEARNING_PACK_ARTIFACT=PASS"
"REAL_COURSE_CONCEPT_COUNT=14"
"REAL_COURSE_REVIEW_ITEM_COUNT=20"
"PACK_PENDING_DECISION_COUNT=0"
"DOCUMENT_LEARNING_STATUS=PASS"
"GENERATION_ALLOWED=True"
"DECISIONS_FIXTURE_ONLY=True"
"VERIFIED_USER_EVIDENCE_COUNT=0"
"GENERATE_INTEGRATION=NOT_CHANGED"
"UI_IMPLEMENTATION=NOT_CHANGED"
"LESSONS_QUIZ_FLASHCARDS_GLOSSARY=NOT_CHANGED"
"TESTER_READINESS=BLOCKED"
"POLICY=synthetic_fixture_smoke_only_no_real_user_review_no_generate_integration_no_ui_no_regeneration_no_build_no_zip_no_share_no_delivery_no_distribution"
