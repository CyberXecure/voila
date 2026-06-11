# Voila Windows Package Complete Runtime Source Copy Map

Milestone:

`	ext
v0.3.48-voila-windows-package-complete-runtime-source-discovery
`

## Purpose

Draft a copy map for the future complete Windows runtime source based on discovery output.

## Proposed runtime source root

`	ext
<runtime-source>\voila
`

## API/backend

`	ext
Candidate API entrypoint: scripts\dev\add-course-tools-navigation.py
Target path should match launcher expectations or launcher helper must be updated.
`

## Dependencies

`	ext
Detected strategy: requirements.txt detected
Future package should use embedded Python or package-local .venv where practical.
`

## Frontend/static

`	ext
Detected strategy: frontend/static references detected; exact packaging strategy requires review
Future package should define whether static assets are served by backend or UI is deferred.
`

## LanguageTool/Java

`	ext
Detected strategy: LanguageTool references detected
Future package should define bundled vs deferred LanguageTool.
`

## Tesseract/OCR

`	ext
Detected strategy: Tesseract/OCR references detected
Future package should define bundled vs deferred OCR.
`

## Always generate during packaging

`	ext
START-VOILA.bat
STOP-VOILA.bat
scripts/start-voila.ps1
scripts/stop-voila.ps1
scripts/check-voila-health.ps1
runtime/state/
runtime/logs/
legal/
`

## Exclusions

`	ext
.git/
.github/
.env
secrets
private data
developer caches
.release-cache/
temporary build outputs
`
