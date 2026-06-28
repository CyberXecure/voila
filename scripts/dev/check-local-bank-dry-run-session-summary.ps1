param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK DRY-RUN SESSION SUMMARY CHECK v0.4.58 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$CorrectRaw = python .\services\api\exam_prep_local_bank_dry_run_session_summary.py --course-id v058-smoke --skill-id local_concept_001_functiile --limit 5 --sample-mode correct --expect-correct
if ($LASTEXITCODE -ne 0) { throw "dry-run session summary correct sample failed" }
Write-Host $CorrectRaw

$WrongRaw = python .\services\api\exam_prep_local_bank_dry_run_session_summary.py --course-id v058-smoke --skill-id local_concept_001_functiile --limit 5 --sample-mode wrong --expect-wrong
if ($LASTEXITCODE -ne 0) { throw "dry-run session summary wrong sample failed" }
Write-Host $WrongRaw

$Correct = $CorrectRaw | ConvertFrom-Json
$Wrong = $WrongRaw | ConvertFrom-Json

$version_ok = ($Correct.session_summary_version -eq "v0.4.58" -and $Wrong.session_summary_version -eq "v0.4.58")
$mode_ok = ($Correct.mode -eq "dry_run_session_summary" -and $Wrong.mode -eq "dry_run_session_summary")
$source_ok = ($Correct.selected_source -eq "local_exercise_bank_adapter" -and $Wrong.selected_source -eq "local_exercise_bank_adapter")
$id_ok = ([string]$Correct.dry_run_session_id).Trim().Length -gt 0
$count_ok = ([int]$Correct.total_questions -gt 0 -and [int]$Wrong.total_questions -eq [int]$Correct.total_questions)
$correct_counts_ok = ([int]$Correct.correct_count -eq [int]$Correct.total_questions)
$wrong_counts_ok = ([int]$Wrong.incorrect_count -eq [int]$Wrong.total_questions)
$average_correct_ok = ([double]$Correct.average_score_preview -eq 1.0)
$average_wrong_ok = ([double]$Wrong.average_score_preview -eq 0.0)
$feedback_ok = ([string]$Correct.feedback_summary).Trim().Length -gt 0 -and [string]$Wrong.feedback_summary -ne ""
$envelopes_ok = (@($Correct.envelopes).Count -eq [int]$Correct.total_questions)
$first = $Correct.envelopes[0]
$first_envelope_ok = ($first.attempt_envelope_version -eq "v0.4.57" -and $first.attempt_mode -eq "dry_run_non_persistent")
$path_policy_ok = ($Correct.path_policy -eq "no_user_provided_filesystem_root" -and $Wrong.path_policy -eq "no_user_provided_filesystem_root")
$no_session_persist_ok = ($Correct.will_persist_session -eq $false -and $Wrong.will_persist_session -eq $false)
$no_attempt_persist_ok = ($Correct.will_persist_attempts -eq $false -and $Wrong.will_persist_attempts -eq $false)
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
Write-Host "id_ok $id_ok"
Write-Host "count_ok $count_ok"
Write-Host "correct_counts_ok $correct_counts_ok"
Write-Host "wrong_counts_ok $wrong_counts_ok"
Write-Host "average_correct_ok $average_correct_ok"
Write-Host "average_wrong_ok $average_wrong_ok"
Write-Host "feedback_ok $feedback_ok"
Write-Host "envelopes_ok $envelopes_ok"
Write-Host "first_envelope_ok $first_envelope_ok"
Write-Host "path_policy_ok $path_policy_ok"
Write-Host "no_session_persist_ok $no_session_persist_ok"
Write-Host "no_attempt_persist_ok $no_attempt_persist_ok"
Write-Host "no_progress_ok $no_progress_ok"
Write-Host "no_live_score_ok $no_live_score_ok"
Write-Host "no_ui_ok $no_ui_ok"
Write-Host "no_weak_ok $no_weak_ok"
Write-Host "no_live_replace_ok $no_live_replace_ok"
Write-Host "no_legacy_replace_ok $no_legacy_replace_ok"
Write-Host "no_live_consumption_ok $no_live_consumption_ok"
Write-Host "no_cloud_ok $no_cloud_ok"

if (-not ($version_ok -and $mode_ok -and $source_ok -and $id_ok -and $count_ok -and $correct_counts_ok -and $wrong_counts_ok -and $average_correct_ok -and $average_wrong_ok -and $feedback_ok -and $envelopes_ok -and $first_envelope_ok -and $path_policy_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
  throw "LOCAL BANK DRY-RUN SESSION SUMMARY CHECK v0.4.58 FAILED"
}

Write-Host "LOCAL BANK DRY-RUN SESSION SUMMARY CHECK v0.4.58 PASS"

