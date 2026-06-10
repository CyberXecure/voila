# Voila Windows Package Real Launchers Helper Smoke Test

Milestone:

```text
v0.3.41-voila-windows-package-real-launchers-helper-smoke
```

## Purpose

Smoke test `scripts/release/create-windows-package-launchers.ps1` in a temporary package staging folder.

## Scope

```text
Release/package launcher helper smoke test only.
No runtime changes.
No backend changes.
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

## Smoke setup

The smoke test used a temporary package root outside the repository.

The helper was run with:

```powershell
.\scripts\release\create-windows-package-launchers.ps1 `
  -PackageRoot <temporary-package-root> `
  -Force
```

## Result

```text
real launchers helper execution: PASS
START-VOILA.bat generated: PASS
STOP-VOILA.bat generated: PASS
scripts/start-voila.ps1 generated: PASS
scripts/stop-voila.ps1 generated: PASS
scripts/check-voila-health.ps1 generated: PASS
runtime/state created: PASS
runtime/logs created: PASS
package-relative content check: PASS
unsafe repository root rejection: PASS
no START/STOP execution: PASS
no ZIP created: PASS
no installer created: PASS
```

## Generated files verified

```text
START-VOILA.bat
STOP-VOILA.bat
scripts/start-voila.ps1
scripts/stop-voila.ps1
scripts/check-voila-health.ps1
runtime/state/
runtime/logs/
```

## Notes

This milestone validates launcher helper generation only.

A later milestone should integrate generated launchers into package staging, rebuild the ZIP candidate, and rerun START/STOP smoke.
