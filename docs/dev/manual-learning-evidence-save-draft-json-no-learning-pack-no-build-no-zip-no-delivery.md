# v0.8.0 Manual Learning Evidence save draft JSON — no Learning Pack/no build/no ZIP/no delivery

## Purpose

This milestone adds the first controlled write for Manual Learning Evidence.

It follows:

- v0.7.94 Voila Direction Charter and Guard
- v0.7.95 Manual Learning Evidence UI Design
- v0.7.96 Manual Learning Evidence UI Skeleton
- v0.7.97 Visual polish and Course Tools link
- v0.7.98 Browser-only crop selection preview
- v0.7.99 Metadata pending preview binding

## Implemented

- Adds owner-local POST endpoint:
  `/owner/manual-learning-evidence/{course_id}/save-draft`
- Adds `Save draft evidence` button on the Manual Learning Evidence page.
- Writes only:
  `data/output/{course_id}/manual_learning_evidence.json`
- Saved items use:
  - `status=pending_owner_review`
  - `owner_verified=false`
  - `save_state=draft`
  - `crop_file_written=false`
  - `learning_pack_changed=false`

## Boundary

This milestone allows one controlled write: `manual_learning_evidence.json`.

It does not write crop image files.

It does not change:

- Learning Pack
- Course generation
- Study
- Progress
- OCR text
- Formula OCR

## Non-goals

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
