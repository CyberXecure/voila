# Voila Complete Windows Runtime Source Helper Implementation Notes

Milestone:

```text
v0.3.52-voila-complete-windows-runtime-source-helper
```

## Purpose

Implement the complete Windows runtime source helper:

```text
scripts/release/create-complete-windows-runtime-source.ps1
```

## Scope

```text
Release/package helper implementation only.
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

## Implemented behavior

The helper can create a complete runtime source under:

```text
<RuntimeSourceRoot>\voila
```

It supports the initial `PackageVenv` strategy and copies:

```text
services/api runtime files
package-local .venv
README-WINDOWS.txt
RELEASE-NOTES.txt
aligned START/STOP/health launchers
runtime/state/
runtime/logs/
RUNTIME-SOURCE-SUMMARY.txt
```

## API entrypoint alignment

The helper is aligned with the confirmed main API entrypoint:

```text
services/api/web_app.py
```

Required start pattern:

```powershell
python -m uvicorn web_app:app --app-dir .\services\api --host 127.0.0.1 --port 8787
```

## Validation

The helper validates:

```text
safe RuntimeSourceRoot
services/api/web_app.py exists
package-local Python exists when PackageVenv is selected
runtime imports for fastapi, uvicorn, and web_app
launcher alignment for web_app:app and services/api
forbidden file scan
runtime source summary output
```

## Non-goals

The helper does not:

```text
build ZIP
copy legal files
run START/STOP
publish release assets
install dependencies from the internet
modify source runtime behavior
```

## Next milestone

Recommended next milestone:

```text
v0.3.53-voila-complete-windows-runtime-source-helper-smoke
```

That milestone should run the helper in a temporary folder and validate output without creating a ZIP.
