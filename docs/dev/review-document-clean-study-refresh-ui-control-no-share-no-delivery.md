# v0.8.82 Review Document Clean Study refresh UI control — no share/no delivery

## Purpose

This milestone adds the explicit user-facing Clean Study refresh control in `Revizuire document`.

It adds the button:

`Actualizează lecția curată`

The button submits to the existing v0.8.81 route:

`POST /review-document/visual-validation/refresh-clean-study-preview`

## Scope

This milestone may modify `services/api/web_app.py` only to render the UI control.

It does not add a new route.

It does not add a new POST endpoint.

It does not change the v0.8.81 refresh action.

It does not change `/study`.

It does not write Progress.

It does not run refresh during GET.

It does not write Clean Study during GET.

## UI behavior

`Revizuire document` shows a clear local action after the visual validation section.

The user-facing label is:

`Actualizează lecția curată`

The UI explains that:

- accepted and corrected items can enter the lesson;
- ignored and pending items remain outside the lesson;
- the refresh is local;
- it does not modify the original document;
- it does not write Progress;
- it does not publish or share anything.

The UI also shows a link:

`Deschide lecția curată`

## Form contract

The form uses:

`method="post"`

The form action is:

`/review-document/visual-validation/refresh-clean-study-preview`

The form sends only:

`course_id`

The form does not submit item data.

The form does not submit crop paths.

The form does not submit ready flags.

The form does not submit OCR Math status.

The form does not submit bbox data.

## Validation

The check uses FastAPI TestClient with GET only.

It creates a temporary fixture under:

`data/output/v0882-clean-study-refresh-ui-control-smoke`

It renders:

`GET /review-document/v0882-clean-study-refresh-ui-control-smoke`

It verifies:

- the Clean Study refresh control is visible;
- the button text is visible;
- the existing v0.8.81 POST route is used;
- only `course_id` is submitted by the refresh form;
- no item payload is submitted;
- no crop path is submitted;
- no bbox data is submitted;
- no ready flag is submitted;
- no OCR Math status is submitted;
- no Clean Study artifact is written by GET;
- no Progress write occurs;
- `/study` is unchanged.

## Explicit non-goals

This milestone does not submit the refresh form.

It does not call the refresh POST route.

It does not start uvicorn.

It does not start LanguageTool.

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

`v0.8.83-owner-local-review-document-clean-study-refresh-rendered-form-post-smoke-no-share-no-delivery`

That milestone can submit the rendered `Actualizează lecția curată` form through TestClient and verify the Clean Study preview artifact is written only after explicit POST.
