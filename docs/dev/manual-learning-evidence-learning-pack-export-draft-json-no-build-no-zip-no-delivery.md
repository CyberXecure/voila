# v0.8.8 Manual Learning Evidence Learning Pack export draft JSON — no build/no ZIP/no delivery

## Purpose

This milestone adds a controlled owner-local export for a draft Learning Pack preview JSON artifact.

It follows:

- v0.8.0 Controlled save draft JSON
- v0.8.1 Read-only draft list
- v0.8.2 Verify draft JSON
- v0.8.3 Reject draft JSON
- v0.8.4 Review summary
- v0.8.5 Accepted preview
- v0.8.6 Quality gate
- v0.8.7 Learning Pack dry-run preview

## Implemented

- Adds a controlled POST export endpoint:
  - `/owner/manual-learning-evidence/{course_id}/export-learning-pack-draft`
- Writes only:
  - `manual_learning_pack.preview.json`
- Uses only evidence items with:
  - `status=accepted_owner_verified`
  - `owner_verified=true`
  - all quality gate required fields present
- Required fields:
  - `title`
  - `kind`
  - `verified_text`
  - `explanation_ro`
  - `page`
  - `bbox`
- The preview JSON includes:
  - source evidence id
  - title
  - kind
  - verified_text
  - explanation_ro
  - page
  - bbox
  - source_status
  - policy flags
- Adds an export button to the existing dry-run preview section.

## Boundary

This milestone writes only `manual_learning_pack.preview.json`.

It does not write crop image files.

It does not change:

- Course generation
- Study
- Progress
- OCR text
- Formula OCR

## Non-goals

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
