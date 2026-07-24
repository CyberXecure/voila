# v0.8.73 Review Document visual validation UI plan — no share/no delivery

## Purpose

This milestone defines the user-facing UI plan for connecting the validated bbox/crop/OCR Math pipeline into `Revizuire document`.

This is a planning-only milestone.

It does not implement the UI.

It does not modify `services/api/web_app.py`.

It does not add a POST endpoint.

It does not change `/study`.

## Current validated backend chain

The user-facing visual validation UI must be built on the existing controlled local chain:

1. `v0.8.67` defines the bbox visual item contract.
2. `v0.8.68` validates bbox visual items.
3. `v0.8.69` creates real crop PNG artifacts from bbox coordinates.
4. `v0.8.70` runs OCR Math candidate extraction on crop PNG artifacts.
5. `v0.8.71` applies explicit manual validation decisions.
6. `v0.8.72` ingests only validated `accept/edit` items into Clean Study preview.

## Canonical user flow

The canonical user flow in `Revizuire document` should become:

1. The user uploads a PDF.
2. Voila prepares OCR text, LanguageTool suggestions, page images, bbox visual candidates, crops, and OCR Math candidates.
3. The user opens `Revizuire document`.
4. The user reviews text corrections.
5. The user reviews visual candidates.
6. For each visual candidate, the user sees the crop image and OCR Math candidate text.
7. The user chooses `Acceptă`, `Editează`, or `Ignoră`.
8. The user may add a learner-friendly explanation.
9. Only `Acceptă` and `Editează` items marked ready for study can enter Clean Study.
10. `Ignoră` and undecided/pending items must not enter Clean Study.

## Visual validation card

Each visual validation card should show learner-friendly information first:

- crop image preview;
- source page;
- visual type label: formula, figură, diagramă, tabel, simbol, mixt, necunoscut;
- OCR Math candidate text;
- editable corrected text field;
- learner-friendly explanation field;
- decision controls: `Acceptă`, `Editează`, `Ignoră`;
- status label: `În așteptare`, `Acceptat`, `Corectat`, `Ignorat`;
- Clean Study eligibility indicator.

## Friendly Romanian labels

Preferred labels:

- section title: `Formule și imagini de verificat`;
- crop preview: `Imagine extrasă din document`;
- candidate text: `Text detectat`;
- corrected text: `Corectare`;
- explanation: `Explicație pe înțeles`;
- accept action: `Acceptă`;
- edit action: `Salvează corectarea`;
- ignore action: `Ignoră`;
- ready indicator: `Gata pentru lecție`;
- not ready indicator: `Nu intră încă în lecție`;
- collapsed technical details: `Diagnostic tehnic`.

## Hidden technical details

The default user-facing UI should not expose:

- bbox coordinates;
- raw artifact file names;
- absolute local paths;
- Python script names;
- JSON schema internals;
- policy flags;
- package/release terminology.

These may appear only inside a collapsed `Diagnostic tehnic` section for owner-local troubleshooting.

## Data mapping plan

The future UI implementation should read:

- `formula_visual_evidence/visual_items.bbox.with-ocrmath-candidates.json` for pending visual candidates;
- `formula_visual_evidence/visual_items.bbox.validated.json` after manual decisions;
- `formula_visual_evidence/visual_items.clean-study.preview.json` after Clean Study visual ingestion.

The future UI implementation should write decisions only through a controlled local action equivalent to:

- `scripts/dev/apply-bbox-visual-validation-decisions.py`.

The future UI implementation should not allow implicit approval.

## Decision rules

`Acceptă` should require:

- crop exists;
- OCR Math candidate text is non-empty;
- explicit user action.

`Editează` should require:

- crop exists;
- corrected text is non-empty;
- explicit user action.

`Ignoră` should require:

- explicit user action;
- item remains excluded from Clean Study.

Undecided items remain pending.

## Clean Study rule

Clean Study may include only:

- `ready_for_study=true`;
- `user_decision=accept` or `user_decision=edit`.

Clean Study must exclude:

- `user_decision=ignore`;
- `user_decision=pending`;
- any item without a crop;
- any accepted item without OCR Math candidate text;
- any edited item without corrected text.

## UX boundary

The visual validation UI should feel like document review, not developer tooling.

The user should understand:

- what was extracted;
- where it came from;
- what Voila thinks it says;
- what needs correction;
- what will enter the lesson.

## Future implementation sequence

Recommended implementation after this plan:

1. Add read-only visual validation UI section in `Revizuire document`.
2. Show crop image and candidate text from existing artifacts.
3. Add owner-local save action for Accept/Edit/Ignore decisions.
4. Add read-only Clean Study preview link/status for validated visual items.
5. Only after local browser PASS, consider integrating with the broader upload/generate pipeline.

## Explicit non-goals for v0.8.73

This milestone does not implement visual validation UI.

It does not modify `services/api/web_app.py`.

It does not start the server.

It does not call any route.

It does not add a POST endpoint.

It does not upload a PDF.

It does not run `/generate`.

It does not run OCR.

It does not run LanguageTool.

It does not run OCR Math.

It does not generate crops.

It does not write manual decisions.

It does not write Clean Study.

It does not write Progress.

It does not build.

It does not create a ZIP.

It does not create OneDrive staging.

It does not create a share link.

It does not deliver to testers.

It does not distribute anything.

It does not create a public release.
