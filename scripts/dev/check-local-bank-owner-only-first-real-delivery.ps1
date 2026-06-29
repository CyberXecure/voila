$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

Write-Host "=== v0.5.0 owner-only local-bank first real delivery check ===" -ForegroundColor Cyan

$ApiPath = Join-Path $RepoRoot "services\api"
$env:PYTHONPATH = $ApiPath

$CourseId = "v050-owner-only-local-bank-first-real-delivery"
$SkillId = "local_concept_001_functiile"
$FixtureRoot = Join-Path $RepoRoot ".tmp\v050-owner-only-local-bank-first-real-delivery"
$FixtureCourseRoot = Join-Path $FixtureRoot "course"

if (Test-Path $FixtureRoot) {
  Remove-Item $FixtureRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $FixtureCourseRoot | Out-Null

$exercises = @()
for ($i = 1; $i -le 7; $i++) {
  $exercises += [ordered]@{
    id = "q$i"
    skill_id = $SkillId
    type = "multiple_choice"
    difficulty = "medium"
    question = "Întrebarea local-bank owner-only $i?"
    choices = @("Varianta A$i", "Varianta B$i", "Varianta C$i")
    correct_answer = "Varianta A$i"
    explanation = "Explicație ascunsă pentru întrebarea $i."
    source_excerpt = "Fragment local ascuns $i."
  }
}

$bank = [ordered]@{
  schema_version = "1"
  engine = "local_pedagogy_engine"
  course_id = $CourseId
  exercise_count = $exercises.Count
  generated_by = "v0.5.0 owner-only first real delivery fixture"
  legacy_fallback = "Legacy quiz/question data remains available as rollback fallback."
  exercises = $exercises
}

$bankPath = Join-Path $FixtureCourseRoot "exercise_bank.local.json"
$bank | ConvertTo-Json -Depth 20 | Set-Content -Path $bankPath -Encoding UTF8

Write-Host "`n=== Fixture created ===" -ForegroundColor Yellow
Write-Host $bankPath

Write-Host "`n=== Clear delivery-related env ===" -ForegroundColor Yellow
Get-ChildItem Env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK* -ErrorAction SilentlyContinue | ForEach-Object {
  Remove-Item "Env:$($_.Name)" -ErrorAction SilentlyContinue
}
Remove-Item "Env:VOILA_FORCE_EXAM_PREP_LOCAL_BANK_OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK" -ErrorAction SilentlyContinue

Write-Host "`n=== PASS 1: default must stay disabled / legacy_fallback ===" -ForegroundColor Yellow
python "services/api/exam_prep_local_bank_owner_only_first_real_delivery.py" `
  --root $FixtureRoot `
  --course-id $CourseId `
  --skill-id $SkillId `
  --limit 5 `
  --expect-disabled | Out-Host

Write-Host "`n=== Enable full v0.4.94 freeze chain flags + v0.5.0 delivery flag ===" -ForegroundColor Yellow
$requiredFlagsJson = python -c "import json; from exam_prep_local_bank_first_live_trial_readiness_freeze import REQUIRED_OWNER_FLAGS; print(json.dumps(REQUIRED_OWNER_FLAGS))"
$requiredFlags = $requiredFlagsJson | ConvertFrom-Json

foreach ($flag in $requiredFlags) {
  Set-Item -Path "Env:$flag" -Value "1"
  Write-Host "ON $flag" -ForegroundColor DarkGreen
}

Set-Item -Path "Env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_OWNER_ONLY_FIRST_REAL_DELIVERY" -Value "1"
Write-Host "ON VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_OWNER_ONLY_FIRST_REAL_DELIVERY" -ForegroundColor Green

Write-Host "`n=== Sanity: local-bank adapter preview must find 5 questions ===" -ForegroundColor Yellow
$previewJson = python "services/api/exam_prep_local_bank_adapter.py" `
  --root $FixtureRoot `
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

Write-Host "`n=== PASS 2: owner-only real delivery must deliver max 5 local-bank questions ===" -ForegroundColor Yellow
$resultJson = python "services/api/exam_prep_local_bank_owner_only_first_real_delivery.py" `
  --root $FixtureRoot `
  --course-id $CourseId `
  --skill-id $SkillId `
  --limit 7 `
  --expect-delivered

$resultJson | Out-Host
$result = $resultJson | ConvertFrom-Json

if ($result.delivery_performed -ne $true) {
  throw "delivery_performed is not true"
}
if ($result.effective_source -ne "local_bank") {
  throw "effective_source is not local_bank"
}
if ([int]$result.delivered_question_count -gt 5) {
  throw "delivered_question_count exceeds 5"
}
if ([int]$result.delivered_question_count -lt 1) {
  throw "delivered_question_count below 1"
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

Write-Host "`n=== PASS 3: rollback flag must force legacy_fallback ===" -ForegroundColor Yellow
Set-Item -Path "Env:VOILA_FORCE_EXAM_PREP_LOCAL_BANK_OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK" -Value "1"

python "services/api/exam_prep_local_bank_owner_only_first_real_delivery.py" `
  --root $FixtureRoot `
  --course-id $CourseId `
  --skill-id $SkillId `
  --limit 5 `
  --expect-rollback | Out-Host

Remove-Item "Env:VOILA_FORCE_EXAM_PREP_LOCAL_BANK_OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK" -ErrorAction SilentlyContinue

Write-Host "`n=== PASS 4: ensure no public UI / web_app patch marker in git diff ===" -ForegroundColor Yellow
$changed = git diff --name-only
$changed | Out-Host

if ($changed -match "services/api/web_app.py") {
  throw "web_app.py was modified, which is not allowed for v0.5.0"
}

Write-Host "`n=== PASS 5: compile changed module ===" -ForegroundColor Yellow
python -m compileall "services/api/exam_prep_local_bank_owner_only_first_real_delivery.py"

Write-Host "`n=== PASS 6: diff whitespace check ===" -ForegroundColor Yellow
git diff --check

Write-Host "`n=== v0.5.0 CHECK PASS ===" -ForegroundColor Green
