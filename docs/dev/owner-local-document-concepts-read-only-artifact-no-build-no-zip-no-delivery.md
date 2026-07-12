# v0.7.61 Owner-local document concepts read-only artifact

Status: IMPLEMENTED_LOCAL_ARTIFACT / NOT_INTEGRATED_IN_GENERATE

Marker:
VOILA_V0_7_61_DOCUMENT_CONCEPTS_READ_ONLY_ARTIFACT_CHECK=PASS

Baseline:
v0.7.60 completed and merged to protected main at `9e2fc86`.

## Scope

This milestone adds a small owner-local document concepts artifact builder.

New module:

`services/api/document_concepts.py`

New explicit CLI artifacts:

- `document_concepts.json`
- `document_concepts.md`

This milestone does not integrate the artifact into `/generate`.

## Policy

No `/generate` route change.
No lesson generation change.
No quiz generation change.
No flashcards generation change.
No glossary generation change.
No active course regeneration.
No destructive data change.
No build.
No ZIP.
No share.
No delivery.
No distribution.

## Purpose

v0.7.59 showed that Voila generated weak study assets because the generator depended on an English/marine static dictionary.

v0.7.60 defined the new direction:

Voila should extract document-specific concepts from each OCR-recognized PDF before generating lessons, glossary, flashcards, and quiz.

v0.7.61 adds the first small artifact toward that direction.

## Artifact behavior

`document_concepts.py` reads `pages.json`.

It detects:

- source language
- likely domain
- definition-like concepts
- document-specific concept count
- concept quality status

It writes:

- `document_concepts.json`
- `document_concepts.md`

## Quality behavior

The artifact includes:

`generation_quality_status`

Possible values in this first version:

- `PASS`
- `LOW_QUALITY_BLOCKED`

A low-quality extraction should be visible. It must not be silently treated as tester-ready.

## Translation policy

This milestone does not translate text.

It preserves source language.

Future translation/explanation must be additive, not a replacement for source OCR text.

## Validation

The validation uses a controlled owner-local fixture outside the repo under:

`D:\dev\tester-runs\voila-v0.7.61-owner-local-document-concepts-read-only-artifact-no-build-no-zip-no-delivery`

The fixture verifies Romanian mathematics concept extraction from OCR-like `pages.json`.

Observed result from the small CLI smoke:

- `DOCUMENT_CONCEPTS_ARTIFACT=PASS`
- `concept_count=3`
- `quality_status=PASS`
- `source_language=ro`
- `detected_domain=mathematics`

## Explicitly not changed

The following are intentionally unchanged:

- `/generate`
- `course_generator.py`
- `normalize_outline.py`
- `quiz.json`
- `flashcards.json`
- `glossary.json`
- `ocr_report.json` generation
- OCR Math hook integration
- tester packaging

## Tester decision

Tester readiness remains BLOCKED.

DO NOT package for testers.
DO NOT create ZIP.
DO NOT share.
DO NOT deliver.
DO NOT distribute.
