# v0.7.96 Manual Learning Evidence UI Skeleton — no build/no ZIP/no delivery

## Purpose

This milestone implements the first read-only skeleton route for Manual Learning Evidence.

It follows:

- v0.7.94 Voila Direction Charter and Guard
- v0.7.95 Manual Learning Evidence UI Design

## Implemented route

`/owner/manual-learning-evidence/{course_id}`

Optional query:

`?page=1`

The route runs in the main Voila app on port `8787`.

It does not use the old external Crop Editor on port `8790`.

## Implemented skeleton UI

The read-only skeleton page shows:

- course id
- selected page number
- source page image if available
- Previous page / Next page links
- disabled metadata form
- required future fields:
  - title
  - kind
  - verified_text
  - explanation_ro
  - source_status
  - source_note
  - status
- allowed kind values:
  - formula
  - definition
  - example
  - theorem
  - diagram
  - drawing
  - note
- allowed source_status values:
  - verified
  - uncertain
  - possible_source_error
- allowed status values:
  - pending_owner_review
  - accepted_owner_verified
  - rejected_noise

## Source image

The skeleton uses existing rendered page images when available:

`data/output/{course_id}/formula_visual_evidence/pages/page-NNN.png`

This is temporary for skeleton display only.

## Manual Learning Evidence artifact

The future save target remains:

`data/output/{course_id}/manual_learning_evidence.json`

Crop folder remains:

`data/output/{course_id}/manual_learning_evidence/crops/`

No artifact is written in this milestone.

## Non-goals

- No mouse crop selection.
- No save endpoint.
- No manual_learning_evidence.json write.
- No crop file write.
- No Learning Pack integration.
- No Course generation change.
- No Study change.
- No Progress change.
- No OCR rewrite.
- No Formula OCR.
- No old Crop Editor 8790 integration.
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.
