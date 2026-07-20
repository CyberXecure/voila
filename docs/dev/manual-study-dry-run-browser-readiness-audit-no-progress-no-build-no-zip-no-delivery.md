# v0.8.20 Manual Study dry-run browser readiness audit — no Progress/no build/no ZIP/no delivery

## Purpose

This milestone records an owner-local browser readiness audit for the Manual Study integration dry-run flow.

It follows:

- v0.8.17 Manual Study integration readiness contract
- v0.8.18 Manual Study integration dry-run toggle
- v0.8.19 Course Tools link to Manual Study dry-run

## Audited flow

- Homepage loads.
- The real Course Tools URL is discovered from homepage.
- Course Tools loads with HTTP 200.
- Course Tools exposes the Manual Study dry-run link.
- Course Tools shows dry-run status/policy.
- Manual Study dry-run Toggle OFF route loads.
- Toggle OFF keeps cards hidden.
- Manual Study dry-run Toggle ON route loads.
- Toggle ON renders Study-like cards.
- Answers remain read-only inside `<details>`.
- Source metadata remains visible.
- Existing `/study` route code remains present and unchanged by this milestone.
- Legacy `study_items.preview.json` remains unchanged.
- No Progress write is added.
- No answer marking is added.

## Boundary

This milestone is audit/check only.

It does not modify `services/api/web_app.py`.

It does not add a route.

It does not add a POST endpoint.

It does not connect Manual Study to real `/study`.

It does not replace or modify the existing `/study` route.

It does not write progress.

It does not mark answers.

It does not overwrite or modify the legacy `study_items.preview.json`.

It does not write a new Study artifact.

It does not change Course, Progress, OCR, or Formula OCR.

## Result policy

The dry-run browser flow may pass owner-local readiness, but tester readiness remains blocked until a separate explicit milestone connects real `/study`, validates it, and separately approves packaging.

## Non-goals

- No UI implementation change.
- No real `/study` replacement.
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
