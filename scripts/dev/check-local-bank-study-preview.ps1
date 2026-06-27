param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK READ-ONLY STUDY PREVIEW CHECK v0.4.49 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$Tmp = Join-Path $env:TEMP ("voila-local-bank-study-preview-" + [guid]::NewGuid().ToString("N"))
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

  $GeneratedRaw = python .\services\api\local_pedagogy_engine.py --text $SampleText --output-dir $CourseDir --course-id "v049-smoke" --language ro
  if ($LASTEXITCODE -ne 0) { throw "local_pedagogy_engine.py failed" }
  Write-Host $GeneratedRaw

  $PreviewRaw = python .\services\api\exam_prep_local_bank_study_preview.py --root $Tmp --course-id "v049-smoke" --skill-id "local_concept_001_functiile" --limit 3 --strict-local
  if ($LASTEXITCODE -ne 0) { throw "exam_prep_local_bank_study_preview.py strict-local failed" }
  Write-Host $PreviewRaw

  $AutoPreviewRaw = python .\services\api\exam_prep_local_bank_study_preview.py --root $Tmp --course-id "v049-smoke" --limit 2 --strict-local
  if ($LASTEXITCODE -ne 0) { throw "exam_prep_local_bank_study_preview.py auto-skill failed" }
  Write-Host $AutoPreviewRaw

  $FallbackRaw = python .\services\api\exam_prep_local_bank_study_preview.py --root $EmptyDir
  if ($LASTEXITCODE -ne 0) { throw "exam_prep_local_bank_study_preview.py fallback failed" }
  Write-Host $FallbackRaw

  $Preview = $PreviewRaw | ConvertFrom-Json
  $AutoPreview = $AutoPreviewRaw | ConvertFrom-Json
  $Fallback = $FallbackRaw | ConvertFrom-Json

  $version_ok = ($Preview.study_preview_version -eq "v0.4.49")
  $mode_ok = ($Preview.mode -eq "read_only_study_preview")
  $active_source_ok = ($Preview.active_source -eq "local_exercise_bank_adapter")
  $skill_ok = ($Preview.selected_skill_id -eq "local_concept_001_functiile")
  $question_count_ok = ([int]$Preview.preview_question_count -gt 0 -and [int]$Preview.preview_question_count -le 3)
  $has_questions_ok = (@($Preview.questions).Count -gt 0)
  $first = $Preview.questions[0]
  $first_ready_ok = ($first.ready_for_read_only_study_preview -eq $true)
  $first_no_attempt_ok = ($first.will_save_attempt -eq $false)
  $first_no_progress_ok = ($first.will_update_progress -eq $false)
  $first_no_score_ok = ($first.will_score_answer -eq $false)
  $first_has_answer_ok = ([string]$first.correct_answer).Trim().Length -gt 0
  $first_source_ok = ($first.source -eq "local_exercise_bank_adapter")
  $auto_skill_ok = ([string]$AutoPreview.selected_skill_id).Trim().Length -gt 0
  $fallback_ok = ($Fallback.active_source -eq "legacy_fallback" -and [int]$Fallback.preview_question_count -eq 0)
  $legacy_fallback_ok = ($Preview.legacy_fallback_available -eq $true)
  $no_save_ok = ($Preview.will_save_attempt -eq $false)
  $no_progress_ok = ($Preview.will_update_progress -eq $false)
  $no_scoring_ok = ($Preview.will_score_answer -eq $false)
  $no_ui_ok = ($Preview.will_modify_exam_prep_ui -eq $false)
  $no_weak_ok = ($Preview.will_modify_weak_review -eq $false)
  $no_live_session_replace_ok = ($Preview.will_replace_live_study_session -eq $false)
  $no_legacy_replace_ok = ($Preview.will_replace_legacy_generator -eq $false)
  $no_live_consumption_ok = ($Preview.will_enable_live_consumption -eq $false)
  $no_cloud_ok = ($Preview.requires_cloud_or_api -eq $false)
  $skill_counts_ok = (@($Preview.available_skill_counts.PSObject.Properties).Count -gt 0)

  Write-Host "version_ok $version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "active_source_ok $active_source_ok"
  Write-Host "skill_ok $skill_ok"
  Write-Host "question_count_ok $question_count_ok"
  Write-Host "has_questions_ok $has_questions_ok"
  Write-Host "first_ready_ok $first_ready_ok"
  Write-Host "first_no_attempt_ok $first_no_attempt_ok"
  Write-Host "first_no_progress_ok $first_no_progress_ok"
  Write-Host "first_no_score_ok $first_no_score_ok"
  Write-Host "first_has_answer_ok $first_has_answer_ok"
  Write-Host "first_source_ok $first_source_ok"
  Write-Host "auto_skill_ok $auto_skill_ok"
  Write-Host "fallback_ok $fallback_ok"
  Write-Host "legacy_fallback_ok $legacy_fallback_ok"
  Write-Host "no_save_ok $no_save_ok"
  Write-Host "no_progress_ok $no_progress_ok"
  Write-Host "no_scoring_ok $no_scoring_ok"
  Write-Host "no_ui_ok $no_ui_ok"
  Write-Host "no_weak_ok $no_weak_ok"
  Write-Host "no_live_session_replace_ok $no_live_session_replace_ok"
  Write-Host "no_legacy_replace_ok $no_legacy_replace_ok"
  Write-Host "no_live_consumption_ok $no_live_consumption_ok"
  Write-Host "no_cloud_ok $no_cloud_ok"
  Write-Host "skill_counts_ok $skill_counts_ok"

  if (-not ($version_ok -and $mode_ok -and $active_source_ok -and $skill_ok -and $question_count_ok -and $has_questions_ok -and $first_ready_ok -and $first_no_attempt_ok -and $first_no_progress_ok -and $first_no_score_ok -and $first_has_answer_ok -and $first_source_ok -and $auto_skill_ok -and $fallback_ok -and $legacy_fallback_ok -and $no_save_ok -and $no_progress_ok -and $no_scoring_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_session_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok -and $skill_counts_ok)) {
    throw "LOCAL BANK READ-ONLY STUDY PREVIEW CHECK v0.4.49 FAILED"
  }

  Write-Host "LOCAL BANK READ-ONLY STUDY PREVIEW CHECK v0.4.49 PASS"
} finally {
  if (Test-Path $Tmp) {
    Remove-Item -Recurse -Force $Tmp
  }
}

