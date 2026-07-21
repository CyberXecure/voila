# v0.8.27 Manual Study default `/study` read-only fallback — no Progress/no build/no ZIP/no delivery

## Purpose

This milestone implements the first guarded default `/study` behavior change for Manual Study.

It follows:

- v0.8.26 Manual Study default `/study` integration preflight contract

## Implemented

When `/study?pdf={pdf_name}` is opened:

1. The existing PDF name validation is reused.
2. The active course id is derived from the validated PDF stem.
3. If `manual_study_items.preview.json` exists, is readable, and contains items:
   - `/study` renders Manual Study read-only cards;
   - answers remain inside `<details>`;
   - source metadata remains visible;
   - policy metadata declares no Progress write and no answer marking.
4. If `manual_study_items.preview.json` is missing, invalid, or empty:
   - `/study` falls back to the existing legacy Study behavior.

The explicit shadow path remains available:

- `/study?manual_study_shadow=1&course_id={course_id}`

## Boundary

This milestone does not add a route.

It does not add a POST endpoint.

It does not remove the existing `/study` route.

It does not modify the legacy `/study` route block.

It does not write progress.

It does not mark answers.

It does not overwrite or modify the legacy `study_items.preview.json`.

It does not write a new Study artifact.

It does not change Course, Progress, OCR, or Formula OCR.

## Safety policy

- Default Manual Study is read-only.
- Default Manual Study is enabled only when `manual_study_items.preview.json` is present and valid.
- Legacy fallback remains active when Manual Study preview is missing, invalid, or empty.
- Source metadata remains visible.
- Answers remain read-only inside `<details>`.
- No Progress write.
- No answer marking.
- No legacy Study artifact overwrite.
- Rollback is a clean revert of this implementation commit.

## Non-goals

- No Progress integration.
- No answer scoring.
- No answer persistence.
- No Study artifact write.
- No Course generation change.
- No OCR rewrite.
- No Formula OCR.
- No crop file write.
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.
