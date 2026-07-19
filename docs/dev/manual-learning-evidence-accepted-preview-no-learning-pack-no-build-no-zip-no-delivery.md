# v0.8.5 Manual Learning Evidence accepted preview — no Learning Pack/no build/no ZIP/no delivery

## Purpose

This milestone adds a read-only accepted evidence preview to the Manual Learning Evidence page.

It follows:

- v0.8.0 Controlled save draft JSON
- v0.8.1 Read-only draft list
- v0.8.2 Verify draft JSON
- v0.8.3 Reject draft JSON
- v0.8.4 Review summary

## Implemented

- Adds a separate accepted evidence preview.
- Shows only items with:
  - `status=accepted_owner_verified`
  - `owner_verified=true`
- Displays:
  - id
  - title
  - page
  - kind
  - source_status
  - verified_text
  - explanation_ro
  - bbox
- Labels accepted items as eligible for a future Learning Pack.
- Adds no new write endpoint.
- Does not generate or modify Learning Pack artifacts.

## Boundary

This milestone is read-only UI preview over `manual_learning_evidence.json`.

It does not write crop image files.

It does not change:

- Learning Pack
- Course generation
- Study
- Progress
- OCR text
- Formula OCR

## Non-goals

- No new write endpoint.
- No crop file write.
- No Learning Pack integration or generation.
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
