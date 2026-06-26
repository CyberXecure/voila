$ErrorActionPreference = "Stop"

cd "D:\dev\projects\voila"

Write-Host "=== EXAM PREP LEARNING PATH CHECKPOINT v0.4.33 ==="

Write-Host "=== STOP BEFORE LEARNING PATH CHECK ==="
& .\scripts\dev\stop-voila.ps1 -Silent | Out-Host

Write-Host "=== START ==="
& .\scripts\dev\start-voila.ps1 -Silent | Out-Host
Start-Sleep -Seconds 3

try {
    $base = "http://127.0.0.1:8787"

    $routes = @(
        "/health",
        "/",
        "/quick-tools",
        "/exam-prep",
        "/exam-prep/skill/derivate"
    )

    foreach ($route in $routes) {
        $resp = Invoke-WebRequest -Uri "$base$route" -UseBasicParsing -TimeoutSec 10
        Write-Host "$route $($resp.StatusCode)"
        if ($resp.StatusCode -ne 200) {
            throw "Route failed: $route"
        }
    }

    $dashboard = (Invoke-WebRequest -Uri "$base/exam-prep" -UseBasicParsing -TimeoutSec 10).Content
    $detail = (Invoke-WebRequest -Uri "$base/exam-prep/skill/derivate" -UseBasicParsing -TimeoutSec 10).Content
    $combined = $dashboard + $detail

    $dashboardNextIndex = $dashboard.IndexOf("exam-prep-dashboard-next-action-v0417")
    $dashboardLearningIndex = $dashboard.IndexOf("exam-prep-dashboard-learning-path-v0432")
    $dashboardSummaryIndex = $dashboard.IndexOf("exam-prep-progress-summary-v0410")

    $detailMetadataIndex = $detail.IndexOf("exam-prep-skill-metadata-v0427")
    $detailLearningIndex = $detail.IndexOf("exam-prep-learning-path-v0431")
    $detailRelatedIndex = $detail.IndexOf("exam-prep-related-study-questions-v0415")
    $detailNextIndex = $detail.IndexOf("exam-prep-next-action-v0416")

    $checks = [ordered]@{
        "dashboard_has_learning_path_marker_v0432" = ($dashboardLearningIndex -ge 0)
        "dashboard_has_traseu_recomandat" = ($dashboard -cmatch "Traseu recomandat")
        "dashboard_has_skill_recomandat" = ($dashboard -cmatch "Skill recomandat")
        "dashboard_has_status_curent" = ($dashboard -cmatch "Status curent")
        "dashboard_has_vezi_traseul" = ($dashboard -cmatch "Vezi traseul de învățare")
        "dashboard_has_skill_detail_link" = ($dashboard -cmatch "/exam-prep/skill/")
        "dashboard_order_next_before_learning_path" = ($dashboardNextIndex -ge 0 -and $dashboardLearningIndex -gt $dashboardNextIndex)
        "dashboard_order_learning_path_before_summary" = ($dashboardLearningIndex -ge 0 -and $dashboardSummaryIndex -gt $dashboardLearningIndex)

        "detail_has_learning_path_marker_v0431" = ($detailLearningIndex -ge 0)
        "detail_has_traseu_de_invatare" = ($detail -cmatch "Traseu de învățare")
        "detail_has_skill_curent" = ($detail -cmatch "Skill curent")
        "detail_has_conditii_preliminare" = ($detail -cmatch "Condiții preliminare")
        "detail_has_urmatorul_pas" = ($detail -cmatch "Următorul pas")
        "detail_order_metadata_before_learning_path" = ($detailMetadataIndex -ge 0 -and $detailLearningIndex -gt $detailMetadataIndex)
        "detail_order_learning_path_before_related" = ($detailLearningIndex -ge 0 -and $detailRelatedIndex -gt $detailLearningIndex)
        "detail_order_related_before_next_action" = ($detailRelatedIndex -ge 0 -and $detailNextIndex -gt $detailRelatedIndex)

        "combined_has_modul_studiu" = ($combined -cmatch "Modul Studiu")
        "combined_has_pregatire_examene" = ($combined -cmatch "Pregătire examene")
        "combined_has_consolidat" = ($combined -cmatch "Consolidat")
        "combined_no_old_mixed_wording" = ($combined -cnotmatch "Întrebări Study legate|Continuă în Study Mode|Înapoi la Exam Prep")
        "combined_no_ascii_ro_regressions" = ($combined -cnotmatch ">Functii<|Functii,|Status: In progres|>In progres<")
        "combined_no_stapanire" = ($combined -cnotmatch "Stăpânire|stăpânire|Stapanire|stapanire")
        "technical_slug_functii_allowed" = ($combined -cmatch "/exam-prep/skill/functii")
    }

    foreach ($item in $checks.GetEnumerator()) {
        Write-Host "$($item.Key) $($item.Value)"
    }

    if ($checks.Values -contains $false) {
        throw "EXAM PREP LEARNING PATH CHECKPOINT v0.4.33 FAILED"
    }

    Write-Host "EXAM PREP LEARNING PATH CHECKPOINT v0.4.33 PASS"
}
finally {
    Write-Host "=== STOP AFTER LEARNING PATH CHECK ==="
    & .\scripts\dev\stop-voila.ps1 -Silent | Out-Host
}
