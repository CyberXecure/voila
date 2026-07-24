# v0.8.85 Clean Study preview visual items read-only UI implementation — no share/no delivery

## Purpose

This milestone implements read-only display of validated visual study items inside Clean Study preview.

It reads the learner-facing artifact:

`formula_visual_evidence/visual_items.clean-study.preview.json`

It does not read raw validation artifacts for display.

It does not change `/study`.

It does not write Clean Study.

It does not write Progress.

## UI

The Clean Study preview page may show a section titled:

`Elemente vizuale validate`

Each card may show:

- title;
- `Sursa: pagina`;
- safe visual image when available;
- `Întrebare`;
- `Răspuns validat`;
- `Explicație`;
- `Verificat în Revizuire document`.

## Empty states

If Clean Study was not refreshed, the UI shows:

`Lecția curată nu a fost actualizată încă.`

If the artifact exists but has no items, the UI shows:

`Nu există încă elemente vizuale validate pentru lecție.`

## Hidden metadata

The learner-facing UI must not display:

- bbox;
- bbox_units;
- crop_path as text;
- page_image_path;
- source_visual_item_id;
- study_item_id;
- schema_version;
- source_visual_items_path;
- artifact names;
- absolute paths;
- local filesystem roots;
- ready_for_study;
- ready_for_clean_study;
- user_decision;
- ocr_math_status;
- learning_source;
- raw JSON.

## Image safety

The implementation may use crop_path internally to render a data URI image.

The raw crop path must not be displayed as text.

Absolute paths must not be displayed.

Unsafe crop paths must be hidden.

Missing crop files must degrade gracefully.

## Validation

The check uses FastAPI TestClient with GET only.

It creates temporary fixtures under:

`data/output/v0885-visual-ui-smoke`

It verifies:

- Clean Study preview renders the visual items section;
- accepted visual item is visible;
- edited visual item is visible with corrected text;
- explanation is visible;
- page source is visible;
- safe image data URI is rendered when the crop exists;
- missing crop image degrades gracefully;
- empty state is friendly;
- technical metadata is hidden;
- raw JSON is hidden;
- absolute paths are hidden;
- GET does not write Clean Study;
- GET does not write Progress;
- `/study` remains unchanged.

## Scope boundary

This milestone may modify `services/api/web_app.py` only for read-only Clean Study preview visual item display.

It does not add a route.

It does not add a POST endpoint.

It does not add a button.

It does not submit a form.

It does not call a POST route.

It does not start uvicorn.

It does not start LanguageTool.

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

`v0.8.86-owner-local-clean-study-preview-visual-items-readonly-ui-smoke-no-share-no-delivery`

That milestone can add a narrower regression smoke for the rendered Clean Study preview UI after this implementation.
