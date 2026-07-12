# v0.7.59 Owner-local active course generation quality root-cause audit

Status: ROOT_CAUSE_IDENTIFIED / NOT FIXED

Marker:
VOILA_V0_7_59_ACTIVE_COURSE_GENERATION_QUALITY_ROOT_CAUSE_AUDIT_CHECK=PASS_ROOT_CAUSE_IDENTIFIED

Evidence root:
D:\dev\tester-runs\voila-v0.7.59-owner-local-active-course-generation-quality-root-cause-audit-no-build-no-zip-no-delivery

Evidence files:
- V0.7.59-REPO-BASELINE.json
- V0.7.59-ACTIVE-ARTIFACT-TIMELINE.json
- V0.7.59-RUNTIME-GENERATION-SOURCE-HITS.json
- V0.7.59-RUNTIME-GENERATION-HOT-SNIPPETS.json
- V0.7.59-READONLY-COURSE-GENERATOR-SIMULATION.json
- V0.7.59-COURSE-GENERATOR-FOCUSED-WINDOW.txt
- V0.7.59-WEBAPP-GENERATE-ROUTE-WINDOW.txt
- V0.7.59-OCR-MATH-HOOK-WINDOW.txt
- V0.7.59-OCR-REPORT-WINDOW.txt
- V0.7.59-NORMALIZED-OUTLINE-COMPARE.json
- V0.7.59-GENERATE-STEP-PRESENCE-AUDIT.json
- V0.7.59-NORMALIZE-OUTLINE-LESSON-DIFF.json
- V0.7.59-NORMALIZE-OUTLINE-SOURCE-WINDOW.txt

## Scope

This milestone is an audit only.

It investigates the active-course quality blockers recorded by v0.7.58:

- quiz too thin
- empty flashcards
- empty glossary
- missing ocr_report.json
- no active OCR Math available-state coverage

This milestone does not patch product behavior.

## Policy

No product patch.
No regeneration.
No destructive data change.
No build.
No ZIP.
No share.
No delivery.
No distribution.

## Active local course under audit

Course:

`03-pag-30-34-vectori-trigonometrie.pdf`

Active artifact timeline:

- `pages.json`: exists
- `course_outline.json`: exists
- `course_outline.normalized.json`: exists
- `course.md`: exists
- `course.cleaned.md`: exists
- `course.cleaned.html`: exists
- `quiz.json`: exists, but contains only 1 item
- `flashcards.json`: exists, but is `[]`
- `glossary.json`: exists, but is `[]`
- `ocr_report.json`: missing
- `ocr_math_report.md`: missing
- `ocr_math_report.json`: missing

All active generation files were created in the same timestamp window, so the evidence points to a generated minimal/incomplete state, not later corruption.

## Root cause 1: quiz too thin

The real `/generate` route runs `generate_for_pdf`.

The generation steps in `generate_for_pdf` are:

1. `pdf_extract.py`
2. `outline_builder.py`
3. `normalize_outline.py`
4. `course_generator.py`
5. `course_polisher.py`

The route passes this file to `course_generator.py`:

`course_outline.normalized.json`

The normalized-outline comparison confirmed:

- `course_outline.json`: 2 lessons, simulated quiz count 2
- `course_outline.normalized.json`: 1 lesson, simulated quiz count 1
- active `quiz.json`: 1 item
- normalized simulation matches active quiz count

Therefore the active quiz is thin because the real pipeline uses the normalized outline, and the normalized outline contains only one lesson.

## Root cause 2: normalize_outline reduces the active course from 2 lessons to 1

Lesson diff evidence:

Original `course_outline.json`:

- L001: `Opening Section`, word_count 19
- L002: `Se numeşte vector, mulţimea tuturor segmentelor`, word_count 783

Normalized `course_outline.normalized.json`:

- L001: `Se numeşte vector, mulţimea tuturor segmentelor`, word_count 783

Removed or merged lesson id:

- L002

The apparent L002 removal is caused by renumbering. The original L001 is removed because `normalize_outline.py` skips lessons with `word_count < 20`; then the original L002 is renumbered to L001.

Relevant rule in `normalize_outline.py`:

`if word_count < 20: continue`

This is not necessarily wrong by itself, because the removed section is only 19 words. But it explains why the active normalized course has one lesson and why the generated quiz has only one item.

## Root cause 3: flashcards and glossary are empty

`course_generator.py` builds glossary and flashcards from `find_terms(text)`.

The `TECHNICAL_TERMS` dictionary in `course_generator.py` is English/marine-engineering focused, with terms such as:

- steam trap
- pumping trap
- vacuum trap
- non-return valve
- exhaust valve
- steam valve
- float
- spindle
- strainer
- bilge system

The active PDF is Romanian mathematics content about vectori/trigonometrie.

Because the term dictionary does not cover Romanian mathematics terms, `find_terms(text)` finds no terms.

The read-only simulation confirmed:

- terms not detected
- glossary count 0
- flashcards count 0

Since `make_flashcards()` depends on terms and figures, and there are no detected terms/figures, `flashcards.json` becomes `[]`.

## Root cause 4: ocr_report.json is missing

`ocr_report.py` exists and writes `ocr_report.json`.

However, `generate_for_pdf` does not call `ocr_report.py`.

The generate step presence audit confirmed:

`generate_for_pdf_calls_ocr_report=False`

Therefore `ocr_report.json` is missing because the active `/generate` pipeline does not include the OCR report generation step.

## Root cause 5: OCR Math report is missing

`ocr_math_report_hook.py` exists and can write:

- `ocr_math_report.json`
- `ocr_math_report.md`

The hook is explicitly owner-local and safe, but only runs when called/enabled.

However, `generate_for_pdf` does not call `ocr_math_report_hook.py`.

The generate step presence audit confirmed:

- `generate_for_pdf_calls_ocr_math_report_hook=False`
- `generate_for_pdf_mentions_VOILA_ENABLE_OCR_MATH_REPORT_HOOK=False`

Therefore the active OCR Math report is missing because the real `/generate` pipeline does not include the OCR Math hook.

## Final root-cause decision

Root cause is identified.

The active course is not tester-ready because generation quality is currently minimal for this Romanian mathematics PDF.

The problem is not a navigation issue.

The problem is not Course Tools hang.

The problem is not raw JavaScript visibility.

The root causes are:

1. normalized outline has only one lesson
2. rule-based generator is English/marine-term focused
3. generated study assets depend on detected terms/figures
4. OCR report generation is not part of `/generate`
5. OCR Math report hook is not part of `/generate`

## Recommended next milestone

Do not patch in v0.7.59.

Recommended next milestone:

`v0.7.60-owner-local-generation-quality-contract-and-fix-plan-no-build-no-zip-no-delivery`

Purpose:

- define minimum active-course quality contract before tester packaging
- decide whether Romanian math fallback terms/questions are required
- decide whether flashcards/glossary should have generic fallback generation
- decide whether `ocr_report.py` should be inserted into `/generate`
- decide whether OCR Math hook should remain explicit owner-local opt-in or be included in owner-local generate path behind the existing env flag
- define validation thresholds before any tester ZIP

## Explicit tester decision

DO NOT package for testers.
DO NOT create ZIP.
DO NOT share.
DO NOT deliver.
DO NOT distribute.

## Explicitly unchanged

No product patch.
No route change.
No normalize_outline change.
No course_generator change.
No OCR report integration.
No OCR Math hook integration.
No regeneration.
No destructive data change.
No build.
No ZIP.
No share.
No delivery.
No distribution.
