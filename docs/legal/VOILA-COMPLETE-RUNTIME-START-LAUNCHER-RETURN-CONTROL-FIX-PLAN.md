# Voila Complete Runtime START Launcher Return-Control Fix Plan

Milestone:

```text
v0.3.58-voila-complete-runtime-start-launcher-return-control-fix-plan
```

## Purpose

Plan the fix for the v0.3.57 START/STOP smoke blocker.

The v0.3.57 smoke proved that the complete-runtime ZIP candidate can start the package-local Voila API on:

```text
127.0.0.1:8787
```

and that Uvicorn reaches:

```text
Application startup complete
```

However, the automated smoke runner blocked while executing:

```text
START-VOILA.bat
```

and therefore did not complete its own health-check/documentation flow autonomously.

This milestone is documentation/fix planning only.

It does not:

```text
modify launchers
modify smoke runner
run START-VOILA.bat
run STOP-VOILA.bat
rebuild ZIP
create installer
publish GitHub release
change GitHub visibility
add payment/licensing
provide final legal approval
```

## Background

Completed milestone:

```text
v0.3.57-voila-windows-zip-candidate-complete-runtime-source-start-stop-smoke
```

Result:

```text
CONDITIONAL
```

Observed:

```text
ZIP SHA256 verified
package extracted to safe smoke folder
required package files verified
port 8787 free before START
port 8081 free before START
START-VOILA.bat executed
Voila API reached Uvicorn application startup complete
Voila API listened on 127.0.0.1:8787
STOP-VOILA.bat manually stopped package-owned processes
post-STOP ports/processes were clean
```

Blocker:

```text
START-VOILA.bat / smoke runner did not return control predictably
```

## Fix goal

After the fix, the smoke should be able to run:

```text
START-VOILA.bat
health checks
STOP-VOILA.bat
post-stop verification
documentation
```

without manual intervention.

## Preferred fix strategy

Preferred implementation strategy:

```text
Keep START-VOILA.bat user-friendly.
Make scripts/start-voila.ps1 launch the API as a detached background process and return exit code 0 after startup verification.
```

Expected behavior:

```text
START returns control within a bounded timeout.
API remains running after START exits.
runtime/state/voila-api.pid records the process ID.
runtime/logs/start-voila.log records startup status.
runtime/logs/voila-api.out.log and voila-api.err.log capture service logs.
```

## Alternative strategy

If launcher changes are risky, the smoke runner can use:

```powershell
Start-Process -FilePath .\START-VOILA.bat -WorkingDirectory <package-root> -PassThru
```

and then perform health checks independently.

This is acceptable for internal smoke automation, but less valuable for tester UX than a START launcher that returns control predictably.

## Required launcher behavior

START should:

```text
resolve package root
verify .venv/Scripts/python.exe exists
verify services/api/web_app.py exists
launch uvicorn web_app:app with --app-dir .\services\api
write PID file
wait briefly for process to remain alive
optionally poll health endpoint
return 0 if startup appears successful
return non-zero if process exits early or required files are missing
never block indefinitely
```

## Required STOP behavior

STOP should:

```text
read runtime/state/voila-api.pid
stop package-owned process only
remove stale PID file
not kill unrelated Python/Java processes
return 0 if process is stopped or already stopped
```

## Required validation

Future implementation milestone should validate:

```text
START returns within bounded timeout
port 8787 listens after START
health/root endpoint responds
STOP returns 0
port 8787 is free after STOP
no unrelated processes are killed
logs and PID files are created as expected
```

## Recommended next milestone

```text
v0.3.59-voila-complete-runtime-start-launcher-return-control-fix
```

That milestone should implement the launcher or smoke runner fix.
