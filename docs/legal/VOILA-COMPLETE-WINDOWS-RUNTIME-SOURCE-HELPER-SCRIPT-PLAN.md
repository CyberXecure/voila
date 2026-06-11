# Voila Complete Windows Runtime Source Helper Script Plan

Milestone:

```text
v0.3.51-voila-complete-windows-runtime-source-helper-script-plan
```

## Purpose

Plan the actual helper script that will create a complete Windows runtime source for Voila.

Future helper:

```text
scripts/release/create-complete-windows-runtime-source.ps1
```

This milestone is documentation/release helper-script planning only.

It does not:

```text
implement the helper
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

The complete runtime implementation plan completed in:

```text
v0.3.50-voila-windows-package-complete-runtime-source-implementation-plan
```

Confirmed main Voila API entrypoint:

```text
services/api/web_app.py
```

Required start command pattern:

```powershell
.\.venv\Scripts\python.exe -m uvicorn web_app:app --app-dir .\services\api --host 127.0.0.1 --port 8787
```

The v0.3.46 START/STOP smoke was CONDITIONAL because the ZIP candidate did not include the complete runtime/API entrypoint.

---

## Helper goal

The helper must create a complete local runtime source folder:

```text
<RuntimeSourceRoot>\voila
```

that is ready to be passed to:

```text
scripts/release/build-windows-zip-candidate.ps1
```

The produced runtime source should include:

```text
services/api/web_app.py
required services/api modules
package-local Python strategy
README-WINDOWS.txt
RELEASE-NOTES.txt
real launchers
runtime/state/
runtime/logs/
RUNTIME-SOURCE-SUMMARY.txt
```

Legal files remain copied later by the ZIP/package build helper.

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

---

## Proposed parameters

```powershell
param(
  [Parameter(Mandatory = $true)]
  [string] $RuntimeSourceRoot,

  [ValidateSet("PackageVenv", "EmbeddedPython", "GlobalPython")]
  [string] $PythonStrategy = "PackageVenv",

  [switch] $IncludeCropEditor,

  [ValidateSet("Bundled", "Deferred")]
  [string] $LanguageToolStrategy = "Deferred",

  [ValidateSet("Bundled", "Deferred")]
  [string] $OcrStrategy = "Deferred",

  [switch] $Force
)
```

---

## Required implementation behavior

The helper should perform these phases:

```text
1. sync-independent local validation
2. resolve repository root
3. validate source files
4. validate target safety
5. create clean target runtime source
6. copy package docs
7. copy services/api runtime files
8. copy package-local Python/.venv if selected
9. generate real launchers
10. validate launcher alignment
11. validate runtime imports
12. scan forbidden files
13. write RUNTIME-SOURCE-SUMMARY.txt
```

---

## Source files required

Required source files:

```text
services/api/web_app.py
services/api/requirements.txt
scripts/release/create-windows-package-launchers.ps1
```

Conditional source files:

```text
services/api/crop_editor_app.py
.venv/Scripts/python.exe
runtime/java/
runtime/languagetool/
runtime/tesseract/
runtime/tessdata/
```

---

## Copy behavior

Recommended initial copy behavior:

```text
copy services/api/*.py
copy services/api/requirements.txt
copy package-local .venv/ when PythonStrategy is PackageVenv
generate START/STOP/health launchers
create runtime/state/
create runtime/logs/
write README-WINDOWS.txt
write RELEASE-NOTES.txt
write RUNTIME-SOURCE-SUMMARY.txt
```

Do not copy legal files in this helper. Legal file copy remains responsibility of:

```text
scripts/release/copy-package-legal-files.ps1
```

inside the ZIP build flow.

---

## Launcher alignment

The helper should either:

```text
update create-windows-package-launchers.ps1 before use
```

or verify it already generates a START command equivalent to:

```powershell
python -m uvicorn web_app:app --app-dir .\services\api --host 127.0.0.1 --port 8787
```

If generated launchers still target:

```text
main:app
```

then complete runtime START/STOP smoke is expected to fail or remain CONDITIONAL.

---

## Runtime import validation

From the target runtime source root:

```powershell
Push-Location <RuntimeSourceRoot>\voila
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, r'.\services\api'); import fastapi, uvicorn, web_app; print('OK')"
Pop-Location
```

Expected:

```text
OK
```

Failure means the runtime source is not ready for ZIP build.

---

## Forbidden copy validation

The helper must fail if target runtime source includes:

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

## Runtime source summary

The helper should create:

```text
RUNTIME-SOURCE-SUMMARY.txt
```

with:

```text
source commit
source branch
created timestamp
runtime source root
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

## Non-goals

This helper must not:

```text
create a ZIP
copy legal files
create an installer
run START/STOP
publish a release
install dependencies from the internet
modify source repository files
change GitHub visibility
```

---

## Recommended next milestone

```text
v0.3.52-voila-complete-windows-runtime-source-helper
```

That milestone should implement the helper script.
