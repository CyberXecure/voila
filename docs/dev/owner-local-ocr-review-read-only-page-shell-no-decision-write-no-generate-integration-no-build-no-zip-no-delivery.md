# v0.7.71 Owner-local OCR Review read-only page shell

Status: PASS_READ_ONLY_PAGE_SHELL

Marker:
VOILA_V0_7_71_OCR_REVIEW_READ_ONLY_PAGE_SHELL_CHECK=PASS

Baseline:
v0.7.70 completed and merged to protected main at `a8340a5`.

## Purpose

This milestone adds the first owner-local guided OCR Review page shell.

The page is read-only.

It helps the owner see OCR Review status without editing JSON manually.

It does not write decisions.

It does not apply patches.

It does not rebuild the document learning pack.

It does not call `/generate`.

## Route

Added owner-local read-only route:

`/owner/ocr-review/{course_id}`

The route reads local artifacts from the course output directory:

- `ocr_review_queue.json`
- `ocr_review_decisions.json`

## Display contract implemented

The read-only shell displays:

- course id
- review item count
- decision count
- pending decision count
- resolved decision count
- `generation_should_wait_for_review`
- `all_required_decisions_resolved`
- diagnostic message when required artifacts are missing
- review item cards

Each review card displays:

- review item id
- source PDF page
- issue type
- suggested learning role
- linked concept terms
- source OCR text
- suggested text
- current decision

## Real route smoke

The direct route smoke used copied owner-local evidence:

- v0.7.65 real-course `ocr_review_queue.json`
- v0.7.66 real-course `ocr_review_decisions.json`

Smoke result:

- `VOILA_V0_7_71_DIRECT_ROUTE_SMOKE=PASS`
- `HTTP_STATUS=200`
- `REVIEW_ITEM_COUNT=20`
- `DECISION_COUNT=20`
- `PENDING_DECISION_COUNT=20`
- `RESOLVED_DECISION_COUNT=0`
- `GENERATION_SHOULD_WAIT_FOR_REVIEW=True`
- `ALL_REQUIRED_DECISIONS_RESOLVED=False`
- `READ_ONLY_NO_DECISION_WRITE=PASS`

HTML smoke artifact:

`D:\dev\tester-runs\voila-v0.7.71-owner-local-ocr-review-read-only-page-shell-no-decision-write-no-generate-integration-no-build-no-zip-no-delivery\owner-ocr-review-read-only-route-smoke.html`

## Important limitation

This page is a shell only.

It has no decision buttons.

It has no forms.

It has no POST route.

It does not write `ocr_review_decisions.json`.

It does not create `ocr_review_decisions.applied.json`.

It does not call `ocr_review_decision_apply.py`.

It does not rebuild `document_learning_pack.json`.

It does not approve generation.

## Generation gate behavior

For the current smoke course, the page correctly shows:

`generation_should_wait_for_review=True`

and:

`all_required_decisions_resolved=False`

because 20 OCR Review decisions are still pending.

## Policy

Read-only page shell only.
No decision write.
No decision patch apply.
No learning pack rebuild.
No route POST.
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
