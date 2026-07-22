# v0.8.59 UI polish/readability pass — no build/no ZIP/no share/no delivery

## Purpose

This milestone validates the learner-facing UI readability after the v0.8.50–v0.8.58 workflow chain.

It is an owner-local readability pass.

It does not implement new product behavior.

It does not change `services/api/web_app.py`.

## Pages checked

The pass checks:

- Course Tools
- Revizuire document
- Revizuire document draft form
- Study curat — previzualizare

## Readability expectations

The UI must expose a clear learner path:

1. Revizuire document
2. Text detectat
3. Corecturi sugerate
4. Formule și imagini
5. Explicație prietenoasă
6. Draft explicație
7. Study curat — previzualizare

The learner-facing UI should use friendly labels, not technical implementation labels.

The main surface should explain:

- what the learner can do next
- what is read-only
- what is local-only
- what does not yet create real Study cards
- how to return to Revizuire document

## Technical boundary

Technical details must stay in collapsed `Diagnostic tehnic`.

The main learner surface must not expose:

- raw JSON paths
- bbox
- crop_path
- visual_evidence_id
- source_evidence_id
- manual_study_item_id
- build flags
- package flags
- delivery flags
- internal route/debug markers as learner labels

## Read-only smoke rule

This pass does not submit forms.

It does not call POST endpoints.

It does not create a new explanation draft.

It does not write manual evidence.

It does not create Study cards.

It does not write Progress.

It does not mark answers.

It does not change default `/study`.

## Artifact boundary

The pass verifies that these artifacts do not change:

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

If this pass succeeds, the owner-local learner workflow is readable enough for a separate package rebuild preflight decision.

Package readiness remains blocked until a separate explicit owner-approved rebuild/share/delivery path.
