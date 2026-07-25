# v0.8.86 Clean Study preview visual items read-only UI smoke — no share/no delivery

## Purpose

This milestone adds a narrow regression smoke for the v0.8.85 Clean Study preview visual items read-only UI.

It verifies that Clean Study preview can render validated visual study items from:

`formula_visual_evidence/visual_items.clean-study.preview.json`

This is a smoke-only milestone.

It does not modify `services/api/web_app.py`.

It does not add a route.

It does not add a POST endpoint.

## Flow under test

The smoke flow is:

1. create a temporary Clean Study visual preview fixture;
2. render `GET /study-clean-preview/<course_id>`;
3. verify the learner-facing visual items section is visible;
4. verify accepted/edited visual study content is visible;
5. verify a safe image data URI is rendered when crop exists;
6. verify missing crop degrades gracefully;
7. verify technical metadata is hidden;
8. verify GET does not write Clean Study or Progress.

## Expected learner-facing UI

The rendered page should show:

- `Elemente vizuale validate`;
- `Sursa: pagina`;
- `Întrebare`;
- `Răspuns validat`;
- `Explicație`;
- `Verificat în Revizuire document`.

## Hidden technical metadata

The rendered learner-facing page must not expose:

- raw crop path text;
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
- local filesystem roots;
- `ready_for_study`;
- `ready_for_clean_study`;
- `user_decision`;
- `ocr_math_status`;
- `learning_source`;
- raw JSON.

## Explicit non-goals

This milestone does not modify `services/api/web_app.py`.

It does not implement UI.

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

`v0.8.87-owner-local-review-to-clean-study-visual-flow-final-audit-no-share-no-delivery`

That milestone can audit the full visual review-to-clean-study path after v0.8.67 through v0.8.86.
