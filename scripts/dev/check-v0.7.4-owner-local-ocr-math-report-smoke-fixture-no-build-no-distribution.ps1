param(
  [switch] $FinalMainCheck
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$V075Check = Join-Path $RepoRoot "scripts\dev\check-v0.7.5-owner-local-ocr-math-report-syntax-and-smoke-fix-no-build-no-distribution.ps1"

if (-not (Test-Path $V075Check)) {
  throw "v0.7.5 repair check is required for repaired v0.7.4 smoke validation"
}

Write-Host "== v0.7.4 smoke validation delegated to repaired v0.7.5 check =="
pwsh -NoProfile -ExecutionPolicy Bypass -File $V075Check -FinalMainCheck:$FinalMainCheck
if ($LASTEXITCODE -ne 0) {
  throw "Delegated v0.7.4/v0.7.5 smoke validation failed"
}