param(
    [switch]$DesktopOnly,
    [switch]$StartMenuOnly
)

$ErrorActionPreference = "Stop"

$AppRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetCmd = Join-Path $AppRoot "Run-Voila.cmd"
$TargetPs1 = Join-Path $AppRoot "Run-Voila.ps1"

if (Test-Path $TargetCmd) {
    $TargetPath = $TargetCmd
}
elseif (Test-Path $TargetPs1) {
    $TargetPath = "powershell.exe"
}
else {
    throw "Nu găsesc Run-Voila.cmd sau Run-Voila.ps1 în: $AppRoot"
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

    if ($TargetPath -eq "powershell.exe") {
        $Shortcut.TargetPath = "powershell.exe"
        $Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$TargetPs1`""
    }
    else {
        $Shortcut.TargetPath = $TargetPath
        $Shortcut.Arguments = ""
    }

    $Shortcut.WorkingDirectory = $AppRoot
    $Shortcut.Description = "Voila! local standalone runtime"

    if ($IconPath) {
        $Shortcut.IconLocation = $IconPath
    }

    $Shortcut.Save()

    Write-Host "Shortcut creat:"
    Write-Host $ShortcutPath
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
