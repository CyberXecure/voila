# Voila Windows ZIP Candidate START/STOP Smoke Result

Milestone:

```text
v0.3.38-voila-windows-zip-candidate-start-stop-smoke
```

## Purpose

Run a local START/STOP smoke test against the extracted Voila Windows ZIP candidate.

## Scope

```text
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
```

## Candidate

```text
Package root: C:\Users\liian\AppData\Local\Temp\voila-v0.3.36-first-real-zip-candidate-output\extract-smoke\voila
ZIP path: C:\Users\liian\AppData\Local\Temp\voila-v0.3.36-first-real-zip-candidate-output\out\voila-v0.3.36-public-beta-windows-package-candidate.zip
SHA256: 40D9AED111900C1CC47AAF24F45DE406E74480E3F480F448FA521C5F6BD3B22A
```

## Pre-smoke port status

```text
Port 8787: free before smoke
Port 8081: free before smoke
```

## START result

```text
Exit code: 0

START-VOILA first real ZIP candidate placeholder
```

## Local service check

```text
http://127.0.0.1:8787 did not respond: No connection could be made because the target machine actively refused it. (127.0.0.1:8787)
http://localhost:8787 did not respond: No connection could be made because the target machine actively refused it. (localhost:8787)
```

## Port status after START

```text
Port 8787: not in use after START
Port 8081: not in use after START
```

## STOP result

```text
Exit code: 0

STOP-VOILA first real ZIP candidate placeholder
```

## Port status after STOP

```text
Port 8787: free after STOP
Port 8081: free after STOP
```

## Final smoke status

```text
CONDITIONAL
```

Reason:

```text
START/STOP launchers executed successfully, but they appear to be placeholders; no local service response expected.
```

## Notes

If this result is CONDITIONAL, the candidate should not be shared as a runnable package until START/STOP launchers are replaced with real runtime launchers and the smoke test is repeated.

This smoke test did not publish a GitHub release.
