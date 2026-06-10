# Voila Windows ZIP Candidate START/STOP Smoke Plan

Milestone:

```text
v0.3.37-voila-windows-zip-candidate-start-stop-smoke-plan
```

## Purpose

Plan a local START/STOP smoke test for the first Voila Windows ZIP candidate after extraction.

This milestone is documentation/release smoke-test planning only.

It does not:

```text
run START-VOILA.bat
run STOP-VOILA.bat
change runtime files
change backend behavior
change frontend behavior
change dependencies
create a ZIP
create an installer
publish a GitHub release
upload release assets
change GitHub visibility
add payment or activation
provide final legal approval
```

---

## Background

The first local ZIP candidate build passed in:

```text
v0.3.36-voila-windows-zip-candidate-first-real-zip-build
```

Result:

```text
ZIP created: PASS
SHA256 created: PASS
SHA256 verified: PASS
extract validation: PASS
BUILD-SUMMARY.txt created: PASS
no EXE/MSI installer created: PASS
no GitHub release created: PASS
```

ZIP candidate:

```text
voila-v0.3.36-public-beta-windows-package-candidate.zip
```

SHA256:

```text
40D9AED111900C1CC47AAF24F45DE406E74480E3F480F448FA521C5F6BD3B22A
```

The next step is to plan a START/STOP smoke test on the extracted ZIP candidate.

---

## Smoke test goal

Confirm that an extracted Windows ZIP candidate can:

```text
start using START-VOILA.bat
expose expected local service/UI
stay running long enough for a basic check
stop using STOP-VOILA.bat
clean up expected processes and ports
```

---

## Candidate under test

Recommended candidate:

```text
voila-v0.3.36-public-beta-windows-package-candidate.zip
```

Expected local output root from prior build:

```text
C:\Users\liian\AppData\Local\Temp\voila-v0.3.36-first-real-zip-candidate-output
```

Expected extracted package root from prior build:

```text
C:\Users\liian\AppData\Local\Temp\voila-v0.3.36-first-real-zip-candidate-output\extract-smoke\voila
```

If the temp output no longer exists, re-run the local build or extract the ZIP candidate to a clean local folder.

---

## Expected files before smoke

Required:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

---

## Expected checks

Before START:

```text
[ ] extracted package root exists
[ ] START-VOILA.bat exists
[ ] STOP-VOILA.bat exists
[ ] README-WINDOWS.txt exists
[ ] RELEASE-NOTES.txt exists
[ ] legal/ folder exists
[ ] expected local ports are free or previous processes are stopped
```

During START:

```text
[ ] START-VOILA.bat launches without immediate failure
[ ] expected local service starts
[ ] expected UI or health endpoint responds
[ ] logs do not show blocking errors
```

During STOP:

```text
[ ] STOP-VOILA.bat runs
[ ] expected processes stop
[ ] expected ports are released
[ ] no orphaned service windows/processes remain
```

---

## Expected ports

Known Voila local service ports from previous package work:

```text
Voila API/UI service: 8787
LanguageTool service: 8081
```

If the current package uses different ports, record the actual ports in the smoke result.

---

## Suggested checks

Health/API check if available:

```powershell
Invoke-WebRequest http://127.0.0.1:8787 -UseBasicParsing
```

Port check:

```powershell
Get-NetTCPConnection -LocalPort 8787 -ErrorAction SilentlyContinue
Get-NetTCPConnection -LocalPort 8081 -ErrorAction SilentlyContinue
```

Process review:

```powershell
Get-Process | Where-Object {
  $_.ProcessName -match "python|java|tesseract|voila|languagetool"
}
```

---

## Smoke result statuses

Use:

```text
PASS
CONDITIONAL
FAIL
NOT RUN
```

Definitions:

```text
PASS:
START works, local check responds, STOP cleans up.

CONDITIONAL:
App starts but has warnings or manual cleanup was required.

FAIL:
App does not start, local check fails, or STOP does not clean up.

NOT RUN:
Smoke test not executed.
```

---

## Required output documentation

The future smoke result should record:

```text
ZIP path
SHA256
extracted path
START command result
local service check result
STOP command result
process/port cleanup result
known warnings
final status
```

---

## Publication boundary

A passing START/STOP smoke test does not automatically publish a GitHub release.

Publication remains a separate milestone with:

```text
release notes review
asset upload decision
SHA256 asset upload
public wording review
support/feedback path
legal/commercial review as needed
```

---

## Recommended next milestone

After this plan:

```text
v0.3.38-voila-windows-zip-candidate-start-stop-smoke
```

That milestone should run the START/STOP smoke test and document results.
