# Voila! Language Pack RC Manual Test Plan

Milestone: v0.2.41-public-beta-language-pack-rc-manual-test-plan
Status: manual test planning
Scope: documentation only; no GitHub release upload, no tag, no public ZIP publish, no runtime changes, no UI changes

## Goal

This milestone documents the manual validation plan for the local RC ZIP produced in v0.2.40.

Validated RC ZIP:

```text
ZIP:    D:\dev\releases\voila-v0240-lp-rc1-20260517-0914.zip
SHA256: 33DC31243F45AD499A889A12F4140779499EFCC0C6218C5BB011920CF36679BC
```

## Current automated baseline

The RC ZIP already passed:

- build-output language-pack smoke
- standalone package language-pack smoke
- full standalone runtime smoke
- source language-pack inspection
- language-pack validation
- Python compile
- PowerShell parse check

## Why manual testing is still needed

Automated smoke tests verify packaging, startup, ports, LanguageTool, Tesseract, and required files.

Manual testing verifies the actual user flow:

- ZIP extraction experience
- startup script behavior
- browser/app usability
- PDF upload flow
- OCR review flow
- language-pack-backed UI behavior
- clean shutdown behavior

## Manual test environment

Recommended environment:

- Windows 10 or Windows 11
- PowerShell 7.x
- clean extraction folder outside the repository
- no system Python, Tesseract, or Java required in PATH
- no GitHub release upload during test

## Suggested extraction path

```text
D:\dev\manual-tests\voila-v0240-lp-rc1-20260517-0914-manual
```

## Manual test steps

### 1. Prepare clean folder

- create a clean manual test directory
- remove any previous extracted copy
- extract the RC ZIP into the clean directory

### 2. Verify package contents

Confirm these files exist after extraction:

- app/Run-Voila.ps1
- app/Stop-Voila.ps1
- app/python/python.exe
- app/runtime/tesseract/tesseract.exe
- app/runtime/java/bin/java.exe
- app/runtime/languagetool/languagetool-server.jar
- app/language-packs/core/ro.language-pack.json
- app/language-packs/core/en.language-pack.json
- app/language-packs/schema/language-pack.schema.json

### 3. Start Voila

From the extracted app folder, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\Run-Voila.ps1
```

Expected result:

- Voila starts without requiring dev environment setup
- local API becomes available
- browser/app opens or the local URL is shown
- LanguageTool starts locally

### 4. Verify health endpoint

Expected endpoint:

```text
http://127.0.0.1:8780/health
```

Expected response:

```json
{"status":"ok"}
```

### 5. Verify LanguageTool

Expected endpoint:

```text
http://127.0.0.1:8081/v2/check
```

Expected result:

- LanguageTool responds to a basic grammar check
- no external LanguageTool server is required

### 6. Verify Tesseract languages

Expected OCR languages:

- eng
- osd
- ron
- rus

### 7. Manual app flow

Perform a real user flow:

- open Voila in the browser
- upload a small PDF
- run OCR or open OCR review flow
- confirm OCR review page opens
- confirm generated or reviewed text can be viewed
- confirm no obvious broken navigation
- confirm language-pack-backed Romanian and English labels are present where expected

### 8. Stop Voila

From the extracted app folder, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\Stop-Voila.ps1
```

Expected result:

- Voila stops cleanly
- LanguageTool stops cleanly
- port 8780 is released
- port 8081 is released

## Pass criteria

The RC manual test passes only if:

- ZIP extracts cleanly
- required files are present
- Run-Voila.ps1 starts the app
- /health returns ok
- LanguageTool responds
- Tesseract languages are available
- PDF upload flow works
- OCR review flow opens
- Stop-Voila.ps1 stops all local services
- ports are released after shutdown

## Safety rules

This milestone must not:

- upload assets to GitHub Releases
- create a Git tag
- publish the ZIP
- overwrite v0.2.0-public-beta assets
- change runtime behavior
- change UI behavior
- add or modify LICENSE files

## Decision for this milestone

v0.2.41 is documentation only.

No manual test execution is required by this milestone itself.
