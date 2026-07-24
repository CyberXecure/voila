# v0.8.81 Review Document visual validation Clean Study refresh implementation — no share/no delivery

## Purpose

This milestone implements the explicit owner-local Clean Study preview refresh action after visual validation decisions in `Revizuire document`.

It implements:

`POST /review-document/visual-validation/refresh-clean-study-preview`

The route rebuilds only the Clean Study visual preview artifact.

It does not write the default `/study` output.

It does not write Progress.

## Input artifact

The route reads only:

`formula_visual_evidence/visual_items.bbox.validated.json`

It does not read `visual_items.bbox.with-ocrmath-candidates.json` when rebuilding Clean Study.

It does not trust client-submitted item data.

It does not trust client-submitted crop paths.

It does not trust client-submitted ready flags.

## Output artifacts

The route writes only:

- `formula_visual_evidence/visual_items.clean-study.preview.json`;
- `formula_visual_evidence/visual_items.clean-study.preview-summary.json`.

The route does not modify:

- `formula_visual_evidence/visual_items.bbox.validated.json`;
- `/study`;
- Progress.

## Inclusion rule

Clean Study visual preview includes only items where:

- `ready_for_study=true`;
- `user_decision=accept` or `user_decision=edit`;
- `crop_exists=true`;
- server-side `crop_path` is present;
- accepted items have non-empty `ocr_math_candidate_text`;
- edited items have non-empty `user_corrected_text`.

## Exclusion rule

Clean Study visual preview excludes:

- `user_decision=ignore`;
- `user_decision=pending`;
- items without crop;
- accepted items without OCR Math candidate text;
- edited items without corrected text;
- malformed items.

## Safety

The route is owner-local.

The route accepts only `course_id` from the form.

The route uses safe course ID validation.

The route resolves the output directory under `data/output`.

The route does not join client-controlled paths.

The route does not accept client-submitted item payloads.

The route returns friendly escaped HTML responses.

The route does not redirect to user-controlled URLs.

The route does not expose stack traces.

## Validation

The check uses FastAPI TestClient.

It creates a temporary fixture under:

`data/output/v0881-clean-study-refresh-smoke`

It writes a validated visual decisions artifact.

It calls:

`POST /review-document/visual-validation/refresh-clean-study-preview`

It verifies:

- Clean Study preview artifact exists;
- Clean Study preview summary exists;
- accepted item is included;
- edited item is included with corrected text;
- ignored item is excluded;
- pending item is excluded;
- malformed item is excluded;
- validated visual decisions artifact remains preserved;
- `/study` is unchanged;
- Progress is unchanged;
- no upload/generate/OCR/LanguageTool/OCR Math/crop generation/build/ZIP/share/delivery occurs.

## Scope boundary

This milestone may modify `services/api/web_app.py` for the explicit refresh action.

It does not add UI buttons.

It does not submit rendered UI forms.

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

`v0.8.82-owner-local-review-document-clean-study-refresh-ui-control-no-share-no-delivery`

That milestone can add a user-facing `Actualizează lecția curată` control in `Revizuire document`.
