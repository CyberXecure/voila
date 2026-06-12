# Voila Windows ZIP Candidate Complete Runtime Source START/STOP Smoke Checklist

Milestone:

```text
v0.3.56-voila-windows-zip-candidate-complete-runtime-source-start-stop-smoke-plan
```

## Preconditions

```text
[ ] v0.3.55 ZIP build completed
[ ] ZIP SHA256 known
[ ] ZIP extracted into a safe temp/output folder
[ ] extracted package root exists
[ ] START-VOILA.bat exists
[ ] STOP-VOILA.bat exists
[ ] services/api/web_app.py exists
[ ] .venv/Scripts/python.exe exists
[ ] RUNTIME-SOURCE-SUMMARY.txt exists
```

## Pre-smoke checks

```text
[ ] port 8787 free before START
[ ] port 8081 status recorded
[ ] process snapshot captured
[ ] package root confirmed not repository root
```

## START checks

```text
[ ] START-VOILA.bat executed
[ ] START exit code recorded
[ ] START stdout/stderr captured
[ ] runtime/logs/start-voila.log exists
[ ] runtime/state/voila-api.pid status recorded
[ ] port 8787 status after START recorded
```

## Service checks

```text
[ ] http://127.0.0.1:8787/health checked
[ ] http://127.0.0.1:8787 checked
[ ] http://localhost:8787 checked
[ ] response status/body summarized
```

## STOP checks

```text
[ ] STOP-VOILA.bat executed
[ ] STOP exit code recorded
[ ] STOP stdout/stderr captured
[ ] runtime/logs/stop-voila.log exists
[ ] port 8787 free after STOP
[ ] package-owned process stopped
```

## Classification

```text
[ ] PASS/CONDITIONAL/FAIL selected
[ ] reason documented
[ ] no unrelated process killing confirmed
[ ] no installer created
[ ] no GitHub release created
```
