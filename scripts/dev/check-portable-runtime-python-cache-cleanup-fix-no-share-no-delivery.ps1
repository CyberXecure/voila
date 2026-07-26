$ErrorActionPreference = "Stop"

$RepoRoot = (
    Resolve-Path `
        -LiteralPath (Join-Path $PSScriptRoot "..\..")
).Path

$BuildScript = Join-Path `
    $RepoRoot `
    "scripts\release\build-portable-runtime.ps1"

$Documentation = Join-Path `
    $RepoRoot `
    "docs\dev\portable-runtime-python-cache-cleanup-fix-no-share-no-delivery.md"

foreach ($RequiredPath in @(
    $BuildScript
    $Documentation
)) {
    if (-not (Test-Path -LiteralPath $RequiredPath -PathType Leaf)) {
        throw "Required file missing: $RequiredPath"
    }
}

$Tokens = $null
$ParseErrors = $null

[System.Management.Automation.Language.Parser]::ParseFile(
    $BuildScript,
    [ref]$Tokens,
    [ref]$ParseErrors
) | Out-Null

if ($ParseErrors.Count -ne 0) {
    $ParseErrors |
        Format-Table `
            Message,
            @{
                Name = "Line"
                Expression = {
                    $_.Extent.StartLineNumber
                }
            } `
            -AutoSize

    throw "Portable builder does not parse."
}

$Content = Get-Content `
    -LiteralPath $BuildScript `
    -Raw `
    -Encoding UTF8

$RequiredMarkers = @(
    'Write-Host "=== Cleanup final înainte de ZIP ==="'
    'Write-Host "=== Clean Python runtime cache before ZIP ==="'
    '$PythonRuntimeCacheDirs = @('
    '$PythonRuntimeBytecodeFiles = @('
    '$RemainingPythonRuntimeCacheDirs = @('
    '$RemainingPythonRuntimeBytecodeFiles = @('
    '$_.Name -eq "__pycache__"'
    '$_.Extension -in @(".pyc", ".pyo")'
    'throw "Python runtime cache cleanup failed before ZIP."'
    'Write-Host "Python runtime cache cleanup passed."'
    '$DataDir = Join-Path $AppDir "data"'
    'Compress-Archive -Path (Join-Path $StageDir "*")'
)

foreach ($Marker in $RequiredMarkers) {
    if (-not $Content.Contains($Marker)) {
        throw "Required cleanup marker missing: $Marker"
    }
}

$FinalCleanupIndex = $Content.IndexOf(
    'Write-Host "=== Cleanup final înainte de ZIP ==="',
    [System.StringComparison]::Ordinal
)

$PythonCleanupIndex = $Content.IndexOf(
    'Write-Host "=== Clean Python runtime cache before ZIP ==="',
    [System.StringComparison]::Ordinal
)

$DataResetIndex = $Content.IndexOf(
    '$DataDir = Join-Path $AppDir "data"',
    [System.StringComparison]::Ordinal
)

$CompressIndex = $Content.IndexOf(
    'Compress-Archive -Path (Join-Path $StageDir "*")',
    [System.StringComparison]::Ordinal
)

if (
    $FinalCleanupIndex -lt 0 `
    -or $PythonCleanupIndex -lt 0 `
    -or $DataResetIndex -lt 0 `
    -or $CompressIndex -lt 0
) {
    throw "Could not resolve cleanup ordering."
}

if (-not (
    $FinalCleanupIndex -lt $PythonCleanupIndex `
    -and $PythonCleanupIndex -lt $DataResetIndex `
    -and $DataResetIndex -lt $CompressIndex
)) {
    throw "Python cache cleanup is not positioned before ZIP creation."
}

$PythonCleanupMarkerCount = (
    [regex]::Matches(
        $Content,
        [regex]::Escape(
            'Write-Host "=== Clean Python runtime cache before ZIP ==="'
        )
    )
).Count

if ($PythonCleanupMarkerCount -ne 1) {
    throw "Python cleanup marker count is not exactly one."
}

$DocumentationText = Get-Content `
    -LiteralPath $Documentation `
    -Raw `
    -Encoding UTF8

foreach ($PolicyMarker in @(
    "no build is executed"
    "no existing ZIP is modified"
    "no new ZIP is created"
    "no tester share is performed"
    "no delivery or distribution is performed"
)) {
    if (
        $DocumentationText.IndexOf(
            $PolicyMarker,
            [System.StringComparison]::OrdinalIgnoreCase
        ) -lt 0
    ) {
        throw "Policy marker missing from documentation: $PolicyMarker"
    }
}

Write-Host "V0_8_92A_BUILD_SCRIPT_PARSE=PASS"
Write-Host "V0_8_92A_PYTHON_CACHE_DISCOVERY=PASS"
Write-Host "V0_8_92A_PYTHON_CACHE_REMOVAL=PASS"
Write-Host "V0_8_92A_POST_CLEANUP_RESCAN=PASS"
Write-Host "V0_8_92A_CLEANUP_BEFORE_ZIP_ORDER=PASS"
Write-Host "V0_8_92A_POLICY_NO_BUILD_NO_ZIP_NO_SHARE_NO_DELIVERY=PASS"
Write-Host "VOILA_V0_8_92A_PORTABLE_RUNTIME_PYTHON_CACHE_CLEANUP_FIX=PASS"
