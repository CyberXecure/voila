param(
  [string]$Version = "v0.3.2-public-beta-limited-tester-demo",
  [string]$ReleaseRoot = "D:\dev\releases"
)

$ErrorActionPreference = "Stop"

function Write-Step {
  param([string]$Message)
  Write-Host ""
  Write-Host "=== $Message ==="
}

function Write-TextFile {
  param(
    [string]$Path,
    [string[]]$Lines,
    [string]$Encoding = "UTF8"
  )

  Set-Content -Path $Path -Value $Lines -Encoding $Encoding
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$stamp = Get-Date -Format "yyyy-MM-dd_HHmmss"

$packageName = "voila-$Version"
$stageRoot = Join-Path $ReleaseRoot "$packageName-stage-$stamp"
$packageDir = Join-Path $stageRoot $packageName
$zipPath = Join-Path $ReleaseRoot "$packageName.zip"
$shaPath = "$zipPath.sha256"
$notesPath = Join-Path $ReleaseRoot "$packageName-release-notes.md"
$checklistPath = Join-Path $ReleaseRoot "$packageName-final-checklist.md"
$testLogPath = Join-Path $ReleaseRoot "$packageName-test-log.md"

Write-Step "Voila Windows tester package build"
Write-Host "Repo root:    $repoRoot"
Write-Host "Release root: $ReleaseRoot"
Write-Host "Package:      $packageName"
Write-Host "ZIP:          $zipPath"

Write-Step "Preflight checks"

$requiredPaths = @(
  "scripts\dev\start-voila.ps1",
  "scripts\dev\stop-voila.ps1",
  "docs\testers\VOILA-WINDOWS-TESTER-PACKAGE-PLAN.md",
  "docs\testers\VOILA-WINDOWS-TESTER-PACKAGE-CHECKLIST.md",
  "docs\testers\VOILA-TESTER-QUICKSTART.md",
  "docs\testers\VOILA-TESTER-FEEDBACK-QUESTIONS.md",
  "docs\testers\VOILA-TESTER-LIMITATIONS.md"
)

foreach ($rel in $requiredPaths) {
  $path = Join-Path $repoRoot $rel
  if (-not (Test-Path $path)) {
    throw "Required path missing: $rel"
  }
  Write-Host "OK: $rel"
}

$licenseFiles = Get-ChildItem $repoRoot -Force | Where-Object { $_.Name -match '^(LICENSE|LICENCE)(\..*)?$' }
if ($licenseFiles) {
  $licenseFiles | Select-Object Name, FullName
  throw "LICENSE/LICENCE file found. Stop and review commercial/licensing decision."
}
Write-Host "OK: no LICENSE/LICENCE file found."


$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
  throw "Win tester package requires local Python venv: .venv\Scripts\python.exe"
}
Write-Host "OK: .venv Python runtime found."

Write-Step "Prepare staging folder"

New-Item -ItemType Directory -Force -Path $ReleaseRoot | Out-Null
Remove-Item $stageRoot -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $packageDir | Out-Null

$excludeDirs = @(
  ".git",
  ".github",
  ".release-cache",
  "data",
  "venv",
  "env",
  "node_modules",
  ".next",
  "dist",
  "build",
  "__pycache__",
  ".pytest_cache",
  ".mypy_cache",
  ".ruff_cache",
  ".cache",
  ".idea",
  ".vscode"
)

$excludeFilePatterns = @(
  "*.pyc",
  "*.pyo",
  "*.log",
  "*.tmp",
  "*.bak",
  "*.zip",
  "*.7z",
  "*.tar",
  "*.gz",
  ".env",
  ".env.*"
)

Write-Step "Copy repository files"

$items = Get-ChildItem $repoRoot -Force

foreach ($item in $items) {
  if ($excludeDirs -contains $item.Name) {
    Write-Host "Skip dir: $($item.Name)"
    continue
  }

  $skipFile = $false

  if (-not $item.PSIsContainer) {
    foreach ($pattern in $excludeFilePatterns) {
      if ($item.Name -like $pattern) {
        $skipFile = $true
        break
      }
    }
  }

  if ($skipFile) {
    Write-Host "Skip file: $($item.Name)"
    continue
  }

  $dest = Join-Path $packageDir $item.Name
  Copy-Item $item.FullName $dest -Recurse -Force
}


Write-Step "Create clean data folders"

$dataDirs = @(
  "data",
  "data\input",
  "data\output",
  "data\trash",
  "data\trash\pdfs",
  "data\trash\courses"
)

foreach ($relDataDir in $dataDirs) {
  New-Item -ItemType Directory -Force -Path (Join-Path $packageDir $relDataDir) | Out-Null
}

$dataReadmePath = Join-Path $packageDir "data\README.txt"
Write-TextFile -Path $dataReadmePath -Encoding "UTF8" -Lines @(
  "Voila data folder",
  "",
  "This tester package intentionally ships with an empty data folder.",
  "",
  "Use data/input for local test PDFs if needed.",
  "Generated outputs may appear under data/output.",
  "",
  "Do not use confidential, legal, medical, financial, safety-critical or personal documents for early testing."
)

Write-Step "Create tester helper files"

Write-TextFile `
  -Path (Join-Path $packageDir "START-VOILA.bat") `
  -Encoding "ASCII" `
  -Lines @(
    "@echo off",
    "setlocal",
    "cd /d ""%~dp0""",
    "start ""Voila Starter"" powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "".\\scripts\\dev\\start-voila.ps1""",
    "exit /b 0"
  )

Write-TextFile `
  -Path (Join-Path $packageDir "STOP-VOILA.bat") `
  -Encoding "ASCII" `
  -Lines @(
    "@echo off",
    "setlocal",
    "cd /d ""%~dp0""",
    "start ""Voila Stopper"" powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "".\\scripts\\dev\\stop-voila.ps1""",
    "exit /b 0"
  )

Write-TextFile `
  -Path (Join-Path $packageDir "README-TESTERS.txt") `
  -Encoding "UTF8" `
  -Lines @(
    "Voila! Windows Tester Package",
    "",
    "How to test:",
    "",
    "1. Right-click the ZIP and choose Extract All.",
    "2. Open the extracted folder.",
    "3. Double-click START-VOILA.vbs for silent background start. If that does not work, use START-VOILA.bat.",
    "4. Wait for the browser to open.",
    "5. If the browser does not open, go to:",
    "   http://127.0.0.1:8787",
    "6. Test with a small non-confidential PDF first (maximum 5 pages per PDF).",
    "7. Review generated outputs:",
    "   - course outline",
    "   - normalized outline",
    "   - cleaned course content",
    "   - glossary",
    "   - quiz",
    "   - flashcards",
    "   - OCR review",
    "8. When finished, double-click STOP-VOILA.vbs for silent background stop. If that does not work, use STOP-VOILA.bat.",
    "9. If something fails, use START-VOILA-DEBUG.bat or STOP-VOILA-DEBUG.bat to see troubleshooting output.`n10. Send feedback using docs/testers/VOILA-TESTER-FEEDBACK-QUESTIONS.md.",
    "",
    "Important limitations:",
    "",
    "- This is a public beta limited tester demo.",
    "- This demo is limited to 5 pages per PDF.",
    "- Generated content must be reviewed by a human.",
    "- Do not test with confidential, legal, medical, financial, safety-critical or personal documents.",
    "- Output quality depends on PDF quality and structure.",
    "- Scanned PDFs, complex tables, forms and image-heavy files may need manual review.",
    "- No LICENSE file is included because the licensing/commercial model is still under evaluation."
  )


Write-TextFile `
  -Path (Join-Path $packageDir "START-VOILA-DEBUG.bat") `
  -Encoding "ASCII" `
  -Lines @(
    "@echo off",
    "setlocal",
    "cd /d ""%~dp0""",
    "echo.",
    "echo Starting Voila! tester package in DEBUG mode...",
    "echo.",
    "powershell -NoProfile -ExecutionPolicy Bypass -File "".\\scripts\\dev\\start-voila.ps1""",
    "echo.",
    "echo If the browser did not open automatically, open:",
    "echo http://127.0.0.1:8787",
    "echo.",
    "pause"
  )

Write-TextFile `
  -Path (Join-Path $packageDir "STOP-VOILA-DEBUG.bat") `
  -Encoding "ASCII" `
  -Lines @(
    "@echo off",
    "setlocal",
    "cd /d ""%~dp0""",
    "echo.",
    "echo Stopping Voila! tester package in DEBUG mode...",
    "echo.",
    "powershell -NoProfile -ExecutionPolicy Bypass -File "".\\scripts\\dev\\stop-voila.ps1""",
    "echo.",
    "echo Voila stop command completed.",
    "echo.",
    "pause"
  )


Write-TextFile `
  -Path (Join-Path $packageDir "START-VOILA.vbs") `
  -Encoding "ASCII" `
  -Lines @(
    'Set shell = CreateObject("WScript.Shell")',
    'Set fso = CreateObject("Scripting.FileSystemObject")',
    'base = fso.GetParentFolderName(WScript.ScriptFullName)',
    'cmd = "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File " & Chr(34) & base & "\scripts\dev\start-voila.ps1" & Chr(34) & " -Silent"',
    'shell.Run cmd, 0, False'
  )

Write-TextFile `
  -Path (Join-Path $packageDir "STOP-VOILA.vbs") `
  -Encoding "ASCII" `
  -Lines @(
    'Set shell = CreateObject("WScript.Shell")',
    'Set fso = CreateObject("Scripting.FileSystemObject")',
    'base = fso.GetParentFolderName(WScript.ScriptFullName)',
    'cmd = "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File " & Chr(34) & base & "\scripts\dev\stop-voila.ps1" & Chr(34)',
    'shell.Run cmd, 0, False'
  )

Write-Step "Create release notes/checklist/test log"

Write-TextFile `
  -Path $notesPath `
  -Encoding "UTF8" `
  -Lines @(
    "# Voila! $Version Release Notes",
    "",
    "This is a local tester-friendly Windows package build.",
    "",
    "## Purpose",
    "",
    "Make Voila! easier to test for non-technical users.",
    "",
    "Target experience:",
    "",
    "download -> extract -> double-click START-VOILA.bat -> browser opens -> test PDF -> feedback",
    "",
    "## Included",
    "",
    "- START-VOILA.bat",
    "- STOP-VOILA.bat",
    "- README-TESTERS.txt",
    "- tester docs under docs/testers",
    "- existing Voila app/source/runtime files from the repository",
    "- existing language-pack files from the repository",
    "",
    "## Scope",
    "",
    "- no LICENSE added",
    "- no installer",
    "- no payment flow",
    "- no cloud accounts",
    "- no forced de/es/it/pt language packs",
    "- no GitHub release upload in this build step",
    "- no Git tag in this build step",
    "- existing v0.3.0 Language Pack RC1 remains unchanged",
    "",
    "## Notes",
    "",
    "This package is intended for early tester feedback, not production use."
  )

Write-TextFile `
  -Path $checklistPath `
  -Encoding "UTF8" `
  -Lines @(
    "# Voila! $Version Final Checklist",
    "",
    "## Build checklist",
    "",
    "- [ ] Package folder created",
    "- [ ] START-VOILA.bat included",
    "- [ ] STOP-VOILA.bat included",
    "- [ ] README-TESTERS.txt included",
    "- [ ] tester docs included",
    "- [ ] ZIP created",
    "- [ ] SHA256 generated",
    "- [ ] no LICENSE file included",
    "- [ ] no Git tag created",
    "- [ ] no GitHub release uploaded",
    "- [ ] package extracted successfully",
    "- [ ] app start tested locally",
    "- [ ] app stop tested locally",
    "- [ ] browser reachable at http://127.0.0.1:8787",
    "- [ ] small PDF test completed",
    "- [ ] feedback questions reviewed",
    "",
    "## Safety checklist",
    "",
    "- [ ] Tester package is marked public beta",
    "- [ ] Generated content requires human review",
    "- [ ] Sensitive documents are discouraged",
    "- [ ] v0.3.0 RC1 remains unchanged"
  )

Write-TextFile `
  -Path $testLogPath `
  -Encoding "UTF8" `
  -Lines @(
    "# Voila! $Version Test Log",
    "",
    "Build time: $stamp",
    "Repo root: $repoRoot",
    "Package name: $packageName",
    "ZIP path: $zipPath",
    "",
    "## Automated checks",
    "",
    "- Required tester docs: PASS",
    "- Required start/stop scripts: PASS",
    "- No LICENSE/LICENCE file at repo root: PASS",
    "- Staging folder created: PASS",
    "- Tester helper files created: PASS",
    "",
    "## Manual checks still required",
    "",
    "- Extract ZIP",
    "- Run START-VOILA.bat",
    "- Confirm browser/app opens",
    "- Test a small PDF",
    "- Run STOP-VOILA.bat",
    "- Confirm final git status is clean"
  )

Write-Step "Create ZIP"

Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
Remove-Item $shaPath -Force -ErrorAction SilentlyContinue

Compress-Archive -Path $packageDir -DestinationPath $zipPath -Force

Write-Step "Generate SHA256"

$sha = (Get-FileHash $zipPath -Algorithm SHA256).Hash
$shaLine = "$sha  $(Split-Path $zipPath -Leaf)"
$shaLine | Set-Content -Path $shaPath -Encoding ASCII

Write-Host "SHA256: $sha"

Write-Step "Inspect ZIP"

$zipInfo = Get-Item $zipPath
Write-Host "ZIP:  $($zipInfo.FullName)"
Write-Host "Size: $($zipInfo.Length) bytes"
Write-Host "SHA:  $sha"

Write-Step "Release files"

Get-ChildItem $ReleaseRoot -File |
  Where-Object { $_.Name -like "$packageName*" } |
  Select-Object Name, Length, LastWriteTime

Write-Step "Done"

Write-Host "Package directory:"
Write-Host $packageDir

Write-Host ""
Write-Host "ZIP:"
Write-Host $zipPath

Write-Host ""
Write-Host "SHA256:"
Write-Host $sha




