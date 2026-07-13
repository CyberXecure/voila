# v0.7.65 Owner-local OCR Review queue artifact builder

Status: PASS_QUEUE_ARTIFACT_BUILDER

Marker:
VOILA_V0_7_65_OCR_REVIEW_QUEUE_ARTIFACT_BUILDER_CHECK=PASS

Baseline:
v0.7.64 completed and merged to protected main at `df9e984`.

## Purpose

Voila must learn the document before it teaches it.

If automatic document learning sees uncertain OCR/OCR Math evidence, Voila should create a guided review queue instead of silently generating a weak course.

OCR Review is user-assisted document learning.

User corrections should become verified evidence for future document concepts and document learning pack generation.

## Scope

This milestone adds a local artifact builder:

`services/api/ocr_review_queue.py`

It creates:

- `ocr_review_queue.json`
- `ocr_review_queue.md`

The builder reads:

- `pages.json`
- optional `document_concepts.json`

It does not implement UI.

It does not integrate with `/generate`.

## Real active course smoke

Real active course:

`data\output\03-pag-30-34-vectori-trigonometrie`

Input:

- `pages.json`
- v0.7.63 real-course `document_concepts.json`

Observed output:

- `OCR_REVIEW_QUEUE_ARTIFACT=PASS`
- `review_item_count=20`
- `review_required=True`
- `generation_should_wait_for_review=True`

## Review item examples

The real queue includes review items for:

- broken formula lines
- uncertain OCR Math fragments
- definition candidates
- notation candidates
- theorem-like fragments
- trigonometric function formulas
- possible OCR spacing issues such as `vectoruluiv`
- legacy/uncertain OCR text around Romanian math material

Examples include:

- vector modulus formula line
- scalar/vector formula fragments
- collinearity expressions
- coordinates in a basis
- versors of coordinate axes
- scalar product formulas
- trigonometric function ranges

## Artifact contract

Each review item includes:

- `review_item_id`
- `source_pdf_page`
- `source_text`
- `suspect_text`
- `suggested_text`
- `issue_type`
- `confidence`
- `reason_codes`
- `suggested_learning_role`
- `linked_concept_terms`
- `ocr_math_context`
- `requires_user_decision`
- `allowed_decisions`

## Learning policy

The artifact records that:

- OCR Review is user-assisted document learning
- user corrections become verified evidence
- corrections feed back into future `document_learning_pack.json`
- unresolved blocked review items must not be treated as reliable learning material

## Future UI expectation

A future UI should show these review items in a simple guided flow.

The user should not inspect JSON manually.

The UI should support easy decisions such as:

- accept
- edit
- ignore
- mark as definition
- mark as formula
- mark as notation
- mark as theorem
- mark as example
- mark as glossary term
- mark as not relevant

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
