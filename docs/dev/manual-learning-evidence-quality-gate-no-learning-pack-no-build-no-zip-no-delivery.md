# v0.8.6 Manual Learning Evidence quality gate — no Learning Pack/no build/no ZIP/no delivery

## Purpose

This milestone adds a read-only quality gate for accepted Manual Learning Evidence.

It follows:

- v0.8.0 Controlled save draft JSON
- v0.8.1 Read-only draft list
- v0.8.2 Verify draft JSON
- v0.8.3 Reject draft JSON
- v0.8.4 Review summary
- v0.8.5 Accepted preview

## Implemented

- Adds a read-only accepted evidence quality gate.
- Checks only items with:
  - `status=accepted_owner_verified`
  - `owner_verified=true`
- Required fields:
  - `title`
  - `kind`
  - `verified_text`
  - `explanation_ro`
  - `page`
  - `bbox`
- Displays:
  - eligible
  - incomplete
  - blocked
- Shows missing fields per accepted item.
- Adds no new write endpoint.
- Does not generate or modify Learning Pack artifacts.

## Boundary

This milestone is read-only validation over `manual_learning_evidence.json`.

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
