# Voila Windows Package Complete Runtime Source Packaging Strategy

Milestone:

```text
v0.3.49-voila-windows-package-complete-runtime-source-copy-map-plan
```

## Recommended initial strategy

Use a pragmatic Windows tester candidate strategy:

```text
services/api copied into runtime source
package-local .venv copied into runtime source
real launchers generated into runtime source
legal files copied by build helper
ZIP built by build-windows-zip-candidate.ps1
START/STOP smoke rerun
```

## Why .venv first

```text
fastest path to complete local runtime
matches discovered start command
reduces new packaging logic
can be hardened later
```

## Known risk

Copying `.venv/` can make the package larger and more environment-coupled.

Mitigation:

```text
validate on clean Windows machine
later replace with embedded Python/runtime packaging if needed
```

## Launcher update requirement

The launcher helper should support:

```powershell
python -m uvicorn web_app:app --app-dir .\services\api --host 127.0.0.1 --port 8787
```

If it only supports `main:app`, update it before expecting START smoke PASS.

## Next implementation direction

A later script should:

```text
create clean runtime source
copy services/api
copy package-local Python/.venv
generate launchers
validate imports
validate package staging
build ZIP
run START/STOP smoke
```
