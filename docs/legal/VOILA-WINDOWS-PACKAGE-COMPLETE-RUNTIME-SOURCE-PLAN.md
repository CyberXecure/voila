# Voila Windows Package Complete Runtime Source Plan

Milestone:

```text
v0.3.47-voila-windows-package-complete-runtime-source-plan
```

## Purpose

Plan the move from a structurally valid Windows ZIP candidate with real launchers to a candidate that contains a complete runtime source capable of starting Voila locally.

This milestone is documentation/release planning only.

It does not:

```text
change runtime files
change backend behavior
change frontend behavior
change dependencies
rebuild a package
create a ZIP
create an installer
run START-VOILA.bat
run STOP-VOILA.bat
publish a GitHub release
upload release assets
change GitHub visibility
add payment or activation
provide final legal approval
```

---

## Background

The real launchers START/STOP smoke completed in:

```text
v0.3.46-voila-windows-zip-candidate-real-launchers-start-stop-smoke
```

Result:

```text
CONDITIONAL
```

Reason:

```text
Real launchers executed, but the package runtime is incomplete for a full service start in this candidate.
Voila API entrypoint was not found.
```

Confirmed:

```text
ZIP candidate located: PASS
SHA256 verified: PASS
real launcher files present: PASS
START-VOILA.bat executed: PASS
STOP-VOILA.bat executed: PASS
ports cleaned up: PASS
runtime/API entrypoint missing: BLOCKER
```

Therefore, the next packaging risk is clear:

```text
define and prepare a complete runtime source
```

---

## Goal

Define the required complete runtime source that can be used to rebuild a Windows ZIP candidate that actually starts Voila.

The complete runtime source should contain:

```text
Voila API entrypoint
Python runtime or reliable packaged Python environment
Python dependencies
frontend/static UI assets if required
LanguageTool runtime if expected
Java runtime if LanguageTool is bundled
Tesseract/OCR runtime if OCR is included
package README and release notes
real launchers
legal files copied during package build
```

---

## Required API entrypoint

The current generated launcher searches for one of:

```text
app/api/main.py
api/main.py
backend/main.py
service/main.py
main.py
```

The complete runtime source must either:

```text
include one of these supported entrypoints
```

or a later launcher milestone must explicitly update the supported entrypoint path.

Recommended for next implementation:

```text
choose and document the actual Voila API entrypoint path from the repository
align launcher expectations with that path
```

---

## Required Python runtime

The runtime source must define one supported Python strategy:

```text
Option A: embedded Python runtime included under runtime/python/
Option B: package-local virtual environment under .venv/
Option C: controlled global Python dependency documented for testers
```

Recommended for package reliability:

```text
Option A or Option B
```

Avoid depending on a developer machine Python path.

---

## Required dependency strategy

The package must include or install required Python dependencies in a package-local way.

The plan must identify:

```text
FastAPI / ASGI server dependency
uvicorn dependency
PDF/OCR dependencies
LanguageTool integration dependency if any
static asset serving dependency if any
```

The candidate should not require users to run:

```text
pip install
npm install
poetry install
```

unless explicitly documented as a developer-only package.

---

## Required frontend/static strategy

The runtime source must define whether Voila UI is served by:

```text
FastAPI static files
separate frontend dev server
prebuilt frontend static assets
desktop/webview wrapper
```

For a Windows ZIP tester candidate, recommended direction:

```text
prebuilt static assets served by the local backend
```

if compatible with current architecture.

---

## Required LanguageTool strategy

If LanguageTool is expected in the package, define:

```text
LanguageTool server location
Java runtime location
startup command
health/port check on 8081
logs
PID file
shutdown behavior
```

If LanguageTool is not expected for the next candidate, document it as:

```text
not bundled in this candidate
```

and ensure START/STOP smoke expectations match.

---

## Required OCR/Tesseract strategy

If OCR is expected in the package, define:

```text
Tesseract executable path
traineddata path
environment variables
runtime/log behavior
smoke validation boundary
```

If OCR is deferred, document it clearly.

---

## Proposed complete runtime source layout

Candidate layout:

```text
voila/
  README-WINDOWS.txt
  RELEASE-NOTES.txt
  START-VOILA.bat
  STOP-VOILA.bat
  scripts/
    start-voila.ps1
    stop-voila.ps1
    check-voila-health.ps1
  app/
    api/
      main.py
    static/
    assets/
  runtime/
    python/
    java/
    languagetool/
    tesseract/
    state/
    logs/
  legal/
```

This layout is a planning target and must be adjusted to the actual repository/runtime structure.

---

## Required validation before rebuild

Before another ZIP build, validate the runtime source contains:

```text
[ ] API entrypoint path exists
[ ] Python executable exists or package-local Python strategy is documented
[ ] uvicorn can be resolved by packaged Python
[ ] required app files exist
[ ] START-VOILA.bat generated
[ ] STOP-VOILA.bat generated
[ ] scripts/start-voila.ps1 generated
[ ] scripts/stop-voila.ps1 generated
[ ] scripts/check-voila-health.ps1 generated
[ ] runtime/state exists
[ ] runtime/logs exists
[ ] no secrets
[ ] no developer cache
[ ] no .git folder
[ ] no private data
```

---

## Required future build flow

Recommended future sequence:

```text
1. identify actual API/runtime source from repository
2. create complete runtime source staging
3. generate real launchers
4. run complete-runtime-source validation
5. run build-windows-zip-candidate.ps1
6. verify ZIP/SHA256/extract validation
7. run START/STOP smoke
8. document PASS/CONDITIONAL/FAIL
```

---

## Acceptance criteria

The complete runtime source plan is acceptable when it identifies:

```text
actual API entrypoint
Python runtime/dependency approach
frontend/static approach
LanguageTool/Java decision
Tesseract/OCR decision
package layout
validation checklist
next implementation milestone
```

---

## Recommended next milestone

```text
v0.3.48-voila-windows-package-complete-runtime-source-discovery
```

That milestone should inspect the repository/runtime structure and document the exact files and commands needed for a complete runtime source.
