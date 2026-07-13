# v0.7.69 Owner-local OCR Review user decision apply helper

Status: PASS_UNCONFIRMED_PATCH_SMOKE

Marker:
VOILA_V0_7_69_OCR_REVIEW_USER_DECISION_APPLY_HELPER_CHECK=PASS_UNCONFIRMED_PATCH_SMOKE

Baseline:
v0.7.68 completed and merged to protected main at `4715435`.

## Purpose

This milestone adds a local helper that can apply an explicit OCR Review decision patch to `ocr_review_decisions.json`.

The helper is a local bridge toward future guided OCR Review UI.

It does not implement UI.

It does not integrate with `/generate`.

It does not regenerate the active course.

## Scope

This milestone adds:

`services/api/ocr_review_decision_apply.py`

It reads:

- `ocr_review_decisions.json`
- an explicit decision patch JSON

It writes:

- `ocr_review_decisions.applied.json`
- `ocr_review_decisions.applied.md`

## Decision patch model

A decision patch can contain:

- `review_item_id`
- `decision`
- `corrected_text`
- `confirmed_learning_role`
- `user_note`

Supported decisions:

- `pending`
- `accepted`
- `edited`
- `ignored`
- `marked_definition`
- `marked_formula`
- `marked_notation`
- `marked_theorem`
- `marked_example`
- `marked_glossary_term`
- `marked_not_relevant`

## Real user decision policy

A patch is treated as real user review only when both flags are true:

- `owner_review_confirmed=True`
- `real_user_decisions_performed=True`

If those flags are not both true, the patch is treated as synthetic or unconfirmed.

Synthetic or unconfirmed patches are not verified user evidence.

Real user review is still required for actual delivery.

## Smoke

The local smoke uses the v0.7.66 real-course pending `ocr_review_decisions.json`.

It applies an unconfirmed smoke patch for 3 items:

- `R001`
- `R003`
- `R020`

Observed output:

- `OCR_REVIEW_USER_DECISION_APPLY_HELPER=PASS`
- `decision_count=20`
- `applied_patch_decision_count=3`
- `pending_decision_count=17`
- `resolved_decision_count=3`
- `all_required_decisions_resolved=False`
- `generation_should_wait_for_review=True`
- `real_user_decisions_performed=False`
- `synthetic_or_unconfirmed_patch=True`

## Important interpretation

The helper successfully applies selected decisions.

However, the smoke patch is not real user review.

Therefore:

- unresolved decisions remain pending
- generation should still wait
- the applied smoke patch is not verified user evidence
- tester readiness remains blocked

## Learning policy

The applied artifact records:

- OCR Review is user-assisted document learning
- user corrections become verified evidence only for real confirmed user patches
- synthetic or unconfirmed patches are not verified evidence
- real user review is required for actual delivery
- pending decisions are not verified evidence

## Policy

No `/generate` route change.
No UI implementation.
No active course regeneration.
No lesson generation change.
No quiz generation change.
No flashcards generation change.
No glossary generation change.
No OCR rewrite.
No OCR Math rewrite.
No real user review performed in the smoke.
No real generation approval.
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
