# v0.7.66 Owner-local OCR Review decisions artifact builder

Status: PASS_DECISIONS_ARTIFACT_BUILDER

Marker:
VOILA_V0_7_66_OCR_REVIEW_DECISIONS_ARTIFACT_BUILDER_CHECK=PASS

Baseline:
v0.7.65 completed and merged to protected main at `9b1a0b4`.

## Purpose

OCR Review is user-assisted document learning.

The review queue identifies OCR/OCR Math items that need user attention.

This milestone adds the companion decisions artifact.

The decisions artifact records the user decision state for each review item.

Pending decisions are not verified evidence.

Course generation should wait until required review decisions are resolved.

## Scope

This milestone adds a local artifact builder:

`services/api/ocr_review_decisions.py`

It creates:

- `ocr_review_decisions.json`
- `ocr_review_decisions.md`

The builder reads:

- `ocr_review_queue.json`

It does not implement UI.

It does not integrate with `/generate`.

## Real active course smoke

Input queue:

v0.7.65 real-course `ocr_review_queue.json`

Observed output:

- `OCR_REVIEW_DECISIONS_ARTIFACT=PASS`
- `decision_count=20`
- `pending_decision_count=20`
- `all_required_decisions_resolved=False`
- `generation_should_wait_for_review=True`

## Decision contract

Each decision item includes:

- `review_item_id`
- `decision`
- `allowed_decisions`
- `source_pdf_page`
- `source_text`
- `suggested_text`
- `corrected_text`
- `original_issue_type`
- `suggested_learning_role`
- `confirmed_learning_role`
- `linked_concept_terms`
- `user_note`
- `requires_user_decision`
- `applied_to_learning_pack`
- `created_at`
- `updated_at`

## Allowed decisions

The initial artifact supports:

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

## Learning policy

The artifact records that:

- OCR Review is user-assisted document learning
- user corrections become verified evidence
- corrections feed back into future `document_learning_pack.json`
- unresolved blocked review items must not be treated as reliable learning material
- pending decisions are not verified evidence

## Future UI expectation

A future UI should allow the user to resolve these pending decisions easily.

The user should not edit JSON manually.

The UI should let the user accept, edit, ignore, or mark each item as definition, formula, notation, theorem, example, glossary term, or not relevant.

After decisions are resolved, Voila should rebuild document concepts and the document learning pack.

Only then should course generation proceed.

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
