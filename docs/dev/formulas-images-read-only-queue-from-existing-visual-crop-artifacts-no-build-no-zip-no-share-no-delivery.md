# v0.8.54 Formule și imagini read-only queue from existing visual/crop artifacts — no build/no ZIP/no share/no delivery

## Purpose

This milestone adds the third real content section inside the learner-facing `Revizuire document` shell.

It implements a read-only `Formule și imagini` queue using existing visual/crop artifacts only.

It follows:

- v0.8.50 — Review Document shell read-only first slice
- v0.8.51 — Course Tools link to Review Document shell
- v0.8.52 — Text detectat read-only queue from existing OCR artifacts
- v0.8.53 — Corecturi sugerate read-only queue from existing LanguageTool artifacts

## Implemented change

The `Revizuire document` page now includes a learner-facing section:

`Formule și imagini`

The section displays existing visual items as friendly read-only cards.

The learner sees:

- page number when available
- friendly item type
- short title or label when available
- friendly description when available
- read-only status

## Friendly item types

The learner-facing item types are:

- Formulă
- Imagine
- Diagramă
- Tabel
- Grafic
- Desen
- Observație importantă

## Source rule

The section reads only existing local visual/crop artifacts.

Preferred sources include existing local visual sidecars and reports when present.

This milestone does not create new visual output.

This milestone does not run Formula OCR.

This milestone does not run crop extraction.

This milestone does not write crop files.

This milestone does not write visual evidence.

## Learner-facing language

The main surface uses friendly labels:

- Formule și imagini
- Elemente vizuale găsite
- Pagina
- Tip
- Descriere
- Doar citire

The main learner surface avoids technical identifiers.

## Diagnostic boundary

Technical artifact details are allowed only in collapsed `Diagnostic tehnic`.

The main learner surface must not expose:

- bbox
- crop_path
- visual_evidence_id
- source_evidence_id
- manual_study_item_id
- JSON artifact paths
- route names
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

v0.8.55 — friendly explanation form read-only/static draft shell.
