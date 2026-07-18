# v0.7.98 Manual Learning Evidence crop selection preview — no save/no build/no ZIP/no delivery

## Purpose

This milestone adds browser-only crop selection preview to the owner-local Manual Learning Evidence page.

It follows:

- v0.7.94 Voila Direction Charter and Guard
- v0.7.95 Manual Learning Evidence UI Design
- v0.7.96 Manual Learning Evidence UI Skeleton
- v0.7.97 Visual polish and Course Tools link

## Implemented

- Pointer drag selection on the rendered source page image.
- Visible selection rectangle.
- Browser-only `bbox_px=[x1, y1, x2, y2]` display.
- Browser-only crop preview rendered into a canvas.
- Explicit read-only status: save disabled.
- Metadata form remains disabled.

## Route

`/owner/manual-learning-evidence/{course_id}?page=1`

## Security and storage boundary

The crop preview runs only in the browser.

This milestone does not add:

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
