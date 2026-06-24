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

    $checks = [ordered]@{
        "exam_has_skill_detail_links" = ($exam -match "/exam-prep/skill/")
        "exam_has_status" = ($exam -match "Status|Stare")
        "skill_detail_200" = ($skillResp.StatusCode -eq 200)
        "skill_has_detail_title" = ($skill -match "Detaliu skill|Skill")
        "skill_has_progress" = ($skill -match "Progres|progres|Stare consolidare|Intrebari Study|Întrebări Study")
        "skill_has_study_entry" = ($skill -match "Study Mode|Studiu|Study")
        "skill_uses_consolidat_terms" = ($skill -match "Consolidat|Aproape consolidat|In progres|În progres|Nepornit|De revizuit")
        "skill_no_stapanire" = ($skill -notmatch "Stăpânire|stăpânire|Stapanire|stapanire")
    }

    foreach ($item in $checks.GetEnumerator()) {
        Write-Host "$($item.Key) $($item.Value)"
    }

    if ($checks.Values -contains $false) {
        throw "EXAM PREP SKILL DETAIL SMOKE FAILED"
    }

    Write-Host "EXAM PREP SKILL DETAIL SMOKE PASS"
}
finally {
    Write-Host "=== STOP AFTER EXAM PREP SKILL DETAIL SMOKE ==="
    Invoke-VoilaStop
}
