# v0.8.75 Review Document visual validation read-only browser smoke — no share/no delivery

## Purpose

This milestone validates the v0.8.74 read-only visual validation section through a local in-process HTTP-style smoke check.

It uses FastAPI TestClient.

It does not start uvicorn.

It does not start LanguageTool.

It does not modify `services/api/web_app.py`.

It does not add a POST endpoint.

It does not add decision saving.

It does not change `/study`.

## Smoke target

The smoke check performs a GET request against:

`/review-document/v0875-visual-readonly-smoke`

The check uses a controlled local fixture under `data/output/v0875-visual-readonly-smoke`.

The fixture is removed after the check.

## Expected UI evidence

The response must include the read-only section:

`Formule și imagini de verificat`

The section must show:

- source page;
- visual type;
- OCR Math candidate text;
- validation status;
- crop availability;
- Clean Study eligibility;
- collapsed `Diagnostic tehnic`.

## Read-only assertions

The section must not contain:

- forms;
- POST methods;
- buttons;
- Accept/Edit/Ignore save controls;
- raw visual item ids in the learner-facing card;
- raw crop artifact paths in the learner-facing card;
- absolute local paths in the learner-facing card.

## Scope boundary

This milestone creates only documentation and a local smoke-check script.

It may create and remove a temporary local fixture under `data/output`.

It performs GET-only route access through FastAPI TestClient.

It does not start uvicorn.

It does not start LanguageTool.

It does not perform POST.

It does not upload a PDF.

It does not run `/generate`.

It does not run OCR.

It does not run LanguageTool.

It does not run OCR Math.

It does not generate crops.

It does not write manual decisions.

It does not write Clean Study.

It does not write Progress.

It does not build.

It does not create a ZIP.

It does not create OneDrive staging.

It does not create a share link.

It does not deliver to testers.

It does not distribute anything.

It does not create a public release.

## Recommended next slice

After this smoke passes, the next safe milestone is a controlled owner-local save-action plan for visual validation decisions before implementing POST writes.
