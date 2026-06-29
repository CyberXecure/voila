$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

Write-Host "=== v0.5.3 owner-only session preview JSON check ===" -ForegroundColor Cyan

$ApiPath = Join-Path $RepoRoot "services\api"
$env:PYTHONPATH = $ApiPath

$WorkRoot = Join-Path $RepoRoot ".tmp\v053-owner-only-session-preview-json"
$PreviewPath = Join-Path $WorkRoot "owner_only_session_preview.json"

if (Test-Path $WorkRoot) {
  Remove-Item $WorkRoot -Recurse -Force
}

Write-Host "`n=== Build v0.5.3 session preview ===" -ForegroundColor Yellow
$previewJson = python "scripts/dev/build-local-bank-owner-only-session-preview.py" `
  --root "." `
  --work-root $WorkRoot `
  --output $PreviewPath `
  --expect-pass

$previewJson | Out-Host
$preview = $previewJson | ConvertFrom-Json

Write-Host "`n=== Validate preview file exists ===" -ForegroundColor Yellow
if (!(Test-Path $PreviewPath)) {
  throw "Preview file was not created: $PreviewPath"
}

$previewFromFile = Get-Content $PreviewPath -Raw -Encoding UTF8 | ConvertFrom-Json

if ($previewFromFile.status -ne "pass") {
  throw "Preview status is not pass"
}
if ($previewFromFile.session_preview.question_count -ne 5) {
  throw "Session preview question_count is not 5"
}
if ($previewFromFile.delivery_result.effective_source -ne "local_bank") {
  throw "Delivery effective_source is not local_bank"
}
if ($previewFromFile.delivery_result.delivery_performed -ne $true) {
  throw "Delivery was not performed"
}
if ($previewFromFile.rollback_result.effective_source -ne "legacy_fallback") {
  throw "Rollback effective_source is not legacy_fallback"
}
if ($previewFromFile.rollback_result.delivery_performed -ne $false) {
  throw "Rollback delivery_performed is not false"
}
if ($previewFromFile.session_preview.interaction_policy.save_attempt_supported -ne $false) {
  throw "save_attempt_supported is not false"
}
if ($previewFromFile.session_preview.interaction_policy.progress_update_supported -ne $false) {
  throw "progress_update_supported is not false"
}
if ($previewFromFile.session_preview.interaction_policy.live_scoring_supported -ne $false) {
  throw "live_scoring_supported is not false"
}
if ($previewFromFile.session_preview.interaction_policy.answers_available_in_preview -ne $false) {
  throw "answers_available_in_preview is not false"
}

foreach ($question in $previewFromFile.session_preview.questions) {
  if (-not $question.question_id) {
    throw "Question missing question_id"
  }
  if (-not $question.prompt) {
    throw "Question missing prompt"
  }
  if ($question.will_save_attempt -ne $false) {
    throw "Question will_save_attempt is not false"
  }
  if ($question.will_update_progress -ne $false) {
    throw "Question will_update_progress is not false"
  }
  if ($question.will_score_answer -ne $false) {
    throw "Question will_score_answer is not false"
  }
}

Write-Host "`n=== Ensure no public UI / web_app.py patch ===" -ForegroundColor Yellow
$changed = git diff --name-only
$changed | Out-Host

if ($changed -match "services/api/web_app.py") {
  throw "web_app.py was modified, which is not allowed for v0.5.3"
}

Write-Host "`n=== Clean temporary preview data ===" -ForegroundColor Yellow
if (Test-Path $WorkRoot) {
  Remove-Item $WorkRoot -Recurse -Force
}
if (Test-Path ".tmp") {
  $remaining = Get-ChildItem ".tmp" -Force -ErrorAction SilentlyContinue
  if (-not $remaining) {
    Remove-Item ".tmp" -Force
  }
}

Write-Host "`n=== Compile session preview helper ===" -ForegroundColor Yellow
python -m compileall "scripts/dev/build-local-bank-owner-only-session-preview.py"

Write-Host "`n=== Diff whitespace check ===" -ForegroundColor Yellow
git diff --check

Write-Host "`n=== v0.5.3 SESSION PREVIEW CHECK PASS ===" -ForegroundColor Green

