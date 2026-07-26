[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    $Python = (Get-Command python -ErrorAction Stop).Source
}

$env:PYTHONDONTWRITEBYTECODE = "1"
Set-Location $RepoRoot

& $Python (Join-Path $PSScriptRoot "check-ui-language-consistency-and-silent-runtime-bootstrap-no-share-no-delivery.py")
if ($LASTEXITCODE -ne 0) { throw "V0.8.91 durable validation failed." }

Write-Host "V0_8_91_CHECK_WRAPPER=PASS"
Write-Host "BUILD_EXECUTED=FALSE"
Write-Host "ZIP_CREATED=FALSE"
Write-Host "SHARE_PERFORMED=FALSE"
Write-Host "DELIVERY_PERFORMED=FALSE"
