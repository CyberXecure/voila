param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK DRY-RUN SOURCE SELECTION CHECK v0.4.53 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$oldFlag = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION

try {
  Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION -ErrorAction SilentlyContinue

  $OffRaw = python .\services\api\exam_prep_local_bank_dry_run_source_selection.py --course-id v053-smoke --skill-id local_concept_001_functiile --limit 3 --strict-legacy
  if ($LASTEXITCODE -ne 0) { throw "dry-run source selection OFF check failed" }
  Write-Host $OffRaw

  $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION = "1"

  $OnRaw = python .\services\api\exam_prep_local_bank_dry_run_source_selection.py --course-id v053-smoke --skill-id local_concept_001_functiile --limit 3 --strict-local
  if ($LASTEXITCODE -ne 0) { throw "dry-run source selection ON check failed" }
  Write-Host $OnRaw

  $Off = $OffRaw | ConvertFrom-Json
  $On = $OnRaw | ConvertFrom-Json

  $version_ok = ($On.dry_run_version -eq "v0.4.53" -and $Off.dry_run_version -eq "v0.4.53")
  $mode_ok = ($On.mode -eq "dry_run_source_selection" -and $Off.mode -eq "dry_run_source_selection")
  $flag_name_ok = ($On.flag_name -eq "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION")
  $off_flag_ok = ($Off.flag_enabled -eq $false)
  $off_source_ok = ($Off.selected_source -eq "legacy_fallback")
  $off_status_ok = ($Off.dry_run_status -eq "legacy_fallback_selected_for_dry_run")
  $off_items_ok = ([int]$Off.dry_run_item_count -eq 0)
  $on_flag_ok = ($On.flag_enabled -eq $true)
  $on_source_ok = ($On.selected_source -eq "local_exercise_bank_adapter")
  $on_status_ok = ($On.dry_run_status -eq "local_bank_selected_for_dry_run")
  $on_items_ok = ([int]$On.dry_run_item_count -gt 0 -and [int]$On.dry_run_item_count -le 3)
  $first = $On.dry_run_items[0]
  $first_dry_run_ok = ($first.dry_run_only -eq $true)
  $first_has_question_ok = ([string]$first.question).Trim().Length -gt 0
  $first_has_answer_preview_ok = ([string]$first.correct_answer_preview).Trim().Length -gt 0
  $first_no_attempt_ok = ($first.will_save_attempt -eq $false)
  $first_no_progress_ok = ($first.will_update_progress -eq $false)
  $first_no_score_ok = ($first.will_score_answer -eq $false)
  $legacy_fallback_ok = ($On.legacy_fallback_available -eq $true -and $Off.legacy_fallback_available -eq $true)
  $path_policy_ok = ($On.path_policy -eq "no_user_provided_filesystem_root" -and $Off.path_policy -eq "no_user_provided_filesystem_root")
  $no_attempt_ok = ($On.will_save_attempt -eq $false -and $Off.will_save_attempt -eq $false)
  $no_progress_ok = ($On.will_update_progress -eq $false -and $Off.will_update_progress -eq $false)
  $no_score_ok = ($On.will_score_answer -eq $false -and $Off.will_score_answer -eq $false)
  $no_ui_ok = ($On.will_modify_exam_prep_ui -eq $false -and $Off.will_modify_exam_prep_ui -eq $false)
  $no_weak_ok = ($On.will_modify_weak_review -eq $false -and $Off.will_modify_weak_review -eq $false)
  $no_live_replace_ok = ($On.will_replace_live_study_session -eq $false -and $Off.will_replace_live_study_session -eq $false)
  $no_legacy_replace_ok = ($On.will_replace_legacy_generator -eq $false -and $Off.will_replace_legacy_generator -eq $false)
  $no_live_consumption_ok = ($On.will_enable_live_consumption -eq $false -and $Off.will_enable_live_consumption -eq $false)
  $no_cloud_ok = ($On.requires_cloud_or_api -eq $false -and $Off.requires_cloud_or_api -eq $false)

  Write-Host "version_ok $version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "flag_name_ok $flag_name_ok"
  Write-Host "off_flag_ok $off_flag_ok"
  Write-Host "off_source_ok $off_source_ok"
  Write-Host "off_status_ok $off_status_ok"
  Write-Host "off_items_ok $off_items_ok"
  Write-Host "on_flag_ok $on_flag_ok"
  Write-Host "on_source_ok $on_source_ok"
  Write-Host "on_status_ok $on_status_ok"
  Write-Host "on_items_ok $on_items_ok"
  Write-Host "first_dry_run_ok $first_dry_run_ok"
  Write-Host "first_has_question_ok $first_has_question_ok"
  Write-Host "first_has_answer_preview_ok $first_has_answer_preview_ok"
  Write-Host "first_no_attempt_ok $first_no_attempt_ok"
  Write-Host "first_no_progress_ok $first_no_progress_ok"
  Write-Host "first_no_score_ok $first_no_score_ok"
  Write-Host "legacy_fallback_ok $legacy_fallback_ok"
  Write-Host "path_policy_ok $path_policy_ok"
  Write-Host "no_attempt_ok $no_attempt_ok"
  Write-Host "no_progress_ok $no_progress_ok"
  Write-Host "no_score_ok $no_score_ok"
  Write-Host "no_ui_ok $no_ui_ok"
  Write-Host "no_weak_ok $no_weak_ok"
  Write-Host "no_live_replace_ok $no_live_replace_ok"
  Write-Host "no_legacy_replace_ok $no_legacy_replace_ok"
  Write-Host "no_live_consumption_ok $no_live_consumption_ok"
  Write-Host "no_cloud_ok $no_cloud_ok"

  if (-not ($version_ok -and $mode_ok -and $flag_name_ok -and $off_flag_ok -and $off_source_ok -and $off_status_ok -and $off_items_ok -and $on_flag_ok -and $on_source_ok -and $on_status_ok -and $on_items_ok -and $first_dry_run_ok -and $first_has_question_ok -and $first_has_answer_preview_ok -and $first_no_attempt_ok -and $first_no_progress_ok -and $first_no_score_ok -and $legacy_fallback_ok -and $path_policy_ok -and $no_attempt_ok -and $no_progress_ok -and $no_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
    throw "LOCAL BANK DRY-RUN SOURCE SELECTION CHECK v0.4.53 FAILED"
  }

  Write-Host "LOCAL BANK DRY-RUN SOURCE SELECTION CHECK v0.4.53 PASS"
} finally {
  if ($null -eq $oldFlag) {
    Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION -ErrorAction SilentlyContinue
  } else {
    $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION = $oldFlag
  }
}

