# v0.8.37 Packaged startup bootstrap — no build/no ZIP/no share/no delivery

## Purpose

This milestone adds a controlled startup script for future extracted tester packages.

It follows the v0.8.35 blocker and the v0.8.36 runtime strategy preflight.

v0.8.35 confirmed that the v0.8.34 tester ZIP is not self-startable after extraction because:

- the package excludes `.venv`
- `scripts/dev/start-voila.ps1` requires `.venv\Scripts\python.exe`

v0.8.36 selected Option B:

- add a packaged bootstrap/start script first
- rebuild the package only in a later separate milestone
- retry extracted-package browser validation only after that rebuild

## Added script

This milestone adds:

`scripts/dev/start-voila-packaged.ps1`

The script is intended for future extracted package roots.

It can:

1. resolve the package root from its own script location
2. detect `.venv\Scripts\python.exe`
3. create `.venv` if missing
4. install dependencies from tracked requirement files when available
5. start Voila on `127.0.0.1:8787`
6. support `-CheckOnly` so validation can inspect behavior without creating a venv or starting servers

## Boundary

This milestone does not rebuild the package.

This milestone does not create a new ZIP.

This milestone does not extract the package.

This milestone does not start the extracted package.

This milestone does not modify `services/api/web_app.py`.

This milestone does not add a route.

This milestone does not add a POST endpoint.

This milestone does not change Study behavior.

This milestone does not write Progress.

This milestone does not mark answers.

This milestone does not perform OCR rewrite.

This milestone does not perform Formula OCR.

This milestone does not write crop files.

This milestone does not copy to OneDrive.

This milestone does not create a share.

This milestone does not deliver anything.

This milestone does not distribute anything.

This milestone does not create a public release.

## Required next steps

1. v0.8.38 — rebuild local tester ZIP with `start-voila-packaged.ps1`, no share/no delivery
2. v0.8.39 — retry extracted-package browser validation, no share/no delivery
3. final no-delivery review before any owner decision about sharing

## Policy

Package readiness remains blocked until rebuild and extracted-package validation pass.

Sharing remains blocked.

Delivery remains blocked.

Distribution remains blocked.

Public release remains blocked.
