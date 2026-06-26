param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL EXERCISE BANK DISCOVERY CHECK v0.4.45 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$Tmp = Join-Path $env:TEMP ("voila-local-bank-discovery-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $Tmp | Out-Null

try {
  $CourseDir = Join-Path $Tmp "course-a"
  New-Item -ItemType Directory -Force -Path $CourseDir | Out-Null

  $SampleText = @"
Funcțiile sunt relații matematice între două mulțimi. O funcție este definită prin domeniu, codomeniu și lege de corespondență.
Derivata descrie variația locală a unei funcții. Apoi se poate studia monotonia și se pot identifica punctele critice.
Formula f'(x)=lim h->0 (f(x+h)-f(x))/h este folosită pentru calculul derivatei.
"@

  $GeneratedRaw = python .\services\api\local_pedagogy_engine.py --text $SampleText --output-dir $CourseDir --course-id "v045-smoke" --language ro
  Write-Host $GeneratedRaw

  $DiscoveryRaw = python .\services\api\local_exercise_bank.py --root $Tmp --course-id "v045-smoke" --strict
  Write-Host $DiscoveryRaw

  $Summary = $DiscoveryRaw | ConvertFrom-Json

  $banks_found_ok = ([int]$Summary.banks_found -ge 1)
  $valid_banks_ok = ([int]$Summary.valid_banks -ge 1)
  $selected_bank_ok = ([string]$Summary.selected_bank).Trim().Length -gt 0
  $exercise_count_ok = ([int]$Summary.selected_exercise_count -gt 0)
  $fallback_policy_ok = ([string]$Summary.fallback_policy -match "legacy")
  $candidate_valid_ok = ($Summary.candidates.Count -ge 1 -and $Summary.candidates[0].valid -eq $true)
  $runtime_output_no_cloud_dependency = (($GeneratedRaw + "`n" + $DiscoveryRaw) -notmatch "openai|mathpix|ollama|lm studio")

  Write-Host "banks_found_ok $banks_found_ok"
  Write-Host "valid_banks_ok $valid_banks_ok"
  Write-Host "selected_bank_ok $selected_bank_ok"
  Write-Host "exercise_count_ok $exercise_count_ok"
  Write-Host "fallback_policy_ok $fallback_policy_ok"
  Write-Host "candidate_valid_ok $candidate_valid_ok"
  Write-Host "runtime_output_no_cloud_dependency $runtime_output_no_cloud_dependency"

  if (-not ($banks_found_ok -and $valid_banks_ok -and $selected_bank_ok -and $exercise_count_ok -and $fallback_policy_ok -and $candidate_valid_ok -and $runtime_output_no_cloud_dependency)) {
    throw "LOCAL EXERCISE BANK DISCOVERY CHECK v0.4.45 FAILED"
  }

  Write-Host "LOCAL EXERCISE BANK DISCOVERY CHECK v0.4.45 PASS"
} finally {
  if (Test-Path $Tmp) {
    Remove-Item -Recurse -Force $Tmp
  }
}

