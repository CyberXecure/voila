$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

Write-Host "=== v0.5.1 owner-only real-course local-bank delivery smoke ===" -ForegroundColor Cyan

$ApiPath = Join-Path $RepoRoot "services\api"
$env:PYTHONPATH = $ApiPath

$SmokeRoot = Join-Path $RepoRoot ".tmp\v051-owner-only-real-course-local-bank-delivery-smoke"

if (Test-Path $SmokeRoot) {
  Remove-Item $SmokeRoot -Recurse -Force
}

Write-Host "`n=== Build temporary local bank from real course artifact ===" -ForegroundColor Yellow
$summaryJson = python "scripts/dev/build-local-bank-real-course-smoke.py" --root "." --smoke-root $SmokeRoot
$summaryJson | Out-Host
$summary = $summaryJson | ConvertFrom-Json

$CourseId = [string]$summary.course_id
$SkillId = [string]$summary.skill_id

if (-not $CourseId) {
  throw "Missing generated CourseId"
}
if (-not $SkillId) {
  throw "Missing generated SkillId"
}

Write-Host "`n=== Clear delivery-related env ===" -ForegroundColor Yellow
Get-ChildItem Env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK* -ErrorAction SilentlyContinue | ForEach-Object {
  Remove-Item "Env:$($_.Name)" -ErrorAction SilentlyContinue
}
Remove-Item "Env:VOILA_FORCE_EXAM_PREP_LOCAL_BANK_OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK" -ErrorAction SilentlyContinue

Write-Host "`n=== PASS 1: default must stay disabled / legacy_fallback ===" -ForegroundColor Yellow
python "services/api/exam_prep_local_bank_owner_only_first_real_delivery.py" `
  --root $SmokeRoot `
  --course-id $CourseId `
  --skill-id $SkillId `
  --limit 5 `
  --expect-disabled | Out-Host

Write-Host "`n=== Enable full v0.4.94 freeze chain flags + v0.5.0 delivery flag ===" -ForegroundColor Yellow
$requiredFlagsJson = python -c "import json; from exam_prep_local_bank_first_live_trial_readiness_freeze import REQUIRED_OWNER_FLAGS; print(json.dumps(REQUIRED_OWNER_FLAGS))"
$requiredFlags = $requiredFlagsJson | ConvertFrom-Json

foreach ($flag in $requiredFlags) {
  Set-Item -Path "Env:$flag" -Value "1"
}

Set-Item -Path "Env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_OWNER_ONLY_FIRST_REAL_DELIVERY" -Value "1"

Write-Host "`n=== PASS 2: adapter preview must find 5 real-course local-bank questions ===" -ForegroundColor Yellow
$previewJson = python "services/api/exam_prep_local_bank_adapter.py" `
  --root $SmokeRoot `
  --course-id $CourseId `
  --limit 5 `
  --strict-local

$previewJson | Out-Host
$preview = $previewJson | ConvertFrom-Json

if ($preview.active_source_adapter -ne "local_exercise_bank_adapter") {
  throw "adapter did not select local_exercise_bank_adapter"
}
if ([int]$preview.question_count -ne 5) {
  throw "adapter preview question_count is not 5"
}

Write-Host "`n=== PASS 3: owner-only real-course delivery must deliver max 5 questions ===" -ForegroundColor Yellow
$resultJson = python "services/api/exam_prep_local_bank_owner_only_first_real_delivery.py" `
  --root $SmokeRoot `
  --course-id $CourseId `
  --skill-id $SkillId `
  --readiness-course-id "v050-owner-only-local-bank-first-real-delivery" `
  --readiness-skill-id "local_concept_001_functiile" `
  --limit 5 `
  --expect-delivered

$resultJson | Out-Host
$result = $resultJson | ConvertFrom-Json

if ($result.delivery_performed -ne $true) {
  throw "delivery_performed is not true"
}
if ($result.effective_source -ne "local_bank") {
  throw "effective_source is not local_bank"
}
if ([int]$result.delivered_question_count -lt 1 -or [int]$result.delivered_question_count -gt 5) {
  throw "delivered_question_count outside 1..5"
}
if ($result.implementation_scope.adds_public_ui -ne $false) {
  throw "adds_public_ui is not false"
}
if ($result.implementation_scope.patches_web_app -ne $false) {
  throw "patches_web_app is not false"
}
if ($result.no_persistence_policy.persist_attempts -ne $false) {
  throw "persist_attempts is not false"
}
if ($result.no_persistence_policy.persist_session -ne $false) {
  throw "persist_session is not false"
}
if ($result.no_persistence_policy.persist_progress -ne $false) {
  throw "persist_progress is not false"
}
if ($result.no_persistence_policy.score_live_session -ne $false) {
  throw "score_live_session is not false"
}

Write-Host "`n=== PASS 4: rollback flag must force legacy_fallback ===" -ForegroundColor Yellow
Set-Item -Path "Env:VOILA_FORCE_EXAM_PREP_LOCAL_BANK_OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK" -Value "1"

python "services/api/exam_prep_local_bank_owner_only_first_real_delivery.py" `
  --root $SmokeRoot `
  --course-id $CourseId `
  --skill-id $SkillId `
  --limit 5 `
  --expect-rollback | Out-Host

Remove-Item "Env:VOILA_FORCE_EXAM_PREP_LOCAL_BANK_OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK" -ErrorAction SilentlyContinue

Write-Host "`n=== PASS 5: ensure no public UI / web_app.py patch ===" -ForegroundColor Yellow
$changed = git diff --name-only
$changed | Out-Host

if ($changed -match "services/api/web_app.py") {
  throw "web_app.py was modified, which is not allowed for v0.5.1"
}

Write-Host "`n=== PASS 6: clean temporary smoke data ===" -ForegroundColor Yellow
if (Test-Path $SmokeRoot) {
  Remove-Item $SmokeRoot -Recurse -Force
}
if (Test-Path ".tmp") {
  $remaining = Get-ChildItem ".tmp" -Force -ErrorAction SilentlyContinue
  if (-not $remaining) {
    Remove-Item ".tmp" -Force
  }
}

Write-Host "`n=== PASS 7: compile helper ===" -ForegroundColor Yellow
python -m compileall "scripts/dev/build-local-bank-real-course-smoke.py"

Write-Host "`n=== PASS 8: diff whitespace check ===" -ForegroundColor Yellow
git diff --check

Write-Host "`n=== v0.5.1 REAL-COURSE DELIVERY SMOKE PASS ===" -ForegroundColor Green
