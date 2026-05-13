param(
    [string]$VersionTag = "voila-v0.1.2-standalone-runtime",
    [string]$ReleaseRoot = "D:\dev\releases",
    [switch]$RefreshWheelhouse,
    [string]$TesseractRoot = "C:\Program Files\Tesseract-OCR",
    [string]$TessdataSource = "",
    [string[]]$TessLanguages = @("eng", "osd", "ron", "rus")
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $ScriptDir "..\..\"))
$RequirementsPath = Join-Path $ProjectRoot "services\api\requirements.txt"

function Invoke-RobocopyChecked {
    param(
        [string]$Source,
        [string]$Destination,
        [string[]]$RoboArgs
    )

    & robocopy $Source $Destination @RoboArgs | Out-Host

    if ($LASTEXITCODE -gt 7) {
        throw "Robocopy a eșuat cu exit code $LASTEXITCODE"
    }

    $global:LASTEXITCODE = 0
}

function Resolve-BuildPython {
    $candidates = @()

    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        $candidates += [pscustomobject]@{
            Exe = $pyLauncher.Source
            Args = @("-3.12")
        }
    }

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $candidates += [pscustomobject]@{
            Exe = $pythonCmd.Source
            Args = @()
        }
    }

    foreach ($candidate in $candidates) {
        try {
            $versionText = (& $candidate.Exe @($candidate.Args) -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')").Trim()
            $majorMinor = (& $candidate.Exe @($candidate.Args) -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')").Trim()

            if ($majorMinor -eq "3.12") {
                return [pscustomobject]@{
                    Exe = $candidate.Exe
                    Args = $candidate.Args
                    Version = $versionText
                    MajorMinor = $majorMinor
                }
            }
        }
        catch {
            continue
        }
    }

    throw "Nu găsesc Python 3.12 pentru build. Runtime-ul final nu va depinde de Python în PATH, dar build-ul are nevoie de Python 3.12."
}

function Write-RuntimeLaunchers {
    param(
        [string]$AppDir
    )

    $runScriptPath = Join-Path $AppDir "Run-Voila.ps1"
    $stopScriptPath = Join-Path $AppDir "Stop-Voila.ps1"
    $cmdPath = Join-Path $AppDir "Run-Voila.cmd"

    $runLines = @(
        'param(',
        '    [int]$Port = 8765,',
        '    [switch]$NoBrowser',
        ')',
        '',
        '$ErrorActionPreference = "Stop"',
        '',
        '$AppRoot = Split-Path -Parent $MyInvocation.MyCommand.Path',
        '$PythonExe = Join-Path $AppRoot "python\python.exe"',
        '$ApiDir = Join-Path $AppRoot "services\api"',
        '$LogsDir = Join-Path $AppRoot "logs"',
        '',
        'New-Item -ItemType Directory -Force $LogsDir | Out-Null',
        '',
        'if (-not (Test-Path $PythonExe)) { throw "Python runtime lipsă: $PythonExe" }',
        'if (-not (Test-Path $ApiDir)) { throw "API dir lipsă: $ApiDir" }',
        '',
        '$env:PYTHONUTF8 = "1"',
        '$env:PYTHONDONTWRITEBYTECODE = "1"',
        '$env:VOILA_RUNTIME = "standalone"',
        '',
        '$LocalTesseract = Join-Path $AppRoot "runtime\tesseract\tesseract.exe"',
        'if (Test-Path $LocalTesseract) { $env:TESSERACT_CMD = $LocalTesseract }',
        '',
        '$LocalJavaBin = Join-Path $AppRoot "runtime\java\bin"',
        'if (Test-Path (Join-Path $LocalJavaBin "java.exe")) { $env:Path = "$LocalJavaBin;$env:Path" }',
        '',
        '$Url = "http://127.0.0.1:$Port"',
        '$HealthUrl = "$Url/health"',
        '',
        'Write-Host "=== Voila standalone runtime ==="',
        'Write-Host "AppRoot: $AppRoot"',
        'Write-Host "Python:  $PythonExe"',
        'Write-Host "URL:     $Url"',
        '',
        '$existing = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue',
        'if ($existing) {',
        '    Write-Host "Portul $Port este deja folosit. Încerc health check..."',
        '    try {',
        '        curl.exe -fsS $HealthUrl | Out-Host',
        '        if (-not $NoBrowser) { Start-Process $Url }',
        '        exit 0',
        '    }',
        '    catch {',
        '        throw "Portul $Port este ocupat, dar aplicația nu răspunde la $HealthUrl"',
        '    }',
        '}',
        '',
        '$outLog = Join-Path $LogsDir "api.out.log"',
        '$errLog = Join-Path $LogsDir "api.err.log"',
        '',
        '$proc = Start-Process -FilePath $PythonExe -ArgumentList @("-m", "uvicorn", "web_app:app", "--host", "127.0.0.1", "--port", "$Port") -WorkingDirectory $ApiDir -RedirectStandardOutput $outLog -RedirectStandardError $errLog -WindowStyle Minimized -PassThru',
        '',
        'Write-Host "API pornit. PID: $($proc.Id)"',
        'Write-Host "Aștept health check..."',
        '',
        '$ok = $false',
        'for ($i = 1; $i -le 40; $i++) {',
        '    Start-Sleep -Milliseconds 500',
        '    try {',
        '        curl.exe -fsS $HealthUrl | Out-Null',
        '        $ok = $true',
        '        break',
        '    }',
        '    catch {',
        '        if ($proc.HasExited) {',
        '            Write-Host "API s-a oprit neașteptat."',
        '            if (Test-Path $errLog) { Get-Content $errLog -Tail 80 | Out-Host }',
        '            throw "Voila nu a pornit."',
        '        }',
        '    }',
        '}',
        '',
        'if (-not $ok) {',
        '    Write-Host "Health check timeout."',
        '    if (Test-Path $errLog) { Get-Content $errLog -Tail 80 | Out-Host }',
        '    throw "Voila nu a răspuns la $HealthUrl"',
        '}',
        '',
        'Write-Host "OK: $HealthUrl"',
        'if (-not $NoBrowser) { Start-Process $Url }'
    )

    $stopLines = @(
        'param(',
        '    [int]$Port = 8765',
        ')',
        '',
        '$ErrorActionPreference = "SilentlyContinue"',
        'Write-Host "Oprire Voila pe portul $Port..."',
        '',
        '$pids = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique',
        'foreach ($pidValue in $pids) {',
        '    if ($pidValue) {',
        '        Write-Host "Stop PID $pidValue"',
        '        Stop-Process -Id $pidValue -Force',
        '    }',
        '}',
        '',
        'Start-Sleep -Milliseconds 500',
        '$stillOpen = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue',
        'if ($stillOpen) { Write-Host "Portul $Port încă pare ocupat." } else { Write-Host "OK: portul $Port este liber." }'
    )

    $cmdLines = @(
        '@echo off',
        'where pwsh >nul 2>nul',
        'if %ERRORLEVEL% EQU 0 (',
        '  pwsh -ExecutionPolicy Bypass -File "%~dp0Run-Voila.ps1"',
        ') else (',
        '  powershell.exe -ExecutionPolicy Bypass -File "%~dp0Run-Voila.ps1"',
        ')'
    )

    $runLines | Set-Content -Path $runScriptPath -Encoding UTF8
    $stopLines | Set-Content -Path $stopScriptPath -Encoding UTF8
    $cmdLines | Set-Content -Path $cmdPath -Encoding ASCII
}

Write-Host "=== Voila standalone runtime build ==="
Write-Host "ProjectRoot: $ProjectRoot"
Write-Host "VersionTag:  $VersionTag"

if (-not (Test-Path $RequirementsPath)) {
    throw "Nu găsesc requirements.txt: $RequirementsPath"
}

if (-not (Test-Path $ReleaseRoot)) {
    New-Item -ItemType Directory -Force $ReleaseRoot | Out-Null
}

$gitStatus = (git -C $ProjectRoot status --short) -join "
"
if ($gitStatus.Trim()) {
    throw "Working tree nu este clean. Commit/stash înainte de build."
}

$BuildPython = Resolve-BuildPython
Write-Host "Build Python: $($BuildPython.Exe) $($BuildPython.Args -join ' ')"
Write-Host "Build Python version: $($BuildPython.Version)"

$CacheRoot = Join-Path $ProjectRoot ".release-cache"
$PythonCache = Join-Path $CacheRoot "python"
$Wheelhouse = Join-Path $CacheRoot "wheelhouse-py$($BuildPython.MajorMinor.Replace('.', ''))"

New-Item -ItemType Directory -Force $PythonCache, $Wheelhouse | Out-Null

$WorkRoot = Join-Path $env:TEMP ("voila-build-" + $VersionTag)
$StageDir = Join-Path $WorkRoot $VersionTag
$AppDir = Join-Path $StageDir "app"

Remove-Item $WorkRoot -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $AppDir | Out-Null

Write-Host ""
Write-Host "=== Copiez proiectul în staging ==="

Invoke-RobocopyChecked -Source $ProjectRoot -Destination $AppDir -RoboArgs @(
    "/E",
    "/XD",
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".next",
    "dist",
    "build",
    ".release-cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    "/XF",
    "*.pyc",
    "*.pyo",
    "*.log",
    ".env"
)

Write-Host ""
Write-Host "=== Curăț foldere locale care nu intră în runtime ==="

$LocalOnlyDirs = @(
    (Join-Path $AppDir "data"),
    (Join-Path $AppDir "audit"),
    (Join-Path $AppDir ".tessdata"),
    (Join-Path $AppDir ".release-cache")
)

foreach ($dir in $LocalOnlyDirs) {
    if (Test-Path $dir) {
        Write-Host "Remove local-only dir: $dir"
        Remove-Item $dir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "=== Recreez directoare runtime goale ==="

$RuntimeDataDirs = @(
    (Join-Path $AppDir "data"),
    (Join-Path $AppDir "data\input"),
    (Join-Path $AppDir "data\output"),
    (Join-Path $AppDir "data\trash"),
    (Join-Path $AppDir "logs"),
    (Join-Path $AppDir "runtime")
)

foreach ($dir in $RuntimeDataDirs) {
    New-Item -ItemType Directory -Force $dir | Out-Null
}
$PythonVersion = $BuildPython.Version
$PythonZipName = "python-$PythonVersion-embed-amd64.zip"
$PythonZipPath = Join-Path $PythonCache $PythonZipName
$PythonUrl = "https://www.python.org/ftp/python/$PythonVersion/$PythonZipName"
$PythonRuntimeDir = Join-Path $AppDir "python"

Write-Host ""
Write-Host "=== Pregătesc Python embeddable ==="

if (-not (Test-Path $PythonZipPath)) {
    Write-Host "Download: $PythonUrl"
    Invoke-WebRequest -Uri $PythonUrl -OutFile $PythonZipPath
}
else {
    Write-Host "Folosesc cache: $PythonZipPath"
}

New-Item -ItemType Directory -Force $PythonRuntimeDir | Out-Null
Expand-Archive -Path $PythonZipPath -DestinationPath $PythonRuntimeDir -Force

$PyMajorMinorCompact = $BuildPython.MajorMinor.Replace(".", "")
$PthPath = Join-Path $PythonRuntimeDir "python$PyMajorMinorCompact._pth"

if (-not (Test-Path $PthPath)) {
    throw "Nu găsesc fișierul _pth pentru Python embedded: $PthPath"
}

@(
    "python$PyMajorMinorCompact.zip",
    ".",
    "..\services\api",
    "Lib\site-packages",
    "import site"
) | Set-Content -Path $PthPath -Encoding ASCII

$SitePackages = Join-Path $PythonRuntimeDir "Lib\site-packages"
New-Item -ItemType Directory -Force $SitePackages | Out-Null

Write-Host ""
Write-Host "=== Pregătesc wheelhouse ==="

$wheelCount = @(Get-ChildItem $Wheelhouse -Filter "*.whl" -ErrorAction SilentlyContinue).Count

if ($RefreshWheelhouse -or $wheelCount -eq 0) {
    Write-Host "Descarc wheels în: $Wheelhouse"
    & $BuildPython.Exe @($BuildPython.Args) -m pip download --dest $Wheelhouse -r $RequirementsPath

    if ($LASTEXITCODE -ne 0) {
        throw "pip download a eșuat."
    }
}
else {
    Write-Host "Folosesc wheelhouse existent: $Wheelhouse"
}

Write-Host ""
Write-Host "=== Instalez dependențele în Python runtime ==="

& $BuildPython.Exe @($BuildPython.Args) -m pip install --no-index --find-links $Wheelhouse --target $SitePackages --upgrade -r $RequirementsPath

if ($LASTEXITCODE -ne 0) {
    throw "pip install în runtime a eșuat."
}

Write-Host ""
Write-Host "=== Scriu scripturile de runtime ==="
Write-RuntimeLaunchers -AppDir $AppDir

Write-Host ""
Write-Host "=== Validare importuri standalone ==="

Push-Location (Join-Path $AppDir "services\api")
try {
    & (Join-Path $PythonRuntimeDir "python.exe") -c "import sys; print(sys.version); import fastapi, uvicorn; import web_app; print('OK: imports standalone')"

    if ($LASTEXITCODE -ne 0) {
        throw "Validarea importurilor a eșuat."
    }
}
finally {
    Pop-Location
}

$ZipPath = Join-Path $ReleaseRoot "$VersionTag.zip"
$InfoPath = Join-Path $ReleaseRoot "$($VersionTag)_RELEASE-INFO.txt"

Remove-Item $ZipPath -Force -ErrorAction SilentlyContinue
Remove-Item $InfoPath -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=== Creez ZIP ==="


Write-Host ""

Write-Host ""
Write-Host "=== Pregătesc Tesseract runtime OCR ==="

if (-not $TesseractRoot) {
    throw "TesseractRoot este gol."
}

$TesseractRoot = [System.IO.Path]::GetFullPath($TesseractRoot)
$TesseractExe = Join-Path $TesseractRoot "tesseract.exe"
$InstalledTessdataDir = Join-Path $TesseractRoot "tessdata"

if (-not (Test-Path $TesseractExe)) {
    throw "Nu găsesc tesseract.exe: $TesseractExe"
}

$RuntimeTesseractDir = Join-Path $AppDir "runtime\tesseract"
$RuntimeTessdataDir = Join-Path $RuntimeTesseractDir "tessdata"

New-Item -ItemType Directory -Force $RuntimeTesseractDir, $RuntimeTessdataDir | Out-Null

Write-Host "Copiez fișiere Tesseract din: $TesseractRoot"

Get-ChildItem $TesseractRoot -File -Force |
    Where-Object {
        $_.Name -match '\.(exe|dll)$'
    } |
    Copy-Item -Destination $RuntimeTesseractDir -Force

$TessdataCandidates = @()

if ($TessdataSource) {
    if ([System.IO.Path]::IsPathRooted($TessdataSource)) {
        $ResolvedTessdataSource = [System.IO.Path]::GetFullPath($TessdataSource)
    }
    else {
        $ResolvedTessdataSource = [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot $TessdataSource))
    }

    $TessdataCandidates += $ResolvedTessdataSource
}

$TessdataCandidates += (Join-Path $ProjectRoot ".tessdata")
$TessdataCandidates += $InstalledTessdataDir

$TessdataCandidates = $TessdataCandidates |
    Where-Object { $_ -and (Test-Path $_) } |
    Select-Object -Unique

Write-Host "Surse tessdata:"
$TessdataCandidates | ForEach-Object { Write-Host " - $_" }

foreach ($lang in $TessLanguages) {
    $fileName = "$lang.traineddata"
    $sourceFile = $null

    foreach ($candidateDir in $TessdataCandidates) {
        $candidateFile = Join-Path $candidateDir $fileName
        if (Test-Path $candidateFile) {
            $sourceFile = $candidateFile
            break
        }
    }

    if (-not $sourceFile) {
        throw "Lipsește $fileName. Surse verificate: $($TessdataCandidates -join '; ')"
    }

    Write-Host "Copiez OCR lang $lang din $sourceFile"
    Copy-Item $sourceFile -Destination (Join-Path $RuntimeTessdataDir $fileName) -Force
}

$env:TESSDATA_PREFIX = $RuntimeTesseractDir

Write-Host "=== Verific Tesseract runtime copiat ==="
& (Join-Path $RuntimeTesseractDir "tesseract.exe") --version | Select-Object -First 1 | Out-Host
& (Join-Path $RuntimeTesseractDir "tesseract.exe") --list-langs | Out-Host

$expectedLangFiles = foreach ($lang in $TessLanguages) {
    Join-Path $RuntimeTessdataDir "$lang.traineddata"
}

foreach ($expectedLangFile in $expectedLangFiles) {
    if (-not (Test-Path $expectedLangFile)) {
        throw "Lipsește în runtime: $expectedLangFile"
    }
}
Write-Host "=== Cleanup final înainte de ZIP ==="

$FinalRemoveDirs = @(
    (Join-Path $AppDir ".tessdata"),
    (Join-Path $AppDir "audit"),
    (Join-Path $AppDir ".release-cache")
)

foreach ($dir in $FinalRemoveDirs) {
    if (Test-Path $dir) {
        Write-Host "Remove before ZIP: $dir"
        Remove-Item $dir -Recurse -Force -ErrorAction Stop
    }
}

$DataDir = Join-Path $AppDir "data"
if (Test-Path $DataDir) {
    Write-Host "Reset data dir before ZIP: $DataDir"
    Remove-Item $DataDir -Recurse -Force -ErrorAction Stop
}

$RuntimeDataDirs = @(
    (Join-Path $AppDir "data"),
    (Join-Path $AppDir "data\input"),
    (Join-Path $AppDir "data\output"),
    (Join-Path $AppDir "data\trash"),
    (Join-Path $AppDir "logs"),
    (Join-Path $AppDir "runtime")
)

foreach ($dir in $RuntimeDataDirs) {
    New-Item -ItemType Directory -Force $dir | Out-Null
}

$ForbiddenPaths = @(
    (Join-Path $AppDir ".tessdata"),
    (Join-Path $AppDir "audit"),
    (Join-Path $AppDir ".release-cache")
)

foreach ($forbidden in $ForbiddenPaths) {
    if (Test-Path $forbidden) {
        throw "Forbidden path still exists before ZIP: $forbidden"
    }
}

$PopulatedDataFiles = @(Get-ChildItem (Join-Path $AppDir "data") -Recurse -File -Force -ErrorAction SilentlyContinue)
if ($PopulatedDataFiles.Count -gt 0) {
    Write-Host "Data files found before ZIP:"
    $PopulatedDataFiles | Select-Object FullName, Length | Format-Table -AutoSize
    throw "Data directory must be empty before ZIP."
}

Write-Host "OK: staging curat înainte de ZIP."
Compress-Archive -Path (Join-Path $StageDir "*") -DestinationPath $ZipPath -Force

$Sha256 = (Get-FileHash $ZipPath -Algorithm SHA256).Hash
$ZipSizeMb = [Math]::Round((Get-Item $ZipPath).Length / 1MB, 2)
$BuiltAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
$branch = (git -C $ProjectRoot branch --show-current).Trim()
$commit = (git -C $ProjectRoot rev-parse --short HEAD).Trim()

$infoLines = @(
    "Voila $VersionTag",
    "",
    "Built at:",
    "$BuiltAt",
    "",
    "Project root:",
    "$ProjectRoot",
    "",
    "Git branch:",
    "$branch",
    "",
    "Git commit:",
    "$commit",
    "",
    "Runtime model:",
    "Standalone ZIP with embedded Python runtime.",
    "Does not require Python installed in PATH at runtime.",
    "",
    "Still external for v0.1.2:",
    "- Java / LanguageTool",
    "- Tesseract OCR",
    "- PowerShell or pwsh for launcher script",
    "",
    "ZIP:",
    "$ZipPath",
    "",
    "ZIP size MB:",
    "$ZipSizeMb",
    "",
    "SHA256:",
    "$Sha256",
    "",
    "Run:",
    "app\Run-Voila.cmd",
    "or",
    "pwsh -ExecutionPolicy Bypass -File app\Run-Voila.ps1",
    "",
    "Health:",
    "http://127.0.0.1:8765/health"
)

$infoLines | Set-Content -Path $InfoPath -Encoding UTF8

Write-Host ""
Write-Host "=== BUILD OK ==="
Write-Host "ZIP:     $ZipPath"
Write-Host "INFO:    $InfoPath"
Write-Host "SIZE MB: $ZipSizeMb"
Write-Host "SHA256:  $Sha256"











