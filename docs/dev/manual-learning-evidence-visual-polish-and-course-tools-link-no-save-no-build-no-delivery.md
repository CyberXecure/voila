# v0.7.97 Manual Learning Evidence visual polish + Course Tools link — no save/no build/no ZIP/no delivery

## Purpose

This milestone improves discoverability and readability for the owner-local Manual Learning Evidence skeleton.

It follows:

- v0.7.94 Voila Direction Charter and Guard
- v0.7.95 Manual Learning Evidence UI Design
- v0.7.96 Manual Learning Evidence UI Skeleton

## Implemented

- Adds a `Manual evidence` link in Course Tools top navigation.
- Keeps the link inside the main Voila app on port `8787`.
- Keeps old external Crop Editor port `8790` unused.
- Adds clearer read-only visual status on the Manual Learning Evidence skeleton page.
- Adds explicit chips:
  - crop disabled
  - save disabled
  - Learning Pack disabled
  - owner-local only
- Keeps the disabled metadata form.

## Route

`/owner/manual-learning-evidence/{course_id}?page=1`

## Security

The Course Tools link is built with:

- `quote(pdf_path.stem, safe="")`
- `html.escape(..., quote=True)`

The v0.7.96 page-level escaping remains in place.

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
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.
