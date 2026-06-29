$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

Write-Host "=== v0.5.4 session preview encoding/copy polish check ===" -ForegroundColor Cyan

$ApiPath = Join-Path $RepoRoot "services\api"
$env:PYTHONPATH = $ApiPath

$WorkRoot = Join-Path $RepoRoot ".tmp\v054-session-preview-copy-polish"
$PreviewPath = Join-Path $WorkRoot "owner_only_session_preview.json"

if (Test-Path $WorkRoot) {
  Remove-Item $WorkRoot -Recurse -Force
}

Write-Host "`n=== Build polished v0.5.3 session preview ===" -ForegroundColor Yellow
$previewJson = python "scripts/dev/build-local-bank-owner-only-session-preview.py" `
  --root "." `
  --work-root $WorkRoot `
  --output $PreviewPath `
  --expect-pass

$previewJson | Out-Host

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

Write-Host "`n=== Validate prompt copy polish ===" -ForegroundColor Yellow
$badMarkers = @("Γ", "╦", "┬", "─", "∩", "�")
$questionJson = $previewFromFile.session_preview.questions | ConvertTo-Json -Depth 20

foreach ($marker in $badMarkers) {
  if ($questionJson.Contains($marker)) {
    throw "Preview question copy still contains mojibake marker: $marker"
  }
}

foreach ($question in $previewFromFile.session_preview.questions) {
  if (-not $question.prompt) {
    throw "Question prompt is empty"
  }
  if ([string]$question.prompt -match "Name one key point supported by the source text") {
    throw "Generic English smoke prompt was not polished"
  }
  if (($question.prompt).Length -gt 320) {
    throw "Question prompt exceeds polished copy length limit"
  }
  if ($question.answer_hidden_until_submission -ne $true) {
    throw "answer_hidden_until_submission is not true"
  }
  if ($question.explanation_hidden_until_submission -ne $true) {
    throw "explanation_hidden_until_submission is not true"
  }
  if ($question.will_save_attempt -ne $false) {
    throw "will_save_attempt is not false"
  }
  if ($question.will_update_progress -ne $false) {
    throw "will_update_progress is not false"
  }
  if ($question.will_score_answer -ne $false) {
    throw "will_score_answer is not false"
  }
}

if ($previewFromFile.safety_confirmations.adds_public_ui -ne $false) {
  throw "adds_public_ui is not false"
}
if ($previewFromFile.safety_confirmations.patches_web_app -ne $false) {
  throw "patches_web_app is not false"
}
if ($previewFromFile.safety_confirmations.persists_attempts -ne $false) {
  throw "persists_attempts is not false"
}
if ($previewFromFile.safety_confirmations.scores_live_session -ne $false) {
  throw "scores_live_session is not false"
}

Write-Host "`n=== Ensure no public UI / web_app.py patch ===" -ForegroundColor Yellow
$changed = git diff --name-only
$changed | Out-Host

if ($changed -match "services/api/web_app.py") {
  throw "web_app.py was modified, which is not allowed for v0.5.4"
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

Write-Host "`n=== Compile touched helper ===" -ForegroundColor Yellow
python -m compileall "scripts/dev/build-local-bank-owner-only-session-preview.py"

Write-Host "`n=== Diff whitespace check ===" -ForegroundColor Yellow
git diff --check

Write-Host "`n=== v0.5.4 SESSION PREVIEW COPY POLISH CHECK PASS ===" -ForegroundColor Green
