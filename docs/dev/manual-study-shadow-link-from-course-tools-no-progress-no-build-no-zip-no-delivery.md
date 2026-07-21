# v0.8.24 Manual Study shadow link from Course Tools — no Progress/no build/no ZIP/no delivery

## Purpose

This milestone exposes the existing `/study` Manual Study shadow toggle from Course Tools.

It follows:

- v0.8.22 Manual Study real `/study` read-only shadow toggle
- v0.8.23 Manual Study shadow browser readiness audit

## Implemented

Course Tools now shows a visible owner-local link to:

- `/study?manual_study_shadow=1&course_id={course_id}`

Course Tools keeps the separate dry-run link to:

- `/owner/manual-study-integration-dry-run/{course_id}?enabled=0`

Course Tools shows shadow policy/status:

- `manual_study_items.preview.json`
- `read_only_shadow_toggle`
- `manual_study_default_enabled=false`
- `manual_study_connected_to_real_study=shadow_only_explicit_link`
- `progress_write=false`
- `answer_marking=false`
- `writes_legacy_study_items_preview=false`

## Boundary

This milestone only exposes a Course Tools link to the existing explicit shadow route.

It does not make Manual Study the default `/study`.

It does not replace or modify the existing `/study` route.

It does not add a route.

It does not add a POST endpoint.

It does not write progress.

It does not mark answers.

It does not overwrite or modify the legacy `study_items.preview.json`.

It does not write a new Study artifact.

It does not change Course, Progress, OCR, or Formula OCR.

## Safety policy

- Link target: explicit owner-local `/study` shadow route
- Shadow mode: `read_only_shadow_toggle`
- Default Study behavior: unchanged
- Progress write: disabled
- Answer marking: disabled
- Legacy Study artifact write: disabled
- Rollback: revert this link/check/doc commit

## Non-goals

- No default `/study` replacement.
- No silent switch from legacy Study to Manual Study.
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
