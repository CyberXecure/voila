# v0.8.19 Manual Study dry-run link from Course Tools — no Progress/no build/no ZIP/no delivery

## Purpose

This milestone exposes the existing Manual Study integration dry-run toggle from Course Tools.

It follows:

- v0.8.17 Manual Study integration readiness contract
- v0.8.18 Manual Study integration dry-run toggle

## Implemented

Course Tools now shows a visible owner-local link to:

- `/owner/manual-study-integration-dry-run/{course_id}?enabled=0`

Course Tools also shows dry-run policy/status:

- `manual_study_items.preview.json`
- `dry_run_only`
- `manual_study_connected_to_real_study=false`
- `progress_write=false`
- `answer_marking=false`
- `writes_legacy_study_items_preview=false`

## Boundary

This milestone only exposes a link/status card from Course Tools.

It does not connect Manual Study to real `/study`.

It does not replace or modify the existing `/study` route.

It does not add a POST endpoint.

It does not write progress.

It does not mark answers.

It does not overwrite or modify the legacy `study_items.preview.json`.

It does not write a new Study artifact.

It does not change Course, Progress, OCR, or Formula OCR.

## Safety policy

- Link target: owner-local dry-run route
- Default toggle state: off
- Integration mode: `dry_run_only`
- Progress write: disabled
- Answer marking: disabled
- Real Study connection: disabled
- Rollback: revert this link/check/doc commit

## Non-goals

- No real `/study` replacement.
- No new Progress behavior.
- No answer marking.
- No Study artifact write.
- No Course integration.
- No OCR rewrite.
- No Formula OCR.
- No crop file write.
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.
