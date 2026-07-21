# v0.8.34 Owner-local tester package rebuild — no share/no delivery

## Purpose

This milestone creates a local owner-controlled tester package candidate after the Manual Study tester-like flow passed owner-local readiness.

It follows:

- v0.8.32 Manual Study full tester-like flow readiness audit from Home UI
- v0.8.33 Tester package rebuild preflight

## Package rebuild permission

This milestone may create a local package ZIP.

This milestone may create a SHA256 checksum.

This milestone may create local package manifest and tester notes.

This milestone must not create a share.

This milestone must not copy anything to OneDrive.

This milestone must not deliver anything.

This milestone must not distribute anything.

This milestone must not create a public release.

## Required package contents

The package candidate must include the current application source state and preserve:

1. Manual Study default on `/study?pdf={pdf_name}`.
2. Course Tools normal Study link.
3. Course Tools explicit Manual Study shadow link.
4. Course Tools separate dry-run link.
5. Legacy fallback when `manual_study_items.preview.json` is missing, invalid, or empty.
6. Read-only answers in `<details>`.
7. Source metadata display.
8. Unchanged legacy `study_items.preview.json`.
9. No Progress write.
10. No answer marking.
11. No new Study POST endpoint.
12. No Course generation behavior change.
13. No OCR rewrite.
14. No Formula OCR.
15. No crop file write.

## Required package evidence

The rebuild must record:

- package candidate path;
- package SHA256;
- source commit used;
- package file count;
- included Manual Study readiness markers;
- no public release;
- no share;
- no delivery;
- no distribution.

## Boundary

This milestone may create local files only under `D:\dev\release-assets\voila\v0.8.34-tester-package-rebuild-no-share-no-delivery`.

This milestone does not modify `services/api/web_app.py`.

This milestone does not add a route.

This milestone does not add a POST endpoint.

This milestone does not change Course Tools implementation.

This milestone does not change the default Study implementation.

This milestone does not write progress.

This milestone does not mark answers.

This milestone does not overwrite or modify the legacy `study_items.preview.json`.

This milestone does not create a share.

This milestone does not copy to OneDrive.

This milestone does not deliver anything.

This milestone does not distribute anything.

## Remaining blockers

Package readiness remains blocked until all of these are completed separately:

- extracted-package browser validation milestone;
- final no-delivery review milestone;
- explicit owner approval before any share or delivery.

## Result policy

A local ZIP candidate may exist after this milestone.

That ZIP candidate is not delivered.

That ZIP candidate is not shared.

That ZIP candidate is not a public release.

A separate extracted-package validation milestone is required next.

A separate final no-delivery review milestone is required before any share.

Explicit owner approval is required before any share or delivery.

## Non-goals

- No UI implementation change.
- No new default behavior change.
- No Progress integration.
- No answer scoring.
- No answer persistence.
- No Study artifact write.
- No Course generation change.
- No OCR rewrite.
- No Formula OCR.
- No crop file write.
- No share.
- No OneDrive copy.
- No delivery.
- No distribution.
- No public release.
