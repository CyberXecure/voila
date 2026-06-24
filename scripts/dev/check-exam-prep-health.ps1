$ErrorActionPreference = "Stop"

cd "D:\dev\projects\voila"

$base = "http://127.0.0.1:8787"

function Invoke-VoilaStop {
    if (Test-Path ".\scripts\dev\stop-voila.ps1") {
        try {
            & .\scripts\dev\stop-voila.ps1 -Silent | Out-Host
        } catch {
            try { & .\scripts\dev\stop-voila.ps1 | Out-Host } catch {}
        }
    }
}

function Invoke-VoilaStart {
    if (-not (Test-Path ".\scripts\dev\start-voila.ps1")) {
        throw "Missing .\scripts\dev\start-voila.ps1"
    }

    try {
        & .\scripts\dev\start-voila.ps1 -Silent | Out-Host
    } catch {
        & .\scripts\dev\start-voila.ps1 | Out-Host
    }
}

function Wait-VoilaHealth {
    for ($i = 0; $i -lt 45; $i++) {
        try {
            $r = Invoke-WebRequest -Uri "$base/health" -UseBasicParsing -TimeoutSec 3
            if ($r.StatusCode -eq 200) {
                return
            }
        } catch {
            Start-Sleep -Seconds 1
        }
    }

    throw "Voila did not become healthy on $base"
}

Write-Host "=== EXAM PREP HEALTH CHECKPOINT v0.4.20 ==="

Write-Host "=== COMPILE ==="
python -m py_compile .\services\api\exam_prep.py .\services\api\web_app.py .\services\api\study_quiz_builder.py

Write-Host "=== SOURCE MARKER CHECK ==="

$web = Get-Content ".\services\api\web_app.py" -Raw
$exam = Get-Content ".\services\api\exam_prep.py" -Raw
$smoke = Get-Content ".\scripts\dev\smoke-exam-prep-skill-detail.ps1" -Raw

$sourceChecks = [ordered]@{
    "source_has_dashboard_next_action_v0417" = ($web -cmatch "exam-prep-dashboard-next-action-v0417" -or $exam -cmatch "exam-prep-dashboard-next-action-v0417")
    "source_has_progress_summary_v0410" = ($web -cmatch "exam-prep-progress-summary-v0410" -or $exam -cmatch "exam-prep-progress-summary-v0410")
    "source_has_skill_cards_v0411" = ($web -cmatch "exam-prep-skill-cards-v0411" -or $exam -cmatch "exam-prep-skill-cards-v0411")
    "source_has_order_marker_v0418" = ($web -cmatch "exam-prep-dashboard-order-v0418")
    "source_has_visual_marker_v0419" = ($web -cmatch "exam-prep-dashboard-visual-v0419")
    "source_has_detail_next_action_v0416" = ($web -cmatch "exam-prep-next-action-v0416" -or $exam -cmatch "exam-prep-next-action-v0416")
    "source_has_related_questions_v0415" = ($web -cmatch "exam-prep-related-study-questions-v0415" -or $exam -cmatch "exam-prep-related-study-questions-v0415")
    "source_has_modul_studiu" = (($web + $exam) -cmatch "Modul Studiu")
    "source_has_pregatire_examene" = (($web + $exam) -cmatch "Pregătire examene")
    "source_has_consolidat" = (($web + $exam) -cmatch "Consolidat")
    "source_no_stapanire" = (($web + $exam) -cnotmatch "Stăpânire|stăpânire|Stapanire|stapanire")
    "source_has_dashboard_consolidated_v0422" = (($web + $exam) -cmatch "exam-prep-dashboard-consolidated-v0422")
    "source_has_skill_detail_consolidated_v0423" = (($web + $exam) -cmatch "exam-prep-skill-detail-consolidated-v0423")
    "source_has_v424_cleanup_marker" = (($web + $exam) -cmatch "v0.4.24 Exam Prep wording wrapper cleanup checkpoint")
    "smoke_has_v424_checks" = ($smoke -cmatch "v424_combined_has_dashboard_consolidation")
    "source_has_skill_metadata_v0427" = (($web + $exam) -cmatch "exam-prep-skill-metadata-v0427")
    "smoke_has_v427_checks" = ($smoke -cmatch "v427_detail_has_metadata_marker")
    "smoke_has_v0419_checks" = ($smoke -cmatch "v419_dashboard_has_visual_marker")
}

foreach ($item in $sourceChecks.GetEnumerator()) {
    Write-Host "$($item.Key) $($item.Value)"
}

if ($sourceChecks.Values -contains $false) {
    throw "SOURCE MARKER CHECK FAILED"
}

Write-Host "=== RUN PERMANENT EXAM PREP SMOKE ==="
& .\scripts\dev\smoke-exam-prep-skill-detail.ps1

Write-Host "=== ROUTE + CONTENT CHECKPOINT ==="

try {
    Invoke-VoilaStop
    Invoke-VoilaStart
    Wait-VoilaHealth

    $routes = @("/health", "/", "/quick-tools", "/exam-prep", "/exam-prep/skill/derivate")
    foreach ($route in $routes) {
        $resp = Invoke-WebRequest -Uri "$base$route" -UseBasicParsing -TimeoutSec 10
        Write-Host "$route $($resp.StatusCode)"
        if ($resp.StatusCode -ne 200) {
            throw "$route failed"
        }
    }

    $dashboard = (Invoke-WebRequest -Uri "$base/exam-prep" -UseBasicParsing -TimeoutSec 10).Content
    $detail = (Invoke-WebRequest -Uri "$base/exam-prep/skill/derivate" -UseBasicParsing -TimeoutSec 10).Content
    $combined = $dashboard + $detail

    $nextIndex = $dashboard.IndexOf("exam-prep-dashboard-next-action-v0417")
    $summaryIndex = $dashboard.IndexOf("exam-prep-progress-summary-v0410")
    $cardsIndex = $dashboard.IndexOf("exam-prep-skill-cards-v0411")

    $contentChecks = [ordered]@{
        "dashboard_has_visual_marker_v0419" = ($dashboard -cmatch "exam-prep-dashboard-visual-v0419")
        "dashboard_has_order_marker_v0418" = ($dashboard -cmatch "exam-prep-dashboard-order-v0418")
        "dashboard_has_next_action_v0417" = ($nextIndex -ge 0)
        "dashboard_has_progress_summary_v0410" = ($summaryIndex -ge 0)
        "dashboard_has_skill_cards_v0411" = ($cardsIndex -ge 0)
        "dashboard_order_next_before_summary" = ($nextIndex -ge 0 -and $summaryIndex -gt $nextIndex)
        "dashboard_order_summary_before_cards" = ($summaryIndex -ge 0 -and $cardsIndex -gt $summaryIndex)
        "dashboard_has_ce_sa_faci_acum" = ($dashboard -cmatch "Ce să faci acum")
        "dashboard_has_rezumat_progres" = ($dashboard -cmatch "Rezumat progres")
        "dashboard_has_skilluri_exam_prep" = ($dashboard -cmatch "Skill-uri Exam Prep")
        "dashboard_has_functii_ro" = ($dashboard -cmatch "Funcții")
        "dashboard_has_in_progres_ro" = ($dashboard -cmatch "În progres")

        "detail_has_related_questions_v0415" = ($detail -cmatch "exam-prep-related-study-questions-v0415")
        "detail_has_next_action_v0416" = ($detail -cmatch "exam-prep-next-action-v0416")
        "detail_has_questions_heading" = ($detail -cmatch "Întrebări asociate din Modul Studiu")
        "detail_has_modul_studiu_sentence" = ($detail -cmatch "Răspunde la întrebări în Modul Studiu, iar progresul se va actualiza aici")
        "detail_has_continue_modul_studiu" = ($detail -cmatch "Continuă în Modul Studiu")
        "detail_has_back_pregatire" = ($detail -cmatch "Înapoi la Pregătire examene")
        "detail_has_next_action_title" = ($detail -cmatch "Acțiune recomandată")
        "detail_has_current_status" = ($detail -cmatch "Status curent")

        "combined_has_consolidat" = ($combined -cmatch "Consolidat")
        "combined_no_old_mixed_wording" = ($combined -cnotmatch "Întrebări Study legate|Continuă în Study Mode|Înapoi la Exam Prep")
        "combined_no_ascii_ro_regressions" = ($combined -cnotmatch ">Functii<|Functii,|Status: In progres|>In progres<")
        "combined_no_stapanire" = ($combined -cnotmatch "Stăpânire|stăpânire|Stapanire|stapanire")
        "v425_dashboard_has_consolidated_marker_v0422" = ($dashboard -cmatch "exam-prep-dashboard-consolidated-v0422")
        "v425_detail_has_consolidated_marker_v0423" = ($detail -cmatch "exam-prep-skill-detail-consolidated-v0423")
        "v425_combined_has_v424_smoke_guarded_markers" = ($combined -cmatch "exam-prep-dashboard-consolidated-v0422" -and $combined -cmatch "exam-prep-skill-detail-consolidated-v0423")
        "v425_combined_keeps_modul_studiu_wording" = ($combined -cmatch "Modul Studiu" -and $combined -cmatch "Pregătire examene")
        "v425_combined_keeps_romanian_labels" = ($combined -cmatch "Funcții" -and $combined -cmatch "În progres")
        "technical_slug_functii_allowed" = ($combined -cmatch "/exam-prep/skill/functii")
    }

    foreach ($item in $contentChecks.GetEnumerator()) {
        Write-Host "$($item.Key) $($item.Value)"
    }

    if ($contentChecks.Values -contains $false) {
        throw "ROUTE + CONTENT CHECKPOINT FAILED"
    }

    Write-Host "EXAM PREP HEALTH CHECKPOINT PASS"
Write-Host "EXAM PREP POST-CLEANUP HEALTH EXPANSION v0.4.25 PASS"
Write-Host "EXAM PREP SKILL METADATA DISPLAY v0.4.27 PASS"
}
finally {
    Invoke-VoilaStop
}

