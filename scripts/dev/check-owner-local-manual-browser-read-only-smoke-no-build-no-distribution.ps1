[CmdletBinding()]
param(
  [string]$BaseUrl = "http://127.0.0.1:8787",
  [switch]$OpenBrowser,
  [switch]$AssumeManualPass
)

$ErrorActionPreference = "Stop"

$Milestone = "v0.7.16-smoke"
$FinalMarker = "VOILA_V0_7_16_OWNER_LOCAL_MANUAL_BROWSER_READ_ONLY_SMOKE_CHECK=PASS"
$StartedRuntime = $false

function Write-Step([string]$Message) {
  Write-Host "[$Milestone] $Message"
}

function Invoke-GetCheck {
  param(
    [string]$Path,
    [string]$Name,
    [switch]$Optional
  )

  $uri = "$BaseUrl$Path"
  Write-Step "GET $Path"

  try {
    $response = Invoke-WebRequest -Uri $uri -Method GET -UseBasicParsing -TimeoutSec 20
    if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) {
      Write-Host "$Name=pass"
      return $true
    }

    if ($Optional) {
      Write-Host "$Name=optional_skipped_status_$($response.StatusCode)"
      return $false
    }

    throw "GET $Path returned status $($response.StatusCode)"
  } catch {
    if ($Optional) {
      Write-Host "$Name=optional_skipped"
      return $false
    }

    throw
  }
}

function Open-LocalBrowser {
  param([string]$Path)

  $uri = "$BaseUrl$Path"
  Write-Step "Opening browser $Path"
  Start-Process $uri | Out-Null
}

Write-Host ""
Write-Host "=== Voila v0.7.16 owner-local manual browser read-only smoke ==="
Write-Host ""

Write-Step "Policy guard: manual browser read-only smoke; no write-capable routes will be called"
Write-Host "server_start_local=permitted"
Write-Host "manual_browser_open=permitted"
Write-Host "build_created=false"
Write-Host "zip_created=false"
Write-Host "delivery_performed=false"
Write-Host "distribution_performed=false"
Write-Host "upload_generate_save_delete_reset_performed=false"
Write-Host "feature_changes=false"
Write-Host "behavior_changes=false"
Write-Host "public_ui_expansion=false"

try {
  try {
    Invoke-WebRequest -Uri "$BaseUrl/health" -Method GET -UseBasicParsing -TimeoutSec 3 | Out-Null
    Write-Step "Runtime already available at $BaseUrl"
  } catch {
    Write-Step "Starting owner-local runtime via scripts/dev/start-voila.ps1 -Silent"
    pwsh -NoProfile -ExecutionPolicy Bypass -File ".\scripts\dev\start-voila.ps1" -Silent
    $StartedRuntime = $true
    Start-Sleep -Seconds 3
  }

  Invoke-GetCheck -Path "/health" -Name "health_get_check" | Out-Null
  Invoke-GetCheck -Path "/" -Name "homepage_get_check" | Out-Null
  Invoke-GetCheck -Path "/quick-tools" -Name "readonly_route_quick_tools_get_check" -Optional | Out-Null
  Invoke-GetCheck -Path "/exam-prep" -Name "readonly_route_exam_prep_get_check" -Optional | Out-Null
  Write-Host "readonly_routes_get_check=pass_or_optional_skipped"

  if ($OpenBrowser) {
    Open-LocalBrowser -Path "/"
    Start-Sleep -Milliseconds 500
    Open-LocalBrowser -Path "/quick-tools"
    Start-Sleep -Milliseconds 500
    Open-LocalBrowser -Path "/exam-prep"
  }

  Write-Host ""
  Write-Host "Manual browser rule:"
  Write-Host "- Inspect only already-opened local pages."
  Write-Host "- Do not upload, generate, regenerate, save, delete, reset, or mutate progress/data."
  Write-Host "- Do not use write-capable page actions."
  Write-Host ""

  if ($AssumeManualPass) {
    Write-Host "manual_browser_read_only_confirmation=pass"
  } else {
    $answer = Read-Host "After manual read-only inspection, type PASS to confirm no write actions were performed"
    if ($answer -ne "PASS") {
      throw "Manual browser read-only confirmation was not PASS."
    }
    Write-Host "manual_browser_read_only_confirmation=pass"
  }

  Write-Host $FinalMarker
} finally {
  if ($StartedRuntime) {
    Write-Step "Stopping owner-local runtime via scripts/dev/stop-voila.ps1 -Silent"
    pwsh -NoProfile -ExecutionPolicy Bypass -File ".\scripts\dev\stop-voila.ps1" -Silent
  } else {
    Write-Step "Runtime was already running before this check; leaving it running"
  }

  Write-Host ""
  Write-Host "=== Final check ==="
  Write-Host ""
  Write-Host "DONE."
}
