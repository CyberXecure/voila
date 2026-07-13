# v0.7.67 Owner-local document learning pack builder from concepts and review artifacts

Status: PASS_DOCUMENT_LEARNING_PACK_BUILDER_BLOCKED_BY_PENDING_REVIEW

Marker:
VOILA_V0_7_67_DOCUMENT_LEARNING_PACK_BUILDER_CHECK=PASS_BLOCKED_BY_PENDING_REVIEW

Baseline:
v0.7.66 completed and merged to protected main at `6857553`.

## Purpose

Voila must learn the document before it teaches it.

This milestone adds the first owner-local `document_learning_pack` artifact builder.

The pack combines:

- document concepts
- OCR Review queue
- OCR Review decisions

If OCR Review decisions are still pending, the learning pack is created but generation remains blocked.

## Scope

This milestone adds:

`services/api/document_learning_pack.py`

It creates:

- `document_learning_pack.json`
- `document_learning_pack.md`

It reads:

- `document_concepts.json`
- `ocr_review_queue.json`
- `ocr_review_decisions.json`

It does not implement UI.

It does not integrate with `/generate`.

It does not regenerate the active course.

## Real active course smoke

Real active course source:

`D:\dev\projects\voila\data\input\03-pag-30-34-vectori-trigonometrie.pdf`

Inputs:

- v0.7.63 real-course `document_concepts.json`
- v0.7.65 real-course `ocr_review_queue.json`
- v0.7.66 real-course `ocr_review_decisions.json`

Observed output:

- `DOCUMENT_LEARNING_PACK_ARTIFACT=PASS`
- `concept_count=14`
- `review_item_count=20`
- `pending_decision_count=20`
- `document_learning_status=OCR_REVIEW_PENDING_BLOCKED`
- `generation_allowed=False`

## Concept coverage

The pack contains 14 extracted concepts:

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

## Review-linked concepts

The pack links pending OCR Review items back to affected concepts.

Review-linked concept terms include:

- `vector`
- `modul`
- `vectori necoliniari`
- `coordonatele vectorului`
- `versorii axelor de coordonate`
- `produsul scalar`
- `funcții trigonometrice`

Those concepts are marked with:

`needs_review_before_generation=True`

## Quality gate

Because 20 OCR Review decisions are pending, the quality gate reports:

`OCR_REVIEW_PENDING_BLOCKED`

and:

`generation_allowed=False`

This is intentional.

Pending OCR Review decisions are not verified evidence.

The course generator must not use unresolved blocked review items as reliable learning material.

## Teaching plan candidates

The pack produces candidate-only learning material:

- lesson sequence candidates
- glossary candidates
- flashcard candidates
- quiz candidates

These candidates are not generator-ready while OCR Review is pending.

They are blocked until review decisions are resolved.

## Learning policy

The pack records that:

- Voila must learn the document before teaching it
- OCR Review is user-assisted document learning
- user corrections become verified evidence
- pending decisions are not verified evidence
- unresolved blocked review items must not feed course generation

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
