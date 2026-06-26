$ErrorActionPreference = "Stop"
cd "D:\dev\projects\voila"

Write-Host "=== EXAM PREP COMPACTNESS CHECKPOINT v0.4.40 ==="
Write-Host "=== STOP BEFORE COMPACTNESS CHECK ==="
& .\scripts\dev\stop-voila.ps1 -Silent | Out-Host

Write-Host "=== START ==="
& .\scripts\dev\start-voila.ps1 -Silent | Out-Host
Start-Sleep -Seconds 3

try {
    $base = "http://127.0.0.1:8787"
    foreach ($route in @("/health", "/", "/quick-tools", "/exam-prep", "/exam-prep/skill/derivate")) {
        $resp = Invoke-WebRequest -Uri "$base$route" -UseBasicParsing -TimeoutSec 10
        Write-Host "$route $($resp.StatusCode)"
        if ($resp.StatusCode -ne 200) { throw "Route failed: $route" }
    }

    $dashboard = (Invoke-WebRequest -Uri "$base/exam-prep" -UseBasicParsing -TimeoutSec 10).Content
    $detail = (Invoke-WebRequest -Uri "$base/exam-prep/skill/derivate" -UseBasicParsing -TimeoutSec 10).Content
    $combined = $dashboard + $detail

    $dashboardNextIndex = $dashboard.IndexOf("exam-prep-dashboard-next-action-v0417")
    $dashboardLearningIndex = $dashboard.IndexOf("exam-prep-dashboard-learning-path-v0432")
    $dashboardSummaryIndex = $dashboard.IndexOf("exam-prep-progress-summary-v0410")
    $dashboardInterpretationIndex = $dashboard.IndexOf("exam-prep-progress-interpretation-v0436")
    $dashboardCardsCandidates = @(
        $dashboard.IndexOf("exam-prep-dashboard-skill-cards-v0411"),
        $dashboard.IndexOf("exam-prep-skill-cards-v0411"),
        $dashboard.IndexOf("Skill-uri Exam Prep")
    ) | Where-Object { $_ -ge 0 }
    $dashboardCardsIndex = if ($dashboardCardsCandidates.Count -gt 0) { ($dashboardCardsCandidates | Measure-Object -Minimum).Minimum } else { -1 }
    $dashboardWeakIndex = $dashboard.IndexOf("exam-prep-weak-review-entry-v0428")

    $detailMetadataIndex = $detail.IndexOf("exam-prep-skill-metadata-v0427")
    $detailLearningIndex = $detail.IndexOf("exam-prep-learning-path-v0431")
    $detailRelatedIndex = $detail.IndexOf("exam-prep-related-study-questions-v0415")
    $detailStudyIndex = $detail.IndexOf("exam-prep-study-session-entry-v0435")
    $detailInterpretationIndex = $detail.IndexOf("exam-prep-progress-interpretation-v0436")
    $detailNextIndex = $detail.IndexOf("exam-prep-next-action-v0416")
    $detailWeakIndex = $detail.IndexOf("exam-prep-weak-review-entry-v0428")

    $checks = [ordered]@{
        "dashboard_has_v422_consolidated_marker" = ($dashboard -cmatch "exam-prep-dashboard-consolidated-v0422")
        "dashboard_has_compact_marker_v0438" = ($dashboard -cmatch "exam-prep-dashboard-compact-v0438")
        "dashboard_has_compact_style_v0438" = ($dashboard -cmatch "exam-prep-dashboard-compactness-v0438")
        "dashboard_has_compact_note_v0438" = ($dashboard -cmatch "Dashboard compact")
        "dashboard_keeps_next_action" = ($dashboardNextIndex -ge 0)
        "dashboard_keeps_learning_path" = ($dashboardLearningIndex -ge 0)
        "dashboard_keeps_progress_summary" = ($dashboardSummaryIndex -ge 0)
        "dashboard_keeps_progress_interpretation" = ($dashboardInterpretationIndex -ge 0)
        "dashboard_keeps_skill_cards" = ($dashboardCardsIndex -ge 0)
        "dashboard_keeps_weak_review" = ($dashboardWeakIndex -ge 0)
        "dashboard_order_next_learning_summary_interpretation_cards_weak" = ($dashboardNextIndex -ge 0 -and $dashboardLearningIndex -gt $dashboardNextIndex -and $dashboardSummaryIndex -gt $dashboardLearningIndex -and $dashboardInterpretationIndex -gt $dashboardSummaryIndex -and $dashboardCardsIndex -gt $dashboardInterpretationIndex -and $dashboardWeakIndex -gt $dashboardCardsIndex)
        "detail_has_v423_consolidated_marker" = ($detail -cmatch "exam-prep-skill-detail-consolidated-v0423")
        "detail_has_compact_marker_v0439" = ($detail -cmatch "exam-prep-skill-detail-compact-v0439")
        "detail_has_compact_style_v0439" = ($detail -cmatch "exam-prep-skill-detail-compactness-v0439")
        "detail_has_compact_note_v0439" = ($detail -cmatch "Detaliu skill compact")
        "detail_keeps_metadata" = ($detailMetadataIndex -ge 0)
        "detail_keeps_learning_path" = ($detailLearningIndex -ge 0)
        "detail_keeps_related_questions" = ($detailRelatedIndex -ge 0)
        "detail_keeps_study_entry" = ($detailStudyIndex -ge 0)
        "detail_keeps_progress_interpretation" = ($detailInterpretationIndex -ge 0)
        "detail_keeps_next_action" = ($detailNextIndex -ge 0)
        "detail_keeps_weak_review" = ($detailWeakIndex -ge 0)
        "detail_order_metadata_learning_related_study_progress_next_weak" = ($detailMetadataIndex -ge 0 -and $detailLearningIndex -gt $detailMetadataIndex -and $detailRelatedIndex -gt $detailLearningIndex -and $detailStudyIndex -gt $detailRelatedIndex -and $detailInterpretationIndex -gt $detailStudyIndex -and $detailNextIndex -gt $detailInterpretationIndex -and $detailWeakIndex -gt $detailNextIndex)
        "combined_has_modul_studiu" = ($combined -cmatch "Modul Studiu")
        "combined_has_pregatire_examene" = ($combined -cmatch "Pregătire examene")
        "combined_has_consolidat" = ($combined -cmatch "Consolidat")
        "combined_no_old_mixed_wording" = ($combined -cnotmatch "Întrebări Study legate|Continuă în Study Mode|Înapoi la Exam Prep")
        "combined_no_ascii_ro_regressions" = ($combined -cnotmatch ">Functii<|Functii,|Status: In progres|>In progres<")
        "combined_no_stapanire" = ($combined -cnotmatch "Stăpânire|stăpânire|Stapanire|stapanire")
        "technical_slug_functii_allowed" = ($combined -cmatch "/exam-prep/skill/functii")
    }

    foreach ($item in $checks.GetEnumerator()) { Write-Host "$($item.Key) $($item.Value)" }
    if ($checks.Values -contains $false) { throw "EXAM PREP COMPACTNESS CHECKPOINT v0.4.40 FAILED" }
    Write-Host "EXAM PREP COMPACTNESS CHECKPOINT v0.4.40 PASS"
}
finally {
    Write-Host "=== STOP AFTER COMPACTNESS CHECK ==="
    & .\scripts\dev\stop-voila.ps1 -Silent | Out-Host
}
