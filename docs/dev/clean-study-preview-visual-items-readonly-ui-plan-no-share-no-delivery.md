# v0.8.84 Clean Study preview visual items read-only UI plan — no share/no delivery

## Purpose

This milestone defines the owner-local plan for displaying validated visual study items inside Clean Study preview.

This is a planning-only milestone.

It does not implement the UI.

It does not modify `services/api/web_app.py`.

It does not change `/study`.

It does not write Clean Study.

It does not write Progress.

## Current chain

The plan builds on the completed chain:

1. `v0.8.67` defines bbox visual item artifacts.
2. `v0.8.68` validates bbox visual item artifacts.
3. `v0.8.69` creates real crop PNG artifacts.
4. `v0.8.70` creates OCR Math candidates from crop PNG artifacts.
5. `v0.8.71` applies manual accept/edit/ignore decisions.
6. `v0.8.72` builds Clean Study visual preview items.
7. `v0.8.81` implements explicit Clean Study preview refresh.
8. `v0.8.82` adds the `Actualizează lecția curată` UI control.
9. `v0.8.83` smoke-tests the rendered refresh form POST flow.

## Input artifact for future UI

The future read-only UI should read only:

`formula_visual_evidence/visual_items.clean-study.preview.json`

It should not read:

`formula_visual_evidence/visual_items.bbox.validated.json`

It should not read:

`formula_visual_evidence/visual_items.bbox.with-ocrmath-candidates.json`

Clean Study preview should consume the already refreshed learner-facing artifact, not raw validation artifacts.

## Learner-facing display goal

The future Clean Study preview UI should show validated visual items as learning material.

It should be friendly for a student or adult learner.

It should not look like a technical diagnostic report.

The UI should explain the item in plain language.

The UI should make clear that the item came from the uploaded document.

## Suggested section label

Preferred Romanian section title:

`Elemente vizuale validate`

Alternative shorter label:

`Formule și imagini validate`

## Suggested card fields

Each visual study item card may show:

- title;
- page source;
- validated visual crop image when available;
- question or prompt;
- validated answer;
- explanation;
- learner note that the item was accepted or corrected during review.

Preferred Romanian labels:

- `Sursa: pagina`;
- `Întrebare`;
- `Răspuns validat`;
- `Explicație`;
- `Verificat în Revizuire document`.

## Image display plan

If `image.crop_path` exists in the Clean Study preview artifact, the future UI may render the image.

The UI may use the crop path internally as an image source.

The UI must not display the raw crop path as text.

The UI must not display absolute paths.

The UI must not expose local filesystem roots.

The UI should include safe alt text.

The UI should degrade gracefully if the crop file is missing.

## Hidden technical metadata

The future learner-facing UI must not display:

- `bbox`;
- `bbox_units`;
- `crop_path`;
- `page_image_path`;
- `source_visual_item_id`;
- `study_item_id`;
- `schema_version`;
- `source_visual_items_path`;
- artifact names;
- absolute paths;
- local filesystem paths;
- `ready_for_study`;
- `ready_for_clean_study`;
- `user_decision`;
- `ocr_math_status`;
- `learning_source`;
- raw JSON.

## Empty state

If no Clean Study visual preview artifact exists, the UI should show a friendly message:

`Lecția curată nu a fost actualizată încă.`

It may also show a link back to `Revizuire document`.

If the artifact exists but contains no items, the UI should show:

`Nu există încă elemente vizuale validate pentru lecție.`

## Relationship with `/study`

This plan does not change `/study`.

Clean Study preview remains a separate preview surface.

A later milestone may decide whether and how validated visual items become part of the main study experience.

That decision should remain explicit and separate.

## Relationship with refresh action

The future UI should not rebuild Clean Study automatically.

The refresh already happens through the explicit v0.8.81 route.

The future UI should only read the already-built Clean Study preview artifact.

A GET request to Clean Study preview must not write files.

A page refresh must not write files.

## Safety and escaping

The future UI must escape learner-facing text.

The future UI must not expose stack traces.

The future UI must not trust client-submitted paths.

The future UI should resolve image paths only under the course output directory.

The future UI should reject or hide unsafe image paths.

The future UI should not redirect to user-controlled URLs.

## Validation plan for future implementation

A future implementation check should use FastAPI TestClient.

It should create a temporary fixture under `data/output`.

It should write a Clean Study visual preview artifact directly.

It should render Clean Study preview.

It should verify:

- visual items section is visible;
- accepted item is visible;
- edited item is visible with corrected text;
- explanation is visible;
- page source is visible;
- crop image reference is rendered safely when available;
- missing crop image degrades gracefully;
- empty state is friendly;
- technical metadata is hidden;
- raw JSON is hidden;
- absolute paths are hidden;
- GET does not write Clean Study;
- GET does not write Progress;
- `/study` remains unchanged;
- no build, ZIP, share, delivery, or public release occurs.

## Explicit non-goals for v0.8.84

This milestone does not implement the Clean Study visual item UI.

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

It does not refresh Clean Study.

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

`v0.8.85-owner-local-clean-study-preview-visual-items-readonly-ui-implementation-no-share-no-delivery`

That milestone may implement read-only display of `visual_items.clean-study.preview.json` inside Clean Study preview.
