# v0.7.72 Owner-local OCR Review guided decision buttons

Status: PASS_GUIDED_DECISION_BUTTONS_WRITE_DECISIONS_ONLY

Marker:
VOILA_V0_7_72_OCR_REVIEW_GUIDED_DECISION_BUTTONS_CHECK=PASS

Baseline:
v0.7.71 completed and merged to protected main at `6aba2af`.

## Purpose

This milestone adds guided decision buttons to the owner-local OCR Review page.

The owner no longer needs to edit JSON manually for individual OCR Review decisions.

## Routes

Existing read/display route:

`/owner/ocr-review/{course_id}`

New guided decision write route:

`/owner/ocr-review/{course_id}/decision`

The POST route writes only to:

`ocr_review_decisions.json`

## Guided decisions

The page now exposes guided buttons:

- Acceptă sugestia
- Editează textul
- Ignoră
- Este definiție
- Este formulă
- Este notație
- Este teoremă
- Este exemplu
- Este termen de glosar
- Nu este relevant

`Editează textul` requires a corrected text field.

## Write behavior

A saved guided decision updates one matching decision item in `ocr_review_decisions.json`.

The saved decision records:

- `decision`
- `corrected_text`
- `user_note`
- `requires_user_decision=false`
- `real_user_decision=true`
- `decision_source=owner_local_guided_ui_v0.7.72`
- `applied_to_learning_pack=false`
- `updated_at`

The artifact summary is updated:

- `decision_count`
- `pending_decision_count`
- `resolved_decision_count`
- `real_user_decisions_performed=true`
- `owner_review_confirmed=false`
- `applied_to_learning_pack=false`

The quality gate remains blocked until final confirmation:

- `generation_should_wait_for_review=true`
- `owner_review_confirmed=false`
- `generation_block_reason=owner_review_not_final_confirmed`

## Direct smoke

Smoke evidence used a short Windows path to avoid path length failure:

`D:\dev\tester-runs\v0772-ocr-review-buttons`

HTML before:

`D:\dev\tester-runs\v0772-ocr-review-buttons\before.html`

HTML after:

`D:\dev\tester-runs\v0772-ocr-review-buttons\after.html`

Smoke result:

- `VOILA_V0_7_72_GUIDED_DECISION_BUTTONS_SMOKE=PASS`
- `POST_ROUTE=/owner/ocr-review/{course_id}/decision`
- `POST_STATUS=303`
- `DECISION_WRITE_TARGET=ocr_review_decisions.json`
- `UPDATED_REVIEW_ITEM=R001`
- `UPDATED_DECISION=accepted`
- `PENDING_DECISION_COUNT_AFTER=19`
- `RESOLVED_DECISION_COUNT_AFTER=1`
- `REAL_USER_DECISIONS_PERFORMED=True`
- `OWNER_REVIEW_CONFIRMED=False`
- `GENERATION_SHOULD_WAIT_FOR_REVIEW=True`
- `APPLIED_DECISIONS_JSON_CREATED=False`
- `DOCUMENT_LEARNING_PACK_REBUILD=False`
- `GENERATE_INTEGRATION=NOT_CHANGED`

## Explicit non-goals

This milestone does not apply the decisions to generated learning material.

It does not create `ocr_review_decisions.applied.json`.

It does not create `ocr_review_decisions.applied.md`.

It does not call `ocr_review_decision_apply.py`.

It does not rebuild `document_learning_pack.json`.

It does not approve generation.

It does not change `/generate`.

It does not regenerate course, quiz, flashcards, glossary, Study, Progress, OCR, or OCR Math.

## Policy

Owner-local OCR Review guided decision buttons only.
Write decisions only to `ocr_review_decisions.json`.
No apply patch.
No applied decisions artifact.
No learning pack rebuild.
No final owner confirmation.
No generation approval.
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
