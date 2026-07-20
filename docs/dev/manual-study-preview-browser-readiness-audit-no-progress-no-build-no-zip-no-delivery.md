# v0.8.16 Manual Study Preview browser readiness audit — no Progress/no build/no ZIP/no delivery

## Purpose

This milestone records an owner-local browser readiness audit for the Manual Study Preview flow.

It follows:

- v0.8.13 Manual Study read-only preview route
- v0.8.14 Course Tools link to Manual Study Preview
- v0.8.15 Manual Study Preview navigation polish

## Audited flow

- Course Tools loads.
- Course Tools exposes Manual Study Preview link.
- Course Tools shows status for `manual_study_items.preview.json`.
- Manual Study Preview route loads.
- Manual Study Preview displays Study-like cards.
- Top card navigation is visible.
- Previous/Next navigation is visible.
- Back to top navigation is visible.
- Answers remain read-only inside `<details>`.
- Source metadata remains visible.
- Legacy `study_items.preview.json` remains unchanged.

## Boundary

This milestone is audit/check only.

It does not modify `services/api/web_app.py`.

It does not add a route.

It does not add a write endpoint.

It does not replace or modify the existing `/study` route.

It does not write progress.

It does not mark answers.

It does not write or modify the legacy `study_items.preview.json`.

It does not change:

- Course generation
- Progress
- OCR text
- Formula OCR

## Non-goals

- No UI implementation change.
- No new POST endpoint.
- No Progress write.
- No answer marking.
- No Study integration.
- No Course integration.
- No OCR rewrite.
- No Formula OCR.
- No crop file write.
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.

## Result policy

The audit may pass browser readiness for the owner-local preview flow, but tester readiness remains blocked until a separate explicit milestone approves real Study integration and tester packaging.
