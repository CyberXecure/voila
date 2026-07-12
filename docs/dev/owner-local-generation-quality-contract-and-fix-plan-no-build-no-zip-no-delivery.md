# v0.7.60 Owner-local generation quality contract and fix plan

Status: PLAN_ONLY / CONTRACT_DEFINED / NOT_FIXED

Marker:
VOILA_V0_7_60_GENERATION_QUALITY_CONTRACT_AND_FIX_PLAN_CHECK=PASS_PLAN_ONLY

Baseline:
v0.7.59 completed and merged to protected main at `cf75d6c`.

## Scope

This milestone defines the generation-quality contract and fix plan after v0.7.59 identified the active-course root cause.

This milestone does not patch product behavior.

## Policy

No product patch.
No route change.
No generator change.
No OCR pipeline change.
No OCR Math hook integration.
No regeneration.
No destructive data change.
No build.
No ZIP.
No share.
No delivery.
No distribution.

## User decision

The static `TECHNICAL_TERMS` dictionary is not acceptable as the primary generator knowledge source.

It was effectively adapted to the first Voila PDF domain: marine/steam/auxiliary machinery.

Voila must instead learn/extract concepts from each OCR-recognized PDF.

For every PDF, Voila should derive document-specific knowledge first, then generate:

- lessons
- glossary
- flashcards
- quiz
- study/progress material

## Required generation order

Target order:

1. PDF input
2. OCR extraction
3. OCR text cleanup / correction signal analysis
4. language and domain detection
5. document concept extraction
6. optional source-language preservation plus translated pedagogical explanation
7. document-specific glossary
8. document-specific flashcards
9. document-specific quiz
10. lessons generated from the document concept map

Lessons should not be generated first from a fixed domain dictionary.

## New conceptual artifact: document concept map

Future implementation should introduce a document-derived concept map.

Proposed artifact names:

- `document_concepts.json`
- `document_concepts.md`

The concept map should include, when available:

- source language
- detected domain
- terms
- definitions
- formulas
- symbols
- examples
- procedures
- named concepts
- concept relationships
- source page references
- OCR confidence / OCR risk markers
- translation or explanation fields, when enabled

For Romanian mathematics PDFs, examples of expected extracted concepts include:

- vector
- segment orientat
- direcție
- sens
- modul
- coordonate
- origine
- extremitate
- coliniaritate
- trigonometrie

These examples are not a hardcoded final dictionary. They are examples of the type of document-specific concepts the extractor should learn from OCR text.

## Static dictionary role

The existing static `TECHNICAL_TERMS` dictionary may remain only as:

- a legacy seed
- a domain-specific fallback for old marine test PDFs
- a test fixture

It must not be the primary generator knowledge source.

## Translation policy

Voila should preserve the original source language.

If translation/explanation is enabled, it should be additive:

- original OCR/source text remains available
- translated explanation may be stored separately
- glossary may include source term and translated pedagogical explanation
- generated study material should be clear in the selected UI/study language

Translation must not erase the source.

## Minimum quality contract before tester readiness

For a readable OCR-recognized PDF, tester readiness should require more than file existence.

Candidate minimums before tester package:

- `course.cleaned.html` exists and opens
- `ocr_report.json` exists
- concept extraction ran and produced a non-empty concept map
- glossary is non-empty when the PDF contains definitions/concepts
- flashcards are non-empty when glossary/concepts are present
- quiz contains multiple useful questions, not only one generic question
- Study page is populated from meaningful questions
- Progress page reflects meaningful question/concept coverage
- OCR Math status is explicit: generated, disabled by policy, or not applicable

A missing or empty result must be surfaced as LOW_QUALITY/BLOCKED, not silently treated as tester-ready.

## Quality failure behavior

If concept extraction cannot find enough concepts, Voila should report:

- `generation_quality_status=LOW_QUALITY_BLOCKED`
- reason codes
- affected artifacts
- suggested next action

It should not pretend that `quiz.json`, `flashcards.json`, and `glossary.json` are good only because files exist.

## Root causes from v0.7.59 to address later

Root cause 1:

Quiz too thin because the normalized outline reduces the active course to one lesson and the generator runs on `course_outline.normalized.json`.

Root cause 2:

Flashcards and glossary are empty because `course_generator.py` depends on an English/marine technical-terms dictionary and does not extract Romanian mathematics concepts from the PDF.

Root cause 3:

`ocr_report.json` is missing because `generate_for_pdf` does not call `ocr_report.py`.

Root cause 4:

OCR Math report is missing because `generate_for_pdf` does not call `ocr_math_report_hook.py`.

## Proposed implementation plan after this milestone

Do not implement in v0.7.60.

Recommended next product milestones:

1. Add read-only generation quality contract checks.
2. Add document concept extraction artifact.
3. Add Romanian/math-friendly concept extraction fallback.
4. Generate glossary from document concepts.
5. Generate flashcards from glossary and concepts.
6. Generate quiz from concepts, definitions, formulas, examples, and pages.
7. Integrate `ocr_report.py` into the owner-local generate pipeline.
8. Decide whether OCR Math report remains explicit opt-in or becomes owner-local generate hook behind the existing environment flag.
9. Add a final tester readiness gate requiring content quality, not only navigation success.

## Tester decision

Tester readiness remains BLOCKED.

DO NOT package for testers.
DO NOT create ZIP.
DO NOT share.
DO NOT deliver.
DO NOT distribute.

## Explicitly unchanged

No product patch.
No route change.
No generator change.
No OCR report integration.
No OCR Math hook integration.
No regeneration.
No destructive data change.
No build.
No ZIP.
No share.
No delivery.
No distribution.
