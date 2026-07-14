# v0.7.73 Owner-local OCR Review final confirm button

Status: PASS_FINAL_CONFIRM_BUTTON

Marker:
VOILA_V0_7_73_OCR_REVIEW_FINAL_CONFIRM_BUTTON_CHECK=PASS

Baseline:
v0.7.72 completed and merged to protected main at `9340b76`.

## Purpose

This milestone adds a separate final confirmation button to the owner-local OCR Review page.

The button is shown only after all OCR Review decisions are resolved.

The confirmation writes only to `ocr_review_decisions.json`.

## Routes

Existing OCR Review route:

`/owner/ocr-review/{course_id}`

New final confirmation route:

`/owner/ocr-review/{course_id}/confirm`

## UI behavior

When pending decisions remain, the page shows that final confirmation is blocked.

When `pending_decision_count=0`, the page shows the button:

`Confirmă OCR Review`

After confirmation, the page shows that OCR Review is final-confirmed.

## Write behavior

The final confirmation writes only to:

`ocr_review_decisions.json`

It sets:

- `owner_review_confirmed=true`
- `owner_review_confirmed_at`
- `real_user_decisions_performed=true`
- `pending_decision_count=0`
- `resolved_decision_count=decision_count`
- `applied_to_learning_pack=false`
- `final_confirmation_source=owner_local_guided_ui_v0.7.73`

The quality gate is updated to:

- `all_required_decisions_resolved=true`
- `owner_review_confirmed=true`
- `generation_should_wait_for_review=true`
- `generation_block_reason=generate_integration_not_enabled_v0.7.73`

## Important safety rule

Even after final OCR Review confirmation, generation remains blocked.

This milestone intentionally does not integrate with `/generate`.

A separate future milestone must explicitly integrate confirmed OCR Review decisions into the document learning pack and generation gate.

## Direct smoke

Smoke evidence path:

`D:\dev\tester-runs\v0773-ocr-review-confirm`

HTML pending before confirmation:

`D:\dev\tester-runs\v0773-ocr-review-confirm\pending-before-confirm.html`

HTML ready before confirmation:

`D:\dev\tester-runs\v0773-ocr-review-confirm\ready-before-confirm.html`

HTML after confirmation:

`D:\dev\tester-runs\v0773-ocr-review-confirm\after-confirm.html`

Smoke result:

- `VOILA_V0_7_73_FINAL_CONFIRM_BUTTON_SMOKE=PASS`
- `POST_ROUTE=/owner/ocr-review/{course_id}/confirm`
- `CONFIRM_BLOCKED_WHEN_PENDING=PASS`
- `CONFIRM_READY_WHEN_PENDING_ZERO=PASS`
- `POST_STATUS=303`
- `DECISION_WRITE_TARGET=ocr_review_decisions.json`
- `OWNER_REVIEW_CONFIRMED=True`
- `PENDING_DECISION_COUNT_AFTER=0`
- `RESOLVED_DECISION_COUNT_AFTER=20`
- `GENERATION_SHOULD_WAIT_FOR_REVIEW=True`
- `GENERATION_BLOCK_REASON=generate_integration_not_enabled_v0.7.73`
- `APPLIED_DECISIONS_JSON_CREATED=False`
- `DOCUMENT_LEARNING_PACK_REBUILD=False`
- `GENERATE_INTEGRATION=NOT_CHANGED`

## Explicit non-goals

This milestone does not apply decisions.

It does not create `ocr_review_decisions.applied.json`.

It does not create `ocr_review_decisions.applied.md`.

It does not call `ocr_review_decision_apply.py`.

It does not rebuild `document_learning_pack.json`.

It does not change `/generate`.

It does not approve generation.

It does not regenerate course, quiz, flashcards, glossary, Study, Progress, OCR, or OCR Math.

## Policy

Owner-local OCR Review final confirm button only.
Write final confirmation only to `ocr_review_decisions.json`.
No apply patch.
No applied decisions artifact.
No learning pack rebuild.
No `/generate` integration.
No course regeneration.
No build.
No ZIP.
No share.
No delivery.
No distribution.

## Tester decision

Tester readiness remains BLOCKED.

DO NOT package for testers.
DO NOT create ZIP.
DO NOT share.
DO NOT deliver.
DO NOT distribute.
