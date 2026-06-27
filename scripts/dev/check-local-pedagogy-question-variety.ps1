param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL PEDAGOGY QUESTION VARIETY UPGRADE CHECK v0.4.55 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$Tmp = Join-Path $env:TEMP ("voila-local-variety-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $Tmp | Out-Null

try {
  $SampleText = @"
Funcțiile sunt relații matematice între două mulțimi. O funcție este definită prin domeniu, codomeniu și lege de corespondență.
Derivata descrie variația locală a unei funcții. Apoi se poate studia monotonia și se pot identifica punctele critice.
Formula f'(x)=lim h->0 (f(x+h)-f(x))/h este folosită pentru calculul derivatei.
"@

  $GeneratedRaw = python .\services\api\local_pedagogy_engine.py --text $SampleText --output-dir $Tmp --course-id "v055-smoke" --language ro
  if ($LASTEXITCODE -ne 0) { throw "local_pedagogy_engine.py failed" }
  Write-Host $GeneratedRaw

  $BankPath = Join-Path $Tmp "exercise_bank.local.json"
  $AnalysisPath = Join-Path $Tmp "course_analysis.local.json"
  $BlueprintPath = Join-Path $Tmp "exam_blueprint.local.json"

  $has_bank = Test-Path $BankPath
  $has_analysis = Test-Path $AnalysisPath
  $has_blueprint = Test-Path $BlueprintPath

  $Bank = Get-Content -Raw $BankPath | ConvertFrom-Json
  $Analysis = Get-Content -Raw $AnalysisPath | ConvertFrom-Json
  $Blueprint = Get-Content -Raw $BlueprintPath | ConvertFrom-Json

  $firstSkillQuestions = @($Bank.exercises | Where-Object { $_.skill_id -eq "local_concept_001_functiile" })
  $firstSkillTypes = @($firstSkillQuestions | ForEach-Object { $_.type } | Sort-Object -Unique)

  $engine_version_ok = ($Bank.engine_version -eq "v0.4.55" -and $Analysis.engine_version -eq "v0.4.55")
  $variety_version_ok = ($Bank.question_variety_version -eq "v0.4.55" -and $Blueprint.question_variety_version -eq "v0.4.55")
  $files_ok = ($has_bank -and $has_analysis -and $has_blueprint)
  $exercise_count_ok = ([int]$Bank.exercise_count -ge 20)
  $first_skill_question_count_ok = ($firstSkillQuestions.Count -ge 5)
  $first_skill_type_diversity_ok = ($firstSkillTypes.Count -ge 5)
  $has_short_answer = ($firstSkillTypes -contains "short_answer")
  $has_evidence_based = ($firstSkillTypes -contains "evidence_based")
  $has_compare = ($firstSkillTypes -contains "compare_concepts")
  $has_apply = ($firstSkillTypes -contains "apply_concept")
  $has_formula = (@($Bank.exercises | Where-Object { $_.type -eq "formula_interpretation" }).Count -ge 1)
  $legacy_fallback_ok = ([string]$Bank.legacy_fallback -match "legacy")
  $no_cloud_ok = ($GeneratedRaw -notmatch "openai|mathpix|ollama|lm studio")

  Write-Host "files_ok $files_ok"
  Write-Host "engine_version_ok $engine_version_ok"
  Write-Host "variety_version_ok $variety_version_ok"
  Write-Host "exercise_count_ok $exercise_count_ok"
  Write-Host "first_skill_question_count_ok $first_skill_question_count_ok"
  Write-Host "first_skill_type_diversity_ok $first_skill_type_diversity_ok"
  Write-Host "has_short_answer $has_short_answer"
  Write-Host "has_evidence_based $has_evidence_based"
  Write-Host "has_compare $has_compare"
  Write-Host "has_apply $has_apply"
  Write-Host "has_formula $has_formula"
  Write-Host "legacy_fallback_ok $legacy_fallback_ok"
  Write-Host "no_cloud_ok $no_cloud_ok"

  if (-not ($files_ok -and $engine_version_ok -and $variety_version_ok -and $exercise_count_ok -and $first_skill_question_count_ok -and $first_skill_type_diversity_ok -and $has_short_answer -and $has_evidence_based -and $has_compare -and $has_apply -and $has_formula -and $legacy_fallback_ok -and $no_cloud_ok)) {
    throw "LOCAL PEDAGOGY QUESTION VARIETY UPGRADE CHECK v0.4.55 FAILED"
  }

  Write-Host "LOCAL PEDAGOGY QUESTION VARIETY UPGRADE CHECK v0.4.55 PASS"
} finally {
  if (Test-Path $Tmp) {
    Remove-Item -Recurse -Force $Tmp
  }
}

