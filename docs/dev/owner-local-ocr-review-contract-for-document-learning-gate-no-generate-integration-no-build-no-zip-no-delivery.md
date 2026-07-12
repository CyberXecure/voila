# v0.7.64 Owner-local OCR Review contract for document learning gate

Status: PASS_CONTRACT_ONLY

Marker:
VOILA_V0_7_64_OCR_REVIEW_CONTRACT_FOR_DOCUMENT_LEARNING_GATE_CHECK=PASS

Baseline:
v0.7.63 completed and merged to protected main at `f8ea780`.

## Purpose

Voila must learn the document before it teaches it.

If automatic document learning is blocked, the next step must not be a superficial course.

The next step must be a guided OCR Review flow.

OCR Review is not only OCR cleanup.

OCR Review is user-assisted document learning.

The user's corrections help Voila understand the source document before course generation.

## Core rule

Future flow:

1. OCR recognized text
2. OCR Math / formulas / symbols
3. document concepts
4. document learning pack
5. quality gate
6. if blocked: guided OCR Review
7. rebuild document concepts / document learning pack
8. generate course only after the learning gate passes

## User-friendly requirement

The OCR Review flow must be easy for a non-technical user.

It must not expose raw technical artifacts as the main interaction.

It must guide the user through focused review items.

The user should see:

- page context
- suspect OCR line or formula
- extracted interpretation
- reason why Voila is unsure
- simple available actions

## Minimum user actions

Future OCR Review should support at least:

- Accept
- Edit
- Ignore
- Mark as definition
- Mark as formula
- Mark as notation
- Mark as theorem
- Mark as example
- Mark as glossary term
- Mark as not relevant

## Review item contract

Future `ocr_review_queue.json` should contain review items with at least:

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

Expected issue types include:

- `ocr_text_uncertain`
- `ocr_math_uncertain`
- `definition_candidate_uncertain`
- `formula_candidate_uncertain`
- `notation_candidate_uncertain`
- `concept_relation_uncertain`
- `low_confidence_symbol`
- `broken_line_join`
- `legacy_diacritic_or_encoding`

Expected learning roles include:

- `definition`
- `formula`
- `notation`
- `theorem`
- `example`
- `glossary_term`
- `ignore`

## User decision contract

Future `ocr_review_decisions.json` should contain at least:

- `review_item_id`
- `decision`
- `corrected_text`
- `confirmed_learning_role`
- `user_note`
- `source_pdf_page`
- `applied_to_learning_pack`
- `created_at`

Expected decisions include:

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

## Learning integration contract

Future reviewed items must feed the document learning process.

A user correction must become verified evidence for:

- document concepts
- OCR Math interpretation
- formula extraction
- concept relations
- glossary candidates
- flashcard candidates
- quiz candidates
- teaching plan

Corrected/reviewed material should be represented in future `document_learning_pack.json` as user-verified evidence.

The course generator should not use unresolved blocked review items as if they were reliable learning material.

## Quality gate behavior

If the document learning gate is blocked because of OCR/OCR Math uncertainty, Voila should produce a review queue.

Generation should remain blocked until either:

- the review queue is resolved enough for the learning gate to pass
- the user explicitly ignores low-priority items
- Voila can rebuild a sufficient document learning pack from verified evidence

## What the UI should avoid

The OCR Review UI should avoid:

- raw JSON as the main user experience
- asking the user to inspect internal files
- showing too many items at once
- requiring technical OCR knowledge
- silently continuing to generate weak lessons
- hiding formulas or symbols that affected learning quality

## Good UX behavior

The OCR Review UI should:

- show one focused issue at a time
- show the PDF page context
- highlight the suspect line or formula
- show Voila's suggested interpretation
- use simple Romanian labels
- support keyboard-free correction where possible
- allow quick accept/ignore/edit
- explain why the item matters for course generation
- show progress through the review queue
- rerun learning analysis after review

## Scope

This milestone is contract-only.

It does not implement the OCR Review UI.

It does not create new web routes.

It does not integrate with `/generate`.

It does not regenerate the active course.

It does not modify OCR or OCR Math extraction.

It records the future artifact and UX contract only.

## Policy

No `/generate` route change.
No active course regeneration.
No lesson generation change.
No quiz generation change.
No flashcards generation change.
No glossary generation change.
No OCR rewrite.
No OCR Math rewrite.
No UI implementation.
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

## Next recommended milestone

`v0.7.65-owner-local-ocr-review-queue-artifact-builder-no-ui-no-generate-integration-no-build-no-zip-no-delivery`

Goal:

Create the first owner-local review queue artifact from document learning/OCR evidence, still without UI and without `/generate` integration.
