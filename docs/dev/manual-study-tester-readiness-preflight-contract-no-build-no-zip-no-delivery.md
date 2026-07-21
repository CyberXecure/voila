# v0.8.31 Manual Study tester readiness preflight contract — no build/no ZIP/no delivery

## Purpose

This milestone records the preflight contract before any tester readiness claim, package rebuild, ZIP creation, share, or delivery.

It follows:

- v0.8.27 Manual Study default `/study` read-only fallback
- v0.8.28 Manual Study default Study browser readiness audit
- v0.8.29 Course Tools normal Study link → default Manual Study audit
- v0.8.30 Full Manual Study flow readiness audit

## Owner-local readiness already confirmed

The following owner-local Manual Study flow is confirmed:

- Course Tools loads.
- Course Tools normal Study link opens `/study?pdf={pdf_name}`.
- Normal Study renders Manual Study by default when `manual_study_items.preview.json` exists and contains items.
- Manual Study cards are visible.
- Answers remain read-only inside `<details>`.
- Source metadata remains visible.
- Course Tools explicit Manual Study shadow link remains available.
- The shadow route opens `/study?manual_study_shadow=1&course_id={course_id}`.
- Course Tools dry-run link remains available.
- The dry-run route opens separately.
- Normal Study falls back to legacy Study when `manual_study_items.preview.json` is missing, invalid, or empty.
- Legacy `study_items.preview.json` remains unchanged.
- No Progress write is added.
- No answer marking is added.
- No Study artifact is written.
- No Course generation behavior changes.
- No OCR rewrite happens.
- No Formula OCR happens.

## Tester readiness contract

Tester readiness is not approved by this milestone.

Before any tester package, a future separate tester-readiness milestone must validate:

1. Upload or existing generated course opens in the tester UI path.
2. Course Tools is reachable from the normal tester navigation.
3. Normal Study link from Course Tools opens Manual Study default.
4. Manual Study default shows readable cards.
5. Answers remain read-only.
6. Source metadata is visible.
7. Shadow link remains available for owner-local diagnostics.
8. Dry-run link remains separate.
9. Legacy fallback works when `manual_study_items.preview.json` is missing, invalid, or empty.
10. `study_items.preview.json` is not overwritten.
11. No Progress write is introduced.
12. No answer marking is introduced.
13. No new Study POST endpoint is introduced.
14. No OCR rewrite is introduced.
15. No Formula OCR is introduced.
16. No crop file write is introduced.
17. No build or ZIP is created during the readiness milestone.

## Package readiness blockers

Tester package remains blocked until all of these are completed separately:

- full tester-flow readiness milestone;
- package rebuild milestone;
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

It does not build.

It does not create a ZIP.

It does not create a share.

It does not deliver anything.

It does not distribute anything.

## Result policy

Manual Study has owner-local readiness evidence.

Tester readiness remains blocked by this milestone.

A separate explicit tester-readiness milestone is required next.

A separate explicit package rebuild milestone is required after tester readiness passes.

A separate explicit extracted-package validation milestone is required after package rebuild.

Delivery remains blocked until explicit owner approval.

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
