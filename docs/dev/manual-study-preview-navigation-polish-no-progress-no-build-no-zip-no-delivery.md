# v0.8.15 Manual Study Preview navigation polish — no Progress/no build/no ZIP/no delivery

## Purpose

This milestone polishes the separate owner-local Manual Study Preview route.

It follows:

- v0.8.13 Manual Study read-only preview route
- v0.8.14 Course Tools link to Manual Study Preview

## Implemented

- Improves the read-only route:
  - `/owner/manual-study-preview/{course_id}`
- Adds local in-page navigation:
  - top card jump links
  - Previous link
  - Next link
  - Back to top link
- Keeps answer display read-only in a `<details>` block.
- Keeps source metadata visible.

## Boundary

This milestone is read-only.

It does not write any artifact.

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
