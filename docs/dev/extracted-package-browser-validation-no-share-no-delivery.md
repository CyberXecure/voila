# v0.8.35 Extracted package browser validation BLOCKED — no share/no delivery

## Purpose

This milestone records the owner-local extracted-package browser validation blocker for the v0.8.34 tester ZIP candidate.

## Result

Extracted-package browser validation is blocked.

The extracted package cannot be started by `scripts/dev/start-voila.ps1` because the package does not contain the required local Python virtual environment:

`.venv\Scripts\python.exe`

The start script expects that venv and fails with:

`Nu gasesc Python venv: ...\.venv\Scripts\python.exe`

## Root cause

The v0.8.34 package rebuild copied tracked repository files and intentionally excluded `.venv`.

However, the packaged `scripts/dev/start-voila.ps1` still requires `.venv\Scripts\python.exe`.

Therefore the ZIP is not self-startable after extraction.

## Confirmed package state

The package exists.

The package SHA256 file matches.

The ZIP contains app source, start/stop scripts, policy notes, and Manual Study markers.

The ZIP does not contain the required venv runtime.

## Boundary

This milestone records blocker evidence only.

It does not extract the package.

It does not start the extracted package.

It does not modify `services/api/web_app.py`.

It does not add a route.

It does not add a POST endpoint.

It does not rebuild the ZIP.

It does not create a new ZIP.

It does not copy to OneDrive.

It does not create a share.

It does not deliver anything.

It does not distribute anything.

It does not create a public release.

## Required next step

A separate package runtime fix/rebuild milestone is required before extracted-package browser validation can pass.

That future milestone must make the package self-startable after extraction by either:

- including the required local runtime/venv in the package; or
- changing packaged startup/bootstrap behavior in a controlled way.

## Policy

No share.

No OneDrive copy.

No delivery.

No distribution.

No public release.
