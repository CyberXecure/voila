param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK PREVIEW INTERNAL PANEL CHECK v0.4.51 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$Tmp = Join-Path $env:TEMP ("voila-local-bank-panel-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $Tmp | Out-Null

$oldFlag = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_PREVIEW_ROUTE

try {
  $CourseDir = Join-Path $Tmp "course-a"
  New-Item -ItemType Directory -Force -Path $CourseDir | Out-Null

  $SampleText = @"
Funcțiile sunt relații matematice între două mulțimi. O funcție este definită prin domeniu, codomeniu și lege de corespondență.
Derivata descrie variația locală a unei funcții. Apoi se poate studia monotonia și se pot identifica punctele critice.
Formula f'(x)=lim h->0 (f(x+h)-f(x))/h este folosită pentru calculul derivatei.
"@

  $GeneratedRaw = python .\services\api\local_pedagogy_engine.py --text $SampleText --output-dir $CourseDir --course-id "v051-smoke" --language ro
  if ($LASTEXITCODE -ne 0) { throw "local_pedagogy_engine.py failed" }
  Write-Host $GeneratedRaw

  & .\scripts\dev\stop-voila.ps1 | Out-Host

  $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_PREVIEW_ROUTE = "1"
  & .\scripts\dev\start-voila.ps1 -Silent | Out-Host

  $healthOk = $false
  for ($i = 0; $i -lt 30; $i++) {
    try {
      $health = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8787/health" -TimeoutSec 2
      if ($health.StatusCode -eq 200) {
        $healthOk = $true
        break
      }
    } catch {
      Start-Sleep -Seconds 1
    }
  }

  if (-not $healthOk) {
    throw "Voila health endpoint did not become ready."
  }

  $encodedRoot = [uri]::EscapeDataString($Tmp)
  $encodedSkill = [uri]::EscapeDataString("local_concept_001_functiile")
  $url = "http://127.0.0.1:8787/exam-prep/local-bank-study-preview/panel?root=$encodedRoot&course_id=v051-smoke&skill_id=$encodedSkill&limit=3"

  $Response = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 10
  Write-Host "panel_status_code $($Response.StatusCode)"
  Write-Host $Response.Content

  $Json = $Response.Content | ConvertFrom-Json
  $Preview = $Json.preview

  $status_ok = ($Response.StatusCode -eq 200 -and $Json.status -eq "ok")
  $route_version_ok = ($Json.route_version -eq "v0.4.51")
  $mode_ok = ($Json.mode -eq "protected_json_panel")
  $panel_kind_ok = ($Json.panel_kind -eq "internal_diagnostics_json")
  $no_public_ui_link_ok = ($Json.has_public_ui_link -eq $false)
  $preview_version_ok = ($Preview.study_preview_version -eq "v0.4.49")
  $preview_mode_ok = ($Preview.mode -eq "read_only_study_preview")
  $active_source_ok = ($Preview.active_source -eq "local_exercise_bank_adapter")
  $selected_skill_ok = ($Preview.selected_skill_id -eq "local_concept_001_functiile")
  $question_count_ok = ([int]$Preview.preview_question_count -gt 0 -and [int]$Preview.preview_question_count -le 3)
  $has_questions_ok = (@($Preview.questions).Count -gt 0)
  $no_attempt_ok = ($Json.will_save_attempt -eq $false -and $Preview.will_save_attempt -eq $false)
  $no_progress_ok = ($Json.will_update_progress -eq $false -and $Preview.will_update_progress -eq $false)
  $no_score_ok = ($Json.will_score_answer -eq $false -and $Preview.will_score_answer -eq $false)
  $no_ui_ok = ($Json.will_modify_exam_prep_ui -eq $false -and $Preview.will_modify_exam_prep_ui -eq $false)
  $no_weak_ok = ($Json.will_modify_weak_review -eq $false -and $Preview.will_modify_weak_review -eq $false)
  $no_live_ok = ($Json.will_replace_live_study_session -eq $false -and $Preview.will_replace_live_study_session -eq $false)
  $no_legacy_replace_ok = ($Json.will_replace_legacy_generator -eq $false -and $Preview.will_replace_legacy_generator -eq $false)
  $no_live_consumption_ok = ($Json.will_enable_live_consumption -eq $false -and $Preview.will_enable_live_consumption -eq $false)
  $no_cloud_ok = ($Json.requires_cloud_or_api -eq $false -and $Preview.requires_cloud_or_api -eq $false)

  Write-Host "status_ok $status_ok"
  Write-Host "route_version_ok $route_version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "panel_kind_ok $panel_kind_ok"
  Write-Host "no_public_ui_link_ok $no_public_ui_link_ok"
  Write-Host "preview_version_ok $preview_version_ok"
  Write-Host "preview_mode_ok $preview_mode_ok"
  Write-Host "active_source_ok $active_source_ok"
  Write-Host "selected_skill_ok $selected_skill_ok"
  Write-Host "question_count_ok $question_count_ok"
  Write-Host "has_questions_ok $has_questions_ok"
  Write-Host "no_attempt_ok $no_attempt_ok"
  Write-Host "no_progress_ok $no_progress_ok"
  Write-Host "no_score_ok $no_score_ok"
  Write-Host "no_ui_ok $no_ui_ok"
  Write-Host "no_weak_ok $no_weak_ok"
  Write-Host "no_live_ok $no_live_ok"
  Write-Host "no_legacy_replace_ok $no_legacy_replace_ok"
  Write-Host "no_live_consumption_ok $no_live_consumption_ok"
  Write-Host "no_cloud_ok $no_cloud_ok"

  if (-not ($status_ok -and $route_version_ok -and $mode_ok -and $panel_kind_ok -and $no_public_ui_link_ok -and $preview_version_ok -and $preview_mode_ok -and $active_source_ok -and $selected_skill_ok -and $question_count_ok -and $has_questions_ok -and $no_attempt_ok -and $no_progress_ok -and $no_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
    throw "LOCAL BANK PREVIEW INTERNAL PANEL CHECK v0.4.51 FAILED"
  }

  Write-Host "LOCAL BANK PREVIEW INTERNAL PANEL CHECK v0.4.51 PASS"
} finally {
  & .\scripts\dev\stop-voila.ps1 | Out-Host

  if ($null -eq $oldFlag) {
    Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_PREVIEW_ROUTE -ErrorAction SilentlyContinue
  } else {
    $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_PREVIEW_ROUTE = $oldFlag
  }

  if (Test-Path $Tmp) {
    Remove-Item -Recurse -Force $Tmp
  }
}
