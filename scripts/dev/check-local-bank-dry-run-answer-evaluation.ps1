param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK DRY-RUN ANSWER EVALUATION CHECK v0.4.56 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$CorrectRaw = python .\services\api\exam_prep_local_bank_dry_run_answer_evaluation.py --course-id v056-smoke --skill-id local_concept_001_functiile --limit 5 --sample-mode correct --expect-all-correct
if ($LASTEXITCODE -ne 0) { throw "dry-run answer evaluation correct sample failed" }
Write-Host $CorrectRaw

$WrongRaw = python .\services\api\exam_prep_local_bank_dry_run_answer_evaluation.py --course-id v056-smoke --skill-id local_concept_001_functiile --limit 5 --sample-mode wrong --expect-all-wrong
if ($LASTEXITCODE -ne 0) { throw "dry-run answer evaluation wrong sample failed" }
Write-Host $WrongRaw

$Correct = $CorrectRaw | ConvertFrom-Json
$Wrong = $WrongRaw | ConvertFrom-Json

$version_ok = ($Correct.answer_evaluation_version -eq "v0.4.56" -and $Wrong.answer_evaluation_version -eq "v0.4.56")
$mode_ok = ($Correct.mode -eq "dry_run_answer_evaluation" -and $Wrong.mode -eq "dry_run_answer_evaluation")
$source_ok = ($Correct.selected_source -eq "local_exercise_bank_adapter" -and $Wrong.selected_source -eq "local_exercise_bank_adapter")
$count_ok = ([int]$Correct.evaluation_count -gt 0 -and [int]$Wrong.evaluation_count -eq [int]$Correct.evaluation_count)
$correct_all_ok = ([int]$Correct.correct_count -eq [int]$Correct.evaluation_count)
$wrong_all_ok = ([int]$Wrong.incorrect_count -eq [int]$Wrong.evaluation_count)
$average_correct_ok = ([double]$Correct.average_score_preview -eq 1.0)
$average_wrong_ok = ([double]$Wrong.average_score_preview -eq 0.0)
$first = $Correct.evaluations[0]
$first_has_feedback_ok = ([string]$first.feedback_preview).Trim().Length -gt 0
$first_has_verdict_ok = ($first.verdict -eq "correct")
$first_dry_run_ok = ($first.dry_run_only -eq $true)
$first_no_persist_ok = ($first.will_persist_attempt -eq $false)
$first_no_progress_ok = ($first.will_update_progress -eq $false)
$first_no_live_score_ok = ($first.will_score_live_session -eq $false)
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
Write-Host "correct_all_ok $correct_all_ok"
Write-Host "wrong_all_ok $wrong_all_ok"
Write-Host "average_correct_ok $average_correct_ok"
Write-Host "average_wrong_ok $average_wrong_ok"
Write-Host "first_has_feedback_ok $first_has_feedback_ok"
Write-Host "first_has_verdict_ok $first_has_verdict_ok"
Write-Host "first_dry_run_ok $first_dry_run_ok"
Write-Host "first_no_persist_ok $first_no_persist_ok"
Write-Host "first_no_progress_ok $first_no_progress_ok"
Write-Host "first_no_live_score_ok $first_no_live_score_ok"
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

if (-not ($version_ok -and $mode_ok -and $source_ok -and $count_ok -and $correct_all_ok -and $wrong_all_ok -and $average_correct_ok -and $average_wrong_ok -and $first_has_feedback_ok -and $first_has_verdict_ok -and $first_dry_run_ok -and $first_no_persist_ok -and $first_no_progress_ok -and $first_no_live_score_ok -and $path_policy_ok -and $no_persist_ok -and $no_progress_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
  throw "LOCAL BANK DRY-RUN ANSWER EVALUATION CHECK v0.4.56 FAILED"
}

Write-Host "LOCAL BANK DRY-RUN ANSWER EVALUATION CHECK v0.4.56 PASS"

