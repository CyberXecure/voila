# v0.8.78 Review Document visual validation form controls — no share/no delivery

## Purpose

This milestone adds user-facing form controls for visual validation decisions inside `Revizuire document`.

It connects the v0.8.74 visual validation cards to the v0.8.77 controlled save action.

It adds UI controls only.

It does not add a new POST endpoint.

It does not change `/study`.

It does not write Clean Study.

## Added controls

Each visual validation card may show explicit controls:

- `Acceptă`;
- `Salvează corectarea`;
- `Ignoră`.

The forms submit to the existing controlled route:

`POST /review-document/visual-validation/save`

## Form boundary

The form submits only minimal fields:

- `course_id`;
- `item_id`;
- `decision`;
- `user_corrected_text`;
- `user_explanation`.

The form does not submit:

- bbox coordinates;
- crop path;
- page image path;
- absolute local path;
- OCR Math status;
- ready flag;
- Clean Study eligibility;
- schema internals.

Those values remain server-side only.

## Decision boundary

The UI does not approve anything implicitly.

`Acceptă` is an explicit submit action.

`Salvează corectarea` is an explicit submit action.

`Ignoră` is an explicit submit action.

A GET request does not write anything.

A page refresh does not approve anything.

## Clean Study boundary

This UI does not write Clean Study.

The save route writes only the visual validation artifact and summary.

Clean Study preview remains a separate controlled ingestion step.

## Validation

The check uses FastAPI TestClient.

It creates a temporary fixture under:

`data/output/v0878-visual-form-controls-smoke`

It performs a GET request against:

`/review-document/v0878-visual-form-controls-smoke`

It verifies:

- the visual validation section is visible;
- form controls are visible;
- forms use POST;
- forms submit to `/review-document/visual-validation/save`;
- Acceptă control exists;
- Salvează corectarea control exists;
- Ignoră control exists;
- correction textarea exists;
- explanation textarea exists;
- minimal hidden fields exist;
- learner-facing cards still hide bbox coordinates, crop paths, and absolute local paths.

The check does not submit the forms.

## Scope boundary

This milestone may modify `services/api/web_app.py` for UI form rendering.

It does not add a new route.

It does not add a new POST endpoint.

It does not perform POST in the automated check.

It does not write manual decisions in the automated check.

It does not write Clean Study.

It does not change `/study`.

It does not start uvicorn.

It does not start LanguageTool.

It does not upload a PDF.

It does not run `/generate`.

It does not run OCR.

It does not run LanguageTool.

It does not run OCR Math.

It does not generate crops.

It does not write Progress.

It does not build.

It does not create a ZIP.

It does not create OneDrive staging.

It does not create a share link.

It does not deliver to testers.

It does not distribute anything.

It does not create a public release.

## Recommended next slice

The next milestone should be:

`v0.8.79-owner-local-review-document-visual-validation-form-controls-post-smoke-no-share-no-delivery`

That milestone can submit the visible forms through TestClient and verify the already implemented save action end-to-end from the rendered UI.
