# v0.7.94 Voila Direction Charter and Guard — no build/no ZIP/no delivery

## Product direction

Voila is a human-in-the-loop verified learning tool.

Voila is not positioned as a fully automatic AI course generator.

The owner opens a real document, inspects the source material, verifies text, formulas, drawings, diagrams, examples, and possible source mistakes, then builds a trusted learning course from verified evidence.

AI assists. The owner validates.

## Core principle

Evidence-first, owner-verified learning.

Learning content must be traceable to real source evidence:

- source document
- source page
- crop or visual evidence
- owner-verified text
- owner explanation
- source status

## Required manual learning evidence fields

Future manual learning evidence artifacts must support at least:

- title
- kind
- verified_text
- explanation_ro
- source_status
- source_note
- page
- crop_path
- status

Accepted `kind` values should include:

- formula
- definition
- example
- theorem
- diagram
- drawing
- note

Accepted `source_status` values should include:

- verified
- uncertain
- possible_source_error

Accepted review statuses should include:

- pending_owner_review
- accepted_owner_verified
- rejected_noise

## Canonical artifact

The future canonical owner-verified evidence artifact is:

`manual_learning_evidence.json`

This artifact should be the bridge from source material to Learning Pack.

## Learning Pack rule

Learning Pack must consume accepted owner-verified evidence, not raw OCR alone.

Learning Pack may use OCR text, automatic candidate detection, formula visual evidence, diagrams, and crops as inputs, but trusted learning blocks must come from owner-verified evidence.

## AI rule

AI may assist with:

- suggesting titles
- suggesting kind
- suggesting explanations
- formatting verified text
- detecting possible inconsistencies
- proposing questions

AI must not silently invent learning content without traceable evidence.

AI output must remain reviewable and correctable by the owner.

## Source mistakes

Voila must allow the owner to mark possible mistakes in the source document.

A diagram, formula, or definition can be marked as:

`possible_source_error`

The course should preserve that note instead of pretending the source is always correct.

## Sharing rule

A course is shareable only after evidence is reviewed and accepted by the owner.

Sharing, packaging, ZIP creation, or tester delivery requires a separate explicit milestone.

## Non-goals for this milestone

- No UI implementation.
- No Crop Editor integration.
- No manual crop implementation.
- No Learning Pack rewrite.
- No OCR rewrite.
- No Formula OCR.
- No course generation change.
- No Study change.
- No Progress change.
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.

## Required direction check for future PRs

Every future milestone that affects learning content should state:

- evidence-first: PASS
- owner verified: PASS
- AI autonomy limited: PASS
- Learning Pack source traceability: PASS
- source mistakes supported or not applicable: PASS
- no build/no ZIP/no delivery unless explicitly approved: PASS
