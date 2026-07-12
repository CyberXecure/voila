# v0.7.63 Owner-local document concepts real OCR coverage improvement

Status: PASS_REAL_OCR_COVERAGE_IMPROVED

Marker:
VOILA_V0_7_63_DOCUMENT_CONCEPTS_REAL_OCR_COVERAGE_IMPROVEMENT_CHECK=PASS

Baseline:
v0.7.62 completed and merged to protected main at `761d8ae`.

## Purpose

Voila must learn the recognized PDF before it teaches it.

This milestone improves the owner-local `document_concepts.py` extractor so it can extract real concepts from Romanian OCR text in the active vector/trigonometry PDF.

This is still a pre-generation artifact step.

## Scope

Changed:

- `services/api/document_concepts.py`

Added validation/doc:

- this document
- v0.7.63 check script

Not changed:

- `/generate`
- web routes
- active course outputs
- lesson generation
- quiz generation
- flashcards generation
- glossary generation
- OCR extraction
- OCR Math extraction
- build/package/delivery flow

## Real-course baseline before patch

Real active course:

`data\output\03-pag-30-34-vectori-trigonometrie`

Baseline before this patch:

- `source_language=ro`
- `detected_domain=mathematics`
- `concept_count=0`
- `quality_status=LOW_QUALITY_BLOCKED`

This baseline proved that the real OCR text had mathematical content, but the concept extractor was too narrow.

## Improvement

The extractor now handles more real Romanian OCR forms:

- legacy Romanian diacritics: `ş`, `ţ`
- `Definiţie:` prefixes
- `se numeşte`
- `se numesc`
- multiple definitions separated by semicolons
- vector relation definitions using `dacă`
- vector characteristics such as modul, direcţie, sens
- notation-like statements
- named structures such as bază, coordonate, versori
- formula/topic sections such as produs scalar and funcţii trigonometrice

## Small fixture validation

Controlled small fixture after patch:

- `concept_count=3`
- `quality_status=PASS`

Extracted concepts:

- `vector`
- `segment orientat`
- `modul`

This preserves the v0.7.61 small fixture behavior.

## Real active course validation after patch

Real course after patch:

- `source_language=ro`
- `detected_domain=mathematics`
- `concept_count=14`
- `quality_status=PASS`

Extracted real concepts include:

- `segment orientat`
- `vector`
- `modul`
- `direcție`
- `vectori egali`
- `vectori opuși`
- `vectori coliniari`
- `vectori necoliniari`
- `bază`
- `coordonatele vectorului`
- `versorii axelor de coordonate`
- `bază ortonormată`
- `produsul scalar`
- `funcții trigonometrice`

## Important limitation

This milestone does not mean the course generator is fixed yet.

It only proves that the owner-local document concept artifact can now extract useful real concepts from the active OCR text.

The next steps still need OCR report, OCR Math report, document learning pack, and quality gate before generation.

## User-friendly OCR Review requirement

If the document learning quality gate is blocked in the future, Voila must not expose raw technical files or fail silently.

It must route the user to a guided OCR Review flow.

That review must be as easy as possible:

- show only suspect lines/formulas
- highlight the exact text or symbol issue
- show page context
- allow simple actions: accept, edit, ignore
- allow marking a line as definition, formula, notation, theorem, or example
- rebuild the document learning pack after review
- continue course generation only after the quality gate passes

The user should not need technical knowledge to correct OCR issues.

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

`v0.7.64-owner-local-ocr-review-contract-for-document-learning-gate-no-generate-integration-no-build-no-zip-no-delivery`

Goal:

Define the guided OCR Review UX and artifact contract used when document learning is blocked before course generation.
