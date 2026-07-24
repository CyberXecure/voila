# v0.8.83 Review Document Clean Study refresh rendered-form POST smoke — no share/no delivery

## Purpose

This milestone smoke-tests the rendered `Actualizează lecția curată` form in `Revizuire document`.

It verifies that the user-facing form added in v0.8.82 submits to the existing v0.8.81 refresh route.

It does not modify `services/api/web_app.py`.

It does not add a route.

It does not add a POST endpoint.

## Flow under test

The smoke flow is:

1. create a temporary validated visual decisions fixture;
2. render `GET /review-document/<course_id>`;
3. find the rendered Clean Study refresh form;
4. verify the form submits only `course_id`;
5. verify GET does not write Clean Study;
6. submit the rendered form through FastAPI TestClient;
7. verify Clean Study preview artifacts are written only after explicit POST.

## Existing route used

The rendered form must submit to:

`POST /review-document/visual-validation/refresh-clean-study-preview`

This is the existing v0.8.81 route.

## Form contract

The rendered form must use:

`method="post"`

The rendered form action must be:

`/review-document/visual-validation/refresh-clean-study-preview`

The rendered form must submit only:

`course_id`

The rendered form must not submit:

- item data;
- item IDs;
- crop paths;
- bbox data;
- ready flags;
- OCR Math status;
- user decisions;
- corrected text;
- explanation text.

## Expected refresh output

After explicit POST, the route may write only:

- `formula_visual_evidence/visual_items.clean-study.preview.json`;
- `formula_visual_evidence/visual_items.clean-study.preview-summary.json`.

The route must preserve:

`formula_visual_evidence/visual_items.bbox.validated.json`

The route must not write Progress.

The route must not change `/study`.

## Inclusion and exclusion expectations

The check verifies:

- accepted item is included;
- edited item is included with corrected text;
- ignored item is excluded;
- pending item is excluded;
- malformed item is excluded;
- older candidate artifact is not used for refresh.

## Explicit non-goals

This milestone does not modify `services/api/web_app.py`.

It does not add UI.

It does not add a route.

It does not add a POST endpoint.

It does not start uvicorn.

It does not start LanguageTool.

It does not upload a PDF.

It does not run `/generate`.

It does not run OCR.

It does not run LanguageTool.

It does not run OCR Math.

It does not generate crops.

It does not write manual decisions.

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

`v0.8.84-owner-local-clean-study-preview-visual-items-readonly-ui-plan-no-share-no-delivery`

That milestone can plan how the Clean Study preview page should display validated visual study items without exposing technical metadata.
