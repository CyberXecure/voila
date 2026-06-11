# Voila Windows ZIP Candidate Real Launchers START/STOP Smoke Plan

Milestone:

```text
v0.3.45-voila-windows-zip-candidate-real-launchers-start-stop-smoke-plan
```

## Purpose

Plan a local START/STOP smoke test for the Windows ZIP candidate rebuilt with real package launchers.

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

The real launchers ZIP candidate build completed in:

```text
v0.3.44-voila-windows-zip-candidate-real-launchers-build
```

Result:

```text
ZIP created: PASS
SHA256 created: PASS
SHA256 verified: PASS
extract validation: PASS
real launchers present in extracted ZIP: PASS
BUILD-SUMMARY.txt created: PASS
no EXE/MSI installer created: PASS
no START/STOP execution: PASS
no GitHub release created: PASS
```

ZIP candidate:

```text
voila-v0.3.44-public-beta-windows-package-candidate.zip
```

SHA256:

```text
9516F462B3D12D800DBC37EDBD6F3148C2A85BBC0690E7CB577A65FB1624C2F5
```

The next step is to plan START/STOP smoke execution on the extracted ZIP candidate.

---

## Candidate under test

Expected local output root from v0.3.44:

```text
C:\Users\liian\AppData\Local\Temp\voila-v0.3.44-real-launchers-zip-candidate-output
```

Expected ZIP path:

```text
C:\Users\liian\AppData\Local\Temp\voila-v0.3.44-real-launchers-zip-candidate-output\out\voila-v0.3.44-public-beta-windows-package-candidate.zip
```

Expected extracted package root:

```text
C:\Users\liian\AppData\Local\Temp\voila-v0.3.44-real-launchers-zip-candidate-output\extract-smoke\voila
```

If the temp output no longer exists, rerun the v0.3.44 build or extract the ZIP candidate into a clean local folder.

---

## Required files before smoke

The extracted package root must include:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
scripts/start-voila.ps1
scripts/stop-voila.ps1
scripts/check-voila-health.ps1
runtime/state/
runtime/logs/
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

---

## Pre-smoke checks

Before running START:

```text
[ ] ZIP SHA256 verified
[ ] extracted package root exists
[ ] required launcher files exist
[ ] legal folder exists
[ ] runtime/state exists
[ ] runtime/logs exists
[ ] ports 8787 and 8081 checked
[ ] old Voila/LanguageTool package-owned processes are stopped
[ ] no unrelated process will be killed by the smoke
```

---

## START smoke checks

Run:

```powershell
.\START-VOILA.bat
```

Expected:

```text
START exit code 0
runtime/logs/start-voila.log created
runtime/state/voila-api.pid created if API starts
Voila local service responds
health check passes if endpoint exists
```

Preferred health URLs:

```text
http://127.0.0.1:8787/health
http://127.0.0.1:8787
```

LanguageTool check if bundled and expected:

```text
http://127.0.0.1:8081
```

---

## STOP smoke checks

Run:

```powershell
.\STOP-VOILA.bat
```

Expected:

```text
STOP exit code 0
package-owned processes stopped or already stopped
ports released
stale PID files cleaned if applicable
runtime/logs/stop-voila.log created
no unrelated Python/Java processes killed
```

---

## Port checks

Use:

```powershell
Get-NetTCPConnection -LocalPort 8787 -ErrorAction SilentlyContinue
Get-NetTCPConnection -LocalPort 8081 -ErrorAction SilentlyContinue
```

Expected final state after STOP:

```text
port 8787 free
port 8081 free or documented if intentionally still used
```

---

## Process checks

Use:

```powershell
Get-Process | Where-Object {
  $_.ProcessName -match "python|java|tesseract|voila|languagetool"
}
```

The smoke result must distinguish between:

```text
package-owned processes
unrelated user processes
```

STOP must not be counted as PASS if it kills unrelated Python/Java processes.

---

## Result classification

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
START returns success, Voila responds locally, STOP returns success, package-owned processes stop, ports clean up.

CONDITIONAL:
START/STOP executes but runtime files are incomplete, a manual cleanup was needed, or a known limitation prevents full service response.

FAIL:
START fails, service does not start when it should, STOP fails, ports remain stuck, or unrelated processes are killed.

NOT RUN:
Smoke test not executed.
```

---

## Required result documentation

The execution milestone should record:

```text
ZIP path
SHA256
extracted package root
pre-smoke port status
START command result
local service/health result
process snapshot after START
STOP command result
post-STOP port status
final result classification
known warnings
next action
```

---

## Safety boundary

This smoke plan does not approve public sharing.

A successful smoke test may qualify the package for a later publication/release gate, but it does not automatically:

```text
publish GitHub release
upload release assets
claim final release
enable paid distribution
create installer
sign binaries
```

---

## Recommended next milestone

```text
v0.3.46-voila-windows-zip-candidate-real-launchers-start-stop-smoke
```

That milestone should run the START/STOP smoke test and document the result.
