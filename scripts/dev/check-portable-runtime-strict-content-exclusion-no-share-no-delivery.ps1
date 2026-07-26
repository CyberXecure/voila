$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path `
    (Split-Path $PSScriptRoot -Parent) `
    -Parent

$BuilderPath = Join-Path `
    $RepoRoot `
    "scripts\release\build-portable-runtime.ps1"

$RequiredDirectoryExclusions = @(
    ".github"
    "docs"
    "scripts\dev"
    "scripts\release"
    "test"
    "tests"
    "testdata"
    "fixture"
    "fixtures"
)

$RequiredFileExclusions = @(
    ".gitattributes"
    ".gitignore"
)

function Get-ArgumentToken {
    param(
        [AllowEmptyString()]
        [string]$Line
    )

    if ([string]::IsNullOrWhiteSpace($Line)) {
        return ""
    }

    $Token = $Line.Trim()

    while ($Token.EndsWith(",")) {
        $Token = $Token.Substring(
            0,
            $Token.Length - 1
        ).TrimEnd()
    }

    if ($Token.Length -ge 2) {
        if (
            ($Token[0] -eq '"' -and $Token[$Token.Length - 1] -eq '"') `
            -or ($Token[0] -eq "'" -and $Token[$Token.Length - 1] -eq "'")
        ) {
            $Token = $Token.Substring(
                1,
                $Token.Length - 2
            )
        }
    }

    return $Token
}

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

Write-Host "V0_8_92C_BUILD_SCRIPT_PARSE=PASS"

$Lines = [System.IO.File]::ReadAllLines(
    $BuilderPath
)

$Needle = 'Invoke-RobocopyChecked -Source $ProjectRoot -Destination $AppDir -RoboArgs @('

$StartIndexes = @()

for ($Index = 0; $Index -lt $Lines.Count; $Index++) {
    if ($Lines[$Index].IndexOf(
        $Needle,
        [System.StringComparison]::Ordinal
    ) -ge 0) {
        $StartIndexes += $Index
    }
}

if ($StartIndexes.Count -ne 1) {
    throw "Blocul inițial de copiere trebuie să apară exact o dată."
}

$StartIndex = $StartIndexes[0]
$EndIndex = -1

for (
    $Index = $StartIndex + 1;
    $Index -lt $Lines.Count;
    $Index++
) {
    if ($Lines[$Index].Trim() -eq ")") {
        $EndIndex = $Index
        break
    }
}

if ($EndIndex -lt 0) {
    throw "Închiderea blocului inițial de copiere lipsește."
}

$XdIndexes = @()
$XfIndexes = @()

for (
    $Index = $StartIndex + 1;
    $Index -lt $EndIndex;
    $Index++
) {
    $Token = Get-ArgumentToken `
        -Line ([string]$Lines[$Index])

    if ($Token.Equals(
        "/XD",
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        $XdIndexes += $Index
    }

    if ($Token.Equals(
        "/XF",
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        $XfIndexes += $Index
    }
}

if ($XdIndexes.Count -ne 1 -or $XfIndexes.Count -ne 1) {
    throw "Blocul trebuie să conțină exact un /XD și un /XF."
}

$XdIndex = $XdIndexes[0]
$XfIndex = $XfIndexes[0]

if ($XdIndex -ge $XfIndex) {
    throw "/XD trebuie să fie înainte de /XF."
}

foreach ($RequiredExclusion in $RequiredDirectoryExclusions) {
    $Count = 0

    for (
        $Index = $XdIndex + 1;
        $Index -lt $XfIndex;
        $Index++
    ) {
        $Token = Get-ArgumentToken `
            -Line ([string]$Lines[$Index])

        if ($Token.Equals(
            $RequiredExclusion,
            [System.StringComparison]::OrdinalIgnoreCase
        )) {
            $Count++
        }
    }

    if ($Count -ne 1) {
        throw "Excluderea de director $RequiredExclusion trebuie să apară exact o dată."
    }
}

foreach ($RequiredExclusion in $RequiredFileExclusions) {
    $Count = 0

    for (
        $Index = $XfIndex + 1;
        $Index -lt $EndIndex;
        $Index++
    ) {
        $Token = Get-ArgumentToken `
            -Line ([string]$Lines[$Index])

        if ($Token.Equals(
            $RequiredExclusion,
            [System.StringComparison]::OrdinalIgnoreCase
        )) {
            $Count++
        }
    }

    if ($Count -ne 1) {
        throw "Excluderea de fișier $RequiredExclusion trebuie să apară exact o dată."
    }
}

$PlainScriptsCount = 0

for (
    $Index = $XdIndex + 1;
    $Index -lt $XfIndex;
    $Index++
) {
    $Token = Get-ArgumentToken `
        -Line ([string]$Lines[$Index])

    if ($Token.Equals(
        "scripts",
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        $PlainScriptsCount++
    }
}

if ($PlainScriptsCount -ne 0) {
    throw "Directorul scripts complet nu trebuie exclus."
}

Write-Host "V0_8_92C_INITIAL_COPY_DIRECTORY_EXCLUSIONS=PASS"
Write-Host "V0_8_92C_INITIAL_COPY_FILE_EXCLUSIONS=PASS"
Write-Host "V0_8_92C_RUNTIME_SCRIPTS_NOT_BROADLY_EXCLUDED=PASS"

$BuilderText = [System.IO.File]::ReadAllText(
    $BuilderPath
)

foreach ($RequiredMarker in @(
    '$sourceShortcutScript = Join-Path $ProjectRoot "scripts\runtime\$shortcutScript"'
    'Copy-Item $sourceShortcutScript $destShortcutScript -Force'
    '=== Clean Python runtime cache before ZIP ==='
    'Python runtime cache cleanup passed.'
    'Compress-Archive'
)) {
    if ($BuilderText.IndexOf(
        $RequiredMarker,
        [System.StringComparison]::Ordinal
    ) -lt 0) {
        throw "Marcaj obligatoriu lipsă: $RequiredMarker"
    }
}

$CleanupMarkerIndex = $BuilderText.IndexOf(
    '=== Clean Python runtime cache before ZIP ===',
    [System.StringComparison]::Ordinal
)

$CompressIndex = $BuilderText.IndexOf(
    'Compress-Archive',
    [System.StringComparison]::Ordinal
)

if (
    $CleanupMarkerIndex -lt 0 `
    -or $CompressIndex -lt 0 `
    -or $CleanupMarkerIndex -ge $CompressIndex
) {
    throw "Ordinea cleanup înainte de ZIP nu este păstrată."
}

Write-Host "V0_8_92C_RUNTIME_SHORTCUT_COPY_PRESERVED=PASS"
Write-Host "V0_8_92C_PYTHON_CACHE_FIX_PRESERVED=PASS"
Write-Host "V0_8_92C_CLEANUP_BEFORE_ZIP_ORDER=PASS"
Write-Host "V0_8_92C_POLICY_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY=PASS"
Write-Host "VOILA_V0_8_92C_PORTABLE_RUNTIME_STRICT_CONTENT_EXCLUSION=PASS"
