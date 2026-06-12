# Voila Windows ZIP Candidate START/STOP Smoke After Return-Control Fix Result

Milestone: v0.3.62-voila-windows-zip-candidate-start-stop-smoke-after-return-control-fix

Scope: Local START/STOP smoke on rebuilt ZIP candidate only.

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

Source branch: test/v0.3.62-voila-windows-zip-candidate-start-stop-smoke-after-return-control-fix
Source commit: 095e86c

ZIP: C:\Users\liian\AppData\Local\Temp\voila-v0.3.61-complete-runtime-source-zip-candidate-output\out\voila-v0.3.61-public-beta-windows-package-candidate.zip
Expected SHA256: 121F3747203BB539033FDE073BC51BD1B0C707C1C562E25A10CE9A77EA24941A
Actual SHA256: 121F3747203BB539033FDE073BC51BD1B0C707C1C562E25A10CE9A77EA24941A
SmokeRoot: C:\Users\liian\AppData\Local\Temp\voila-v0.3.62-zip-start-stop-smoke-after-return-control-fix
PackageRoot: C:\Users\liian\AppData\Local\Temp\voila-v0.3.62-zip-start-stop-smoke-after-return-control-fix\extract\voila

Smoke status: PASS
Reason: ZIP candidate START returned control, local API responded, STOP returned control, and port 8787 was free after STOP.

ZIP located: PASS
SHA256 verified: PASS
Extract validation: PASS
Required package files: PASS
Fixed START launcher content: PASS

START returned within timeout: True
START exit code: 0
START duration seconds: 6.68
START output:
Voila API started. PID: 8180
Open http://127.0.0.1:8787

Local service checks:
- http://127.0.0.1:8787/health: PASS 200
- http://127.0.0.1:8787: PASS 200
- http://localhost:8787: PASS 200

Runtime logs/state:
voila-api.pid: present (9 bytes)
start-voila.log: present (125 bytes)
voila-api.out.log: present (0 bytes)
voila-api.err.log: present (0 bytes)

STOP returned within timeout: True
STOP exit code: 0
STOP output:
Voila package-owned processes stopped or already stopped.

Port status before START:
Port 8787: free before START
Port 8081: free before START

Port status after START:
Port 8787: IN USE after START
Port 8081: free after START

Port status after STOP:
Port 8787: free after STOP
Port 8081: free after STOP

Boundary: No package rebuild, release ZIP, SHA256 file, EXE/MSI installer, GitHub release, GitHub visibility change, payment/licensing implementation, or final legal guarantee was produced by this milestone.
