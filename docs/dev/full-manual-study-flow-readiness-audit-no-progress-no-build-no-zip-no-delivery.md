# v0.8.30 Full Manual Study flow readiness audit — no Progress/no build/no ZIP/no delivery

## Purpose

This milestone records an owner-local full Manual Study flow readiness audit after the guarded default `/study` activation.

It follows:

- v0.8.27 Manual Study default `/study` read-only fallback
- v0.8.28 Manual Study default Study browser readiness audit
- v0.8.29 Course Tools normal Study link → default Manual Study audit

## Audited flow

- Course Tools loads with HTTP 200.
- Course Tools contains the normal Study link to `/study?pdf={pdf_name}`.
- Following the normal Study link opens `/study?pdf={pdf_name}` with HTTP 200.
- The normal Study path renders Manual Study by default when `manual_study_items.preview.json` exists and contains items.
- The default Manual Study page renders Manual Study cards.
- Answers remain read-only inside `<details>`.
- Source metadata remains visible.
- Course Tools contains the explicit Manual Study shadow link.
- Following the shadow link opens `/study?manual_study_shadow=1&course_id={course_id}` with HTTP 200.
- The shadow page remains separate from the normal Study link.
- Course Tools contains the separate dry-run link.
- Following the dry-run link opens the dry-run route with HTTP 200.
- The dry-run route remains separate from default Study.
- When `manual_study_items.preview.json` is temporarily missing, the normal Study path falls back to legacy Study.
- Legacy `study_items.preview.json` remains unchanged.
- No Progress write is added.
- No answer marking is added.
- No Study artifact is written.
- No Course generation behavior changes.
- No OCR rewrite happens.
- No Formula OCR happens.

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

## Result policy

This is owner-local readiness evidence only.

Tester readiness remains blocked until a separate explicit tester-readiness milestone validates the full tester flow and a separate explicit packaging milestone is approved.

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
