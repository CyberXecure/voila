# v0.8.21 Manual Study real `/study` integration preflight freeze — no code change/no build/no ZIP/no delivery

## Purpose

This milestone freezes the preflight contract before the first controlled change to the real `/study` route.

It follows:

- v0.8.17 Manual Study integration readiness contract
- v0.8.18 Manual Study integration dry-run toggle
- v0.8.19 Course Tools link to Manual Study dry-run
- v0.8.20 Manual Study dry-run browser readiness audit

## Current state frozen

The current state is:

- Manual Study exists only as preview/dry-run.
- Manual Study dry-run reads `manual_study_items.preview.json`.
- Course Tools links to the dry-run route.
- Dry-run Toggle OFF keeps cards hidden.
- Dry-run Toggle ON renders Study-like cards.
- Existing `/study` remains untouched.
- Progress write remains disabled for Manual Study.
- Answer marking remains disabled for Manual Study.
- Legacy `study_items.preview.json` remains protected.

## Static preflight comparison

Before any real integration, the check records:

- real `/study` route is still present
- Manual Study dry-run route is separate
- Manual Study dry-run policy still declares `manual_study_connected_to_real_study=false`
- Manual Study dry-run policy still declares `progress_write=false`
- Manual Study dry-run policy still declares `answer_marking=false`
- Manual Study dry-run policy still declares `writes_legacy_study_items_preview=false`

## Runtime preflight comparison

Before any real integration, the check verifies:

- homepage loads
- Course Tools loads through discovered real URL
- Course Tools dry-run link/status is visible
- dry-run Toggle OFF loads and keeps cards hidden
- dry-run Toggle ON loads and renders cards
- answers remain read-only in `<details>`
- source metadata remains visible
- legacy `study_items.preview.json` remains unchanged

## Allowed future v0.8.22 shape

A future v0.8.22 may touch the real `/study` route only if it remains narrow and reversible.

Recommended future milestone:

`v0.8.22-owner-local-manual-study-real-study-read-only-shadow-toggle-no-progress-no-build-no-zip-no-delivery`

Allowed v0.8.22 changes:

- add an explicit owner-local toggle or query path for real `/study` to read `manual_study_items.preview.json`
- keep existing `/study` fallback available
- keep answers read-only
- keep source metadata visible
- avoid Progress writes
- avoid answer marking
- avoid overwriting `study_items.preview.json`
- avoid Course generation changes
- avoid OCR/Formula OCR changes
- keep rollback as reverting the v0.8.22 commit

Disallowed v0.8.22 changes:

- no default replacement of `/study`
- no silent switch from legacy Study to Manual Study
- no Progress write
- no answer marking
- no legacy `study_items.preview.json` overwrite
- no build
- no ZIP
- no share
- no delivery
- no distribution

## Boundary

This milestone is preflight/check only.

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

Tester readiness remains blocked.

Real `/study` integration requires a separate explicit milestone after this preflight freeze.

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
