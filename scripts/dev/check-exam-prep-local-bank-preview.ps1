param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== EXAM PREP LOCAL BANK PREVIEW CHECK v0.4.46 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$Tmp = Join-Path $env:TEMP ("voila-exam-prep-local-bank-preview-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $Tmp | Out-Null

try {
  $CourseDir = Join-Path $Tmp "course-a"
  $EmptyDir = Join-Path $Tmp "empty"
  New-Item -ItemType Directory -Force -Path $CourseDir | Out-Null
  New-Item -ItemType Directory -Force -Path $EmptyDir | Out-Null

  $SampleText = @"
Funcțiile sunt relații matematice între două mulțimi. O funcție este definită prin domeniu, codomeniu și lege de corespondență.
Derivata descrie variația locală a unei funcții. Apoi se poate studia monotonia și se pot identifica punctele critice.
Formula f'(x)=lim h->0 (f(x+h)-f(x))/h este folosită pentru calculul derivatei.
"@

  $GeneratedRaw = python .\services\api\local_pedagogy_engine.py --text $SampleText --output-dir $CourseDir --course-id "v046-smoke" --language ro
  if ($LASTEXITCODE -ne 0) { throw "local_pedagogy_engine.py failed" }
  Write-Host $GeneratedRaw

  $PreviewRaw = python .\services\api\exam_prep_local_bank_preview.py --root $Tmp --course-id "v046-smoke" --strict-local
  if ($LASTEXITCODE -ne 0) { throw "exam_prep_local_bank_preview.py strict-local failed" }
  Write-Host $PreviewRaw

  $FallbackRaw = python .\services\api\exam_prep_local_bank_preview.py --root $EmptyDir
  if ($LASTEXITCODE -ne 0) { throw "exam_prep_local_bank_preview.py fallback preview failed" }
  Write-Host $FallbackRaw

  $Preview = $PreviewRaw | ConvertFrom-Json
  $Fallback = $FallbackRaw | ConvertFrom-Json

  $preview_version_ok = ($Preview.preview_version -eq "v0.4.46")
  $mode_ok = ($Preview.mode -eq "non_destructive_preview")
  $local_available_ok = ($Preview.local_bank_available -eq $true)
  $active_source_ok = ($Preview.active_source_preview -eq "local_exercise_bank_preview")
  $selected_count_ok = ([int]$Preview.selected_exercise_count -gt 0)
  $legacy_fallback_ok = ($Preview.legacy_fallback_available -eq $true)
  $no_progress_change_ok = ($Preview.will_modify_progress -eq $false)
  $no_ui_change_ok = ($Preview.will_modify_exam_prep_ui -eq $false)
  $no_replace_legacy_ok = ($Preview.will_replace_legacy_generator -eq $false)
  $no_cloud_ok = ($Preview.requires_cloud_or_api -eq $false)
  $fallback_source_ok = ($Fallback.local_bank_available -eq $false -and $Fallback.active_source_preview -eq "legacy_fallback")

  Write-Host "preview_version_ok $preview_version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "local_available_ok $local_available_ok"
  Write-Host "active_source_ok $active_source_ok"
  Write-Host "selected_count_ok $selected_count_ok"
  Write-Host "legacy_fallback_ok $legacy_fallback_ok"
  Write-Host "no_progress_change_ok $no_progress_change_ok"
  Write-Host "no_ui_change_ok $no_ui_change_ok"
  Write-Host "no_replace_legacy_ok $no_replace_legacy_ok"
  Write-Host "no_cloud_ok $no_cloud_ok"
  Write-Host "fallback_source_ok $fallback_source_ok"

  if (-not ($preview_version_ok -and $mode_ok -and $local_available_ok -and $active_source_ok -and $selected_count_ok -and $legacy_fallback_ok -and $no_progress_change_ok -and $no_ui_change_ok -and $no_replace_legacy_ok -and $no_cloud_ok -and $fallback_source_ok)) {
    throw "EXAM PREP LOCAL BANK PREVIEW CHECK v0.4.46 FAILED"
  }

  Write-Host "EXAM PREP LOCAL BANK PREVIEW CHECK v0.4.46 PASS"
} finally {
  if (Test-Path $Tmp) {
    Remove-Item -Recurse -Force $Tmp
  }
}

