# v0.8.42 Exam document workflow UX polish — no share/no delivery

## Purpose

This milestone adds a student-facing workflow card to Course Tools.

It follows v0.8.41, where the owner personal smoke test recorded:

`owner_personal_workflow_result=NEEDS_UX_POLISH`

The technical Study flow worked, but the workflow was not clear enough for a tester without extra explanation.

## UX direction

Use general, friendly, professional language:

`Învață pentru examen din acest document`

Do not hardcode BAC as the main label.

The product should remain usable for BAC, Evaluare Națională, admitere, facultate, training, and other exam contexts.

## Student-facing workflow

Course Tools should show a clear workflow:

1. Revizuiește documentul
2. Alege noțiuni importante
3. Creează material de învățare
4. Învață acum
5. Exersează pentru examen

## Unified concept

OCR Review, Crop Editor, and Manual Learning Evidence should be presented as one learner-facing idea:

`Revizuire document`

Technical concepts can remain available in diagnostic/advanced areas, but the main workflow should avoid terms like:

- metadata
- bbox
- accepted_owner_verified
- dry-run
- manual_study_items.preview.json
- Learning Pack artifact

## Boundary

This milestone is owner-local UX polish only.

It does not rebuild the package.

It does not create a new ZIP.

It does not copy to OneDrive.

It does not create a share.

It does not deliver anything.

It does not distribute anything.

It does not create a public release.

It does not add a route.

It does not add a POST endpoint.

It does not change Study behavior.

It does not write Progress.

It does not mark answers.

It does not perform OCR rewrite.

It does not perform Formula OCR.

It does not write crop files.

## Required next step

After this polish, the owner should run another personal workflow smoke test before any package rebuild or tester delivery.

## Policy

No OneDrive copy.

No share.

No delivery.

No distribution.

No public release.
