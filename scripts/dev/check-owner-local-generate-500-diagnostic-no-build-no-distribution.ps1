[CmdletBinding()]
param(
  [string]$BaseUrl = "http://127.0.0.1:8787",
  [switch]$OpenBrowser,
  [ValidateSet("PROMPT","REPRODUCED_500","NO_500")]
  [string]$Result = "PROMPT"
)

$ErrorActionPreference = "Stop"

$Milestone = "v0.7.17a-diagnostic"
$FinalMarker = "VOILA_V0_7_17A_OWNER_LOCAL_GENERATE_500_DIAGNOSTIC_CHECK=PASS"
$EvidenceRoot = Join-Path $env:TEMP "voila-v0.7.17a-generate-500-diagnostic"
$FixturePdf = Join-Path $EvidenceRoot "voila-v0.7.17a-controlled-fixture.pdf"
$StdOutLog = Join-Path $EvidenceRoot "uvicorn.stdout.log"
$StdErrLog = Join-Path $EvidenceRoot "uvicorn.stderr.log"
$SummaryPath = Join-Path $EvidenceRoot "diagnostic-summary.txt"
$StartedRuntime = $false
$CapturedUvicorn = $null

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

function Get-PortOwningProcessId {
  param([int]$Port)

  $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($null -eq $listener) {
    return $null
  }

  return [int]$listener.OwningProcess
}

function Stop-PortOwner {
  param([int]$Port)

  $owningProcessId = Get-PortOwningProcessId -Port $Port
  if ($null -ne $owningProcessId) {
    Write-Step "Stopping process on port $Port PID $owningProcessId for diagnostic log capture"
    Stop-Process -Id $owningProcessId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
  }
}

function New-ControlledFixturePdf {
  New-Item -ItemType Directory -Force -Path $EvidenceRoot | Out-Null

  $pdfLines = @(
    "%PDF-1.4",
    "1 0 obj",
    "<< /Type /Catalog /Pages 2 0 R >>",
    "endobj",
    "2 0 obj",
    "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
    "endobj",
    "3 0 obj",
    "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
    "endobj",
    "4 0 obj",
    "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    "endobj",
    "5 0 obj",
    "<< /Length 238 >>",
    "stream",
    "BT",
    "/F1 18 Tf",
    "72 720 Td",
    "(Voila v0.7.17a diagnostic fixture) Tj",
    "0 -32 Td",
    "/F1 12 Tf",
    "(Synthetic non-confidential local diagnostic PDF.) Tj",
    "0 -22 Td",
    "(Use only to reproduce the owner-local /generate 500 failure.) Tj",
    "0 -22 Td",
    "(No private, confidential, legal, medical, financial, or safety-critical content.) Tj",
    "ET",
    "endstream",
    "endobj",
    "xref",
    "0 6",
    "0000000000 65535 f ",
    "0000000009 00000 n ",
    "0000000058 00000 n ",
    "0000000115 00000 n ",
    "0000000241 00000 n ",
    "0000000311 00000 n ",
    "trailer",
    "<< /Size 6 /Root 1 0 R >>",
    "startxref",
    "599",
    "%%EOF"
  )

  Set-Content -LiteralPath $FixturePdf -Value ($pdfLines -join "`n") -Encoding ascii
  if (-not (Test-Path -LiteralPath $FixturePdf)) {
    throw "Fixture PDF was not created: $FixturePdf"
  }

  Write-Host "controlled_fixture_pdf_created=true"
  Write-Host "controlled_fixture_pdf_path=$FixturePdf"
}

function Start-WithCapturedUvicorn {
  Write-Step "Starting normal runtime once to initialize LanguageTool and discover Python"
  pwsh -NoProfile -ExecutionPolicy Bypass -File ".\scripts\dev\start-voila.ps1" -Silent
  $script:StartedRuntime = $true
  Start-Sleep -Seconds 3

  $uvicornProcessId = Get-PortOwningProcessId -Port 8787
  if ($null -eq $uvicornProcessId) {
    throw "Could not find Uvicorn process on port 8787 after start-voila."
  }

  $proc = Get-CimInstance Win32_Process -Filter "ProcessId=$uvicornProcessId"
  $cmdLine = [string]$proc.CommandLine
  Write-Host "diagnostic_original_uvicorn_pid=$uvicornProcessId"
  Write-Host "diagnostic_original_uvicorn_cmd=$cmdLine"

  $pythonExe = $null
  if ($cmdLine -match '^"([^"]+python\.exe)"') {
    $pythonExe = $Matches[1]
  } elseif ($cmdLine -match '^(\S*python\.exe)') {
    $pythonExe = $Matches[1]
  }

  if (-not $pythonExe -or -not (Test-Path -LiteralPath $pythonExe)) {
    Write-Step "Could not parse python.exe from original command; using PATH python"
    $pythonExe = "python"
  }

  Stop-PortOwner -Port 8787

  Remove-Item -LiteralPath $StdOutLog,$StdErrLog -Force -ErrorAction SilentlyContinue

  Write-Step "Starting captured Uvicorn with redirected logs"
  $args = @(
    "-m", "uvicorn",
    "web_app:app",
    "--app-dir", ".\services\api",
    "--host", "127.0.0.1",
    "--port", "8787",
    "--log-level", "debug"
  )

  $script:CapturedUvicorn = Start-Process `
    -FilePath $pythonExe `
    -ArgumentList $args `
    -WorkingDirectory (Get-Location).Path `
    -RedirectStandardOutput $StdOutLog `
    -RedirectStandardError $StdErrLog `
    -PassThru `
    -WindowStyle Hidden

  Start-Sleep -Seconds 4

  try {
    Invoke-WebRequest -Uri "$BaseUrl/health" -Method GET -UseBasicParsing -TimeoutSec 10 | Out-Null
  } catch {
    throw "Captured Uvicorn did not respond on /health. stdout=$StdOutLog stderr=$StdErrLog"
  }

  Write-Host "captured_uvicorn_pid=$($script:CapturedUvicorn.Id)"
  Write-Host "uvicorn_stdout_log=$StdOutLog"
  Write-Host "uvicorn_stderr_log=$StdErrLog"
}

function Stop-DiagnosticRuntime {
  if ($null -ne $script:CapturedUvicorn -and -not $script:CapturedUvicorn.HasExited) {
    Write-Step "Stopping captured Uvicorn PID $($script:CapturedUvicorn.Id)"
    Stop-Process -Id $script:CapturedUvicorn.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
  }

  if ($script:StartedRuntime) {
    Write-Step "Stopping owner-local runtime via scripts/dev/stop-voila.ps1 -Silent"
    pwsh -NoProfile -ExecutionPolicy Bypass -File ".\scripts\dev\stop-voila.ps1" -Silent
  }
}

function Write-DiagnosticSummary {
  param([string]$ManualResult)

  $stderrTail = ""
  $stdoutTail = ""

  if (Test-Path -LiteralPath $StdErrLog) {
    $stderrTail = (Get-Content -LiteralPath $StdErrLog -Tail 160 -ErrorAction SilentlyContinue) -join "`n"
  }

  if (Test-Path -LiteralPath $StdOutLog) {
    $stdoutTail = (Get-Content -LiteralPath $StdOutLog -Tail 100 -ErrorAction SilentlyContinue) -join "`n"
  }

  $summary = @"
Voila v0.7.17a /generate 500 diagnostic

diagnostic_completed=true
manual_result=$ManualResult
generate_500_reproduced=$($ManualResult -eq "REPRODUCED_500")
base_url=$BaseUrl
fixture_pdf=$FixturePdf
uvicorn_stdout_log=$StdOutLog
uvicorn_stderr_log=$StdErrLog
build_created=false
zip_created=false
delivery_performed=false
distribution_performed=false
real_private_confidential_data_used=false
delete_reset_cleanup_performed=false
feature_changes=false
behavior_changes=false
public_ui_expansion=false

--- stderr tail ---
$stderrTail

--- stdout tail ---
$stdoutTail
"@

  Set-Content -LiteralPath $SummaryPath -Value $summary -Encoding utf8NoBOM
  Write-Host "diagnostic_summary_path=$SummaryPath"
}

Write-Host ""
Write-Host "=== Voila v0.7.17a owner-local /generate 500 diagnostic ==="
Write-Host ""

Write-Step "Policy guard: diagnostic only; controlled synthetic fixture; no build/ZIP/distribution"
Write-Host "server_start_local=permitted"
Write-Host "manual_browser_open=permitted"
Write-Host "controlled_fixture_upload_generate_manual=permitted_once"
Write-Host "diagnostic_log_capture=permitted"
Write-Host "build_created=false"
Write-Host "zip_created=false"
Write-Host "delivery_performed=false"
Write-Host "distribution_performed=false"
Write-Host "real_private_confidential_data_used=false"
Write-Host "delete_reset_cleanup_performed=false"
Write-Host "feature_changes=false"
Write-Host "behavior_changes=false"
Write-Host "public_ui_expansion=false"

New-ControlledFixturePdf

try {
  Start-WithCapturedUvicorn

  Invoke-GetCheck -Path "/health" -Name "health_get_check" | Out-Null
  Invoke-GetCheck -Path "/" -Name "homepage_get_check" | Out-Null
  Invoke-GetCheck -Path "/quick-tools" -Name "readonly_route_quick_tools_get_check" -Optional | Out-Null
  Invoke-GetCheck -Path "/exam-prep" -Name "readonly_route_exam_prep_get_check" -Optional | Out-Null
  Write-Host "readonly_routes_get_check=pass_or_optional_skipped"

  if ($OpenBrowser) {
    Write-Step "Opening browser /"
    Start-Process "$BaseUrl/" | Out-Null
    Start-Sleep -Milliseconds 500
    Start-Process $EvidenceRoot | Out-Null
  }

  Write-Host ""
  Write-Host "Manual diagnostic rule:"
  Write-Host "- Use only this synthetic PDF:"
  Write-Host "  $FixturePdf"
  Write-Host "- Upload exactly this file."
  Write-Host "- Run generate once, enough to reproduce or not reproduce the /generate result."
  Write-Host "- Do not use private/confidential files."
  Write-Host "- Do not delete/reset/cleanup/export/build/zip/deliver/distribute anything."
  Write-Host ""
  Write-Host "After the attempt, answer with one of:"
  Write-Host "  REPRODUCED_500  = browser showed Internal Server Error / 500"
  Write-Host "  NO_500          = generate did not reproduce the 500"
  Write-Host ""

  $manualResult = $Result
  if ($manualResult -eq "PROMPT") {
    $manualResult = Read-Host "Diagnostic result"
  }

  if ($manualResult -ne "REPRODUCED_500" -and $manualResult -ne "NO_500") {
    throw "Invalid diagnostic result. Expected REPRODUCED_500 or NO_500."
  }

  Write-Host "manual_diagnostic_result=$manualResult"
  Write-Host "generate_500_reproduced=$($manualResult -eq 'REPRODUCED_500')"

  Write-DiagnosticSummary -ManualResult $manualResult

  Write-Host $FinalMarker
} finally {
  Stop-DiagnosticRuntime

  Write-Host ""
  Write-Host "=== Final check ==="
  Write-Host ""
  Write-Host "DONE."
}
