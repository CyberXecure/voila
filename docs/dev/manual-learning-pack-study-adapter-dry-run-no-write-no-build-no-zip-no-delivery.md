# v0.8.10 Manual Learning Pack Study Adapter dry-run — no write/no build/no ZIP/no delivery

## Purpose

This milestone adds a read-only Study Adapter dry-run over `manual_learning_pack.preview.json`.

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

## Implemented

- Adds read-only route:
  - `/owner/manual-learning-pack-study-adapter-dry-run/{course_id}`
- Reads only:
  - `manual_learning_pack.preview.json`
- Transforms preview items in memory into candidate Study items.
- Displays:
  - source schema
  - course_id
  - source preview items count
  - candidate Study items count
  - candidate Study cards
- For each candidate item, displays:
  - dry_run_id
  - source_evidence_id
  - study_item_type
  - title
  - prompt
  - answer
  - source_page
  - source_bbox
  - source_kind
  - source_status
  - write_target=none

## Boundary

This milestone is read-only.

It does not write any artifact.

It does not write `study_items.preview.json`.

It does not change:

- Course generation
- Study integration
- Progress
- OCR text
- Formula OCR

## Non-goals

- No new write endpoint.
- No Study artifact write.
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
