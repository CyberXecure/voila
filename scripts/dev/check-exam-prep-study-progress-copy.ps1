$ErrorActionPreference = "Stop"
cd "D:\dev\projects\voila"
Write-Host "=== EXAM PREP STUDY/PROGRESS COPY CHECKPOINT v0.4.37 ==="
Write-Host "=== STOP BEFORE STUDY/PROGRESS COPY CHECK ==="
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
    $relatedIndex = $detail.IndexOf("exam-prep-related-study-questions-v0415")
    $studyIndex = $detail.IndexOf("exam-prep-study-session-entry-v0435")
    $nextIndex = $detail.IndexOf("exam-prep-next-action-v0416")
    $summaryIndex = $dashboard.IndexOf("exam-prep-progress-summary-v0410")
    $dashboardInterpretationIndex = $dashboard.IndexOf("exam-prep-progress-interpretation-v0436")
    $detailInterpretationIndex = $detail.IndexOf("exam-prep-progress-interpretation-v0436")
    $checks = [ordered]@{
        "detail_has_study_session_marker_v0435" = ($studyIndex -ge 0)
        "detail_has_study_session_title" = ($detail -cmatch "Intrare în Modul Studiu")
        "detail_has_progress_update_copy" = ($detail -cmatch "Răspunde la întrebări în Modul Studiu" -and $detail -cmatch "progresul Exam Prep se va actualiza aici")
        "detail_has_continue_modul_studiu_cta" = ($detail -cmatch "Continuă în Modul Studiu")
        "detail_order_related_before_study_entry" = ($relatedIndex -ge 0 -and $studyIndex -gt $relatedIndex)
        "detail_order_study_entry_before_next_action" = ($studyIndex -ge 0 -and $nextIndex -gt $studyIndex)
        "dashboard_has_progress_interpretation_marker_v0436" = ($dashboardInterpretationIndex -ge 0)
        "detail_has_progress_interpretation_marker_v0436" = ($detailInterpretationIndex -ge 0)
        "combined_has_progress_interpretation_title" = ($combined -cmatch "Cum interpretăm progresul")
        "combined_has_nepornit" = ($combined -cmatch "Nepornit")
        "combined_has_in_progres" = ($combined -cmatch "În progres")
        "combined_has_consolidat" = ($combined -cmatch "Consolidat")
        "combined_has_no_threshold_change_copy" = ($combined -cmatch "nu modifică scorurile, pragurile sau BKT")
        "dashboard_order_summary_before_interpretation" = ($summaryIndex -ge 0 -and $dashboardInterpretationIndex -gt $summaryIndex)
        "detail_order_study_before_interpretation" = ($studyIndex -ge 0 -and $detailInterpretationIndex -gt $studyIndex)
        "combined_has_modul_studiu" = ($combined -cmatch "Modul Studiu")
        "combined_has_pregatire_examene" = ($combined -cmatch "Pregătire examene")
        "combined_no_old_mixed_wording" = ($combined -cnotmatch "Întrebări Study legate|Continuă în Study Mode|Înapoi la Exam Prep")
        "combined_no_ascii_ro_regressions" = ($combined -cnotmatch ">Functii<|Functii,|Status: In progres|>In progres<")
        "combined_no_stapanire" = ($combined -cnotmatch "Stăpânire|stăpânire|Stapanire|stapanire")
        "technical_slug_functii_allowed" = ($combined -cmatch "/exam-prep/skill/functii")
    }
    foreach ($item in $checks.GetEnumerator()) { Write-Host "$($item.Key) $($item.Value)" }
    if ($checks.Values -contains $false) { throw "EXAM PREP STUDY/PROGRESS COPY CHECKPOINT v0.4.37 FAILED" }
    Write-Host "EXAM PREP STUDY/PROGRESS COPY CHECKPOINT v0.4.37 PASS"
}
finally {
    Write-Host "=== STOP AFTER STUDY/PROGRESS COPY CHECK ==="
    & .\scripts\dev\stop-voila.ps1 -Silent | Out-Host
}
