# Voila Complete Windows Runtime Source Validation Plan

Milestone:

```text
v0.3.50-voila-windows-package-complete-runtime-source-implementation-plan
```

## Validation stages

The future helper should validate in four stages:

```text
source validation
copy validation
runtime import validation
exclusion validation
```

## Source validation

```text
[ ] repository root exists
[ ] services/api/web_app.py exists
[ ] services/api/requirements.txt exists or dependency strategy documented
[ ] .venv/Scripts/python.exe exists when PackageVenv selected
[ ] create-windows-package-launchers.ps1 exists
```

## Copy validation

```text
[ ] target runtime source created
[ ] services/api/web_app.py copied
[ ] required API modules copied
[ ] package-local Python copied if selected
[ ] launcher files generated
[ ] runtime/state created
[ ] runtime/logs created
[ ] README-WINDOWS.txt present
[ ] RELEASE-NOTES.txt present
```

## Import validation

Suggested command from target package root:

```powershell
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, r'.\services\api'); import fastapi, uvicorn, web_app; print('OK')"
```

Required outcome:

```text
OK
```

## Launcher validation

Check that generated `scripts/start-voila.ps1` contains:

```text
web_app:app
--app-dir
services\api
127.0.0.1
8787
```

## Exclusion validation

Fail if target contains:

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
```

## Smoke boundary

This validation plan does not run START/STOP.

START/STOP smoke remains a separate later milestone after ZIP build.
