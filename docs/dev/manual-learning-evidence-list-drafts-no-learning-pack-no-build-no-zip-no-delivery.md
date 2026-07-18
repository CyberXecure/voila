# v0.8.1 Manual Learning Evidence list drafts — no Learning Pack/no build/no ZIP/no delivery

## Purpose

This milestone adds a read-only draft list to the Manual Learning Evidence page.

It follows:

- v0.7.94 Voila Direction Charter and Guard
- v0.7.95 Manual Learning Evidence UI Design
- v0.7.96 Manual Learning Evidence UI Skeleton
- v0.7.97 Visual polish and Course Tools link
- v0.7.98 Browser-only crop selection preview
- v0.7.99 Metadata pending preview binding
- v0.8.0 Controlled save draft JSON

## Implemented

- Reads `manual_learning_evidence.json`.
- Displays draft evidence cards.
- Shows:
  - id
  - title
  - page
  - kind
  - source_status
  - status
  - owner_verified
  - save_state
  - bbox
- Keeps the list read-only.
- Adds no new write endpoint.

## Boundary

This milestone only lists drafts.

It does not add:

- accept/verify action
- crop file write
- Learning Pack integration
- Course generation change
- Study change
- Progress change
- OCR rewrite
- Formula OCR

## Non-goals

- No accept/verify.
- No new write endpoint.
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
