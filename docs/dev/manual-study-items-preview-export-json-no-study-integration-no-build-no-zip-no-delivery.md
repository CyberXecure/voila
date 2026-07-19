# v0.8.11 Manual Study Items preview export JSON — no Study integration/no build/no ZIP/no delivery

## Purpose

This milestone adds a controlled owner-local export for `manual_study_items.preview.json`.

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

## Implemented

- Adds controlled POST endpoint:
  - `/owner/manual-learning-pack-study-adapter-dry-run/{course_id}/export-manual-study-items-preview`
- Writes only:
  - `manual_study_items.preview.json`
- Reads:
  - `manual_learning_pack.preview.json`
- Uses the v0.8.10 Study Adapter dry-run transformation.
- Exports candidate Study items with:
  - source_evidence_id
  - manual_study_item_id
  - study_item_type
  - title
  - prompt
  - answer
  - source_page
  - source_bbox
  - source_kind
  - source_status
  - write_target

## Boundary

This milestone writes only `manual_study_items.preview.json`.

It does not write or modify the legacy `study_items.preview.json`.

It does not connect the real Study page.

It does not change:

- Course generation
- Progress
- OCR text
- Formula OCR

## Non-goals

- No legacy Study artifact write.
- No Study integration.
- No Course integration.
- No Progress integration.
- No OCR rewrite.
- No Formula OCR.
- No crop file write.
- No final Learning Pack delivery artifact.
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.
