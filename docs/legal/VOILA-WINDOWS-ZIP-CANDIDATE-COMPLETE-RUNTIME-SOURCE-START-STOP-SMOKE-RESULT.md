# Voila Windows ZIP Candidate Complete Runtime Source START/STOP Smoke Result

Milestone:

v0.3.57-voila-windows-zip-candidate-complete-runtime-source-start-stop-smoke

## Scope

Local START/STOP smoke only.

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

## Candidate

ZIP: voila-v0.3.55-public-beta-windows-package-candidate.zip
SHA256: DCA7066038409CF759A055D494CA981F9DE4A0DDE6AD79F5CC20ACD062140E1D

## Result

Smoke status: CONDITIONAL

Reason: START-VOILA.bat started the package-local Voila API and Uvicorn reached application startup complete on 127.0.0.1:8787, but the automated smoke runner blocked while executing START-VOILA.bat and did not complete its own health-check/documentation flow. STOP-VOILA.bat was then run manually and package-owned processes were stopped or already stopped.

## Observed evidence

Pre-smoke ports:
- Port 8787 free before START
- Port 8081 free before START

START evidence:
- START-VOILA.bat was executed
- Port 8787 entered Listen state
- Uvicorn reported: Started server process
- Uvicorn reported: Application startup complete
- Uvicorn reported: running on http://127.0.0.1:8787

STOP evidence:
- STOP-VOILA.bat output: Voila package-owned processes stopped or already stopped.
- Post-stop verification showed no listed 8787/8081 listeners.
- Post-stop verification showed no listed matching python/java/tesseract/voila/languagetool/uvicorn processes.

## Interpretation

The complete-runtime ZIP candidate is materially improved versus previous candidates because the API can start locally from the package. However, tester readiness is not yet PASS because START-VOILA.bat / the smoke runner needs to return control cleanly for automated verification.

## Recommended next milestone

v0.3.58-voila-complete-runtime-start-launcher-return-control-fix-plan

Goal: update the launcher or smoke strategy so START returns predictably after launching the API, while STOP remains package-owned and safe.
