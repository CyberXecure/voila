# v0.8.55 Friendly explanation form read-only static draft shell — no build/no ZIP/no share/no delivery

## Purpose

This milestone adds the learner-facing `Explicație prietenoasă` shell inside `Revizuire document`.

It follows:

- v0.8.50 — Review Document shell read-only first slice
- v0.8.51 — Course Tools link to Review Document shell
- v0.8.52 — Text detectat read-only queue from existing OCR artifacts
- v0.8.53 — Corecturi sugerate read-only queue from existing LanguageTool artifacts
- v0.8.54 — Formule și imagini read-only queue from existing visual/crop artifacts

## Implemented change

The `Revizuire document` page now includes a learner-facing static section:

`Explicație prietenoasă`

This is a visual/static draft shell only.

It shows the fields that will later be used to prepare verified learning material.

## Static fields shown

The learner sees the future explanation structure:

- Titlu scurt
- Ce este asta?
- Text / zonă verificată
- Explicație pe înțeles
- De ce este important?
- Sursa: pagina X
- Limba lecției
- Gata pentru studiu

## Read-only rule

This milestone does not save anything.

It does not add a form submit.

It does not add a POST endpoint.

It does not create explanation drafts.

It does not write manual evidence.

It does not create Study cards.

It only shows the shape of the future explanation workflow.

## Learner-facing intent

The learner understands that before Study curat, every useful notion should become:

- clear
- verified
- explained simply
- attached to a source page
- in one selected language

## Diagnostic boundary

Technical details are allowed only in collapsed `Diagnostic tehnic`.

The main learner surface must not expose:

- metadata
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

v0.8.56 — safe local save for explanation drafts, only after separate explicit approval.
