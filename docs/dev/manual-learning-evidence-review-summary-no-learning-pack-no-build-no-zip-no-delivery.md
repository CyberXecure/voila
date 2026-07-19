# v0.8.4 Manual Learning Evidence review summary — no Learning Pack/no build/no ZIP/no delivery

## Purpose

This milestone adds a read-only review summary to the Manual Learning Evidence page.

It follows:

- v0.8.0 Controlled save draft JSON
- v0.8.1 Read-only draft list
- v0.8.2 Verify draft JSON
- v0.8.3 Reject draft JSON

## Implemented

- Adds a visible read-only review summary.
- Counts evidence items by status:
  - `pending_owner_review`
  - `accepted_owner_verified`
  - `rejected_noise`
- Adds simple status filter links.
- Adds status anchors/sections in the draft list.
- Adds no new write endpoint.

## Boundary

This milestone is read-only UI summarization over `manual_learning_evidence.json`.

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
