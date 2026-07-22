# v0.8.56 Safe local save for explanation drafts — no build/no ZIP/no share/no delivery

## Purpose

This milestone introduces the first controlled local write in the learner-facing `Revizuire document` workflow.

## Allowed write target

The only allowed write target is:

`data/output/<course_id>/explanation_drafts.preview.json`

This is local-only draft data.

It is not manual evidence.

It is not Study data.

It is not Progress data.

It is not package data.

## Form fields

- Titlu scurt
- Ce este asta?
- Text / zonă verificată
- Explicație pe înțeles
- De ce este important?
- Sursa: pagina X
- Limba lecției
- Gata pentru studiu

## Boundaries

This milestone may add one POST endpoint for local draft save only.

It does not run OCR.

It does not run LanguageTool.

It does not run Formula OCR.

It does not run crop extraction.

It does not create crop files.

It does not write visual evidence.

It does not write manual evidence.

It does not create Study cards.

It does not write Progress.

It does not mark answers.

It does not rewrite OCR text.

## Policy

No build.

No ZIP.

No package rebuild.

No OneDrive copy.

No share.

No delivery.

No distribution.

No public release.
