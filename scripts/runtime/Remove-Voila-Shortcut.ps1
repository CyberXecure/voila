param(
    [switch]$DesktopOnly,
    [switch]$StartMenuOnly
)

$ErrorActionPreference = "SilentlyContinue"

$Removed = @()

if (-not $StartMenuOnly) {
    $Desktop = [Environment]::GetFolderPath("Desktop")
    $DesktopShortcut = Join-Path $Desktop "Voila!.lnk"

    if (Test-Path $DesktopShortcut) {
        Remove-Item $DesktopShortcut -Force
        $Removed += $DesktopShortcut
    }
}

if (-not $DesktopOnly) {
    $Programs = [Environment]::GetFolderPath("Programs")
    $StartMenuDir = Join-Path $Programs "Voila"
    $StartMenuShortcut = Join-Path $StartMenuDir "Voila!.lnk"

    if (Test-Path $StartMenuShortcut) {
        Remove-Item $StartMenuShortcut -Force
        $Removed += $StartMenuShortcut
    }

    if (Test-Path $StartMenuDir) {
        $remaining = Get-ChildItem $StartMenuDir -Force
        if (-not $remaining) {
            Remove-Item $StartMenuDir -Force
        }
    }
}

if ($Removed.Count -gt 0) {
    Write-Host "Shortcut-uri șterse:"
    $Removed | ForEach-Object { Write-Host " - $_" }
}
else {
    Write-Host "Nu am găsit shortcut-uri Voila de șters."
}

Write-Host "OK: cleanup shortcut finalizat."
