param(
    [switch]$DesktopOnly,
    [switch]$StartMenuOnly
)

$ErrorActionPreference = "Stop"

$AppRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunScript = Join-Path $AppRoot "Run-Voila.ps1"

if (-not (Test-Path $RunScript)) {
    throw "Nu găsesc Run-Voila.ps1 în: $AppRoot"
}

$PowerShellExe = Join-Path $env:WINDIR "System32\WindowsPowerShell\v1.0\powershell.exe"

if (-not (Test-Path $PowerShellExe)) {
    $PowerShellExe = "powershell.exe"
}

$IconCandidates = @(
    (Join-Path $AppRoot "services\api\static\favicon.ico"),
    (Join-Path $AppRoot "favicon.ico")
)

$IconPath = $null

foreach ($candidate in $IconCandidates) {
    if (Test-Path $candidate) {
        $IconPath = $candidate
        break
    }
}

function New-VoilaShortcut {
    param(
        [string]$ShortcutPath
    )

    $ShortcutDir = Split-Path -Parent $ShortcutPath
    New-Item -ItemType Directory -Force $ShortcutDir | Out-Null

    $Shell = New-Object -ComObject WScript.Shell
    $Shortcut = $Shell.CreateShortcut($ShortcutPath)

    $Shortcut.TargetPath = $PowerShellExe
    $Shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$RunScript`""
    $Shortcut.WorkingDirectory = $AppRoot
    $Shortcut.Description = "Voila! standalone runtime"

    if ($IconPath) {
        $Shortcut.IconLocation = $IconPath
    }

    $Shortcut.WindowStyle = 1
    $Shortcut.Save()

    Write-Host "Shortcut creat:"
    Write-Host $ShortcutPath
    Write-Host "Target:"
    Write-Host $Shortcut.TargetPath
    Write-Host "Arguments:"
    Write-Host $Shortcut.Arguments
    Write-Host "Icon:"
    Write-Host $Shortcut.IconLocation
}

$Created = @()

if (-not $StartMenuOnly) {
    $Desktop = [Environment]::GetFolderPath("Desktop")
    $DesktopShortcut = Join-Path $Desktop "Voila!.lnk"
    New-VoilaShortcut -ShortcutPath $DesktopShortcut
    $Created += $DesktopShortcut
}

if (-not $DesktopOnly) {
    $Programs = [Environment]::GetFolderPath("Programs")
    $StartMenuDir = Join-Path $Programs "Voila"
    $StartMenuShortcut = Join-Path $StartMenuDir "Voila!.lnk"
    New-VoilaShortcut -ShortcutPath $StartMenuShortcut
    $Created += $StartMenuShortcut
}

Write-Host ""
Write-Host "OK: shortcut-uri Voila create."
$Created | ForEach-Object { Write-Host " - $_" }
