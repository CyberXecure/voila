# v0.8.14 Manual Study Preview link from Course Tools — no Progress/no build/no ZIP/no delivery

## Purpose

This milestone adds a visible Course Tools link to the separate Manual Study Preview route.

It follows:

- v0.8.0 Controlled save draft JSON
- v0.8.1 Read-only draft list
- v0.8.2 Verify draft JSON
- v0.8.3 Reject draft JSON
- v0.8.4 Review summary
- v0.8.5 Accepted preview
- v0.8.6 Quality gate
- v0.8.7 Learning Pack dry-run preview
- v0.8.8 Learning Pack preview JSON export
- v0.8.9 Learning Pack preview viewer
- v0.8.10 Study Adapter dry-run
- v0.8.11 Manual Study Items preview export JSON
- v0.8.12 Manual Study Items preview viewer
- v0.8.13 Manual Study read-only preview route

## Implemented

- Adds visible Course Tools link:
  - `/owner/manual-study-preview/{course_id}`
- Displays status for:
  - `manual_study_items.preview.json`
- Status labels:
  - `Manual Study preview: OK`
  - `Manual Study preview: lipsește manual_study_items.preview.json`

## Boundary

This milestone only links to an existing read-only preview route.

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
- No Course generation change.
- No OCR rewrite.
- No Formula OCR.
- No crop file write.
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.
