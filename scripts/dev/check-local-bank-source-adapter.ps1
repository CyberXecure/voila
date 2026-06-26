param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK SOURCE ADAPTER CHECK v0.4.47 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$Tmp = Join-Path $env:TEMP ("voila-local-bank-adapter-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $Tmp | Out-Null

try {
  $CourseDir = Join-Path $Tmp "course-a"
  $EmptyDir = Join-Path $Tmp "empty"
  New-Item -ItemType Directory -Force -Path $CourseDir | Out-Null
  New-Item -ItemType Directory -Force -Path $EmptyDir | Out-Null

  $SampleText = @"
Funcțiile sunt relații matematice între două mulțimi. O funcție este definită prin domeniu, codomeniu și lege de corespondență.
Derivata descrie variația locală a unei funcții. Apoi se poate studia monotonia și se pot identifica punctele critice.
Formula f'(x)=lim h->0 (f(x+h)-f(x))/h este folosită pentru calculul derivatei.
"@

  $GeneratedRaw = python .\services\api\local_pedagogy_engine.py --text $SampleText --output-dir $CourseDir --course-id "v047-smoke" --language ro
  if ($LASTEXITCODE -ne 0) { throw "local_pedagogy_engine.py failed" }
  Write-Host $GeneratedRaw

  $AdapterRaw = python .\services\api\exam_prep_local_bank_adapter.py --root $Tmp --course-id "v047-smoke" --limit 5 --strict-local
  if ($LASTEXITCODE -ne 0) { throw "exam_prep_local_bank_adapter.py strict-local failed" }
  Write-Host $AdapterRaw

  $FallbackRaw = python .\services\api\exam_prep_local_bank_adapter.py --root $EmptyDir
  if ($LASTEXITCODE -ne 0) { throw "exam_prep_local_bank_adapter.py fallback preview failed" }
  Write-Host $FallbackRaw

  $Adapter = $AdapterRaw | ConvertFrom-Json
  $Fallback = $FallbackRaw | ConvertFrom-Json

  $adapter_version_ok = ($Adapter.adapter_version -eq "v0.4.47")
  $mode_ok = ($Adapter.mode -eq "read_only_adapter_preview")
  $active_source_ok = ($Adapter.active_source_adapter -eq "local_exercise_bank_adapter")
  $question_count_ok = ([int]$Adapter.question_count -gt 0)
  $limit_ok = ([int]$Adapter.question_count -le 5)
  $has_questions_ok = ($Adapter.questions.Count -gt 0)
  $first = $Adapter.questions[0]
  $first_has_id_ok = ([string]$first.question_id).Trim().Length -gt 0
  $first_has_skill_ok = ([string]$first.skill_id).Trim().Length -gt 0
  $first_has_question_ok = ([string]$first.question).Trim().Length -gt 0
  $first_has_answer_ok = ([string]$first.correct_answer).Trim().Length -gt 0
  $first_source_ok = ($first.source -eq "local_exercise_bank_adapter")
  $first_ready_ok = ($first.ready_for_exam_prep_preview -eq $true)
  $legacy_fallback_ok = ($Adapter.legacy_fallback_available -eq $true)
  $no_progress_change_ok = ($Adapter.will_modify_progress -eq $false -and $first.will_modify_progress -eq $false)
  $no_ui_change_ok = ($Adapter.will_modify_exam_prep_ui -eq $false)
  $no_replace_legacy_ok = ($Adapter.will_replace_legacy_generator -eq $false -and $first.will_replace_legacy_generator -eq $false)
  $no_cloud_ok = ($Adapter.requires_cloud_or_api -eq $false)
  $fallback_source_ok = ($Fallback.active_source_adapter -eq "legacy_fallback" -and [int]$Fallback.question_count -eq 0)

  Write-Host "adapter_version_ok $adapter_version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "active_source_ok $active_source_ok"
  Write-Host "question_count_ok $question_count_ok"
  Write-Host "limit_ok $limit_ok"
  Write-Host "has_questions_ok $has_questions_ok"
  Write-Host "first_has_id_ok $first_has_id_ok"
  Write-Host "first_has_skill_ok $first_has_skill_ok"
  Write-Host "first_has_question_ok $first_has_question_ok"
  Write-Host "first_has_answer_ok $first_has_answer_ok"
  Write-Host "first_source_ok $first_source_ok"
  Write-Host "first_ready_ok $first_ready_ok"
  Write-Host "legacy_fallback_ok $legacy_fallback_ok"
  Write-Host "no_progress_change_ok $no_progress_change_ok"
  Write-Host "no_ui_change_ok $no_ui_change_ok"
  Write-Host "no_replace_legacy_ok $no_replace_legacy_ok"
  Write-Host "no_cloud_ok $no_cloud_ok"
  Write-Host "fallback_source_ok $fallback_source_ok"

  if (-not ($adapter_version_ok -and $mode_ok -and $active_source_ok -and $question_count_ok -and $limit_ok -and $has_questions_ok -and $first_has_id_ok -and $first_has_skill_ok -and $first_has_question_ok -and $first_has_answer_ok -and $first_source_ok -and $first_ready_ok -and $legacy_fallback_ok -and $no_progress_change_ok -and $no_ui_change_ok -and $no_replace_legacy_ok -and $no_cloud_ok -and $fallback_source_ok)) {
    throw "LOCAL BANK SOURCE ADAPTER CHECK v0.4.47 FAILED"
  }

  Write-Host "LOCAL BANK SOURCE ADAPTER CHECK v0.4.47 PASS"
} finally {
  if (Test-Path $Tmp) {
    Remove-Item -Recurse -Force $Tmp
  }
}

