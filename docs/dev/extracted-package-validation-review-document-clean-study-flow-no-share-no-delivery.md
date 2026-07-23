# v0.8.62 Extracted package validation with Review Document + Clean Study flow — no share/no delivery

## Purpose

This milestone validates the v0.8.61 owner-local ZIP package after extraction.

It does not rebuild the package.

It does not create a new ZIP.

It does not copy anything to OneDrive.

It does not share anything.

It does not deliver anything.

## Source package

Validated ZIP:

`D:\dev\release-assets\voila\v0.8.61-package-rebuild-with-review-document-clean-study-flow-no-share-no-delivery\voila-v0.8.61-controlled-tester-windows-package-candidate.zip`

Expected SHA256:

`1f46f26ca4e5cbc357450d568428d1a9c595a4356c2523c2eb67442774979ff7`

## Extraction target

The package is extracted outside the repository under:

`D:\dev\tester-runs\v0862pkg`

## Local validation fixture

Because the v0.8.61 ZIP is created from tracked repository files only, runtime course data is not expected to be inside the ZIP.

For this owner-local extracted-package validation only, the check copies the existing local test PDF and existing local output artifacts into the extracted package under data/input and data/output.

This seed is local test setup only.

It does not modify the repository.

It does not rebuild the ZIP.

It does not add runtime data to the package source.

It does not share or deliver anything.

## Validation path

The extracted package validation checks:

1. ZIP exists.
2. ZIP SHA256 matches v0.8.61 final-main evidence.
3. ZIP is extracted outside the repository.
4. Extracted package includes `scripts/dev/start-voila-packaged.ps1`.
5. Extracted package includes `services/api/web_app.py`.
6. Extracted package includes v0.8.50–v0.8.57 implementation markers.
7. Extracted package includes v0.8.58, v0.8.59, and v0.8.60 validation scripts.
8. Extracted package excludes `.git`, `.venv`, `__pycache__`, `node_modules`, and `.pyc`.
9. App starts from extracted package.
10. Browser/HTML flow works:
   - Course Tools
   - Revizuire document
   - Draft explicație form via GET only
   - Study curat — previzualizare
11. No POST is called.
12. No new draft is created.
13. No Study cards are created.
14. No Progress is written.
15. No share or delivery is performed.

## Windows cleanup lock fix

The validation stops any running local Voila process before removing the previous extracted package folder.

This avoids Windows file locks from a previously started packaged .venv, for example locked .pyd files.

This is validation cleanup only.

It does not modify application behavior.

It does not rebuild the ZIP.

It does not create a new ZIP.

## Policy

Owner-local extracted package validation only.

No rebuild.

No new ZIP.

No OneDrive copy.

No share.

No delivery.

No distribution.

No public release.

## Recommended next

v0.8.63 — final no-delivery package validation review, owner-local only.
