# v0.8.61 Package rebuild with Review Document + Clean Study flow — no share/no delivery

## Purpose

This milestone performs an owner-local package rebuild after the v0.8.60 preflight passed.

This milestone is explicitly approved for local package rebuild and ZIP creation only.

It does not copy anything to OneDrive.

It does not share anything.

It does not deliver anything.

## Included validated workflow

The rebuilt owner-local package includes the learner workflow validated through v0.8.60:

- Course Tools
- Revizuire document
- Text detectat
- Corecturi sugerate
- Formule și imagini
- Explicație prietenoasă
- Draft explicație local
- Study curat — previzualizare

## Package output

The local package candidate is written outside the repo under:

`D:\dev\release-assets\voila\v0.8.61-package-rebuild-with-review-document-clean-study-flow-no-share-no-delivery`

Expected ZIP name:

`voila-v0.8.61-controlled-tester-windows-package-candidate.zip`

## Package source rule

The ZIP is created from tracked repository files only.

Local untracked runtime/test data is not added to the package.

The package must not include:

- `.git`
- `.venv`
- `__pycache__`
- `.pytest_cache`
- `.mypy_cache`
- `node_modules`
- `.pyc` files

## Required package content

The package must include:

- `scripts/dev/start-voila-packaged.ps1`
- `services/api/web_app.py`
- v0.8.50–v0.8.57 learner workflow implementation markers
- v0.8.58 learner workflow UI smoke script
- v0.8.59 UI readability pass script
- v0.8.60 package rebuild preflight script

## Explicit non-goals

This milestone does not create a GitHub release.

This milestone does not create a public release.

This milestone does not copy the ZIP to OneDrive.

This milestone does not create or modify a share link.

This milestone does not contact testers.

This milestone does not perform delivery.

## Policy

Owner-local package rebuild allowed.

ZIP creation allowed.

No OneDrive copy.

No share.

No delivery.

No distribution.

No public release.

## Recommended next

v0.8.62 — extracted package validation, owner-local only, no share/no delivery.

