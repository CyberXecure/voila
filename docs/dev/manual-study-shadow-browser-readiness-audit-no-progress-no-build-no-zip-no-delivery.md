# v0.8.23 Manual Study shadow browser readiness audit — no Progress/no build/no ZIP/no delivery

## Purpose

This milestone records an owner-local browser readiness audit for the real `/study` Manual Study shadow toggle.

It follows:

- v0.8.21 Manual Study real `/study` integration preflight freeze
- v0.8.22 Manual Study real `/study` read-only shadow toggle

## Audited flow

- `/study?manual_study_shadow=1&course_id={course_id}` loads with HTTP 200.
- The shadow route reads `manual_study_items.preview.json`.
- The shadow route renders Manual Study cards.
- Answers remain read-only inside `<details>`.
- Source metadata remains visible.
- `/study?manual_study_shadow=1` without `course_id` shows the missing course message.
- `/study` without shadow toggle does not render the Manual Study shadow page.
- Existing `/study` route block hash remains unchanged from the v0.8.21 preflight snapshot.
- Legacy `study_items.preview.json` remains unchanged.
- No Progress write is added.
- No answer marking is added.

## Boundary

This milestone is audit/check only.

It does not modify `services/api/web_app.py`.

It does not add a route.

It does not add a POST endpoint.

It does not connect Manual Study as the default real `/study`.

It does not replace or modify the existing `/study` route.

It does not write progress.

It does not mark answers.

It does not overwrite or modify the legacy `study_items.preview.json`.

It does not write a new Study artifact.

It does not change Course, Progress, OCR, or Formula OCR.

## Result policy

The shadow browser flow may pass owner-local readiness, but tester readiness remains blocked until a separate explicit milestone approves a default/fallback behavior change and then separately approves packaging.

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
