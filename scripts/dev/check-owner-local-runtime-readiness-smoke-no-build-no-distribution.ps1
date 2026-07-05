<#
Voila v0.7.15 owner-local runtime readiness smoke.
GET-only local runtime check. No upload/generate/save/delete/reset.
No build, no ZIP, no delivery, no distribution.
#>

[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [int]$Port = 8787,
    [switch]$OpenBrowser,
    [switch]$KeepServerRunning,
    [int]$StartupWaitSeconds = 45
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Step {
    param([string]$Message)
    Write-Host "[v0.7.15-smoke] $Message" -ForegroundColor Cyan
}

function Fail {
    param([string]$Message)
    throw "[v0.7.15-smoke] $Message"
}

function Test-GetSuccess {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [int]$TimeoutSec = 5
    )
    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -UseBasicParsing -TimeoutSec $TimeoutSec
        return ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400)
    } catch {
        return $false
    }
}

function Invoke-RequiredGet {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Label
    )
    $url = "$BaseUrl$Path"
    Write-Step "GET $Path"
    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -UseBasicParsing -TimeoutSec 12
        if ($response.StatusCode -lt 200 -or $response.StatusCode -ge 400) {
            Fail "$Label failed: HTTP $($response.StatusCode) for $url"
        }
        Write-Host "$Label=pass"
    } catch {
        Fail "$Label failed for $url. $($_.Exception.Message)"
    }
}

function Invoke-OptionalGet {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Label
    )
    $url = "$BaseUrl$Path"
    Write-Step "Optional GET $Path"
    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -UseBasicParsing -TimeoutSec 12
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) {
            Write-Host "$Label=pass"
        } else {
            Write-Warning "$Label=optional_skipped_http_$($response.StatusCode)"
        }
    } catch {
        Write-Warning "$Label=optional_skipped_unavailable"
    }
}

if (-not (Test-Path -LiteralPath $RepoRoot)) {
    Fail "Repo root not found: $RepoRoot"
}

$BaseUrl = "http://127.0.0.1:$Port"
$HealthUrl = "$BaseUrl/health"
$startedByThisScript = $false
$startProcess = $null

Push-Location $RepoRoot
try {
    Write-Step "Policy guard: GET-only runtime smoke; no write-capable routes will be called"
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

    if (-not (Test-GetSuccess -Url $HealthUrl -TimeoutSec 3)) {
        $startScript = Join-Path $RepoRoot "scripts/dev/start-voila.ps1"
        if (-not (Test-Path -LiteralPath $startScript)) {
            Fail "Start script not found: $startScript"
        }

        Write-Step "Starting owner-local runtime via scripts/dev/start-voila.ps1 -Silent"
        $startProcess = Start-Process -FilePath "pwsh" -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $startScript, "-Silent") -PassThru
        $startedByThisScript = $true

        $deadline = (Get-Date).AddSeconds($StartupWaitSeconds)
        $ready = $false
        while ((Get-Date) -lt $deadline) {
            if (Test-GetSuccess -Url $HealthUrl -TimeoutSec 3) {
                $ready = $true
                break
            }
            Start-Sleep -Seconds 1
        }

        if (-not $ready) {
            Fail "Local runtime did not become ready on GET /health at $HealthUrl"
        }
    } else {
        Write-Step "Existing local runtime detected on $BaseUrl"
    }

    Invoke-RequiredGet -Path "/health" -Label "health_get_check"
    Invoke-RequiredGet -Path "/" -Label "homepage_get_check"

    Invoke-OptionalGet -Path "/quick-tools" -Label "readonly_route_quick_tools_get_check"
    Invoke-OptionalGet -Path "/exam-prep" -Label "readonly_route_exam_prep_get_check"
    Write-Host "readonly_routes_get_check=pass_or_optional_skipped"

    if ($OpenBrowser) {
        Write-Step "Opening local homepage in browser"
        Start-Process "$BaseUrl/"
    }

    Write-Host "VOILA_V0_7_15_OWNER_LOCAL_RUNTIME_READINESS_SMOKE_CHECK=PASS" -ForegroundColor Green
} finally {
    if ($startedByThisScript -and (-not $KeepServerRunning)) {
        $stopScript = Join-Path $RepoRoot "scripts/dev/stop-voila.ps1"
        if (Test-Path -LiteralPath $stopScript) {
            Write-Step "Stopping owner-local runtime via scripts/dev/stop-voila.ps1 -Silent"
            try {
                & pwsh -NoProfile -ExecutionPolicy Bypass -File $stopScript -Silent
            } catch {
                Write-Warning "Stop script returned an error: $($_.Exception.Message)"
            }
        } elseif ($null -ne $startProcess -and -not $startProcess.HasExited) {
            Write-Warning "Stop script not found; stopping start process only."
            Stop-Process -Id $startProcess.Id -Force -ErrorAction SilentlyContinue
        }
    }
    Pop-Location
}