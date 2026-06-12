# Voila Complete Runtime START Launcher Return-Control Fix Implementation Notes

Milestone:

```text
v0.3.59-voila-complete-runtime-start-launcher-return-control-fix
```

## Purpose

Implement the return-control fix planned in v0.3.58.

## Scope

```text
Release/package launcher generator implementation only.
No backend behavior changes.
No frontend behavior changes.
No dependency changes.
No runtime source committed to repository.
No package rebuild.
No ZIP creation.
No installer creation.
No START/STOP execution.
No GitHub visibility change.
No payment/licensing implementation.
No GitHub release publication.
No final legal guarantee.
```

## Implemented change

The helper generator:

```text
scripts/release/create-complete-windows-runtime-source.ps1
```

now generates a START launcher that:

```text
starts the package-local API as a detached/background process
uses package-local .venv/Scripts/python.exe
runs uvicorn web_app:app with --app-dir .\services\api
uses Python -B to avoid bytecode cache creation
writes runtime/state/voila-api.pid
uses a bounded startup window
returns control after startup appears successful
returns non-zero on missing files, occupied port, early exit, or timeout
```

## Start command alignment

The generated command remains aligned to:

```powershell
.\.venv\Scripts\python.exe -B -m uvicorn web_app:app --app-dir .\services\api --host 127.0.0.1 --port 8787
```

## STOP behavior

STOP remains package-owned and PID-based:

```text
runtime/state/voila-api.pid
runtime/state/languagetool.pid
```

No broad process killing is introduced.

## Next milestone

Recommended next milestone:

```text
v0.3.60-voila-complete-runtime-start-launcher-return-control-helper-smoke
```

That milestone should generate a runtime source and verify that START returns control, service responds, and STOP cleans up.
