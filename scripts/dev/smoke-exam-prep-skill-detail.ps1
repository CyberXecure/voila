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
