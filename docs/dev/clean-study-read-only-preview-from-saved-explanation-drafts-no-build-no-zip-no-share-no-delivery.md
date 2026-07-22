# v0.8.57 Clean Study read-only preview from saved explanation drafts - no build/no ZIP/no share/no delivery

## Purpose

This milestone adds a learner-facing Clean Study preview from saved local explanation drafts.

It follows v0.8.56, where local explanation drafts can be saved to:

`data/output/<course_id>/explanation_drafts.preview.json`

## Implemented change

The app adds a separate read-only preview surface:

`/study-clean-preview?pdf=<pdf_name>`

and:

`/study-clean-preview/<course_id>`

The `Revizuire document` page receives a friendly link to open the Clean Study preview.

## Data source

The preview reads only:

`data/output/<course_id>/explanation_drafts.preview.json`

It does not write to this file.

It does not create manual evidence.

It does not create real Study cards.

It does not write Progress.

## Learner-facing card shape

Each preview card shows:

- Card X din Y
- Tip
- Titlu scurt
- Întrebare
- Răspuns
- Explicație pe înțeles
- De ce este important?
- Sursa: pagina X
- Limba lecției

## Clean Study boundary

The preview is read-only.

It is not the default `/study` route.

It does not change legacy Study fallback.

It does not mark answers.

It does not create attempts.

It does not persist progress.

## Diagnostic boundary

Technical details are allowed only in collapsed `Diagnostic tehnic`.

The main learner surface must not expose raw JSON paths, metadata IDs, bbox, crop paths, package flags, delivery flags, or internal evidence IDs.

## Engine boundary

This milestone does not run OCR.

It does not run LanguageTool.

It does not run Formula OCR.

It does not run crop extraction.

## Policy

No build.

No ZIP.

No package rebuild.

No OneDrive copy.

No share.

No delivery.

No distribution.

No public release.

## Explicit engine boundary markers for validation

It does not run OCR.

It does not run LanguageTool.

It does not run Formula OCR.

It does not run crop extraction.
