# v0.8.3 Manual Learning Evidence reject draft — no Learning Pack/no build/no ZIP/no delivery

## Purpose

This milestone adds owner-local rejection for saved Manual Learning Evidence drafts.

It follows:

- v0.8.0 Controlled save draft JSON
- v0.8.1 Read-only draft list
- v0.8.2 Verify draft JSON

## Implemented

- Adds a `Reject / Noise draft` button on pending draft cards.
- Adds owner-local POST endpoint:
  `/owner/manual-learning-evidence/{course_id}/reject-draft`
- Updates the selected draft inside `manual_learning_evidence.json`.
- Sets:
  - `status=rejected_noise`
  - `owner_verified=false`
  - `save_state=rejected`
  - `rejected_by=owner`
- Writes only `manual_learning_evidence.json`.

## Boundary

This milestone allows one controlled write to update a draft rejection state.

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
