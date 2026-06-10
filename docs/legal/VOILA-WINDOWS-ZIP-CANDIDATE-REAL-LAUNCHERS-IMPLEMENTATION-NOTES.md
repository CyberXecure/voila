# Voila Windows ZIP Candidate Real Launchers Implementation Notes

Milestone:

```text
v0.3.40-voila-windows-zip-candidate-real-launchers
```

## Purpose

Add a release/package helper that creates real Windows package launchers:

```text
scripts/release/create-windows-package-launchers.ps1
```

The helper writes launcher files into a selected package root.

## Scope

```text
Release/package launcher helper only.
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

## Generated package files

```text
START-VOILA.bat
STOP-VOILA.bat
scripts/start-voila.ps1
scripts/stop-voila.ps1
scripts/check-voila-health.ps1
runtime/state/
runtime/logs/
```

## Launcher behavior

START behavior:

```text
uses package-relative paths
starts LanguageTool if bundled runtime is present
starts Voila API if Python and API entrypoint are found
writes PID files
writes logs
runs a local health check
prints local URL
```

STOP behavior:

```text
uses package-relative paths
reads PID files
stops package-owned processes only
removes stale PID files
writes logs
treats already-stopped state safely
```

## Safety

The helper rejects unsafe package roots such as:

```text
repository root
docs/
scripts/
```

The generated STOP launcher avoids broad Python/Java process killing.

## Expected follow-up

After this milestone, a future milestone should:

```text
create package staging with real launchers
rebuild ZIP candidate
rerun START/STOP smoke
confirm local service responds
```
