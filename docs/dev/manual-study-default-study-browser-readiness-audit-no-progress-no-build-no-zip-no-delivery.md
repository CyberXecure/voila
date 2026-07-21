# v0.8.28 Manual Study default Study browser readiness audit — no Progress/no build/no ZIP/no delivery

## Purpose

This milestone records an owner-local browser readiness audit for the new guarded default `/study` Manual Study behavior.

It follows:

- v0.8.27 Manual Study default `/study` read-only fallback

## Audited flow

- `/study?pdf={pdf_name}` loads with HTTP 200.
- When `manual_study_items.preview.json` exists and contains items, `/study?pdf={pdf_name}` renders Manual Study by default.
- The default Study page renders Manual Study cards.
- Answers remain read-only inside `<details>`.
- Source metadata remains visible.
- `/study?manual_study_shadow=1&course_id={course_id}` remains available.
- Course Tools still shows the Manual Study shadow link.
- Course Tools still shows the separate dry-run link.
- When `manual_study_items.preview.json` is temporarily missing, `/study?pdf={pdf_name}` falls back to legacy Study.
- Legacy `study_items.preview.json` remains unchanged.
- No Progress write is added.
- No answer marking is added.

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

Default Manual Study has owner-local browser readiness evidence, but tester readiness remains blocked until a separate explicit milestone validates the full tester flow and then a separate packaging milestone is approved.

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
