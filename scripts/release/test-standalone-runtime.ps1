param(
    [string]$VersionTag = "voila-v0.1.5-polish-runtime",
    [string]$ReleaseRoot = "D:\dev\releases",
    [string]$TestRootBase = "D:\dev\release-tests",
    [int]$VoilaPort = 8780,
    [int]$LanguageToolPort = 8081
)

$ErrorActionPreference = "Stop"

$ZipPath = Join-Path $ReleaseRoot "$VersionTag.zip"
$TestRoot = Join-Path $TestRootBase "$VersionTag-clean"

if (-not (Test-Path $ZipPath)) {
    throw "ZIP lipsă: $ZipPath"
}

Write-Host "=== Voila release smoke test ==="
Write-Host "Version: $VersionTag"
Write-Host "ZIP:     $ZipPath"
Write-Host "Test:    $TestRoot"

Write-Host "=== OPRESC PORTURI EXISTENTE ==="
foreach ($port in @($VoilaPort, $LanguageToolPort)) {
    $pids = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique

    foreach ($pidValue in $pids) {
        if ($pidValue) {
            Write-Host "Stop PID $pidValue pe port $port"
            Stop-Process -Id $pidValue -Force -ErrorAction SilentlyContinue
        }
    }
}

Start-Sleep -Milliseconds 500

Write-Host "=== EXTRAG ZIP ÎN FOLDER CURAT ==="
Remove-Item $TestRoot -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $TestRoot | Out-Null
Expand-Archive -Path $ZipPath -DestinationPath $TestRoot -Force

$AppRoot = Join-Path $TestRoot "app"

$requiredFiles = @(
    "python\python.exe",
    "runtime\tesseract\tesseract.exe",
    "runtime\java\bin\java.exe",
    "runtime\languagetool\languagetool-server.jar",
    "Run-Voila.ps1",
    "Stop-Voila.ps1",
    "language-packs\core\ro.language-pack.json",
    "language-packs\core\en.language-pack.json",
    "language-packs\schema\language-pack.schema.json"
)

Write-Host "=== VERIFIC FIȘIERE CHEIE ==="
foreach ($relative in $requiredFiles) {
    $full = Join-Path $AppRoot $relative
    if (-not (Test-Path $full)) {
        throw "Fișier lipsă: $full"
    }
    Get-Item $full | Select-Object FullName, Length
}

Write-Host "=== VERIFIC LANGUAGE PACKS ÎN ZIP EXTRAS ==="
$ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$LanguagePackInspectScript = Join-Path $ProjectRoot "scripts\release\inspect-language-pack-packaging.ps1"
if (-not (Test-Path $LanguagePackInspectScript)) {
    throw "Script inspectare language packs lipsă: $LanguagePackInspectScript"
}
& powershell -ExecutionPolicy Bypass -File $LanguagePackInspectScript -ProjectRoot $ProjectRoot -PackagedAppRoot $AppRoot
if ($LASTEXITCODE -ne 0) {
    throw "Inspectarea language-pack ZIP extras a eșuat."
}


$oldPath = $env:Path

try {
    Write-Host "=== SCOT PYTHON / TESSERACT / JAVA DIN PATH ==="

    $env:Path = (($env:Path -split ";") | Where-Object {
        $_ -notmatch "(?i)python" `
        -and $_ -notmatch "(?i)windowsapps" `
        -and $_ -notmatch "(?i)tesseract" `
        -and $_ -notmatch "(?i)eclipse adoptium" `
        -and $_ -notmatch "(?i)java"
    }) -join ";"

    if (Get-Command python -ErrorAction SilentlyContinue) {
        throw "Python încă este în PATH."
    }

    if (Get-Command tesseract.exe -ErrorAction SilentlyContinue) {
        throw "Tesseract încă este în PATH."
    }

    if (Get-Command java.exe -ErrorAction SilentlyContinue) {
        throw "Java încă este în PATH."
    }

    Write-Host "OK: Python / Tesseract / Java NU sunt în PATH."

    Write-Host "=== PORNESC VOILA ==="
    & (Join-Path $AppRoot "Run-Voila.ps1") -NoBrowser -Port $VoilaPort

    Write-Host "=== HEALTH ==="
    curl.exe -fsS "http://127.0.0.1:$VoilaPort/health"
    Write-Host ""

    Write-Host "=== LANGUAGETOOL ==="
    $ltResponse = Invoke-WebRequest `
        -Uri "http://127.0.0.1:$LanguageToolPort/v2/check" `
        -Method Post `
        -Body @{
            language = "en-US"
            text = "This are a test."
        } `
        -UseBasicParsing

    if ($ltResponse.StatusCode -ne 200) {
        throw "LanguageTool status invalid: $($ltResponse.StatusCode)"
    }

    $ltJson = $ltResponse.Content | ConvertFrom-Json
    $ruleIds = @($ltJson.matches | ForEach-Object { $_.rule.id })

    if ($ruleIds -notcontains "THIS_NNS" -and $ruleIds -notcontains "PLURAL_VERB_AFTER_THIS") {
        throw "LanguageTool nu a returnat regulile așteptate."
    }

    $ltJson.matches |
        Select-Object message, shortMessage, @{Name="RuleId";Expression={$_.rule.id}} |
        Format-Table -AutoSize

    Write-Host "=== TESSERACT ==="
    $runtimeTesseract = Join-Path $AppRoot "runtime\tesseract\tesseract.exe"
    $env:TESSDATA_PREFIX = Join-Path $AppRoot "runtime\tesseract"

    $langs = & $runtimeTesseract --list-langs
    $langs | Out-Host

    foreach ($requiredLang in @("eng","osd","ron","rus")) {
        if (-not ($langs -match "tessdata/$requiredLang|^$requiredLang$")) {
            throw "Limbă OCR lipsă: $requiredLang"
        }
    }

    Write-Host "=== OPRESC VOILA + LANGUAGETOOL ==="
    & (Join-Path $AppRoot "Stop-Voila.ps1") -Port $VoilaPort -LanguageToolPort $LanguageToolPort

    $stillOpen = Get-NetTCPConnection -LocalPort $VoilaPort,$LanguageToolPort -State Listen -ErrorAction SilentlyContinue
    if ($stillOpen) {
        $stillOpen | Format-Table -AutoSize
        throw "Un port a rămas deschis după stop."
    }

    Write-Host "=== SMOKE TEST PASS ==="
}
finally {
    $env:Path = $oldPath
}
