# v0.8.51 Course Tools link to Review Document shell — no build/no ZIP/no share/no delivery

## Purpose

This milestone makes the new learner-facing `Revizuire document` shell reachable from Course Tools.

It follows:

- v0.8.50 — Review Document shell read-only first slice

## Implemented change

Course Tools now includes a learner-facing entry point:

`Revizuire document`

The link points to:

`/review-document?pdf={pdf_name}`

## User-facing intent

The learner sees a clear next step:

- Revizuiește documentul
- Verifică textul, corecturile, formulele și imaginile
- Pregătește materialul pentru Study curat

This is the first visible bridge from the old technical Course Tools surface to the new guided learner workflow.

## Read-only boundary

This milestone only adds a link/card to an existing read-only shell.

It does not write data.

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

## Technical approach

The implementation is additive.

Existing Course Tools behavior remains intact.

The link is injected into the Course Tools HTML response only when a safe PDF name is available.

The Review Document shell route remains read-only.

## Diagnostic boundary

Technical diagnostic routes and existing owner/developer links remain available.

The new Course Tools entry uses learner-facing language and avoids technical metadata.

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

v0.8.52 — read-only Text detectat queue from existing OCR artifacts.
