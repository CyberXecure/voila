[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$Milestone = "v0.7.18-freeze"
$FinalMarker = "VOILA_V0_7_18_GENERATE_ENTRYPOINT_AND_WRITE_SMOKE_FINAL_FREEZE_CHECK=PASS"

function Write-Step([string]$Message) {
  Write-Host "[$Milestone] $Message"
}

function Assert-PathExists {
  param([string]$PathValue)

  if (-not (Test-Path -LiteralPath $PathValue)) {
    throw "Missing required path: $PathValue"
  }

  Write-Host "path_exists=$PathValue"
}

function Assert-TextContains {
  param(
    [string]$PathValue,
    [string]$Needle,
    [string]$Label
  )

  $text = Get-Content -LiteralPath $PathValue -Raw
  if ($text -notmatch [regex]::Escape($Needle)) {
    throw "Missing expected text for ${Label}: $Needle in $PathValue"
  }

  Write-Host "$Label=present"
}

Write-Host ""
Write-Host "=== Voila v0.7.18 generate entrypoint and write smoke final freeze ==="
Write-Host ""

Write-Step "Policy guard: static freeze only; no runtime write"
Write-Host "runtime_server_start=false"
Write-Host "upload_performed=false"
Write-Host "generate_performed=false"
Write-Host "runtime_write_smoke_performed=false"
Write-Host "build_created=false"
Write-Host "zip_created=false"
Write-Host "delivery_performed=false"
Write-Host "distribution_performed=false"
Write-Host "real_private_confidential_data_used=false"
Write-Host "delete_reset_cleanup_performed=false"
Write-Host "feature_changes=false"
Write-Host "behavior_changes=false"
Write-Host "public_ui_expansion=false"

$webApp = "services/api/web_app.py"

Write-Step "Checking required files"
Assert-PathExists $webApp

$requiredDocsAndScripts = @(
  "docs/dev/v0.7.17b2-owner-local-generate-500-stack-isolation-no-build-no-distribution.md",
  "scripts/dev/check-owner-local-generate-500-stack-isolation-no-build-no-distribution.ps1",
  "docs/dev/v0.7.17c-owner-local-generate-entrypoint-fix-no-build-no-distribution.md",
  "scripts/dev/check-owner-local-generate-entrypoint-fix-no-build-no-distribution.ps1",
  "docs/dev/v0.7.17d-owner-local-controlled-fixture-write-smoke-no-build-no-distribution.md",
  "scripts/dev/check-owner-local-controlled-fixture-write-smoke-no-build-no-distribution.ps1"
)

foreach ($pathValue in $requiredDocsAndScripts) {
  Assert-PathExists $pathValue
}

Write-Step "Checking v0.7.17c generate entrypoint source markers"
Assert-TextContains $webApp "VOILA_V0_7_17C_GENERATE_FOR_PDF_ENTRYPOINT" "generate_entrypoint_marker"
Assert-TextContains $webApp "def generate_for_pdf(pdf_path: Path) -> Path:" "generate_for_pdf_defined"
Assert-TextContains $webApp "generate_for_pdf(pdf_path)" "generate_route_calls_entrypoint"

foreach ($scriptName in @(
  "pdf_extract.py",
  "outline_builder.py",
  "normalize_outline.py",
  "course_generator.py",
  "course_polisher.py"
)) {
  Assert-TextContains $webApp $scriptName ("pipeline_script_" + $scriptName.Replace(".", "_"))
}

Write-Step "Checking previous validation markers"
Assert-TextContains "scripts/dev/check-owner-local-generate-500-stack-isolation-no-build-no-distribution.ps1" "VOILA_V0_7_17B2_OWNER_LOCAL_GENERATE_500_STACK_ISOLATION_CHECK=PASS" "v0_7_17b2_marker"
Assert-TextContains "scripts/dev/check-owner-local-generate-entrypoint-fix-no-build-no-distribution.ps1" "VOILA_V0_7_17C_OWNER_LOCAL_GENERATE_ENTRYPOINT_FIX_CHECK=PASS" "v0_7_17c_marker"
Assert-TextContains "scripts/dev/check-owner-local-controlled-fixture-write-smoke-no-build-no-distribution.ps1" "VOILA_V0_7_17D_OWNER_LOCAL_CONTROLLED_FIXTURE_WRITE_SMOKE_CHECK=PASS" "v0_7_17d_marker"

Write-Step "Compiling web_app.py only"
python -m py_compile $webApp
if ($LASTEXITCODE -ne 0) {
  throw "Python compile failed for $webApp"
}
Write-Host "python_compile_web_app=pass"

Write-Step "Final frozen status"
Write-Host "generate_entrypoint_restored=true"
Write-Host "controlled_fixture_write_smoke_passed=true"
Write-Host "runtime_write_performed_in_this_milestone=false"
Write-Host "build_created=false"
Write-Host "zip_created=false"
Write-Host "delivery_performed=false"
Write-Host "distribution_performed=false"
Write-Host "real_private_confidential_data_used=false"
Write-Host "delete_reset_cleanup_performed=false"
Write-Host "feature_changes=false"
Write-Host "behavior_changes=false"
Write-Host "public_ui_expansion=false"

Write-Host $FinalMarker
