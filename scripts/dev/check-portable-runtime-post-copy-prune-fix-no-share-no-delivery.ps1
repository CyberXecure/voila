$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path `
    (Split-Path $PSScriptRoot -Parent) `
    -Parent

$BuilderPath = Join-Path `
    $RepoRoot `
    "scripts\release\build-portable-runtime.ps1"

if (-not (Test-Path -LiteralPath $BuilderPath -PathType Leaf)) {
    throw "Builder-ul lipsește."
}

$Tokens = $null
$ParseErrors = $null

[void][System.Management.Automation.Language.Parser]::ParseFile(
    $BuilderPath,
    [ref]$Tokens,
    [ref]$ParseErrors
)

if ($ParseErrors.Count -ne 0) {
    $ParseErrors |
        ForEach-Object {
            Write-Host $_.Message
        }

    throw "Builder-ul nu poate fi parsat."
}

Write-Host "V0_8_92E_BUILD_SCRIPT_PARSE=PASS"

$BuilderText = [System.IO.File]::ReadAllText(
    $BuilderPath
)

function Get-LiteralOccurrenceCount {
    param(
        [Parameter(Mandatory)]
        [string]$Text,

        [Parameter(Mandatory)]
        [string]$Needle
    )

    $Count = 0
    $SearchStart = 0

    while ($SearchStart -lt $Text.Length) {
        $Index = $Text.IndexOf(
            $Needle,
            $SearchStart,
            [System.StringComparison]::Ordinal
        )

        if ($Index -lt 0) {
            break
        }

        $Count++
        $SearchStart = $Index + [math]::Max(
            1,
            $Needle.Length
        )
    }

    return $Count
}

$RequiredSingleMarkers = @(
    '# V0.8.92e: begin fail-closed portable staging prune'
    '=== Prune forbidden non-runtime content from portable staging ==='
    '$ForbiddenPortableStageDirectories = @('
    '(Join-Path $AppDir ".github")'
    '(Join-Path $AppDir ".git")'
    '(Join-Path $AppDir ".venv")'
    '(Join-Path $AppDir "docs")'
    '(Join-Path $AppDir "scripts\dev")'
    '(Join-Path $AppDir "scripts\release")'
    '(Join-Path $AppDir "test")'
    '(Join-Path $AppDir "tests")'
    '(Join-Path $AppDir "testdata")'
    '(Join-Path $AppDir "fixture")'
    '(Join-Path $AppDir "fixtures")'
    '(Join-Path $AppDir ".gitattributes")'
    '(Join-Path $AppDir ".gitignore")'
    '$ForbiddenPortableStagePdfFiles = @('
    '$ForbiddenPortableStageDraftFiles = @('
    'Forbidden non-runtime content remains in portable staging.'
    'Portable staging forbidden-content prune passed.'
    '# V0.8.92e: end fail-closed portable staging prune'
    '=== Clean Python runtime cache before ZIP ==='
    'Python runtime cache cleanup passed.'
)

foreach ($RequiredMarker in $RequiredSingleMarkers) {
    $OccurrenceCount = Get-LiteralOccurrenceCount `
        -Text $BuilderText `
        -Needle $RequiredMarker

    if ($OccurrenceCount -ne 1) {
        throw "Marcajul trebuie să apară exact o dată: $RequiredMarker"
    }
}

foreach ($RequiredPreservedMarker in @(
    '$sourceShortcutScript = Join-Path $ProjectRoot "scripts\runtime\$shortcutScript"'
    'Copy-Item $sourceShortcutScript $destShortcutScript -Force'
    'Compress-Archive'
)) {
    if ($BuilderText.IndexOf(
        $RequiredPreservedMarker,
        [System.StringComparison]::Ordinal
    ) -lt 0) {
        throw "Marcaj păstrat lipsă: $RequiredPreservedMarker"
    }
}

$InitialCopyIndex = $BuilderText.IndexOf(
    'Invoke-RobocopyChecked -Source $ProjectRoot -Destination $AppDir -RoboArgs @(',
    [System.StringComparison]::Ordinal
)

$PruneStartIndex = $BuilderText.IndexOf(
    '# V0.8.92e: begin fail-closed portable staging prune',
    [System.StringComparison]::Ordinal
)

$PruneEndIndex = $BuilderText.IndexOf(
    '# V0.8.92e: end fail-closed portable staging prune',
    [System.StringComparison]::Ordinal
)

$PythonRuntimeIndex = $BuilderText.IndexOf(
    '$PythonRuntimeDir = Join-Path $AppDir "python"',
    [System.StringComparison]::Ordinal
)

$PythonCacheCleanupIndex = $BuilderText.IndexOf(
    '=== Clean Python runtime cache before ZIP ===',
    [System.StringComparison]::Ordinal
)

$CompressArchiveIndex = $BuilderText.IndexOf(
    'Compress-Archive',
    [System.StringComparison]::Ordinal
)

if (
    $InitialCopyIndex -lt 0 `
    -or $PruneStartIndex -lt 0 `
    -or $PruneEndIndex -lt 0 `
    -or $PythonRuntimeIndex -lt 0 `
    -or $PythonCacheCleanupIndex -lt 0 `
    -or $CompressArchiveIndex -lt 0
) {
    throw "Nu pot valida ordinea etapelor builder-ului."
}

if (
    $InitialCopyIndex -ge $PruneStartIndex `
    -or $PruneStartIndex -ge $PruneEndIndex `
    -or $PruneEndIndex -ge $PythonRuntimeIndex `
    -or $PythonRuntimeIndex -ge $PythonCacheCleanupIndex `
    -or $PythonCacheCleanupIndex -ge $CompressArchiveIndex
) {
    throw "Ordinea copy -> prune -> runtime -> cache cleanup -> ZIP este invalidă."
}

Write-Host "V0_8_92E_POST_COPY_PRUNE_MARKERS=PASS"
Write-Host "V0_8_92E_POST_COPY_PRUNE_FAIL_CLOSED_ASSERTION=PASS"
Write-Host "V0_8_92E_PRUNE_BEFORE_RUNTIME_ASSEMBLY=PASS"
Write-Host "V0_8_92E_RUNTIME_SHORTCUT_COPY_PRESERVED=PASS"
Write-Host "V0_8_92E_PYTHON_CACHE_FIX_PRESERVED=PASS"
Write-Host "V0_8_92E_PRUNE_AND_CACHE_BEFORE_ZIP_ORDER=PASS"
Write-Host "V0_8_92E_POLICY_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY=PASS"
Write-Host "VOILA_V0_8_92E_PORTABLE_RUNTIME_POST_COPY_PRUNE_FIX=PASS"
