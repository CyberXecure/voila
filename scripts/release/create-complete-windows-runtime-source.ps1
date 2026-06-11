# Voila Complete Windows Runtime Source Helper
# Creates a complete Windows runtime source folder for a future ZIP package build.
# Scope: release/package helper only. Does not build ZIP, does not run START/STOP, does not publish.

[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string] $RuntimeSourceRoot,

  [ValidateSet("PackageVenv", "EmbeddedPython", "GlobalPython")]
  [string] $PythonStrategy = "PackageVenv",

  [switch] $IncludeCropEditor,

  [ValidateSet("Bundled", "Deferred")]
  [string] $LanguageToolStrategy = "Deferred",

  [ValidateSet("Bundled", "Deferred")]
  [string] $OcrStrategy = "Deferred",

  [switch] $Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-FullPath {
  param([Parameter(Mandatory = $true)][string] $Path)

  $expanded = [Environment]::ExpandEnvironmentVariables($Path)
  return [System.IO.Path]::GetFullPath($expanded)
}

function Assert-SafeRuntimeSourceRoot {
  param(
    [Parameter(Mandatory = $true)][string] $TargetRoot,
    [Parameter(Mandatory = $true)][string] $RepoRoot
  )

  $target = Resolve-FullPath $TargetRoot
  $repo = Resolve-FullPath $RepoRoot

  $unsafeRoots = @(
    $repo,
    (Join-Path $repo "docs"),
    (Join-Path $repo "scripts"),
    (Join-Path $repo "services"),
    (Join-Path $repo ".git")
  ) | ForEach-Object { Resolve-FullPath $_ }

  foreach ($unsafe in $unsafeRoots) {
    if ($target.TrimEnd('\') -ieq $unsafe.TrimEnd('\')) {
      throw "RuntimeSourceRoot is unsafe: $target"
    }
  }

  if ($target.StartsWith((Join-Path $repo ".git"), [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "RuntimeSourceRoot must not be inside .git: $target"
  }

  if ($target.StartsWith((Join-Path $repo "docs"), [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "RuntimeSourceRoot must not be inside docs/: $target"
  }

  if ($target.StartsWith((Join-Path $repo "scripts"), [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "RuntimeSourceRoot must not be inside scripts/: $target"
  }

  if ($target.StartsWith((Join-Path $repo "services"), [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "RuntimeSourceRoot must not be inside services/: $target"
  }
}

function Ensure-CleanDirectory {
  param(
    [Parameter(Mandatory = $true)][string] $Path,
    [switch] $Force
  )

  if (Test-Path $Path) {
    if (-not $Force) {
      throw "Target already exists. Use -Force to replace: $Path"
    }

    Remove-Item $Path -Recurse -Force
  }

  New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Copy-FilteredTree {
  param(
    [Parameter(Mandatory = $true)][string] $Source,
    [Parameter(Mandatory = $true)][string] $Destination,
    [string[]] $AllowedExtensions = @()
  )

  if (-not (Test-Path $Source -PathType Container)) {
    throw "Source directory not found: $Source"
  }

  New-Item -ItemType Directory -Force -Path $Destination | Out-Null

  $sourceFull = Resolve-FullPath $Source
  $files = Get-ChildItem $sourceFull -Recurse -File -Force | Where-Object {
    $_.FullName -notmatch "\\__pycache__\\" -and
    $_.FullName -notmatch "\\\.pytest_cache\\" -and
    $_.FullName -notmatch "\\\.mypy_cache\\" -and
    $_.FullName -notmatch "\\\.ruff_cache\\" -and
    $_.Extension -notin @(".pyc", ".pyo")
  }

  if ($AllowedExtensions.Count -gt 0) {
    $files = $files | Where-Object { $AllowedExtensions -contains $_.Extension.ToLowerInvariant() -or $_.Name -eq "requirements.txt" }
  }

  foreach ($file in $files) {
    $relative = $file.FullName.Substring($sourceFull.Length).TrimStart('\')
    $target = Join-Path $Destination $relative
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
    Copy-Item $file.FullName $target -Force
  }
}

function Write-TextFile {
  param(
    [Parameter(Mandatory = $true)][string] $Path,
    [Parameter(Mandatory = $true)][AllowEmptyString()][string[]] $Lines
  )

  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Path) | Out-Null
  Set-Content -Encoding UTF8 -Path $Path -Value $Lines
}

function Write-Launchers {
  param(
    [Parameter(Mandatory = $true)][string] $PackageRoot,
    [string] $VoilaHost = "127.0.0.1",
    [string] $VoilaPort = "8787"
  )

  $scriptsDir = Join-Path $PackageRoot "scripts"
  $runtimeDir = Join-Path $PackageRoot "runtime"
  $stateDir = Join-Path $runtimeDir "state"
  $logsDir = Join-Path $runtimeDir "logs"

  New-Item -ItemType Directory -Force -Path $scriptsDir, $stateDir, $logsDir | Out-Null

  Write-TextFile -Path (Join-Path $PackageRoot "START-VOILA.bat") -Lines @(
    "@echo off",
    "set PACKAGE_ROOT=%~dp0",
    "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""%PACKAGE_ROOT%scripts\start-voila.ps1""",
    "exit /b %ERRORLEVEL%"
  )

  Write-TextFile -Path (Join-Path $PackageRoot "STOP-VOILA.bat") -Lines @(
    "@echo off",
    "set PACKAGE_ROOT=%~dp0",
    "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""%PACKAGE_ROOT%scripts\stop-voila.ps1""",
    "exit /b %ERRORLEVEL%"
  )

  Write-TextFile -Path (Join-Path $scriptsDir "start-voila.ps1") -Lines @(
    'Set-StrictMode -Version Latest',
    '$ErrorActionPreference = "Stop"',
    '',
    '$PackageRoot = Split-Path -Parent $PSScriptRoot',
    '$StateDir = Join-Path $PackageRoot "runtime\state"',
    '$LogsDir = Join-Path $PackageRoot "runtime\logs"',
    '$ApiDir = Join-Path $PackageRoot "services\api"',
    '$PythonExe = Join-Path $PackageRoot ".venv\Scripts\python.exe"',
    '',
    'New-Item -ItemType Directory -Force -Path $StateDir, $LogsDir | Out-Null',
    '',
    'if (-not (Test-Path $PythonExe -PathType Leaf)) {',
    '  Write-Host "Package-local Python not found: $PythonExe"',
    '  exit 2',
    '}',
    '',
    'if (-not (Test-Path (Join-Path $ApiDir "web_app.py") -PathType Leaf)) {',
    '  Write-Host "Voila API entrypoint not found: services\api\web_app.py"',
    '  exit 2',
    '}',
    '',
    '$apiPid = Join-Path $StateDir "voila-api.pid"',
    '$stdoutLog = Join-Path $LogsDir "voila-api.out.log"',
    '$stderrLog = Join-Path $LogsDir "voila-api.err.log"',
    '$startLog = Join-Path $LogsDir "start-voila.log"',
    '',
    '"Starting Voila API at http://127.0.0.1:8787" | Set-Content -Encoding UTF8 $startLog',
    '$args = @("-B", "-m", "uvicorn", "web_app:app", "--app-dir", ".\services\api", "--host", "127.0.0.1", "--port", "8787")',
    '$proc = Start-Process -FilePath $PythonExe -ArgumentList $args -WorkingDirectory $PackageRoot -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog -WindowStyle Minimized -PassThru',
    '$proc.Id | Set-Content -Encoding UTF8 $apiPid',
    'Start-Sleep -Seconds 2',
    '',
    'if ($proc.HasExited) {',
    '  "Voila API exited early with code $($proc.ExitCode)" | Add-Content -Encoding UTF8 $startLog',
    '  if (Test-Path $stderrLog) { Get-Content $stderrLog | Add-Content -Encoding UTF8 $startLog }',
    '  exit 2',
    '}',
    '',
    '"Voila API process started. PID: $($proc.Id)" | Add-Content -Encoding UTF8 $startLog',
    'Write-Host "Voila API started. PID: $($proc.Id)"',
    'Write-Host "Open http://127.0.0.1:8787"',
    'exit 0'
  )

  Write-TextFile -Path (Join-Path $scriptsDir "stop-voila.ps1") -Lines @(
    'Set-StrictMode -Version Latest',
    '$ErrorActionPreference = "Stop"',
    '',
    '$PackageRoot = Split-Path -Parent $PSScriptRoot',
    '$StateDir = Join-Path $PackageRoot "runtime\state"',
    '$LogsDir = Join-Path $PackageRoot "runtime\logs"',
    '$stopLog = Join-Path $LogsDir "stop-voila.log"',
    '',
    'New-Item -ItemType Directory -Force -Path $StateDir, $LogsDir | Out-Null',
    '"Stopping Voila package-owned processes." | Set-Content -Encoding UTF8 $stopLog',
    '',
    'foreach ($pidFileName in @("voila-api.pid", "languagetool.pid")) {',
    '  $pidFile = Join-Path $StateDir $pidFileName',
    '  if (Test-Path $pidFile -PathType Leaf) {',
    '    $pidText = (Get-Content $pidFile -Raw).Trim()',
    '    if ($pidText -match "^\d+$") {',
    '      $proc = Get-Process -Id ([int]$pidText) -ErrorAction SilentlyContinue',
    '      if ($proc) {',
    '        "Stopping PID $pidText from $pidFileName" | Add-Content -Encoding UTF8 $stopLog',
    '        Stop-Process -Id ([int]$pidText) -Force -ErrorAction SilentlyContinue',
    '      } else {',
    '        "PID $pidText from $pidFileName already stopped." | Add-Content -Encoding UTF8 $stopLog',
    '      }',
    '    }',
    '    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue',
    '  }',
    '}',
    '',
    'Write-Host "Voila package-owned processes stopped or already stopped."',
    'exit 0'
  )

  Write-TextFile -Path (Join-Path $scriptsDir "check-voila-health.ps1") -Lines @(
    'param(',
    '  [string] $Url = "http://127.0.0.1:8787/health",',
    '  [int] $TimeoutSec = 5',
    ')',
    '',
    'try {',
    '  $response = Invoke-WebRequest $Url -UseBasicParsing -TimeoutSec $TimeoutSec',
    '  Write-Host "Health check OK: $($response.StatusCode)"',
    '  exit 0',
    '} catch {',
    '  Write-Host "Health check failed: $($_.Exception.Message)"',
    '  exit 1',
    '}'
  )
}

function Invoke-ImportValidation {
  param([Parameter(Mandatory = $true)][string] $PackageRoot)

  $pythonExe = Join-Path $PackageRoot ".venv\Scripts\python.exe"
  if (-not (Test-Path $pythonExe -PathType Leaf)) {
    throw "Package-local Python not found: $pythonExe"
  }

  Push-Location $PackageRoot
  try {
    $code = "import sys; sys.path.insert(0, r'.\services\api'); import fastapi, uvicorn, web_app; print('OK')"
    $output = & $pythonExe -B -c $code 2>&1
    $exitCode = $LASTEXITCODE

    if ($exitCode -ne 0 -or (($output -join "`n") -notmatch "OK")) {
      throw "Import validation failed: $($output -join "`n")"
    }
  } finally {
    Pop-Location
  }
}


function Remove-RuntimeSourceCaches {
  param([Parameter(Mandatory = $true)][string] $PackageRoot)

  $cacheDirs = Get-ChildItem $PackageRoot -Recurse -Force -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -in @("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache") } |
    Sort-Object FullName -Descending

  foreach ($dir in $cacheDirs) {
    Remove-Item $dir.FullName -Recurse -Force -ErrorAction SilentlyContinue
  }

  $cacheFiles = Get-ChildItem $PackageRoot -Recurse -Force -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension.ToLowerInvariant() -in @(".pyc", ".pyo") }

  foreach ($file in $cacheFiles) {
    Remove-Item $file.FullName -Force -ErrorAction SilentlyContinue
  }
}
function Assert-NoForbiddenFiles {
  param([Parameter(Mandatory = $true)][string] $PackageRoot)

  $forbiddenFiles = Get-ChildItem $PackageRoot -Recurse -Force -File | Where-Object {
    $_.Name -eq ".env" -or
    $_.Extension.ToLowerInvariant() -in @(".key", ".pfx", ".pyc", ".pyo")
  }

  if ($forbiddenFiles) {
    throw "Forbidden files found: $($forbiddenFiles.FullName -join '; ')"
  }

  $forbiddenDirs = Get-ChildItem $PackageRoot -Recurse -Force -Directory | Where-Object {
    $_.Name -in @(".git", ".github", ".release-cache", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "secrets", "private")
  }

  if ($forbiddenDirs) {
    throw "Forbidden directories found: $($forbiddenDirs.FullName -join '; ')"
  }
}

$repoRoot = Resolve-FullPath (Join-Path $PSScriptRoot "..\..")
$runtimeRootFull = Resolve-FullPath $RuntimeSourceRoot
$packageRoot = Join-Path $runtimeRootFull "voila"

Write-Host "=== VOILA COMPLETE WINDOWS RUNTIME SOURCE ==="
Write-Host "RepoRoot: $repoRoot"
Write-Host "RuntimeSourceRoot: $runtimeRootFull"
Write-Host "PackageRoot: $packageRoot"
Write-Host "PythonStrategy: $PythonStrategy"
Write-Host "LanguageToolStrategy: $LanguageToolStrategy"
Write-Host "OcrStrategy: $OcrStrategy"
Write-Host "IncludeCropEditor: $($IncludeCropEditor.IsPresent)"

Assert-SafeRuntimeSourceRoot -TargetRoot $runtimeRootFull -RepoRoot $repoRoot

$sourceApiDir = Join-Path $repoRoot "services\api"
$sourceWebApp = Join-Path $sourceApiDir "web_app.py"
$sourceRequirements = Join-Path $sourceApiDir "requirements.txt"
$sourceVenv = Join-Path $repoRoot ".venv"
$sourcePython = Join-Path $sourceVenv "Scripts\python.exe"

if (-not (Test-Path $sourceWebApp -PathType Leaf)) {
  throw "Required API entrypoint missing: $sourceWebApp"
}

if (-not (Test-Path $sourceRequirements -PathType Leaf)) {
  Write-Warning "services/api/requirements.txt not found. Continuing because runtime may still be valid."
}

if ($PythonStrategy -eq "PackageVenv" -and -not (Test-Path $sourcePython -PathType Leaf)) {
  throw "PackageVenv selected, but source Python not found: $sourcePython"
}

Ensure-CleanDirectory -Path $packageRoot -Force:$Force

Write-Host ""
Write-Host "=== COPY PACKAGE DOCS ==="

Write-TextFile -Path (Join-Path $packageRoot "README-WINDOWS.txt") -Lines @(
  "Voila Windows Package",
  "",
  "Start:",
  "Run START-VOILA.bat",
  "",
  "Stop:",
  "Run STOP-VOILA.bat",
  "",
  "Local URL:",
  "http://127.0.0.1:8787",
  "",
  "Legal files are copied during ZIP package build. See legal/ folder, EULA, LICENSE, BETA-TERMS, and THIRD-PARTY-NOTICES."
)

Write-TextFile -Path (Join-Path $packageRoot "RELEASE-NOTES.txt") -Lines @(
  "Release type: PublicBeta",
  "Runtime source: complete Windows runtime source candidate",
  "API entrypoint: services/api/web_app.py",
  "Start command: python -m uvicorn web_app:app --app-dir .\services\api --host 127.0.0.1 --port 8787",
  "SHA256: generated later by ZIP build helper"
)

Write-Host ""
Write-Host "=== COPY SERVICES API ==="

$targetApiDir = Join-Path $packageRoot "services\api"
Copy-FilteredTree -Source $sourceApiDir -Destination $targetApiDir -AllowedExtensions @(".py", ".txt", ".md", ".json", ".html", ".css", ".js", ".ico", ".png", ".jpg", ".jpeg", ".svg")

if (-not $IncludeCropEditor) {
  $cropEditorTarget = Join-Path $targetApiDir "crop_editor_app.py"
  if (Test-Path $cropEditorTarget -PathType Leaf) {
    Remove-Item $cropEditorTarget -Force
  }
}

Write-Host ""
Write-Host "=== COPY PYTHON STRATEGY ==="

if ($PythonStrategy -eq "PackageVenv") {
  $targetVenv = Join-Path $packageRoot ".venv"
  Copy-Item $sourceVenv $targetVenv -Recurse -Force
  Remove-RuntimeSourceCaches -PackageRoot $packageRoot
} elseif ($PythonStrategy -eq "EmbeddedPython") {
  throw "EmbeddedPython strategy is planned but not implemented in this helper yet."
} elseif ($PythonStrategy -eq "GlobalPython") {
  Write-Warning "GlobalPython selected; START launchers still expect package-local .venv in this initial helper."
}

Write-Host ""
Write-Host "=== GENERATE ALIGNED LAUNCHERS ==="
Write-Launchers -PackageRoot $packageRoot

Write-Host ""
Write-Host "=== VALIDATE RUNTIME SOURCE ==="

if (-not (Test-Path (Join-Path $packageRoot "services\api\web_app.py") -PathType Leaf)) {
  throw "web_app.py was not copied into runtime source."
}

if ($PythonStrategy -eq "PackageVenv") {
  Invoke-ImportValidation -PackageRoot $packageRoot
  Remove-RuntimeSourceCaches -PackageRoot $packageRoot
}

$startScript = Join-Path $packageRoot "scripts\start-voila.ps1"
$startContent = Get-Content $startScript -Raw
foreach ($required in @("web_app:app", "--app-dir", "services\api", "127.0.0.1", "8787")) {
  if ($startContent -notmatch [regex]::Escape($required)) {
    throw "Launcher alignment validation failed. Missing: $required"
  }
}

Assert-NoForbiddenFiles -PackageRoot $packageRoot

Write-Host ""
Write-Host "=== WRITE RUNTIME SOURCE SUMMARY ==="

$branch = (& git -C $repoRoot branch --show-current 2>$null)
$commit = (& git -C $repoRoot rev-parse --short HEAD 2>$null)
$fileCount = (Get-ChildItem $packageRoot -Recurse -Force -File | Measure-Object).Count

Write-TextFile -Path (Join-Path $packageRoot "RUNTIME-SOURCE-SUMMARY.txt") -Lines @(
  "Voila Complete Windows Runtime Source Summary",
  "",
  "Result: PASS",
  "CreatedAt: $((Get-Date).ToString('o'))",
  "SourceBranch: $branch",
  "SourceCommit: $commit",
  "RuntimeSourceRoot: $runtimeRootFull",
  "PackageRoot: $packageRoot",
  "PythonStrategy: $PythonStrategy",
  "LanguageToolStrategy: $LanguageToolStrategy",
  "OcrStrategy: $OcrStrategy",
  "IncludeCropEditor: $($IncludeCropEditor.IsPresent)",
  "APIEntrypoint: services/api/web_app.py",
  "StartCommand: python -m uvicorn web_app:app --app-dir .\services\api --host 127.0.0.1 --port 8787",
  "CopiedFileCount: $fileCount",
  "",
  "KnownLimitations:",
  "- Legal files are copied later by ZIP package build helper.",
  "- LanguageTool strategy may be Deferred.",
  "- OCR strategy may be Deferred."
)

Write-Host ""
Write-Host "Complete Windows runtime source created."
Write-Host "RuntimeSource: $packageRoot"
Write-Host "Validation: PASS"
