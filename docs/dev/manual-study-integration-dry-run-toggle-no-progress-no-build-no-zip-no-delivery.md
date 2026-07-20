# v0.8.18 Manual Study integration dry-run toggle — no Progress/no build/no ZIP/no delivery

## Purpose

This milestone adds an owner-local dry-run toggle before any real `/study` integration.

It follows the v0.8.17 readiness contract.

## Implemented

Adds the route:

- `/owner/manual-study-integration-dry-run/{course_id}?enabled=0`
- `/owner/manual-study-integration-dry-run/{course_id}?enabled=1`

The route reads:

- `manual_study_items.preview.json`

The route displays:

- explicit dry-run toggle state
- Manual Study source artifact
- target route `/study`
- Study-like cards when enabled
- read-only answers in `<details>`
- source metadata

## Boundary

This is not real `/study` integration.

It does not modify the existing `/study` route.

It does not write progress.

It does not mark answers.

It does not overwrite or modify the legacy `study_items.preview.json`.

It does not write a new Study artifact.

It does not change Course, Progress, OCR, or Formula OCR.

## Safety policy

- Manual Study source: `manual_study_items.preview.json`
- Legacy Study artifact protected: `study_items.preview.json`
- Mode: `dry_run_only`
- Progress write: disabled
- Answer marking: disabled
- Real Study connection: disabled
- Rollback: revert this route/check/doc commit

## Non-goals

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
