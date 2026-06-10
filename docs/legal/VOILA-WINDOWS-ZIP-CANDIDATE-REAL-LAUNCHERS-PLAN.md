# Voila Windows ZIP Candidate Real Launchers Plan

Milestone:

```text
v0.3.39-voila-windows-zip-candidate-real-launchers-plan
```

## Purpose

Plan replacement of placeholder Windows package launchers with real launchers for the Voila Windows ZIP candidate.

This milestone is documentation/release planning only.

It does not:

```text
implement launchers
run START-VOILA.bat
run STOP-VOILA.bat
change runtime files
change backend behavior
change frontend behavior
change dependencies
create a ZIP
create an installer
publish a GitHub release
upload release assets
change GitHub visibility
add payment or activation
provide final legal approval
```

---

## Background

The START/STOP smoke test completed in:

```text
v0.3.38-voila-windows-zip-candidate-start-stop-smoke
```

Result:

```text
CONDITIONAL
```

Reason:

```text
START/STOP launchers executed successfully, but they appear to be placeholders.
No local service response was expected.
```

Therefore, the next packaging risk is clear:

```text
replace placeholder launchers with real Windows package launchers
```

---

## Target launchers

Required package files:

```text
START-VOILA.bat
STOP-VOILA.bat
```

Optional supporting scripts:

```text
scripts/start-voila.ps1
scripts/stop-voila.ps1
scripts/check-voila-health.ps1
```

The exact structure should be chosen before implementation.

---

## Required START behavior

`START-VOILA.bat` should:

```text
start required local dependencies
start LanguageTool if bundled
start Voila backend/API service
start frontend/UI if separate
avoid requiring developer tools
avoid requiring global Python/Node/Java when bundled runtime exists
write useful logs
return clear exit code
```

Expected ports:

```text
Voila local service: 8787
LanguageTool: 8081
```

If actual ports differ, README and release notes must be updated.

---

## Required STOP behavior

`STOP-VOILA.bat` should:

```text
stop Voila local service
stop LanguageTool if started by package
release ports
avoid killing unrelated user processes
handle already-stopped state safely
write useful logs
return clear exit code
```

STOP must be conservative. It should not kill unrelated Python/Java processes unless it can identify package-owned processes.

---

## Process ownership strategy

Recommended approach:

```text
write PID files under package-local runtime/logs or runtime/state
use package-local process markers
stop only processes started by START
avoid broad process kills
```

Suggested state folder:

```text
runtime/state/
```

Suggested logs folder:

```text
runtime/logs/
```

Suggested files:

```text
runtime/state/voila-api.pid
runtime/state/languagetool.pid
runtime/logs/voila-api.log
runtime/logs/languagetool.log
```

---

## Required package assumptions

The real launchers must define whether the package includes:

```text
embedded Python runtime
embedded Java runtime
LanguageTool server files
Tesseract/OCR runtime files
frontend static files
backend service entrypoint
```

The launcher implementation must not assume developer machine paths such as:

```text
D:\dev\projects\voila
```

It must use package-relative paths.

---

## Candidate package-relative layout

Potential package layout:

```text
voila/
  START-VOILA.bat
  STOP-VOILA.bat
  README-WINDOWS.txt
  RELEASE-NOTES.txt
  legal/
  app/
  runtime/
    python/
    java/
    tesseract/
    languagetool/
    state/
    logs/
  scripts/
    start-voila.ps1
    stop-voila.ps1
```

This is a planning layout and may be adjusted during implementation.

---

## START health check

After START, the launcher or smoke script should verify:

```text
http://127.0.0.1:8787
```

If a dedicated health endpoint exists, prefer:

```text
http://127.0.0.1:8787/health
```

The chosen endpoint must be documented.

---

## Required smoke criteria after implementation

After real launchers are implemented, the smoke test should pass:

```text
SHA256 verified: PASS
START exit code: 0
Voila service responds: PASS
LanguageTool service responds if expected: PASS
STOP exit code: 0
ports released after STOP: PASS
no orphaned package-owned processes: PASS
```

---

## Failure modes to handle

START should handle:

```text
port already in use
missing runtime files
missing Java
missing Python
LanguageTool startup failure
Voila backend startup failure
timeout waiting for service
```

STOP should handle:

```text
missing PID files
stale PID files
already-stopped service
partial cleanup
port still in use
```

---

## Documentation updates required after implementation

Update:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
docs/legal package workflow docs
START/STOP smoke result docs
```

The docs must clearly state whether the package is runnable or still candidate-only.

---

## Out of scope

This milestone does not implement launchers.

It only plans real launcher requirements and validation gates.

---

## Recommended next milestone

After this plan:

```text
v0.3.40-voila-windows-zip-candidate-real-launchers
```

That milestone should implement or stage real launchers, then a later milestone should rebuild ZIP and repeat START/STOP smoke validation.
