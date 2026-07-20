# v0.8.22 Manual Study real `/study` read-only shadow toggle — no Progress/no build/no ZIP/no delivery

## Purpose

This milestone adds the first controlled owner-local touchpoint on the real `/study` route.

It follows:

- v0.8.21 Manual Study real `/study` integration preflight freeze

## Implemented

Adds an explicit shadow toggle on `/study`:

- `/study?manual_study_shadow=1&course_id={course_id}`

When the toggle is active, `/study` renders Manual Study items from:

- `manual_study_items.preview.json`

When the toggle is not active, the existing `/study` behavior remains the fallback.

## Boundary

This is not default `/study` replacement.

The Manual Study shadow mode is active only when:

- `manual_study_shadow=1`
- `course_id` is provided

This milestone does not add a POST endpoint.

It does not write progress.

It does not mark answers.

It does not overwrite or modify the legacy `study_items.preview.json`.

It does not write a new Study artifact.

It does not change Course, Progress, OCR, or Formula OCR.

## Safety policy

- Source artifact: `manual_study_items.preview.json`
- Integration mode: `read_only_shadow_toggle`
- Existing `/study` fallback: available
- Answers: read-only in `<details>`
- Source metadata: visible
- Progress write: disabled
- Answer marking: disabled
- Legacy Study artifact write: disabled
- Rollback: revert this route/middleware/check/doc commit

## Non-goals

- No default `/study` replacement.
- No silent switch from legacy Study to Manual Study.
- No new POST endpoint.
- No Progress write.
- No answer marking.
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
