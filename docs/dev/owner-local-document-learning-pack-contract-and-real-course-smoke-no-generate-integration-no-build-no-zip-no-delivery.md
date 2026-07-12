# v0.7.62 Owner-local document learning pack contract and real course smoke

Status: PASS_CONTRACT_WITH_REAL_COURSE_BLOCKER

Marker:
VOILA_V0_7_62_DOCUMENT_LEARNING_PACK_CONTRACT_AND_REAL_COURSE_SMOKE_CHECK=PASS_BLOCKED

Baseline:
v0.7.61 completed and merged to protected main at `19644df`.

## Purpose

The user requirement is explicit:

Voila must analyze the recognized PDF in detail before generating the course.

In practical terms:

- first recognize the document through OCR text
- include OCR Math / formulas / symbols
- extract document-specific concepts
- understand definitions, relations, examples, notation, formulas, and dependencies
- only then generate lessons, glossary, flashcards, and quiz

This means Voila should first learn the document and only then teach it.

## Scope

This milestone is contract and real-course smoke only.

It does not change `/generate`.

It does not regenerate the active course.

It does not modify lesson, quiz, flashcards, or glossary generation.

It records the required future pre-generation artifact:

- `document_learning_pack.json`
- `document_learning_pack.md`

## Real active course

Real active course inspected:

`data\output\03-pag-30-34-vectori-trigonometrie`

Real source file:

`D:\dev\projects\voila\data\input\03-pag-30-34-vectori-trigonometrie.pdf`

Real `pages.json`:

- exists
- page count: 5
- bytes: 5203

## Real course document concepts smoke

`services/api/document_concepts.py` was run against the real active course `pages.json`.

Observed output:

- `DOCUMENT_CONCEPTS_ARTIFACT=PASS`
- `source_language=ro`
- `detected_domain=mathematics`
- `concept_count=0`
- `quality_status=LOW_QUALITY_BLOCKED`

This is the correct safety result.

Voila detected Romanian mathematics, but did not extract enough document-specific concepts from the real OCR text.

Therefore the document is not learned deeply enough yet.

## Real OCR candidate evidence

The real OCR text contains many candidate learning lines.

Candidate lines detected: 23.

Examples include:

- `Se numeşte segment orientat, o pereche ordonată de puncte din plan`
- `Se numeşte vector, mulţimea tuturor segmentelor orientate...`
- `Orice vector AB se caracterizează prin: modul, direcţie, sens`
- `Se numesc vectori egali...`
- `Doi vectori se numesc coliniari...`
- `Vectorii a şi b formează o bază`
- `se numesc coordonatele vectorului v`
- `se numesc versorii axelor de coordonate`
- `Baza (i,j) se numeşte bază ortonormată`
- `Produsul scalar a doi vectori nenuli`
- `Funcţii trigonometrice`

This proves the real OCR has usable learning material.

The current concept extractor is still too narrow for real OCR.

## Real course inventory

Observed active course files:

- `pages.json`: exists
- `course_outline.json`: exists
- `course_outline.md`: exists
- `course_outline.normalized.json`: exists
- `course.md`: exists
- `course.cleaned.md`: exists
- `course.cleaned.html`: exists
- `quiz.json`: exists but very small
- `flashcards.json`: exists but empty
- `glossary.json`: exists but empty

Missing pre-generation analysis files:

- `ocr_report.json`: missing
- `ocr_math_report.json`: missing
- `ocr_math_report.md`: missing

## Required future document learning pack contract

Future `document_learning_pack.json` must include at least:

1. Source metadata
   - source PDF path
   - page count
   - OCR text coverage
   - OCR quality signals

2. OCR Math analysis
   - formulas
   - symbols
   - mathematical expressions
   - suspect OCR Math lines
   - page references

3. Document concept extraction
   - document-specific concepts
   - definitions
   - notation
   - examples
   - theorem-like statements
   - page references
   - source evidence

4. Concept relations
   - prerequisite concepts
   - related concepts
   - examples attached to concepts
   - formulas attached to concepts

5. Teaching plan
   - proposed lesson sequence
   - objectives per lesson
   - glossary candidates
   - flashcard candidates
   - quiz candidates
   - weak/ambiguous areas that need review

6. Quality gate
   - `PASS`
   - `LOW_QUALITY_BLOCKED`
   - `OCR_MATH_MISSING_BLOCKED`
   - `TOO_FEW_CONCEPTS_BLOCKED`
   - `INSUFFICIENT_SOURCE_EVIDENCE_BLOCKED`

## Required future generate behavior

Before `/generate` creates or refreshes course outputs, Voila should eventually run:

1. OCR extraction
2. OCR report
3. OCR Math report
4. document concepts
5. document learning pack
6. quality gate

Only if the learning pack passes should Voila generate:

- course
- glossary
- flashcards
- quiz
- study/progress material

If the pack is weak, Voila must not silently generate a superficial course.

## Explicit blocker

For the real active Romanian math course:

`document_concepts.py` currently returns:

`LOW_QUALITY_BLOCKED`

because real OCR candidate definitions exist, but v0.7.61 extraction rules do not yet handle enough real OCR forms.

Known gaps include:

- legacy Romanian diacritics such as `ş` and `ţ`
- `Definiţie:` prefixes
- multiple definitions separated by semicolons
- `se numeşte` / `se numesc` variants
- theorem-like and notation-like statements
- formulas mixed into prose

## Policy

No `/generate` route change.
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

## Next recommended milestone

`v0.7.63-owner-local-document-concepts-real-ocr-coverage-improvement-no-generate-integration-no-build-no-zip-no-delivery`

Goal:

Improve `document_concepts.py` so it extracts real concepts from the active Romanian math OCR text, while still not integrating into `/generate`.
