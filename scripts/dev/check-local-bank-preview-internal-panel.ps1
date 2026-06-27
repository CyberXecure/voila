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
  $Content = $Response.Content
  Write-Host ($Content.Substring(0, [Math]::Min(1600, $Content.Length)))

  $status_ok = ($Response.StatusCode -eq 200)
  $has_title = ($Content -match "Local bank preview internal panel")
  $has_version = ($Content -match "v0\.4\.51")
  $has_read_only = ($Content -match "read-only")
  $has_active_source = ($Content -match "local_exercise_bank_adapter")
  $has_selected_skill = ($Content -match "local_concept_001_functiile")
  $has_question_count = ($Content -match "preview_question_count")
  $has_no_attempt = ($Content -match "will_save_attempt = false")
  $has_no_progress = ($Content -match "will_update_progress = false")
  $has_no_score = ($Content -match "will_score_answer = false")
  $has_no_ui = ($Content -match "will_modify_exam_prep_ui = false")
  $has_no_weak = ($Content -match "will_modify_weak_review = false")
  $has_no_live = ($Content -match "will_replace_live_study_session = false")
  $has_no_legacy_replace = ($Content -match "will_replace_legacy_generator = false")
  $has_no_live_consumption = ($Content -match "will_enable_live_consumption = false")
  $has_no_cloud = ($Content -match "requires_cloud_or_api = false")
  $has_noindex = ($Content -match "noindex,nofollow")

  Write-Host "status_ok $status_ok"
  Write-Host "has_title $has_title"
  Write-Host "has_version $has_version"
  Write-Host "has_read_only $has_read_only"
  Write-Host "has_active_source $has_active_source"
  Write-Host "has_selected_skill $has_selected_skill"
  Write-Host "has_question_count $has_question_count"
  Write-Host "has_no_attempt $has_no_attempt"
  Write-Host "has_no_progress $has_no_progress"
  Write-Host "has_no_score $has_no_score"
  Write-Host "has_no_ui $has_no_ui"
  Write-Host "has_no_weak $has_no_weak"
  Write-Host "has_no_live $has_no_live"
  Write-Host "has_no_legacy_replace $has_no_legacy_replace"
  Write-Host "has_no_live_consumption $has_no_live_consumption"
  Write-Host "has_no_cloud $has_no_cloud"
  Write-Host "has_noindex $has_noindex"

  if (-not ($status_ok -and $has_title -and $has_version -and $has_read_only -and $has_active_source -and $has_selected_skill -and $has_question_count -and $has_no_attempt -and $has_no_progress -and $has_no_score -and $has_no_ui -and $has_no_weak -and $has_no_live -and $has_no_legacy_replace -and $has_no_live_consumption -and $has_no_cloud -and $has_noindex)) {
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

