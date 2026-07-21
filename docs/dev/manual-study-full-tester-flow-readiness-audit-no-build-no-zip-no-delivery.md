# v0.8.32 Manual Study full tester-flow readiness audit — no build/no ZIP/no delivery

## Purpose

This milestone records the owner-local full tester-flow readiness audit for Manual Study before any package rebuild, ZIP creation, share, or delivery.

It follows:

- v0.8.27 Manual Study default `/study` read-only fallback
- v0.8.28 Manual Study default browser readiness audit
- v0.8.29 Course Tools normal Study link → default Manual Study audit
- v0.8.30 Full Manual Study flow readiness audit
- v0.8.31 Manual Study tester readiness preflight contract

## Audited tester-like flow

This audit starts from the normal local UI and follows the user-facing route chain:

1. Home page loads with HTTP 200.
2. Existing generated course is present.
3. Home UI exposes the Course Tools entry for the existing course.
4. Course Tools loads from the Home UI link with HTTP 200.
5. Course Tools exposes the normal Study link to `/study?pdf={pdf_name}`.
6. The normal Study link opens `/study?pdf={pdf_name}` with HTTP 200.
7. Normal Study renders Manual Study by default when `manual_study_items.preview.json` exists and contains items.
8. Manual Study default shows readable cards.
9. Answers remain read-only inside `<details>`.
10. Source metadata remains visible.
11. Course Tools still exposes the explicit Manual Study shadow link.
12. The shadow route remains separate and loads with HTTP 200.
13. Course Tools still exposes the separate dry-run link.
14. The dry-run route remains separate and loads with HTTP 200.
15. Normal Study falls back to legacy Study when `manual_study_items.preview.json` is temporarily missing.
16. Legacy `study_items.preview.json` remains unchanged.
17. No Progress write is introduced.
18. No answer marking is introduced.
19. No Study POST endpoint is introduced.
20. No Course generation behavior changes.
21. No OCR rewrite happens.
22. No Formula OCR happens.
23. No crop file write happens.
24. No build is performed.
25. No ZIP is created.
26. No share is created.
27. No delivery is performed.
28. No distribution is performed.

## Readiness interpretation

This milestone can mark the owner-local Manual Study tester-like flow as ready.

It does not approve a tester package.

A separate package rebuild milestone is still required.

A separate extracted-package validation milestone is still required.

A separate final no-delivery review milestone is still required before any share.

Explicit owner approval is required before any share or delivery.

## Boundary

This milestone is audit/check only.

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
