# v0.7.99 Manual Learning Evidence metadata preview binding — no save/no build/no ZIP/no delivery

## Purpose

This milestone binds the browser-only bbox crop selection to a pending metadata/evidence preview.

It follows:

- v0.7.94 Voila Direction Charter and Guard
- v0.7.95 Manual Learning Evidence UI Design
- v0.7.96 Manual Learning Evidence UI Skeleton
- v0.7.97 Visual polish and Course Tools link
- v0.7.98 Browser-only crop selection preview

## Implemented

- Selected bbox updates a readonly metadata preview field.
- Selected bbox updates a browser-only pending evidence preview.
- Pending preview includes:
  - artifact
  - course_id
  - page
  - bbox
  - crop_size
  - kind
  - title
  - verified_text
  - explanation_ro
  - source_status
  - source_note
  - status
  - save_enabled=false
  - manual_learning_evidence_written=false
  - crop_file_written=false
  - learning_pack_changed=false

## Route

`/owner/manual-learning-evidence/{course_id}?page=1`

## Boundary

This milestone is preview-only.

It does not add:

- POST endpoint
- save endpoint
- manual_learning_evidence.json write
- crop file write
- Learning Pack integration

## Non-goals

- No save endpoint.
- No manual_learning_evidence.json write.
- No crop file write.
- No Learning Pack integration.
- No Course generation change.
- No Study change.
- No Progress change.
- No OCR rewrite.
- No Formula OCR.
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.
