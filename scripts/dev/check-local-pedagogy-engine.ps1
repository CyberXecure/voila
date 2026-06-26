param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL PEDAGOGY ENGINE CHECK v0.4.44 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$Tmp = Join-Path $env:TEMP ("voila-local-pedagogy-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $Tmp | Out-Null

try {
  $SampleText = @"
Funcțiile sunt relații matematice între două mulțimi. O funcție este definită prin domeniu, codomeniu și lege de corespondență.
Derivata descrie variația locală a unei funcții. Apoi se poate studia monotonia și se pot identifica punctele critice.
Formula f'(x)=lim h->0 (f(x+h)-f(x))/h este folosită pentru calculul derivatei.
"@

  $ResultRaw = python .\services\api\local_pedagogy_engine.py --text $SampleText --output-dir $Tmp --course-id "v044-smoke" --language ro
  Write-Host $ResultRaw

  $AnalysisPath = Join-Path $Tmp "course_analysis.local.json"
  $ExercisePath = Join-Path $Tmp "exercise_bank.local.json"
  $BlueprintPath = Join-Path $Tmp "exam_blueprint.local.json"

  $hasAnalysis = Test-Path $AnalysisPath
  $hasExerciseBank = Test-Path $ExercisePath
  $hasBlueprint = Test-Path $BlueprintPath

  $Analysis = Get-Content -Raw -Path $AnalysisPath | ConvertFrom-Json
  $ExerciseBank = Get-Content -Raw -Path $ExercisePath | ConvertFrom-Json
  $Blueprint = Get-Content -Raw -Path $BlueprintPath | ConvertFrom-Json

  $analysis_engine_ok = ($Analysis.engine -eq "local_pedagogy_engine")
  $exercise_count_ok = ([int]$ExerciseBank.exercise_count -gt 0)
  $blueprint_policy_ok = ($Blueprint.selection_policy.Count -gt 0)
  $has_legacy_fallback = ($ExerciseBank.legacy_fallback -match "legacy")
  $has_no_cloud_wording = ($ResultRaw -notmatch "openai|mathpix|ollama|lm studio")

  Write-Host "has_course_analysis_local_json $hasAnalysis"
  Write-Host "has_exercise_bank_local_json $hasExerciseBank"
  Write-Host "has_exam_blueprint_local_json $hasBlueprint"
  Write-Host "analysis_engine_ok $analysis_engine_ok"
  Write-Host "exercise_count_ok $exercise_count_ok"
  Write-Host "blueprint_policy_ok $blueprint_policy_ok"
  Write-Host "has_legacy_fallback $has_legacy_fallback"
  Write-Host "runtime_output_no_cloud_dependency $has_no_cloud_wording"

  if (-not ($hasAnalysis -and $hasExerciseBank -and $hasBlueprint -and $analysis_engine_ok -and $exercise_count_ok -and $blueprint_policy_ok -and $has_legacy_fallback -and $has_no_cloud_wording)) {
    throw "LOCAL PEDAGOGY ENGINE CHECK v0.4.44 FAILED"
  }

  Write-Host "LOCAL PEDAGOGY ENGINE CHECK v0.4.44 PASS"
} finally {
  if (Test-Path $Tmp) {
    Remove-Item -Recurse -Force $Tmp
  }
}

