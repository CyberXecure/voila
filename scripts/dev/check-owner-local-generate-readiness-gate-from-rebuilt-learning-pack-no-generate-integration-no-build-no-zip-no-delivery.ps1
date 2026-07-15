$ErrorActionPreference = "Stop"

Write-Host "v0.7.76 check: start"

$module = "services/api/generate_readiness_gate_from_learning_pack.py"
$doc = "docs/dev/owner-local-generate-readiness-gate-from-rebuilt-learning-pack-no-generate-integration-no-build-no-zip-no-delivery.md"
$gateJson = "D:\dev\tester-runs\v0776-generate-readiness-gate\out\03-pag-30-34-vectori-trigonometrie\generate_readiness_gate.json"
$gateMd = "D:\dev\tester-runs\v0776-generate-readiness-gate\out\03-pag-30-34-vectori-trigonometrie\generate_readiness_gate.md"

foreach ($p in @($module, $doc, $gateJson, $gateMd)) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence: $p" }
}

python -m py_compile $module

$text = Get-Content $module -Raw
foreach ($item in @(
  "VOILA_V0_7_76_OWNER_LOCAL_GENERATE_READINESS_GATE_FROM_REBUILT_LEARNING_PACK_START",
  "GenerateReadinessGateError",
  "validate_rebuilt_learning_pack",
  "build_generate_readiness_gate",
  "write_generate_readiness_gate_from_learning_pack",
  "owner_local_generate_readiness_gate",
  "generate_readiness_gate.json",
  "generate_readiness_gate.md",
  "ready_for_separate_generate_integration_milestone",
  "generate_integration_changed",
  "generator_route_changed",
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

$report = Get-Content $gateJson -Raw | ConvertFrom-Json
if ($report.artifact -ne "owner_local_generate_readiness_gate") { throw "artifact mismatch" }
if ($report.artifact_version -ne "v0.7.76") { throw "artifact_version mismatch" }
if ($report.source_rebuild_artifact_version -ne "v0.7.75") { throw "source rebuild version mismatch" }
if ($report.generate_readiness_status -ne "PASS") { throw "readiness status mismatch" }
if ($report.ready_for_separate_generate_integration_milestone -ne $true) { throw "ready flag mismatch" }
if ($report.tester_readiness -ne "BLOCKED") { throw "tester readiness mismatch" }

if ($report.quality_gate.document_learning_status -ne "PASS") { throw "document learning status mismatch" }
if ($report.quality_gate.generation_allowed_in_pack -ne $true) { throw "generation allowed in pack mismatch" }
if ($report.quality_gate.verified_user_evidence_count -ne 20) { throw "verified evidence count mismatch" }
if ($report.quality_gate.pending_decision_count -ne 0) { throw "pending decision count mismatch" }
if ($report.quality_gate.teaching_plan_status -ne "candidate_ready_for_future_generator") { throw "teaching plan status mismatch" }
if ($report.quality_gate.generate_readiness_status -ne "PASS") { throw "gate readiness mismatch" }
if ($report.quality_gate.ready_for_separate_generate_integration_milestone -ne $true) { throw "gate ready flag mismatch" }
if ($report.quality_gate.generate_integration_changed -ne $false) { throw "generate integration changed mismatch" }
if ($report.quality_gate.generator_route_changed -ne $false) { throw "generator route changed mismatch" }
if ($report.quality_gate.course_regeneration_performed -ne $false) { throw "course regeneration mismatch" }

if ($report.policy.writes_only_generate_readiness_artifacts -ne $true) { throw "writes only readiness policy mismatch" }
if ($report.policy.generate_integration_changed -ne $false) { throw "policy generate mismatch" }
if ($report.policy.generator_route_changed -ne $false) { throw "policy route mismatch" }
if ($report.policy.course_regeneration_performed -ne $false) { throw "policy course regen mismatch" }
if ($report.policy.build_performed -ne $false) { throw "policy build mismatch" }
if ($report.policy.zip_created -ne $false) { throw "policy zip mismatch" }
if ($report.policy.share_created -ne $false) { throw "policy share mismatch" }
if ($report.policy.delivery_performed -ne $false) { throw "policy delivery mismatch" }
if ($report.policy.distribution_performed -ne $false) { throw "policy distribution mismatch" }

$md = (Get-Content $gateMd -Raw).Replace('`', '')
foreach ($item in @(
  "# Generate Readiness Gate",
  "Artifact version: v0.7.76",
  "Generate readiness status: PASS",
  "Ready for separate generate integration milestone: True",
  "Tester readiness: BLOCKED",
  "Document learning status: PASS",
  "Generation allowed in pack: True",
  "Verified user evidence count: 20",
  "Generate integration changed: False",
  "Generator route changed: False",
  "Course regeneration performed: False"
)) {
  if ($md -notlike "*$item*") { throw "Markdown missing expected text: $item" }
}

$docText = (Get-Content $doc -Raw).Replace('`', '')
foreach ($item in @(
  "VOILA_V0_7_76_GENERATE_READINESS_GATE_FROM_REBUILT_LEARNING_PACK_CHECK=PASS",
  "PASS_GENERATE_READINESS_GATE_FROM_REBUILT_LEARNING_PACK",
  "SOURCE_REBUILD_ARTIFACT_VERSION=v0.7.75",
  "DOCUMENT_LEARNING_STATUS=PASS",
  "GENERATION_ALLOWED_IN_PACK=True",
  "VERIFIED_USER_EVIDENCE_COUNT=20",
  "GENERATE_READINESS_STATUS=PASS",
  "READY_FOR_SEPARATE_GENERATE_INTEGRATION_MILESTONE=True",
  "GENERATE_INTEGRATION=NOT_CHANGED",
  "GENERATOR_ROUTE_CHANGED=False",
  "COURSE_REGENERATION=False",
  "TESTER_READINESS=BLOCKED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/generate_readiness_gate_from_learning_pack.py",
  "docs/dev/owner-local-generate-readiness-gate-from-rebuilt-learning-pack-no-generate-integration-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-generate-readiness-gate-from-rebuilt-learning-pack-no-generate-integration-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_76_GENERATE_READINESS_GATE_FROM_REBUILT_LEARNING_PACK_CHECK=PASS"
"GENERATE_READINESS_GATE_FROM_REBUILT_LEARNING_PACK=PASS"
"SOURCE_REBUILD_ARTIFACT_VERSION=v0.7.75"
"DOCUMENT_LEARNING_STATUS=PASS"
"GENERATION_ALLOWED_IN_PACK=True"
"VERIFIED_USER_EVIDENCE_COUNT=20"
"PENDING_DECISION_COUNT=0"
"TEACHING_PLAN_STATUS=candidate_ready_for_future_generator"
"GENERATE_READINESS_STATUS=PASS"
"READY_FOR_SEPARATE_GENERATE_INTEGRATION_MILESTONE=True"
"GENERATE_INTEGRATION=NOT_CHANGED"
"GENERATOR_ROUTE_CHANGED=False"
"COURSE_REGENERATION=False"
"BUILD_PERFORMED=False"
"ZIP_CREATED=False"
"SHARE_CREATED=False"
"DELIVERY_PERFORMED=False"
"TESTER_READINESS=BLOCKED"
"POLICY=owner_local_generate_readiness_gate_from_rebuilt_learning_pack_no_generate_integration_no_build_no_zip_no_share_no_delivery_no_distribution"
