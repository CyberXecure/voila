# Voila Windows Package Complete Runtime Source Copy Map Plan

Milestone:

```text
v0.3.49-voila-windows-package-complete-runtime-source-copy-map-plan
```

## Purpose

Turn the v0.3.48 discovery result into a concrete copy map plan for building a complete Windows package runtime source.

This milestone is documentation/release planning only.

It does not:

```text
copy runtime files
change launcher behavior
change backend behavior
change frontend behavior
change dependencies
create a package staging folder
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

The complete runtime source discovery completed in:

```text
v0.3.48-voila-windows-package-complete-runtime-source-discovery
```

Confirmed main Voila API entrypoint:

```text
services/api/web_app.py
```

Confirmed main start command pattern:

```powershell
.\.venv\Scripts\python.exe -m uvicorn web_app:app --app-dir .\services\api --host 127.0.0.1 --port 8787
```

Confirmed separate crop editor:

```text
services/api/crop_editor_app.py
port 8790
```

Detected:

```text
requirements.txt
frontend/static references needing packaging strategy review
LanguageTool references
Tesseract/OCR references
```

The next step is to define a concrete runtime-source layout and copy plan.

---

## Target runtime source root

Recommended temporary runtime source root for future implementation:

```text
<runtime-source>\voila
```

Recommended package output root for later ZIP build:

```text
<output-root>
```

The runtime source should remain separate from the repository root.

---

## Required target layout

Planned target layout:

```text
voila/
  README-WINDOWS.txt
  RELEASE-NOTES.txt
  START-VOILA.bat
  STOP-VOILA.bat
  services/
    api/
      web_app.py
      crop_editor_app.py
      requirements.txt
      <required api modules>
  scripts/
    start-voila.ps1
    stop-voila.ps1
    check-voila-health.ps1
  runtime/
    python-or-venv/
    java/
    languagetool/
    tesseract/
    state/
    logs/
  legal/
```

This is a planning layout. The implementation milestone must validate each copied file.

---

## API/backend copy plan

Primary API entrypoint:

```text
source: services/api/web_app.py
target: services/api/web_app.py
```

Startup expectation:

```powershell
python -m uvicorn web_app:app --app-dir .\services\api --host 127.0.0.1 --port 8787
```

Separate crop editor:

```text
source: services/api/crop_editor_app.py
target: services/api/crop_editor_app.py
port: 8790
```

Recommended initial packaging decision:

```text
include crop_editor_app.py as an app module
do not auto-start crop editor unless explicitly required
document crop editor as separate/deferred if not started by START
```

---

## API module copy rule

Copy enough of `services/api/` for `web_app.py` to import successfully.

Recommended initial rule:

```text
copy services/api/*.py
copy services/api/requirements.txt if present
copy required templates/static/assets under services/api if present
```

Do not copy:

```text
__pycache__/
.pytest_cache/
local generated output
user-uploaded private data
developer-only temp files
```

---

## Python runtime/dependency plan

Detected:

```text
requirements.txt
```

Recommended package strategy for next implementation:

```text
Option B first: package-local .venv copied into the runtime source
```

Rationale:

```text
fastest path to local Windows tester candidate
matches existing start command pattern
avoids requiring tester to run pip install
can be replaced later by embedded Python if needed
```

Planned target:

```text
source: .venv/
target: .venv/
```

Validation must prove:

```powershell
.\.venv\Scripts\python.exe -c "import fastapi, uvicorn; import web_app"
```

from package context with:

```powershell
--app-dir .\services\api
```

---

## Frontend/static strategy

Discovery found frontend/static references but packaging strategy needs review.

Recommended initial decision:

```text
do not add new frontend build behavior in this milestone
copy only static assets required by services/api/web_app.py if they are already used at runtime
document missing frontend assets as blocker if imports/routes require them
```

Future implementation must inspect whether `web_app.py` serves:

```text
inline HTML
templates
static assets
prebuilt frontend assets
```

---

## LanguageTool/Java strategy

Discovery found LanguageTool references.

Recommended initial decision:

```text
preserve LanguageTool as required runtime dependency if current local app expects it
use existing packaged Java/LanguageTool strategy if available
otherwise document LanguageTool as deferred for the next ZIP candidate
```

Planned target paths if bundled:

```text
runtime/java/
runtime/languagetool/
```

START expectations must match actual bundled files.

---

## Tesseract/OCR strategy

Discovery found Tesseract/OCR references.

Recommended initial decision:

```text
include OCR runtime only if the existing package/runtime source already has a safe known Tesseract copy path
otherwise document OCR as deferred for the next complete-runtime smoke candidate
```

Planned target paths if bundled:

```text
runtime/tesseract/
runtime/tessdata/
```

---

## Launcher alignment requirement

Current helper must be aligned with the discovered entrypoint.

Current start command in helper must be reviewed against:

```powershell
python -m uvicorn web_app:app --app-dir .\services\api --host 127.0.0.1 --port 8787
```

If current helper still starts:

```powershell
python -m uvicorn main:app
```

then a later implementation must update `create-windows-package-launchers.ps1` before full smoke PASS can be expected.

---

## Exclusion plan

Always exclude:

```text
.git/
.github/
.env
*.pem
*.key
*.pfx
secrets/
private/
.release-cache/
node_modules/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
dist temporary outputs unless intentionally packaged
test-only artifacts
local user uploads
logs with personal paths
```

---

## Required validation before next ZIP build

Before creating the next ZIP candidate, validate:

```text
[ ] services/api/web_app.py exists in runtime source
[ ] services/api/crop_editor_app.py decision documented
[ ] package-local Python strategy implemented
[ ] uvicorn import works
[ ] web_app import works
[ ] launcher start command matches web_app:app
[ ] README-WINDOWS.txt present
[ ] RELEASE-NOTES.txt present
[ ] real launchers generated
[ ] legal files copied by build helper
[ ] package staging validation -Strict PASS
[ ] no forbidden files copied
```

---

## Recommended next milestone

```text
v0.3.50-voila-windows-package-complete-runtime-source-copy-map-implementation-plan
```

That milestone should plan the implementation script/helper that creates the complete runtime source using this copy map.
