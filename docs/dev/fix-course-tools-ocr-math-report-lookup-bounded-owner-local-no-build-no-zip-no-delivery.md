# v0.7.56 Fix Course Tools OCR Math report lookup bounded

Status: COMPLETED / COURSE TOOLS HANG FIXED / RESIDUAL RAW JS BLOCKER REMAINS

Marker:
VOILA_V0_7_56_FIX_COURSE_TOOLS_OCR_MATH_REPORT_LOOKUP_BOUNDED_CHECK=PASS

Evidence root:
D:\dev\tester-runs\voila-v0.7.56-fix-course-tools-ocr-math-report-lookup-bounded-owner-local-no-build-no-zip-no-delivery

Evidence files:
- V0.7.56-BOUNDED-OCR-MATH-LOOKUP-HTTP-EVIDENCE.json
- V0.7.56-DIRECT-OCR-MATH-LOOKUP-RESULT.json
- V0.7.56-SOURCE-BOUNDED-LOOKUP-EVIDENCE.json

## Scope

This milestone fixes the Course Tools hang root cause found in v0.7.55.

It bounds OCR Math report lookup and removes the unbounded recursive fallback scan from `_voila_ocr_math_report_paths()`.

## Fixed behavior

Before v0.7.56, `/course-tools?pdf=03-pag-30-34-vectori-trigonometrie.pdf` timed out even at 60 seconds.

After v0.7.56:

- `/course-tools?pdf=03-pag-30-34-vectori-trigonometrie.pdf` returns HTTP 200 quickly
- missing OCR Math report lookup returns quickly as unavailable
- OCR Math missing report view returns HTTP 404 quickly
- Quick Tools still returns HTTP 200 quickly

## Direct lookup validation

Direct OCR Math lookup for the tested course:

- elapsed: under 1000 ms
- `md`: null
- `json`: null
- `expected_missing_fast`: true

## Source validation

Source evidence confirms:

- `root.rglob("ocr_math_report.md")` block removed from `_voila_ocr_math_report_paths()`
- v0.7.56 bounded lookup marker is present
- missing OCR Math reports must return quickly as unavailable

## Visual validation

Manual browser validation confirmed:

- `Instrumente curs` opens
- Course Tools page is visible
- OCR Math card is shown as unavailable instead of blocking the page

## Known residual blocker

Raw JavaScript is still visible at the bottom of the Course Tools page.

This milestone does not fix the raw JavaScript rendering issue.

The raw JavaScript issue must be handled in a separate milestone before tester packaging.

## Tester decision

DO NOT package for testers yet.
DO NOT create ZIP.
DO NOT share.
DO NOT deliver.

## Explicitly unchanged

No raw JavaScript fix.
No import click.
No import logic change.
No OCR text rewrite.
No Course rewrite.
No Study rewrite.
No Progress rewrite.
No build.
No ZIP.
No share.
No delivery.
No distribution.
