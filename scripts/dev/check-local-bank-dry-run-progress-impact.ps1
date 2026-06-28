param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK DRY-RUN PROGRESS IMPACT PREVIEW CHECK v0.4.59 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$UpRaw = python .\services\api\exam_prep_local_bank_dry_run_progress_impact.py --course-id v059-smoke --skill-id local_concept_001_functiile --limit 5 --sample-mode correct --old-mastery-preview 0.40 --expect-increase
if ($LASTEXITCODE -ne 0) { throw "dry-run progress impact increase sample failed" }
Write-Host $UpRaw

$DownRaw = python .\services\api\exam_prep_local_bank_dry_run_progress_impact.py --course-id v059-smoke --skill-id local_concept_001_functiile --limit 5 --sample-mode wrong --old-mastery-preview 0.40 --expect-decrease
if ($LASTEXITCODE -ne 0) { throw "dry-run progress impact decrease sample failed" }
Write-Host $DownRaw

$Up = $UpRaw | ConvertFrom-Json
$Down = $DownRaw | ConvertFrom-Json

$version_ok = ($Up.progress_impact_preview_version -eq "v0.4.59" -and $Down.progress_impact_preview_version -eq "v0.4.59")
$mode_ok = ($Up.mode -eq "dry_run_progress_impact_preview" -and $Down.mode -eq "dry_run_progress_impact_preview")
$source_ok = ($Up.selected_source -eq "local_exercise_bank_adapter" -and $Down.selected_source -eq "local_exercise_bank_adapter")
$increase_ok = ($Up.impact_direction -eq "increase" -and [double]$Up.mastery_delta_preview -gt 0)
$decrease_ok = ($Down.impact_direction -eq "decrease" -and [double]$Down.mastery_delta_preview -lt 0)
$new_mastery_up_ok = ([double]$Up.new_mastery_preview -gt [double]$Up.old_mastery_preview)
$new_mastery_down_ok = ([double]$Down.new_mastery_preview -lt [double]$Down.old_mastery_preview)
$delta_shape_ok = (
  [string]$Up.progress_delta_preview.skill_id -eq "local_concept_001_functiile" -and
  [int]$Up.progress_delta_preview.total_questions -gt 0
)
$session_ok = ($Up.dry_run_session_summary.session_summary_version -eq "v0.4.58")
$path_policy_ok = ($Up.path_policy -eq "no_user_provided_filesystem_root" -and $Down.path_policy -eq "no_user_provided_filesystem_root")
$no_progress_persist_ok = ($Up.will_persist_progress -eq $false -and $Down.will_persist_progress -eq $false)
$no_session_persist_ok = ($Up.will_persist_session -eq $false -and $Down.will_persist_session -eq $false)
$no_attempt_persist_ok = ($Up.will_persist_attempts -eq $false -and $Down.will_persist_attempts -eq $false)
$no_progress_update_ok = ($Up.will_update_progress -eq $false -and $Down.will_update_progress -eq $false)
$no_live_score_ok = ($Up.will_score_live_session -eq $false -and $Down.will_score_live_session -eq $false)
$no_ui_ok = ($Up.will_modify_exam_prep_ui -eq $false -and $Down.will_modify_exam_prep_ui -eq $false)
$no_weak_ok = ($Up.will_modify_weak_review -eq $false -and $Down.will_modify_weak_review -eq $false)
$no_live_replace_ok = ($Up.will_replace_live_study_session -eq $false -and $Down.will_replace_live_study_session -eq $false)
$no_legacy_replace_ok = ($Up.will_replace_legacy_generator -eq $false -and $Down.will_replace_legacy_generator -eq $false)
$no_live_consumption_ok = ($Up.will_enable_live_consumption -eq $false -and $Down.will_enable_live_consumption -eq $false)
$no_cloud_ok = ($Up.requires_cloud_or_api -eq $false -and $Down.requires_cloud_or_api -eq $false)

Write-Host "version_ok $version_ok"
Write-Host "mode_ok $mode_ok"
Write-Host "source_ok $source_ok"
Write-Host "increase_ok $increase_ok"
Write-Host "decrease_ok $decrease_ok"
Write-Host "new_mastery_up_ok $new_mastery_up_ok"
Write-Host "new_mastery_down_ok $new_mastery_down_ok"
Write-Host "delta_shape_ok $delta_shape_ok"
Write-Host "session_ok $session_ok"
Write-Host "path_policy_ok $path_policy_ok"
Write-Host "no_progress_persist_ok $no_progress_persist_ok"
Write-Host "no_session_persist_ok $no_session_persist_ok"
Write-Host "no_attempt_persist_ok $no_attempt_persist_ok"
Write-Host "no_progress_update_ok $no_progress_update_ok"
Write-Host "no_live_score_ok $no_live_score_ok"
Write-Host "no_ui_ok $no_ui_ok"
Write-Host "no_weak_ok $no_weak_ok"
Write-Host "no_live_replace_ok $no_live_replace_ok"
Write-Host "no_legacy_replace_ok $no_legacy_replace_ok"
Write-Host "no_live_consumption_ok $no_live_consumption_ok"
Write-Host "no_cloud_ok $no_cloud_ok"

if (-not ($version_ok -and $mode_ok -and $source_ok -and $increase_ok -and $decrease_ok -and $new_mastery_up_ok -and $new_mastery_down_ok -and $delta_shape_ok -and $session_ok -and $path_policy_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
  throw "LOCAL BANK DRY-RUN PROGRESS IMPACT PREVIEW CHECK v0.4.59 FAILED"
}

Write-Host "LOCAL BANK DRY-RUN PROGRESS IMPACT PREVIEW CHECK v0.4.59 PASS"

