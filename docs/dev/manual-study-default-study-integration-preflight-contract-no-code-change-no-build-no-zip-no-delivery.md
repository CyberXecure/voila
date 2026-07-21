# v0.8.26 Manual Study default `/study` integration preflight contract — no code change/no build/no ZIP/no delivery

## Purpose

This milestone records the preflight contract before any future default `/study` behavior change.

It follows:

- v0.8.21 Manual Study real `/study` integration preflight freeze
- v0.8.22 Manual Study real `/study` read-only shadow toggle
- v0.8.23 Manual Study shadow browser readiness audit
- v0.8.24 Manual Study shadow link from Course Tools
- v0.8.25 Course Tools → Manual Study shadow browser readiness audit

## Current state confirmed

Manual Study is available only through the explicit owner-local shadow route:

- `/study?manual_study_shadow=1&course_id={course_id}`

Course Tools links to that explicit shadow route.

The existing `/study` route remains unchanged and is not replaced.

Manual Study is not the default `/study`.

## Future default `/study` contract

A future separate milestone may make `/study` prefer Manual Study only under this guarded rule:

1. Resolve the active course safely.
2. If `manual_study_items.preview.json` exists for that course and is readable:
   - render Manual Study read-only cards;
   - keep answers inside `<details>`;
   - keep source metadata visible;
   - do not write Progress;
   - do not mark answers;
   - do not write or modify `study_items.preview.json`.
3. If `manual_study_items.preview.json` does not exist, is invalid, or is empty:
   - fall back to the existing legacy `/study` behavior.

## Safety gates for the future implementation

The future implementation must prove:

- default `/study` works with Manual Study only when `manual_study_items.preview.json` is present;
- fallback legacy `/study` remains available when Manual Study preview is missing or invalid;
- no POST endpoint is added;
- no Progress write is added;
- no answer marking is added;
- no `study_items.preview.json` overwrite happens;
- no Course generation behavior changes;
- no OCR rewrite happens;
- no Formula OCR happens;
- source metadata remains visible;
- answers remain read-only;
- rollback is a clean revert of the future implementation commit.

## Rollback contract

If the future default `/study` implementation fails browser readiness, CodeQL, fallback behavior, or artifact protection:

- do not merge;
- do not package;
- do not deliver;
- revert the implementation patch;
- preserve the v0.8.22 shadow route and v0.8.24 Course Tools shadow link as0.8.22 shadow route and v0.8.24 Course Tools shadow link as the safe owner-local access path.

- preserve the v0.8.22 shadow route and v0.8.24 Course Tools shadow link as the safe owner-local access path.

## Boundary

This milestone is preflight/docs/check only.

It does not modify `services/api/web_app.py`.

It does not add a route.

It does not add a POST endpoint.

It does not make Manual Study the default `/study`.

It does not replace or modify the existing `/study` route.

It does not write progress.

It does not mark answers.

It does not overwrite or modify the legacy `study_items.preview.json`.

It does not write a new Study artifact.

It does not change Course, Progress, OCR, or Formula OCR.

## Result policy

Tester readiness remains blocked.

A separate explicit implementation milestone is required before any default `/study` change.

A separate explicit packaging milestone is required before any tester package.

## Non-goals

- No UI implementation change.
- No default `/study` replacement.
- No silent switch from legacy Study to Manual Study.
- No new Progress behavior.
- No answer marking.
- No Study artifact write.
- No Course integration.
- No OCR rewrite.
- No Formula OCR.
- No crop file write.
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.
