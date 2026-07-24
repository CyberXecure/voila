# v0.8.80 Review Document visual validation Clean Study refresh plan — no share/no delivery

## Purpose

This milestone defines the owner-local plan for refreshing Clean Study preview after visual validation decisions in `Revizuire document`.

This is a planning-only milestone.

It does not implement a refresh route.

It does not modify `services/api/web_app.py`.

It does not write Clean Study.

It does not change `/study`.

## Current validated chain

The refresh plan builds on the completed chain:

1. `v0.8.67` defines the bbox visual item contract.
2. `v0.8.68` validates bbox visual item artifacts.
3. `v0.8.69` creates real crop artifacts from bbox coordinates.
4. `v0.8.70` creates OCR Math candidates from real crop PNG artifacts.
5. `v0.8.71` validates explicit manual decisions.
6. `v0.8.72` builds Clean Study visual preview items from validated visual items.
7. `v0.8.73` defines the Review Document visual validation UI plan.
8. `v0.8.74` adds the Review Document visual validation UI section.
9. `v0.8.75` smoke-tests the read-only UI.
10. `v0.8.76` defines the save-action plan.
11. `v0.8.77` implements the save action.
12. `v0.8.78` adds form controls.
13. `v0.8.79` smoke-tests rendered form POST flow and fixes post-save readback priority.

## Separation rule

The save action must remain separate from Clean Study refresh.

`POST /review-document/visual-validation/save` should save only visual validation decisions.

It should not directly write Clean Study.

Clean Study preview should be refreshed by a separate explicit owner-local action.

## Future refresh action

Recommended future route:

`POST /review-document/visual-validation/refresh-clean-study-preview`

The route should be owner-local only.

The route should rebuild Clean Study visual preview from the validated artifact.

The route should be explicit.

A GET request must not refresh Clean Study.

A page refresh must not refresh Clean Study.

Saving one decision must not automatically rebuild Clean Study unless a future milestone explicitly chooses that policy.

## Input artifact

The future refresh action should read only:

`formula_visual_evidence/visual_items.bbox.validated.json`

It should not read the older candidate artifact when rebuilding Clean Study.

It should not trust client-submitted item data.

It should not trust client-submitted crop paths.

It should not trust client-submitted ready flags.

## Existing implementation to reuse

The future refresh action should reuse the controlled ingestion behavior from:

`scripts/dev/build-clean-study-visual-items-from-bbox.py`

The same inclusion rules should apply.

## Inclusion rule

Clean Study preview may include only visual items where:

- `ready_for_study=true`;
- `user_decision=accept` or `user_decision=edit`;
- `crop_exists=true`;
- `crop_path` exists in the server-side artifact;
- accepted items have non-empty `ocr_math_candidate_text`;
- edited items have non-empty `user_corrected_text`.

## Exclusion rule

Clean Study preview must exclude:

- `user_decision=ignore`;
- `user_decision=pending`;
- any item without crop;
- any accepted item without OCR Math candidate text;
- any edited item without corrected text;
- any malformed item.

## Output artifact

The future refresh action should write only:

`formula_visual_evidence/visual_items.clean-study.preview.json`

It may also write:

`formula_visual_evidence/visual_items.clean-study.preview-summary.json`

The write should be local only.

The write should be atomic or replace-safe.

The write should not modify the validated visual decisions artifact.

The write should not modify Progress.

The write should not modify the default `/study` route.

## UI plan

After visual decisions are saved, `Revizuire document` should show a clear refresh action:

`Actualizează lecția curată`

The UI should explain:

- accepted and corrected items can enter the lesson;
- ignored and pending items do not enter the lesson;
- refreshing Clean Study does not change the original document;
- refreshing Clean Study does not publish or share anything.

After refresh, the UI should show:

- number of visual items included;
- number of visual items excluded;
- link to Clean Study preview;
- friendly warning if no validated items are ready.

## Suggested future user-facing labels

Preferred Romanian labels:

- action: `Actualizează lecția curată`;
- status before refresh: `Lecția curată nu este actualizată încă`;
- status after refresh: `Lecția curată a fost actualizată`;
- included count: `Elemente adăugate în lecție`;
- excluded count: `Elemente rămase în afara lecției`;
- empty state: `Nu există încă elemente vizuale validate pentru lecție`;
- link: `Deschide lecția curată`;
- diagnostic section: `Diagnostic tehnic`.

## Security and safety plan

The future refresh route must use safe course ID validation.

The route must resolve the course output directory through the existing safe local lookup pattern.

The route must not join client-controlled paths.

The route must not expose stack traces.

The route must return friendly HTML responses.

The route must escape reflected values.

The route must not redirect to user-controlled URLs.

The route must not accept client-submitted item payloads.

## Validation plan for future implementation

A future implementation check should use FastAPI TestClient.

It should create a temporary fixture under `data/output`.

It should submit visual decisions through the existing save action or create a validated fixture directly.

It should call the future refresh action explicitly.

It should verify:

- Clean Study preview artifact exists;
- Clean Study preview summary exists;
- accepted item is included;
- edited item is included with corrected text;
- ignored item is excluded;
- pending item is excluded;
- malformed item is excluded or rejected;
- validated visual decisions artifact remains preserved;
- `/study` is unchanged;
- Progress is unchanged;
- no build, ZIP, share, delivery, or public release occurs.

## Explicit non-goals for v0.8.80

This milestone does not implement the refresh action.

It does not modify `services/api/web_app.py`.

It does not add a route.

It does not add a POST endpoint.

It does not add a button.

It does not submit a form.

It does not call any route.

It does not start the server.

It does not use TestClient.

It does not upload a PDF.

It does not run `/generate`.

It does not run OCR.

It does not run LanguageTool.

It does not run OCR Math.

It does not generate crops.

It does not write manual decisions.

It does not write Clean Study.

It does not write Progress.

It does not change `/study`.

It does not build.

It does not create a ZIP.

It does not create OneDrive staging.

It does not create a share link.

It does not deliver to testers.

It does not distribute anything.

It does not create a public release.

## Recommended next slice

The next milestone should be:

`v0.8.81-owner-local-review-document-visual-validation-clean-study-refresh-implementation-no-share-no-delivery`

That milestone may implement the explicit owner-local refresh action and a TestClient POST check.
