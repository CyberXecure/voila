# v0.8.58 Learner workflow UI smoke from Review Document to Clean Study — no build/no ZIP/no share/no delivery

## Purpose

This milestone validates the learner-facing workflow after the v0.8.50–v0.8.57 implementation chain.

It does not add product functionality.

It does not change `services/api/web_app.py`.

## Smoke path

The owner-local UI smoke validates:

1. Course Tools opens.
2. Course Tools exposes `Revizuire document`.
3. `Revizuire document` opens.
4. `Text detectat` is visible.
5. `Corecturi sugerate` is visible.
6. `Formule și imagini` is visible.
7. `Explicație prietenoasă` is visible.
8. `Draft explicație` entry is visible.
9. Draft form shell opens by GET only.
10. `Study curat — previzualizare` link is visible.
11. Clean Study preview opens.
12. Clean Study preview is read-only.
13. Clean Study preview shows cards or a friendly empty state.

## Read-only smoke rule

This smoke does not submit the draft form.

It does not call POST endpoints.

It does not create a new explanation draft.

It does not write manual evidence.

It does not create Study cards.

It does not write Progress.

It does not mark answers.

It does not change default `/study`.

## Artifact boundary

The smoke verifies that these artifacts do not change:

- `explanation_drafts.preview.json`
- `manual_learning_evidence.json`
- `manual_study_items.preview.json`
- `study_items.preview.json`

## Engine boundary

It does not run OCR.

It does not run LanguageTool correction.

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

## Result expectation

If this smoke passes, the owner-local UI flow is ready for a separate next decision milestone.

Package readiness remains blocked until explicit owner approval for any rebuild/share/delivery path.
