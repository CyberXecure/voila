# v0.8.69 Real crop artifact from bbox — no share/no delivery

## Purpose

This milestone adds a controlled local builder that can create real PNG crop artifacts from a valid bbox visual item file.

It is the first implementation step after the v0.8.67 contract and v0.8.68 validator.

## Added capability

The script:

`services/dev` is not changed.

The new standalone script is:

`scripts/dev/build-bbox-visual-crops.py`

It accepts:

- source PDF path;
- `visual_items.bbox.json` path;
- output root;
- render zoom.

It writes:

- page image PNG files under `formula_visual_evidence/pages/`;
- crop PNG files under `formula_visual_evidence/crops/`;
- updated local artifact `formula_visual_evidence/visual_items.bbox.with-crops.json`;
- summary artifact `formula_visual_evidence/visual_items.bbox.crop-summary.json`.

## Scope boundary

This milestone does not connect the builder to the web UI.

It does not modify `services/api/web_app.py`.

It does not run `/generate`.

It does not run OCR.

It does not run LanguageTool.

It does not run OCR Math.

It does not ingest the crop into Study.

## Validation approach

The milestone check creates a synthetic local PDF outside the repo under `D:\dev\tester-runs`.

The check creates a valid bbox visual item JSON outside the repo.

The check runs the crop builder on that synthetic PDF.

The check validates that:

- page PNG exists;
- crop PNG exists;
- crop PNG has non-zero size;
- updated visual item artifact exists;
- crop summary exists;
- the updated item has `crop_exists=true`;
- the tracked v0.8.68 validator accepts the updated artifact.

## Policy

Controlled local crop artifact generation only.

No web route change.

No server required.

No POST.

No upload.

No generate.

No OCR run.

No LanguageTool run.

No OCR Math run.

No Study write.

No Progress write.

No build.

No ZIP.

No OneDrive staging.

No share link.

No tester delivery.

No distribution.

No public release.
