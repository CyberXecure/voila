# v0.8.74 Review Document visual validation read-only UI — no share/no delivery

## Purpose

This milestone adds the first read-only visual validation UI slice inside `Revizuire document`.

It implements display only.

It does not add decision saving.

It does not add a POST endpoint.

It does not change `/study`.

## User-facing section

The new section is:

`Formule și imagini de verificat`

It shows, when existing local artifacts are present:

- source page;
- visual type label;
- OCR Math candidate text or corrected text when already edited;
- validation status;
- whether the crop image is available;
- learner-friendly explanation when present;
- Clean Study eligibility.

## Read-only boundary

The section is read-only.

It does not show Accept/Edit/Ignore buttons yet.

It does not save manual decisions.

It does not write `visual_items.bbox.validated.json`.

It does not write `visual_items.clean-study.preview.json`.

## Hidden technical details

The learner-facing card does not show:

- bbox coordinates;
- raw artifact file names;
- absolute local paths;
- Python script names;
- JSON schema internals;
- package or release terminology.

Technical context appears only in the collapsed `Diagnostic tehnic` section.

## Data source

The UI reads existing local artifacts only:

- `formula_visual_evidence/visual_items.bbox.with-ocrmath-candidates.json`;
- `formula_visual_evidence/visual_items.bbox.validated.json`.

No artifact is created by this UI slice.

## Scope boundary

This milestone may modify `services/api/web_app.py` for read-only rendering.

It does not add a POST endpoint.

It does not start the server during the automated check.

It does not call any route during the automated check.

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

## Next recommended slice

After this read-only UI is merged, the next milestone should add a local browser smoke check or a small controlled save-action plan before adding decision writes.
