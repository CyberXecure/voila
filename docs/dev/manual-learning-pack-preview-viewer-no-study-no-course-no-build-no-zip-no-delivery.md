# v0.8.9 Manual Learning Pack preview viewer — no Study/no Course/no build/no ZIP/no delivery

## Purpose

This milestone adds a read-only viewer for `manual_learning_pack.preview.json`.

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

## Implemented

- Adds read-only route:
  - `/owner/manual-learning-pack-preview/{course_id}`
- Reads only:
  - `manual_learning_pack.preview.json`
- Displays:
  - schema
  - course_id
  - artifact
  - source
  - mode
  - generated_by
  - items_count
  - policy flags
  - preview items
- For each preview item, displays:
  - source_evidence_id
  - title
  - kind
  - verified_text
  - explanation_ro
  - page
  - bbox
  - source_status

## Boundary

This milestone is read-only.

It does not write any artifact.

It does not change:

- Course generation
- Study
- Progress
- OCR text
- Formula OCR

## Non-goals

- No new write endpoint.
- No Course integration.
- No Study integration.
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
