<#
.SYNOPSIS
Creates real Windows package launchers for a Voila package root.

.DESCRIPTION
Writes START-VOILA.bat, STOP-VOILA.bat, and package-local helper scripts into
a selected package root. Generated launchers use package-relative paths, write
logs/state files under runtime/, and stop only package-owned processes recorded
in PID files.

This helper does not start Voila, rebuild a package, create a ZIP, publish a
release, or modify source runtime behavior.
#>

[CmdletBinding(SupportsShouldProcess = $true)]
param(
  [Parameter(Mandatory = $true)]
  [string] $PackageRoot,

  [switch] $Force,

  [string] $VoilaPort = "8787",

  [string] $LanguageToolPort = "8081"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-PackageRoot {
  param([Parameter(Mandatory = $true)][string] $Path)

  $resolved = Resolve-Path -Path $Path -ErrorAction SilentlyContinue
  if (-not $resolved) {
    throw "PackageRoot does not exist: $Path"
  }

  if (-not (Test-Path -Path $resolved.Path -PathType Container)) {
    throw "PackageRoot is not a directory: $Path"
  }

  return $resolved.Path
}

function Assert-SafePackageRoot {
  param([Parameter(Mandatory = $true)][string] $Path)

  $repoRoot = (Resolve-Path ".").Path.TrimEnd("\")
  $normalized = $Path.TrimEnd("\")

  $unsafe = @(
    $repoRoot,
    (Join-Path $repoRoot "docs").TrimEnd("\"),
    (Join-Path $repoRoot "scripts").TrimEnd("\")
  )

  foreach ($unsafePath in $unsafe) {
    if ($normalized -eq $unsafePath) {
      throw "PackageRoot must not be repository root, docs/, or scripts/: $Path"
    }
  }
}

function Write-TextFile {
  param(
    [Parameter(Mandatory = $true)][string] $Path,
    [Parameter(Mandatory = $true)][string[]] $Lines
  )

  if ((Test-Path $Path) -and (-not $Force)) {
    throw "File already exists. Use -Force to overwrite: $Path"
  }

  Set-Content -Encoding UTF8 -Path $Path -Value $Lines
}

$resolvedPackageRoot = Resolve-PackageRoot -Path $PackageRoot
Assert-SafePackageRoot -Path $resolvedPackageRoot

$packageScripts = Join-Path $resolvedPackageRoot "scripts"
$runtimeDir = Join-Path $resolvedPackageRoot "runtime"
$stateDir = Join-Path $runtimeDir "state"
$logsDir = Join-Path $runtimeDir "logs"

if ($PSCmdlet.ShouldProcess($resolvedPackageRoot, "Create Windows package launchers")) {
  New-Item -ItemType Directory -Force -Path $packageScripts | Out-Null
  New-Item -ItemType Directory -Force -Path $stateDir | Out-Null
  New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
}

$startBatPath = Join-Path $resolvedPackageRoot "START-VOILA.bat"
$stopBatPath = Join-Path $resolvedPackageRoot "STOP-VOILA.bat"
$startPsPath = Join-Path $packageScripts "start-voila.ps1"
$stopPsPath = Join-Path $packageScripts "stop-voila.ps1"
$healthPsPath = Join-Path $packageScripts "check-voila-health.ps1"

$startBat = @(
  "@echo off",
  "setlocal",
  "set SCRIPT_DIR=%~dp0",
  "powershell -NoProfile -ExecutionPolicy Bypass -File ""%SCRIPT_DIR%scripts\start-voila.ps1""",
  "exit /b %ERRORLEVEL%"
)

$stopBat = @(
  "@echo off",
  "setlocal",
  "set SCRIPT_DIR=%~dp0",
  "powershell -NoProfile -ExecutionPolicy Bypass -File ""%SCRIPT_DIR%scripts\stop-voila.ps1""",
  "exit /b %ERRORLEVEL%"
)

$startPs = @(
  'Set-StrictMode -Version Latest',
  '$ErrorActionPreference = "Stop"',
  '',
  '$PackageRoot = Split-Path -Parent $PSScriptRoot',
  '$RuntimeRoot = Join-Path $PackageRoot "runtime"',
  '$StateDir = Join-Path $RuntimeRoot "state"',
  '$LogsDir = Join-Path $RuntimeRoot "logs"',
  '',
  '$VoilaPort = __VOILA_PORT__',
  '$LanguageToolPort = __LANGUAGETOOL_PORT__',
  '',
  'New-Item -ItemType Directory -Force -Path $StateDir | Out-Null',
  'New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null',
  '',
  '$startLog = Join-Path $LogsDir "start-voila.log"',
  '"=== START VOILA $(Get-Date -Format o) ===" | Add-Content -Encoding UTF8 $startLog',
  '"PackageRoot: $PackageRoot" | Add-Content -Encoding UTF8 $startLog',
  '',
  'function Test-PortInUse {',
  '  param([int] $Port)',
  '  $conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue',
  '  return [bool]$conn',
  '}',
  '',
  'function Find-FirstExistingFile {',
  '  param([string[]] $Candidates)',
  '  foreach ($candidate in $Candidates) {',
  '    $full = Join-Path $PackageRoot $candidate',
  '    if (Test-Path $full -PathType Leaf) { return $full }',
  '  }',
  '  return $null',
  '}',
  '',
  'function Start-PackageProcess {',
  '  param(',
  '    [Parameter(Mandatory = $true)][string] $Name,',
  '    [Parameter(Mandatory = $true)][string] $FilePath,',
  '    [Parameter(Mandatory = $true)][string] $Arguments,',
  '    [Parameter(Mandatory = $true)][string] $WorkingDirectory,',
  '    [Parameter(Mandatory = $true)][string] $PidFile,',
  '    [Parameter(Mandatory = $true)][string] $StdoutLog,',
  '    [Parameter(Mandatory = $true)][string] $StderrLog',
  '  )',
  '  "Starting $Name" | Add-Content -Encoding UTF8 $startLog',
  '  $process = Start-Process -FilePath $FilePath -ArgumentList $Arguments -WorkingDirectory $WorkingDirectory -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog -WindowStyle Hidden -PassThru',
  '  Set-Content -Encoding UTF8 -Path $PidFile -Value $process.Id',
  '  "Started $Name with PID $($process.Id)" | Add-Content -Encoding UTF8 $startLog',
  '}',
  '',
  'if (Test-PortInUse -Port $VoilaPort) {',
  '  Write-Host "Voila port $VoilaPort is already in use. Stop existing service first."',
  '  exit 3',
  '}',
  '',
  '$javaExe = Find-FirstExistingFile @("runtime\java\bin\java.exe", "java\bin\java.exe")',
  '$languageToolJar = Find-FirstExistingFile @("runtime\languagetool\languagetool-server.jar", "languagetool\languagetool-server.jar")',
  '',
  'if ($javaExe -and $languageToolJar -and (-not (Test-PortInUse -Port $LanguageToolPort))) {',
  '  $ltWorkDir = Split-Path -Parent $languageToolJar',
  '  Start-PackageProcess -Name "LanguageTool" -FilePath $javaExe -Arguments "-cp ""$languageToolJar"" org.languagetool.server.HTTPServer --port $LanguageToolPort --allow-origin ""*""" -WorkingDirectory $ltWorkDir -PidFile (Join-Path $StateDir "languagetool.pid") -StdoutLog (Join-Path $LogsDir "languagetool.out.log") -StderrLog (Join-Path $LogsDir "languagetool.err.log")',
  '}',
  '',
  '$pythonExe = Find-FirstExistingFile @("runtime\python\python.exe", "python\python.exe", ".venv\Scripts\python.exe")',
  'if (-not $pythonExe) {',
  '  $pythonCommand = Get-Command python -ErrorAction SilentlyContinue',
  '  if ($pythonCommand) { $pythonExe = $pythonCommand.Source }',
  '}',
  '',
  '$apiEntry = Find-FirstExistingFile @("app\api\main.py", "api\main.py", "backend\main.py", "service\main.py", "main.py")',
  '',
  'if (-not $pythonExe) {',
  '  Write-Host "Python runtime not found in package and no global python command available."',
  '  exit 2',
  '}',
  '',
  'if (-not $apiEntry) {',
  '  Write-Host "Voila API entrypoint not found. Expected one of app\api\main.py, api\main.py, backend\main.py, service\main.py, main.py."',
  '  exit 2',
  '}',
  '',
  '$apiWorkDir = Split-Path -Parent $apiEntry',
  'Start-PackageProcess -Name "Voila API" -FilePath $pythonExe -Arguments "-m uvicorn main:app --host 127.0.0.1 --port $VoilaPort" -WorkingDirectory $apiWorkDir -PidFile (Join-Path $StateDir "voila-api.pid") -StdoutLog (Join-Path $LogsDir "voila-api.out.log") -StderrLog (Join-Path $LogsDir "voila-api.err.log")',
  '',
  '$healthScript = Join-Path $PSScriptRoot "check-voila-health.ps1"',
  '& powershell -NoProfile -ExecutionPolicy Bypass -File $healthScript -Port $VoilaPort -TimeoutSeconds 60',
  '$healthExit = $LASTEXITCODE',
  'if ($healthExit -ne 0) {',
  '  Write-Host "Voila failed health check. See runtime\logs."',
  '  exit 4',
  '}',
  '',
  'Write-Host "Voila started successfully."',
  'Write-Host "Open: http://127.0.0.1:$VoilaPort"',
  'exit 0'
)

$startPs = $startPs | ForEach-Object {
  $_.Replace("__VOILA_PORT__", $VoilaPort).Replace("__LANGUAGETOOL_PORT__", $LanguageToolPort)
}

$stopPs = @(
  'Set-StrictMode -Version Latest',
  '$ErrorActionPreference = "Stop"',
  '',
  '$PackageRoot = Split-Path -Parent $PSScriptRoot',
  '$RuntimeRoot = Join-Path $PackageRoot "runtime"',
  '$StateDir = Join-Path $RuntimeRoot "state"',
  '$LogsDir = Join-Path $RuntimeRoot "logs"',
  '',
  'New-Item -ItemType Directory -Force -Path $StateDir | Out-Null',
  'New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null',
  '',
  '$stopLog = Join-Path $LogsDir "stop-voila.log"',
  '"=== STOP VOILA $(Get-Date -Format o) ===" | Add-Content -Encoding UTF8 $stopLog',
  '"PackageRoot: $PackageRoot" | Add-Content -Encoding UTF8 $stopLog',
  '',
  'function Stop-PidFileProcess {',
  '  param(',
  '    [Parameter(Mandatory = $true)][string] $Name,',
  '    [Parameter(Mandatory = $true)][string] $PidFile',
  '  )',
  '  if (-not (Test-Path $PidFile -PathType Leaf)) {',
  '    "$Name PID file not found; treating as already stopped." | Add-Content -Encoding UTF8 $stopLog',
  '    return',
  '  }',
  '  $pidText = (Get-Content $PidFile -Raw).Trim()',
  '  if (-not $pidText) {',
  '    "$Name PID file empty; removing stale PID file." | Add-Content -Encoding UTF8 $stopLog',
  '    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue',
  '    return',
  '  }',
  '  $processId = [int]$pidText',
  '  $process = Get-Process -Id $processId -ErrorAction SilentlyContinue',
  '  if (-not $process) {',
  '    "$Name process $processId not found; removing stale PID file." | Add-Content -Encoding UTF8 $stopLog',
  '    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue',
  '    return',
  '  }',
  '  "Stopping $Name PID $processId ($($process.ProcessName))" | Add-Content -Encoding UTF8 $stopLog',
  '  Stop-Process -Id $processId -Force -ErrorAction Stop',
  '  Remove-Item $PidFile -Force -ErrorAction SilentlyContinue',
  '}',
  '',
  'Stop-PidFileProcess -Name "Voila API" -PidFile (Join-Path $StateDir "voila-api.pid")',
  'Stop-PidFileProcess -Name "LanguageTool" -PidFile (Join-Path $StateDir "languagetool.pid")',
  '',
  'Write-Host "Voila package-owned processes stopped or already stopped."',
  'exit 0'
)

$healthPs = @(
  'param(',
  '  [int] $Port = 8787,',
  '  [int] $TimeoutSeconds = 60',
  ')',
  '',
  'Set-StrictMode -Version Latest',
  '$ErrorActionPreference = "Stop"',
  '',
  '$deadline = (Get-Date).AddSeconds($TimeoutSeconds)',
  '$urls = @("http://127.0.0.1:$Port/health", "http://127.0.0.1:$Port")',
  '',
  'while ((Get-Date) -lt $deadline) {',
  '  foreach ($url in $urls) {',
  '    try {',
  '      $response = Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 3',
  '      if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {',
  '        Write-Host "Health check passed: $url status $($response.StatusCode)"',
  '        exit 0',
  '      }',
  '    } catch {',
  '      Start-Sleep -Seconds 1',
  '    }',
  '  }',
  '}',
  '',
  'Write-Host "Health check timed out on port $Port."',
  'exit 4'
)

if ($PSCmdlet.ShouldProcess($resolvedPackageRoot, "Write launcher files")) {
  Write-TextFile -Path $startBatPath -Lines $startBat
  Write-TextFile -Path $stopBatPath -Lines $stopBat
  Write-TextFile -Path $startPsPath -Lines $startPs
  Write-TextFile -Path $stopPsPath -Lines $stopPs
  Write-TextFile -Path $healthPsPath -Lines $healthPs
}

Write-Host "Windows package launchers created:"
Get-Item $startBatPath, $stopBatPath, $startPsPath, $stopPsPath, $healthPsPath |
  Select-Object FullName, Length
