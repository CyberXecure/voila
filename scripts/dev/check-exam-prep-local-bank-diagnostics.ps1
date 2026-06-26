param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== EXAM PREP LOCAL BANK DIAGNOSTICS CHECK v0.4.48 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$Tmp = Join-Path $env:TEMP ("voila-local-bank-diagnostics-" + [guid]::NewGuid().ToString("N"))
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

  $GeneratedRaw = python .\services\api\local_pedagogy_engine.py --text $SampleText --output-dir $CourseDir --course-id "v048-smoke" --language ro
  if ($LASTEXITCODE -ne 0) { throw "local_pedagogy_engine.py failed" }
  Write-Host $GeneratedRaw

  $DiagnosticsRaw = python .\services\api\exam_prep_local_bank_diagnostics.py --root $Tmp --course-id "v048-smoke" --limit 8 --strict-local
  if ($LASTEXITCODE -ne 0) { throw "exam_prep_local_bank_diagnostics.py strict-local failed" }
  Write-Host $DiagnosticsRaw

  $FallbackRaw = python .\services\api\exam_prep_local_bank_diagnostics.py --root $EmptyDir
  if ($LASTEXITCODE -ne 0) { throw "exam_prep_local_bank_diagnostics.py fallback diagnostics failed" }
  Write-Host $FallbackRaw

  $Diagnostics = $DiagnosticsRaw | ConvertFrom-Json
  $Fallback = $FallbackRaw | ConvertFrom-Json

  $diagnostics_version_ok = ($Diagnostics.diagnostics_version -eq "v0.4.48")
  $mode_ok = ($Diagnostics.mode -eq "read_only_diagnostics")
  $active_source_ok = ($Diagnostics.active_source_adapter -eq "local_exercise_bank_adapter")
  $local_available_ok = ($Diagnostics.local_bank_available -eq $true)
  $local_question_count_ok = ([int]$Diagnostics.local_question_count -gt 0 -and [int]$Diagnostics.local_question_count -le 8)
  $legacy_fallback_ok = ($Diagnostics.legacy_fallback_available -eq $true)
  $validation_ok = ($Diagnostics.validation.valid -eq $true)
  $sample_ids_ok = ($Diagnostics.sample_question_ids.Count -gt 0)
  $coverage_types_ok = (@($Diagnostics.coverage.question_types.PSObject.Properties).Count -gt 0)
  $coverage_difficulty_ok = (@($Diagnostics.coverage.difficulty.PSObject.Properties).Count -gt 0)
  $coverage_skills_ok = (@($Diagnostics.coverage.skills.PSObject.Properties).Count -gt 0)
  $no_progress_change_ok = ($Diagnostics.will_modify_progress -eq $false)
  $no_ui_change_ok = ($Diagnostics.will_modify_exam_prep_ui -eq $false)
  $no_scoring_change_ok = ($Diagnostics.will_modify_scoring -eq $false)
  $no_weak_review_change_ok = ($Diagnostics.will_modify_weak_review -eq $false)
  $no_replace_legacy_ok = ($Diagnostics.will_replace_legacy_generator -eq $false)
  $no_live_consumption_ok = ($Diagnostics.will_enable_live_consumption -eq $false)
  $no_cloud_ok = ($Diagnostics.requires_cloud_or_api -eq $false)
  $fallback_ok = ($Fallback.local_bank_available -eq $false -and $Fallback.active_source_adapter -eq "legacy_fallback")

  Write-Host "diagnostics_version_ok $diagnostics_version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "active_source_ok $active_source_ok"
  Write-Host "local_available_ok $local_available_ok"
  Write-Host "local_question_count_ok $local_question_count_ok"
  Write-Host "legacy_fallback_ok $legacy_fallback_ok"
  Write-Host "validation_ok $validation_ok"
  Write-Host "sample_ids_ok $sample_ids_ok"
  Write-Host "coverage_types_ok $coverage_types_ok"
  Write-Host "coverage_difficulty_ok $coverage_difficulty_ok"
  Write-Host "coverage_skills_ok $coverage_skills_ok"
  Write-Host "no_progress_change_ok $no_progress_change_ok"
  Write-Host "no_ui_change_ok $no_ui_change_ok"
  Write-Host "no_scoring_change_ok $no_scoring_change_ok"
  Write-Host "no_weak_review_change_ok $no_weak_review_change_ok"
  Write-Host "no_replace_legacy_ok $no_replace_legacy_ok"
  Write-Host "no_live_consumption_ok $no_live_consumption_ok"
  Write-Host "no_cloud_ok $no_cloud_ok"
  Write-Host "fallback_ok $fallback_ok"

  if (-not ($diagnostics_version_ok -and $mode_ok -and $active_source_ok -and $local_available_ok -and $local_question_count_ok -and $legacy_fallback_ok -and $validation_ok -and $sample_ids_ok -and $coverage_types_ok -and $coverage_difficulty_ok -and $coverage_skills_ok -and $no_progress_change_ok -and $no_ui_change_ok -and $no_scoring_change_ok -and $no_weak_review_change_ok -and $no_replace_legacy_ok -and $no_live_consumption_ok -and $no_cloud_ok -and $fallback_ok)) {
    throw "EXAM PREP LOCAL BANK DIAGNOSTICS CHECK v0.4.48 FAILED"
  }

  Write-Host "EXAM PREP LOCAL BANK DIAGNOSTICS CHECK v0.4.48 PASS"
} finally {
  if (Test-Path $Tmp) {
    Remove-Item -Recurse -Force $Tmp
  }
}


