[CmdletBinding()]
param(
  [string]$BaseUrl = "http://127.0.0.1:8787",
  [switch]$OpenBrowser
)

$ErrorActionPreference = "Stop"

$Milestone = "v0.7.17d-write-smoke"
$FinalMarker = "VOILA_V0_7_17D_OWNER_LOCAL_CONTROLLED_FIXTURE_WRITE_SMOKE_CHECK=PASS"
$EvidenceRoot = Join-Path $env:TEMP "voila-v0.7.17d-controlled-fixture-write-smoke"
$FixturePdf = Join-Path $EvidenceRoot "voila-v0.7.17d-controlled-fixture.pdf"
$StdOutLog = Join-Path $EvidenceRoot "uvicorn.stdout.log"
$StdErrLog = Join-Path $EvidenceRoot "uvicorn.stderr.log"
$SummaryPath = Join-Path $EvidenceRoot "controlled-fixture-write-smoke-summary.txt"
$StartedRuntime = $false
$CapturedUvicorn = $null
$UploadedName = $null
$GeneratedUrl = $null
$OutputDir = $null

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
    Write-Step "Stopping process on port $Port PID $owningProcessId for controlled write smoke log capture"
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
    "<< /Length 316 >>",
    "stream",
    "BT",
    "/F1 18 Tf",
    "72 720 Td",
    "(Voila v0.7.17d controlled write smoke fixture) Tj",
    "0 -32 Td",
    "/F1 12 Tf",
    "(Synthetic non-confidential local write-smoke PDF.) Tj",
    "0 -22 Td",
    "(This fixture validates upload, generate, and expected local output files.) Tj",
    "0 -22 Td",
    "(No private, confidential, legal, medical, financial, or safety-critical content.) Tj",
    "0 -22 Td",
    "(Policy: no build, no ZIP, no delivery, no distribution.) Tj",
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
  Write-Host "write_smoke_original_uvicorn_pid=$uvicornProcessId"
  Write-Host "write_smoke_original_uvicorn_cmd=$cmdLine"

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

function Stop-SmokeRuntime {
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

function Invoke-CurlInclude {
  param([string[]]$Arguments)

  $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
  if ($null -eq $curl) {
    throw "curl.exe not found; cannot run automated controlled write smoke."
  }

  $output = & curl.exe @Arguments
  $exit = $LASTEXITCODE
  if ($exit -ne 0) {
    throw "curl.exe failed with exit code $exit. Args: $($Arguments -join ' ')"
  }

  return ($output -join "`n")
}

function Get-HttpStatusFromCurlOutput {
  param([string]$Text)

  $statuses = [regex]::Matches($Text, 'HTTP/\S+\s+(\d{3})')
  if ($statuses.Count -eq 0) {
    throw "Could not parse HTTP status from curl output."
  }

  return [int]$statuses[$statuses.Count - 1].Groups[1].Value
}

function Get-LocationHeaderFromCurlOutput {
  param([string]$Text)

  $matchesLocal = [regex]::Matches($Text, '(?im)^location:\s*(.+?)\s*$')
  if ($matchesLocal.Count -eq 0) {
    throw "Could not parse Location header from curl output."
  }

  return $matchesLocal[$matchesLocal.Count - 1].Groups[1].Value.Trim()
}

function Invoke-ControlledWriteSmoke {
  $fixtureItem = Get-Item -LiteralPath $FixturePdf
  Write-Step "Automated POST /upload for synthetic fixture"

  $uploadOutput = Invoke-CurlInclude -Arguments @(
    "--silent",
    "--show-error",
    "--include",
    "--max-time",
    "120",
    "--form",
    "file=@$($fixtureItem.FullName);type=application/pdf",
    "$BaseUrl/upload"
  )

  $uploadStatus = Get-HttpStatusFromCurlOutput -Text $uploadOutput
  $uploadLocation = Get-LocationHeaderFromCurlOutput -Text $uploadOutput

  Write-Host "upload_status=$uploadStatus"
  Write-Host "upload_location=$uploadLocation"

  if ($uploadStatus -ne 303) {
    throw "Expected POST /upload status 303, got $uploadStatus."
  }

  if ($uploadLocation -notmatch 'uploaded=([^&\s]+)') {
    throw "Could not parse uploaded filename from Location: $uploadLocation"
  }

  $script:UploadedName = [System.Uri]::UnescapeDataString($Matches[1])
  Write-Host "uploaded_pdf_name=$script:UploadedName"

  Write-Step "Automated POST /generate for uploaded synthetic fixture"
  $generateOutput = Invoke-CurlInclude -Arguments @(
    "--silent",
    "--show-error",
    "--include",
    "--max-time",
    "300",
    "--form",
    "pdf_name=$script:UploadedName",
    "$BaseUrl/generate"
  )

  $generateStatus = Get-HttpStatusFromCurlOutput -Text $generateOutput
  $generateLocation = Get-LocationHeaderFromCurlOutput -Text $generateOutput

  Write-Host "generate_status=$generateStatus"
  Write-Host "generate_location=$generateLocation"

  if ($generateStatus -ne 303) {
    throw "Expected POST /generate status 303, got $generateStatus."
  }

  if ($generateLocation -notmatch 'generated=([^&\s]+)') {
    throw "Could not parse generated filename from Location: $generateLocation"
  }

  $generatedName = [System.Uri]::UnescapeDataString($Matches[1])
  if ($generatedName -ne $script:UploadedName) {
    throw "Generated filename mismatch. uploaded=$script:UploadedName generated=$generatedName"
  }

  $script:GeneratedUrl = "$BaseUrl/?generated=$([System.Uri]::EscapeDataString($generatedName))"

  Write-Step "GET generated homepage"
  $generatedResponse = Invoke-WebRequest -Uri $script:GeneratedUrl -Method GET -UseBasicParsing -TimeoutSec 30
  Write-Host "generated_homepage_status=$($generatedResponse.StatusCode)"

  if ($generatedResponse.StatusCode -ne 200) {
    throw "Expected generated homepage status 200, got $($generatedResponse.StatusCode)."
  }
}

function Assert-ExpectedOutputs {
  if (-not $script:UploadedName) {
    throw "UploadedName missing."
  }

  $inputPath = Join-Path (Get-Location).Path ("data/input/" + $script:UploadedName)
  $stem = [System.IO.Path]::GetFileNameWithoutExtension($script:UploadedName)
  $script:OutputDir = Join-Path (Get-Location).Path ("data/output/" + $stem)

  Write-Host "input_pdf_path=$inputPath"
  Write-Host "output_dir=$script:OutputDir"

  if (-not (Test-Path -LiteralPath $inputPath)) {
    throw "Expected uploaded input PDF missing: $inputPath"
  }

  if (-not (Test-Path -LiteralPath $script:OutputDir)) {
    throw "Expected output directory missing: $script:OutputDir"
  }

  $expected = @(
    "pages.json",
    "pages.md",
    "course_outline.json",
    "course_outline.md",
    "course_outline.normalized.json",
    "course_outline.normalized.md",
    "course.md",
    "course.cleaned.md",
    "glossary.json",
    "quiz.json",
    "flashcards.json",
    "ocr_corrections.json"
  )

  $missing = @()
  foreach ($name in $expected) {
    $path = Join-Path $script:OutputDir $name
    if (Test-Path -LiteralPath $path) {
      Write-Host "generated_output_$name=present"
    } else {
      Write-Host "generated_output_$name=missing"
      $missing += $name
    }
  }

  if ($missing.Count -gt 0) {
    throw "Missing expected generated outputs: $($missing -join ', ')"
  }

  Write-Host "expected_outputs_present=true"
}

function Assert-NoForbiddenRequests {
  $combined = ""

  if (Test-Path -LiteralPath $StdOutLog) {
    $combined += "`n" + (Get-Content -LiteralPath $StdOutLog -Raw -ErrorAction SilentlyContinue)
  }

  if (Test-Path -LiteralPath $StdErrLog) {
    $combined += "`n" + (Get-Content -LiteralPath $StdErrLog -Raw -ErrorAction SilentlyContinue)
  }

  foreach ($forbidden in @("/delete", "/delete-from-library", "/study-reset", "/reset", "/cleanup", "/export")) {
    if ($combined -match [regex]::Escape($forbidden)) {
      throw "Forbidden request detected in logs: $forbidden"
    }
  }

  if ($combined -match 'POST /generate HTTP/1\.1" 500') {
    throw "POST /generate returned 500 in logs."
  }

  Write-Host "forbidden_requests_detected=false"
  Write-Host "generate_500_detected=false"
}

function Write-SmokeSummary {
  $stderrTail = ""
  $stdoutTail = ""

  if (Test-Path -LiteralPath $StdErrLog) {
    $stderrTail = (Get-Content -LiteralPath $StdErrLog -Tail 180 -ErrorAction SilentlyContinue) -join "`n"
  }

  if (Test-Path -LiteralPath $StdOutLog) {
    $stdoutTail = (Get-Content -LiteralPath $StdOutLog -Tail 160 -ErrorAction SilentlyContinue) -join "`n"
  }

  $summary = @"
Voila v0.7.17d controlled fixture write smoke

controlled_fixture_write_smoke_completed=true
upload_status=303
generate_status=303
generated_homepage_status=200
uploaded_pdf_name=$script:UploadedName
generated_url=$script:GeneratedUrl
output_dir=$script:OutputDir
expected_outputs_present=true
forbidden_requests_detected=false
generate_500_detected=false
delete_reset_cleanup_performed=false
build_created=false
zip_created=false
delivery_performed=false
distribution_performed=false
real_private_confidential_data_used=false
feature_changes=false
behavior_changes=false
public_ui_expansion=false
fixture_pdf=$FixturePdf
uvicorn_stdout_log=$StdOutLog
uvicorn_stderr_log=$StdErrLog

--- stderr tail ---
$stderrTail

--- stdout tail ---
$stdoutTail
"@

  Set-Content -LiteralPath $SummaryPath -Value $summary -Encoding utf8NoBOM
  Write-Host "write_smoke_summary_path=$SummaryPath"
}

Write-Host ""
Write-Host "=== Voila v0.7.17d owner-local controlled fixture write smoke ==="
Write-Host ""

Write-Step "Policy guard: automated synthetic upload/generate only; no delete/reset/cleanup/build/ZIP/distribution"
Write-Host "server_start_local=permitted"
Write-Host "controlled_fixture_upload_generate_automated=permitted_once"
Write-Host "validation_log_capture=permitted"
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

  Invoke-ControlledWriteSmoke
  Assert-ExpectedOutputs
  Assert-NoForbiddenRequests
  Write-SmokeSummary

  if ($OpenBrowser -and $script:GeneratedUrl) {
    Write-Step "Opening generated homepage"
    Start-Process $script:GeneratedUrl | Out-Null
    Start-Sleep -Milliseconds 500
    Start-Process $EvidenceRoot | Out-Null
  }

  Write-Host $FinalMarker
} finally {
  Stop-SmokeRuntime

  Write-Host ""
  Write-Host "=== Final check ==="
  Write-Host ""
  Write-Host "DONE."
}
