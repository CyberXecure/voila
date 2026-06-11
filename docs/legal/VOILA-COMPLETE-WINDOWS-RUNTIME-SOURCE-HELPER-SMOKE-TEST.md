# Voila Complete Windows Runtime Source Helper Smoke Test

Milestone:

```text
v0.3.53-voila-complete-windows-runtime-source-helper-smoke
```

## Purpose

Smoke-test the complete Windows runtime source helper in a temporary folder.

## Scope

```text
Release/package helper smoke only.
No backend behavior changes.
No frontend behavior changes.
No dependency changes.
No package rebuild.
No ZIP creation.
No installer creation.
No START/STOP execution.
No GitHub visibility change.
No payment/licensing implementation.
No GitHub release publication.
No final legal guarantee.
```

## Result

```text
helper execution: PASS
runtime source created: PASS
services/api/web_app.py copied: PASS
services/api/crop_editor_app.py copied: PASS
package-local .venv copied: PASS
README-WINDOWS.txt created: PASS
RELEASE-NOTES.txt created: PASS
START-VOILA.bat generated: PASS
STOP-VOILA.bat generated: PASS
scripts/start-voila.ps1 generated: PASS
scripts/stop-voila.ps1 generated: PASS
scripts/check-voila-health.ps1 generated: PASS
RUNTIME-SOURCE-SUMMARY.txt created: PASS
launcher alignment for web_app:app: PASS
import validation fastapi/uvicorn/web_app: PASS
forbidden file scan after cleanup: PASS
no ZIP created: PASS
no SHA256 created: PASS
no EXE/MSI created: PASS
no START/STOP execution: PASS
```

## Helper hardening from smoke

```text
PackageVenv copy was hardened to avoid Copy-Item failures on .venv cache paths.
Python import validation was hardened with -B to avoid bytecode cache creation.
Generated START launcher was hardened to use Python -B.
certifi cacert.pem is allowed as a legitimate dependency certificate file.
.pyc/.pyo and __pycache__ artifacts are still removed/forbidden.
```

## Runtime source command validated

```powershell
.\scripts\release\create-complete-windows-runtime-source.ps1 `
  -RuntimeSourceRoot <temp-runtime-source-root> `
  -PythonStrategy PackageVenv `
  -IncludeCropEditor `
  -LanguageToolStrategy Deferred `
  -OcrStrategy Deferred `
  -Force
```

## Next step

A later milestone should build a ZIP candidate from the generated complete runtime source and then run START/STOP smoke.
