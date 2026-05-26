param(
    [switch]$Silent
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $ScriptDir "..\.."))
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

$VoilaHost = "127.0.0.1"
$VoilaPort = 8787
$LtHost = "127.0.0.1"
$LtPort = 8081

$LanguageToolDir = "D:\dev\tools\LanguageTool"
$LanguageToolJar = Join-Path $LanguageToolDir "languagetool-server.jar"
$LanguageToolConfig = Join-Path $LanguageToolDir "server.properties"

function Test-PortListening {
    param(
        [int]$Port
    )

    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -First 1

    return $null -ne $conn
}

function Wait-HttpOk {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 30
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)

    while ((Get-Date) -lt $deadline) {
        try {
            $r = Invoke-WebRequest $Url -UseBasicParsing -TimeoutSec 3
            if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) {
                return $true
            }
        } catch {
            Start-Sleep -Milliseconds 700
        }
    }

    return $false
}

function Test-LanguageTool {
    try {
        $body = @{
            language = "ro-RO"
            text = "Acesta este un text cu greseli si functionare incorecta."
        }

        $r = Invoke-RestMethod `
            -Method Post `
            -Uri "http://$LtHost`:$LtPort/v2/check" `
            -Body $body `
            -TimeoutSec 5

        return $true
    } catch {
        return $false
    }
}

Write-Host ""
Write-Host "=== Voila start ==="
Write-Host "Project:" $ProjectRoot
Write-Host ""

if (!(Test-Path $Python)) {
    throw "Nu găsesc Python venv: $Python"
}

Write-Host "=== 1. Compile check ==="
& $Python -m py_compile (Join-Path $ProjectRoot "services\api\web_app.py")
& $Python -m py_compile (Join-Path $ProjectRoot "services\api\ocr_languagetool.py")
Write-Host "OK: Python files compile."
Write-Host ""

Write-Host "=== 2. LanguageTool ==="

if (Test-LanguageTool) {
    Write-Host "OK: LanguageTool rulează deja pe http://$LtHost`:$LtPort"
} else {
    if (!(Get-Command java -ErrorAction SilentlyContinue)) {
        throw "Java nu este disponibil. Instalează: winget install EclipseAdoptium.Temurin.21.JRE --source winget"
    }

    if (!(Test-Path $LanguageToolJar)) {
        throw "Nu găsesc LanguageTool jar: $LanguageToolJar"
    }

    if (!(Test-Path $LanguageToolConfig)) {
        New-Item -ItemType File -Force -Path $LanguageToolConfig | Out-Null
    }

    Write-Host "Pornesc LanguageTool într-o fereastră separată..."

    $ltCommand = @"
cd '$LanguageToolDir'
java -cp languagetool-server.jar org.languagetool.server.HTTPServer --config server.properties --port $LtPort --allow-origin
"@

    if ($Silent) {
        Start-Process `
            -FilePath "java" `
            -WorkingDirectory $LanguageToolDir `
            -ArgumentList @(
                "-cp",
                "languagetool-server.jar",
                "org.languagetool.server.HTTPServer",
                "--config",
                "server.properties",
                "--port",
                "$LtPort",
                "--allow-origin"
            ) `
            -WindowStyle Hidden
    } else {
        Start-Process pwsh -ArgumentList @(
            "-NoExit",
            "-Command",
            $ltCommand
        )
    }
Write-Host "Aștept LanguageTool..."

    $ok = $false
    for ($i = 0; $i -lt 40; $i++) {
        if (Test-LanguageTool) {
            $ok = $true
            break
        }
        Start-Sleep -Seconds 1
    }

    if (!$ok) {
        Write-Host "WARN: LanguageTool nu a răspuns încă. Voila va porni, dar Verifică text poate afișa eroare."
    } else {
        Write-Host "OK: LanguageTool pornit."
    }
}

Write-Host ""
Write-Host "=== 3. Voila web app ==="

if (Test-PortListening -Port $VoilaPort) {
    Write-Host "OK: Voila pare deja pornit pe http://$VoilaHost`:$VoilaPort"
} else {
    Write-Host "Pornesc Voila într-o fereastră separată..."

    $voilaCommand = @"
cd '$ProjectRoot'
& '$Python' -m uvicorn web_app:app --app-dir '.\services\api' --host $VoilaHost --port $VoilaPort --log-level info
"@

    if ($Silent) {
        Start-Process `
            -FilePath $Python `
            -WorkingDirectory $ProjectRoot `
            -ArgumentList @(
                "-m",
                "uvicorn",
                "web_app:app",
                "--app-dir",
                ".\services\api",
                "--host",
                "$VoilaHost",
                "--port",
                "$VoilaPort",
                "--log-level",
                "info"
            ) `
            -WindowStyle Hidden
    } else {
        Start-Process pwsh -ArgumentList @(
            "-NoExit",
            "-Command",
            $voilaCommand
        )
    }
Write-Host "Aștept Voila..."

    $ready = Wait-HttpOk -Url "http://$VoilaHost`:$VoilaPort/" -TimeoutSeconds 30

    if (!$ready) {
        throw "Voila nu a răspuns pe http://$VoilaHost`:$VoilaPort/"
    }

    Write-Host "OK: Voila pornit."
}

Write-Host ""
Write-Host "=== 4. Open browser ==="

$Url = "http://$VoilaHost`:$VoilaPort/"
Write-Host "Open:" $Url
Start-Process $Url

Write-Host ""
Write-Host "DONE."
if ($Silent) {
    Write-Host "Silent mode: LanguageTool and Voila were started in hidden background windows."
} else {
    Write-Host "Ține deschise ferestrele PowerShell pentru LanguageTool și Voila."
}

