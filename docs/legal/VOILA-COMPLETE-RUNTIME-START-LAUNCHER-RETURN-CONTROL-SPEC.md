# Voila Complete Runtime START Launcher Return-Control Specification

Milestone:

```text
v0.3.58-voila-complete-runtime-start-launcher-return-control-fix-plan
```

## Target files for future implementation

Likely affected generated launcher content inside:

```text
scripts/release/create-complete-windows-runtime-source.ps1
```

Generated package files:

```text
START-VOILA.bat
scripts/start-voila.ps1
scripts/stop-voila.ps1
scripts/check-voila-health.ps1
```

## Desired START-VOILA.bat behavior

`START-VOILA.bat` should remain simple:

```text
call package-local scripts/start-voila.ps1
return its exit code
```

## Desired scripts/start-voila.ps1 behavior

The generated `scripts/start-voila.ps1` should:

```text
start uvicorn as a child/background process
redirect stdout/stderr to runtime/logs
write runtime/state/voila-api.pid
wait for a bounded startup window
verify process did not exit early
optionally verify 127.0.0.1:8787 or /health
return 0 on successful launch
return non-zero on missing files, early exit, or timeout
```

## Recommended startup timeout

Recommended initial timeout:

```text
15 seconds
```

Rationale:

```text
long enough for Uvicorn startup
short enough to avoid frozen smoke/tester experience
```

## Required command alignment

The start command must remain aligned to:

```powershell
.\.venv\Scripts\python.exe -B -m uvicorn web_app:app --app-dir .\services\api --host 127.0.0.1 --port 8787
```

## Required process ownership

The package should only manage the PID it created:

```text
runtime/state/voila-api.pid
```

No broad process killing is allowed.

## Log expectations

Expected logs:

```text
runtime/logs/start-voila.log
runtime/logs/voila-api.out.log
runtime/logs/voila-api.err.log
runtime/logs/stop-voila.log
```

## Failure behavior

START should fail fast if:

```text
.venv/Scripts/python.exe missing
services/api/web_app.py missing
port 8787 already in use by unknown process
uvicorn exits early
startup timeout reached
```

## Smoke runner expectation

After the fix, automated smoke should not need manual intervention.
