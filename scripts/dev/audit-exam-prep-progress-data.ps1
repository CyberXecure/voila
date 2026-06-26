param(
    [ValidateSet("Check", "WriteReport")]
    [string]$Mode = "Check"
)

$ErrorActionPreference = "Stop"

cd "D:\dev\projects\voila"

Write-Host "=== EXAM PREP REAL PROGRESS DATA AUDIT v0.4.42 ==="
Write-Host "Mode: $Mode"

$examPath = ".\services\api\exam_prep.py"
$webPath = ".\services\api\web_app.py"
$studyBuilderPath = ".\services\api\study_quiz_builder.py"
$smokePath = ".\scripts\dev\smoke-exam-prep-skill-detail.ps1"
$healthPath = ".\scripts\dev\check-exam-prep-health.ps1"
$coveragePath = ".\scripts\dev\check-exam-prep-skill-coverage.ps1"
$learningPath = ".\scripts\dev\check-exam-prep-learning-path.ps1"
$studyProgressPath = ".\scripts\dev\check-exam-prep-study-progress-copy.ps1"
$compactnessPath = ".\scripts\dev\check-exam-prep-compactness.ps1"
$skillTreePath = ".\assets\exam_prep\bac\matematica_m1\skill_tree.json"
$reportPath = ".\docs\dev\exam-prep-real-progress-data-audit.md"

$exam = if (Test-Path $examPath) { Get-Content $examPath -Raw } else { "" }
$web = if (Test-Path $webPath) { Get-Content $webPath -Raw } else { "" }
$studyBuilder = if (Test-Path $studyBuilderPath) { Get-Content $studyBuilderPath -Raw } else { "" }
$smoke = if (Test-Path $smokePath) { Get-Content $smokePath -Raw } else { "" }
$health = if (Test-Path $healthPath) { Get-Content $healthPath -Raw } else { "" }
$coverage = if (Test-Path $coveragePath) { Get-Content $coveragePath -Raw } else { "" }
$learning = if (Test-Path $learningPath) { Get-Content $learningPath -Raw } else { "" }
$studyProgress = if (Test-Path $studyProgressPath) { Get-Content $studyProgressPath -Raw } else { "" }
$compactness = if (Test-Path $compactnessPath) { Get-Content $compactnessPath -Raw } else { "" }
$skillTree = if (Test-Path $skillTreePath) { Get-Content $skillTreePath -Raw } else { "" }

# Runtime/content sources are separated from guard scripts because guard scripts intentionally contain
# forbidden-word regexes such as Stăpânire|stapanire.
$runtimeCombined = $exam + "`n" + $web + "`n" + $studyBuilder + "`n" + $skillTree
$checkpointCombined = $smoke + "`n" + $health + "`n" + $coverage + "`n" + $learning + "`n" + $studyProgress + "`n" + $compactness
$sourceCombined = $runtimeCombined + "`n" + $checkpointCombined

$sourceChecks = [ordered]@{
    "source_has_exam_prep_py" = (Test-Path $examPath)
    "source_has_web_app_py" = (Test-Path $webPath)
    "source_has_study_quiz_builder_py" = (Test-Path $studyBuilderPath)
    "source_has_skill_tree" = (Test-Path $skillTreePath)

    "source_has_dashboard_progress_summary" = ($sourceCombined -cmatch "exam-prep-progress-summary-v0410")
    "source_has_skill_detail_progress" = ($sourceCombined -cmatch "skill_has_progress" -or $sourceCombined -cmatch "current_status" -or $sourceCombined -cmatch "Status curent")
    "source_has_study_session_entry" = ($sourceCombined -cmatch "exam-prep-study-session-entry-v0435")
    "source_has_progress_interpretation" = ($sourceCombined -cmatch "exam-prep-progress-interpretation-v0436")
    "source_has_weak_review_entry" = ($sourceCombined -cmatch "exam-prep-weak-review-entry-v0428")
    "source_has_learning_path" = ($sourceCombined -cmatch "exam-prep-learning-path-v0431" -and $sourceCombined -cmatch "exam-prep-dashboard-learning-path-v0432")
    "source_has_metadata" = ($sourceCombined -cmatch "exam-prep-skill-metadata-v0427")
    "source_has_compactness_checkpoint" = ($sourceCombined -cmatch "check-exam-prep-compactness.ps1")
    "source_has_study_progress_checkpoint" = ($sourceCombined -cmatch "check-exam-prep-study-progress-copy.ps1")

    "source_has_progress_terms_nepornit" = ($sourceCombined -cmatch "Nepornit")
    "source_has_progress_terms_in_progres" = ($sourceCombined -cmatch "În progres")
    "source_has_progress_terms_consolidat" = ($sourceCombined -cmatch "Consolidat")
    "runtime_source_no_stapanire" = ($runtimeCombined -cnotmatch "Stăpânire|stăpânire|Stapanire|stapanire")
}

Write-Host "=== SOURCE AUDIT CHECKS ==="
foreach ($item in $sourceChecks.GetEnumerator()) {
    Write-Host "$($item.Key) $($item.Value)"
}

if ($sourceChecks.Values -contains $false) {
    throw "EXAM PREP SOURCE PROGRESS DATA AUDIT v0.4.42 FAILED"
}

Write-Host "=== ROUTE AUDIT CHECKS ==="
& .\scripts\dev\stop-voila.ps1 -Silent | Out-Host
& .\scripts\dev\start-voila.ps1 -Silent | Out-Host
Start-Sleep -Seconds 3

try {
    $base = "http://127.0.0.1:8787"

    $dashboard = (Invoke-WebRequest -Uri "$base/exam-prep" -UseBasicParsing -TimeoutSec 10).Content
    $detail = (Invoke-WebRequest -Uri "$base/exam-prep/skill/derivate" -UseBasicParsing -TimeoutSec 10).Content
    $combined = $dashboard + $detail

    $routeChecks = [ordered]@{
        "route_dashboard_has_progress_summary" = ($dashboard -cmatch "exam-prep-progress-summary-v0410")
        "route_dashboard_has_progress_interpretation" = ($dashboard -cmatch "exam-prep-progress-interpretation-v0436")
        "route_dashboard_has_learning_path" = ($dashboard -cmatch "exam-prep-dashboard-learning-path-v0432")
        "route_dashboard_has_weak_review" = ($dashboard -cmatch "exam-prep-weak-review-entry-v0428")
        "route_dashboard_has_compactness" = ($dashboard -cmatch "exam-prep-dashboard-compact-v0438")

        "route_detail_has_metadata" = ($detail -cmatch "exam-prep-skill-metadata-v0427")
        "route_detail_has_learning_path" = ($detail -cmatch "exam-prep-learning-path-v0431")
        "route_detail_has_related_questions" = ($detail -cmatch "exam-prep-related-study-questions-v0415")
        "route_detail_has_study_session_entry" = ($detail -cmatch "exam-prep-study-session-entry-v0435")
        "route_detail_has_progress_interpretation" = ($detail -cmatch "exam-prep-progress-interpretation-v0436")
        "route_detail_has_next_action" = ($detail -cmatch "exam-prep-next-action-v0416")
        "route_detail_has_weak_review" = ($detail -cmatch "exam-prep-weak-review-entry-v0428")
        "route_detail_has_compactness" = ($detail -cmatch "exam-prep-skill-detail-compact-v0439")

        "route_combined_has_modul_studiu" = ($combined -cmatch "Modul Studiu")
        "route_combined_has_pregatire_examene" = ($combined -cmatch "Pregătire examene")
        "route_combined_has_consolidat" = ($combined -cmatch "Consolidat")
        "route_combined_has_no_threshold_change_copy" = ($combined -cmatch "nu modifică scorurile, pragurile sau BKT")
        "route_combined_no_old_wording" = ($combined -cnotmatch "Întrebări Study legate|Continuă în Study Mode|Înapoi la Exam Prep")
        "route_combined_no_stapanire" = ($combined -cnotmatch "Stăpânire|stăpânire|Stapanire|stapanire")
    }

    foreach ($item in $routeChecks.GetEnumerator()) {
        Write-Host "$($item.Key) $($item.Value)"
    }

    if ($routeChecks.Values -contains $false) {
        throw "EXAM PREP ROUTE PROGRESS DATA AUDIT v0.4.42 FAILED"
    }
}
finally {
    & .\scripts\dev\stop-voila.ps1 -Silent | Out-Host
}

$report = @"
# Exam Prep real progress data audit — v0.4.42

This is a read-only audit. It documents the current Exam Prep progress-related data flow without changing runtime logic.

## Audit result

PASS.

## Current visible progress surfaces

The current Exam Prep UI exposes progress-related information through:

- dashboard progress summary
- dashboard recommended next action
- dashboard learning path entry
- dashboard weak review entry
- skill detail metadata
- skill detail learning path
- related Study Mode questions
- Study Mode entry
- progress interpretation helper
- skill detail next action
- skill detail weak review entry

## Current protected scripts

The following checkpoint scripts protect the current behavior:

````powershell
& .\scripts\dev\check-exam-prep-skill-coverage.ps1
& .\scripts\dev\check-exam-prep-learning-path.ps1
& .\scripts\dev\check-exam-prep-study-progress-copy.ps1
& .\scripts\dev\check-exam-prep-compactness.ps1
& .\scripts\dev\smoke-exam-prep-skill-detail.ps1
& .\scripts\dev\check-exam-prep-health.ps1
````

## Current data-source map

| Surface | Current audited evidence | Notes |
|---|---|---|
| Dashboard progress summary | `exam-prep-progress-summary-v0410` | Read-only summary surface. |
| Skill detail status/progress | skill detail route + smoke checks | Uses existing progress/status display. |
| Study Mode connection | `exam-prep-study-session-entry-v0435` | Explains that progress updates after answering in Modul Studiu. |
| Progress interpretation | `exam-prep-progress-interpretation-v0436` | Explains `Nepornit`, `În progres`, `Consolidat`; does not modify thresholds. |
| Weak review | `exam-prep-weak-review-entry-v0428` | Read-only entry/link surface for weak concepts. |
| Learning path | `exam-prep-learning-path-v0431` and `exam-prep-dashboard-learning-path-v0432` | Preserves recommended path display. |
| Skill metadata | `exam-prep-skill-metadata-v0427` | Preserves skill metadata display. |
| Sample skill tree | `assets/exam_prep/bac/matematica_m1/skill_tree.json` | Sample coverage verifies multimi/functii/derivate/integrale/geometrie. |

## Important limitation

This audit confirms the current progress-related UI surfaces and checkpoint coverage.

It does not claim that generated practice questions are already deep, varied, exam-grade, or fully skill-specific. That must be audited separately.

## Non-goals

This audit did not change:

- BKT
- scoring thresholds
- Study Mode engine
- Review weak concepts engine
- Progress engine
- quiz generation
- OCR
- PDF processing
- course generation
- packaging
- ZIP/release assets

## Recommended next step

Proceed with a read-only generated question quality audit before changing generation logic.

Suggested next milestone:

- v0.4.43 — Exam Prep generated question quality audit
"@

if ($Mode -eq "WriteReport") {
    Set-Content -Path $reportPath -Value $report -Encoding UTF8
    Write-Host "Report written: $reportPath"
}

Write-Host "EXAM PREP REAL PROGRESS DATA AUDIT v0.4.42 PASS"
