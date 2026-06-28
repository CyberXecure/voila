param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK DRY-RUN ATTEMPT ENVELOPE CHECK v0.4.57 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$CorrectRaw = python .\services\api\exam_prep_local_bank_dry_run_attempt_envelope.py --course-id v057-smoke --skill-id local_concept_001_functiile --limit 5 --sample-mode correct --expect-correct
if ($LASTEXITCODE -ne 0) { throw "dry-run attempt envelope correct sample failed" }
Write-Host $CorrectRaw

$WrongRaw = python .\services\api\exam_prep_local_bank_dry_run_attempt_envelope.py --course-id v057-smoke --skill-id local_concept_001_functiile --limit 5 --sample-mode wrong --expect-wrong
if ($LASTEXITCODE -ne 0) { throw "dry-run attempt envelope wrong sample failed" }
Write-Host $WrongRaw

$Correct = $CorrectRaw | ConvertFrom-Json
$Wrong = $WrongRaw | ConvertFrom-Json

$version_ok = ($Correct.attempt_envelope_version -eq "v0.4.57" -and $Wrong.attempt_envelope_version -eq "v0.4.57")
$mode_ok = ($Correct.mode -eq "dry_run_attempt_envelope_snapshot" -and $Wrong.mode -eq "dry_run_attempt_envelope_snapshot")
$source_ok = ($Correct.selected_source -eq "local_exercise_bank_adapter" -and $Wrong.selected_source -eq "local_exercise_bank_adapter")
$count_ok = ([int]$Correct.envelope_count -gt 0 -and [int]$Wrong.envelope_count -eq [int]$Correct.envelope_count)
$correct_verdicts_ok = ([int]$Correct.verdict_counts.correct -eq [int]$Correct.envelope_count)
$wrong_verdicts_ok = ([int]$Wrong.verdict_counts.incorrect -eq [int]$Wrong.envelope_count)

$first = $Correct.envelopes[0]
$first_version_ok = ($first.attempt_envelope_version -eq "v0.4.57")
$first_mode_ok = ($first.attempt_mode -eq "dry_run_non_persistent")
$first_id_ok = ([string]$first.dry_run_attempt_id).Trim().Length -gt 0
$first_question_snapshot_ok = ([string]$first.question_snapshot.question_id).Trim().Length -gt 0
$first_answer_ok = ([string]$first.submitted_answer).Trim().Length -gt 0
$first_eval_ok = ($first.evaluation.verdict -eq "correct" -and [string]$first.evaluation.feedback_preview -ne "")
$first_persistence_ok = (
  $first.persistence.will_persist_attempt -eq $false -and
  $first.persistence.will_update_progress -eq $false -and
  $first.persistence.will_score_live_session -eq $false -and
  $first.persistence.will_update_weak_review -eq $false
)
$first_dry_run_ok = ($first.dry_run_only -eq $true)
$first_ready_ok = ($first.ready_for_future_live_shape_review -eq $true)

$path_policy_ok = ($Correct.path_policy -eq "no_user_provided_filesystem_root" -and $Wrong.path_policy -eq "no_user_provided_filesystem_root")
$no_persist_ok = ($Correct.will_persist_attempts -eq $false -and $Wrong.will_persist_attempts -eq $false)
$no_progress_ok = ($Correct.will_update_progress -eq $false -and $Wrong.will_update_progress -eq $false)
$no_live_score_ok = ($Correct.will_score_live_session -eq $false -and $Wrong.will_score_live_session -eq $false)
$no_ui_ok = ($Correct.will_modify_exam_prep_ui -eq $false -and $Wrong.will_modify_exam_prep_ui -eq $false)
$no_weak_ok = ($Correct.will_modify_weak_review -eq $false -and $Wrong.will_modify_weak_review -eq $false)
$no_live_replace_ok = ($Correct.will_replace_live_study_session -eq $false -and $Wrong.will_replace_live_study_session -eq $false)
$no_legacy_replace_ok = ($Correct.will_replace_legacy_generator -eq $false -and $Wrong.will_replace_legacy_generator -eq $false)
$no_live_consumption_ok = ($Correct.will_enable_live_consumption -eq $false -and $Wrong.will_enable_live_consumption -eq $false)
$no_cloud_ok = ($Correct.requires_cloud_or_api -eq $false -and $Wrong.requires_cloud_or_api -eq $false)

Write-Host "version_ok $version_ok"
Write-Host "mode_ok $mode_ok"
Write-Host "source_ok $source_ok"
Write-Host "count_ok $count_ok"
Write-Host "correct_verdicts_ok $correct_verdicts_ok"
Write-Host "wrong_verdicts_ok $wrong_verdicts_ok"
Write-Host "first_version_ok $first_version_ok"
Write-Host "first_mode_ok $first_mode_ok"
Write-Host "first_id_ok $first_id_ok"
Write-Host "first_question_snapshot_ok $first_question_snapshot_ok"
Write-Host "first_answer_ok $first_answer_ok"
Write-Host "first_eval_ok $first_eval_ok"
Write-Host "first_persistence_ok $first_persistence_ok"
Write-Host "first_dry_run_ok $first_dry_run_ok"
Write-Host "first_ready_ok $first_ready_ok"
Write-Host "path_policy_ok $path_policy_ok"
Write-Host "no_persist_ok $no_persist_ok"
Write-Host "no_progress_ok $no_progress_ok"
Write-Host "no_live_score_ok $no_live_score_ok"
Write-Host "no_ui_ok $no_ui_ok"
Write-Host "no_weak_ok $no_weak_ok"
Write-Host "no_live_replace_ok $no_live_replace_ok"
Write-Host "no_legacy_replace_ok $no_legacy_replace_ok"
Write-Host "no_live_consumption_ok $no_live_consumption_ok"
Write-Host "no_cloud_ok $no_cloud_ok"

if (-not ($version_ok -and $mode_ok -and $source_ok -and $count_ok -and $correct_verdicts_ok -and $wrong_verdicts_ok -and $first_version_ok -and $first_mode_ok -and $first_id_ok -and $first_question_snapshot_ok -and $first_answer_ok -and $first_eval_ok -and $first_persistence_ok -and $first_dry_run_ok -and $first_ready_ok -and $path_policy_ok -and $no_persist_ok -and $no_progress_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
  throw "LOCAL BANK DRY-RUN ATTEMPT ENVELOPE CHECK v0.4.57 FAILED"
}

Write-Host "LOCAL BANK DRY-RUN ATTEMPT ENVELOPE CHECK v0.4.57 PASS"

