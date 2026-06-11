# Voila Windows Package Complete Runtime Source Implementation Plan

Milestone:

```text
v0.3.50-voila-windows-package-complete-runtime-source-implementation-plan
```

## Purpose

Plan the implementation of a release helper that creates a complete Windows runtime source for Voila.

This milestone is documentation/release implementation planning only.

It does not:

```text
copy runtime files
create a runtime source
change launcher behavior
change backend behavior
change frontend behavior
change dependencies
create package staging
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

The complete runtime source copy map plan completed in:

```text
v0.3.49-voila-windows-package-complete-runtime-source-copy-map-plan
```

Confirmed main Voila API entrypoint:

```text
services/api/web_app.py
```

Confirmed start command pattern:

```powershell
.\.venv\Scripts\python.exe -m uvicorn web_app:app --app-dir .\services\api --host 127.0.0.1 --port 8787
```

Separate crop editor:

```text
services/api/crop_editor_app.py
port 8790
```

Main blocker from v0.3.46:

```text
real launchers executed but Voila API entrypoint was not found inside the package
```

---

## Implementation target

Add a future release helper:

```text
scripts/release/create-complete-windows-runtime-source.ps1
```

The helper should create a safe complete runtime source folder:

```text
<RuntimeSourceRoot>\voila
```

from the repository, using the v0.3.49 copy map.

---

## Proposed helper responsibilities

The helper should:

```text
1. accept RuntimeSourceRoot
2. reject unsafe target paths
3. clean or create the target runtime source
4. copy required package docs
5. copy services/api runtime files
6. copy package-local .venv if selected
7. generate real launchers
8. validate launcher alignment with web_app:app
9. validate Python imports
10. validate no forbidden files copied
11. write a runtime source summary
```

---

## Proposed command

```powershell
.\scripts\release\create-complete-windows-runtime-source.ps1 `
  -RuntimeSourceRoot <runtime-source-root> `
  -PythonStrategy PackageVenv `
  -IncludeCropEditor `
  -LanguageToolStrategy Deferred `
  -OcrStrategy Deferred `
  -Force
```

Initial strategy:

```text
PythonStrategy: PackageVenv
IncludeCropEditor: true
LanguageToolStrategy: Deferred unless existing packaged runtime is available
OcrStrategy: Deferred unless existing packaged runtime is available
```

---

## Runtime source target layout

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
  .venv/
    Scripts/
      python.exe
  scripts/
    start-voila.ps1
    stop-voila.ps1
    check-voila-health.ps1
  runtime/
    state/
    logs/
  legal/              copied later by ZIP build helper
```

If LanguageTool is included later:

```text
runtime/java/
runtime/languagetool/
```

If OCR is included later:

```text
runtime/tesseract/
runtime/tessdata/
```

---

## Launcher alignment requirement

The existing real launcher helper must be aligned with the discovered main entrypoint.

Required launcher start behavior:

```powershell
python -m uvicorn web_app:app --app-dir .\services\api --host 127.0.0.1 --port 8787
```

If the helper still starts:

```powershell
python -m uvicorn main:app
```

then the implementation must update:

```text
scripts/release/create-windows-package-launchers.ps1
```

before expecting START/STOP smoke PASS.

---

## Runtime validation requirements

The future helper should validate:

```text
[ ] services/api/web_app.py exists
[ ] .venv/Scripts/python.exe exists if PackageVenv strategy is selected
[ ] uvicorn import works
[ ] fastapi import works
[ ] web_app import works with services/api as import path
[ ] generated START-VOILA.bat exists
[ ] generated STOP-VOILA.bat exists
[ ] generated scripts/start-voila.ps1 exists
[ ] generated scripts/stop-voila.ps1 exists
[ ] generated scripts/check-voila-health.ps1 exists
[ ] runtime/state exists
[ ] runtime/logs exists
[ ] no forbidden files copied
```

Suggested import validation:

```powershell
Push-Location <runtime-source>\voila
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, r'.\services\api'); import fastapi, uvicorn, web_app; print('OK')"
Pop-Location
```

---

## Safety requirements

The helper must reject target paths that equal or sit inside unsafe roots:

```text
repository root
docs/
scripts/
services/
.git/
```

The helper must not copy:

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
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
local user uploads
logs with personal paths
```

---

## Output summary

The helper should write:

```text
RUNTIME-SOURCE-SUMMARY.txt
```

containing:

```text
source commit
created timestamp
Python strategy
LanguageTool strategy
OCR strategy
API entrypoint
start command
copied file counts
validation result
known limitations
```

---

## Recommended milestone split

Recommended sequence:

```text
v0.3.50 implementation plan
v0.3.51 helper script plan/spec
v0.3.52 create-complete-windows-runtime-source.ps1 implementation
v0.3.53 helper smoke
v0.3.54 ZIP build with complete runtime source
v0.3.55 START/STOP smoke with complete runtime source
```

---

## Acceptance criteria for this plan

This plan is complete when it defines:

```text
helper name
helper inputs
target runtime layout
copy responsibilities
launcher alignment requirement
validation requirements
exclusion rules
output summary
future milestone sequence
```
