# v0.8.17 Manual Study integration readiness contract — no code change/no build/no ZIP/no delivery

## Purpose

This milestone defines the readiness contract for a future explicit Manual Study integration milestone.

It does not integrate Manual Study into `/study`.

It follows:

- v0.8.13 Manual Study read-only preview route
- v0.8.14 Course Tools link to Manual Study Preview
- v0.8.15 Manual Study Preview navigation polish
- v0.8.16 Manual Study Preview browser readiness audit

## Integration source

The only approved future source for Manual Study integration is:

- `manual_study_items.preview.json`

The legacy artifact remains protected:

- `study_items.preview.json`

A future integration milestone may read `manual_study_items.preview.json`, but it must not overwrite or silently replace the legacy artifact.

## Entry criteria before touching `/study`

A future `/study` integration milestone is allowed only if all criteria below are true:

- `manual_learning_evidence.json` exists.
- Accepted evidence has `status=accepted_owner_verified`.
- Accepted evidence has `owner_verified=true`.
- Quality gate passes for required fields.
- `manual_learning_pack.preview.json` exists.
- `manual_study_items.preview.json` exists.
- Manual Study Preview route loads with HTTP 200.
- Course Tools shows Manual Study Preview link/status.
- Manual Study Preview shows cards, navigation, answer details, and source metadata.
- Existing `/study` route is preserved until a separate integration milestone explicitly changes it.
- Rollback path is documented before integration.
- Progress write remains disabled until a separate explicit milestone enables it.
- Answer marking remains disabled until a separate explicit milestone enables it.

## Safety gates for future integration

A future integration milestone must prove:

- No unverified evidence is included.
- No rejected evidence is included.
- No pending evidence is included.
- No legacy Study artifact is overwritten.
- No Progress file is written.
- No answer marking is added.
- Existing `/study` fallback behavior remains available.
- Manual Study items can be disabled by removing or ignoring `manual_study_items.preview.json`.
- All visible Study cards preserve source metadata.
- All manual Study items are traceable to `source_evidence_id`.

## Rollback contract

Rollback must be possible by:

- Reverting the future integration commit.
- Removing or ignoring `manual_study_items.preview.json`.
- Keeping the existing `/study` route behavior available.
- Keeping legacy `study_items.preview.json` unchanged.
- Keeping progress data unchanged.
- Keeping generated Course/OCR artifacts unchanged.

## Explicit non-goals

This milestone is contract/check only.

It does not modify `services/api/web_app.py`.

It does not add a route.

It does not add a write endpoint.

It does not connect Manual Study to `/study`.

It does not write progress.

It does not mark answers.

It does not write or modify the legacy `study_items.preview.json`.

It does not change:

- Course generation
- Progress
- OCR text
- Formula OCR

## Delivery policy

- No UI implementation change.
- No new POST endpoint.
- No Progress write.
- No answer marking.
- No Study integration.
- No Course integration.
- No OCR rewrite.
- No Formula OCR.
- No crop file write.
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.

## Required next milestone shape

The next integration milestone, if approved separately, must be narrow and reversible.

Recommended future name:

`v0.8.18-owner-local-manual-study-integration-dry-run-toggle-no-progress-no-build-no-zip-no-delivery`

That future milestone must still avoid Progress writes, answer marking, ZIP creation, sharing, and tester delivery.
