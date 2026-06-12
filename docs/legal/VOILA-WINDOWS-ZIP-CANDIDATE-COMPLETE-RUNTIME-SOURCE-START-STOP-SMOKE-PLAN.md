# Voila Windows ZIP Candidate Complete Runtime Source START/STOP Smoke Plan

Milestone:

```text
v0.3.56-voila-windows-zip-candidate-complete-runtime-source-start-stop-smoke-plan
```

## Purpose

Plan a controlled START/STOP smoke test for the Windows ZIP candidate built with complete runtime source:

```text
voila-v0.3.55-public-beta-windows-package-candidate.zip
```

This milestone is documentation/smoke planning only.

It does not run START/STOP, start local services, rebuild ZIP, create installers, publish releases, change GitHub visibility, add payment/licensing, or provide final legal approval.

## Background

The v0.3.55 complete runtime source ZIP build completed with ZIP/SHA256/extract validation PASS.

ZIP candidate:

```text
voila-v0.3.55-public-beta-windows-package-candidate.zip
```

SHA256:

```text
DCA7066038409CF759A055D494CA981F9DE4A0DDE6AD79F5CC20ACD062140E1D
```

## Smoke objective

Verify that the extracted complete-runtime ZIP candidate can run START-VOILA.bat, start the package-local Voila API on 127.0.0.1:8787, serve a local response, write runtime logs/state, run STOP-VOILA.bat, stop package-owned processes, and free expected ports.

## Candidate under test

Expected extracted package root:

```text
<output-root>\extract-smoke\voila
```

Required package files:

```text
START-VOILA.bat
STOP-VOILA.bat
scripts/start-voila.ps1
scripts/stop-voila.ps1
scripts/check-voila-health.ps1
services/api/web_app.py
.venv/Scripts/python.exe
RUNTIME-SOURCE-SUMMARY.txt
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

## Pre-smoke safety checks

Before START:

```text
[ ] confirm package root is under temp/output, not repository root
[ ] verify ZIP SHA256
[ ] verify package files exist
[ ] check port 8787 is free
[ ] check port 8081 and document status
[ ] capture process snapshot for python/java/tesseract/voila/languagetool
```

## START command

From extracted package root:

```powershell
.\START-VOILA.bat
```

Expected:

```text
START exits 0 if API process starts
runtime/state/voila-api.pid created
runtime/logs/start-voila.log created
runtime/logs/voila-api.out.log or err.log created
```

## Local service checks

Check:

```text
http://127.0.0.1:8787/health
http://127.0.0.1:8787
http://localhost:8787
```

Minimum PASS condition: one expected local URL responds successfully.

## STOP command

From extracted package root:

```powershell
.\STOP-VOILA.bat
```

Expected:

```text
STOP exits 0
package-owned API process is stopped
port 8787 is free after STOP
runtime/logs/stop-voila.log exists
```

## Classification rules

PASS:

```text
START exits 0
local Voila service responds
port 8787 active after START
STOP exits 0
port 8787 free after STOP
no unrelated processes killed
```

CONDITIONAL:

```text
START launches but API exits due to a documented runtime dependency issue
START/STOP scripts work but service health is blocked by deferred dependency or asset issue
logs clearly identify blocker
no unsafe process behavior
```

FAIL:

```text
START crashes before service attempt
web_app.py missing
package-local Python missing
START/STOP unsafe process behavior
STOP fails to stop package-owned process
port remains stuck after STOP
```

## Recommended next milestone

```text
v0.3.57-voila-windows-zip-candidate-complete-runtime-source-start-stop-smoke
```
