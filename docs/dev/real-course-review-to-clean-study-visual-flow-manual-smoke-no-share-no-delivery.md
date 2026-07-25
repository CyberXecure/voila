# v0.8.88 Real-course Review-to-Clean-Study visual flow manual smoke — no share/no delivery

## Purpose

This milestone performs an owner-local controlled smoke of the visual review-to-clean-study flow on the real local course:

`03-pag-30-34-vectori-trigonometrie`

This is not a package milestone.

It does not build.

It does not create a ZIP.

It does not share or deliver anything.

## Flow under test

The smoke validates this flow:

`Revizuire document`
→ rendered visual validation forms
→ accept/edit/ignore POST
→ `visual_items.bbox.validated.json`
→ rendered `Actualizează lecția curată` form
→ explicit Clean Study refresh POST
→ `visual_items.clean-study.preview.json`
→ Clean Study preview read-only learner UI

## Controlled local writes

This smoke may temporarily write visual artifacts inside the real course output directory.

Before writing, it backs up the real course `formula_visual_evidence` directory if it exists.

After the smoke, it restores the original state.

The milestone must not leave persistent smoke artifacts in the real course output.

## Expected coverage

The smoke checks:

- real input PDF exists;
- real output directory exists;
- Review Document page renders;
- visual validation forms are rendered;
- accept decision POST works;
- edit decision POST works;
- ignore decision POST works;
- validated visual artifact is produced during the smoke;
- refresh form is rendered;
- refresh form submits only `course_id`;
- explicit refresh POST works;
- Clean Study preview artifact is produced during the smoke;
- Clean Study preview page renders learner-facing visual items;
- accepted item is visible;
- edited item is visible with corrected text;
- ignored item is excluded;
- safe image data URI is rendered;
- missing crop degrades gracefully;
- technical metadata remains hidden;
- raw JSON remains hidden;
- absolute paths remain hidden;
- Progress is not modified;
- `/study` is not changed;
- real course visual artifacts are restored after the smoke.

## Explicit non-goals

This milestone does not modify `services/api/web_app.py`.

It does not modify `services/api/web_app.py`.

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

It does not build.

It does not create a ZIP.

It does not create OneDrive staging.

It does not create a share link.

It does not deliver to testers.

It does not distribute anything.

It does not create a public release.

## Readiness boundary

A PASS here means the owner-local visual review-to-clean-study flow works on the real local course surface.

It still does not authorize a tester package.

A separate package rebuild and extracted-package validation milestone is required before any tester-share decision.

## Recommended next slice

The next milestone should be:

`v0.8.89-owner-local-real-course-review-to-clean-study-visual-flow-final-readiness-audit-no-share-no-delivery`

That milestone can record the readiness boundary after the real-course smoke, still without package rebuild or delivery.
