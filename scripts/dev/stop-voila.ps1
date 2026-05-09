$ErrorActionPreference = "Continue"

$VoilaPort = 8787
$LanguageToolPort = 8081

function Get-ProcessCommandLine {
    param([int]$ProcessId)

    try {
        $p = Get-CimInstance Win32_Process -Filter "ProcessId=$ProcessId" -ErrorAction Stop
        return [string]$p.CommandLine
    } catch {
        return ""
    }
}

function Stop-PortProcess {
    param(
        [int]$Port,
        [string]$Name
    )

    Write-Host ""
    Write-Host "=== Stop $Name on port $Port ==="

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

    if (!$connections) {
        Write-Host "OK: nimic nu ascultă pe portul $Port"
        return
    }

    $processIds = $connections |
        Select-Object -ExpandProperty OwningProcess |
        Sort-Object -Unique

    foreach ($processId in $processIds) {
        if (!$processId) {
            continue
        }

        $proc = Get-Process -Id $processId -ErrorAction SilentlyContinue
        $cmd = Get-ProcessCommandLine -ProcessId $processId

        if (!$proc) {
            Write-Host "Found PID $processId, dar procesul nu mai există."
            continue
        }

        Write-Host "Found PID $processId - $($proc.ProcessName)"
        Write-Host "CMD: $cmd"

        $isVoila = (
            $Port -eq 8787 -and
            $proc.ProcessName -like "python*" -and
            $cmd -like "*uvicorn*" -and
            $cmd -like "*web_app:app*"
        )

        $isLanguageTool = (
            $Port -eq 8081 -and
            $proc.ProcessName -like "java*" -and
            (
                $cmd -like "*languagetool-server.jar*" -or
                $cmd -like "*org.languagetool.server.HTTPServer*"
            )
        )

        if (!$isVoila -and !$isLanguageTool) {
            Write-Host "WARN: nu opresc PID $processId pentru că nu pare Voila/LanguageTool."
            continue
        }

        try {
            Write-Host "Stopping PID $processId - $($proc.ProcessName)"
            Stop-Process -Id $processId -Force -ErrorAction Stop
        } catch {
            Write-Host "WARN: nu pot opri PID $processId"
            Write-Host $_.Exception.Message
        }
    }

    Start-Sleep -Seconds 1

    $still = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

    if ($still) {
        Write-Host "WARN: portul $Port încă pare ocupat:"
        $still | Format-Table -AutoSize
    } else {
        Write-Host "OK: portul $Port este liber."
    }
}

Write-Host ""
Write-Host "=== Voila stop ==="

Stop-PortProcess -Port $VoilaPort -Name "Voila / Uvicorn"
Stop-PortProcess -Port $LanguageToolPort -Name "LanguageTool"

Write-Host ""
Write-Host "=== Final check ==="
Get-NetTCPConnection -LocalPort $VoilaPort,$LanguageToolPort -State Listen -ErrorAction SilentlyContinue |
    Select-Object LocalAddress,LocalPort,State,OwningProcess |
    Format-Table -AutoSize

Write-Host ""
Write-Host "DONE."
