# Voila Windows ZIP Candidate Real Launchers START/STOP Smoke Result

Milestone:

`	ext
v0.3.46-voila-windows-zip-candidate-real-launchers-start-stop-smoke
`

## Purpose

Run local START/STOP smoke validation on the v0.3.44 Windows ZIP candidate with real launchers.

## Scope

`	ext
Local START/STOP smoke validation only.
No runtime changes.
No backend changes.
No frontend behavior changes.
No dependency changes.
No package rebuild.
No ZIP creation.
No installer creation.
No GitHub visibility change.
No payment/licensing implementation.
No GitHub release publication.
No final legal guarantee.
`

## Candidate

`	ext
Package root: C:\Users\liian\AppData\Local\Temp\voila-v0.3.44-real-launchers-zip-candidate-output\extract-smoke\voila
ZIP path: C:\Users\liian\AppData\Local\Temp\voila-v0.3.44-real-launchers-zip-candidate-output\out\voila-v0.3.44-public-beta-windows-package-candidate.zip
SHA256: 9516F462B3D12D800DBC37EDBD6F3148C2A85BBC0690E7CB577A65FB1624C2F5
`

## Pre-smoke port status

`	ext
Port 8787: free before smoke
Port 8081: free before smoke
`

## START result

`	ext
Exit code: 2

Voila API entrypoint not found. Expected one of app\api\main.py, api\main.py, backend\main.py, service\main.py, main.py.
`

## Local service check

`	ext
http://127.0.0.1:8787/health did not respond: No connection could be made because the target machine actively refused it. (127.0.0.1:8787)
http://127.0.0.1:8787 did not respond: No connection could be made because the target machine actively refused it. (127.0.0.1:8787)
http://localhost:8787 did not respond: No connection could be made because the target machine actively refused it. (localhost:8787)
`

## Process snapshot after START

`	ext
No matching python/java/tesseract/voila/languagetool processes found after START.
`

## Port status after START

`	ext
Port 8787: not in use after START
Port 8081: not in use after START
`

## Runtime state

`	ext
voila-api.pid not present
languagetool.pid not present
`

## STOP result

`	ext
Exit code: 0

Voila package-owned processes stopped or already stopped.
`

## Port status after STOP

`	ext
Port 8787: free after STOP
Port 8081: free after STOP
`

## Final smoke status

`	ext
CONDITIONAL
`

Reason:

`	ext
Real launchers executed, but the package runtime is incomplete for a full service start in this candidate.
`

## Notes

This smoke test did not publish a GitHub release.

If the result is CONDITIONAL due to incomplete runtime files, the next step is to build a candidate from a complete runtime source and rerun START/STOP smoke.
