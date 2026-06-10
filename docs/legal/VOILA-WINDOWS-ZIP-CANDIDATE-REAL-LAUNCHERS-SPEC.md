# Voila Windows ZIP Candidate Real Launchers Specification

## Purpose

Specify expected behavior for real Windows package launchers.

This is planning-only.

---

## Files

Required:

```text
START-VOILA.bat
STOP-VOILA.bat
```

Optional helpers:

```text
scripts/start-voila.ps1
scripts/stop-voila.ps1
scripts/check-voila-health.ps1
```

---

## START-VOILA.bat

Responsibilities:

```text
resolve package root
call package-local PowerShell helper if used
start dependencies
start Voila service
wait for health check
print local URL
write logs
return 0 on success
return non-zero on failure
```

Should avoid:

```text
hardcoded developer paths
global dependency assumptions
silent failures
broad process killing
```

---

## STOP-VOILA.bat

Responsibilities:

```text
resolve package root
call package-local PowerShell helper if used
read PID/state files
stop package-owned processes
release ports
clean stale PID files
return 0 when stopped or already stopped safely
return non-zero on cleanup failure
```

Should avoid:

```text
killing unrelated Python processes
killing unrelated Java processes
deleting user files
requiring admin unless absolutely necessary
```

---

## Health check

Preferred order:

```text
http://127.0.0.1:8787/health
http://127.0.0.1:8787
```

Timeout should be finite.

Recommended:

```text
60 seconds maximum wait
```

---

## Logs and state

Recommended package-local folders:

```text
runtime/logs/
runtime/state/
```

Recommended files:

```text
runtime/logs/start-voila.log
runtime/logs/stop-voila.log
runtime/logs/voila-api.log
runtime/logs/languagetool.log
runtime/state/voila-api.pid
runtime/state/languagetool.pid
```

---

## Exit codes

Recommended:

```text
0 = success
1 = general failure
2 = missing runtime files
3 = port conflict
4 = health check timeout
5 = cleanup failure
```

---

## Smoke requirements

The launchers are not acceptable until a ZIP candidate smoke test verifies:

```text
START exit code 0
Voila local service responds
STOP exit code 0
ports released
no orphaned package-owned processes
```
