param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK QUESTION QUALITY GATE CHECK v0.4.55 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$Raw = python .\services\api\exam_prep_local_bank_question_quality_gate.py --course-id v055-smoke --skill-id local_concept_001_functiile --limit 12 --expect-pass
if ($LASTEXITCODE -ne 0) { throw "question quality gate did not pass after v0.4.55 variety upgrade" }
Write-Host $Raw

$Gate = $Raw | ConvertFrom-Json

$quality_gate_version_ok = ($Gate.quality_gate_version -eq "v0.4.54")
$status_ok = ($Gate.quality_status -eq "pass")
$pass_true_ok = ($Gate.quality_gate_pass -eq $true)
$source_ok = ($Gate.selected_source -eq "local_exercise_bank_adapter")
$count_ok = ([int]$Gate.question_count -ge 5)
$type_diversity_ok = (@($Gate.question_type_counts.PSObject.Properties).Count -ge 2)
$difficulty_counts_ok = (@($Gate.difficulty_counts.PSObject.Properties).Count -ge 1)
$skill_counts_ok = (@($Gate.skill_counts.PSObject.Properties).Count -ge 1)
$repetitive_ratio_ok = ([double]$Gate.repetitive_prefix_ratio -le [double]$Gate.maximum_repetitive_prefix_ratio_for_pass)
$simple_ratio_ok = ([double]$Gate.simple_question_ratio -le [double]$Gate.maximum_repetitive_prefix_ratio_for_pass)
$issues_empty_ok = (@($Gate.issues).Count -eq 0)
$required_fields_ok = (@($Gate.missing_required_field_issues).Count -eq 0)
$path_policy_ok = ($Gate.path_policy -eq "no_user_provided_filesystem_root")
$no_attempt_ok = ($Gate.will_save_attempt -eq $false)
$no_progress_ok = ($Gate.will_update_progress -eq $false)
$no_score_ok = ($Gate.will_score_answer -eq $false)
$no_ui_ok = ($Gate.will_modify_exam_prep_ui -eq $false)
$no_weak_ok = ($Gate.will_modify_weak_review -eq $false)
$no_live_replace_ok = ($Gate.will_replace_live_study_session -eq $false)
$no_legacy_replace_ok = ($Gate.will_replace_legacy_generator -eq $false)
$no_live_consumption_ok = ($Gate.will_enable_live_consumption -eq $false)
$no_cloud_ok = ($Gate.requires_cloud_or_api -eq $false)

Write-Host "quality_gate_version_ok $quality_gate_version_ok"
Write-Host "status_ok $status_ok"
Write-Host "pass_true_ok $pass_true_ok"
Write-Host "source_ok $source_ok"
Write-Host "count_ok $count_ok"
Write-Host "type_diversity_ok $type_diversity_ok"
Write-Host "difficulty_counts_ok $difficulty_counts_ok"
Write-Host "skill_counts_ok $skill_counts_ok"
Write-Host "repetitive_ratio_ok $repetitive_ratio_ok"
Write-Host "simple_ratio_ok $simple_ratio_ok"
Write-Host "issues_empty_ok $issues_empty_ok"
Write-Host "required_fields_ok $required_fields_ok"
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

if (-not ($quality_gate_version_ok -and $status_ok -and $pass_true_ok -and $source_ok -and $count_ok -and $type_diversity_ok -and $difficulty_counts_ok -and $skill_counts_ok -and $repetitive_ratio_ok -and $simple_ratio_ok -and $issues_empty_ok -and $required_fields_ok -and $path_policy_ok -and $no_attempt_ok -and $no_progress_ok -and $no_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
  throw "LOCAL BANK QUESTION QUALITY GATE CHECK v0.4.55 FAILED"
}

Write-Host "LOCAL BANK QUESTION QUALITY GATE CHECK v0.4.55 PASS"

