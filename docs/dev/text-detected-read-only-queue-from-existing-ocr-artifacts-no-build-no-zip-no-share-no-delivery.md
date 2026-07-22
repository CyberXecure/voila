# v0.8.52 Text detectat read-only queue from existing OCR artifacts — no build/no ZIP/no share/no delivery

## Purpose

This milestone adds the first real content section inside the learner-facing `Revizuire document` shell.

It implements a read-only `Text detectat` queue using existing OCR artifacts only.

It follows:

- v0.8.50 — Review Document shell read-only first slice
- v0.8.51 — Course Tools link to Review Document shell

## Implemented change

The `Revizuire document` page now includes a learner-facing section:

`Text detectat`

The section displays existing detected text as page/block cards.

The learner sees:

- page number
- short text fragment
- friendly explanation that this is a verification step
- read-only status

## Source rule

The section reads only existing local artifacts.

Preferred source:

- existing page text artifacts already generated for the course

This milestone does not create new OCR output.

This milestone does not rerun OCR.

This milestone does not rewrite OCR text.

## Learner-facing language

The main surface uses friendly labels:

- Text detectat
- Fragmente detectate
- Pagina
- Doar citire
- Verifică dacă textul arată corect înainte de următorul pas

The main learner surface avoids technical identifiers.

## Diagnostic boundary

Technical artifact details are allowed only in collapsed `Diagnostic tehnic`.

The main learner surface must not expose:

- bbox
- source_evidence_id
- manual_study_item_id
- visual_evidence_id
- JSON artifact paths
- crop paths
- build flags
- delivery flags

## Read-only boundary

This milestone does not write data.

It does not add a POST endpoint.

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

## Safety

The route only accepts safe local PDF/course identifiers.

The implementation must not build file paths directly from unsafe user input.

The course output folder lookup remains constrained to the fixed local output root.

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

v0.8.53 — read-only Corecturi sugerate queue from existing LanguageTool artifacts.
