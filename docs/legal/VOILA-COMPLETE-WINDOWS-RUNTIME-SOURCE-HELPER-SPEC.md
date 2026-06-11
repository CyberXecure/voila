# Voila Complete Windows Runtime Source Helper Specification

Milestone:

```text
v0.3.50-voila-windows-package-complete-runtime-source-implementation-plan
```

## Proposed helper

```text
scripts/release/create-complete-windows-runtime-source.ps1
```

## Parameters

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

## Required behavior

```text
[ ] resolve repository root
[ ] resolve RuntimeSourceRoot
[ ] reject unsafe RuntimeSourceRoot
[ ] create <RuntimeSourceRoot>\voila
[ ] copy README-WINDOWS.txt
[ ] copy RELEASE-NOTES.txt
[ ] copy services/api runtime files
[ ] copy services/api/requirements.txt if present
[ ] copy .venv when PythonStrategy is PackageVenv
[ ] optionally include crop_editor_app.py
[ ] generate real launchers
[ ] validate launcher start command
[ ] validate imports
[ ] validate exclusions
[ ] write RUNTIME-SOURCE-SUMMARY.txt
```

## Required start command

```powershell
.\.venv\Scripts\python.exe -m uvicorn web_app:app --app-dir .\services\api --host 127.0.0.1 --port 8787
```

## Required target files

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
services/api/web_app.py
services/api/requirements.txt
.venv/Scripts/python.exe
START-VOILA.bat
STOP-VOILA.bat
scripts/start-voila.ps1
scripts/stop-voila.ps1
scripts/check-voila-health.ps1
runtime/state/
runtime/logs/
RUNTIME-SOURCE-SUMMARY.txt
```

## Optional target files

```text
services/api/crop_editor_app.py
runtime/java/
runtime/languagetool/
runtime/tesseract/
runtime/tessdata/
```

## Failure behavior

The helper must stop with non-zero exit if:

```text
RuntimeSourceRoot is unsafe
services/api/web_app.py missing
selected Python strategy cannot be satisfied
uvicorn import fails
web_app import fails
launcher generation fails
forbidden files are detected
```

## Non-goals

The helper must not:

```text
build ZIP
copy legal files
publish release
run START/STOP
install dependencies from internet
modify source repository files
```
