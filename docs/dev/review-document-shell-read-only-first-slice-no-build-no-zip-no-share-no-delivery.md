# v0.8.50 Review Document shell read-only first slice — no build/no ZIP/no share/no delivery

## Purpose

This milestone implements the first learner-facing read-only slice of the new Voila workflow.

It adds the `Revizuire document` shell as an additive local route.

It follows:

- v0.8.43 — Student workflow UX reset charter
- v0.8.44 — Review Document shell design
- v0.8.45 — OCR + LanguageTool review queue design
- v0.8.46 — Formula/image/diagram/crop queue design
- v0.8.47 — Friendly explanation form design
- v0.8.48 — Clean Study mode design
- v0.8.49 — Learner workflow implementation preflight

## Route decision

Primary learner-facing route:

`/review-document?pdf={pdf_name}`

Read-only alias:

`/review-document/{course_id}`

The route is additive.

Existing OCR Review, Crop Editor, Manual Evidence, Course Tools, and Study routes remain intact.

## Implemented learner-facing shell

The shell shows:

- Revizuire document
- document name
- lesson language display: Română / English
- five learner-facing steps:
  1. Text detectat
  2. Corecturi sugerate
  3. Formule și imagini
  4. Noțiuni importante
  5. Gata pentru studiu
- guidance panel
- collapsed Diagnostic tehnic
- link back to Course Tools

## Read-only boundary

This milestone does not write data.

It does not run OCR.

It does not run LanguageTool.

It does not run Formula OCR.

It does not run crop extraction.

It does not create crop files.

It does not create visual evidence.

It does not create manual evidence.

It does not create Study cards.

It does not change Study behavior.

It does not write Progress.

It does not mark answers.

## User-facing language

The shell uses learner-first Romanian labels by default.

The page includes a language display for:

- Română
- English

No mixed RO/EN learner flow is implemented here.

This slice only displays the language model.

## Diagnostic boundary

Technical details appear only in collapsed `Diagnostic tehnic`.

The main learner surface avoids:

- metadata
- bbox
- source_evidence_id
- manual_study_item_id
- visual_evidence_id
- JSON artifact names
- dry-run
- package policy markers
- build flags
- delivery flags

## Policy

No build.

No ZIP.

No package rebuild.

No OneDrive copy.

No share.

No delivery.

No distribution.

No public release.

## Recommended next

v0.8.51 — Course Tools link to learner shell.
