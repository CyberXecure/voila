# Voila Complete Windows Runtime Source Helper Script Test Plan

Milestone:

```text
v0.3.51-voila-complete-windows-runtime-source-helper-script-plan
```

## Purpose

Define the test plan for the future complete runtime source helper implementation.

## Smoke test

Create a runtime source in a temporary folder:

```powershell
.\scripts\release\create-complete-windows-runtime-source.ps1 `
  -RuntimeSourceRoot <temp-root> `
  -PythonStrategy PackageVenv `
  -Force
```

Expected:

```text
helper exits 0
target root created
services/api/web_app.py copied
.venv/Scripts/python.exe available
real launchers generated
RUNTIME-SOURCE-SUMMARY.txt created
validation PASS
```

## Import validation test

From target package root:

```powershell
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, r'.\services\api'); import fastapi, uvicorn, web_app; print('OK')"
```

Expected:

```text
OK
```

## Launcher alignment test

Generated `scripts/start-voila.ps1` must include:

```text
web_app:app
--app-dir
services\api
127.0.0.1
8787
```

## Unsafe target tests

The helper must reject:

```text
repository root
docs/
scripts/
services/
.git/
```

## Forbidden file tests

The helper must fail if target includes:

```text
.env
*.pem
*.key
*.pfx
.git/
.github/
.release-cache/
```

## Non-goal tests

The helper smoke must verify:

```text
no ZIP created
no EXE/MSI created
no START/STOP executed
no legal files copied by this helper unless explicitly added later
no GitHub release created
```

## Future integration test

After helper smoke passes, a later milestone should:

```text
run build-windows-zip-candidate.ps1 with the generated runtime source
verify ZIP/SHA256/extract validation
run START/STOP smoke
```
