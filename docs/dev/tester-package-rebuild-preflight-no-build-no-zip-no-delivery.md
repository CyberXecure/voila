# v0.8.33 Tester package rebuild preflight — no build/no ZIP/no delivery

## Purpose

This milestone records the owner-local preflight contract before any tester package rebuild, ZIP creation, share, or delivery.

It follows:

- v0.8.27 Manual Study default `/study` read-only fallback
- v0.8.28 Manual Study default browser readiness audit
- v0.8.29 Course Tools normal Study link → default Manual Study audit
- v0.8.30 Full Manual Study flow readiness audit
- v0.8.31 Manual Study tester readiness preflight contract
- v0.8.32 Manual Study full tester-like flow readiness audit from Home UI

## Current readiness baseline

The current owner-local tester-like flow is ready for package rebuild planning only:

- Home page loads.
- Existing generated course is present.
- Home UI exposes Course Tools for the existing course.
- Course Tools loads from the Home UI link.
- Course Tools exposes the normal Study link to `/study?pdf={pdf_name}`.
- Normal Study renders Manual Study by default when `manual_study_items.preview.json` exists and contains items.
- Manual Study default shows readable cards.
- Answers remain read-only inside `<details>`.
- Source metadata remains visible.
- Course Tools still exposes the explicit Manual Study shadow link.
- The shadow route remains separate and loads.
- Course Tools still exposes the separate dry-run link.
- The dry-run route remains separate and loads.
- Normal Study falls back to legacy Study when `manual_study_items.preview.json` is missing, invalid, or empty.
- Legacy `study_items.preview.json` remains unchanged.
- No Progress write is introduced.
- No answer marking is introduced.
- No Study POST endpoint is introduced.
- No OCR rewrite is introduced.
- No Formula OCR is introduced.
- No crop file write is introduced.

## Future package rebuild inclusion contract

A future separate package rebuild milestone must include the current `main` state after v0.8.32 and must preserve:

1. Manual Study default on the normal `/study?pdf={pdf_name}` path.
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

## Future package rebuild output contract

A future separate package rebuild milestone may create local package artifacts only after explicit approval for that milestone.

The future package rebuild must record:

- package candidate path;
- package SHA256;
- source commit used;
- included Manual Study readiness markers;
- no public release;
- no share;
- no delivery;
- no distribution.

## Remaining blockers

Package readiness remains blocked until all of these are completed separately:

- explicit package rebuild milestone;
- extracted-package browser validation milestone;
- final no-delivery review milestone;
- explicit owner approval before any share or delivery.

## Boundary

This milestone is preflight/docs/check only.

It does not modify `services/api/web_app.py`.

It does not add a route.

It does not add a POST endpoint.

It does not change Course Tools implementation.

It does not change the default Study implementation.

It does not write progress.

It does not mark answers.

It does not overwrite or modify the legacy `study_items.preview.json`.

It does not write a new Study artifact.

It does not change Course, Progress, OCR, or Formula OCR.

It does not run a build.

It does not create a ZIP.

It does not create a share.

It does not deliver anything.

It does not distribute anything.

## Result policy

Package rebuild is not approved by this milestone.

ZIP creation is not approved by this milestone.

Share and delivery remain blocked.

A separate explicit package rebuild milestone is required next if the owner approves it.

A separate explicit extracted-package validation milestone is required after package rebuild.

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
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.
