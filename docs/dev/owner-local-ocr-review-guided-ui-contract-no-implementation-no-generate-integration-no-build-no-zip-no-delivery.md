# v0.7.70 Owner-local OCR Review guided UI contract

Status: PASS_CONTRACT_ONLY_NO_IMPLEMENTATION

Marker:
VOILA_V0_7_70_OCR_REVIEW_GUIDED_UI_CONTRACT_CHECK=PASS_CONTRACT_ONLY

Baseline:
v0.7.69 completed and merged to protected main at `6f54da9`.

## Purpose

OCR Review must be easy enough for a non-technical owner/user.

The user should not edit JSON manually.

This milestone defines the guided UI contract before implementation.

No UI is implemented in this milestone.

No `/generate` integration is implemented in this milestone.

## Existing artifact chain

The guided OCR Review UI must use the existing owner-local artifacts:

1. `ocr_review_queue.json`
2. `ocr_review_decisions.json`
3. explicit user decision patch
4. `ocr_review_decisions.applied.json`
5. `document_learning_pack.json`

Relevant existing modules:

- `services/api/ocr_review_queue.py`
- `services/api/ocr_review_decisions.py`
- `services/api/ocr_review_decision_apply.py`
- `services/api/document_learning_pack.py`

## Target user experience

The UI should feel like a guided review checklist.

The user sees one suspicious OCR/OCR Math item at a time, or a compact list of items grouped by page.

The UI must explain why each item needs review.

The user must be able to make a decision without understanding JSON.

## Proposed owner-local route contract

Future implementation may add an owner-local route such as:

`/owner/ocr-review/{course_id}`

This milestone does not add the route.

The route must be owner-local only.

The route must not be public tester functionality until explicitly approved.

## Page-level layout contract

The guided UI should include:

- course title/source PDF
- OCR Review status
- total review items
- pending decisions
- resolved decisions
- generation gate status
- clear warning when generation must wait
- page filter
- learning role filter
- review item cards
- final confirmation section

## Review item card contract

Each review card should show:

- review item id
- source PDF page
- issue type
- suggested learning role
- linked concept terms
- source text
- suggested text
- OCR/OCR Math reason
- current decision status
- corrected text editor when needed
- user note field

The card must make it clear whether the item affects:

- definition
- formula
- notation
- theorem
- example
- glossary term
- not relevant material

## Allowed user decisions

The UI must support these decisions:

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

The UI may also display `pending`, but `pending` is not a final resolved decision.

## Button contract

Each review card should have simple Romanian-friendly actions:

- `Acceptă sugestia`
- `Editează textul`
- `Ignoră`
- `Este definiție`
- `Este formulă`
- `Este notație`
- `Este teoremă`
- `Este exemplu`
- `Este termen de glosar`
- `Nu este relevant`

The final UI copy may be bilingual later, but Romanian labels are required for owner-local testing.

## Correction editor contract

For `edited`, the UI must require corrected text.

The editor should show:

- original OCR text
- suggested text
- editable corrected text
- optional user note

The UI must not allow `edited` with empty corrected text.

## Real user confirmation contract

The UI must not silently treat changes as real user decisions.

Before applying final decisions, the UI must show a confirmation step.

The explicit patch must include:

- `owner_review_confirmed=True`
- `real_user_decisions_performed=True`

Only then may decisions become real verified user evidence.

If these flags are missing or false, the patch remains synthetic or unconfirmed.

## Generation gate contract

If any required decision remains pending:

- generation must remain blocked
- `generation_should_wait_for_review=True`
- `all_required_decisions_resolved=False`
- tester readiness remains blocked

If all required decisions are resolved with real confirmed user review:

- `all_required_decisions_resolved=True`
- `generation_should_wait_for_review=False`
- user corrections may become verified evidence
- document learning pack may be rebuilt

This milestone does not integrate that gate into `/generate`.

## Learning pack feedback contract

After real confirmed decisions are applied, the future flow should rebuild:

`document_learning_pack.json`

The rebuilt pack should include:

- document concepts
- OCR Review resolution summary
- verified user evidence
- teaching plan candidates
- quality gate result

Pending, synthetic, or unconfirmed decisions must not be treated as verified evidence.

## Empty state contract

If no review is required, the UI should show:

- no OCR Review items require action
- document learning pack can proceed
- no manual correction is needed

The UI must still show that this was checked.

## Blocked state contract

If queue/decisions artifacts are missing, the UI should show a clear local diagnostic:

- missing `ocr_review_queue.json`
- missing `ocr_review_decisions.json`
- run/generate required prerequisite artifacts first

The UI must not silently continue.

## Safety contract

The UI must not:

- modify OCR source text directly
- rewrite `pages.json`
- rewrite original PDF artifacts
- regenerate lessons
- regenerate quiz
- regenerate flashcards
- regenerate glossary
- call `/generate`
- package for testers
- create ZIP
- share
- deliver
- distribute

## Future implementation order

Recommended future order:

1. read-only OCR Review page shell
2. render queue and pending decisions
3. per-item action form
4. local decision patch creation
5. apply helper integration
6. rebuild document learning pack
7. final gate summary
8. only later, guarded `/generate` integration

## Acceptance criteria for a future UI milestone

A future implementation milestone should prove:

- the page loads for a real course
- it shows 20 real review items for the current smoke course
- it shows 20 pending decisions before user action
- it can apply at least one real owner-confirmed decision
- it does not mark synthetic patches as real evidence
- it blocks generation while pending decisions remain
- it does not call `/generate`
- it does not build ZIP or deliver anything

## Policy

Contract only.
No UI implementation.
No route implementation.
No `/generate` route change.
No active course regeneration.
No lesson generation change.
No quiz generation change.
No flashcards generation change.
No glossary generation change.
No OCR rewrite.
No OCR Math rewrite.
No real user review performed.
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
