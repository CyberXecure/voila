param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK CONTROLLED CONSUMPTION FLAG CHECK v0.4.52 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$oldFlag = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION

try {
  Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION -ErrorAction SilentlyContinue

  $OffRaw = python .\services\api\exam_prep_local_bank_consumption_flag.py --course-id v052-smoke --skill-id local_concept_001_functiile --limit 3 --strict-disabled
  if ($LASTEXITCODE -ne 0) { throw "consumption flag OFF check failed" }
  Write-Host $OffRaw

  $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION = "1"

  $OnRaw = python .\services\api\exam_prep_local_bank_consumption_flag.py --course-id v052-smoke --skill-id local_concept_001_functiile --limit 3 --strict-enabled
  if ($LASTEXITCODE -ne 0) { throw "consumption flag ON check failed" }
  Write-Host $OnRaw

  $Off = $OffRaw | ConvertFrom-Json
  $On = $OnRaw | ConvertFrom-Json

  $version_ok = ($On.consumption_flag_version -eq "v0.4.52" -and $Off.consumption_flag_version -eq "v0.4.52")
  $mode_ok = ($On.mode -eq "controlled_consumption_flag_scaffold" -and $Off.mode -eq "controlled_consumption_flag_scaffold")
  $flag_name_ok = ($On.flag_name -eq "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION")
  $off_flag_ok = ($Off.flag_enabled -eq $false)
  $off_source_ok = ($Off.selected_source -eq "legacy_fallback")
  $off_reason_ok = ($Off.selection_reason -eq "flag_disabled_legacy_default")
  $on_flag_ok = ($On.flag_enabled -eq $true)
  $on_source_ok = ($On.selected_source -eq "local_exercise_bank_adapter")
  $on_reason_ok = ($On.selection_reason -eq "flag_enabled_and_valid_local_preview_available")
  $local_available_ok = ($On.local_preview_available -eq $true -and [int]$On.local_preview_question_count -gt 0)
  $selected_questions_ok = ([int]$On.selected_question_count -gt 0 -and @($On.selected_questions).Count -gt 0)
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
  Write-Host "off_reason_ok $off_reason_ok"
  Write-Host "on_flag_ok $on_flag_ok"
  Write-Host "on_source_ok $on_source_ok"
  Write-Host "on_reason_ok $on_reason_ok"
  Write-Host "local_available_ok $local_available_ok"
  Write-Host "selected_questions_ok $selected_questions_ok"
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

  if (-not ($version_ok -and $mode_ok -and $flag_name_ok -and $off_flag_ok -and $off_source_ok -and $off_reason_ok -and $on_flag_ok -and $on_source_ok -and $on_reason_ok -and $local_available_ok -and $selected_questions_ok -and $legacy_fallback_ok -and $path_policy_ok -and $no_attempt_ok -and $no_progress_ok -and $no_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
    throw "LOCAL BANK CONTROLLED CONSUMPTION FLAG CHECK v0.4.52 FAILED"
  }

  Write-Host "LOCAL BANK CONTROLLED CONSUMPTION FLAG CHECK v0.4.52 PASS"
} finally {
  if ($null -eq $oldFlag) {
    Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION -ErrorAction SilentlyContinue
  } else {
    $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION = $oldFlag
  }
}

