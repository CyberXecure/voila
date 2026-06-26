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

try {
    Write-Host "=== STOP BEFORE EXAM PREP SKILL DETAIL SMOKE ==="
    Invoke-VoilaStop

    Write-Host "=== START ==="
    Invoke-VoilaStart
    Wait-VoilaHealth

    Write-Host "=== ROUTE STATUS ==="

    $routes = @("/health", "/", "/quick-tools", "/exam-prep")
    foreach ($route in $routes) {
        $resp = Invoke-WebRequest -Uri "$base$route" -UseBasicParsing -TimeoutSec 10
        Write-Host "$route $($resp.StatusCode)"
        if ($resp.StatusCode -ne 200) {
            throw "$route failed"
        }
    }

    $examResp = Invoke-WebRequest -Uri "$base/exam-prep" -UseBasicParsing -TimeoutSec 10
    $exam = $examResp.Content

    $match = [regex]::Match($exam, 'href="(/exam-prep/skill/[^"]+)"')
    if (-not $match.Success) {
        throw "No /exam-prep/skill/... link found on /exam-prep"
    }

    $skillUrl = $match.Groups[1].Value
    Write-Host "first_skill_detail_url $skillUrl"

    $skillResp = Invoke-WebRequest -Uri "$base$skillUrl" -UseBasicParsing -TimeoutSec 10
    $skill = $skillResp.Content

    $derivateResp = Invoke-WebRequest -Uri "$base/exam-prep/skill/derivate" -UseBasicParsing -TimeoutSec 10
    $derivate = $derivateResp.Content

    $combined = $exam + $skill + $derivate

    $checks = [ordered]@{
        "exam_has_skill_detail_links" = ($exam -cmatch "/exam-prep/skill/")
        "exam_has_status" = ($exam -cmatch "Status|Stare")
        "exam_has_progress_summary" = ($exam -cmatch "exam-prep-progress-summary-v0410")
        "exam_has_skill_cards" = ($exam -cmatch "exam-prep-skill-cards-v0411")
        "skill_detail_200" = ($skillResp.StatusCode -eq 200)
        "skill_has_detail_title" = ($skill -cmatch "Detaliu skill|Skill")
        "skill_has_progress" = ($skill -cmatch "Progres|progres|Stare consolidare|Întrebări asociate din Modul Studiu|Întrebări Study|Intrebari Study")
        "skill_has_study_entry" = ($skill -cmatch "Modul Studiu|Studiu|Study Mode|Study")
        "skill_uses_consolidat_terms" = ($skill -cmatch "Consolidat|Aproape consolidat|În progres|In progres|Nepornit|De revizuit")
        "skill_no_stapanire" = ($skill -cnotmatch "Stăpânire|stăpânire|Stapanire|stapanire")

        "ro_dashboard_has_functii" = ($exam -cmatch "Funcții")
        "ro_dashboard_has_in_progres" = ($exam -cmatch "În progres")
        "ro_dashboard_has_consolidat" = ($exam -cmatch "Consolidat")
        "ro_derivate_200" = ($derivateResp.StatusCode -eq 200)
        "ro_detail_has_pregatire" = ($derivate -cmatch "Pregătire examene")
        "ro_detail_has_matematica" = ($derivate -cmatch "Matematică M1")
        "ro_detail_has_questions" = ($derivate -cmatch "Întrebări asociate din Modul Studiu")
        "ro_detail_has_sentence" = ($derivate -cmatch "Răspunde la întrebări în Modul Studiu, iar progresul se va actualiza aici")
        "ro_detail_has_continue" = ($derivate -cmatch "Continuă în Modul Studiu")
        "ro_detail_has_back" = ($derivate -cmatch "Înapoi la Pregătire examene")
        "ro_combined_no_stapanire" = ($combined -cnotmatch "Stăpânire|stăpânire|Stapanire|stapanire")
        "ro_combined_no_visible_functii_ascii" = ($combined -cnotmatch ">Functii<|Functii,|Status: Functii")
        "ro_combined_no_visible_in_progres_ascii" = ($combined -cnotmatch ">In progres<|Status: In progres")
        "ro_combined_no_old_study_wording" = ($combined -cnotmatch "Întrebări Study legate|Intrebari Study legate|Continuă în Study Mode|Continua in Study Mode|Înapoi la Exam Prep|Inapoi la Exam Prep")
        "v415_detail_has_related_questions_marker" = ($derivate -cmatch "exam-prep-related-study-questions-v0415")
        "v415_detail_has_questions_heading" = ($derivate -cmatch "Întrebări asociate din Modul Studiu")
        "v415_detail_has_count_or_empty_message" = ($derivate -cmatch "întrebări asociate detectate|întrebare asociată detectată|Nu există încă întrebări asociate detectate")
        "v415_detail_has_answer_instruction" = ($derivate -cmatch "Răspunde la întrebări în Modul Studiu|Răspunde la întrebările asociate în Modul Studiu|Răspunde la întrebarea asociată în Modul Studiu")
        "v415_detail_has_readonly_note" = ($derivate -cmatch "read-only")
        "v416_detail_has_next_action_marker" = ($derivate -cmatch "exam-prep-next-action-v0416")
        "v416_detail_has_next_action_title" = ($derivate -cmatch "Acțiune recomandată")
        "v416_detail_has_current_status" = ($derivate -cmatch "Status curent")
        "v416_detail_has_action_text" = ($derivate -cmatch "Modul Studiu")
        "v416_detail_has_continue_modul_studiu" = ($derivate -cmatch "Continuă în Modul Studiu")
        "v416_detail_has_back_pregatire" = ($derivate -cmatch "Înapoi la Pregătire examene")
        "v417_dashboard_has_next_action_marker" = ($exam -cmatch "exam-prep-dashboard-next-action-v0417")
        "v417_dashboard_has_next_action_title" = ($exam -cmatch "Ce să faci acum")
        "v417_dashboard_has_recommended_skill" = ($exam -cmatch "Skill recomandat")
        "v417_dashboard_has_current_status" = ($exam -cmatch "Status curent")
        "v417_dashboard_has_vezi_detalii" = ($exam -cmatch "Vezi detalii")
        "v418_dashboard_has_order_marker" = ($exam -cmatch "exam-prep-dashboard-order-v0418")
        "v418_dashboard_order_next_before_summary" = ($exam.IndexOf("exam-prep-dashboard-next-action-v0417") -ge 0 -and $exam.IndexOf("exam-prep-progress-summary-v0410") -gt $exam.IndexOf("exam-prep-dashboard-next-action-v0417"))
        "v418_dashboard_order_summary_before_cards" = ($exam.IndexOf("exam-prep-progress-summary-v0410") -ge 0 -and $exam.IndexOf("exam-prep-skill-cards-v0411") -gt $exam.IndexOf("exam-prep-progress-summary-v0410"))
        "v419_dashboard_has_visual_marker" = ($exam -cmatch "exam-prep-dashboard-visual-v0419")
        "v419_dashboard_has_order_wrapper" = ($exam -cmatch "exam-prep-dashboard-order-v0418")
        "v419_dashboard_has_next_summary_cards" = ($exam -cmatch "exam-prep-dashboard-next-action-v0417" -and $exam -cmatch "exam-prep-progress-summary-v0410" -and $exam -cmatch "exam-prep-skill-cards-v0411")
        "v422_dashboard_has_consolidated_marker" = ($exam -cmatch "exam-prep-dashboard-consolidated-v0422")
        "v422_dashboard_has_order_marker" = ($exam -cmatch "exam-prep-dashboard-order-v0418")
        "v422_dashboard_has_next_summary_cards" = ($exam -cmatch "exam-prep-dashboard-next-action-v0417" -and $exam -cmatch "exam-prep-progress-summary-v0410" -and $exam -cmatch "exam-prep-skill-cards-v0411")
        "v422_dashboard_order_next_before_summary" = ($exam.IndexOf("exam-prep-dashboard-next-action-v0417") -ge 0 -and $exam.IndexOf("exam-prep-progress-summary-v0410") -gt $exam.IndexOf("exam-prep-dashboard-next-action-v0417"))
        "v422_dashboard_order_summary_before_cards" = ($exam.IndexOf("exam-prep-progress-summary-v0410") -ge 0 -and $exam.IndexOf("exam-prep-skill-cards-v0411") -gt $exam.IndexOf("exam-prep-progress-summary-v0410"))
        "v423_detail_has_consolidated_marker" = ($derivate -cmatch "exam-prep-skill-detail-consolidated-v0423")
        "v423_detail_has_related_and_next_sections" = ($derivate -cmatch "exam-prep-related-study-questions-v0415" -and $derivate -cmatch "exam-prep-next-action-v0416")
        "v423_detail_order_related_before_next" = ($derivate.IndexOf("exam-prep-related-study-questions-v0415") -ge 0 -and $derivate.IndexOf("exam-prep-next-action-v0416") -gt $derivate.IndexOf("exam-prep-related-study-questions-v0415"))
        "v424_combined_has_dashboard_consolidation" = ($combined -cmatch "exam-prep-dashboard-consolidated-v0422")
        "v424_combined_has_skill_detail_consolidation" = ($combined -cmatch "exam-prep-skill-detail-consolidated-v0423")
        "v424_combined_no_old_mixed_wording" = ($combined -cnotmatch "Întrebări Study legate|Continuă în Study Mode|Înapoi la Exam Prep")
        "v427_detail_has_metadata_marker" = ($derivate -cmatch "exam-prep-skill-metadata-v0427")
        "v427_detail_has_metadata_title" = ($derivate -cmatch "Detalii skill")
        "v427_detail_has_metadata_fields" = ($derivate -cmatch "Capitol" -and $derivate -cmatch "Descriere" -and $derivate -cmatch "Condiții preliminare" -and $derivate -cmatch "Status Modul Studiu")
        "v427_detail_order_metadata_before_related" = ($derivate.IndexOf("exam-prep-skill-metadata-v0427") -ge 0 -and $derivate.IndexOf("exam-prep-related-study-questions-v0415") -gt $derivate.IndexOf("exam-prep-skill-metadata-v0427"))
        "v428_dashboard_has_weak_review_entry" = ($exam -cmatch "exam-prep-weak-review-entry-v0428" -and $exam -cmatch "Revizuire concepte slabe")
        "v428_detail_has_weak_review_entry" = ($derivate -cmatch "exam-prep-weak-review-entry-v0428" -and $derivate -cmatch "Revizuire concepte slabe")
        "v428_combined_has_weak_review_link" = ($combined -cmatch "Deschide revizuirea conceptelor slabe" -and $combined -cmatch "/#library")
        "v428_detail_order_next_before_weak_review" = ($derivate.IndexOf("exam-prep-next-action-v0416") -ge 0 -and $derivate.IndexOf("exam-prep-weak-review-entry-v0428") -gt $derivate.IndexOf("exam-prep-next-action-v0416"))
        "v431_detail_has_learning_path_marker" = ($derivate -cmatch "exam-prep-learning-path-v0431")
        "v431_detail_has_learning_path_title" = ($derivate -cmatch "Traseu de învățare")
        "v431_detail_has_learning_path_fields" = ($derivate -cmatch "Skill curent" -and $derivate -cmatch "Condiții preliminare" -and $derivate -cmatch "Următorul pas")
        "v431_detail_order_metadata_before_learning_path" = ($derivate.IndexOf("exam-prep-skill-metadata-v0427") -ge 0 -and $derivate.IndexOf("exam-prep-learning-path-v0431") -gt $derivate.IndexOf("exam-prep-skill-metadata-v0427"))
        "v431_detail_order_learning_path_before_related" = ($derivate.IndexOf("exam-prep-learning-path-v0431") -ge 0 -and $derivate.IndexOf("exam-prep-related-study-questions-v0415") -gt $derivate.IndexOf("exam-prep-learning-path-v0431"))
        "v432_dashboard_has_learning_path_entry" = ($exam -cmatch "exam-prep-dashboard-learning-path-v0432")
        "v432_dashboard_has_learning_path_title" = ($exam -cmatch "Traseu recomandat")
        "v432_dashboard_has_learning_path_fields" = ($exam -cmatch "Skill recomandat" -and $exam -cmatch "Status curent" -and $exam -cmatch "Vezi traseul de învățare")
        "v432_dashboard_order_next_before_learning_path" = ($exam.IndexOf("exam-prep-dashboard-next-action-v0417") -ge 0 -and $exam.IndexOf("exam-prep-dashboard-learning-path-v0432") -gt $exam.IndexOf("exam-prep-dashboard-next-action-v0417"))
        "v432_dashboard_order_learning_path_before_summary" = ($exam.IndexOf("exam-prep-dashboard-learning-path-v0432") -ge 0 -and $exam.IndexOf("exam-prep-progress-summary-v0410") -gt $exam.IndexOf("exam-prep-dashboard-learning-path-v0432"))
        "v435_detail_has_study_session_entry" = ($derivate -cmatch "exam-prep-study-session-entry-v0435")
        "v435_detail_has_study_session_title" = ($derivate -cmatch "Intrare în Modul Studiu")
        "v435_detail_has_progress_update_copy" = ($derivate -cmatch "Răspunde la întrebări în Modul Studiu" -and $derivate -cmatch "progresul Exam Prep se va actualiza aici")
        "v435_detail_has_continue_modul_studiu_cta" = ($derivate -cmatch "Continuă în Modul Studiu")
        "v435_detail_order_related_before_study_entry" = ($derivate.IndexOf("exam-prep-related-study-questions-v0415") -ge 0 -and $derivate.IndexOf("exam-prep-study-session-entry-v0435") -gt $derivate.IndexOf("exam-prep-related-study-questions-v0415"))
        "v435_detail_order_study_entry_before_next_action" = ($derivate.IndexOf("exam-prep-study-session-entry-v0435") -ge 0 -and $derivate.IndexOf("exam-prep-next-action-v0416") -gt $derivate.IndexOf("exam-prep-study-session-entry-v0435"))
        "v436_dashboard_has_progress_interpretation" = ($exam -cmatch "exam-prep-progress-interpretation-v0436" -and $exam -cmatch "Cum interpretăm progresul")
        "v436_detail_has_progress_interpretation" = ($derivate -cmatch "exam-prep-progress-interpretation-v0436" -and $derivate -cmatch "Cum interpretăm progresul")
        "v436_combined_has_status_explanations" = ($combined -cmatch "Nepornit" -and $combined -cmatch "În progres" -and $combined -cmatch "Consolidat")
        "v436_combined_has_readonly_no_threshold_copy" = ($combined -cmatch "read-only" -and $combined -cmatch "nu modifică scorurile, pragurile sau BKT")
        "v436_dashboard_order_summary_before_interpretation" = ($exam.IndexOf("exam-prep-progress-summary-v0410") -ge 0 -and $exam.IndexOf("exam-prep-progress-interpretation-v0436") -gt $exam.IndexOf("exam-prep-progress-summary-v0410"))
        "v436_detail_order_study_before_interpretation" = ($derivate.IndexOf("exam-prep-study-session-entry-v0435") -ge 0 -and $derivate.IndexOf("exam-prep-progress-interpretation-v0436") -gt $derivate.IndexOf("exam-prep-study-session-entry-v0435"))
        "v438_dashboard_has_compact_marker" = ($exam -cmatch "exam-prep-dashboard-compact-v0438")
        "v438_dashboard_has_compact_style" = ($exam -cmatch "exam-prep-dashboard-compactness-v0438")
        "v438_dashboard_has_compact_note" = ($exam -cmatch "Dashboard compact")
        "v438_dashboard_keeps_existing_sections" = ($exam -cmatch "exam-prep-dashboard-next-action-v0417" -and $exam -cmatch "exam-prep-dashboard-learning-path-v0432" -and $exam -cmatch "exam-prep-progress-summary-v0410" -and $exam -cmatch "exam-prep-progress-interpretation-v0436" -and ($exam -cmatch "exam-prep-dashboard-skill-cards-v0411" -or $exam -cmatch "exam-prep-skill-cards-v0411" -or $exam -cmatch "Skill-uri Exam Prep") -and $exam -cmatch "exam-prep-weak-review-entry-v0428")
        "v438_dashboard_order_next_learning_summary_interpretation_cards_weak" = ($exam.IndexOf("exam-prep-dashboard-next-action-v0417") -ge 0 -and $exam.IndexOf("exam-prep-dashboard-learning-path-v0432") -gt $exam.IndexOf("exam-prep-dashboard-next-action-v0417") -and $exam.IndexOf("exam-prep-progress-summary-v0410") -gt $exam.IndexOf("exam-prep-dashboard-learning-path-v0432") -and $exam.IndexOf("exam-prep-progress-interpretation-v0436") -gt $exam.IndexOf("exam-prep-progress-summary-v0410") -and ([Math]::Max($exam.IndexOf("exam-prep-dashboard-skill-cards-v0411"), [Math]::Max($exam.IndexOf("exam-prep-skill-cards-v0411"), $exam.IndexOf("Skill-uri Exam Prep"))) -gt $exam.IndexOf("exam-prep-progress-interpretation-v0436")) -and $exam.IndexOf("exam-prep-weak-review-entry-v0428") -gt ([Math]::Max($exam.IndexOf("exam-prep-dashboard-skill-cards-v0411"), [Math]::Max($exam.IndexOf("exam-prep-skill-cards-v0411"), $exam.IndexOf("Skill-uri Exam Prep")))))
        "technical_slug_functii_allowed" = ($combined -cmatch "/exam-prep/skill/functii")
    }

    foreach ($item in $checks.GetEnumerator()) {
        Write-Host "$($item.Key) $($item.Value)"
    }

    if ($checks.Values -contains $false) {
        Write-Host "=== OFFENDING SNIPPETS ==="

        foreach ($term in @("Întrebări Study legate", "Intrebari Study legate", "Continuă în Study Mode", "Continua in Study Mode", "Înapoi la Exam Prep", "Inapoi la Exam Prep", "Functii,", ">Functii<", "Status: In progres", ">In progres<", "Stapanire")) {
            $idx = $combined.IndexOf($term)
            if ($idx -ge 0) {
                $start = [Math]::Max(0, $idx - 120)
                $len = [Math]::Min(300, $combined.Length - $start)
                Write-Host "--- $term ---"
                Write-Host $combined.Substring($start, $len)
            }
        }

        throw "EXAM PREP SKILL DETAIL SMOKE FAILED"
    }

    Write-Host "EXAM PREP SKILL DETAIL SMOKE PASS"
}
finally {
    Write-Host "=== STOP AFTER EXAM PREP SKILL DETAIL SMOKE ==="
    Invoke-VoilaStop
}
