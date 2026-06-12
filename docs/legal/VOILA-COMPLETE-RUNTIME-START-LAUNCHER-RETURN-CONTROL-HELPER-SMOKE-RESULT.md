# Voila Complete Runtime START Launcher Return-Control Helper Smoke Result

Milestone:

v0.3.60-voila-complete-runtime-start-launcher-return-control-helper-smoke

## Scope

Release/package helper smoke with local START/STOP execution.

No backend behavior changes.
No frontend behavior changes.
No dependency changes.
No package rebuild.
No ZIP creation.
No installer creation.
No GitHub visibility change.
No payment/licensing implementation.
No GitHub release publication.
No final legal guarantee.

## Result

Smoke status: PASS

Reason: START-VOILA.bat returned control, the local API responded successfully on 127.0.0.1:8787, STOP-VOILA.bat returned control, and port 8787 was free after STOP.

## Runtime source

RuntimeSourceRoot: C:\Users\liian\AppData\Local\Temp\voila-v0.3.60-start-return-control-helper-smoke
PackageRoot: C:\Users\liian\AppData\Local\Temp\voila-v0.3.60-start-return-control-helper-smoke\voila

## Helper generation

Helper execution: PASS
Runtime source validation: PASS
Launcher content validation: PASS

## START return-control check

START returned: True
START exit code: 0
START duration seconds: 6.38
START output: Voila API started. PID: 10136; Open http://127.0.0.1:8787

## Local service checks

http://127.0.0.1:8787/health: PASS 200
Body preview: {"status":"ok"}
http://127.0.0.1:8787: PASS 200
http://localhost:8787: PASS 200

## Runtime logs/state

voila-api.pid: present
start-voila.log: present
voila-api.out.log: present
voila-api.err.log: present

## STOP check

STOP returned: True
STOP exit code: 0
STOP output: Voila package-owned processes stopped or already stopped.

## Port status

Before START:
- Port 8787: free before START
- Port 8081: free before START

After START:
- Port 8787: IN USE after START
- Port 8081: free after START

After STOP:
- Port 8787: free after STOP
- Port 8081: free after STOP

## Artifact scan note

The smoke script's broad recursive artifact scan found a legitimate .zip test fixture inside package-local .venv dependencies. This is not a release ZIP produced by this milestone.

Future artifact checks should be scoped to release output roots, not package dependency internals.

## Boundary

No release ZIP, SHA256, EXE/MSI installer, GitHub release, GitHub visibility change, payment/licensing implementation, or final legal guarantee was produced by this milestone.

## Recommended next milestone

v0.3.61-voila-windows-zip-candidate-complete-runtime-source-rebuild-after-start-return-control-fix

Goal: rebuild a ZIP candidate using the fixed START launcher and then run full ZIP START/STOP smoke.
