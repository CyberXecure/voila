param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK QUESTION QUALITY GATE CHECK v0.4.54 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$Raw = python .\services\api\exam_prep_local_bank_question_quality_gate.py --course-id v054-smoke --skill-id local_concept_001_functiile --limit 12 --expect-needs-improvement
if ($LASTEXITCODE -ne 0) { throw "question quality gate did not detect needs_improvement" }
Write-Host $Raw

$Gate = $Raw | ConvertFrom-Json

$version_ok = ($Gate.quality_gate_version -eq "v0.4.54")
$mode_ok = ($Gate.mode -eq "dry_run_question_quality_gate")
$status_ok = ($Gate.quality_status -eq "needs_improvement")
$pass_false_ok = ($Gate.quality_gate_pass -eq $false)
$source_ok = ($Gate.selected_source -eq "local_exercise_bank_adapter")
$count_ok = ([int]$Gate.question_count -gt 0)
$type_counts_ok = (@($Gate.question_type_counts.PSObject.Properties).Count -ge 1)
$difficulty_counts_ok = (@($Gate.difficulty_counts.PSObject.Properties).Count -ge 1)
$skill_counts_ok = (@($Gate.skill_counts.PSObject.Properties).Count -ge 1)
$repetitive_detected_ok = ([int]$Gate.repetitive_prefix_count -gt 0)
$simple_detected_ok = ([int]$Gate.simple_question_count -gt 0)
$issues_detected_ok = (@($Gate.issues).Count -gt 0)
$has_repetitive_issue_ok = (@($Gate.issues) -contains "repetitive_concept_recognition_prefix")
$has_simple_issue_ok = (@($Gate.issues) -contains "questions_are_too_simple")
$has_diversity_issue_ok = (@($Gate.issues) -contains "insufficient_question_type_diversity")
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

Write-Host "version_ok $version_ok"
Write-Host "mode_ok $mode_ok"
Write-Host "status_ok $status_ok"
Write-Host "pass_false_ok $pass_false_ok"
Write-Host "source_ok $source_ok"
Write-Host "count_ok $count_ok"
Write-Host "type_counts_ok $type_counts_ok"
Write-Host "difficulty_counts_ok $difficulty_counts_ok"
Write-Host "skill_counts_ok $skill_counts_ok"
Write-Host "repetitive_detected_ok $repetitive_detected_ok"
Write-Host "simple_detected_ok $simple_detected_ok"
Write-Host "issues_detected_ok $issues_detected_ok"
Write-Host "has_repetitive_issue_ok $has_repetitive_issue_ok"
Write-Host "has_simple_issue_ok $has_simple_issue_ok"
Write-Host "has_diversity_issue_ok $has_diversity_issue_ok"
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

if (-not ($version_ok -and $mode_ok -and $status_ok -and $pass_false_ok -and $source_ok -and $count_ok -and $type_counts_ok -and $difficulty_counts_ok -and $skill_counts_ok -and $repetitive_detected_ok -and $simple_detected_ok -and $issues_detected_ok -and $has_repetitive_issue_ok -and $has_simple_issue_ok -and $has_diversity_issue_ok -and $required_fields_ok -and $path_policy_ok -and $no_attempt_ok -and $no_progress_ok -and $no_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
  throw "LOCAL BANK QUESTION QUALITY GATE CHECK v0.4.54 FAILED"
}

Write-Host "LOCAL BANK QUESTION QUALITY GATE CHECK v0.4.54 PASS"

