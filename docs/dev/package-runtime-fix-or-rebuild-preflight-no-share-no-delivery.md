# v0.8.36 Package runtime fix/rebuild preflight — no share/no delivery

## Purpose

This milestone records the safe runtime strategy after the v0.8.35 extracted-package blocker.

v0.8.35 confirmed that the v0.8.34 tester ZIP is not self-startable after extraction because:

- the ZIP excludes `.venv`
- `scripts/dev/start-voila.ps1` requires `.venv\Scripts\python.exe`

## Result

This milestone is a preflight/decision milestone only.

It does not rebuild the package.

It does not create a new ZIP.

It does not extract the package.

It does not start the extracted package.

It does not modify `services/api/web_app.py`.

It does not change Study behavior.

It does not copy to OneDrive.

It does not share.

It does not deliver.

It does not distribute.

It does not create a public release.

## Runtime strategies considered

### Option A — include `.venv` in the tester ZIP

Pros:

- package starts closer to the current local owner setup
- no first-run dependency installation

Cons:

- ZIP becomes much larger
- may include unnecessary local files
- must carefully exclude caches, secrets, and machine-specific paths
- less clean for controlled tester distribution

### Option B — add a packaged bootstrap/start script

Pros:

- cleaner package
- can create `.venv` on first run
- can install requirements from tracked files
- can preserve the existing owner-local `start-voila.ps1`
- better for future controlled tester packaging

Cons:

- requires first-run setup
- requires explicit validation that Python is installed
- requires retry of extracted-package browser validation after rebuild

## Recommended direction

Use Option B first.

The next implementation milestone should add a controlled packaged startup path, for example:

`scripts/dev/start-voila-packaged.ps1`

That script should:

1. run only from the extracted package root
2. detect an existing `.venv\Scripts\python.exe`
3. create `.venv` if missing
4. install dependencies from tracked requirements
5. start Voila on `127.0.0.1:8787`
6. preserve no-share/no-delivery boundaries
7. avoid changing `services/api/web_app.py`

After that, a separate rebuild milestone must create a new local ZIP candidate.

After that, extracted-package browser validation must be retried.

## Required chain

1. v0.8.36 — package runtime preflight/decision only
2. v0.8.37 — packaged startup bootstrap implementation, no ZIP
3. v0.8.38 — package rebuild with packaged startup, no share/no delivery
4. v0.8.39 — extracted-package browser validation retry, no share/no delivery
5. final no-delivery review before any owner decision about sharing

## Boundary

No package rebuild.

No new ZIP.

No extraction.

No app behavior change.

No `services/api/web_app.py` change.

No route change.

No Study behavior change.

No Progress write.

No answer marking.

No OCR rewrite.

No Formula OCR.

No crop file write.

No OneDrive copy.

No share.

No delivery.

No distribution.

No public release.

## Policy

Package readiness remains blocked.

Sharing remains blocked.

Delivery remains blocked.

Distribution remains blocked.

Public release remains blocked.
