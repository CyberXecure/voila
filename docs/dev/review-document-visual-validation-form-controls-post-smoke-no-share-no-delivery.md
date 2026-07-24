# v0.8.79 Review Document visual validation form controls POST smoke — no share/no delivery

## Purpose

This milestone validates the v0.8.78 rendered form controls end-to-end against the v0.8.77 save action.

It uses FastAPI TestClient.

It performs a GET request to render the `Revizuire document` visual validation forms.

It extracts the rendered forms.

It submits POST requests using the rendered form data.

It may modify `services/api/web_app.py` only to make the Review Document UI prefer the validated visual artifact after save.

It does not add a new route.

It does not add a new POST endpoint.

It does not change `/study`.

It does not write Clean Study.

## Smoke target

The smoke check uses a controlled temporary fixture under:

`data/output/v0879-visual-form-post-smoke`

The GET target is:

`/review-document/v0879-visual-form-post-smoke`

The existing POST target is:

`/review-document/visual-validation/save`

## Expected POST behavior

The check submits rendered forms for:

- `accept`;
- `edit`;
- `ignore`.

The check also submits an invalid edit without corrected text to confirm rejection.

Expected result:

- accepted item becomes `ready_for_study=true`;
- edited item becomes `ready_for_study=true` and stores corrected text;
- ignored item remains excluded from study;
- unrelated pending item remains pending;
- invalid edit is rejected;
- `visual_items.bbox.validated.json` exists;
- `visual_items.bbox.validation-summary.json` exists;
- `visual_items.clean-study.preview.json` is not written.
- visual_items.clean-study.preview.json is not written.


## Post-save readback fix

The smoke found that the save action can write `visual_items.bbox.validated.json`, while the read-only UI may still prefer the older candidate artifact.

This milestone therefore also fixes the readback priority so `Revizuire document` prefers:

- `formula_visual_evidence/visual_items.bbox.validated.json`;
- then `formula_visual_evidence/visual_items.bbox.with-ocrmath-candidates.json`.

This does not add a new route and does not change the save contract.

## Boundary

This is an owner-local POST smoke only.

It writes only temporary visual validation artifacts inside the temporary fixture.

The temporary fixture is removed after the check.

It does not write Clean Study.

It does not write Progress.

It does not upload a PDF.

It does not run `/generate`.

It does not run OCR.

It does not run LanguageTool.

It does not run OCR Math.

It does not generate crops.

It does not start uvicorn.

It does not start LanguageTool.

It does not build.

It does not create a ZIP.

It does not create OneDrive staging.

It does not create a share link.

It does not deliver to testers.

It does not distribute anything.

It does not create a public release.

## Recommended next slice

The next milestone should be:

`v0.8.80-owner-local-review-document-visual-validation-clean-study-refresh-plan-no-share-no-delivery`

That milestone should plan how validated visual decisions refresh the separate Clean Study preview without writing Study directly from the save action.
