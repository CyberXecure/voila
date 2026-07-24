# v0.8.70 OCR Math on crop candidate — no share/no delivery

## Purpose

This milestone adds a controlled local runner that applies OCR candidate extraction to existing bbox crop PNG artifacts.

It uses the v0.8.69 real crop artifacts as input.

## Added capability

The standalone script is:

`scripts/dev/run-ocrmath-on-bbox-crops.py`

It accepts:

- `visual_items.bbox.with-crops.json`;
- output root containing `formula_visual_evidence/crops/...`;
- Tesseract command;
- OCR language;
- page segmentation mode.

It writes:

- `formula_visual_evidence/visual_items.bbox.with-ocrmath-candidates.json`;
- `formula_visual_evidence/visual_items.bbox.ocrmath-candidates-summary.json`.

## User validation rule

OCR Math on crop produces only a candidate.

It must not mark the item as ready for Study.

For processed crop items:

- `ocr_math_candidate_text` may be filled;
- `ocr_math_status` becomes `pending_user_validation` when text is detected;
- `user_decision` remains `pending`;
- `ready_for_study` remains `false`.

## Scope boundary

This milestone does not connect the runner to the web UI.

It does not modify `services/api/web_app.py`.

It does not run `/generate`.

It does not run global OCR Math.

It does not run LanguageTool.

It does not ingest candidates into Study.

It does not write Progress.

## Validation approach

The milestone check creates a synthetic local PDF outside the repo under `D:\dev\tester-runs`.

The check uses the v0.8.69 crop builder to create real crop PNG artifacts.

The check then runs OCR candidate extraction only on those crop PNG artifacts.

The check validates that:

- crop PNG exists before OCR;
- OCR candidate artifact exists;
- OCR candidate summary exists;
- processed items are set to `pending_user_validation` when text is detected;
- `user_decision` remains `pending`;
- `ready_for_study` remains `false`;
- the tracked v0.8.68 validator accepts the updated artifact;
- `services/api/web_app.py` is unchanged.

## Policy

Controlled local OCR Math candidate extraction from crop PNG only.

No web route change.

No server required.

No POST.

No upload.

No generate.

No global OCR Math run.

No LanguageTool run.

No Study write.

No Progress write.

No build.

No ZIP.

No OneDrive staging.

No share link.

No tester delivery.

No distribution.

No public release.
